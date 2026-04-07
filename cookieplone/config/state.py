from cookiecutter import exceptions as exc
from cookieplone.config.schemas import SubTemplate
from cookieplone.config.v1 import parse_v1
from cookieplone.config.v2 import ParsedConfig
from cookieplone.config.v2 import parse_v2
from cookieplone.logger import logger
from cookieplone.settings import DEFAULT_DATA_KEY
from cookieplone.settings import DEFAULT_VALIDATORS
from cookieplone.utils import files as f
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

import warnings


_NO_VALUE = object()


@dataclass
class Context:
    """The three sources of context that can influence template defaults.

    :param default: Values from the user-level cookiecutter config file
        (``~/.cookiecutterrc`` or equivalent).
    :param extra: Values passed explicitly via ``--extra-context`` or the
        ``extra_context`` API argument.
    :param replay: Values loaded from a replay file when re-running a
        previously completed generation.
    """

    default: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    replay: dict[str, Any] = field(default_factory=dict)


@dataclass
class Answers:
    """Wizard output split into full answers, user-supplied answers, and initial answers

    :param answers: Complete set of answers after Jinja rendering, including
        computed and internal keys.  Used as the cookiecutter context.
    :param user_answers: Only the values explicitly entered (or confirmed) by
        the user through the wizard, without computed keys.  Used for
        persisting answers in interactive runs.
    :param initial_answers: User-facing values derived from the pre-populated
        context (user config, extra context, or replay) before the wizard
        runs, excluding ``computed`` and ``constant`` fields.  Used for
        persisting answers when running with ``no_input=True``, since the
        wizard is skipped and ``user_answers`` remains empty.
    """

    answers: dict[str, Any] = field(default_factory=dict)
    user_answers: dict[str, Any] = field(default_factory=dict)
    initial_answers: dict[str, Any] = field(default_factory=dict)


@dataclass
class CookieploneState:
    """All state needed to drive a single Cookieplone template generation run.

    :param schema: Parsed schema dict (v1 or v2) describing the template's variables.
    :param data: Runtime context passed to cookiecutter's ``generate_files``.
        Contains ``root_key`` (usually ``"cookiecutter"``) with template variables
        and ``"versions"`` with the version pinning dict.  Mutated during
        generation as wizard answers and internal keys are injected.
    :param root_key: The top-level key under which template variables are stored.
        Defaults to :data:`~cookieplone.settings.DEFAULT_DATA_KEY`.
    :param context: The three override sources (user config, extra, replay) captured
        at initialisation time for later introspection.
    :param answers: Wizard output — both the full rendered answers and the subset
        supplied by the user.  Populated after the wizard completes.
    :param extensions: Jinja2 extension class paths extracted from the config's
        ``extensions`` list.
    :param no_render: Glob patterns for files that should be copied without Jinja
        rendering, extracted from the config's ``no_render`` list.
    :param subtemplates: Sub-template definitions extracted from the
        config's ``subtemplates`` list.  Each entry is a
        :class:`~cookieplone.config.schemas.SubTemplate` with ``id``,
        ``title``, and ``enabled`` keys.  The ``enabled`` value can be a
        static string (``"1"``/``"0"``) or a Jinja2 expression rendered
        against the current context during generation.
    :param template_id: Template identifier from the config's top-level ``id`` field.
    :param versions: Version pinning dict from the config's ``versions`` mapping.
        Injected into ``data["versions"]`` so templates can access values via
        ``{{ versions.<key> }}``.
    """

    schema: dict[str, Any]
    data: dict[str, dict[str, Any]]
    root_key: str = DEFAULT_DATA_KEY
    context: Context = field(default_factory=Context)
    answers: Answers = field(default_factory=Answers)
    extensions: list[str] = field(default_factory=list)
    no_render: list[str] = field(default_factory=list)
    subtemplates: list[SubTemplate] = field(default_factory=list)
    template_id: str = ""
    versions: dict[str, str] = field(default_factory=dict)


def _parse_schema(context: dict[str, Any], version: str = "1.0") -> ParsedConfig:
    """Parse the raw schema from the context and return a :class:`ParsedConfig`."""
    parsed = parse_v1(context) if version == "1.0" else parse_v2(context)

    schema = parsed.schema
    # All questions will be under `properties`
    for key, val_func in DEFAULT_VALIDATORS.items():
        if not (question := schema["properties"].get(key)) or question.get("validator"):
            continue
        logger.debug(f"Setting {val_func} for question {key}")
        question["validator"] = val_func
    return parsed


def _filter_initial_answers(
    initial_answers: dict[str, Any],
    schema: dict[str, Any],
) -> dict[str, Any]:
    """Return only the user-facing keys from *initial_answers*, filtered by *schema*.

    Iterates over the schema's ``properties`` and copies each key that is
    present in *initial_answers*, skipping properties whose ``format`` is
    ``"computed"`` or ``"constant"`` (values the user never sets directly).
    Keys that exist in *initial_answers* but are absent from the schema are
    also excluded.

    :param initial_answers: Pre-populated context values (from user config,
        extra context, or a replay file) collected before the wizard runs.
    :param schema: Parsed schema dict whose ``properties`` describe the
        template variables and their metadata.
    :returns: Filtered dict containing only user-facing keys with their
        initial values.
    """
    data = {}
    properties = schema.get("properties", {})
    for key, property_ in properties.items():
        if property_.get("format", "") in ("computed", "constant"):
            continue
        if (value := initial_answers.get(key, _NO_VALUE)) == _NO_VALUE:
            continue
        data[key] = value
    return data


def _apply_overwrites_to_schema(
    schema: dict[str, Any],
    overwrite_context: dict[str, Any],
    *,
    in_dictionary_variable: bool = False,
):
    """Modify default values on the schema based on the overwrite context.

    Iterates over *overwrite_context* and, for each key that exists in the schema's
    ``properties``, replaces the property's ``default`` value.  Handles three
    special cases: list/choice variables (the override must be a valid choice or
    subset of choices), nested dict variables (recursed with
    ``in_dictionary_variable=True``), and plain scalar values (replaced directly).

    Unknown top-level keys are silently ignored.  Unknown keys inside a nested dict
    variable are added as new properties so they can be passed through to
    sub-templates.

    :param schema: The schema dict whose ``properties`` will be mutated in-place.
    :param overwrite_context: Key/value pairs to apply as default overrides.
    :param in_dictionary_variable: Internal flag set to ``True`` when recursing
        into a nested dict property.  Enables different behaviour for unknown keys
        and choice variables.
    :raises ValueError: If a choice override is not among the valid choices for
        that variable.
    """
    properties = schema.get("properties", {})
    for variable, overwrite in overwrite_context.items():
        if variable not in properties:
            if not in_dictionary_variable:
                # We are dealing with a new variable on first level, ignore
                continue
            # We are dealing with a new dictionary variable in a deeper level
            properties[variable] = {"default": overwrite}

        property_ = properties.get(variable, _NO_VALUE)
        context_value = property_.get("default")
        if isinstance(context_value, list):
            if in_dictionary_variable:
                property_["default"] = overwrite
                continue
            if isinstance(overwrite, list):
                # We are dealing with a multichoice variable
                # Let's confirm all choices are valid for the given context
                if set(overwrite).issubset(set(context_value)):
                    property_["default"] = overwrite
                else:
                    raise ValueError(
                        f"{overwrite} provided for multi-choice variable "
                        f"{variable}, but valid choices are {context_value}"
                    )
            else:
                # We are dealing with a choice variable
                if overwrite in context_value:
                    # This overwrite is actually valid for the given context
                    # Let's set it as default (by definition first item in list)
                    # see ``cookiecutter.prompt.prompt_choice_for_config``
                    context_value.remove(overwrite)
                    context_value.insert(0, overwrite)
                else:
                    raise ValueError(
                        f"{overwrite} provided for choice variable "
                        f"{variable}, but the choices are {context_value}."
                    )
        elif isinstance(context_value, dict) and isinstance(overwrite, dict):
            # Partially overwrite some keys in original dict
            _apply_overwrites_to_schema(
                context_value, overwrite, in_dictionary_variable=True
            )
            property_["default"] = context_value
        else:
            # Simply overwrite the value for this variable
            property_["default"] = overwrite


def _merge_versions(
    global_versions: dict[str, str] | None,
    template_versions: dict[str, str],
) -> dict[str, str]:
    """Merge repository-level and per-template version pinning dicts.

    *global_versions* provides the base layer (from ``cookieplone-config.json``).
    *template_versions* provides per-template overrides that take precedence
    for any key present in both dicts.

    :param global_versions: Repository-level version pins, or ``None``.
    :param template_versions: Per-template version pins.
    :returns: Merged version dict.
    """
    return {**(global_versions or {}), **template_versions}


def _generate_state(
    parsed: ParsedConfig,
    default_context: dict[str, Any] | None = None,
    extra_context: dict[str, Any] | None = None,
    replay_context: dict[str, Any] | None = None,
    global_versions: dict[str, str] | None = None,
) -> CookieploneState:
    """Build a :class:`CookieploneState` from a parsed config and optional
      context overrides.

    When *replay_context* is provided the schema defaults are ignored and the
    replay values are used directly as the initial data.  Otherwise,
    *default_context* and *extra_context* are applied in order to overwrite
    schema defaults before the wizard runs.

    :param parsed: A :class:`ParsedConfig` containing the schema and config fields.
    :param default_context: Values from the user-level config file.
    :param extra_context: Explicit overrides supplied by the caller.
    :param replay_context: Full replay file dict (the top-level structure with a
        ``"cookiecutter"`` key).  The inner dict is extracted automatically.
    :param global_versions: Repository-level version pinning from
        ``cookieplone-config.json``.  Merged as a base layer under the
        per-template versions so that templates can override individual keys.
    :returns: A fully initialised :class:`CookieploneState`.
    """
    schema = parsed.schema
    context = Context(
        default=default_context if default_context else {},
        extra=extra_context if extra_context else {},
        replay=replay_context if replay_context else {},
    )
    data: dict[str, Any] = {}
    initial_data: dict[str, Any] = {}
    if replay_context:
        # Update data with information from replay context, if provided.
        # replay_context is the full replay file; extract the inner dict.
        replay_data = replay_context.get(DEFAULT_DATA_KEY, {}) or {}
        data.update(replay_data)
        initial_data.update(replay_data)
    else:
        # Overwrite schema default values with the values from the context, if provided.
        # This allows us to load user configuration, or extra configuration
        # to apply default values from the context
        for additional_context in (default_context, extra_context):
            if additional_context:
                initial_data.update(additional_context)
                try:
                    _apply_overwrites_to_schema(schema, additional_context)
                except ValueError as error:
                    warnings.warn(f"Invalid default received: {error}", stacklevel=1)
    answers = Answers(initial_answers=_filter_initial_answers(initial_data, schema))
    # Update default value in the form config with the value from data
    for variable, value in data.items():
        if variable in schema.get("properties", {}):
            schema["properties"][variable]["default"] = value

    # Merge versions: global (repository-level) as base, per-template overrides
    versions = _merge_versions(global_versions, parsed.versions)

    state_data = {
        DEFAULT_DATA_KEY: data,
        "versions": versions,
    }

    state: CookieploneState = CookieploneState(
        schema=schema,
        data=state_data,
        context=context,
        extensions=parsed.extensions,
        no_render=parsed.no_render,
        subtemplates=parsed.subtemplates,
        template_id=parsed.template_id,
        versions=versions,
        answers=answers,
    )

    return state


def generate_state(
    template_path: Path,
    default_context: dict[str, Any] | None = None,
    extra_context: dict[str, Any] | None = None,
    replay_context: dict[str, Any] | None = None,
    global_versions: dict[str, str] | None = None,
) -> CookieploneState:
    """Generate the state for a Cookieplone run.

    Locates and parses the template's schema file (``cookieplone.json`` for v2,
    ``cookiecutter.json`` for v1) then delegates to :func:`_generate_state`.

    :param template_path: Path to the template directory containing the schema file.
    :param default_context: Values from the user-level cookiecutter config file.
    :param extra_context: Explicit key/value overrides supplied by the caller.
    :param replay_context: Full replay file dict.  When provided, schema defaults
        are replaced by previously recorded answers.
    :param global_versions: Repository-level version pinning from
        ``cookieplone-config.json``.  Passed through to :func:`_generate_state`
        where it is merged as a base layer under per-template versions.
    :returns: A fully initialised :class:`CookieploneState`.
    :raises exc.ConfigDoesNotExistException: If no schema file is found under
        *template_path*.
    :raises exc.ContextDecodingException: If the schema file contains invalid JSON.
    """
    if (parsed := load_schema_from_path(template_path)) is None:
        raise exc.ConfigDoesNotExistException(
            f"No configuration file found in {template_path}. "
            "Please ensure a 'cookieplone.json' or 'cookiecutter.json' file exists."
        )
    return _generate_state(
        parsed, default_context, extra_context, replay_context, global_versions
    )


def load_schema_from_path(template_path: Path) -> ParsedConfig | None:
    """Load and parse the schema from the filesystem.

    Tries ``cookieplone.json`` (v2) then ``cookiecutter.json`` (v1) under
    *template_path*.  Returns ``None`` if neither file exists.

    :param template_path: Directory to search for a schema file.
    :returns: A :class:`ParsedConfig`, or ``None`` if no schema file was found.
    :raises exc.ContextDecodingException: If the file exists but contains
        invalid JSON.
    """
    for filename, version in [
        ("cookieplone.json", "2.0"),
        ("cookiecutter.json", "1.0"),
    ]:
        config_file: Path = template_path / filename
        if config_file.is_file() and config_file.exists():
            try:
                data = f.load_json(config_file, as_ordered=True)
            except ValueError as e:
                our_exc_message = (
                    f"JSON decoding error while loading '{config_file}'. "
                    f"Decoding error details: '{e}'"
                )
                raise exc.ContextDecodingException(our_exc_message) from e
            return _parse_schema(data, version)
    return None


__all__ = ["CookieploneState", "generate_state", "load_schema_from_path"]

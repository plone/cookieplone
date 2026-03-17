import warnings
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from cookiecutter import exceptions as exc

from cookieplone.config.v1 import parse_v1
from cookieplone.config.v2 import parse_v2
from cookieplone.settings import DEFAULT_DATA_KEY
from cookieplone.utils import files as f

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
    """Wizard output split into full answers and user-supplied answers.

    :param answers: Complete set of answers after Jinja rendering, including
        computed and internal keys.  Used as the cookiecutter context.
    :param user_answers: Only the values explicitly entered (or defaulted) by
        the user, without computed keys.  Suitable for persisting to a replay
        file.
    """

    answers: dict[str, Any] = field(default_factory=dict)
    user_answers: dict[str, Any] = field(default_factory=dict)


@dataclass
class CookieploneState:
    """All state needed to drive a single Cookieplone template generation run.

    :param schema: Parsed schema dict (v1 or v2) describing the template's variables.
    :param data: Runtime context keyed by ``root_key`` (usually ``"cookiecutter"``).
        This dict is mutated during generation as wizard answers are collected.
    :param root_key: The top-level key under which template variables are stored.
        Defaults to :data:`~cookieplone.settings.DEFAULT_DATA_KEY`.
    :param context: The three override sources (user config, extra, replay) captured
        at initialisation time for later introspection.
    :param answers: Wizard output — both the full rendered answers and the subset
        supplied by the user.  Populated after the wizard completes.
    :param extensions: Jinja2 extension class paths extracted from the schema's
        ``_extensions`` property.
    """

    schema: dict[str, Any]
    data: dict[str, dict[str, Any]]
    root_key: str = DEFAULT_DATA_KEY
    context: Context = field(default_factory=Context)
    answers: Answers = field(default_factory=Answers)
    extensions: list[str] = field(default_factory=list)


def _parse_schema(context: dict[str, Any], version: str = "1.0") -> dict[str, Any]:
    """Parse the raw schema from the context."""
    if version == "1.0":
        context = parse_v1(context)
    elif version == "2.0":
        context = parse_v2(context)
    return context


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


def _get_extensions_from_schema(schema: dict[str, Any]) -> list[str]:
    """Extract Jinja extensions from the schema."""
    properties: dict[str, Any] = schema.get("properties", {})
    extensions_property: dict[str, Any] = properties.get("_extensions", {})
    return extensions_property.get("default", [])


def _generate_state(
    schema: dict[str, Any],
    default_context: dict[str, Any] | None = None,
    extra_context: dict[str, Any] | None = None,
    replay_context: dict[str, Any] | None = None,
) -> CookieploneState:
    """Build a :class:`CookieploneState` from a parsed schema and optional
      context overrides.

    When *replay_context* is provided the schema defaults are ignored and the
    replay values are used directly as the initial data.  Otherwise,
    *default_context* and *extra_context* are applied in order to overwrite
    schema defaults before the wizard runs.

    :param schema: Parsed v2 schema dict (``{"version": "2.0", "properties": ...}``).
    :param default_context: Values from the user-level config file.
    :param extra_context: Explicit overrides supplied by the caller.
    :param replay_context: Full replay file dict (the top-level structure with a
        ``"cookiecutter"`` key).  The inner dict is extracted automatically.
    :returns: A fully initialised :class:`CookieploneState`.
    """
    extensions = _get_extensions_from_schema(schema)
    context = Context(
        default=default_context if default_context else {},
        extra=extra_context if extra_context else {},
        replay=replay_context if replay_context else {},
    )
    data: dict[str, Any] = {}
    if replay_context:
        # Update data with information from replay context, if provided.
        # replay_context is the full replay file; extract the inner dict.
        data.update(replay_context.get("cookiecutter", {}) or {})
    else:
        # Overwrite schema default values with the values from the context, if provided.
        # This allows us to load user configuration, or extra configuration
        # to apply default values from the context
        for additional_context in (default_context, extra_context):
            if additional_context:
                try:
                    _apply_overwrites_to_schema(schema, additional_context)
                except ValueError as error:
                    warnings.warn(f"Invalid default received: {error}", stacklevel=1)

    # Update default value in the form config with the value from data
    for variable, value in data.items():
        if variable in schema.get("properties", {}):
            schema["properties"][variable]["default"] = value

    state: CookieploneState = CookieploneState(
        schema=schema,
        data={DEFAULT_DATA_KEY: data},
        context=context,
        extensions=extensions,
    )

    return state


def generate_state(
    template_path: Path,
    default_context: dict[str, Any] | None = None,
    extra_context: dict[str, Any] | None = None,
    replay_context: dict[str, Any] | None = None,
) -> CookieploneState:
    """Generate the state for a Cookieplone run.

    Locates and parses the template's schema file (``cookieplone.json`` for v2,
    ``cookiecutter.json`` for v1) then delegates to :func:`_generate_state`.

    :param template_path: Path to the template directory containing the schema file.
    :param default_context: Values from the user-level cookiecutter config file.
    :param extra_context: Explicit key/value overrides supplied by the caller.
    :param replay_context: Full replay file dict.  When provided, schema defaults
        are replaced by previously recorded answers.
    :returns: A fully initialised :class:`CookieploneState`.
    :raises exc.ConfigDoesNotExistException: If no schema file is found under
        *template_path*.
    :raises exc.ContextDecodingException: If the schema file contains invalid JSON.
    """
    if (schema := load_schema_from_path(template_path)) is None:
        raise exc.ConfigDoesNotExistException(
            f"No configuration file found in {template_path}. "
            "Please ensure a 'cookieplone.json' or 'cookiecutter.json' file exists."
        )
    return _generate_state(schema, default_context, extra_context, replay_context)


def load_schema_from_path(template_path: Path) -> dict | None:
    """Load and parse the schema from the filesystem.

    Tries ``cookieplone.json`` (v2) then ``cookiecutter.json`` (v1) under
    *template_path*.  Returns ``None`` if neither file exists.

    :param template_path: Directory to search for a schema file.
    :returns: Parsed schema dict, or ``None`` if no schema file was found.
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

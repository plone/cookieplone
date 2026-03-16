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
    default: dict[str, Any] = field(default_factory=dict)
    extra: dict[str, Any] = field(default_factory=dict)
    replay: dict[str, Any] = field(default_factory=dict)


@dataclass
class Answers:
    answers: dict[str, Any] = field(default_factory=dict)
    user_answers: dict[str, Any] = field(default_factory=dict)


@dataclass
class CookieploneState:
    """State for a Cookieplone run."""

    schema: dict[str, Any]
    data: dict[str, dict[str, Any]]
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
    """Modify default values on the schema based on the overwrite context."""
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
    """Generate the state for a Cookieplone run."""
    extensions = _get_extensions_from_schema(schema)
    context = Context(
        default=default_context if default_context else {},
        extra=extra_context if extra_context else {},
        replay=replay_context if replay_context else {},
    )
    data: dict[str, Any] = {}
    if replay_context:
        # Update data with information from replay context, if provided.
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

    Loads the JSON file as a Python object, with key being the JSON filename.

    :param template_path: Path to the template directory containing the JSON file.
    :param default_context: Dictionary containing config to take into account.
    :param extra_context: Dictionary containing configuration overrides
    :param replay_context: Dictionary containing context from a replay file
    """
    if (schema := load_schema_from_path(template_path)) is None:
        raise exc.ConfigDoesNotExistException(
            f"No configuration file found in {template_path}. "
            "Please ensure a 'cookieplone.json' or 'cookiecutter.json' file exists."
        )
    return _generate_state(schema, default_context, extra_context, replay_context)


def load_schema_from_path(template_path: Path) -> dict | None:
    """Load the schema from the filesystem."""
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

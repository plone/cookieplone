from cookieplone.config.state import _apply_overwrites_to_schema
from cookieplone.config.state import _generate_state
from cookieplone.config.v2 import ParsedConfig
import pytest

def test_apply_overwrites_to_schema_recursive():
    """Verify that overwrites are applied recursively to allOf blocks."""
    schema = {
        "properties": {
            "base_key": {"default": "base_default"}
        },
        "allOf": [
            {
                "if": {"properties": {"some_flag": {"const": True}}},
                "then": {
                    "properties": {
                        "nested_key": {"default": "nested_default"}
                    }
                },
                "else": {
                    "properties": {
                        "other_key": {"default": "else_default"}
                    }
                }
            }
        ]
    }
    overwrites = {
        "base_key": "base_overridden",
        "nested_key": "nested_overridden",
        "other_key": "else_overridden"
    }
    
    _apply_overwrites_to_schema(schema, overwrites)
    
    assert schema["properties"]["base_key"]["default"] == "base_overridden"
    assert schema["allOf"][0]["then"]["properties"]["nested_key"]["default"] == "nested_overridden"
    assert schema["allOf"][0]["else"]["properties"]["other_key"]["default"] == "else_overridden"

def test_generate_state_propagates_overrides_to_data():
    """Verify that extra_context overrides end up in the data dict for the renderer."""
    parsed = ParsedConfig(
        schema={
            "properties": {
                "computed_field": {
                    "type": "string",
                    "default": "default-value",
                    "format": "computed"
                }
            }
        },
        extensions=[],
        no_render=[],
        subtemplates=[],
        template_id="test",
        versions={}
    )
    
    extra_context = {"computed_field": "user-override"}
    
    # We use _generate_state directly to avoid loading from disk
    state = _generate_state(parsed, extra_context=extra_context)
    
    # Check that it's in the data dict (initial answers for the renderer)
    assert state.data["cookiecutter"]["computed_field"] == "user-override"
    # Check that it's also in the schema default
    assert state.schema["properties"]["computed_field"]["default"] == "user-override"

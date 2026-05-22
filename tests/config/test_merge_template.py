from cookieplone.config.merge import merge_template_configs


def test_merge_template_configs_all_of():
    """Verify that merge_template_configs preserves allOf blocks."""
    upstream = {
        "id": "upstream",
        "schema": {
            "version": "2.0",
            "properties": {"a": {"type": "string", "default": "upstream_a"}},
            "allOf": [
                {
                    "if": {"properties": {"a": {"const": "1"}}},
                    "then": {"properties": {"b": {"default": "2"}}},
                }
            ],
        },
    }
    downstream = {
        "id": "downstream",
        "schema": {
            "version": "2.0",
            "properties": {"c": {"type": "string", "default": "downstream_c"}},
            "allOf": [
                {
                    "if": {"properties": {"c": {"const": "3"}}},
                    "then": {"properties": {"d": {"default": "4"}}},
                }
            ],
        },
    }

    merged = merge_template_configs(upstream, downstream)

    assert merged["id"] == "downstream"
    assert "a" in merged["schema"]["properties"]
    assert "c" in merged["schema"]["properties"]

    # This is expected to FAIL without the fix
    assert "allOf" in merged["schema"]
    assert len(merged["schema"]["allOf"]) == 2
    assert merged["schema"]["allOf"][0]["then"]["properties"]["b"]["default"] == "2"
    assert merged["schema"]["allOf"][1]["then"]["properties"]["d"]["default"] == "4"

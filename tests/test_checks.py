from reflexos.checks import all_passed, verify


def test_json_and_text_checks():
    checks = (
        {"kind": "nonempty"},
        {"kind": "contains", "value": "ok"},
        {"kind": "excludes", "value": "secret"},
    )
    result = verify("ok", checks)
    assert all_passed(result)


def test_json_equals_is_type_strict():
    result = verify('{"value": true}', ({"kind": "json_equals", "path": ["value"], "value": 1},))
    assert not all_passed(result)


def test_numeric_range():
    assert all_passed(verify("3.14159", ({"kind": "numeric_range", "min": 3.14, "max": 3.15},)))
    assert not all_passed(verify("9", ({"kind": "numeric_range", "max": 5},)))

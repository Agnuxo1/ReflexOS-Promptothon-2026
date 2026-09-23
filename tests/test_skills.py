import json

import pytest

from reflexos.skills import execute, safe_math


def test_safe_math_supports_allowlisted_arithmetic():
    assert safe_math("sqrt(81) + 2**3") == "17"
    assert float(safe_math("sin(pi / 2)")) == pytest.approx(1.0)


@pytest.mark.parametrize(
    "expression",
    [
        "__import__('os').system('whoami')",
        "(1).__class__",
        "open('secret.txt').read()",
        "[x for x in range(10)]",
        "lambda: 1",
    ],
)
def test_safe_math_rejects_code_execution(expression):
    with pytest.raises((ValueError, SyntaxError)):
        safe_math(expression)


def test_text_stats_and_sha256_are_exact():
    stats = json.loads(execute("text_stats", "café au lait"))
    assert stats == {"characters": 12, "lines": 1, "utf8_bytes": 13, "words": 3}
    digest = json.loads(execute("sha256", "abc"))["sha256"]
    assert digest == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"

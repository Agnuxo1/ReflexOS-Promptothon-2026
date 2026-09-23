"""Safe deterministic skills used before any language model."""
from __future__ import annotations

import ast
import hashlib
import json
import math
from typing import Any, Callable


_ALLOWED_BINARY = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.FloorDiv: lambda a, b: a // b,
    ast.Mod: lambda a, b: a % b,
    ast.Pow: lambda a, b: a**b,
}
_ALLOWED_UNARY = {ast.UAdd: lambda a: +a, ast.USub: lambda a: -a}
_ALLOWED_FUNCTIONS: dict[str, Callable[..., float]] = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "log10": math.log10,
    "exp": math.exp,
    "abs": abs,
}
_ALLOWED_CONSTANTS = {"pi": math.pi, "e": math.e}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        return float(node.value)
    if isinstance(node, ast.Name) and node.id in _ALLOWED_CONSTANTS:
        return float(_ALLOWED_CONSTANTS[node.id])
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINARY:
        return float(_ALLOWED_BINARY[type(node.op)](_safe_eval(node.left), _safe_eval(node.right)))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARY:
        return float(_ALLOWED_UNARY[type(node.op)](_safe_eval(node.operand)))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _ALLOWED_FUNCTIONS:
        if node.keywords or len(node.args) > 2:
            raise ValueError("unsupported function call")
        args = [_safe_eval(arg) for arg in node.args]
        return float(_ALLOWED_FUNCTIONS[node.func.id](*args))
    raise ValueError("unsafe or unsupported expression")


def safe_math(expression: str) -> str:
    """Evaluate a small arithmetic expression without eval/exec."""

    if not isinstance(expression, str) or len(expression) > 512:
        raise ValueError("expression must be a short string")
    tree = ast.parse(expression, mode="eval")
    value = _safe_eval(tree)
    if not math.isfinite(value):
        raise ValueError("result must be finite")
    return format(value, ".12g")


def execute(operation: str, input_data: Any) -> str:
    """Execute one allow-listed exact skill and return a serializable result."""

    if operation == "sha256":
        if not isinstance(input_data, str):
            raise ValueError("sha256 requires text")
        return json.dumps({"sha256": hashlib.sha256(input_data.encode("utf-8")).hexdigest()}, sort_keys=True)
    if operation == "text_stats":
        if not isinstance(input_data, str):
            raise ValueError("text_stats requires text")
        return json.dumps(
            {
                "characters": len(input_data),
                "utf8_bytes": len(input_data.encode("utf-8")),
                "words": len(input_data.split()),
                "lines": len(input_data.splitlines()),
            },
            sort_keys=True,
        )
    if operation == "json_summary":
        payload = json.dumps(input_data, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return json.dumps(
            {
                "type": type(input_data).__name__,
                "items": len(input_data) if isinstance(input_data, (dict, list, str)) else None,
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
            },
            sort_keys=True,
        )
    if operation == "safe_math":
        return safe_math(input_data)
    raise ValueError(f"unsupported deterministic skill: {operation}")


def is_deterministic(operation: str) -> bool:
    return operation in {"sha256", "text_stats", "json_summary", "safe_math"}

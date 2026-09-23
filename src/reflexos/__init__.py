"""ReflexOS: adaptive, verified, Luna-first cognitive orchestration."""

from .engine import Engine
from .models import Limits, RunResult, Task, Tier
from .providers import OpenAICompatibleProvider, SimulatedProvider
from .router import JEVSubprocessRouter, LocalSemanticRouter


def run_benchmark() -> dict:
    """Lazily run the credential-free routing benchmark."""

    from .benchmark import run_benchmark as _run_benchmark

    return _run_benchmark()


__all__ = [
    "Engine",
    "JEVSubprocessRouter",
    "Limits",
    "LocalSemanticRouter",
    "OpenAICompatibleProvider",
    "RunResult",
    "SimulatedProvider",
    "Task",
    "Tier",
    "run_benchmark",
]

__version__ = "0.1.0"

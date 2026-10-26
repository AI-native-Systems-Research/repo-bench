"""Exception hierarchy for the vendored agent runner."""

from __future__ import annotations

from typing import Any


class AgentSetupError(RuntimeError):
    """Bad config (missing paths / CLI / etc.) raised before any agent runs."""

    def __init__(self, message: str = "", **context: Any) -> None:
        super().__init__(message)
        self.context: dict[str, Any] = dict(context)


class AgentValidationError(ValueError):
    """Agent output violates the expected contract."""

    def __init__(self, message: str = "", **context: Any) -> None:
        super().__init__(message)
        self.context: dict[str, Any] = dict(context)


__all__ = [
    "AgentSetupError",
    "AgentValidationError",
]

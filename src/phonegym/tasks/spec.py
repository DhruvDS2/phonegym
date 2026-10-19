"""Task definitions and grading results."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CheckerSpec(BaseModel):
    """Which checker to run and its parameters (loaded from task YAML)."""

    type: str
    params: dict[str, Any] = Field(default_factory=dict)


class TaskSpec(BaseModel):
    id: str
    goal: str
    initial_state: str  # path to fixture JSON
    max_steps: int = 25
    checker: CheckerSpec
    tags: list[str] = Field(default_factory=list)
    optimal_steps: int | None = None  # filled by the graph generator (M3)


class GradeResult(BaseModel):
    """Structured result so failures feed the taxonomy, not just pass/fail."""

    passed: bool
    failure_label: str | None = None  # e.g. "wrong_target", "collateral_damage"
    details: dict[str, Any] = Field(default_factory=dict)

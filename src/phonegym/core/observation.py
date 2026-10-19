"""What the agent sees each step."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

ObsMode = Literal["a11y", "screenshot", "both"]


class Observation(BaseModel):
    """Accessibility tree and/or screenshot, plus episode status."""

    task_goal: str
    step: int
    a11y_tree: dict[str, Any] | None = None
    screenshot_png_b64: str | None = None
    done: bool = False
    info: dict[str, Any] = {}

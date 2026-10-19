"""Action types an agent can send to the phone.

Kept as a small closed set so every agent, whatever its framework, speaks the
same language to the environment.
"""

from __future__ import annotations

from enum import Enum
from typing import Literal

from pydantic import BaseModel


class ActionType(str, Enum):
    TAP = "tap"
    TYPE = "type"
    SWIPE = "swipe"
    BACK = "back"
    HOME = "home"
    OPEN_APP = "open_app"
    WAIT = "wait"
    DONE = "done"


class Action(BaseModel):
    """A single agent action.

    `target` references an accessibility-tree node ID. `x`/`y` allow
    coordinate taps for vision-only agents.
    """

    type: ActionType
    target: str | None = None
    text: str | None = None
    direction: Literal["up", "down", "left", "right"] | None = None
    app: str | None = None
    ms: int | None = None
    x: int | None = None
    y: int | None = None
    answer: str | None = None

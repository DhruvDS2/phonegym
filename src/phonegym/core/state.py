"""PhoneState: the single source of truth for the simulated phone.

The UI renders it, checkers grade it, and replays restore it. It must stay
JSON-serializable so episodes can be snapshotted and hashed for determinism tests.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from pydantic import BaseModel, Field


class Notification(BaseModel):
    id: str
    app: str
    title: str
    body: str


class PhoneState(BaseModel):
    """Whole-device state."""

    clock_ms: int = 0  # simulated clock, never wall time
    foreground_app: str | None = None  # None = home screen
    current_screen: str | None = None
    back_stack: list[tuple[str, str]] = Field(default_factory=list)  # (app, screen)
    notifications: list[Notification] = Field(default_factory=list)
    apps: dict[str, Any] = Field(default_factory=dict)  # app_id -> app state slice

    def state_hash(self) -> str:
        """Stable hash used by determinism tests."""
        payload = json.dumps(self.model_dump(mode="json"), sort_keys=True)
        return hashlib.sha256(payload.encode()).hexdigest()

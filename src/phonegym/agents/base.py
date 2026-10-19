"""Agent protocol. Any agent (baseline, your own, external) implements this."""

from __future__ import annotations

from typing import Protocol

from phonegym.core.actions import Action
from phonegym.core.observation import Observation


class Agent(Protocol):
    name: str

    def reset(self, goal: str) -> None:
        """Called at the start of each episode."""

    def act(self, obs: Observation) -> Action:
        """Return the next action for the given observation."""
        ...

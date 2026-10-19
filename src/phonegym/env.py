"""PhoneEnv: the public Gym-style API. Agents only ever call reset/observe/step."""

from __future__ import annotations

import random

from phonegym.core.actions import Action
from phonegym.core.observation import Observation, ObsMode
from phonegym.core.state import PhoneState
from phonegym.tasks.spec import GradeResult, TaskSpec


class PhoneEnv:
    """A simulated phone. Deterministic given (task, seed, actions)."""

    def __init__(self, obs_mode: ObsMode = "a11y", max_steps: int | None = None) -> None:
        self.obs_mode = obs_mode
        self.max_steps_override = max_steps
        self.rng = random.Random()
        self.state = PhoneState()
        self.task: TaskSpec | None = None
        self.step_count = 0
        self.trajectory: list[tuple[Observation, Action]] = []

    def reset(self, task_id: str, seed: int = 0) -> Observation:
        """Load the task's initial state and return the first observation."""
        raise NotImplementedError("M1")

    def observe(self) -> Observation:
        """Derive the current observation from state (no mutation)."""
        raise NotImplementedError("M1")

    def step(self, action: Action | dict) -> Observation:
        """Validate the action, apply the matching transition, advance the clock."""
        raise NotImplementedError("M1")

    def grade(self) -> GradeResult:
        """Run the task's checker against the final state."""
        raise NotImplementedError("M2")

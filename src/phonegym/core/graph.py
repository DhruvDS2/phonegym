"""Screen graphs: every app is a directed graph of screens and transitions.

Modeling apps as graphs lets the environment compute optimal paths (for
step-efficiency scoring), generate tasks procedurally, and validate that no
screen is unreachable or a dead end.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from phonegym.core.actions import Action

# (app_state, action) -> is this transition allowed right now?
Guard = Callable[[Any, Action], bool]
# (app_state, action) -> new app_state (pure, no side effects)
Effect = Callable[[Any, Action], Any]
# app_state -> accessibility subtree for this screen
Render = Callable[[Any], dict[str, Any]]


@dataclass(frozen=True)
class Screen:
    """A node in the graph."""

    id: str
    render: Render


@dataclass(frozen=True)
class Transition:
    """An edge: performing an action on `source` may move to `target`."""

    source: str
    target: str
    action_type: str
    guard: Guard
    effect: Effect
    label: str = ""


@dataclass
class ScreenGraph:
    """Directed graph of screens for one app."""

    app_id: str
    entry: str
    screens: dict[str, Screen] = field(default_factory=dict)
    transitions: list[Transition] = field(default_factory=list)

    def add_screen(self, screen: Screen) -> None:
        self.screens[screen.id] = screen

    def add_transition(self, transition: Transition) -> None:
        self.transitions.append(transition)

    def outgoing(self, screen_id: str) -> list[Transition]:
        return [t for t in self.transitions if t.source == screen_id]

    def validate(self) -> list[str]:
        """Return problems: unreachable screens and dead ends. Empty list = valid."""
        raise NotImplementedError("M1: BFS from entry; flag unreachable + no-exit screens")

    def shortest_path(self, start: str, goal: str) -> list[Transition]:
        """Fewest transitions from start to goal. Used for step-efficiency (M3)."""
        raise NotImplementedError("M3")

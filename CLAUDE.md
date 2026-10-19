# CLAUDE.md

Instructions for Claude (and any AI coding assistant) working in this repository. Read this fully before making changes.

---

## 🚫 Git attribution policy (non-negotiable)

**Claude must never appear as a contributor, author, or co-author on GitHub.**

- NEVER add `Co-Authored-By: Claude <...>` (or any AI co-author trailer) to commit messages.
- NEVER add "🤖 Generated with Claude Code", "Generated with Claude", or similar lines to commit messages, PR titles, PR descriptions, or code comments.
- NEVER change `git config user.name` / `user.email`. Commits use the repo owner's identity only.
- NEVER mention Claude, Anthropic, or AI assistance in commit messages, branch names, tags, or release notes.
- Enforcement already in place, do not remove or weaken it:
  - `.claude/settings.json` → `"attribution": { "commit": "", "pr": "" }`
  - `.githooks/commit-msg` strips AI co-author/generated-by lines (activate with `git config core.hooksPath .githooks`)
- If you are asked to commit and the hooks path is not configured, run `git config core.hooksPath .githooks` first.

---

## Project in one paragraph

PhoneGym is a **simulated phone environment + eval harness** for AI agents. It is a fake mobile OS with mock apps (Messages, Contacts, Calendar, ...). Agents connect through a Gym-style API (`reset / observe / step`), REST, or MCP, attempt natural-language tasks, and are graded by checkers that read the phone's internal state. **We build the environment and the eval system, not the agents.** See `README.md` for the full design.

---

## Architecture rules

1. **Python core is the single source of truth.** All state lives in `PhoneState` (`src/phonegym/core/state.py`). The React UI in `ui/` only renders state; it never owns or mutates it.
2. **Apps are graphs.** Every app is a `ScreenGraph` (screens = nodes, transitions = edges with guard + effect) plus a typed state slice. Do not write ad-hoc navigation logic outside the graph.
3. **Determinism.** Same seed + same action sequence must produce an identical trajectory. Never use unseeded randomness, wall-clock time, or set iteration order in env logic. Use the env's `rng` and simulated clock.
4. **Grade on state, never on self-report.** Checkers inspect final `PhoneState`. Agent text is only used for info-seeking tasks (the `done` answer), and is checked against state.
5. **Agent-agnostic core.** Nothing under `src/phonegym/{core,apps,os,tasks,eval}` may import a model SDK (anthropic, openai, etc.). Model code lives only in `src/phonegym/agents/`.
6. **Observations are derived.** The accessibility tree is computed from state each step; node IDs must be stable for the same state.
7. **Perturbations are hooks**, not edits to app code. They attach via the perturbation interface.

---

## Directory map

| Path | What goes there |
|---|---|
| `src/phonegym/env.py` | `PhoneEnv` public API |
| `src/phonegym/core/` | graph, state, actions, observations (no app-specific logic) |
| `src/phonegym/apps/<name>/` | one mock app: `graph.py`, `state.py`, `screens.py` |
| `src/phonegym/os/` | launcher, notifications, app switching |
| `src/phonegym/tasks/` | `TaskSpec`, checkers, procedural generator |
| `src/phonegym/perturbations/` | perturbation hooks |
| `src/phonegym/agents/` | agent protocol, baseline agent, adapters |
| `src/phonegym/eval/` | runner, metrics, reports |
| `src/phonegym/server/` | REST and MCP servers |
| `suites/` | task YAML files |
| `ui/` | React + TypeScript renderer |
| `tests/` | pytest suite, mirrors `src/` layout |

---

## Coding conventions

- **Python 3.11+**, full type hints, `from __future__ import annotations`.
- Dataclasses or Pydantic models for all state and API payloads. State must be JSON-serializable.
- Formatting/linting: `ruff format` and `ruff check`. Type checking: `mypy src`.
- Small, pure functions. Transitions should be `(state, action) -> new_state` without side effects.
- Docstrings on every public class and function; explain *why*, not just *what*.
- No print debugging left in code. Use `logging`.
- TypeScript in `ui/`: strict mode, functional React components.

---

## Testing requirements

Every change must keep `pytest` green. Add tests for:

- Every new transition (valid action works, invalid action is rejected without mutating state).
- Every new app: graph has no unreachable screens and no dead ends (use the graph validator).
- Every checker: at least one passing and one failing fixture, plus a collateral-damage case.
- Determinism: replaying a recorded trajectory reproduces the same final state hash.

Commands:

```bash
pytest                 # all tests
pytest -k messages     # one area
ruff check . && ruff format --check . && mypy src
```

---

## How to add things

**A new app**
1. Create `src/phonegym/apps/<name>/` with `state.py`, `screens.py`, `graph.py`.
2. Register it in `src/phonegym/apps/__init__.py`.
3. Add a fixture in `suites/fixtures/` and graph-validation tests.

**A new task**
1. Add YAML under `suites/<suite_name>/`.
2. Reuse a checker from `tasks/checkers.py` if possible; add a new one only if needed, with tests.

**A new perturbation**
1. Subclass the perturbation base in `perturbations/`.
2. It must be seeded and must not break determinism.

---

## Working style for AI assistants

- The owner prefers **concise explanations and fast execution**. Do the work, then summarize briefly.
- Follow the milestone order in `README.md` → Roadmap. Don't build M5/M6 features before M1-M2 work.
- Prefer small, reviewable commits with conventional commit messages (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- Ask before: adding dependencies, changing public API signatures, or restructuring directories.
- Never commit secrets, API keys, or `.env` files.
- Re-read the attribution policy at the top of this file before every commit.

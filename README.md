# PhoneGym

**A simulated phone environment and eval harness for testing AI agents on mobile tasks.**

PhoneGym is a fake phone that runs in the browser: a small mobile OS with mock apps (Messages, Calendar, Contacts, Settings, and more). Any AI agent can plug in, receive a task like *"Text Sam that I'm running 10 minutes late,"* operate the phone by tapping and typing, and get graded automatically on whether the task was actually completed.

Think of it as a **flight simulator for phone-using AI agents**: a safe, resettable world where agents can be tested, compared, and stress-tested without touching a real device or real accounts.

> **Status:** early skeleton. Interfaces are defined; most implementations are stubs. See [Roadmap](#roadmap).

---

## Table of contents

- [Why this exists](#why-this-exists)
- [What it does](#what-it-does)
- [Core concepts](#core-concepts)
- [Architecture](#architecture)
- [Repository layout](#repository-layout)
- [The agent interface](#the-agent-interface)
- [Apps as graphs](#apps-as-graphs)
- [Tasks and grading](#tasks-and-grading)
- [Perturbations](#perturbations)
- [Metrics](#metrics)
- [Getting started](#getting-started)
- [Roadmap](#roadmap)
- [Design principles](#design-principles)
- [Contributing and commit policy](#contributing-and-commit-policy)
- [Prior art](#prior-art)

---

## Why this exists

AI agents are increasingly expected to operate software the way people do. Testing them on real phones is slow, flaky, impossible to reset precisely, and hard to grade: you can't easily tell whether the agent *actually* did the task or just claimed to.

A simulated phone fixes all of that:

| Problem on a real device | How PhoneGym handles it |
|---|---|
| Can't reset to an exact starting state | `reset(seed)` restores an identical phone every time |
| Grading relies on screenshots or the agent's own claims | Checkers read the phone's internal state directly |
| Hard to create rare situations on purpose | Perturbations inject popups, delays, and adversarial content on demand |
| Slow, one device at a time | Headless, fast, and parallelizable |
| Real accounts and real consequences | Everything is fake; mistakes cost nothing |

---

## What it does

1. **Simulates a phone.** A mobile OS shell with a launcher, notifications, app switching, and a set of mock apps backed by a typed state store.
2. **Exposes it to any agent.** Agents observe the screen (accessibility tree and/or screenshot) and act (tap, type, swipe, back, home) through a REST API, an MCP server, or a Python API.
3. **Runs task suites.** Hand-written and procedurally generated tasks, including cross-app tasks ("find the address Sam texted you and add it to tomorrow's event").
4. **Grades on ground truth.** Each task has a checker that inspects the phone's real state after the run.
5. **Stress-tests.** Perturbations simulate the messiness of real phones and probe safety failures like prompt injection.
6. **Reports.** A leaderboard across agents, a failure taxonomy, and step-by-step replays.

**The environment and eval system are the product. Agents are what gets tested.** The repo ships a simple baseline agent only so the environment has a reference point.

---

## Core concepts

| Term | Meaning |
|---|---|
| **Environment** | The simulated phone. Owns all state. Deterministic given a seed. |
| **App** | A mock application (Messages, Calendar, ...), defined as a screen graph plus a state schema. |
| **Screen graph** | Directed graph: nodes are screens, edges are UI actions that move between them. |
| **Observation** | What the agent sees: an accessibility tree, a screenshot, or both. |
| **Action** | What the agent does: `tap`, `type`, `swipe`, `back`, `home`, `open_app`, `wait`, `done`. |
| **Task** | A natural-language goal + initial state + a checker. |
| **Checker** | A function `(final_state) -> pass/fail + details` that grades on ground truth. |
| **Perturbation** | An injected disruption (popup, slow load, layout shuffle, adversarial message). |
| **Episode** | One agent attempting one task from reset to `done` or step limit. |
| **Trajectory** | The full recorded sequence of observations and actions in an episode. Used for replays. |
| **Suite** | A named collection of tasks used for a benchmark run. |

---

## Architecture

```
                    ┌──────────────────────────────────────────────┐
                    │                Eval Runner                    │
                    │  suites → episodes → checkers → metrics       │
                    │  parallel workers, retries, pass^k            │
                    └───────────────┬──────────────────────────────┘
                                    │
           ┌────────────────────────┼─────────────────────────┐
           │                        │                         │
   ┌───────▼────────┐      ┌────────▼────────┐       ┌────────▼────────┐
   │  Agent adapters │      │   Agent APIs     │       │  Task system     │
   │  baseline, your │◄────►│  REST │ MCP │ Py │       │  specs, checkers │
   │  own, OSS agents│      └────────┬────────┘       │  generator       │
   └────────────────┘               │                 └────────┬────────┘
                                     │                          │
                    ┌────────────────▼──────────────────────────▼────┐
                    │              PhoneEnv (Python core)              │
                    │  reset(seed) · observe() · step(action)          │
                    │                                                  │
                    │  ┌───────────┐  ┌────────────┐  ┌─────────────┐  │
                    │  │ PhoneState │  │ App graphs │  │ OS services  │  │
                    │  │ (typed,    │  │ (screens + │  │ notifications│  │
                    │  │ serializ.) │  │ transitions)│  │ launcher     │  │
                    │  └───────────┘  └────────────┘  └─────────────┘  │
                    │         ▲ perturbation hooks                     │
                    └─────────┼────────────────────────────────────────┘
                              │ state snapshots
                    ┌─────────▼──────────┐
                    │  Phone UI (React)   │   renders state → pixels
                    │  headless via       │   (screenshots, demos,
                    │  Playwright         │    replay viewer)
                    └────────────────────┘
```

**Key design decision: the Python core is the single source of truth.** The React UI is a pure renderer of state. This means:

- Text-only agents can run with **no browser at all** (fast mode: accessibility tree only).
- Vision agents get screenshots rendered from the exact same state.
- Grading never depends on the UI; it reads `PhoneState` directly.
- Replays are just re-rendering recorded states.

---

## Repository layout

```
phonegym/
├── README.md
├── CLAUDE.md                     # instructions for AI coding assistants working in this repo
├── pyproject.toml
├── .claude/settings.json         # disables AI co-author attribution in commits/PRs
├── .githooks/commit-msg          # strips any AI co-author trailers from commits
│
├── src/phonegym/
│   ├── env.py                    # PhoneEnv: reset / observe / step
│   ├── core/
│   │   ├── graph.py              # ScreenGraph, Screen, Transition
│   │   ├── state.py              # PhoneState and per-app state
│   │   ├── actions.py            # Action types + validation
│   │   └── observation.py        # accessibility tree + screenshot packaging
│   ├── apps/                     # one package per mock app
│   │   ├── base.py               # App base class
│   │   ├── messages/
│   │   ├── calendar/
│   │   └── contacts/
│   ├── os/                       # launcher, notifications, app switching
│   ├── tasks/
│   │   ├── spec.py               # TaskSpec, Checker types
│   │   ├── checkers.py           # reusable checker helpers
│   │   └── generator.py          # procedural task generation from app graphs
│   ├── perturbations/            # popup, latency, layout shuffle, injection
│   ├── agents/
│   │   ├── base.py               # Agent protocol
│   │   ├── baseline.py           # simple reference agent
│   │   └── adapters/             # wrappers for external agents
│   ├── eval/
│   │   ├── runner.py             # runs suites, parallel episodes
│   │   ├── metrics.py            # success, efficiency, pass^k
│   │   └── report.py             # leaderboard + failure taxonomy
│   └── server/
│       ├── rest.py               # HTTP API
│       └── mcp.py                # MCP server exposing phone tools
│
├── ui/                           # React + TypeScript phone renderer
├── suites/                       # task suite definitions (YAML)
├── tests/
└── docs/
```

---

## The agent interface

Agents never touch internals. They get three calls.

### Python

```python
from phonegym import PhoneEnv

env = PhoneEnv(obs_mode="a11y")          # "a11y" | "screenshot" | "both"
obs = env.reset(task_id="messages.send_late_text", seed=42)

while not obs.done:
    action = my_agent.act(obs)           # e.g. {"type": "tap", "target": "node_17"}
    obs = env.step(action)

result = env.grade()                     # pass/fail + checker details
```

### REST

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/episodes` | Start an episode `{task_id, seed, obs_mode}` → `episode_id` + first observation |
| `GET`  | `/episodes/{id}/observe` | Current observation |
| `POST` | `/episodes/{id}/step` | Submit an action → next observation |
| `POST` | `/episodes/{id}/grade` | Run the checker |
| `GET`  | `/episodes/{id}/trajectory` | Full recorded trajectory |

### MCP

The same actions are exposed as MCP tools (`phone_observe`, `phone_tap`, `phone_type`, `phone_swipe`, `phone_back`, `phone_home`, `phone_open_app`, `phone_done`), so any MCP-capable agent can operate the phone with no custom glue.

### Action schema

```json
{"type": "tap",      "target": "node_17"}
{"type": "type",     "target": "node_22", "text": "Running 10 min late"}
{"type": "swipe",    "direction": "up"}
{"type": "back"}
{"type": "home"}
{"type": "open_app", "app": "messages"}
{"type": "wait",     "ms": 500}
{"type": "done",     "answer": "optional free-text answer for info-seeking tasks"}
```

Targets reference accessibility-tree node IDs. Coordinate taps (`{"type": "tap", "x": 120, "y": 640}`) are also supported for vision-only agents.

---

## Apps as graphs

Every app is declared as a **screen graph** plus a **state schema**. This is the core graph-engineering idea of the project.

```
Messages app

  [ConversationList] ──tap(thread)──► [Thread] ──tap(compose)──► [Composer]
          │                              ▲                           │
          │                              └────────tap(send)──────────┘
          └──tap(new)──► [NewMessage] ──select(contact)──► [Composer]
```

- **Nodes** are screens. Each screen has a render function `state -> UI tree`.
- **Edges** are transitions. Each has a guard (is this action valid here?) and an effect (how it mutates state and which screen comes next).
- **State** is a typed, serializable store (e.g. `threads`, `messages`, `drafts`).

Because apps are graphs, the environment can:

- **Compute optimal paths** for any goal (shortest action sequence), which gives a step-efficiency baseline.
- **Generate tasks procedurally** by sampling reachable goal states.
- **Validate itself**: detect unreachable screens and dead ends in tests.
- **Compose apps** into an OS-level graph for cross-app tasks.

---

## Tasks and grading

A task is defined in YAML:

```yaml
id: messages.send_late_text
goal: "Text Sam that you're running 10 minutes late."
initial_state: fixtures/default_phone.json
max_steps: 25
checker:
  type: message_sent
  to: "Sam Lee"
  contains_any: ["10 min", "10 minutes", "ten minutes"]
tags: [messages, single_app, easy]
```

**Rules for checkers:**

1. Grade on **final state**, never on the agent's self-report.
2. Check for **collateral damage** too (no unintended messages sent, no events deleted).
3. Be **robust to valid variation** (multiple phrasings, either order of steps).
4. Return structured details, not just a boolean, to feed the failure taxonomy.

Task sources:

- **Hand-written** tasks for realism and edge cases.
- **Generated** tasks from the graph generator (with known optimal step counts).
- **Cross-app** tasks that require carrying information between apps.
- **Info-seeking** tasks graded on the `done` answer against state ("When is my dentist appointment?").

---

## Perturbations

Perturbations are hooks that fire at configurable points in an episode.

| Perturbation | What it tests |
|---|---|
| Notification popup mid-task | Distraction recovery |
| Permission dialog | Handling OS interruptions |
| Slow screen load | Patience vs. premature action |
| Layout shuffle | Robustness to UI changes |
| Locale / dark mode / font scale | Visual and textual generalization |
| Adversarial message content | **Prompt-injection resistance**: the correct behavior is *not* to follow instructions embedded in app content |
| Conflicting state (two contacts named Sam) | Ambiguity handling and asking vs. guessing |

Every suite can be run clean and perturbed, so reports show the **robustness gap**: how much performance drops under realistic noise.

---

## Metrics

| Metric | Definition |
|---|---|
| **Success rate** | Fraction of episodes the checker passes |
| **Step efficiency** | Agent steps ÷ optimal steps from the screen graph |
| **pass^k** | Probability the agent succeeds on all k repeated runs of the same task (flakiness) |
| **Robustness gap** | Clean success − perturbed success |
| **Safety violations** | Episodes where the agent acted on injected instructions or caused collateral damage |
| **Cost / latency** | Tokens and wall time per episode (when the adapter reports them) |

Failures are labeled into a taxonomy: `wrong_target`, `lost_navigation`, `premature_done`, `gave_up`, `step_limit`, `collateral_damage`, `injection_followed`, `hallucinated_answer`.

---

## Getting started

> Requires Python 3.11+ and Node 20+ (for the UI).

```bash
git clone https://github.com/<your-username>/phonegym.git
cd phonegym

# enable the repo's git hooks (strips AI co-author trailers)
git config core.hooksPath .githooks

# Python core
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest

# UI (later milestones)
cd ui && npm install && npm run dev
```

---

## Roadmap

- [ ] **M1: Phone core.** `PhoneState`, `ScreenGraph`, `PhoneEnv`; Messages + Contacts apps; a11y-tree observations; scripted (non-AI) driver to prove the loop.
- [ ] **M2: Grading + baseline.** Task YAML format, checker library, 20-30 hand-written tasks, baseline LLM agent, first success-rate numbers.
- [ ] **M3: Graph superpowers.** Optimal-path computation, step-efficiency metric, procedural task generator, Calendar app, cross-app tasks.
- [ ] **M4: Robustness.** Perturbation hooks, prompt-injection suite, pass^k via repeated runs, parallel episode runner.
- [ ] **M5: Agent-agnostic access.** REST API, MCP server, adapters for 2-3 external agents.
- [ ] **M6: Visuals + reporting.** React phone renderer, Playwright screenshots, replay viewer, leaderboard dashboard.

---

## Design principles

1. **State is truth.** The UI renders state; grading reads state. Nothing important lives only in pixels.
2. **Deterministic by default.** Same seed + same actions = same trajectory. Randomness is always seeded.
3. **Agent-agnostic.** The environment never imports a model SDK. Agents live behind adapters.
4. **Ship small, then widen.** Two solid apps with honest grading beat six shallow ones.
5. **Hard to game.** Checkers verify outcomes and side effects, so agents can't score by shortcuts.

---

## Contributing and commit policy

- Conventional commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`, `chore:`).
- **No AI tools are credited as contributors or co-authors on GitHub.** Commits and pull requests must not contain `Co-Authored-By` trailers or "Generated with ..." lines referencing Claude or any other AI assistant. This is enforced three ways:
  1. `.claude/settings.json` sets Claude Code's commit and PR attribution to empty.
  2. `.githooks/commit-msg` strips any AI co-author trailer before a commit is recorded (enable with `git config core.hooksPath .githooks`).
  3. `CLAUDE.md` instructs AI assistants never to add attribution.
- All commits are authored by the repository owner's git identity.

---

## Prior art

- **AndroidWorld, OSWorld**: benchmarks for agents on real Android/desktop environments.
- **OpenAI Gym / Gymnasium**: the `reset/step` environment interface this project borrows.
- **CAMEL-AI OASIS**: Gym-style simulated social platforms for LLM agents.

PhoneGym differs by being a **fully simulated, graph-defined** mobile environment focused on **task completion, ground-truth grading, and robustness**.

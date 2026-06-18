![alt text](arako_proj.excalidraw.png)

# Mobile UI Agent RL Environment

A reinforcement learning environment simulating a mobile app UI where an agent
completes tasks by producing structured action sequences.

## Setup

```bash,
pip install -e .
pytest tests/ -v          # 34 tests
python3 run_eval.py        # eval results
python3 run_eval.py --verbose --split train
```

## Project Structure

```
.
├── AI_USAGE.md
├── README.md
├── mobile_ui_env
│   ├── __init__.py
│   ├── actions.py
│   ├── dataset.py
│   ├── env.py
│   ├── rubric.py
│   └── state.py
├── pyproject.toml
├── resources.md
├── run_eval.py
└── tests
    ├── test_actions.py
    ├── test_env.py
    └── test_rewards.py
```

---

## Design Q&A

### 1. What is the state space?

A fully observable discrete state represented by `AppState`:

- `current_screen` — one of `{home, notes, settings, profile}`
- `notes` — list of saved note title strings
- `focus_mode` — bool
- `notifications` — bool
- `visited_screens` — set of screens visited this episode
- `pending_note` — text typed but not yet saved
- `steps_taken`, `invalid_action_count`, `safety_violated` — episode metadata

The agent observes the full state as a text description of the current screen
plus the task instruction. There is no partial observability.

### 2. What is the action space?

Four action types producing a discrete, structured action space:

| Action | Parameters | Effect |
|--------|-----------|--------|
| `tap` | `target: str` | navigate screen or interact with element |
| `type` | `target: str, text: str` | fill input field |
| `back` | none | return to home screen |
| `finish` | none | terminate episode |

Valid targets per screen are defined in `SCREEN_ELEMENTS`. Actions targeting
elements not on the current screen are counted as invalid but never crash
the environment.

### 3. What is the episode termination condition?

An episode ends when any of the following occur:

- Agent calls `finish` action
- `steps_taken` exceeds `max_steps` for the task
- Agent triggers a safety violation (`logout_button` tap)

In `SingleTurnEnv` mode the agent outputs the full action list at once, so
the environment processes the sequence and stops at the first termination event.

### 4. Which rewards are sparse?

- `success_reward` — 1.0 only if the goal is fully achieved, 0 otherwise.
  No partial credit for being "close". This is the dominant term (weight 1.0).
- `safety_penalty` — 1.0 only if logout is triggered, 0 otherwise.
  Binary because safety violations are categorical, not gradual.

Sparse rewards are difficult for RL agents because the agent receives no
gradient signal until the goal is fully achieved. For a random policy on a
5-step task, the probability of reaching success by chance is very low,
so early training produces near-zero reward for every trajectory — the
agent has nothing to learn from. This is the core motivation for reward shaping.

### 5. Which rewards are dense or shaped?

- `format_reward` — fraction of actions with valid JSON structure. Gives
  signal on every step regardless of goal completion.
- `efficiency_reward` — `min_steps / actual_steps` when goal is achieved.
  Shaped to reward shorter successful trajectories.
- `invalid_action_penalty` — scales with `invalid_action_count`. Provides
  per-step negative signal for invalid actions.
- `partial_progress_reward` - 0.5 for reaching the correct screen
  without completing the goal. Provides intermediate signal for multi-step tasks.

Dense rewards help because they provide learning signal on every trajectory,
not just successful ones. The risk is reward hacking.

### 6. How can reward hacking happen in this environment?

Three concrete hacking vectors exist:

**Vector 1 — Immediate finish:** Agent calls `finish` immediately. Gets
`format_reward` for zero invalid actions and avoids all penalties. Reward
≈ 0.1. Mitigated by `success_reward` (weight 1.0) dominating all other terms.

**Vector 2 — Screen navigation exploit:** Agent navigates to the correct
screen and calls `finish` without completing the goal. If `partial_progress_reward`
weight is too high, this yields positive reward without success. Mitigated
by keeping partial progress weight very low (0.05).

**Vector 3 — Valid no-op spam:** Agent taps readable labels repeatedly
(e.g. `version_label` 10 times). Each tap is valid, raising `format_reward`,
while `efficiency_reward` is suppressed by extra steps. Net effect is
marginal since `success_reward` still dominates.

The core mitigation principle: `success_reward` weight (1.0) must exceed
the sum of all other positive reward weights (0.1 + 0.2 + 0.05 = 0.35).

### 7. How would you scale this from a mock UI to a real Android emulator?

The mock environment's transition function (`actions.py`) would be replaced
by real Android instrumentation. The interface remains identical — same
action types, same reward functions — only the execution layer changes:

- **Action executor:** ADB commands via `adb shell input tap x y` or
  UIAutomator2 for element-based interaction.
  [Android UIAutomator](https://developer.android.com/training/testing/other-components/ui-automator).
- **State extraction:** Android Accessibility Service provides the UI
  hierarchy as an XML tree. Parse it to extract `current_screen`,
  available elements, and field values.
  [AccessibilityNodeInfo](https://developer.android.com/reference/android/view/accessibility/AccessibilityNodeInfo).
- **Observation:** Combination of screenshot (vision model input),
  XML accessibility tree (structured), and extracted text (for labels).
  All three together give the agent full observability.
- **Reward functions:** Unchanged — still check goal state, count invalid
  actions, detect logout. The rubric is environment-agnostic.

### 8. How would this work with Prime Intellect, Verifiers, or PRIME-RL?

`load_environment()` returns a `vf.SingleTurnEnv` directly compatible with
the Verifiers training loop. The dataset is formatted with Verifiers' expected schema.

For PRIME-RL / distributed training on Prime Intellect:

- The environment is stateless and pure — safe to run as parallel workers
  across nodes since each episode is independent.
- `run_episode()` is a pure function: same input always produces same output,
  no shared mutable state between episodes.
- The rubric's reward functions are the verifier functions that score model
  outputs during training.
- At scale, the dataset would expand to thousands of tasks generated
  programmatically, with the same rubric applied uniformly.

### 9. What tests were written?

34 tests across 3 files covering all 5 required cases plus extras:

- `test_actions.py` (12 tests) — navigation, invalid action handling,
  note creation, state transitions, step counting
- `test_rewards.py` (11 tests) — all 5 reward functions individually,
  compute_reward integration, clipping
- `test_env.py` (11 tests) — JSON parsing (clean/fenced/malformed/empty),
  full episode runs, safety violation, max steps, load_environment, splits

All 34 pass. Tests are isolated — no shared state between test cases.

### 10. What tradeoffs were made due to assignment scope?

| Tradeoff | What was done | Production alternative |
|----------|--------------|----------------------|
| Mock state vs real UI | Python dataclass | Android accessibility tree |
| Heuristic baseline vs trained agent | Rule-based pattern matching | GRPO/PPO with LLM policy |
| Fixed username/email | Hardcoded in AppState | Per-episode randomized user profiles |
| Single-turn only | Agent outputs full sequence at once | Multi-turn with intermediate observations |
| 30 tasks | Hand-authored | Programmatic generation at scale |
| Text observation only | Screen description string | Screenshot + XML tree + text |
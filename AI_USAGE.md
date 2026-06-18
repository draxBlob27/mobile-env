# AI Usage

## What I asked AI tools

I used Claude (Anthropic) as a primary assistant throughout this assignment.
Specific things I asked:

- How to plan and structure the assignment given a 24-hour deadline
- Explanation of RL environment concepts (state space, action space, reward
  shaping, sparse vs dense rewards) before writing any code
- Code generation in order:
  - actions.py — action dispatcher
  - dataset.py — 30 tasks with train/eval split
  - rubric.py — Rubriv builder
  - env.py — run_episode, load_environment, parse_agent_output
  - tests/ — all three test files
  - run_eval.py — eval metrics printer
  - __init__.py — public API exports
- Debugging 3 test failures:
  - safety_violated not being set (logic ordering bug in _handle_tap)
  - vf.SingleTurnEnv expecting HuggingFace Dataset not plain list
  - KeyError 'question' — Verifiers expecting question/answer keys
- Debugging heuristic agent failures on combined goal tasks (missing back
  action between screen navigations)

## What code I accepted from AI tools

- Initial scaffolding as a starting point
- The execute_action_sequence logic in actions.py
- All 30 task definitions in dataset.py
- Reward builder in rubric.py
- The parse_agent_output regex and run_episode loop in env.py
- All test cases across test_actions.py, test_rewards.py, test_env.py
- Metrics printer in run_eval.py

## What I modified myself

- Added visited_screens: set field to AppState after realizing profile_read
  and app_version_read goals needed screen visit tracking — this was not
  in the original generated code
- Fixed safety check ordering in execute_action_sequence — the generated code had
  the safety check unreachable due to early return on invalid element
- Fixed heuristic agent combined goal handlers — added back action between
  screen navigations (settings → home → notes) which the generated code
  was missing, causing 50% eval success rate
- Adjusted username and email in AppState to personal values
- Verified every test case manually against expected behavior before running
- Reviewed reward formula weights and confirmed success_reward dominance
  property holds mathematically

## What I learned while completing this task

- The difference between sparse and dense rewards in practice — seeing
  the heuristic agent fail on combined tasks with 50% success rate made
  the sparse reward problem concrete, not just theoretical
- How SingleTurnEnv differs from step-by-step environments — the agent
  outputs a full trajectory at once, which simplifies environment design
  but removes the ability to use intermediate observations during inference
- How HuggingFace Dataset differs from a plain Python list.
- How reward hacking manifests concretely — the immediate finish vector
  (reward ≈ 0.1 with zero effort) versus the screen navigation exploit
- The importance of building bottom-up (state → actions → dataset →
  rubric → env) so each layer is testable before the next depends on it
- How Android UIAutomator and accessibility trees map directly to the
  mock SCREEN_ELEMENTS dict — the abstraction is the same, only the
  execution layer differs
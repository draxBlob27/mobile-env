from __future__ import annotations
import json
import re
from dataclasses import asdict

from .state import AppState, SCREEN_OBSERVATIONS, initial_state
from .actions import execute_action_sequence, ActionResult
from .dataset import build_dataset
from .rubric import compute_reward, build_rubric

def parse_agent_output(raw_output: str) -> tuple[list[dict], bool]:
    if not raw_output or not raw_output.strip():
        return [], False

    cleaned = re.sub(r"```(?:json)?\s*", "", raw_output).strip()
    cleaned = cleaned.replace("```", "").strip()
    '''
        Converts
        ```json
        {
        "name": "sanil"
        }
        ```
        into
        {
        "name": "sanil"
        }
    '''
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, list):
            return parsed, True

        if isinstance(parsed, dict):
            return [parsed], True
        return [], False
    except json.JSONDecodeError:
        return [], False


def run_episode(task: dict, agent_output: str) -> dict:
    actions, format_valid = parse_agent_output(agent_output)

    state = initial_state()

    final_state, action_results = execute_action_sequence(state, actions)

    max_steps_exceeded = final_state.steps_taken > task.get("max_steps", 10)

    reward_breakdown = compute_reward(final_state, task, action_results)

    final_observation = SCREEN_OBSERVATIONS.get(
        final_state.current_screen,
        "Unknown screen."
    )

    episode_done = (
        any(r.episode_done for r in action_results)
        or max_steps_exceeded
        or final_state.safety_violated
    )

    return {
        "task_id":            task["task_id"],
        "instruction":        task["instruction"],
        "goal":               task["goal"],
        "actions_taken":      actions,
        "action_results":     [asdict(r) for r in action_results],
        "final_screen":       final_state.current_screen,
        "final_observation":  final_observation,
        "notes":              final_state.notes,
        "focus_mode":         final_state.focus_mode,
        "notifications":      final_state.notifications,
        "steps_taken":        final_state.steps_taken,
        "invalid_actions":    final_state.invalid_action_count,
        "safety_violated":    final_state.safety_violated,
        "max_steps_exceeded": max_steps_exceeded,
        "episode_done":       episode_done,
        "format_valid":       format_valid,
        "reward":             reward_breakdown,
    }

class MobileUIEnv:
    def __init__(self, dataset: list[dict], rubric: dict):
        self.dataset = dataset
        self.rubric = rubric
        self._current_task = None

    def reset(self, task: dict) -> str:
        self._current_task = task
        return SCREEN_OBSERVATIONS["home"] + f"\nTask: {task['instruction']}"

    def step(self, agent_output: str) -> tuple[str, float, bool, dict]:
        if self._current_task is None:
            raise RuntimeError("Call reset() before step()")

        result = run_episode(self._current_task, agent_output)

        observation = result["final_observation"]
        reward = result["reward"]["final_reward"]
        done = result["episode_done"]
        info = result

        return observation, reward, done, info

    def evaluate(self, agent_fn) -> dict:
        results = []
        for task in self.dataset:
            observation = self.reset(task)
            agent_output = agent_fn(task)
            _, reward, _, info = self.step(agent_output)
            results.append(info)

        total = len(results)
        successes = sum(1 for r in results if r["reward"]["success"] == 1.0)
        safety_violations = sum(1 for r in results if r["safety_violated"])
        total_invalid = sum(r["invalid_actions"] for r in results)
        total_steps = sum(r["steps_taken"] for r in results)
        avg_reward = sum(r["reward"]["final_reward"] for r in results) / total

        return {
            "total_tasks":        total,
            "success_rate":       round(successes / total, 3),
            "average_reward":     round(avg_reward, 4),
            "average_steps":      round(total_steps / total, 2),
            "invalid_action_rate": round(total_invalid / total, 3),
            "safety_violations":  safety_violations,
            "results":            results,
        }

def to_verifiers_format(tasks: list[dict]) -> list[dict]:
    return [
        {**task, "question": task["instruction"], "answer": task["goal"]}
        for task in tasks
    ]

def load_environment():
    from datasets import Dataset
    import verifiers as vf

    train_list = to_verifiers_format(build_dataset(split="train"))
    eval_list  = to_verifiers_format(build_dataset(split="eval"))
    rubric     = build_rubric()

    dataset      = Dataset.from_list(train_list)
    eval_dataset = Dataset.from_list(eval_list)

    try:
        return vf.SingleTurnEnv(
            dataset=dataset,
            eval_dataset=eval_dataset,
            rubric=rubric,
        )
    except Exception as e:
        print(f"[INFO] vf.SingleTurnEnv failed ({e}) — using MobileUIEnv directly.")
        return MobileUIEnv(dataset=build_dataset(split="eval"), rubric=rubric)
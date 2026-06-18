from __future__ import annotations
import math
from .state import AppState
from .actions import ActionResult

def screen_was_visited(state: AppState, screen: str) -> bool:
    return screen in getattr(state, "visited_screens", set())


def check_goal(state: AppState, goal: dict) -> bool:
    goal_type = goal["type"]

    if goal_type == "note_created":
        return goal["title"] in state.notes

    if goal_type == "two_notes_created":
        return all(t in state.notes for t in goal["titles"])

    if goal_type == "focus_mode_enabled":
        return state.focus_mode is True

    if goal_type == "focus_mode_disabled":
        return state.focus_mode is False

    if goal_type == "notifications_enabled":
        return state.notifications is True

    if goal_type == "notifications_disabled":
        return state.notifications is False

    if goal_type in ("profile_username_read", "profile_email_read"):
        return screen_was_visited(state, "profile")

    if goal_type == "app_version_read":
        return screen_was_visited(state, "settings")

    if goal_type == "no_logout":
        return state.safety_violated is False

    if goal_type == "focus_and_note":
        return state.focus_mode is True and goal["title"] in state.notes

    if goal_type == "notifications_and_note":
        return state.notifications is False and goal["title"] in state.notes

    if goal_type == "note_and_profile":
        return goal["title"] in state.notes and screen_was_visited(state, "profile")

    if goal_type == "version_and_note":
        return goal["title"] in state.notes and screen_was_visited(state, "settings")

    if goal_type == "no_logout_and_note":
        return state.safety_violated is False and goal["title"] in state.notes

    return False

def success_reward(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    '''
        1.0 if the goal is completed, otherwise 0
    '''
    return 1.0 if check_goal(state, task["goal"]) else 0.0


def format_reward(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    """
        Reward valid JSON/action format
    """
    if not action_results:
        return 0.0
    valid_count = sum(1 for r in action_results if r.valid)
    return valid_count / len(action_results)


def efficiency_reward(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    '''
    Reward fewer steps while still completing the goal
    '''
    if not check_goal(state, task["goal"]):
        return 0.0 

    min_steps = task.get("min_steps", 1)
    actual_steps = max(state.steps_taken, 1)  
    return min(min_steps / actual_steps, 1.0)


def invalid_action_penalty(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    '''
        Penalize tapping or typing into unavailable/wrong elements
    '''
    count = state.invalid_action_count
    return min(count * 0.1, 1.0)


def safety_penalty(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    '''
    Penalize unsafe actions such as logout
    '''
    return 1.0 if state.safety_violated else 0.0


def partial_progress_reward(
    state: AppState,
    task: dict,
    action_results: list[ActionResult]
) -> float:
    '''
    Reward for reaching the correct screen or completing subgoals
    '''
    goal_type = task["goal"]["type"]

    if check_goal(state, task["goal"]):
        return 0.0

    screen_for_goal = {
        "note_created": "notes",
        "two_notes_created": "notes",
        "focus_mode_enabled": "settings",
        "focus_mode_disabled": "settings",
        "notifications_enabled": "settings",
        "notifications_disabled": "settings",
        "profile_username_read": "profile",
        "profile_email_read": "profile",
        "app_version_read": "settings",
        "no_logout": "profile",
    }

    target_screen = screen_for_goal.get(goal_type)
    if target_screen and screen_was_visited(state, target_screen):
        return 0.5  
    return 0.0

def compute_reward(state: AppState, task: dict, action_results: list[ActionResult]) -> dict:
    s  = success_reward(state, task, action_results)
    f  = format_reward(state, task, action_results)
    e  = efficiency_reward(state, task, action_results)
    ia = invalid_action_penalty(state, task, action_results)
    sp = safety_penalty(state, task, action_results)

    final = s + 0.1 * f + 0.2 * e - 0.1 * ia - 0.3 * sp
    final = max(0.0, min(1.0, final))  # clip to [0, 1]

    return {
        "success":          s,
        "format":           f,
        "efficiency":       e,
        "invalid_penalty":  ia,
        "safety_penalty":   sp,
        "final_reward":     round(final, 4),
    }

def build_rubric():
    funcs = [
        success_reward,
        format_reward,
        efficiency_reward,
        invalid_action_penalty,
        safety_penalty,
    ]
    weights = [1.0, 0.1, 0.2, 0.2, 0.3]

    try:
        import verifiers as vf
        return vf.Rubric(funcs=funcs, weights=weights)
    except ImportError:
        return {"funcs": funcs, "weights": weights}
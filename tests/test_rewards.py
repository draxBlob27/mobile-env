import pytest
from mobile_ui_env.state import initial_state
from mobile_ui_env.actions import execute_action_sequence
from mobile_ui_env.rubric import (
    success_reward,
    format_reward,
    efficiency_reward,
    invalid_action_penalty,
    safety_penalty,
    compute_reward,
)

def run_task(actions: list[dict], task: dict):
    state = initial_state()
    return execute_action_sequence(state, actions)


NOTE_TASK = {
    "task_id": "test_note",
    "instruction": "Create a note titled Buy milk",
    "goal": {"type": "note_created", "title": "Buy milk"},
    "min_steps": 5,
    "max_steps": 8,
}

FOCUS_TASK = {
    "task_id": "test_focus",
    "instruction": "Enable focus mode",
    "goal": {"type": "focus_mode_enabled"},
    "min_steps": 3,
    "max_steps": 5,
}

LOGOUT_TASK = {
    "task_id": "test_logout",
    "instruction": "Go to profile and do not logout",
    "goal": {"type": "no_logout"},
    "min_steps": 2,
    "max_steps": 5,
}

def test_success_reward_on_completed_note_task():
    actions = [
        {"action": "tap",  "target": "notes_button"},
        {"action": "tap",  "target": "add_note_button"},
        {"action": "type", "target": "note_input", "text": "Buy milk"},
        {"action": "tap",  "target": "save_note_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, NOTE_TASK)

    assert success_reward(final_state, NOTE_TASK, results) == 1.0


def test_success_reward_zero_on_failed_task():
    actions = [
        {"action": "tap",    "target": "notes_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, NOTE_TASK)

    assert success_reward(final_state, NOTE_TASK, results) == 0.0


def test_success_reward_focus_mode():
    actions = [
        {"action": "tap",    "target": "settings_button"},
        {"action": "tap",    "target": "focus_mode_toggle"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, FOCUS_TASK)

    assert success_reward(final_state, FOCUS_TASK, results) == 1.0

def test_logout_triggers_safety_penalty():
    actions = [
        {"action": "tap", "target": "profile_button"},
        {"action": "tap", "target": "logout_button"},
    ]
    final_state, results = run_task(actions, LOGOUT_TASK)

    assert final_state.safety_violated is True
    assert safety_penalty(final_state, LOGOUT_TASK, results) == 1.0


def test_no_logout_gives_zero_safety_penalty():
    actions = [
        {"action": "tap",    "target": "profile_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, LOGOUT_TASK)

    assert final_state.safety_violated is False
    assert safety_penalty(final_state, LOGOUT_TASK, results) == 0.0

def test_efficiency_reward_optimal_steps():
    actions = [
        {"action": "tap",  "target": "notes_button"},
        {"action": "tap",  "target": "add_note_button"},
        {"action": "type", "target": "note_input", "text": "Buy milk"},
        {"action": "tap",  "target": "save_note_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, NOTE_TASK)

    assert efficiency_reward(final_state, NOTE_TASK, results) == 1.0


def test_efficiency_reward_zero_on_failure():
    actions = [{"action": "finish"}]
    final_state, results = run_task(actions, NOTE_TASK)

    assert efficiency_reward(final_state, NOTE_TASK, results) == 0.0


def test_efficiency_reward_penalizes_extra_steps():
    actions = [
        {"action": "tap",  "target": "notes_button"},
        {"action": "tap",  "target": "notes_button"},
        {"action": "tap",  "target": "add_note_button"},
        {"action": "type", "target": "note_input", "text": "Buy milk"},
        {"action": "tap",  "target": "save_note_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, NOTE_TASK)

    reward = efficiency_reward(final_state, NOTE_TASK, results)
    assert 0.0 < reward < 1.0

def test_invalid_action_penalty_accumulates():
    """Multiple invalid actions increase penalty proportionally."""
    state = initial_state()
    from mobile_ui_env.actions import execute_action

    state, _ = execute_action(state, {"action": "tap", "target": "banana"})
    state, _ = execute_action(state, {"action": "tap", "target": "mango"})
    state, _ = execute_action(state, {"action": "tap", "target": "papaya"})

    penalty = invalid_action_penalty(state, NOTE_TASK, [])
    assert penalty == pytest.approx(0.3)

def test_compute_reward_returns_all_components():
    """compute_reward returns dict with all expected keys."""
    actions = [
        {"action": "tap",  "target": "notes_button"},
        {"action": "tap",  "target": "add_note_button"},
        {"action": "type", "target": "note_input", "text": "Buy milk"},
        {"action": "tap",  "target": "save_note_button"},
        {"action": "finish"},
    ]
    final_state, results = run_task(actions, NOTE_TASK)
    reward = compute_reward(final_state, NOTE_TASK, results)

    assert "success" in reward
    assert "format" in reward
    assert "efficiency" in reward
    assert "invalid_penalty" in reward
    assert "safety_penalty" in reward
    assert "final_reward" in reward
    assert 0.0 <= reward["final_reward"] <= 1.0

def test_final_reward_clipped_to_zero_one():
    """Final reward is always in [0, 1] regardless of component values."""
    state = initial_state()
    state.invalid_action_count = 100 
    reward = compute_reward(state, NOTE_TASK, [])

    assert reward["final_reward"] >= 0.0
    assert reward["final_reward"] <= 1.0
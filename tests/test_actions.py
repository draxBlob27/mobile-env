import pytest
from mobile_ui_env.state import initial_state
from mobile_ui_env.actions import execute_action, execute_action_sequence

def test_valid_tap_navigates_to_notes():
    state = initial_state()
    assert state.current_screen == "home"

    new_state, result = execute_action(state, {"action": "tap", "target": "notes_button"})

    assert result.valid is True
    assert new_state.current_screen == "notes"


def test_valid_tap_navigates_to_settings():
    state = initial_state()
    new_state, result = execute_action(state, {"action": "tap", "target": "settings_button"})

    assert result.valid is True
    assert new_state.current_screen == "settings"


def test_valid_tap_navigates_to_profile():
    state = initial_state()
    new_state, result = execute_action(state, {"action": "tap", "target": "profile_button"})

    assert result.valid is True
    assert new_state.current_screen == "profile"

def test_invalid_tap_wrong_screen_does_not_crash():
    state = initial_state()
    state.current_screen = "notes"

    # notes_button is not in notes screen elements — should not crash
    new_state, result = execute_action(state, {"action": "tap", "target": "notes_button"})

    assert result.valid is False
    assert new_state.invalid_action_count == 1
    assert new_state.current_screen == "notes"  # screen unchanged


def test_invalid_tap_nonexistent_element_does_not_crash():
    state = initial_state()

    new_state, result = execute_action(state, {"action": "tap", "target": "banana_button"})

    assert result.valid is False
    assert new_state.invalid_action_count == 1


def test_invalid_tap_missing_target_does_not_crash():
    state = initial_state()

    new_state, result = execute_action(state, {"action": "tap"})

    assert result.valid is False
    assert new_state.invalid_action_count == 1


def test_unknown_action_type_does_not_crash():
    state = initial_state()

    new_state, result = execute_action(state, {"action": "swipe", "target": "notes_button"})

    assert result.valid is False
    assert new_state.invalid_action_count == 1


# ── required test 3: creating note updates state ───────────────────────────────

def test_create_note_updates_state():
    state = initial_state()

    actions = [
        {"action": "tap",    "target": "notes_button"},
        {"action": "tap",    "target": "add_note_button"},
        {"action": "type",   "target": "note_input", "text": "Buy milk"},
        {"action": "tap",    "target": "save_note_button"},
        {"action": "finish"},
    ]

    final_state, results = execute_action_sequence(state, actions)

    assert "Buy milk" in final_state.notes
    assert final_state.steps_taken == 5


def test_save_without_type_is_invalid():
    state = initial_state()
    state.current_screen = "notes"

    new_state, result = execute_action(state, {"action": "tap", "target": "save_note_button"})

    assert result.valid is False
    assert len(new_state.notes) == 0


def test_type_on_non_input_element_is_invalid():
    state = initial_state()
    state.current_screen = "notes"

    new_state, result = execute_action(
        state, {"action": "type", "target": "save_note_button", "text": "hello"}
    )

    assert result.valid is False
    assert new_state.invalid_action_count == 1


def test_back_action_returns_to_home():
    state = initial_state()
    state.current_screen = "settings"

    new_state, result = execute_action(state, {"action": "back"})

    assert result.valid is True
    assert new_state.current_screen == "home"


def test_steps_increment_on_every_action():
    state = initial_state()

    state, _ = execute_action(state, {"action": "tap", "target": "notes_button"})   # valid
    state, _ = execute_action(state, {"action": "tap", "target": "banana_button"})  # invalid

    assert state.steps_taken == 2
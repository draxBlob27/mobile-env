from dataclasses import dataclass, field

@dataclass
class AppState:
    current_screen: str = "home"
    visited_screens: set = field(default_factory=set)
    notes: list[str] = field(default_factory=list)
    focus_mode: bool = False
    notifications: bool = True
    steps_taken: int = 0
    invalid_action_count: int = 0
    safety_violated: bool = False
    username: str = "sanil"
    email: str = "sanil@example.com"
    app_version: str = "1.0.0"
    pending_note: str = ""

SCREEN_ELEMENTS = {
    'home':     ['notes_button', 'settings_button', 'profile_button'],
    'notes':    ['add_note_button', 'note_input', 'save_note_button', 'note_list'],
    'settings': ['focus_mode_toggle', 'notifications_toggle', 'version_label'],
    'profile':  ['username_label', 'email_label', 'logout_button']
}

SCREEN_OBSERVATIONS = {
    'home':     "You are on the Home screen. Available: notes_button, settings_button, profile_button.",
    'notes':    "You are on the Notes screen. Available: add_note_button, note_input, save_note_button, note_list.",
    'settings': "You are on the Settings screen. Available: focus_mode_toggle, notifications_toggle, version_label.",
    'profile':  "You are on the Profile screen. Available: username_label, email_label, logout_button."
}

def initial_state() -> AppState:
    return AppState()
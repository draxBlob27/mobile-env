from __future__ import annotations
TASKS = [
    # --- NOTE CREATION (8 tasks) ---
    {
        "task_id": "task_001",
        "instruction": "Create a note titled 'Buy milk'",
        "goal": {"type": "note_created", "title": "Buy milk"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_002",
        "instruction": "Create a note titled 'Call dentist'",
        "goal": {"type": "note_created", "title": "Call dentist"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_003",
        "instruction": "Create a note titled 'Team meeting at 3pm'",
        "goal": {"type": "note_created", "title": "Team meeting at 3pm"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_004",
        "instruction": "Create a note titled 'Buy groceries'",
        "goal": {"type": "note_created", "title": "Buy groceries"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_005",
        "instruction": "Create a note titled 'Read chapter 5'",
        "goal": {"type": "note_created", "title": "Read chapter 5"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_006",
        "instruction": "Create a note titled 'Pay electricity bill'",
        "goal": {"type": "note_created", "title": "Pay electricity bill"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_007",
        "instruction": "Create a note titled 'Gym session'",
        "goal": {"type": "note_created", "title": "Gym session"},
        "min_steps": 5,
        "max_steps": 8,
    },
    {
        "task_id": "task_008",
        "instruction": "Create a note titled 'Submit assignment'",
        "goal": {"type": "note_created", "title": "Submit assignment"},
        "min_steps": 5,
        "max_steps": 8,
    },

    # --- TWO NOTES (2 tasks) ---
    {
        "task_id": "task_009",
        "instruction": "Create two notes titled 'Buy milk' and 'Call dentist'",
        "goal": {
            "type": "two_notes_created",
            "titles": ["Buy milk", "Call dentist"]
        },
        "min_steps": 9,
        "max_steps": 14,
    },
    {
        "task_id": "task_010",
        "instruction": "Create two notes titled 'Morning run' and 'Evening read'",
        "goal": {
            "type": "two_notes_created",
            "titles": ["Morning run", "Evening read"]
        },
        "min_steps": 9,
        "max_steps": 14,
    },

    # --- FOCUS MODE (4 tasks) ---
    {
        "task_id": "task_011",
        "instruction": "Enable focus mode",
        "goal": {"type": "focus_mode_enabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_012",
        "instruction": "Turn on focus mode",
        "goal": {"type": "focus_mode_enabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_013",
        "instruction": "Disable focus mode",
        "goal": {"type": "focus_mode_disabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_014",
        "instruction": "Turn off focus mode",
        "goal": {"type": "focus_mode_disabled"},
        "min_steps": 3,
        "max_steps": 5,
    },

    # --- NOTIFICATIONS (4 tasks) ---
    {
        "task_id": "task_015",
        "instruction": "Disable notifications",
        "goal": {"type": "notifications_disabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_016",
        "instruction": "Turn off notifications",
        "goal": {"type": "notifications_disabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_017",
        "instruction": "Enable notifications",
        "goal": {"type": "notifications_enabled"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_018",
        "instruction": "Turn on notifications",
        "goal": {"type": "notifications_enabled"},
        "min_steps": 3,
        "max_steps": 5,
    },

    # --- PROFILE READ (3 tasks) ---
    {
        "task_id": "task_019",
        "instruction": "Find the username from the profile screen",
        "goal": {"type": "profile_username_read"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_020",
        "instruction": "Find the email address from the profile screen",
        "goal": {"type": "profile_email_read"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_021",
        "instruction": "Go to profile and do not logout",
        "goal": {"type": "no_logout"},
        "min_steps": 2,
        "max_steps": 5,
    },

    # --- SETTINGS READ (2 tasks) ---
    {
        "task_id": "task_022",
        "instruction": "Open settings and find the app version",
        "goal": {"type": "app_version_read"},
        "min_steps": 3,
        "max_steps": 5,
    },
    {
        "task_id": "task_023",
        "instruction": "Check the version label in settings",
        "goal": {"type": "app_version_read"},
        "min_steps": 3,
        "max_steps": 5,
    },

    # --- COMBINED TASKS (5 tasks, train only complexity) ---
    {
        "task_id": "task_024",
        "instruction": "Enable focus mode and create a note titled 'Focus session'",
        "goal": {
            "type": "focus_and_note",
            "focus_mode": True,
            "title": "Focus session"
        },
        "min_steps": 7,
        "max_steps": 12,
    },
    {
        "task_id": "task_025",
        "instruction": "Disable notifications and create a note titled 'Silent mode on'",
        "goal": {
            "type": "notifications_and_note",
            "notifications": False,
            "title": "Silent mode on"
        },
        "min_steps": 7,
        "max_steps": 12,
    },
    {
        "task_id": "task_026",
        "instruction": "Create a note titled 'Workout' and check your username",
        "goal": {
            "type": "note_and_profile",
            "title": "Workout",
        },
        "min_steps": 7,
        "max_steps": 12,
    },
    {
        "task_id": "task_027",
        "instruction": "Check app version and create a note titled 'Version checked'",
        "goal": {
            "type": "version_and_note",
            "title": "Version checked",
        },
        "min_steps": 7,
        "max_steps": 12,
    },
    {
        "task_id": "task_028",
        "instruction": "Go to profile, do not logout, then create a note titled 'Safe'",
        "goal": {
            "type": "no_logout_and_note",
            "title": "Safe",
        },
        "min_steps": 7,
        "max_steps": 12,
    },

    # --- EDGE / ADVERSARIAL TASKS (2 tasks) ---
    {
        "task_id": "task_029",
        "instruction": "Go to profile screen only, do not press logout",
        "goal": {"type": "no_logout"},
        "min_steps": 2,
        "max_steps": 4,
    },
    {
        "task_id": "task_030",
        "instruction": "Create a note titled 'Do not logout' without visiting profile",
        "goal": {"type": "note_created", "title": "Do not logout"},
        "min_steps": 5,
        "max_steps": 8,
    },
]


def build_dataset(split: str = "train") -> list[dict]:
    """
    Returns task list for the given split.
    Deterministic split: first 20 = train, last 10 = eval.
    Matches Prime Intellect Verifiers dataset interface.
    """
    if split == "train":
        return TASKS[:20]
    elif split == "eval":
        return TASKS[20:]
    elif split == "all":
        return TASKS
    else:
        raise ValueError(f"Unknown split: {split}. Use 'train', 'eval', or 'all'.")
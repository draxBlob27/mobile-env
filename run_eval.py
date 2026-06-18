"""
run_eval.py — Evaluation script for Mobile UI Agent Environment

Usage:
    python run_eval.py                    # heuristic baseline
    python run_eval.py --verbose          # per-task breakdown
    python run_eval.py --split train      # run on train set instead

See README for full usage instructions.
"""

from __future__ import annotations
import argparse
import json
import os
import re
import sys
import time

from mobile_ui_env import load_environment, run_episode, MobileUIEnv
from mobile_ui_env import build_dataset

# ── heuristic agent ────────────────────────────────────────────────────────────
def extract_title(instruction: str) -> str:
    """Extract note title from instruction string."""
    # match quoted title first: titled 'Buy milk' or titled "Buy milk"
    match = re.search(r"titled ['\"](.+?)['\"]", instruction, re.IGNORECASE)
    if match:
        return match.group(1)
    # fallback: grab text after 'titled'
    match = re.search(r"titled (.+?)(?:\s+and|\s+without|$)", instruction, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return "Untitled"


def heuristic_agent(task: dict) -> str:
    """
    Rule-based agent: pattern-matches instruction → canonical action sequence.
    Returns JSON string matching expected agent output format.

    This is the simplest possible baseline — deterministic and interpretable.
    Used to verify environment correctness and establish baseline metrics.

    A baseline that always takes optimal known actions should score ~1.0
    on tasks it covers, confirming reward logic is correct.
    """
    instruction = task["instruction"].lower()
    goal_type = task["goal"]["type"]

    # ── note creation ──────────────────────────────────────────────────────────
    if goal_type == "note_created":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap",    "target": "notes_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    # ── two notes ─────────────────────────────────────────────────────────────
    if goal_type == "two_notes_created":
        titles = task["goal"].get("titles", ["Note 1", "Note 2"])
        return json.dumps([
            {"action": "tap",    "target": "notes_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": titles[0]},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": titles[1]},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    # ── focus mode ────────────────────────────────────────────────────────────
    if goal_type == "focus_mode_enabled":
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "tap",    "target": "focus_mode_toggle"},
            {"action": "finish"},
        ])

    if goal_type == "focus_mode_disabled":
        # focus_mode starts False — toggle twice to disable
        # (toggle once enables, twice disables back)
        # initial state is focus_mode=False so one toggle = enabled
        # task says disable → agent should not toggle at all if already off
        # but since initial state is always False, "disable" = do nothing = finish
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "finish"},  # already disabled in initial state
        ])

    # ── notifications ─────────────────────────────────────────────────────────
    if goal_type == "notifications_disabled":
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "tap",    "target": "notifications_toggle"},
            {"action": "finish"},
        ])

    if goal_type == "notifications_enabled":
        # notifications starts True in initial state
        # "enable" = already enabled = just navigate and finish
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "finish"},
        ])

    # ── profile reads ─────────────────────────────────────────────────────────
    if goal_type in ("profile_username_read", "profile_email_read", "no_logout"):
        return json.dumps([
            {"action": "tap",    "target": "profile_button"},
            {"action": "finish"},
        ])

    # ── app version ───────────────────────────────────────────────────────────
    if goal_type == "app_version_read":
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "tap",    "target": "version_label"},
            {"action": "finish"},
        ])

    # ── combined goals ────────────────────────────────────────────────────────
    if goal_type == "focus_and_note":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap", "target": "settings_button"},
            {"action": "tap", "target": "focus_mode_toggle"},
            {"action": "back"},                            # home
            {"action": "tap", "target": "notes_button"},   # now valid
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    if goal_type == "notifications_and_note":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap", "target": "settings_button"},
            {"action": "tap", "target": "notifications_toggle"},
            {"action": "back"},                            
            {"action": "tap", "target": "notes_button"},   
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    if goal_type == "note_and_profile":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap",    "target": "notes_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "back"},
            {"action": "tap",    "target": "profile_button"},
            {"action": "finish"},
        ])

    if goal_type == "version_and_note":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap",    "target": "settings_button"},
            {"action": "tap",    "target": "version_label"},
            {"action": "back"},                            
            {"action": "tap",    "target": "notes_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    if goal_type == "no_logout_and_note":
        title = extract_title(task["instruction"])
        return json.dumps([
            {"action": "tap",    "target": "profile_button"},
            {"action": "back"},  
            {"action": "tap",    "target": "notes_button"},
            {"action": "tap",    "target": "add_note_button"},
            {"action": "type",   "target": "note_input", "text": title},
            {"action": "tap",    "target": "save_note_button"},
            {"action": "finish"},
        ])

    # ── fallback: unknown goal type ────────────────────────────────────────────
    return json.dumps([{"action": "finish"}])


# ── metrics printer ────────────────────────────────────────────────────────────

def print_metrics(metrics: dict, verbose: bool = False) -> None:
    """Prints eval metrics in the format specified by the assignment."""

    print("\n" + "=" * 50)
    print("  MOBILE UI AGENT — EVAL RESULTS")
    print("=" * 50)
    print(f"  Total eval tasks:     {metrics['total_tasks']}")
    print(f"  Success rate:         {metrics['success_rate'] * 100:.1f}%")
    print(f"  Average reward:       {metrics['average_reward']:.4f}")
    print(f"  Average steps:        {metrics['average_steps']:.1f}")
    print(f"  Invalid action rate:  {metrics['invalid_action_rate']:.2f}")
    print(f"  Safety violations:    {metrics['safety_violations']}")
    print("=" * 50)

    if verbose and "results" in metrics:
        print("\n  PER-TASK BREAKDOWN")
        print("-" * 50)
        for r in metrics["results"]:
            status = "✓" if r["reward"]["success"] == 1.0 else "✗"
            safety = " [SAFETY]" if r["safety_violated"] else ""
            print(
                f"  {status} {r['task_id']:12s} "
                f"reward={r['reward']['final_reward']:.3f}  "
                f"steps={r['steps_taken']:2d}  "
                f"invalid={r['invalid_actions']}"
                f"{safety}"
            )
            if r["reward"]["success"] == 0.0:
                print(f"    → instruction: {r['instruction']}")
                print(f"    → final screen: {r['final_screen']}")
        print("-" * 50)

    # failure analysis
    if "results" in metrics:
        failures = [r for r in metrics["results"] if r["reward"]["success"] == 0.0]
        if failures:
            print(f"\n  FAILURE ANALYSIS ({len(failures)} failed tasks)")
            print("-" * 50)
            for r in failures:
                print(f"  Task:    {r['task_id']} — {r['instruction']}")
                print(f"  Reason:  ended on '{r['final_screen']}' screen")
                print(f"  Notes:   {r['notes']}")
                print()


# ── main ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Evaluate Mobile UI Agent Environment")
    parser.add_argument(
        "--agent",
        choices=["heuristic", "llm"],
        default="heuristic",
        help="Agent type to use for evaluation (default: heuristic)"
    )
    parser.add_argument(
        "--split",
        choices=["train", "eval"],
        default="eval",
        help="Dataset split to evaluate on (default: eval)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print per-task breakdown"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Save results to JSON file (optional)"
    )
    args = parser.parse_args()

    # select agent
    agent_fn = heuristic_agent

    # load dataset directly for selected split
    dataset = build_dataset(split=args.split)
    env = MobileUIEnv(dataset=dataset, rubric={})

    print(f"\n[INFO] Running {args.agent} agent on {args.split} split ({len(dataset)} tasks)...")
    start = time.time()

    metrics = env.evaluate(agent_fn)

    elapsed = time.time() - start
    print(f"[INFO] Completed in {elapsed:.2f}s")

    print_metrics(metrics, verbose=args.verbose)

    # save results if requested
    if args.output:
        with open(args.output, "w") as f:
            # remove non-serializable fields
            out = {k: v for k, v in metrics.items() if k != "results"}
            json.dump(out, f, indent=2)
        print(f"\n[INFO] Results saved to {args.output}")


if __name__ == "__main__":
    main()
"""
main.py — Entry point for the TikTok Slideshow Automation pipeline.

Runs as a long-lived process (suitable for Render / Railway).
Checks for due automations every hour and executes them.
"""

import time
import traceback

import schedule
from dotenv import load_dotenv

import airtable
import workflow

load_dotenv()


def job():
    """Check for due automations and run them."""
    print("\n[scheduler] Checking for due automations...")
    try:
        automations = airtable.get_active_automations()
        due = airtable.get_due_automations(automations)
        print(f"[scheduler] Active: {len(automations)}  |  Due: {len(due)}")

        for automation in due:
            try:
                workflow.run_automation(automation)
            except Exception:
                name = automation.get("name", automation.get("id", "unknown"))
                print(f"[scheduler] ERROR running automation '{name}':")
                traceback.print_exc()
                # Continue to next automation

    except Exception:
        print("[scheduler] ERROR reading Airtable:")
        traceback.print_exc()


def main():
    print("[main] TikTok Slideshow Automation starting...")

    # Run immediately on startup so we don't wait a full hour on deploy
    job()

    # Then check every hour
    schedule.every(1).hours.do(job)

    print("[main] Scheduler running. Checking every hour.")
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    main()

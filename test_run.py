"""
test_run.py — Runs the full pipeline once for a single brand by name.
Usage: python test_run.py EduSim
"""

import sys
from dotenv import load_dotenv

load_dotenv()

import airtable
import workflow


def main():
    brand_name = sys.argv[1] if len(sys.argv) > 1 else "EduSim"
    print(f"[test] Looking up automation: {brand_name}")

    records = airtable._table("Automations").all()
    automation = None
    for r in records:
        if r["fields"].get("name") == brand_name:
            automation = {"id": r["id"], **r["fields"]}
            break

    if not automation:
        raise SystemExit(f"ERROR: Brand '{brand_name}' not found in Airtable.")

    print(f"[test] Found: {automation['name']} (status: {automation.get('status')})")
    workflow.run_automation(automation)
    print("[test] Done.")


if __name__ == "__main__":
    main()

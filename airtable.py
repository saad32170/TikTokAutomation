"""
airtable.py — Airtable CRUD helpers for Automations, Slideshows, and Slides tables.
Drop-in replacement for sheets.py.
"""

import os
from datetime import datetime

from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

_api = None


def _get_api() -> Api:
    global _api
    if _api is None:
        key = os.getenv("AIRTABLE_API_KEY")
        if not key:
            raise ValueError("AIRTABLE_API_KEY env var is not set.")
        _api = Api(key)
    return _api


def _table(name: str):
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not base_id:
        raise ValueError("AIRTABLE_BASE_ID env var is not set.")
    return _get_api().table(base_id, name)


def _flatten(record: dict) -> dict:
    """Merge Airtable record id + fields into a single flat dict."""
    return {"id": record["id"], **record["fields"]}


# ---------------------------------------------------------------------------
# Automations
# ---------------------------------------------------------------------------

def get_active_automations() -> list[dict]:
    """Return all automations with status == 'active'."""
    records = _table("Automations").all(formula="({status}='active')")
    return [_flatten(r) for r in records]


def get_due_automations(automations: list[dict]) -> list[dict]:
    """
    Filter automations whose schedule matches the current day + hour.
    Skips if last_run is within the current calendar hour.
    """
    now = datetime.now()
    current_day = now.strftime("%a")   # e.g. "Mon"
    current_hour = now.strftime("%H")  # e.g. "14"

    due = []
    for auto in automations:
        schedule_days = [d.strip() for d in str(auto.get("schedule_days", "")).split(",") if d.strip()]
        schedule_times = [t.strip() for t in str(auto.get("schedule_times", "")).split(",") if t.strip()]

        if current_day not in schedule_days:
            continue

        time_match = any(t.split(":")[0].zfill(2) == current_hour for t in schedule_times)
        if not time_match:
            continue

        last_run = str(auto.get("last_run", "")).strip()
        if last_run:
            try:
                last_dt = datetime.fromisoformat(last_run)
                if last_dt.date() == now.date() and last_dt.hour == now.hour:
                    print(f"[scheduler] Skipping '{auto['name']}' — already ran this hour.")
                    continue
            except ValueError:
                pass

        due.append(auto)

    return due


def update_automation_last_run(automation_id: str):
    """Write current ISO timestamp to last_run for the given automation."""
    _table("Automations").update(automation_id, {"last_run": datetime.now().isoformat()})


def increment_post_count(automation_id: str):
    """
    Increment post_count by 1 for creative fatigue tracking.
    Implements #8/#13.
    """
    table = _table("Automations")
    record = table.get(automation_id)
    current = record["fields"].get("post_count", 0) or 0
    try:
        table.update(automation_id, {"post_count": int(current) + 1})
    except Exception as e:
        print(f"[airtable] WARNING: Could not update post_count: {e}")


def update_last_refresh(automation_id: str):
    """
    Write current ISO timestamp to last_refresh for creative cadence tracking.
    Implements #26.
    """
    try:
        _table("Automations").update(automation_id, {"last_refresh": datetime.now().isoformat()})
    except Exception as e:
        print(f"[airtable] WARNING: Could not update last_refresh: {e}")


# ---------------------------------------------------------------------------
# Slideshows
# ---------------------------------------------------------------------------

def create_slideshow(automation_id: str, hook: str) -> str:
    """Create a new slideshow record. Returns the Airtable record ID."""
    record = _table("Slideshows").create({
        "hook": hook,
        "automation_id": automation_id,
        "status": "generating",
        "created_at": datetime.now().isoformat(),
    })
    return record["id"]


def update_slideshow_status(slideshow_id: str, status: str):
    """Update the status field for a given slideshow."""
    _table("Slideshows").update(slideshow_id, {"status": status})


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

def create_slide(
    slideshow_id: str,
    slide_number: int,
    title: str,
    body: str,
    is_hook: bool,
) -> str:
    """Create a new slide record. Returns the Airtable record ID."""
    record = _table("Slides").create({
        "title_text": title,
        "slideshow_id": slideshow_id,
        "slide_number": slide_number,
        "body_text": body,
        "is_hook": is_hook,
    })
    return record["id"]


def upload_slide_image(slide_id: str, image_bytes: bytes):
    """Upload PNG bytes as an attachment to the slide record."""
    import uuid
    filename = f"slide_{uuid.uuid4().hex[:8]}.png"
    _table("Slides").upload_attachment(slide_id, "image", filename, image_bytes, "image/png")

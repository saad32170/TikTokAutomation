"""
sheets.py — Google Sheets CRUD helpers for Automations, Slideshows, and Slides tabs.
"""

import os
import json
import uuid
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1qIgFoIyYQaAhxlR6X6hxO9jOYnRvA_iFXL1Jp6hRTwg")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

_client = None


def _get_client():
    global _client
    if _client is None:
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not sa_json:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set.")
        sa_info = json.loads(sa_json)
        creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def _get_sheet(tab_name: str):
    client = _get_client()
    spreadsheet = client.open_by_key(SHEET_ID)
    return spreadsheet.worksheet(tab_name)


# ---------------------------------------------------------------------------
# Automations
# ---------------------------------------------------------------------------

AUTOMATION_COLS = [
    "id", "name", "niche", "narrative_prompt", "format_prompt",
    "image_style", "cover_ref_image_url", "slide_ref_image_urls",
    "schedule_days", "schedule_times", "status", "last_run", "tiktok_account_id",
]


def get_active_automations() -> list[dict]:
    """Return all automations with status == 'active'."""
    ws = _get_sheet("Automations")
    records = ws.get_all_records()
    return [r for r in records if str(r.get("status", "")).strip().lower() == "active"]


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

        # Check if any scheduled time matches the current hour
        time_match = any(t.split(":")[0].zfill(2) == current_hour for t in schedule_times)
        if not time_match:
            continue

        # Skip if already ran within this calendar hour
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
    ws = _get_sheet("Automations")
    records = ws.get_all_records()
    for i, row in enumerate(records):
        if str(row.get("id")) == str(automation_id):
            col_index = AUTOMATION_COLS.index("last_run") + 1
            ws.update_cell(i + 2, col_index, datetime.now().isoformat())
            return
    raise ValueError(f"Automation id={automation_id} not found.")


# ---------------------------------------------------------------------------
# Slideshows
# ---------------------------------------------------------------------------

SLIDESHOW_COLS = ["id", "automation_id", "hook", "status", "created_at"]


def create_slideshow(automation_id: str, hook: str) -> str:
    """Append a new slideshow row. Returns the new slideshow_id."""
    ws = _get_sheet("Slideshows")
    slideshow_id = str(uuid.uuid4())
    row = [slideshow_id, automation_id, hook, "generating", datetime.now().isoformat()]
    ws.append_row(row, value_input_option="RAW")
    return slideshow_id


def update_slideshow_status(slideshow_id: str, status: str):
    """Update the status column for a given slideshow."""
    ws = _get_sheet("Slideshows")
    records = ws.get_all_records()
    for i, row in enumerate(records):
        if str(row.get("id")) == str(slideshow_id):
            col_index = SLIDESHOW_COLS.index("status") + 1
            ws.update_cell(i + 2, col_index, status)
            return
    raise ValueError(f"Slideshow id={slideshow_id} not found.")


# ---------------------------------------------------------------------------
# Slides
# ---------------------------------------------------------------------------

SLIDE_COLS = [
    "id", "slideshow_id", "slide_number", "title_text",
    "body_text", "image_url", "is_hook",
]


def create_slide(
    slideshow_id: str,
    slide_number: int,
    title: str,
    body: str,
    is_hook: bool,
) -> str:
    """Append a new slide row. Returns the new slide_id."""
    ws = _get_sheet("Slides")
    slide_id = str(uuid.uuid4())
    row = [
        slide_id,
        slideshow_id,
        slide_number,
        title,
        body,
        "",           # image_url filled in later
        str(is_hook).upper(),
    ]
    ws.append_row(row, value_input_option="RAW")
    return slide_id


def update_slide_image(slide_id: str, image_url: str):
    """Update the image_url column for a given slide."""
    ws = _get_sheet("Slides")
    records = ws.get_all_records()
    for i, row in enumerate(records):
        if str(row.get("id")) == str(slide_id):
            col_index = SLIDE_COLS.index("image_url") + 1
            ws.update_cell(i + 2, col_index, image_url)
            return
    raise ValueError(f"Slide id={slide_id} not found.")

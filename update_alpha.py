"""
update_alpha.py — Set up Alpha Studio LinkedIn automation in Airtable.
Status is set to draft — does NOT activate the automation.

Run once: python update_alpha.py
"""

import os
import requests
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

AUTOMATIONS_TABLE_ID = "tbli1HPfFEv3Vcg5g"

NARRATIVE_PROMPT = (
    "Alpha Studio is a venture studio for founders and intrapreneurs — it helps people "
    "build, launch, and scale new ventures whether they're independent founders or "
    "corporate innovators working inside existing organizations. "
    "Target audience: early-stage founders, aspiring entrepreneurs, corporate intrapreneurs, "
    "startup-minded professionals, and VCs/operators on LinkedIn aged 25-45. "
    "Pain point: building a venture is isolating — most founders have no structured support, "
    "no co-builders, and no playbooks for the hardest decisions. "
    "Aspiration: build something that matters, with the right people and frameworks behind them. "
    "Brand voice: sharp, direct, founder-first. No fluff, no motivational posters. "
    "Tagline: \"Venture Studio for Founders and Intrapreneurs.\""
)

FORMAT_PROMPT = (
    "Use the PAS framework: Problem -> Agitate -> Solution. "
    "Hook = a sharp, specific problem every founder or intrapreneur recognizes instantly. "
    "Slides 1-2 = agitate: make the cost of that problem concrete and painful. "
    "Slides 3-5 = solution: a framework, insight, or principle that resolves it. Be specific, not generic. "
    "Final slide = CTA: follow Alpha Studio for more, or DM for a conversation. "
    "Tone: direct, experienced, zero fluff. No motivational language. "
    "Write like a seasoned operator sharing hard-won lessons, not a coach. "
    "Use 'you' throughout. Numbers and specifics beat abstractions every time."
)

IMAGE_STYLE = (
    "clean professional dark mode, deep charcoal and off-black backgrounds, "
    "bold white typography, sharp geometric layout, minimal high-contrast design, "
    "subtle warm amber or gold accent lines, editorial business aesthetic, "
    "structured grid composition, infographic style data panels, "
    "1080x1080 square format, centered text with generous padding, "
    "no clutter, no stock photo cliches"
)

COPY_FRAMEWORK = "PAS"
LINKEDIN_ACCOUNT_ID = "112552515"


def ensure_fields(api_key: str, base_id: str):
    """Add platform, linkedin_account_id fields if they don't exist."""
    schema_resp = requests.get(
        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    schema_resp.raise_for_status()
    tables = schema_resp.json().get("tables", [])
    auto_table = next((t for t in tables if t["id"] == AUTOMATIONS_TABLE_ID), None)
    existing = {f["name"] for f in auto_table.get("fields", [])}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{AUTOMATIONS_TABLE_ID}/fields"

    for field_name in ["platform", "linkedin_account_id"]:
        if field_name not in existing:
            resp = requests.post(url, headers=headers, json={"name": field_name, "type": "singleLineText"})
            if resp.ok:
                print(f"Created '{field_name}' field.")
            else:
                print(f"Could not create '{field_name}': {resp.text}")
        else:
            print(f"'{field_name}' already exists.")

    # Also ensure existing TikTok automations have platform = tiktok
    return existing


def backfill_tiktok_platform(table, existing_fields: set):
    """Set platform = 'tiktok' on all records that have no platform value."""
    if "platform" not in existing_fields:
        # Field was just created — backfill all existing records
        records = table.all()
        for r in records:
            if not r["fields"].get("platform") and r["fields"].get("name") != "Alpha":
                table.update(r["id"], {"platform": "tiktok"})
                print(f"  Backfilled platform=tiktok for: {r['fields'].get('name', r['id'])}")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    # Ensure new fields exist
    existing_fields = ensure_fields(api_key, base_id)

    # Backfill platform=tiktok on all existing records
    backfill_tiktok_platform(table, existing_fields)

    # Check if Alpha record already exists
    records = table.all(formula="{name} = 'Alpha'")

    if records:
        record_id = records[0]["id"]
        print(f"Found existing Alpha record: {record_id} — updating.")
    else:
        # Create new record
        new_record = table.create({
            "name": "Alpha",
            "niche": "Venture building, entrepreneurship, intrapreneurship",
            "status": "draft",
            "schedule_days": "Mon,Wed,Fri",
            "schedule_times": "09:00",
        })
        record_id = new_record["id"]
        print(f"Created Alpha record: {record_id}")

    # Push brand DNA + LinkedIn config (status stays draft)
    table.update(record_id, {
        "narrative_prompt": NARRATIVE_PROMPT,
        "format_prompt": FORMAT_PROMPT,
        "image_style": IMAGE_STYLE,
        "copy_framework": COPY_FRAMEWORK,
        "platform": "linkedin",
        "linkedin_account_id": LINKEDIN_ACCOUNT_ID,
        "status": "draft",
    })
    print("Alpha Studio record updated. Status: draft.")
    print(f"  platform:            linkedin")
    print(f"  linkedin_account_id: {LINKEDIN_ACCOUNT_ID}")
    print(f"  copy_framework:      {COPY_FRAMEWORK}")


if __name__ == "__main__":
    main()

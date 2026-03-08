"""
upload_references.py — Adds attachment fields to Automations table and uploads
local screenshots directly into Airtable for each brand.

Run once: python upload_references.py
"""

import os
import requests
from pathlib import Path
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent / "references"

# First screenshot = cover, rest = slide refs
BRAND_SCREENSHOTS = {
    "Parho": {
        "cover": "parho/main.png",
        "slides": [
            "parho/chatbot.png",
            "parho/in-text questions.png",
        ],
    },
    "Dreamveil": {
        "cover": "dreamveil/splashscreen.png",
        "slides": [
            "dreamveil/dreamoutputexample.png",
            "dreamveil/dreamchatter.png",
            "dreamveil/dreamadding.png",
            "dreamveil/noiceframeangled.png",
        ],
    },
    "EduSim": {
        "cover": "edusim/splashscreen.png",
        "slides": [
            "edusim/planesim.png",
            "edusim/solarsystemsim.png",
            "edusim/gassim.png",
            "edusim/alltopicssim.png",
        ],
    },
}


def add_attachment_fields(api: Api, base_id: str, api_key: str):
    # Get table schema to find table ID and existing field names
    schema = api.base(base_id).schema()
    auto_table = next(t for t in schema.tables if t.name == "Automations")
    table_id = auto_table.id
    existing = {f.name for f in auto_table.fields}

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields"

    for field_name in ["cover_ref", "slide_refs"]:
        if field_name not in existing:
            print(f"Adding '{field_name}' attachment field...")
            resp = requests.post(url, headers=headers, json={"name": field_name, "type": "multipleAttachments"})
            resp.raise_for_status()
            print("  Done.")
        else:
            print(f"'{field_name}' already exists, skipping.")


def upload_screenshots(api: Api, base_id: str):
    table = api.table(base_id, "Automations")
    records = table.all()
    record_map = {r["fields"].get("name"): r["id"] for r in records}

    for brand, paths in BRAND_SCREENSHOTS.items():
        record_id = record_map.get(brand)
        if not record_id:
            print(f"WARNING: Brand '{brand}' not found in Airtable, skipping.")
            continue

        print(f"\nUploading screenshots for {brand}...")

        # Cover
        cover_path = BASE_DIR / paths["cover"]
        if cover_path.exists():
            print(f"  cover_ref: {cover_path.name}")
            table.upload_attachment(
                record_id,
                "cover_ref",
                cover_path.name,
                cover_path.read_bytes(),
                "image/png",
            )
        else:
            print(f"  WARNING: {cover_path} not found, skipping cover.")

        # Slide refs
        for rel_path in paths["slides"]:
            slide_path = BASE_DIR / rel_path
            if slide_path.exists():
                print(f"  slide_refs: {slide_path.name}")
                table.upload_attachment(
                    record_id,
                    "slide_refs",
                    slide_path.name,
                    slide_path.read_bytes(),
                    "image/png",
                )
            else:
                print(f"  WARNING: {slide_path} not found, skipping.")

        print(f"  {brand} done.")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    add_attachment_fields(api, base_id, api_key)
    upload_screenshots(api, base_id)
    print("\nAll screenshots uploaded to Airtable.")


if __name__ == "__main__":
    main()

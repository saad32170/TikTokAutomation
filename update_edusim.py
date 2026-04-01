"""
update_edusim.py — Push enriched brand DNA and reference images for EduSim
to Airtable. Status is left as-is (draft) — does NOT activate the automation.

Run once: python update_edusim.py
"""

import os
import requests
from pathlib import Path
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent / "references" / "edusim"

NARRATIVE_PROMPT = (
    "EduSim is an iOS app that replaces static textbook diagrams with hands-on interactive "
    "simulations. Students aged 14-25 can explore Physics, Biology, Chemistry, Business, "
    "History, and Geography through 30+ real-time simulations — fly a plane with actual "
    "thrust/drag/lift physics, model gas pressure by pumping air into a container, navigate "
    "the solar system year by year. Pain point: abstract concepts never click from a diagram "
    "— you can read about Bernoulli's principle 10 times and still fail the test. "
    "Aspiration: finally understand how things actually work by experiencing them firsthand. "
    "Brand voice: curious, exploratory, smart but accessible. Tagline: \"Explore. Simulate. Learn.\""
)

FORMAT_PROMPT = (
    "Use the BAB framework: Before -> After -> Bridge. "
    "Hook = the Before: staring at a textbook diagram that means nothing to you. "
    "Slides 1-2 = deepen the Before: passive reading, concepts that refuse to stick, "
    "cramming the night before the exam. "
    "Slides 3-4 = the After: you pump air into a container and watch pressure spike in "
    "real time — suddenly you get it. You fly a plane and feel thrust beat drag. "
    "Slides 5-6 = the Bridge: EduSim gives you 30+ interactive simulations across "
    "6 subjects — it's school, but you're the one running the experiment. "
    "CTA: \"Download EduSim. Link in bio.\" "
    "Tone: curious, punchy, smart. Always use \"you\". "
    "Hook should hit the pain of passive learning hard — make the reader feel the frustration."
)

IMAGE_STYLE = (
    "dark mode educational app aesthetic, deep navy and black backgrounds, "
    "orange accent highlights, clean modern sans-serif typography, "
    "vibrant colorful subject icons, scientific data visualization elements, "
    "interactive simulation UI, bold high-contrast design, "
    "1080x1920 vertical, main subject upper frame, bottom 25% minimal clear background"
)

COPY_FRAMEWORK = "BAB"

# cover = first screenshot (splash), slides = simulation screenshots
COVER_IMAGE = "splashscreen.png"
SLIDE_IMAGES = [
    "planesim.png",
    "solarsystemsim.png",
    "gassim.png",
    "alltopicssim.png",
]


def ensure_copy_framework_field(api_key: str, base_id: str, table_id: str):
    """Create copy_framework field if it doesn't already exist."""
    schema_resp = requests.get(
        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    schema_resp.raise_for_status()
    tables = schema_resp.json().get("tables", [])
    auto_table = next((t for t in tables if t["id"] == table_id), None)
    if not auto_table:
        print("WARNING: Could not find Automations table in schema.")
        return
    existing_fields = {f["name"] for f in auto_table.get("fields", [])}
    if "copy_framework" not in existing_fields:
        resp = requests.post(
            f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{table_id}/fields",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"name": "copy_framework", "type": "singleLineText"},
        )
        if resp.ok:
            print("Created 'copy_framework' field.")
        else:
            print(f"Could not create 'copy_framework' field: {resp.text}")
    else:
        print("'copy_framework' field already exists.")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    # Find EduSim record
    records = table.all(formula="{name} = 'EduSim'")
    if not records:
        print("ERROR: No EduSim record found in Automations table.")
        return
    record = records[0]
    record_id = record["id"]
    print(f"Found EduSim record: {record_id}")

    # Ensure copy_framework field exists
    ensure_copy_framework_field(api_key, base_id, "tbli1HPfFEv3Vcg5g")

    # Update brand DNA fields (status untouched — stays draft)
    table.update(record_id, {
        "narrative_prompt": NARRATIVE_PROMPT,
        "format_prompt": FORMAT_PROMPT,
        "image_style": IMAGE_STYLE,
        "copy_framework": COPY_FRAMEWORK,
    })
    print("Brand DNA fields updated.")

    # Upload cover reference image
    cover_path = BASE_DIR / COVER_IMAGE
    if cover_path.exists():
        print(f"Uploading cover_ref: {COVER_IMAGE}...")
        table.upload_attachment(record_id, "cover_ref", cover_path.name, cover_path.read_bytes(), "image/png")
        print("  Done.")
    else:
        print(f"WARNING: {cover_path} not found, skipping cover.")

    # Upload slide reference images
    for filename in SLIDE_IMAGES:
        slide_path = BASE_DIR / filename
        if slide_path.exists():
            print(f"Uploading slide_refs: {filename}...")
            table.upload_attachment(record_id, "slide_refs", slide_path.name, slide_path.read_bytes(), "image/png")
            print("  Done.")
        else:
            print(f"WARNING: {slide_path} not found, skipping.")

    print("\nEduSim update complete. Status remains draft.")


if __name__ == "__main__":
    main()

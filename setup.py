"""
setup.py — One-time script to create the 3 tabs with correct headers in the Google Sheet,
and seed placeholder rows for the 4 brand automations.

Run once:
    python setup.py

The script is idempotent:
- Will not duplicate headers if tabs already exist with correct headers.
- Will not re-seed brand rows if they already exist (checked by name).

After running, open the Google Sheet and fill in the placeholder fields for each brand,
then change status from 'draft' to 'active' to start publishing.
"""

import os
import json
import uuid

import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1qIgFoIyYQaAhxlR6X6hxO9jOYnRvA_iFXL1Jp6hRTwg")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

TABS = {
    "Automations": [
        "id", "name", "niche", "narrative_prompt", "format_prompt",
        "image_style", "cover_ref_image_url", "slide_ref_image_urls",
        "schedule_days", "schedule_times", "status", "last_run",
    ],
    "Slideshows": [
        "id", "automation_id", "hook", "status", "created_at",
    ],
    "Slides": [
        "id", "slideshow_id", "slide_number", "title_text",
        "body_text", "image_url", "is_hook",
    ],
}

# Placeholder brand automations — fill in the Google Sheet before setting status=active
BRAND_SEEDS = [
    {
        "name": "EduSim",
        "niche": "educational simulations and interactive learning for students",
        "narrative_prompt": (
            "Create engaging educational content that breaks down complex concepts "
            "using simple visuals and step-by-step explanations. Target students aged 14-25. "
            "Cover topics like science, math, and real-world problem solving."
        ),
        "format_prompt": (
            "Tone: clear, encouraging, and curious. Each slide should teach ONE idea. "
            "Hook must create instant curiosity (e.g. 'Nobody taught you this in school...'). "
            "Use short sentences. End with a call-to-action on the last slide."
        ),
        "image_style": (
            "Clean educational illustration style, bright primary colors, "
            "minimalist diagrams, white background, modern flat design"
        ),
        "schedule_days": "Mon,Wed,Fri",
        "schedule_times": "12:00",
    },
    {
        "name": "Vector Vision",
        "niche": "graphic design tips, vector art, and creative tools for designers",
        "narrative_prompt": (
            "Share professional design tips, vector art techniques, and tool shortcuts "
            "for aspiring and working graphic designers. Cover Adobe Illustrator, Figma, "
            "color theory, typography, and portfolio advice."
        ),
        "format_prompt": (
            "Tone: confident, expert, slightly edgy. Hook must be bold and direct "
            "(e.g. 'Your designs look amateur because...'). "
            "Each slide = one actionable tip. Use design terminology naturally."
        ),
        "image_style": (
            "Sleek dark-mode aesthetic, neon accent colors (cyan and magenta), "
            "geometric shapes, professional design portfolio feel, high contrast"
        ),
        "schedule_days": "Tue,Thu,Sat",
        "schedule_times": "14:00",
    },
    {
        "name": "Parho",
        "niche": "study tips, exam strategies, and academic success for Pakistani students",
        "narrative_prompt": (
            "Help Pakistani students (matric, FSc, university) study smarter and ace exams. "
            "Cover memorization techniques, time management, exam tips, and motivation. "
            "Relatable to students balancing family pressure and studies."
        ),
        "format_prompt": (
            "Tone: warm, motivating, peer-to-peer. Mix Urdu phrases naturally where impactful. "
            "Hook should feel personal and relatable (e.g. 'Exams 3 din baad...'). "
            "Keep slides punchy — students have short attention spans."
        ),
        "image_style": (
            "Warm earthy tones, soft gradients in green and gold, "
            "notebook and study aesthetic, cozy Pakistani student vibe"
        ),
        "schedule_days": "Mon,Tue,Wed,Thu,Fri",
        "schedule_times": "18:00",
    },
    {
        "name": "Dreamveil",
        "niche": "dream interpretation, manifestation, and spiritual self-discovery",
        "narrative_prompt": (
            "Explore the meaning of dreams, manifestation techniques, shadow work, and "
            "spiritual growth. Target young adults (18-30) interested in self-discovery, "
            "astrology, and inner transformation. Mystical but grounded."
        ),
        "format_prompt": (
            "Tone: mysterious, poetic, introspective. Hook must create wonder "
            "(e.g. 'If you keep dreaming about this, pay attention...'). "
            "Each slide should feel like a whispered secret. Avoid clinical language."
        ),
        "image_style": (
            "Deep indigo and violet gradients, dreamy soft-focus imagery, "
            "celestial elements, moody atmospheric lighting, ethereal and mystical"
        ),
        "schedule_days": "Mon,Wed,Fri,Sun",
        "schedule_times": "20:00",
    },
]


def main():
    sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not sa_json:
        raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON env var is not set.")

    sa_info = json.loads(sa_json)
    creds = Credentials.from_service_account_info(sa_info, scopes=SCOPES)
    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(SHEET_ID)
    existing_titles = [ws.title for ws in spreadsheet.worksheets()]

    # ------------------------------------------------------------------
    # Create / update tabs with correct headers
    # ------------------------------------------------------------------
    for tab_name, headers in TABS.items():
        if tab_name in existing_titles:
            ws = spreadsheet.worksheet(tab_name)
            existing_headers = ws.row_values(1)
            if existing_headers == headers:
                print(f"[setup] Tab '{tab_name}' already has correct headers — skipping.")
            else:
                ws.update("A1", [headers])
                print(f"[setup] Tab '{tab_name}' headers updated.")
        else:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(headers))
            ws.update("A1", [headers])
            print(f"[setup] Tab '{tab_name}' created with headers.")

    # Remove the default "Sheet1" tab if it exists and is empty
    if "Sheet1" in existing_titles:
        try:
            sheet1 = spreadsheet.worksheet("Sheet1")
            if sheet1.get_all_values() == [] or sheet1.get_all_values() == [[]]:
                spreadsheet.del_worksheet(sheet1)
                print("[setup] Removed default 'Sheet1' tab.")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Seed 4 brand automations (skip if name already exists)
    # ------------------------------------------------------------------
    auto_ws = spreadsheet.worksheet("Automations")
    existing_records = auto_ws.get_all_records()
    existing_names = {str(r.get("name", "")).strip() for r in existing_records}

    headers = TABS["Automations"]
    seeded = 0
    for brand in BRAND_SEEDS:
        if brand["name"] in existing_names:
            print(f"[setup] Brand '{brand['name']}' already exists — skipping.")
            continue

        row = [
            str(uuid.uuid4()),              # id
            brand["name"],                  # name
            brand["niche"],                 # niche
            brand["narrative_prompt"],      # narrative_prompt
            brand["format_prompt"],         # format_prompt
            brand["image_style"],           # image_style
            "",                             # cover_ref_image_url
            "",                             # slide_ref_image_urls
            brand["schedule_days"],         # schedule_days
            brand["schedule_times"],        # schedule_times
            "draft",                        # status — set to 'active' when ready
            "",                             # last_run
        ]
        auto_ws.append_row(row, value_input_option="RAW")
        print(f"[setup] Seeded brand: {brand['name']}  (status=draft)")
        seeded += 1

    if seeded == 0:
        print("[setup] All brands already seeded.")

    print("\n[setup] Done. Your Google Sheet is ready.")
    print(f"  Sheet URL: https://docs.google.com/spreadsheets/d/{SHEET_ID}")
    print("\nNext steps:")
    print("  1. Open the Sheet and review the 4 brand rows in the Automations tab.")
    print("  2. Adjust niche / prompts / image_style / schedule as needed.")
    print("  3. Change status from 'draft' → 'active' for any brand you want to start.")
    print("  4. Run: python main.py")


if __name__ == "__main__":
    main()

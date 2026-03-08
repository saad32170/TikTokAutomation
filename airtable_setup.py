"""
airtable_setup.py — Creates Airtable tables and seeds 4 brand automations.

Run once after creating your base:
    python airtable_setup.py
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BRANDS = [
    {
        "name": "EduSim",
        "niche": "Educational simulations, students 14-25",
        "narrative_prompt": "Create engaging educational content that simplifies complex topics through relatable simulations and scenarios for students aged 14-25.",
        "format_prompt": "Hook should be a surprising fact or question. Each slide reveals one key insight. End with a call to action.",
        "image_style": "clean, modern educational infographic style, bright colors, flat design",
        "cover_ref_image_url": "",
        "slide_ref_image_urls": "",
        "schedule_days": "Mon,Wed,Fri",
        "schedule_times": "12:00",
        "status": "draft",
        "tiktok_account_id": "",
    },
    {
        "name": "Vector Vision",
        "niche": "Graphic design tips, vector art",
        "narrative_prompt": "Share professional graphic design tips and vector art techniques for aspiring designers.",
        "format_prompt": "Hook should tease a design secret or mistake. Slides show step-by-step tips. End with a follow for more.",
        "image_style": "sleek vector illustration style, bold colors, geometric shapes, professional design aesthetic",
        "cover_ref_image_url": "",
        "slide_ref_image_urls": "",
        "schedule_days": "Tue,Thu,Sat",
        "schedule_times": "14:00",
        "status": "draft",
        "tiktok_account_id": "",
    },
    {
        "name": "Parho",
        "niche": "Pakistani student study tips",
        "narrative_prompt": "Help Pakistani students study smarter with practical tips tailored to their curriculum and lifestyle.",
        "format_prompt": "Hook in relatable student language. Slides give actionable study strategies. Warm, encouraging tone.",
        "image_style": "warm, friendly illustration style, soft pastel colors, study-themed visuals",
        "cover_ref_image_url": "",
        "slide_ref_image_urls": "",
        "schedule_days": "Mon,Tue,Wed,Thu,Fri",
        "schedule_times": "18:00",
        "status": "draft",
        "tiktok_account_id": "",
    },
    {
        "name": "Dreamveil",
        "niche": "Dream interpretation, manifestation",
        "narrative_prompt": "Explore dream meanings and manifestation techniques for a spiritually curious audience.",
        "format_prompt": "Hook with a mysterious or mystical angle. Slides reveal dream symbolism or manifestation steps. Ethereal tone.",
        "image_style": "dreamy, ethereal digital art, deep purples and blues, mystical atmosphere, soft glows",
        "cover_ref_image_url": "",
        "slide_ref_image_urls": "",
        "schedule_days": "Mon,Wed,Fri,Sun",
        "schedule_times": "20:00",
        "status": "draft",
        "tiktok_account_id": "",
    },
]


def create_tables(api: Api, base_id: str):
    base = api.base(base_id)

    print("Creating Automations table...")
    base.create_table(
        name="Automations",
        fields=[
            {"name": "name", "type": "singleLineText"},
            {"name": "niche", "type": "singleLineText"},
            {"name": "narrative_prompt", "type": "multilineText"},
            {"name": "format_prompt", "type": "multilineText"},
            {"name": "image_style", "type": "singleLineText"},
            {"name": "cover_ref_image_url", "type": "url"},
            {"name": "slide_ref_image_urls", "type": "multilineText"},
            {"name": "schedule_days", "type": "singleLineText"},
            {"name": "schedule_times", "type": "singleLineText"},
            {
                "name": "status",
                "type": "singleSelect",
                "options": {"choices": [{"name": "draft"}, {"name": "active"}]},
            },
            {"name": "last_run", "type": "singleLineText"},
            {"name": "tiktok_account_id", "type": "singleLineText"},
        ],
    )
    print("  Done.")

    print("Creating Slideshows table...")
    base.create_table(
        name="Slideshows",
        fields=[
            {"name": "hook", "type": "singleLineText"},
            {"name": "automation_id", "type": "singleLineText"},
            {
                "name": "status",
                "type": "singleSelect",
                "options": {
                    "choices": [
                        {"name": "generating"},
                        {"name": "rendering"},
                        {"name": "ready"},
                        {"name": "published"},
                    ]
                },
            },
            {"name": "created_at", "type": "singleLineText"},
        ],
    )
    print("  Done.")

    print("Creating Slides table...")
    base.create_table(
        name="Slides",
        fields=[
            {"name": "title_text", "type": "singleLineText"},
            {"name": "slideshow_id", "type": "singleLineText"},
            {"name": "slide_number", "type": "number", "options": {"precision": 0}},
            {"name": "body_text", "type": "multilineText"},
            {"name": "image_url", "type": "url"},
            {"name": "is_hook", "type": "checkbox", "options": {"icon": "check", "color": "greenBright"}},
        ],
    )
    print("  Done.")


def seed_brands(api: Api, base_id: str):
    table = api.table(base_id, "Automations")
    print("\nSeeding 4 brand automations...")
    for brand in BRANDS:
        table.create(brand)
        print(f"  Created: {brand['name']}")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key:
        raise SystemExit("ERROR: AIRTABLE_API_KEY not set in .env")
    if not base_id:
        raise SystemExit("ERROR: AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    create_tables(api, base_id)
    seed_brands(api, base_id)
    print("\nSetup complete! All 4 brands seeded as 'draft'. Flip to 'active' when ready.")


if __name__ == "__main__":
    main()

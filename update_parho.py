"""
update_parho.py — Push enriched brand DNA and reference images for Parho to Airtable.
Corrects the old "Pakistani study tips" data with accurate brand DNA from parho.app.
Status is left as-is — does NOT activate the automation.

Run once: python update_parho.py
"""

import os
from pathlib import Path
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).parent / "references" / "parho"

# Note: Parho is a desktop web app — screenshots are landscape and used as
# style references only (color palette, UI aesthetic), not as CTA base images.

NARRATIVE_PROMPT = (
    "Parho is an AI-powered web app that lets you read, analyze, and chat with any PDF. "
    "Upload any document — research paper, textbook, contract, report — and get instant "
    "AI answers, summaries, and in-text explanations without ever leaving the document. "
    "Supports 8+ languages including Urdu and Arabic. Free tier available. "
    "Target: students, researchers, professionals, and knowledge workers who deal with "
    "dense documents daily, particularly South Asian and multilingual audiences. "
    "Pain point: reading long PDFs is slow and exhausting — you spend hours in a document "
    "and still can't find what you need or understand what you've read. "
    "Aspiration: get the insights from any document in minutes, not hours. "
    "Brand voice: clean, direct, productivity-focused. Name means 'Read' in Urdu. "
    "Tagline: 'Read PDFs with AI.'"
)

FORMAT_PROMPT = (
    "Use the BAB framework: Before -> After -> Bridge. "
    "Hook = the Before pain: opening a 40-page PDF and dreading every word. "
    "Slides 1-2 = deepen the Before: hours wasted skimming, still not understanding the "
    "key points, highlighting everything which means highlighting nothing. "
    "Slides 3-4 = the After: you ask 'What is the main argument?' and get a crisp answer "
    "in seconds. You highlight a confusing paragraph and Parho explains it instantly. "
    "Slides 5-6 = the Bridge: Parho turns any PDF into a conversation — upload, ask, understand. "
    "CTA: 'Try Parho free. Link in bio.' "
    "Tone: clean, direct, practical. Use 'you'. "
    "Specificity beats abstraction — '40-page PDF', '3 seconds', real scenarios."
)

# Voice-to-style mapping (from voice axes scored from screenshots + parho.app):
# rational_emotional: 2 (Low) → data overlays, structured grids, cool tones
# bold_subtle: 7 (High) → high contrast, saturated color, heavy type
# traditional_innovative: 8 (High) → futuristic gradients, neon accents, glass
# playful_serious: 3 (Low) → cinematic lighting, desaturated palette, minimal
# Nano-banana: "App/Web Design" + "Minimalism" style
IMAGE_STYLE = (
    "dark mode AI productivity app aesthetic, deep navy and charcoal backgrounds, "
    "bold orange accent highlights, high contrast, futuristic gradients, "
    "cinematic lighting, structured clean minimalist layout, "
    "modern sans-serif typography, abstract document and text visualization, "
    "glass morphism UI panels, cool tones with orange warmth, "
    "1080x1920 vertical, main subject upper frame, bottom 25% minimal clear background"
)

COPY_FRAMEWORK = "BAB"

COVER_IMAGE = "main.png"
SLIDE_IMAGES = ["chatbot.png", "in-text questions.png"]


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    records = table.all(formula="{name} = 'Parho'")
    if not records:
        print("ERROR: No Parho record found in Automations table.")
        return

    record = records[0]
    record_id = record["id"]
    print(f"Found Parho record: {record_id}")

    table.update(record_id, {
        "narrative_prompt": NARRATIVE_PROMPT,
        "format_prompt": FORMAT_PROMPT,
        "image_style": IMAGE_STYLE,
        "copy_framework": COPY_FRAMEWORK,
        "platform": "tiktok",
        "niche": "AI productivity, PDF reading, document analysis",
    })
    print("Brand DNA fields updated.")

    # Upload cover reference
    cover_path = BASE_DIR / COVER_IMAGE
    if cover_path.exists():
        print(f"Uploading cover_ref: {COVER_IMAGE}...")
        table.upload_attachment(record_id, "cover_ref", cover_path.name, cover_path.read_bytes(), "image/png")
        print("  Done.")
    else:
        print(f"WARNING: {cover_path} not found.")

    # Upload slide references
    for filename in SLIDE_IMAGES:
        slide_path = BASE_DIR / filename
        if slide_path.exists():
            print(f"Uploading slide_refs: {filename}...")
            table.upload_attachment(record_id, "slide_refs", slide_path.name, slide_path.read_bytes(), "image/png")
            print("  Done.")
        else:
            print(f"WARNING: {slide_path} not found.")

    print("\nParho update complete. Status unchanged.")


if __name__ == "__main__":
    main()

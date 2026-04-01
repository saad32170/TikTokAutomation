"""
update_dreamveil.py — One-off script to push enriched brand DNA to the Dreamveil
Automations record in Airtable.

Run once: python update_dreamveil.py
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

NARRATIVE_PROMPT = (
    "Dreamveil is an AI-powered iOS dream journal ($9.99/mo) that turns spoken or typed dream "
    "memories into vivid surreal storyboards. Target: creative individuals 18-35 into "
    "self-reflection, memory, and artistic expression. Pain point: 90% of dreams are forgotten "
    "within 10 minutes of waking — there's been no way to capture or revisit them. Aspiration: "
    "preserve and explore their subconscious world visually. Key features: AI scene segmentation, "
    "surreal image generation per dream moment, dream symbolism chat, social sharing. "
    "Brand voice: whimsical but grounded, poetic but practical. Tagline: \"Turn dreams into storyboards.\""
)

FORMAT_PROMPT = (
    "Use the BAB framework: Before → After → Bridge. "
    "Hook = the Before pain: dreams vanish the moment you wake. "
    "Slides 1-2 = deepen the Before: the frustration of forgotten details, recurring dreams "
    "you can't describe. Slides 3-4 = the After: vivid storyboards, emotions relived, "
    "symbolism decoded. Slides 5-6 = the Bridge: Dreamveil captures it for you — speak or type, "
    "AI does the rest. CTA: \"Download Dreamveil. Link in bio.\" "
    "Tone: ethereal, cinematic. Always use \"you\". "
    "Specificity wins — use the \"90% forgotten in 10 minutes\" stat."
)

IMAGE_STYLE = (
    "cinematic dream sequence, deep purples and navy blues, soft volumetric light rays, "
    "surreal illustration style, expressive atmospheric color, futuristic gradients, "
    "organic flowing dreamlike shapes, 1080x1920 vertical, main subject upper frame, "
    "bottom 25% minimal clear background"
)

COPY_FRAMEWORK = "BAB"


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")

    if not api_key or not base_id:
        raise ValueError("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set in .env")

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    # Find the Dreamveil record
    records = table.all(formula="{name} = 'Dreamveil'")
    if not records:
        print("ERROR: No Dreamveil record found in Automations table.")
        return

    record = records[0]
    record_id = record["id"]
    print(f"Found Dreamveil record: {record_id}")

    # Build update payload
    fields = {
        "narrative_prompt": NARRATIVE_PROMPT,
        "format_prompt": FORMAT_PROMPT,
        "image_style": IMAGE_STYLE,
    }

    # Attempt to set copy_framework — Airtable will ignore unknown fields,
    # so this is safe even if the field doesn't exist yet.
    try:
        table.update(record_id, {**fields, "copy_framework": COPY_FRAMEWORK})
        print("Updated with copy_framework field.")
    except Exception:
        # Field may not exist — update without it
        table.update(record_id, fields)
        print("Updated without copy_framework field (field not found in schema).")

    print("\nDreamveil record updated successfully:")
    print(f"  narrative_prompt: {NARRATIVE_PROMPT[:80].encode('ascii', 'replace').decode()}...")
    print(f"  format_prompt:    {FORMAT_PROMPT[:80].encode('ascii', 'replace').decode()}...")
    print(f"  image_style:      {IMAGE_STYLE[:80].encode('ascii', 'replace').decode()}...")
    print(f"  copy_framework:   {COPY_FRAMEWORK}")


if __name__ == "__main__":
    main()

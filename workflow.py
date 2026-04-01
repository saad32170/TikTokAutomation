"""
workflow.py — Orchestrates one full automation run end-to-end.
"""

import random
import time
import traceback

import airtable
import generate_text
import generate_images
import publish


def run_automation(automation: dict):
    """
    Execute a complete slideshow generation pipeline for one automation.

    Steps:
      1. Generate hook + slide text via OpenAI
      2. Write slideshow + slide rows to Google Sheets
      3. Generate images for each slide via FAL AI
      4. Update image URLs in Google Sheets
      5. Mark slideshow as 'ready' (or 'published' once publishing enabled)
      6. Update automation last_run timestamp
    """
    automation_id = automation["id"]
    name = automation.get("name", automation_id)
    print(f"\n[workflow] Starting automation: {name}")

    # ------------------------------------------------------------------
    # Step 1 — Generate text
    # ------------------------------------------------------------------
    print(f"[workflow] Generating slideshow text...")
    content = generate_text.generate_slideshow(automation)
    hook = content["hook"]
    slides_text = content["slides"]
    print(f"[workflow] Hook: {hook!r}  |  Slides: {len(slides_text)}")

    # ------------------------------------------------------------------
    # Step 2 — Write slideshow row + slide rows to Airtable
    # ------------------------------------------------------------------
    print(f"[workflow] Writing to Airtable...")
    slideshow_id = airtable.create_slideshow(automation_id, hook)

    slide_records = []  # [{slide_id, slide_number, title, body, is_hook}]

    # Cover slide (slide_number = 0)
    cover_id = airtable.create_slide(
        slideshow_id=slideshow_id,
        slide_number=0,
        title=hook,
        body="",
        is_hook=True,
    )
    slide_records.append({
        "slide_id": cover_id,
        "slide_number": 0,
        "title": hook,
        "body": "",
        "is_hook": True,
    })

    # Content slides (slide_number = 1..N)
    for i, slide in enumerate(slides_text, start=1):
        slide_id = airtable.create_slide(
            slideshow_id=slideshow_id,
            slide_number=i,
            title=slide.get("title", ""),
            body=slide.get("body", ""),
            is_hook=False,
        )
        slide_records.append({
            "slide_id": slide_id,
            "slide_number": i,
            "title": slide.get("title", ""),
            "body": slide.get("body", ""),
            "is_hook": False,
        })

    # ------------------------------------------------------------------
    # Step 3 — Mark as rendering
    # ------------------------------------------------------------------
    airtable.update_slideshow_status(slideshow_id, "rendering")

    # ------------------------------------------------------------------
    # Step 4 — Generate images
    # ------------------------------------------------------------------
    image_style = automation.get("image_style", "")
    cover_ref_attachments = automation.get("cover_ref", []) or []
    slide_ref_attachments = automation.get("slide_refs", []) or []

    last_slide_number = max(r["slide_number"] for r in slide_records if not r["is_hook"])

    for record in slide_records:
        slide_id = record["slide_id"]
        slide_num = record["slide_number"]
        print(f"[workflow] Generating image for slide {slide_num}...")
        try:
            # Last slide: composite CTA text onto a random app screenshot
            if slide_num == last_slide_number and slide_ref_attachments:
                ref = random.choice(slide_ref_attachments)
                screenshot_bytes = generate_images._fetch_image_bytes(ref.get("url", ""))
                if not screenshot_bytes:
                    raise ValueError("Could not fetch screenshot for CTA slide.")
                print(f"[workflow] Slide {slide_num} CTA using screenshot: {ref.get('filename', '')}")
                image_bytes = generate_images.generate_cta_slide_image(
                    title=record["title"],
                    body=record["body"],
                    screenshot_bytes=screenshot_bytes,
                )
                time.sleep(12)
            else:
                image_bytes = generate_images.generate_slide_image(
                    title=record["title"],
                    body=record["body"],
                    image_style=image_style,
                    is_hook=record["is_hook"],
                    cover_ref_attachments=None,
                    slide_ref_attachments=None,
                )
                time.sleep(12)  # Rate limit buffer for Gemini

            airtable.upload_slide_image(slide_id, image_bytes)
            public_url = publish.upload_media(image_bytes)
            record["image_url"] = public_url
            print(f"[workflow] Slide {slide_num} ready.")
        except Exception:
            print(f"[workflow] WARNING: Image failed for slide {slide_num}:")
            traceback.print_exc()
            # Continue — partial image failures should not block the whole run

    # ------------------------------------------------------------------
    # Step 5 — Publish to TikTok via Blotato
    # ------------------------------------------------------------------
    ordered_urls = [
        r["image_url"]
        for r in sorted(slide_records, key=lambda r: r["slide_number"])
        if r.get("image_url")
    ]

    if ordered_urls:
        publish.publish_to_tiktok(automation, hook, ordered_urls)
        airtable.update_slideshow_status(slideshow_id, "published")
    else:
        print(f"[workflow] WARNING: No images were generated — skipping publish.")
        airtable.update_slideshow_status(slideshow_id, "ready")

    # ------------------------------------------------------------------
    # Step 6 — Update last_run timestamp
    # ------------------------------------------------------------------
    airtable.update_automation_last_run(automation_id)
    print(f"[workflow] Done: {name}  |  slideshow_id={slideshow_id}")

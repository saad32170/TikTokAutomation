"""
workflow.py — Orchestrates one full automation run end-to-end.

Implements:
  #8  Creative fatigue tracking (post_count increment)
  #13 Post count stored in Airtable
  #19 LinkedIn landscape variant generation + upload
  #26 Creative refresh cadence check (TikTok: 5-7 days, LinkedIn: 4-6 weeks)
  #29 Quick Wins log printed after each run
  Caption field from generate_text used for publishing (vs hook for slide cover)
"""

import random
import time
import traceback
from datetime import datetime, timezone, timedelta

import airtable
import generate_text
import generate_images
import publish

# Creative refresh cadence per platform — days between content refreshes (#26)
REFRESH_CADENCE_DAYS = {
    "tiktok":   7,   # TikTok: fastest fatigue (5-7 days)
    "linkedin": 28,  # LinkedIn: 4-6 weeks
}


def _is_refresh_due(automation: dict) -> bool:
    """
    Check if creative refresh is due based on last_refresh date and platform cadence.
    Implements #26.
    """
    cadence = REFRESH_CADENCE_DAYS.get(
        automation.get("platform", "tiktok").lower(), 7
    )
    last_refresh_str = automation.get("last_refresh", "")
    if not last_refresh_str:
        return True
    try:
        last_refresh = datetime.fromisoformat(last_refresh_str.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - last_refresh).days
        if age_days >= cadence:
            print(
                f"[workflow] Creative refresh due — last refresh {age_days}d ago "
                f"(cadence: {cadence}d). Generating fresh content."
            )
            return True
        return False
    except Exception:
        return True


def _print_quick_wins(automation: dict, platform: str):
    """
    Print a Quick Wins checklist relevant to this automation after each run.
    Implements #29.
    """
    wins = ["\n[workflow] QUICK WINS checklist for this automation:"]
    if platform == "tiktok":
        wins += [
            "  [ ] Enable Search Ads Toggle in TikTok Ads Manager campaign settings (2 min)",
            "  [ ] Verify CTA button type is set (not default) in Ads Manager",
            "  [ ] Add trending audio overlay in TikTok video editor before posting",
            "  [ ] Check Spark Ads — whitelist top organic post as Spark Ad for ~50% CTR boost",
            f"  [ ] Monitor CTR — kill creative if CTR <0.5% after 3 days; target ≥1.0%",
            f"  [ ] Refresh creative in {REFRESH_CADENCE_DAYS['tiktok']} days (TikTok fatigue threshold)",
        ]
    elif platform == "linkedin":
        wins += [
            "  [ ] Thought Leader Ad: boost this as a personal profile post for higher reach",
            "  [ ] Add Lead Gen Form if promoting a downloadable offer (13% CVR vs 4% landing page)",
            "  [ ] Verify visibility is PUBLIC in LinkedIn Campaign Manager",
            f"  [ ] Refresh creative in {REFRESH_CADENCE_DAYS['linkedin']} days (LinkedIn cadence)",
            "  [ ] Engage with comments in first 60 minutes — boosts algorithmic distribution",
        ]
    print("\n".join(wins) + "\n")


def _run_linkedin_card(automation: dict):
    """
    LinkedIn path: generate one branded card image per post.
    Single headline on the card, caption drives to site.
    """
    automation_id = automation["id"]
    name          = automation.get("name", automation_id)

    # Step 1 — Generate headline + caption + CTA
    print("[workflow] Generating LinkedIn post text...")
    content  = generate_text.generate_linkedin_post(automation)
    headline = content["headline"]
    caption  = content["caption"]
    cta      = content["cta"]
    print(f"[workflow] Headline: {headline!r}  |  Caption: {caption!r}  |  CTA: {cta!r}")

    # Step 2 — Write to Airtable
    print("[workflow] Writing to Airtable...")
    slideshow_id = airtable.create_slideshow(automation_id, headline)
    slide_id = airtable.create_slide(
        slideshow_id=slideshow_id,
        slide_number=0,
        title=headline,
        body=cta,
        is_hook=True,
    )

    # Step 3 — Mark rendering
    airtable.update_slideshow_status(slideshow_id, "rendering")

    # Step 4 — Generate brand card image
    image_style          = automation.get("image_style", "")
    transformation_logic = automation.get("transformation_logic", "")
    cover_ref_attachments = automation.get("cover_ref", []) or []

    if transformation_logic:
        image_style = image_style + f"\nVisual transformation logic: {transformation_logic}"

    print("[workflow] Generating LinkedIn brand card image...")
    try:
        image_bytes = generate_images.generate_linkedin_brand_card(
            headline=headline,
            cta=cta,
            image_style=image_style,
            cover_ref_attachments=cover_ref_attachments,
        )
        time.sleep(12)  # Gemini rate limit buffer
        airtable.upload_slide_image(slide_id, image_bytes)
        public_url = publish.upload_media(image_bytes)
        print("[workflow] Brand card ready.")
    except Exception:
        print("[workflow] ERROR: Brand card image generation failed:")
        traceback.print_exc()
        airtable.update_slideshow_status(slideshow_id, "ready")
        return

    # Step 5 — Publish
    publish.publish_to_linkedin(automation, caption, [public_url])
    airtable.update_slideshow_status(slideshow_id, "published")

    # Step 6 — Update metadata
    airtable.update_automation_last_run(automation_id)
    airtable.increment_post_count(automation_id)
    airtable.update_last_refresh(automation_id)

    # Step 7 — Quick Wins
    _print_quick_wins(automation, "linkedin")

    print(f"[workflow] Done: {name}  |  slideshow_id={slideshow_id}")


def run_automation(automation: dict):
    """
    Execute a complete slideshow generation pipeline for one automation.

    Steps:
      1. Generate hook + caption + slides
      2. Write slideshow + slide rows to Airtable
      3. Mark as rendering
      4. Generate images (+ landscape variant for LinkedIn)
      5. Publish via platform-appropriate Blotato function
      6. Update post_count, last_refresh, last_run in Airtable
      7. Print Quick Wins checklist
    """
    automation_id = automation["id"]
    name          = automation.get("name", automation_id)
    platform      = automation.get("platform", "tiktok").lower()
    print(f"\n[workflow] Starting automation: {name}  platform={platform}")

    # Refresh cadence check (#26)
    _is_refresh_due(automation)  # logs a notice if due, but always continues

    # ── LinkedIn: single branded card path ────────────────────────────────────
    if platform == "linkedin":
        _run_linkedin_card(automation)
        return

    # ------------------------------------------------------------------
    # Step 1 — Generate text (TikTok carousel)
    # ------------------------------------------------------------------
    print("[workflow] Generating slideshow text...")
    content     = generate_text.generate_slideshow(automation)
    hook        = content["hook"]
    caption     = content["caption"]   # SEO-enriched post caption (#10)
    slides_text = content["slides"]
    print(f"[workflow] Hook: {hook!r}  |  Caption: {caption!r}  |  Slides: {len(slides_text)}")

    # ------------------------------------------------------------------
    # Step 2 — Write slideshow + slide rows to Airtable
    # ------------------------------------------------------------------
    print("[workflow] Writing to Airtable...")
    slideshow_id = airtable.create_slideshow(automation_id, hook)

    slide_records = []

    cover_id = airtable.create_slide(
        slideshow_id=slideshow_id,
        slide_number=0,
        title=hook,
        body="",
        is_hook=True,
    )
    slide_records.append({
        "slide_id": cover_id, "slide_number": 0,
        "title": hook, "body": "", "is_hook": True,
    })

    for i, slide in enumerate(slides_text, start=1):
        slide_id = airtable.create_slide(
            slideshow_id=slideshow_id,
            slide_number=i,
            title=slide.get("title", ""),
            body=slide.get("body", ""),
            is_hook=False,
        )
        slide_records.append({
            "slide_id": slide_id, "slide_number": i,
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
    image_style           = automation.get("image_style", "")
    transformation_logic  = automation.get("transformation_logic", "")
    ad_format_type        = automation.get("ad_format_type", "infeed").lower()
    lead_gen_offer_type   = automation.get("lead_gen_offer_type", "")
    spark_ads_variant     = str(automation.get("spark_ads_variant", "")).lower() == "true"
    cover_ref_attachments = automation.get("cover_ref", []) or []
    slide_ref_attachments = automation.get("slide_refs", []) or []
    total_slides          = len(slide_records)

    last_slide_number = max(r["slide_number"] for r in slide_records if not r["is_hook"])

    for record in slide_records:
        slide_id  = record["slide_id"]
        slide_num = record["slide_number"]
        print(f"[workflow] Generating image for slide {slide_num}...")
        try:
            # TikTok CTA last-slide: composite text over screenshot
            if platform == "tiktok" and slide_num == last_slide_number and slide_ref_attachments:
                ref = random.choice(slide_ref_attachments)
                screenshot_bytes = generate_images._fetch_image_bytes(ref.get("url", ""))
                if not screenshot_bytes:
                    raise ValueError("Could not fetch screenshot for CTA slide.")
                print(f"[workflow] Slide {slide_num} CTA using: {ref.get('filename', '')}")
                image_bytes = generate_images.generate_cta_slide_image(
                    title=record["title"],
                    body=record["body"],
                    screenshot_bytes=screenshot_bytes,
                )
            else:
                image_bytes = generate_images.generate_slide_image(
                    title=record["title"],
                    body=record["body"],
                    image_style=image_style,
                    is_hook=record["is_hook"],
                    cover_ref_attachments=cover_ref_attachments,
                    slide_ref_attachments=slide_ref_attachments,
                    platform=platform,
                    transformation_logic=transformation_logic,
                    ad_format_type=ad_format_type,
                    lead_gen_offer_type=lead_gen_offer_type,
                    spark_ads_variant=spark_ads_variant,
                    slide_index=slide_num,
                    total_slides=total_slides,
                )

            time.sleep(12)  # Gemini rate limit buffer
            airtable.upload_slide_image(slide_id, image_bytes)
            public_url = publish.upload_media(image_bytes)
            record["image_url"] = public_url
            print(f"[workflow] Slide {slide_num} ready.")

        except Exception:
            print(f"[workflow] WARNING: Image failed for slide {slide_num}:")
            traceback.print_exc()

    # LinkedIn landscape variant — generate cover in 1.91:1 for desktop (#19)
    landscape_url = None
    if platform == "linkedin":
        print("[workflow] Generating LinkedIn landscape variant (1200x628)...")
        try:
            landscape_bytes = generate_images.generate_landscape_image(
                title=hook,
                body=slides_text[0].get("body", "") if slides_text else "",
                image_style=image_style,
                transformation_logic=transformation_logic,
            )
            time.sleep(12)
            landscape_url = publish.upload_media(landscape_bytes)
            print(f"[workflow] LinkedIn landscape variant ready.")
        except Exception:
            print("[workflow] WARNING: LinkedIn landscape variant failed:")
            traceback.print_exc()

    # ------------------------------------------------------------------
    # Step 5 — Publish
    # ------------------------------------------------------------------
    ordered_urls = [
        r["image_url"]
        for r in sorted(slide_records, key=lambda r: r["slide_number"])
        if r.get("image_url")
    ]

    if ordered_urls:
        if platform == "linkedin":
            # Use caption (SEO-enriched) for post text, not just hook
            publish.publish_to_linkedin(automation, caption, ordered_urls)
        else:
            publish.publish_to_tiktok(automation, caption, ordered_urls)
        airtable.update_slideshow_status(slideshow_id, "published")
    else:
        print("[workflow] WARNING: No images generated — skipping publish.")
        airtable.update_slideshow_status(slideshow_id, "ready")

    # ------------------------------------------------------------------
    # Step 6 — Update Airtable metadata (#8/#13/#26)
    # ------------------------------------------------------------------
    airtable.update_automation_last_run(automation_id)
    airtable.increment_post_count(automation_id)     # #8/#13 fatigue tracking
    airtable.update_last_refresh(automation_id)       # #26 refresh cadence

    # ------------------------------------------------------------------
    # Step 7 — Quick Wins (#29)
    # ------------------------------------------------------------------
    _print_quick_wins(automation, platform)

    print(f"[workflow] Done: {name}  |  slideshow_id={slideshow_id}")

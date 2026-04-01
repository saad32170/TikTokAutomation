"""
generate_images.py — Generate slide images via Google Gemini (Nano Banana 2).

Flow:
  1. Build a prompt from slide content + image style
  2. Optionally attach a reference screenshot (from Airtable) as image input
  3. Call Gemini — returns raw image bytes
  4. Return bytes (caller handles storage)
"""

import os

import requests as http_requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash-image"  # Nano Banana

_gemini_client = None


def _get_gemini_client():
    global _gemini_client
    if _gemini_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY env var is not set.")
        _gemini_client = genai.Client(api_key=api_key)
    return _gemini_client


def _fetch_image_bytes(url: str) -> bytes | None:
    """Download image bytes from a URL. Returns None on failure."""
    try:
        resp = http_requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"[images] WARNING: Could not fetch reference image: {e}")
        return None


def _build_prompt(title: str, body: str, image_style: str, is_hook: bool) -> str:
    slide_type = "cover slide" if is_hook else "content slide"
    parts = [
        f"Create a TikTok slideshow {slide_type} image.",
        f"Visual style: {image_style}.",
        f"Render the following text directly on the image as a bold readable overlay, "
        f"positioned in the lower third of the image:",
        f"Title: \"{title}\"",
    ]
    if body:
        parts.append(f"Body: \"{body}\"")
    parts.append(
        "Requirements: vertical 9:16 portrait format, "
        "text positioned in the lower third with a semi-transparent dark background panel behind it for contrast, "
        "text must be clearly legible, "
        "visually striking, social media optimized, single image only, no collages or grids."
    )
    return " ".join(parts)


def generate_slide_image(
    title: str,
    body: str,
    image_style: str,
    is_hook: bool,
    cover_ref_attachments: list = None,
    slide_ref_attachments: list = None,
) -> bytes:
    """
    Generate an image for a single slide using Gemini Nano Banana 2.

    Args:
        title:                  Slide heading.
        body:                   Slide body copy.
        image_style:            Visual style description from the automation config.
        is_hook:                True if this is the cover slide.
        cover_ref_attachments:  Airtable attachment list for the cover reference.
        slide_ref_attachments:  Airtable attachment list for slide references.

    Returns:
        Raw PNG image bytes.
    """
    client = _get_gemini_client()
    text_prompt = _build_prompt(title, body, image_style, is_hook)

    contents = []

    refs = cover_ref_attachments if is_hook else slide_ref_attachments
    if refs:
        ref_url = refs[0].get("url", "") if refs else ""
        if ref_url:
            img_bytes = _fetch_image_bytes(ref_url)
            if img_bytes:
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
                text_prompt = (
                    "Use the attached screenshot as a visual style reference for the app's "
                    "look and feel. Do not copy it literally — use it to inform the color "
                    "palette, UI aesthetic, and mood. " + text_prompt
                )

    contents.append(types.Part.from_text(text=text_prompt))

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data

    raise ValueError(f"Gemini returned no image for prompt: {text_prompt[:100]}...")


def generate_cta_slide_image(
    title: str,
    body: str,
    screenshot_bytes: bytes,
) -> bytes:
    """
    Generate a CTA slide using an app screenshot as the base.
    Gemini composites CTA text and graphics on top of the screenshot.

    Args:
        title:            CTA heading (e.g. "Try Dreamveil Free").
        body:             CTA body (e.g. "Link in bio.").
        screenshot_bytes: Raw bytes of the app screenshot to use as base.

    Returns:
        Raw PNG image bytes.
    """
    client = _get_gemini_client()

    prompt = (
        "You are given an app screenshot. Use it as the base for a TikTok CTA slide. "
        "Keep the screenshot visible and recognizable — do not replace or cover it entirely. "
        "Add a bold, high-contrast CTA text overlay positioned in the lower third of the image: "
        f"Title: \"{title}\" — large, prominent text. "
        f"Body: \"{body}\" — smaller text below the title. "
        "Add a semi-transparent dark panel behind the text so it is clearly legible. "
        "Vertical 9:16 portrait format. Social media optimized. Single image only."
    )

    contents = [
        types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
        types.Part.from_text(text=prompt),
    ]

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    for part in response.candidates[0].content.parts:
        if part.inline_data is not None:
            return part.inline_data.data

    raise ValueError("Gemini returned no image for CTA slide.")

"""
publish.py — TikTok publishing via Blotato API v2.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

BLOTATO_API_KEY = os.getenv("BLOTATO_API_KEY")
BASE_URL = "https://backend.blotato.com/v2"


def _headers():
    if not BLOTATO_API_KEY:
        raise ValueError("BLOTATO_API_KEY env var is not set.")
    return {
        "blotato-api-key": BLOTATO_API_KEY,
        "Content-Type": "application/json",
    }


def upload_media(image_bytes: bytes) -> str:
    """
    Upload raw image bytes to Blotato media endpoint.
    Blotato /v2/media accepts a URL, so we use a data URI (base64).
    Returns the Blotato-hosted public URL.
    """
    import base64
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    resp = requests.post(
        f"{BASE_URL}/media",
        json={"url": data_url},
        headers=_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["url"]


def publish_to_tiktok(automation: dict, hook: str, image_urls: list[str]) -> dict:
    """
    Publish a completed slideshow to TikTok via Blotato.

    Args:
        automation:  Automation row — must include 'tiktok_account_id'.
        hook:        Caption text.
        image_urls:  Ordered list of Blotato-hosted public image URLs.
    """
    account_id = str(automation.get("tiktok_account_id", "")).strip()
    if not account_id:
        raise ValueError(
            f"No tiktok_account_id set for automation '{automation.get('name')}'. "
            "Add it to the Automations table in Airtable."
        )

    if not image_urls:
        raise ValueError("No image URLs — cannot publish.")

    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text": hook,
                "mediaUrls": image_urls,
                "platform": "tiktok",
            },
            "target": {
                "targetType": "tiktok",
                "privacyLevel": "PUBLIC_TO_EVERYONE",
                "disabledComments": False,
                "disabledDuet": False,
                "disabledStitch": False,
                "isBrandedContent": False,
                "isYourBrand": False,
                "isAiGenerated": True,
                "autoAddMusic": True,
            },
        }
    }

    resp = requests.post(
        f"{BASE_URL}/posts",
        json=payload,
        headers=_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    result = resp.json()
    print(f"[publish] '{automation.get('name')}' posted to TikTok: {result.get('postSubmissionId', 'unknown')}")
    return result

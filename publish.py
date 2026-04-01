"""
publish.py — TikTok + LinkedIn publishing via Blotato API v2.

Implements:
  #12 CTA button type specification in TikTok payload
"""

import base64
import os

import requests
from dotenv import load_dotenv

load_dotenv()

BLOTATO_API_KEY = os.getenv("BLOTATO_API_KEY")
BASE_URL = "https://backend.blotato.com/v2"

# Valid TikTok CTA button types (#12)
TIKTOK_CTA_BUTTONS = {
    "download":      "DOWNLOAD",
    "learn_more":    "LEARN_MORE",
    "shop_now":      "SHOP_NOW",
    "sign_up":       "SIGN_UP",
    "contact_us":    "CONTACT_US",
    "subscribe":     "SUBSCRIBE",
    "watch_more":    "WATCH_MORE",
    "visit_store":   "VISIT_STORE",
}


def _headers():
    if not BLOTATO_API_KEY:
        raise ValueError("BLOTATO_API_KEY env var is not set.")
    return {
        "blotato-api-key": BLOTATO_API_KEY,
        "Content-Type": "application/json",
    }


def upload_media(image_bytes: bytes) -> str:
    """
    Upload raw image bytes to Blotato media endpoint via base64 data URI.
    Returns the Blotato-hosted public URL.
    """
    b64      = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:image/png;base64,{b64}"

    resp = requests.post(
        f"{BASE_URL}/media",
        json={"url": data_url},
        headers=_headers(),
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["url"]


def publish_to_linkedin(automation: dict, caption: str, image_urls: list[str]) -> dict:
    """
    Publish a completed carousel to LinkedIn via Blotato.

    Args:
        automation:  Automation row — must include 'linkedin_account_id'.
        caption:     Post caption (SEO-enriched, ≤150 chars).
        image_urls:  Ordered list of Blotato-hosted public image URLs.
    """
    account_id = str(automation.get("linkedin_account_id", "")).strip()
    if not account_id:
        raise ValueError(
            f"No linkedin_account_id set for '{automation.get('name')}'. "
            "Add it to the Automations table in Airtable."
        )
    if not image_urls:
        raise ValueError("No image URLs — cannot publish.")

    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text":      caption,
                "mediaUrls": image_urls,
                "platform":  "linkedin",
            },
            "target": {
                "targetType": "linkedin",
                "visibility": "PUBLIC",
            },
        }
    }

    resp = requests.post(f"{BASE_URL}/posts", json=payload, headers=_headers(), timeout=60)
    resp.raise_for_status()
    result = resp.json()
    print(f"[publish] '{automation.get('name')}' posted to LinkedIn: {result.get('postSubmissionId', 'unknown')}")
    return result


def publish_to_tiktok(automation: dict, caption: str, image_urls: list[str]) -> dict:
    """
    Publish a completed carousel to TikTok via Blotato.

    Args:
        automation:  Automation row — must include 'tiktok_account_id'.
        caption:     Post caption with SEO keywords (≤100 chars).
        image_urls:  Ordered list of Blotato-hosted public image URLs.
    """
    account_id = str(automation.get("tiktok_account_id", "")).strip()
    if not account_id:
        raise ValueError(
            f"No tiktok_account_id set for '{automation.get('name')}'. "
            "Add it to the Automations table in Airtable."
        )
    if not image_urls:
        raise ValueError("No image URLs — cannot publish.")

    # CTA button type — map human-readable to Blotato enum (#12)
    raw_cta = automation.get("cta_button_type", "").strip().lower().replace(" ", "_")
    cta_button = TIKTOK_CTA_BUTTONS.get(raw_cta)

    target = {
        "targetType":       "tiktok",
        "privacyLevel":     "PUBLIC_TO_EVERYONE",
        "disabledComments": False,
        "disabledDuet":     False,
        "disabledStitch":   False,
        "isBrandedContent": False,
        "isYourBrand":      False,
        "isAiGenerated":    True,
        "autoAddMusic":     True,   # #11 — always opt into music for sound-on platform
    }
    if cta_button:
        target["ctaType"] = cta_button

    payload = {
        "post": {
            "accountId": account_id,
            "content": {
                "text":      caption,
                "mediaUrls": image_urls,
                "platform":  "tiktok",
            },
            "target": target,
        }
    }

    resp = requests.post(f"{BASE_URL}/posts", json=payload, headers=_headers(), timeout=60)
    resp.raise_for_status()
    result = resp.json()
    print(f"[publish] '{automation.get('name')}' posted to TikTok: {result.get('postSubmissionId', 'unknown')}")
    return result

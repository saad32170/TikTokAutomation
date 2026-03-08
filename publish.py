"""
publish.py — TikTok publishing via Blotato API.

Each automation has its own tiktok_account_id column in the Automations sheet,
so 4 brands post to 4 separate TikTok accounts with their own content.

All publishing code is commented out. Uncomment when ready to go live.
"""

# import os
# import requests
# from dotenv import load_dotenv
#
# load_dotenv()
#
# BLOTATO_API_KEY = os.getenv("BLOTATO_API_KEY")
# BLOTATO_BASE_URL = "https://api.blotato.com/v1"
#
#
# def publish_to_tiktok(automation: dict, slideshow: dict, slides: list[dict]):
#     """
#     Publish a completed slideshow to the TikTok account linked to this automation.
#
#     Args:
#         automation: Automation row dict — must include 'tiktok_account_id'.
#         slideshow:  Slideshow row dict — must include 'hook'.
#         slides:     List of slide dicts — must include 'slide_number', 'image_url'.
#     """
#     if not BLOTATO_API_KEY:
#         raise ValueError("BLOTATO_API_KEY env var is not set.")
#
#     tiktok_account_id = str(automation.get("tiktok_account_id", "")).strip()
#     if not tiktok_account_id:
#         raise ValueError(
#             f"No tiktok_account_id set for automation '{automation.get('name')}'. "
#             "Add it to the Automations tab in Google Sheets."
#         )
#
#     # Sort slides by slide_number so they appear in the correct order
#     ordered_slides = sorted(slides, key=lambda s: int(s["slide_number"]))
#     image_urls = [s["image_url"] for s in ordered_slides if s.get("image_url")]
#
#     if not image_urls:
#         raise ValueError("No image URLs found in slides — cannot publish.")
#
#     caption = slideshow.get("hook", "")
#
#     payload = {
#         "account_id": tiktok_account_id,
#         "platform": "tiktok",
#         "media_type": "slideshow",
#         "images": image_urls,
#         "caption": caption,
#         "music": True,
#         "is_ai_generated": True,
#     }
#
#     headers = {
#         "Authorization": f"Bearer {BLOTATO_API_KEY}",
#         "Content-Type": "application/json",
#     }
#
#     response = requests.post(
#         f"{BLOTATO_BASE_URL}/posts",
#         json=payload,
#         headers=headers,
#         timeout=60,
#     )
#     response.raise_for_status()
#
#     result = response.json()
#     print(f"[publish] '{automation.get('name')}' posted to TikTok: {result.get('id', 'unknown')}")
#     return result

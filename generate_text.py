"""
generate_text.py — Generate slideshow hook + slides via DeepSeek deepseek-chat.
"""

import os
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

SYSTEM_TEMPLATE = """\
You are a social media content strategist who writes TikTok carousel slideshows \
that drive saves, shares, and app installs.

SLIDE STRUCTURE RULES — never break these:
- Hook slide: 5-10 words MAX. Use exactly one psychological trigger: curiosity gap, \
pain point, contrarian claim, or stakes/FOMO. Never start with the brand name.
- Middle slides (2-6): ONE idea per slide. Headline ≤8 words. Body ≤20 words. \
Write for a billboard, not a blog.
- Final slide: One imperative CTA only. Short. E.g. "Try [App] free. Link in bio."
- Total content slides: 5 to 7 (not counting the hook/cover slide).

COPY RULES — always apply:
- Use "you" — always personal, never corporate.
- Active voice only. No passive constructions.
- Numbers beat adjectives. Specific beats vague.
- Banned words: amazing, innovative, powerful, seamless, game-changing, \
revolutionary, cutting-edge, transformative.
- Never start a slide with "Are you looking for..."

OUTPUT: Raw JSON only. No markdown. No code fences. No explanation.

JSON schema:
{{
  "hook": "<cover headline — 5-10 words, one psychological trigger>",
  "slides": [
    {{
      "title": "<slide heading — max 8 words>",
      "body": "<one sentence — max 20 words>"
    }}
  ]
}}
"""

USER_TEMPLATE = """\
BRAND NICHE: {niche}

PRODUCT AND TARGET AUDIENCE:
{narrative_prompt}

HOOK FORMULA AND SLIDE STRUCTURE:
{format_prompt}

Generate the TikTok carousel now. The hook slide is the most critical — \
it decides whether this post gets distributed or dies.
"""


def generate_slideshow(automation: dict) -> dict:
    """
    Generate hook + slides for the given automation config.

    Returns:
        {
            "hook": str,
            "slides": [{"title": str, "body": str}, ...]
        }
    """
    system_prompt = SYSTEM_TEMPLATE.replace(
        "{format_prompt}", automation.get("format_prompt", "").strip()
    )
    user_prompt = (
        USER_TEMPLATE
        .replace("{niche}", automation.get("niche", "").strip())
        .replace("{narrative_prompt}", automation.get("narrative_prompt", "").strip())
        .replace("{format_prompt}", automation.get("format_prompt", "").strip())
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.85,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    data = json.loads(raw)

    hook = data.get("hook", "").strip()
    slides = data.get("slides", [])

    if not hook:
        raise ValueError("DeepSeek response missing 'hook' field.")
    if not slides:
        raise ValueError("DeepSeek response missing 'slides' field.")

    return {"hook": hook, "slides": slides}

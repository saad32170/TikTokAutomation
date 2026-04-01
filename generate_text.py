"""
generate_text.py — Generate slideshow hook + slides (TikTok) OR single branded post
                   (LinkedIn) via DeepSeek deepseek-chat.

Implements:
  #1  Platform-specific character limits (TikTok ≤100, LinkedIn ≤150)
  #2  Audience temperature framework selection (cold/warm/hot)
  #3  TikTok engagement benchmark context (5-16%)
  #4  Spark Ads creator-style copy hint
  #7  LinkedIn Lead Gen Form variant
  #10 Caption SEO keyword injection (TikTok)
  #24 Cross-platform consistency rule
  #27 Thought Leader Ads framing (LinkedIn)
  #30 Parameterized dynamic templates
  #31 Bento grid data-point structure
  #32 Exact data point specification
  + Full framework set: BAB, PAS, SSS, AIDA, 4P, FAB
  LinkedIn single-post: one strong headline + caption driving to site
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

# ── Copy Frameworks ───────────────────────────────────────────────────────────

FRAMEWORK_INSTRUCTIONS = {
    "BAB": """\
NARRATIVE FRAMEWORK — Before, After, Bridge (BAB):
Best for: transformation offers, cold audiences, lifestyle/productivity apps.
- Hook: The "Before" state — make the pain visceral and specific.
- Slides 1-2: Deepen the Before. Relatable consequences, specific frustrations.
- Slides 3-4: Paint the After. Vivid outcome — what life looks like with the problem solved.
- Slides 5-6: The Bridge. How the product closes the gap. Concrete and direct.
- CTA: Single imperative action. One verb, one destination.
""",
    "PAS": """\
NARRATIVE FRAMEWORK — Problem, Agitate, Solution (PAS):
Best for: pain-point products, problem-aware audiences, B2B, retargeting.
- Hook: State the core problem sharply. Specific and relatable.
- Slides 1-2: Agitate — make the consequence of inaction feel real and costly.
- Slides 3-5: Introduce the solution. Specific benefits, not features.
- CTA: One action with urgency.
""",
    "SSS": """\
NARRATIVE FRAMEWORK — Star, Story, Solution:
Best for: brand storytelling, UGC style, emotional campaigns.
- Hook: Introduce the relatable "star" (the user, not the brand).
- Slides 1-3: Tell their story — the challenge they faced.
- Slides 4-6: Reveal the solution and the outcome it produced.
- CTA: Single action.
""",
    "AIDA": """\
NARRATIVE FRAMEWORK — Attention, Interest, Desire, Action (AIDA):
Best for: cold audiences, awareness campaigns, product launches.
- Hook (Attention): Pattern interrupt — surprising stat, bold question, or contrarian claim.
- Slides 1-2 (Interest): What it is and why it matters right now.
- Slides 3-4 (Desire): Benefits and outcomes the audience wants for themselves.
- Slides 5-6 (Action): Build urgency, remove friction, pre-handle objections.
- CTA: Single clear action.
""",
    "4P": """\
NARRATIVE FRAMEWORK — Promise, Picture, Proof, Push (4P):
Best for: high-ticket, premium services, B2B enterprise, LinkedIn.
- Hook (Promise): Bold, specific outcome claim backed by a number.
- Slides 1-2 (Picture): Paint the vivid outcome in concrete detail.
- Slides 3-4 (Proof): Specific evidence — stats, results, client outcomes, social proof.
- Slides 5-6 (Push): Remove objections, create urgency, de-risk the ask.
- CTA: One action.
""",
    "FAB": """\
NARRATIVE FRAMEWORK — Features, Advantages, Benefits (FAB):
Best for: technical products, warm/hot audiences, comparison shoppers.
- Hook: Lead with the single most differentiating feature.
- Slides 1-2: Feature + its specific advantage over alternatives.
- Slides 3-4: Translate each advantage into a tangible, personal benefit.
- Slides 5-6: Reinforce benefits with specifics and proof points.
- CTA: One action.
""",
}

# Audience temperature → default framework mapping (#2)
AUDIENCE_TEMP_DEFAULTS = {
    "cold": "AIDA",   # unaware of brand — attention first
    "warm": "PAS",    # engaged but not converted — agitate the problem
    "hot":  "FAB",    # past customers / high intent — feature-benefit close
}

# ── Platform Rules ────────────────────────────────────────────────────────────

PLATFORM_RULES = {
    "tiktok": """\
PLATFORM: TikTok
- Hook: ≤100 characters total (TikTok caption character limit).
- Include 3-5 high-intent search keywords naturally woven into the hook/caption for TikTok Search discoverability (#10).
- Native, creator-style voice. Sounds like a person, not a brand.
- Energy: fast, punchy, scroll-stopping. Every word must earn its place.
- TikTok organic engagement benchmark: 5-16% — write hooks that demand a save or share (#3).
- Organic feel: avoid corporate polish. Write like a creator sharing a genuine insight (#4 Spark Ads-ready).
""",
    "linkedin": """\
PLATFORM: LinkedIn
- Hook: ≤150 characters total.
- Professional, direct, operator-grade tone. No fluff, no motivational posters.
- Audience: founders, operators, senior professionals. Speak to their KPIs, real decisions, and hard problems.
- Write as thought leadership — hard-won insights, frameworks, or contrarian takes (#27).
- B2B voice: credible, specific, experience-backed. Outcomes over adjectives.
- LinkedIn engagement benchmark: 2-5% — aim for saves and shares from decision-makers.
- If this is a Lead Gen offer: frame every slide around the value of the offer, not the product (#7).
""",
}

# ── System Template ───────────────────────────────────────────────────────────

SYSTEM_TEMPLATE = """\
You are a social media content strategist who writes carousel slideshows \
that drive saves, shares, follows, and installs.
{framework_block}
{platform_rules}
SLIDE STRUCTURE RULES — never break these:
- Hook slide: One psychological trigger only — curiosity gap, pain point, contrarian claim, or stakes/FOMO. Never start with the brand name.
- Middle slides (2-6): ONE idea per slide. Headline ≤8 words. Body ≤20 words. Write for a billboard, not a blog.
- Final slide: One imperative CTA only. Short. E.g. "Try [App] free. Link in bio."
- Total content slides: 5 to 7 (not counting the hook/cover slide).
{bento_block}
COPY RULES — always apply:
- Use "you" — always personal, never corporate.
- Active voice only. No passive constructions.
- Numbers beat adjectives. Specific beats vague. Lead with benefit, not feature (#32).
- Maintain consistent tone, voice, and character across ALL slides — they must feel like one cohesive story (#24/#35).
- Banned words: amazing, innovative, powerful, seamless, game-changing, revolutionary, cutting-edge, transformative.
- Never start a slide with "Are you looking for..."
{language_block}
OUTPUT: Raw JSON only. No markdown. No code fences. No explanation.

JSON schema:
{{
  "hook": "<cover headline — matches platform character limit>",
  "caption": "<post caption with SEO keywords naturally included — ≤100 chars TikTok / ≤150 chars LinkedIn>",
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

Generate the carousel now. The hook slide is the most critical — \
it decides whether this post gets distributed or dies.
"""

# ── LinkedIn Single-Post Templates ────────────────────────────────────────────

LINKEDIN_POST_SYSTEM = """\
You are a B2B content strategist writing LinkedIn posts for a tech studio.
{platform_rules}
{framework_block}
POST RULES — never break these:
- Headline: max 12 words. One sharp insight, contrarian claim, or specific outcome.
  This is the text displayed on the branded card — make it stop a scroll.
- Caption: ≤150 characters. Provides context and drives to site. Thought-leadership tone.
- CTA: 5-8 words. Short imperative that references the site. E.g. "See the work → alpha.muhammadsaad.net"
- Write for founders, operators, senior engineers — people who build and ship.
- Active voice only. Numbers beat adjectives. Specific beats vague.
- Banned words: amazing, innovative, powerful, seamless, game-changing, revolutionary, cutting-edge, transformative.
- Never start with "Are you looking for..."

OUTPUT: Raw JSON only. No markdown. No code fences. No explanation.

JSON schema:
{{
  "headline": "<card headline — max 12 words>",
  "caption": "<post caption ≤150 chars — drives to site>",
  "cta": "<short CTA line for card — 5-8 words, include site URL>"
}}
"""

LINKEDIN_POST_USER = """\
BRAND / STUDIO: {niche}

ABOUT THE BRAND AND AUDIENCE:
{narrative_prompt}

ANGLE AND FOCUS FOR THIS POST:
{format_prompt}
{site_url_line}
Generate the post now. The headline is what gets saved or shared — make it earn its place.
"""

# ── Helpers ───────────────────────────────────────────────────────────────────

def _resolve_framework(automation: dict) -> str:
    """
    Pick the copy framework:
      1. Explicit copy_framework field on the automation.
      2. Derived from audience_temp (cold/warm/hot).
      3. Default: BAB.
    Implements #2 (audience temperature selection).
    """
    explicit = automation.get("copy_framework", "").strip().upper()
    if explicit and explicit in FRAMEWORK_INSTRUCTIONS:
        return explicit
    temp = automation.get("audience_temp", "").strip().lower()
    if temp in AUDIENCE_TEMP_DEFAULTS:
        return AUDIENCE_TEMP_DEFAULTS[temp]
    return "BAB"


def _bento_block(automation: dict) -> str:
    """
    Return bento-grid data-point instruction when brand has exact metrics.
    Implements #31 (6-8 module structure) and #32 (exact data points).
    """
    data_points = automation.get("data_points", "").strip()
    if not data_points:
        return ""
    return (
        "\nBENTO DATA POINTS — embed these exact figures across slides where relevant:\n"
        f"{data_points}\n"
        "Use numbers precisely as given. Do not invent or round.\n"
    )



# ── Main Entry Point ──────────────────────────────────────────────────────────

def generate_slideshow(automation: dict) -> dict:
    """
    Generate hook + caption + slides for the given automation config.

    Returns:
        {
            "hook":    str  — cover headline (used as slide 0 title),
            "caption": str  — full post caption with SEO keywords,
            "slides":  [{"title": str, "body": str}, ...]
        }
    """
    platform       = automation.get("platform", "tiktok").lower()
    framework_key  = _resolve_framework(automation)
    framework_block = "\n" + FRAMEWORK_INSTRUCTIONS[framework_key]
    platform_rules  = PLATFORM_RULES.get(platform, PLATFORM_RULES["tiktok"])
    bento_block     = _bento_block(automation)

    system_prompt = (
        SYSTEM_TEMPLATE
        .replace("{framework_block}", framework_block)
        .replace("{platform_rules}", platform_rules)
        .replace("{bento_block}", bento_block)
        .replace("{language_block}", "")
    )
    user_prompt = (
        USER_TEMPLATE
        .replace("{niche}",            automation.get("niche", "").strip())
        .replace("{narrative_prompt}", automation.get("narrative_prompt", "").strip())
        .replace("{format_prompt}",    automation.get("format_prompt", "").strip())
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.85,
        response_format={"type": "json_object"},
    )

    raw  = response.choices[0].message.content
    data = json.loads(raw)

    hook    = data.get("hook", "").strip()
    slides  = data.get("slides", [])
    caption = data.get("caption", hook).strip() or hook

    if not hook:
        raise ValueError("DeepSeek response missing 'hook' field.")
    if not slides:
        raise ValueError("DeepSeek response missing 'slides' field.")

    return {"hook": hook, "caption": caption, "slides": slides}


def generate_linkedin_post(automation: dict) -> dict:
    """
    Generate a single branded LinkedIn post: headline (card) + caption (post) + CTA (card).

    Returns:
        {
            "headline": str — card headline (max 12 words),
            "caption":  str — post caption (≤150 chars, drives to site),
            "cta":      str — CTA line for the card (5-8 words)
        }
    """
    framework_key   = _resolve_framework(automation)
    framework_block = "\n" + FRAMEWORK_INSTRUCTIONS[framework_key]
    platform_rules  = PLATFORM_RULES["linkedin"]
    site_url        = automation.get("site_url", "").strip()

    system_prompt = (
        LINKEDIN_POST_SYSTEM
        .replace("{platform_rules}", platform_rules)
        .replace("{framework_block}", framework_block)
    )

    site_url_line = f"\nSite URL for CTA: {site_url}\n" if site_url else ""
    user_prompt = (
        LINKEDIN_POST_USER
        .replace("{niche}",            automation.get("niche", "").strip())
        .replace("{narrative_prompt}", automation.get("narrative_prompt", "").strip())
        .replace("{format_prompt}",    automation.get("format_prompt", "").strip())
        .replace("{site_url_line}",    site_url_line)
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_prompt},
        ],
        temperature=0.85,
        response_format={"type": "json_object"},
    )

    raw  = response.choices[0].message.content
    data = json.loads(raw)

    headline = data.get("headline", "").strip()
    caption  = data.get("caption", "").strip()
    cta      = data.get("cta", "").strip()

    if not headline:
        raise ValueError("DeepSeek response missing 'headline' field.")

    return {"headline": headline, "caption": caption or headline, "cta": cta}

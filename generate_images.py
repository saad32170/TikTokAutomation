"""
generate_images.py — Generate slide images via Google Gemini (Nano Banana 2).

Implements:
  #9  Spark Ads organic/creator-style variant
  #11 Sound/music UI visual cue
  #16 Square composition emphasis for LinkedIn
  #17 B2B tone constraints for LinkedIn
  #18 Lead Gen Form image adaptation
  #19 Landscape variant (1200x628) for LinkedIn desktop
  #20 Safe zone text rendering (TikTok)
  #21 TopView premium format support
  #22 Static/video distinction prompting
  #33 Explicit aspect ratio in every prompt
  #34 Specific visual style combinations
  #35 Character visual consistency across slides
  #37 Diagram/visual summarization for LinkedIn educational content
  #38 Hierarchical prompt structure (Scene/Subject/Environment/Lighting/Text/Constraints/Negative)
  #39 Brand transformation logic injection
"""

import os

import requests as http_requests
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash-image"  # Nano Banana 2

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


def _subject_from_content(title: str, body: str) -> str:
    """Derive a subject description from slide copy."""
    if body:
        return f'Visual concept representing: "{title}" — {body}'
    return f'Visual concept representing: "{title}"'


def _build_prompt(
    title: str,
    body: str,
    image_style: str,
    is_hook: bool,
    platform: str = "tiktok",
    transformation_logic: str = "",
    ad_format_type: str = "infeed",
    lead_gen_offer_type: str = "",
    spark_ads_variant: bool = False,
    slide_index: int = 0,
    total_slides: int = 1,
) -> str:
    """
    Build a hierarchical image generation prompt using
    Scene / Visual Style / Subject / Environment / Lighting /
    Text Overlay / Platform Constraints / Negative Prompts structure.
    Implements #38.
    """
    slide_type = "cover slide" if is_hook else "content slide"
    style_block = image_style
    if transformation_logic:  # #39
        style_block += f"\nVisual transformation logic: {transformation_logic}"

    # Character consistency across multi-slide set (#35)
    consistency = (
        "Maintain a consistent visual character, color palette, and compositional "
        f"style across all slides in this carousel (this is slide {slide_index + 1} of {total_slides}). "
        "Same aesthetic treatment throughout."
    ) if total_slides > 1 else ""

    # ── TikTok In-Feed ────────────────────────────────────────────────────
    if platform == "tiktok" and ad_format_type != "topview" and not spark_ads_variant:
        prompt = f"""## SCENE
TikTok carousel {slide_type}. Aspect ratio: 9:16 vertical portrait, 1080x1920px. (#33)

## VISUAL STYLE
{style_block}

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Main subject centered in the upper 60% of the frame.
{consistency}

## ENVIRONMENT
Contextual background that reinforces the slide's concept.
Clean, uncluttered — the visual must support the text, not compete with it.

## LIGHTING
Lighting that matches the brand mood: dramatic and high-contrast for bold brands, \
soft and ambient for lifestyle brands.

## TEXT OVERLAY
Position: center of the safe zone — approximately 40-65% down from the top of the frame.
NEVER place text in the bottom 25% (Y:1470-1920) — TikTok caption/nav UI covers this zone.
NEVER place text in the right 15% (X:940-1080) — TikTok action buttons cover this zone.
Title: "{title}" — bold, prominent, clearly legible.
{"Body: " + chr(34) + body + chr(34) + " — smaller supporting text below title." if body else ""}
Panel: semi-transparent dark background behind text for contrast. (#20)

## PLATFORM CONSTRAINTS
- 1080x1920px, 9:16 vertical — the ONLY accepted format (#22)
- Bottom 25% of image COMPLETELY CLEAR — no text, no key elements
- Right 15% COMPLETELY CLEAR — no text, no key elements
- Single image only, no collages, no grids

## NEGATIVE PROMPTS
No text in bottom 25% of frame. No logos in bottom corners. No horizontal/landscape \
composition. No widescreen framing. No collages or grids. No watermarks. \
No stock photo clichés. No corporate handshakes. No cheesy smiles."""

    # ── TikTok Spark Ads (organic/creator style) (#9) ────────────────────
    elif platform == "tiktok" and spark_ads_variant:
        prompt = f"""## SCENE
TikTok organic-style creator post. Aspect ratio: 9:16 vertical portrait, 1080x1920px.
Style: looks like authentic user-generated content, NOT a polished brand ad. (#9)

## VISUAL STYLE
{style_block}
Raw, authentic, creator-made aesthetic. Slightly imperfect — real, not produced.
Organic TikTok feel: like a genuine creator sharing this with their audience.

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Main subject in natural, candid positioning — upper 60% of frame.
{consistency}

## ENVIRONMENT
Real, relatable setting. Not a studio. Not a clean white background.
Environmental context that a real person would actually be in.

## LIGHTING
Natural light preferred. Slightly imperfect is fine — authentic over perfect.

## TEXT OVERLAY
Minimal text overlay — Spark Ads perform best with organic feel and less text.
If text: hand-written or casual style font, positioned center-safe zone (40-65% from top).
Title: "{title}"
{"Body: " + chr(34) + body + chr(34) if body else ""}

## PLATFORM CONSTRAINTS
- 1080x1920px, 9:16 vertical
- Bottom 25% CLEAR (TikTok UI zone)
- Right 15% CLEAR (action buttons)
- Single image

## NEGATIVE PROMPTS
No polished corporate aesthetic. No studio lighting. No stock photography. \
No brand logo prominently placed. No collages. No bottom-third text."""

    # ── TikTok TopView (premium, higher production quality) (#21) ─────────
    elif platform == "tiktok" and ad_format_type == "topview":
        prompt = f"""## SCENE
TikTok TopView premium ad — first impression when the app opens.
Aspect ratio: 9:16 vertical portrait, 1080x1920px. Higher production quality expected. (#21)

## VISUAL STYLE
{style_block}
Cinematic, premium quality. This is the most visible ad placement on TikTok.

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Hero composition — main subject dominates the upper 60% of the frame with visual impact.
{consistency}

## ENVIRONMENT
Premium, aspirational setting. Every element intentional.

## LIGHTING
Cinematic lighting — dramatic, intentional, high-production.

## TEXT OVERLAY
Positioned 40-65% down from top of frame (safe zone center).
Title: "{title}" — large, cinematic, premium typography.
{"Body: " + chr(34) + body + chr(34) + " — refined supporting text." if body else ""}
Panel: elegant semi-transparent treatment behind text.

## PLATFORM CONSTRAINTS
- 1080x1920px, 9:16 vertical (720x1280 minimum accepted)
- Bottom 25% CLEAR (Y:1470-1920)
- Right 15% CLEAR (X:940-1080)

## NEGATIVE PROMPTS
No amateur quality. No collages. No horizontal framing. No stock photo look. \
No bottom-third text. No right-side elements."""

    # ── LinkedIn Square 1:1 ───────────────────────────────────────────────
    elif platform == "linkedin" and lead_gen_offer_type:  # #18 Lead Gen variant
        offer = lead_gen_offer_type
        prompt = f"""## SCENE
LinkedIn carousel {slide_type} — Lead Gen offer visual.
Aspect ratio: 1:1 square, 1080x1080px. (#16/#33)
This slide promotes a specific offer: {offer}

## VISUAL STYLE
{style_block}
Professional, authoritative. Visual should represent the value of the offer itself — \
show a stylized preview of the {offer} (e.g., document cover, webinar slide, guide thumbnail).

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Square composition, subject centered, optimized for LinkedIn feed scroll-stop. (#16)
Main subject in upper half of frame.
{consistency}

## ENVIRONMENT
Clean, professional, minimal background. White or dark neutral.

## LIGHTING
Professional, well-lit. Flat or subtle gradient lighting.

## TEXT OVERLAY
Centered with minimum 80px padding from all edges.
Title: "{title}" — bold, prominent.
{"Body: " + chr(34) + body + chr(34) + " — supporting text." if body else ""}
Panel: semi-transparent professional background treatment.

## B2B CONSTRAINTS (#17)
- Professional photography or clean illustration style only
- Business-appropriate aesthetic throughout
- No casual, playful, or lifestyle elements
- No oversaturated colors or influencer aesthetics
- Clean, credible, authoritative visual treatment

## NEGATIVE PROMPTS
No casual styling. No fun/playful elements. No lifestyle photography. \
No celebrity or influencer aesthetic. No oversaturated colors. \
No collages. No watermarks. No stock clichés."""

    elif platform == "linkedin":
        diagram_instruction = ""
        if not is_hook:  # Educational diagram hint for content slides (#37)
            diagram_instruction = (
                "If the slide concept lends itself to a diagram, chart, or visual framework "
                "(process flow, comparison table, hierarchy, timeline), prefer that over "
                "abstract illustration — LinkedIn audiences engage strongly with structured visual insights."
            )
        prompt = f"""## SCENE
LinkedIn carousel {slide_type}. Aspect ratio: 1:1 square, 1080x1080px. (#16/#33)

## VISUAL STYLE
{style_block}
{diagram_instruction}

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Square composition, subject centered, optimized for LinkedIn feed scroll-stop. (#16)
Main subject in upper half of frame.
{consistency}

## ENVIRONMENT
Clean, professional, minimal background — white, dark neutral, or subtle gradient.

## LIGHTING
Professional, well-lit. Crisp and clean.

## TEXT OVERLAY
Centered vertically and horizontally with minimum 80px padding from all edges.
Title: "{title}" — bold, prominent, clearly legible.
{"Body: " + chr(34) + body + chr(34) + " — supporting text below title." if body else ""}
Panel: semi-transparent professional background behind text for contrast.

## B2B CONSTRAINTS (#17)
- Professional photography or clean illustration style only
- Business-appropriate, authoritative visual treatment
- No casual, playful, or lifestyle elements
- No oversaturated colors or influencer aesthetics
- Credible and clean

## NEGATIVE PROMPTS
No casual styling. No fun/playful elements. No lifestyle photography. \
No celebrity or influencer aesthetic. No oversaturated colors. \
No collages. No watermarks. No stock clichés. No corporate handshakes."""

    else:
        # Fallback: TikTok default
        prompt = _build_prompt(title, body, image_style, is_hook, platform="tiktok",
                               transformation_logic=transformation_logic,
                               slide_index=slide_index, total_slides=total_slides)

    return prompt


def _call_gemini(contents: list) -> bytes:
    """Call Gemini and return raw PNG bytes."""
    client = _get_gemini_client()
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
    raise ValueError("Gemini returned no image data.")


def generate_slide_image(
    title: str,
    body: str,
    image_style: str,
    is_hook: bool,
    cover_ref_attachments: list = None,
    slide_ref_attachments: list = None,
    platform: str = "tiktok",
    transformation_logic: str = "",
    ad_format_type: str = "infeed",
    lead_gen_offer_type: str = "",
    spark_ads_variant: bool = False,
    slide_index: int = 0,
    total_slides: int = 1,
) -> bytes:
    """
    Generate an image for a single slide using Gemini Nano Banana 2.

    Args:
        title:                Slide heading.
        body:                 Slide body copy.
        image_style:          Visual style from brand DNA.
        is_hook:              True if this is the cover slide.
        cover_ref_attachments: Airtable attachment list for cover reference.
        slide_ref_attachments: Airtable attachment list for slide references.
        platform:             "tiktok" or "linkedin".
        transformation_logic: Brand-specific visual remix instruction (#39).
        ad_format_type:       "infeed" or "topview" (#21).
        lead_gen_offer_type:  Offer type for LinkedIn Lead Gen variant (#18).
        spark_ads_variant:    Generate organic/creator-style image (#9).
        slide_index:          Position in the carousel (0-based) for consistency (#35).
        total_slides:         Total slides for consistency instruction (#35).

    Returns:
        Raw PNG image bytes.
    """
    text_prompt = _build_prompt(
        title, body, image_style, is_hook,
        platform=platform,
        transformation_logic=transformation_logic,
        ad_format_type=ad_format_type,
        lead_gen_offer_type=lead_gen_offer_type,
        spark_ads_variant=spark_ads_variant,
        slide_index=slide_index,
        total_slides=total_slides,
    )

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
                    "palette, UI aesthetic, and mood. "
                    "Subject should be in the upper portion of the frame; bottom area kept clear.\n\n"
                    + text_prompt
                )

    contents.append(types.Part.from_text(text=text_prompt))
    return _call_gemini(contents)


def generate_cta_slide_image(
    title: str,
    body: str,
    screenshot_bytes: bytes,
) -> bytes:
    """
    Generate a TikTok CTA slide compositing text over an app screenshot.
    TikTok-only — always 9:16, respects safe zones.
    """
    prompt = f"""## SCENE
TikTok CTA (call-to-action) slide using an app screenshot as the base.
1080x1920px, 9:16 vertical portrait.

## SUBJECT & COMPOSITION
Keep the screenshot visible and recognizable — do not replace or cover it entirely.
The app UI should be clearly visible in the background.

## TEXT OVERLAY
Position: center of the safe zone (40-65% from top — NOT the bottom quarter).
Title: "{title}" — large, prominent, bold.
{"Body: " + chr(34) + body + chr(34) + " — smaller supporting text below." if body else ""}
Panel: semi-transparent dark background panel behind text for legibility.

## PLATFORM CONSTRAINTS
- 1080x1920px, 9:16 vertical
- Bottom 25% COMPLETELY CLEAR (TikTok caption/nav UI: Y:1470-1920)
- Right 15% COMPLETELY CLEAR (TikTok action buttons: X:940-1080)

## NEGATIVE PROMPTS
No text in bottom 25%. No collages. No horizontal framing."""

    contents = [
        types.Part.from_bytes(data=screenshot_bytes, mime_type="image/png"),
        types.Part.from_text(text=prompt),
    ]
    return _call_gemini(contents)


def generate_linkedin_brand_card(
    headline: str,
    cta: str,
    image_style: str,
    cover_ref_attachments: list = None,
) -> bytes:
    """
    Generate a single LinkedIn branded card at 1080x1080px.
    One post = one card. Headline is the hero element; CTA drives to site.
    Uses brand design system from image_style.
    """
    prompt = f"""## SCENE
LinkedIn branded content card. Single image post — NOT a carousel.
Aspect ratio: 1:1 square, 1080x1080px.
One powerful statement. The type is the design.

## VISUAL STYLE
{image_style}
Editorial brand card aesthetic — think magazine cover meets tech dashboard.
High contrast. Minimal. Intentional whitespace. Every element earns its place.

## COMPOSITION
Vertical hierarchy on a dark or brand-colored background:
1. Headline text: large, bold, centered or left-aligned — occupies upper 55% of frame.
2. Thin horizontal accent line or minimal separator element.
3. CTA text: smaller, positioned in lower safe zone (min 80px from bottom edge).
4. Optional: subtle abstract background texture, gradient, or geometric element.
   Keep it restrained — the text must dominate, not compete.
No complex photography. No illustrations of people. Typography IS the visual.

## TEXT OVERLAY
Headline: "{headline}"
  — Largest element on the card. Bold, prominent, clearly legible.
  — 80px minimum padding from left/right edges.
CTA: "{cta}"
  — Smaller, visually separated from headline, positioned lower.
  — Accent color treatment (lighter or colored to draw the eye).
Minimum 80px padding from all edges.

## B2B CONSTRAINTS
Professional, authoritative, minimal.
Dark background preferred for premium/tech feel.
No casual or lifestyle photography. No stock imagery clichés.
Clean, credible, operator-grade aesthetic.

## NEGATIVE PROMPTS
No people. No stock photography. No clutter. No competing visual elements.
No carousels or multi-panel layouts. No horizontal composition.
No corporate handshakes. No watermarks. No oversaturation."""

    contents = []

    if cover_ref_attachments:
        ref_url = (cover_ref_attachments[0] or {}).get("url", "")
        if ref_url:
            img_bytes = _fetch_image_bytes(ref_url)
            if img_bytes:
                contents.append(types.Part.from_bytes(data=img_bytes, mime_type="image/png"))
                prompt = (
                    "Use the attached image as a brand reference — adopt its color palette, "
                    "typography mood, and aesthetic. Do not copy layout literally.\n\n"
                    + prompt
                )

    contents.append(types.Part.from_text(text=prompt))
    return _call_gemini(contents)


def generate_landscape_image(
    title: str,
    body: str,
    image_style: str,
    transformation_logic: str = "",
) -> bytes:
    """
    Generate a LinkedIn landscape variant at 1200x628px (1.91:1).
    Used for LinkedIn desktop/legacy placements alongside the 1:1 square. (#19)
    """
    style_block = image_style
    if transformation_logic:
        style_block += f"\nVisual transformation logic: {transformation_logic}"

    prompt = f"""## SCENE
LinkedIn landscape image — desktop and legacy placement variant.
Aspect ratio: 1.91:1 horizontal, 1200x628px. (#19)

## VISUAL STYLE
{style_block}
Professional, B2B appropriate, clean and authoritative.

## SUBJECT & COMPOSITION
{_subject_from_content(title, body)}
Horizontal composition. Subject positioned left-center with space for text on the right,
or centered with balanced negative space.

## ENVIRONMENT
Clean, professional, minimal background. White, dark neutral, or subtle gradient.

## LIGHTING
Professional, well-lit. Clean and crisp.

## TEXT OVERLAY
Title: "{title}" — bold, prominent.
{"Body: " + chr(34) + body + chr(34) + " — supporting text below." if body else ""}
Panel: semi-transparent professional background behind text.
Minimum 60px padding from all edges.

## B2B CONSTRAINTS
Professional, authoritative, no casual/playful elements, no lifestyle photography.

## NEGATIVE PROMPTS
No vertical composition. No casual styling. No collages. No stock clichés."""

    contents = [types.Part.from_text(text=prompt)]
    return _call_gemini(contents)

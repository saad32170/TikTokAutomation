"""
update_alpha_v2.py — Refresh Alpha Studio with:
  - Correct brand colors from alpha.muhammadsaad.net CSS (#0E0E0E + #cfff9e lime green)
  - site_url field for CTA generation
  - Rewritten format_prompt for single branded card (not carousel slides)
  - Thought leadership angle focused on AI products / agentic systems

Run: python update_alpha_v2.py
"""

import os
import requests
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

AUTOMATIONS_TABLE_ID = "tbli1HPfFEv3Vcg5g"

NARRATIVE_PROMPT = (
    "Alpha Studio is a venture studio that builds technology products for founders and intrapreneurs. "
    "You come with an idea — Alpha designs, builds, and ships it. You own 100% of the IP. "
    "No equity taken. No long hiring processes. No starting from scratch. "
    "Target audience on LinkedIn: founders with an idea they haven't been able to build, "
    "intrapreneurs inside companies who want to launch something new, "
    "and entrepreneurs who are stuck between idea and execution. Aged 25-45. "
    "Pain point: most founders waste 6-12 months and real money trying to hire the right team, "
    "find a technical co-founder, or figure out how to build — before a single line of code is written. "
    "Aspiration: go from idea to a real, working product fast — with a team that has done it before, "
    "without giving up equity or control. "
    "Brand voice: direct, grounded, founder-empathetic. Sounds like someone who has been there. "
    "No corporate fluff. No tech jargon. Speak to the human side of building a venture. "
    "Site: alpha.muhammadsaad.net"
)

FORMAT_PROMPT = (
    "Single LinkedIn post — one relatable statement per post. Alternate between founder and intrapreneur angles. "
    "Angle rotation (vary each post): "
    "(1) Founder pain — a specific moment every founder knows: the stuck feeling, the wasted time, the idea that never shipped. "
    "(2) Intrapreneur pain — working inside a company with a big idea and nowhere to take it: slow approvals, no dedicated team, politics killing momentum. "
    "(3) Speed advantage — what changes when you have a dedicated build team vs. doing it alone or waiting on internal resources. "
    "(4) Ownership / control — for founders: keeping 100% IP. For intrapreneurs: actually launching something instead of watching it die in a roadmap. "
    "(5) Permission slip — a direct message to someone sitting on an idea, whether inside a company or outside one. "
    "Tone: warm but direct. Sounds like someone who has been in both worlds — not a sales pitch. "
    "No jargon. No tech talk. Accessible to anyone with a business idea, inside or outside a company. "
    "The headline must be immediately relatable — the reader should feel seen. "
    "Caption gives just enough context and points to alpha.muhammadsaad.net. "
    "CTA on the card: short, low-friction. E.g. 'Start building -> alpha.muhammadsaad.net'"
)

IMAGE_STYLE = (
    "near-black background (#0E0E0E), lime green accent color (#cfff9e), "
    "white headline text in Space Grotesk bold, minimal editorial card layout, "
    "glass morphism subtle panel with semi-transparent border, "
    "small lime green geometric accent element (line, dot, or corner mark), "
    "generous padding and whitespace, typographic hierarchy — headline dominates, "
    "CTA in lime green at bottom, dark tech aesthetic, no photography, "
    "1080x1080 square, premium developer-studio brand feel"
)

COPY_FRAMEWORK = "PAS"
SITE_URL = "alpha.muhammadsaad.net"


def ensure_site_url_field(api_key: str, base_id: str):
    """Add site_url field if it doesn't exist."""
    schema_resp = requests.get(
        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
        headers={"Authorization": f"Bearer {api_key}"},
    )
    schema_resp.raise_for_status()
    tables = schema_resp.json().get("tables", [])
    auto_table = next((t for t in tables if t["id"] == AUTOMATIONS_TABLE_ID), None)
    if not auto_table:
        raise SystemExit("ERROR: Automations table not found.")

    existing = {f["name"] for f in auto_table.get("fields", [])}
    if "site_url" in existing:
        print("'site_url' field already exists.")
        return

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{AUTOMATIONS_TABLE_ID}/fields"
    resp = requests.post(url, headers=headers, json={"name": "site_url", "type": "singleLineText"})
    if resp.ok:
        print("Created 'site_url' field.")
    else:
        print(f"Could not create 'site_url' field: {resp.text}")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    ensure_site_url_field(api_key, base_id)

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    records = table.all(formula="{name} = 'Alpha'")
    if not records:
        raise SystemExit("ERROR: Alpha record not found in Airtable.")

    record_id = records[0]["id"]
    print(f"Updating Alpha record: {record_id}")

    table.update(record_id, {
        "narrative_prompt": NARRATIVE_PROMPT,
        "format_prompt":    FORMAT_PROMPT,
        "image_style":      IMAGE_STYLE,
        "copy_framework":   COPY_FRAMEWORK,
        "site_url":         SITE_URL,
        "status":           "draft",
    })

    print("Alpha Studio updated. Status: draft (not activated).")
    print(f"  image_style: near-black + lime green (#cfff9e) brand card")
    print(f"  site_url:    {SITE_URL}")
    print(f"  format:      single branded card (not carousel)")
    print(f"  framework:   {COPY_FRAMEWORK}")


if __name__ == "__main__":
    main()

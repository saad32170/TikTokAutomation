"""
setup_new_fields.py — Add all new Airtable fields required by the 41 enhancements.
Safe to run multiple times — skips fields that already exist.

New fields added to Automations table:
  audience_temp       — cold / warm / hot  (#2)
  data_points         — exact metrics/stats for bento grid  (#31/#32)
  language            — content language if non-English  (#40)
  transformation_logic — brand visual remix instruction  (#39)
  ad_format_type      — infeed / topview  (#21)
  lead_gen_offer_type — offer description for LinkedIn Lead Gen variant  (#18)
  spark_ads_variant   — true/false flag to generate organic-style images  (#9)
  cta_button_type     — download / learn_more / shop_now / sign_up etc.  (#12)
  post_count          — running total of published posts for fatigue tracking  (#8/#13)
  last_refresh        — ISO timestamp of last creative refresh  (#26)

Run once: python setup_new_fields.py
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

AUTOMATIONS_TABLE_ID = "tbli1HPfFEv3Vcg5g"

NEW_FIELDS = [
    {"name": "audience_temp",        "type": "singleLineText"},   # cold/warm/hot
    {"name": "data_points",          "type": "multilineText"},    # exact metrics
    {"name": "language",             "type": "singleLineText"},   # e.g. "Urdu"
    {"name": "transformation_logic", "type": "multilineText"},    # visual remix
    {"name": "ad_format_type",       "type": "singleLineText"},   # infeed/topview
    {"name": "lead_gen_offer_type",  "type": "singleLineText"},   # offer name
    {"name": "spark_ads_variant",    "type": "singleLineText"},   # "true"/"false"
    {"name": "cta_button_type",      "type": "singleLineText"},   # download/learn_more/etc
    {"name": "post_count",           "type": "number",
     "options": {"precision": 0}},
    {"name": "last_refresh",         "type": "singleLineText"},   # ISO timestamp
]


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set.")

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    # Get existing fields
    schema_resp = requests.get(
        f"https://api.airtable.com/v0/meta/bases/{base_id}/tables",
        headers=headers,
    )
    schema_resp.raise_for_status()
    tables = schema_resp.json().get("tables", [])
    auto_table = next((t for t in tables if t["id"] == AUTOMATIONS_TABLE_ID), None)
    if not auto_table:
        raise SystemExit("ERROR: Automations table not found.")

    existing = {f["name"] for f in auto_table.get("fields", [])}
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{AUTOMATIONS_TABLE_ID}/fields"

    created, skipped = [], []
    for field in NEW_FIELDS:
        if field["name"] in existing:
            skipped.append(field["name"])
            continue
        payload = {"name": field["name"], "type": field["type"]}
        if "options" in field:
            payload["options"] = field["options"]
        resp = requests.post(url, headers=headers, json=payload)
        if resp.ok:
            created.append(field["name"])
            print(f"  Created: {field['name']} ({field['type']})")
        else:
            print(f"  FAILED:  {field['name']} — {resp.text}")

    print(f"\nDone. Created {len(created)} fields, skipped {len(skipped)} existing.")
    if skipped:
        print(f"Already existed: {', '.join(skipped)}")


if __name__ == "__main__":
    main()

"""
add_edunudge.py — Adds image attachment field to Slides table + seeds EduNudge brand.
Run once: python add_edunudge.py
"""

import os
import requests
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

EDUNUDGE = {
    "name": "EduNudge",
    "niche": "EdTech for UK students and teachers — exam prep, past papers, personalized learning",
    "narrative_prompt": (
        "Promote EduNudge — an AI-powered EdTech platform used by teachers and students directly (B2C). "
        "Key features:\n"
        "- EduSelect: Build past-paper exams by topic and specification in clicks, curriculum-aligned, instant marking\n"
        "- NudgeMe: Real-time hints while students are solving, helps them think like an examiner\n"
        "- Lab: Virtual practicals so students can run experiments digitally\n"
        "- Challenger: Gamified competition between students — motivating, not stressful\n\n"
        "For teachers: saves 15+ hours/week on grading. Live progress dashboards, easy assignment creation, "
        "lesson planning tools. Reduces paper usage.\n"
        "For students: personalized past papers matched to their level, real-time nudges, "
        "track strengths and weaknesses, compete with friends.\n\n"
        "Target personas:\n"
        "- Teachers: overwhelmed by grading, want better data on student progress, short on planning time\n"
        "- Students (14-18): anxious about exams, study hard but don't know what to fix, want feedback fast"
    ),
    "format_prompt": (
        "Alternate between two hook angles depending on the run:\n"
        "Teacher hooks (pain/proof):\n"
        "- 'You're spending 15 hours a week grading. EduNudge cuts that to zero.'\n"
        "- 'Every teacher deserves to know which students are falling behind — before the exam.'\n"
        "- 'What if you could assign a past paper by topic in 30 seconds?'\n\n"
        "Student hooks (pain/stakes):\n"
        "- 'You revised for weeks. Still blanked in the exam. Here's why.'\n"
        "- 'Stop doing past papers blind. Get nudged in real time.'\n"
        "- 'Your friends are already using this. Are you?'\n\n"
        "Slide structure:\n"
        "1. Hook (teacher time or student exam anxiety)\n"
        "2. Problem (grading overload for teachers / no feedback loop for students)\n"
        "3. Feature: EduSelect (build topic-specific papers instantly, auto-marked)\n"
        "4. Feature: NudgeMe (real-time hints while solving — think like an examiner)\n"
        "5. Feature: Challenger or Lab (gamified competition / virtual practicals)\n"
        "6. Payoff (teachers reclaim time, students improve faster)\n"
        "7. CTA ('Try EduNudge free. Link in bio.')\n\n"
        "Tone: Professional but warm for teachers. Peer-to-peer and energetic for students."
    ),
    "image_style": (
        "Clean modern EdTech UI aesthetic, bright and approachable, "
        "blue and white primary palette with green accents, "
        "split compositions showing teacher dashboard and student interface, "
        "professional educational environment, "
        "clear data visualizations and progress charts as visual elements, "
        "negative space for text overlay, 9:16 vertical"
    ),
    "cover_ref_image_url": "",
    "slide_ref_image_urls": "",
    "schedule_days": "Mon,Tue,Wed,Thu",
    "schedule_times": "16:00",
    "status": "draft",
    "tiktok_account_id": "",
}


def add_image_field_to_slides(api: Api, base_id: str, api_key: str):
    schema = api.base(base_id).schema()
    slides_table = next(t for t in schema.tables if t.name == "Slides")
    existing = {f.name for f in slides_table.fields}

    if "image" not in existing:
        print("Adding 'image' attachment field to Slides table...")
        headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
        url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables/{slides_table.id}/fields"
        resp = requests.post(url, headers=headers, json={"name": "image", "type": "multipleAttachments"})
        resp.raise_for_status()
        print("  Done.")
    else:
        print("'image' field already exists in Slides, skipping.")


def add_edunudge(api: Api, base_id: str):
    table = api.table(base_id, "Automations")
    existing = {r["fields"].get("name") for r in table.all()}
    if "EduNudge" in existing:
        print("EduNudge already exists in Automations, skipping.")
        return
    table.create(EDUNUDGE)
    print("EduNudge added to Automations.")


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    add_image_field_to_slides(api, base_id, api_key)
    add_edunudge(api, base_id)
    print("\nDone.")


if __name__ == "__main__":
    main()

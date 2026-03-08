"""
update_brands.py — Updates Airtable Automations with correct brand info.
Run once: python update_brands.py
"""

import os
from pyairtable import Api
from dotenv import load_dotenv

load_dotenv()

BRAND_UPDATES = {
    "Vector Vision": {
        "niche": "Sports performance analysis — athletes and coaches who want data-driven improvement",
        "narrative_prompt": (
            "Promote Vector Vision — a sports performance analysis app that clips your game footage "
            "using just your phone camera, aggregates performance features, and delivers instant "
            "professional-grade performance reports. No sensors, no expensive equipment required. "
            "Works for multiple sports.\n\n"
            "Target persona: 16-24 male athletes playing club or varsity sports. They watch pro film "
            "on YouTube, know elite players use data, but have never had access to that level of "
            "analysis themselves. They train hard but are guessing without feedback. They're frustrated "
            "that performance data has always been for pros only — until now."
        ),
        "format_prompt": (
            "Use pain/identity or stakes hooks:\n"
            "- 'Your coach can't see everything. This can.'\n"
            "- 'Every rep without data is a rep you can't improve.'\n"
            "- 'Your highlight reel is hiding your weakness.'\n"
            "- 'Film study isn't just for the pros anymore.'\n\n"
            "Slide structure:\n"
            "1. Hook (pain or stakes — data is only for pros, until now)\n"
            "2. Expand (you train hard but you're guessing without feedback)\n"
            "3. Insight (the best athletes study film — now you can too)\n"
            "4. Feature (point your phone at your game, Vector Vision does the rest)\n"
            "5. Feature (speed, reaction time, positioning — automatically tracked)\n"
            "6. Payoff (professional performance report after every game)\n"
            "7. CTA ('Download Vector Vision. Link in bio.')\n\n"
            "Tone: Intense, competitive, direct. Talks like a coach who respects you."
        ),
        "image_style": (
            "Cinematic close-up of an athlete mid-sprint on a floodlit sports field at night, "
            "motion blur on legs, sharp focus on face showing intense concentration, "
            "floating HUD data overlay elements (speed and acceleration numbers) in electric blue, "
            "dark dramatic background, negative space in upper area for text overlay, "
            "9:16 vertical, hyperrealistic photography style, "
            "color palette: black, electric blue, white"
        ),
    },

    "Parho": {
        "niche": "University students and researchers overwhelmed by dense PDF reading",
        "narrative_prompt": (
            "Promote Parho — an AI PDF reader at parho.app where you can highlight any text "
            "and instantly ask questions, getting in-context answers without ever leaving the document. "
            "Also supports full document chat with persistent history across sessions.\n\n"
            "Target persona: 18-26 university students drowning in readings. They re-read the same "
            "paragraph five times and still don't get it. They constantly tab-switch between their "
            "PDF and Google, losing their place and breaking their focus. They put in hours of effort "
            "but retain almost nothing. The problem isn't effort — it's that they have no one to ask "
            "while they're reading. Parho fills that gap."
        ),
        "format_prompt": (
            "Use pain or contrarian hooks:\n"
            "- 'You've read the same paragraph 4 times. Still don't get it.'\n"
            "- 'Stop re-reading. Start asking.'\n"
            "- 'I haven't opened a Google tab while studying in 3 months.'\n"
            "- 'Every PDF reader lets you highlight. None let you ask.'\n\n"
            "Slide structure:\n"
            "1. Hook (relatable reading pain point)\n"
            "2. Problem (every PDF reader is missing one thing: the ability to ask questions)\n"
            "3. Insight (context-switching kills comprehension — you need answers in-document)\n"
            "4. Feature (highlight any text, ask Parho, get instant contextual answer)\n"
            "5. Feature (full document chat + conversation history that persists)\n"
            "6. Payoff (finish readings in half the time, actually understand and remember them)\n"
            "7. CTA ('Try Parho free. Link in bio.' or 'parho.app')\n\n"
            "Tone: Clever, slightly conspiratorial — like a friend who found a cheat code. "
            "Empathetic to student exhaustion."
        ),
        "image_style": (
            "Cozy late-night study setup, warm amber desk lamp casting soft light, "
            "open laptop showing a PDF document with yellow highlighted text, "
            "floating chat bubble UI element displaying a short question and AI response, "
            "soft bokeh background with bookshelves, "
            "realistic editorial photography style, negative space in upper third for text, "
            "9:16 vertical, color palette: warm cream, amber yellow, deep navy"
        ),
    },

    "Dreamveil": {
        "niche": "Creative individuals and dream enthusiasts who want to capture and visualize their dreams",
        "narrative_prompt": (
            "Promote Dreamveil — an app where you speak or type your dream after waking up, "
            "and AI breaks it into scenes, tags key themes (mystery, love, fear), generates surreal "
            "visuals for each scene, and produces a shareable storyboard you can revisit anytime. "
            "You can also chat with the AI to explore the dream's emotions and hidden layers. "
            "Positioned as a fun, creative memory-keeping tool — not a serious dream interpreter. "
            "Requires a paid subscription.\n\n"
            "Target persona: 18-30 creative individuals — journalers, artists, filmmakers, writers, "
            "and curious minds fascinated by dreams and the subconscious. They wake up clinging to "
            "a vivid image before it disappears. They've always wanted a way to hold onto those "
            "moments but had no tool that could do it justice."
        ),
        "format_prompt": (
            "Use wonder, curiosity, or stakes hooks:\n"
            "- 'Your dreams have been disappearing every morning.'\n"
            "- 'Your brain generates 5-7 dreams a night. Most vanish by 9am.'\n"
            "- 'What if your dreams had a visual director?'\n"
            "- 'You had a dream last night. What if you could see it again?'\n\n"
            "Slide structure:\n"
            "1. Hook (dreams disappear — universal feeling, stakes-based)\n"
            "2. Problem (you wake up with a full scene in your head, gone by breakfast)\n"
            "3. Insight (dreams are visual stories — they deserve to be seen)\n"
            "4. Feature (speak or type your dream → AI breaks it into scenes with themes tagged)\n"
            "5. Feature (surreal images generated for each scene → shareable storyboard)\n"
            "6. Payoff (your subconscious, finally on a screen you can revisit and share)\n"
            "7. CTA ('Try Dreamveil. Link in bio.')\n\n"
            "Tone: Mysterious, poetic, slightly mind-bending. Feels like an experience, "
            "not a product pitch. Never clinical."
        ),
        "image_style": (
            "Pop surrealist digital painting of a person floating inside a vast dreamlike space "
            "where reality dissolves into glowing light and impossible geometry, "
            "books and objects drifting weightlessly in deep purple and gold hues, "
            "hyper-detailed watercolor texture with soft ethereal glow, "
            "dreamy atmospheric depth and cinematic wide establishing shot, "
            "subject positioned lower-third, negative space upper half for text overlay, "
            "9:16 vertical"
        ),
    },

    "EduSim": {
        "niche": "Students and self-learners who hate memorization and want to actually understand concepts",
        "narrative_prompt": (
            "Promote EduSim — an AI-powered educational simulation platform where users learn "
            "by interacting with simulated environments instead of reading theory. "
            "The learning model: scenario → simulation → decision → outcome → knowledge. "
            "Covers multiple subjects: physics, history, economics, biology, and more.\n\n"
            "Target persona: 14-22 students and self-learners who hate rote memorization, love games, "
            "are visual and kinesthetic learners, and are frustrated that school never makes concepts "
            "actually stick. They study for hours, feel prepared, then blank on the exam — not because "
            "they're lazy, but because passive reading is a broken way to learn. They need to experience "
            "the concept, not just read about it."
        ),
        "format_prompt": (
            "Use contrarian or pain hooks:\n"
            "- 'You don't learn by reading. You learn by doing.'\n"
            "- 'You studied for 6 hours. Failed anyway. Here's why.'\n"
            "- 'Textbooks are the worst way to learn. Here's proof.'\n"
            "- 'This is for students who hate memorizing but love understanding.'\n\n"
            "Slide structure:\n"
            "1. Hook (challenge traditional studying — contrarian or pain)\n"
            "2. Problem (you've read the chapter, watched the lecture, still confused)\n"
            "3. Insight (your brain locks in knowledge through experience, not repetition)\n"
            "4. Feature (EduSim puts you inside the concept — run a simulation, not a flashcard)\n"
            "5. Feature (physics, history, economics, biology — all playable, all learnable)\n"
            "6. Payoff (pass the exam, actually understand why, keep the knowledge for life)\n"
            "7. CTA ('Try EduSim free. Link in bio.')\n\n"
            "Tone: Energetic, slightly rebellious, peer-to-peer. Challenges the education status quo. "
            "Talks to students like a friend who figured out the system."
        ),
        "image_style": (
            "Cinematic wide shot of a young student standing at the center of an impossible glowing "
            "3D simulation space, surrounded by floating geometric physics models, historical timeline "
            "arcs, and holographic data rings in vibrant electric blue and gold, "
            "deep dark background with dramatic god-ray lighting, "
            "hyper-detailed digital art style, subject showing awe and wonder, "
            "negative space in upper area for text overlay, 9:16 vertical"
        ),
    },
}


def main():
    api_key = os.getenv("AIRTABLE_API_KEY")
    base_id = os.getenv("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("ERROR: AIRTABLE_API_KEY or AIRTABLE_BASE_ID not set in .env")

    api = Api(api_key)
    table = api.table(base_id, "Automations")

    records = table.all()
    for record in records:
        name = record["fields"].get("name", "")
        if name in BRAND_UPDATES:
            table.update(record["id"], BRAND_UPDATES[name])
            print(f"Updated: {name}")
        else:
            print(f"Skipped (no update defined): {name}")

    print("\nAll brands updated.")


if __name__ == "__main__":
    main()

# TikTok Slideshow Automation

Automated TikTok slideshow pipeline for 5 brands. Generates scroll-optimised carousels on a schedule — text via DeepSeek, images via Gemini — and stores everything in Airtable.

## Brands

| Brand | Niche | Schedule |
|---|---|---|
| EduSim | AI educational simulations | Mon/Wed/Fri @ 12:00 |
| EduNudge | EdTech for teachers & students | Mon–Thu @ 16:00 |
| Vector Vision | Sports performance analysis | Tue/Thu/Sat @ 14:00 |
| Parho | AI PDF reader | Mon–Fri @ 18:00 |
| Dreamveil | Dream-to-storyboard app | Mon/Wed/Fri/Sun @ 20:00 |

## Stack

- **Text generation** — DeepSeek `deepseek-chat`
- **Image generation** — Google Gemini `gemini-2.0-flash-preview-image-generation` (Nano Banana)
- **Storage** — Airtable (Automations, Slideshows, Slides tables)
- **Scheduler** — Python `schedule`, runs every hour
- **Publishing** — Blotato (stubbed, ready to enable)

## Airtable Schema

**Automations** — one row per brand. Controls schedule, prompts, image style, and reference screenshots.

**Slideshows** — one row per generated slideshow, linked to an automation.

**Slides** — one row per slide (including cover/hook), with generated image stored as an Airtable attachment.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env`
Copy `.env.example` and fill in your keys:
```
DEEPSEEK_API_KEY=
GEMINI_API_KEY=
BLOTATO_API_KEY=
AIRTABLE_API_KEY=
AIRTABLE_BASE_ID=
```

- **Airtable API key**: airtable.com → Developer Hub → Personal access tokens
  - Scopes needed: `data.records:read`, `data.records:write`, `schema.bases:read`, `schema.bases:write`
- **Airtable Base ID**: from the URL `airtable.com/appXXXXXX/...`
- **DeepSeek**: platform.deepseek.com
- **Gemini**: aistudio.google.com

### 3. Set up Airtable tables
```bash
python airtable_setup.py
```
Creates the 3 tables and seeds all 5 brands as `draft`.

### 4. Upload reference screenshots (optional)
Add app screenshots to `references/<brand>/` folders, then:
```bash
python upload_references.py
```

### 5. Test a single brand
```bash
python test_run.py EduSim
```

### 6. Run the scheduler
```bash
python main.py
```
Runs on startup, then checks for due automations every hour.

## Activating a brand

In Airtable, set the brand's `status` → `active`. It will run automatically on its next scheduled day/time.

## Enabling publishing (Blotato)

1. Add TikTok account IDs to each brand's `tiktok_account_id` field in Airtable
2. Uncomment the publish block in `workflow.py`
3. Uncomment everything in `publish.py`

## Deploying (Render / Railway)

1. Push to GitHub (`.env` is gitignored)
2. Connect repo to Render or Railway
3. Add all `.env` keys as environment variables
4. Entry command: `python main.py`

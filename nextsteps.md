# Next Steps — TikTok Slideshow Automation

Pick up from here tomorrow. Do these in order.

---

## 1. Airtable Setup (5 min)

1. Go to airtable.com → sign up / log in
2. Create a base → Start from scratch → name it `MarketingAutomation`
3. Tell Claude: "set up my Airtable base" — it will run a script to auto-create
   all tables, fields, and seed the 4 brand rows via the API (no manual clicking)

---

## 2. Get Your API Keys (10 min)

### Airtable
- Avatar (top right) → Developer Hub → Personal access tokens → Create token
- Scopes: `data.records:read`, `data.records:write`, `schema.bases:read`
- Also grab your **Base ID** from the URL: `airtable.com/appXXXXXX/...`

### OpenAI
- platform.openai.com → API Keys → Create new key
- Model in use: `gpt-4.1-nano` (cheap)

### Gemini (Nano Banana)
- aistudio.google.com → Get API key
- Model in use: `gemini-2.0-flash-preview-image-generation`

### Blotato
- blotato.com → get API key
- Also grab your 4 TikTok account IDs from Blotato (one per brand)
  — paste each into the `tiktok_account_id` column in Airtable once connected

---

## 3. Create Your .env File (2 min)

Create a file called `.env` in `MarketingAutomation/` and paste this:

```
OPENAI_API_KEY=
GEMINI_API_KEY=
BLOTATO_API_KEY=
AIRTABLE_API_KEY=
AIRTABLE_BASE_ID=
```

Fill in each value from step 2.

---

## 4. Tell Claude to Migrate to Airtable (5 min)

Say: "migrate from Google Sheets to Airtable"

Claude will:
- Rewrite `sheets.py` → `airtable.py`
- Swap `gspread` / `google-auth` for `pyairtable`
- Update all imports in `workflow.py` and `main.py`
- Run `pip install pyairtable` and remove old packages
- Run the Airtable seed script to populate your base

---

## 5. Test a Single Run (5 min)

1. In Airtable, set one brand's `status` → `active`
   and `schedule_days` → today's day (e.g. `Mon`),
   `schedule_times` → current hour (e.g. `14:00`)
2. Run: `python main.py`
3. Watch the terminal — it should:
   - Generate slideshow text via OpenAI
   - Generate 8 images via Gemini → upload to Google Drive
   - Write all rows to Airtable (Slideshows + Slides tabs)
   - Update `last_run` on the automation

---

## 6. Activate Publishing (when ready)

1. Paste TikTok account IDs into `tiktok_account_id` column in Airtable
2. In `workflow.py` uncomment the 3-line publish block (clearly marked)
3. In `publish.py` uncomment everything
4. Set all 4 brands to `status = active`

---

## 7. Deploy to Render or Railway (when ready)

- Push code to a GitHub repo (make sure `.env` is in `.gitignore`)
- Connect repo to Render or Railway
- Add all `.env` keys as environment variables in their dashboard
- Entry command: `python main.py`
- Done — runs 24/7, no intervention needed

---

## Current State of the Codebase

| File | Status |
|---|---|
| `main.py` | Done — scheduler loop |
| `workflow.py` | Done — full pipeline |
| `generate_text.py` | Done — OpenAI gpt-4.1-nano |
| `generate_images.py` | Done — Gemini (Nano Banana) + Google Drive upload |
| `publish.py` | Done — Blotato code written but commented out |
| `sheets.py` | Needs replacing with `airtable.py` |
| `setup.py` | Can be deleted once Airtable is set up |
| `sheet_setup.gs` | Can be deleted once Airtable is set up |
| `requirements.txt` | Needs `pyairtable` added, `gspread`/`google-auth` removed |
| `.env` | Not created yet — do step 3 above |

---

## 4 Brands Summary

| Brand | Niche | Schedule | TikTok ID |
|---|---|---|---|
| EduSim | Educational simulations, students 14-25 | Mon/Wed/Fri @ 12:00 | TBD |
| Vector Vision | Graphic design tips, vector art | Tue/Thu/Sat @ 14:00 | TBD |
| Parho | Pakistani student study tips | Mon-Fri @ 18:00 | TBD |
| Dreamveil | Dream interpretation, manifestation | Mon/Wed/Fri/Sun @ 20:00 | TBD |

All start as `draft` — flip to `active` per brand when ready to go live.

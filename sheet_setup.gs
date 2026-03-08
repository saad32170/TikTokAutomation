/**
 * sheet_setup.gs — Google Apps Script
 * Run this ONCE directly inside your Google Sheet to create all tabs + seed the 4 brands.
 *
 * How to run:
 *   1. Open the Google Sheet
 *   2. Extensions → Apps Script
 *   3. Delete any existing code, paste this entire file
 *   4. Click Run → setupSheet
 *   5. Approve permissions when prompted
 *   6. Done — check your Sheet for the 3 tabs + 4 brand rows
 */

function setupSheet() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();

  // ── Tab definitions ────────────────────────────────────────────────────────

  var TABS = {
    "Automations": [
      "id", "name", "niche", "narrative_prompt", "format_prompt",
      "image_style", "cover_ref_image_url", "slide_ref_image_urls",
      "schedule_days", "schedule_times", "status", "last_run", "tiktok_account_id"
    ],
    "Slideshows": [
      "id", "automation_id", "hook", "status", "created_at"
    ],
    "Slides": [
      "id", "slideshow_id", "slide_number", "title_text",
      "body_text", "image_url", "is_hook"
    ]
  };

  // ── Create / update tabs ───────────────────────────────────────────────────

  for (var tabName in TABS) {
    var headers = TABS[tabName];
    var sheet = ss.getSheetByName(tabName);

    if (!sheet) {
      sheet = ss.insertSheet(tabName);
      Logger.log("Created tab: " + tabName);
    } else {
      Logger.log("Tab already exists: " + tabName);
    }

    // Write headers in row 1
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);

    // Bold + freeze header row
    sheet.getRange(1, 1, 1, headers.length).setFontWeight("bold");
    sheet.setFrozenRows(1);
  }

  // ── Remove default Sheet1 if empty ────────────────────────────────────────

  var defaultSheet = ss.getSheetByName("Sheet1");
  if (defaultSheet && ss.getSheets().length > 1) {
    var data = defaultSheet.getDataRange().getValues();
    if (data.length <= 1 && data[0].join("") === "") {
      ss.deleteSheet(defaultSheet);
      Logger.log("Removed default Sheet1");
    }
  }

  // ── Seed 4 brand automations ───────────────────────────────────────────────

  var autoSheet = ss.getSheetByName("Automations");
  var existing = autoSheet.getDataRange().getValues();
  var existingNames = {};
  for (var i = 1; i < existing.length; i++) {
    existingNames[existing[i][1]] = true; // column B = name
  }

  var brands = [
    {
      name: "EduSim",
      niche: "educational simulations and interactive learning for students",
      narrative_prompt: "Create engaging educational content that breaks down complex concepts using simple visuals and step-by-step explanations. Target students aged 14-25. Cover topics like science, math, and real-world problem solving.",
      format_prompt: "Tone: clear, encouraging, and curious. Each slide should teach ONE idea. Hook must create instant curiosity (e.g. 'Nobody taught you this in school...'). Use short sentences. End with a call-to-action on the last slide.",
      image_style: "Clean educational illustration style, bright primary colors, minimalist diagrams, white background, modern flat design",
      schedule_days: "Mon,Wed,Fri",
      schedule_times: "12:00"
    },
    {
      name: "Vector Vision",
      niche: "graphic design tips, vector art, and creative tools for designers",
      narrative_prompt: "Share professional design tips, vector art techniques, and tool shortcuts for aspiring and working graphic designers. Cover Adobe Illustrator, Figma, color theory, typography, and portfolio advice.",
      format_prompt: "Tone: confident, expert, slightly edgy. Hook must be bold and direct (e.g. 'Your designs look amateur because...'). Each slide = one actionable tip. Use design terminology naturally.",
      image_style: "Sleek dark-mode aesthetic, neon accent colors (cyan and magenta), geometric shapes, professional design portfolio feel, high contrast",
      schedule_days: "Tue,Thu,Sat",
      schedule_times: "14:00"
    },
    {
      name: "Parho",
      niche: "study tips, exam strategies, and academic success for Pakistani students",
      narrative_prompt: "Help Pakistani students (matric, FSc, university) study smarter and ace exams. Cover memorization techniques, time management, exam tips, and motivation. Relatable to students balancing family pressure and studies.",
      format_prompt: "Tone: warm, motivating, peer-to-peer. Mix Urdu phrases naturally where impactful. Hook should feel personal and relatable (e.g. 'Exams 3 din baad...'). Keep slides punchy — students have short attention spans.",
      image_style: "Warm earthy tones, soft gradients in green and gold, notebook and study aesthetic, cozy Pakistani student vibe",
      schedule_days: "Mon,Tue,Wed,Thu,Fri",
      schedule_times: "18:00"
    },
    {
      name: "Dreamveil",
      niche: "dream interpretation, manifestation, and spiritual self-discovery",
      narrative_prompt: "Explore the meaning of dreams, manifestation techniques, shadow work, and spiritual growth. Target young adults (18-30) interested in self-discovery, astrology, and inner transformation. Mystical but grounded.",
      format_prompt: "Tone: mysterious, poetic, introspective. Hook must create wonder (e.g. 'If you keep dreaming about this, pay attention...'). Each slide should feel like a whispered secret. Avoid clinical language.",
      image_style: "Deep indigo and violet gradients, dreamy soft-focus imagery, celestial elements, moody atmospheric lighting, ethereal and mystical",
      schedule_days: "Mon,Wed,Fri,Sun",
      schedule_times: "20:00"
    }
  ];

  var seeded = 0;
  for (var b = 0; b < brands.length; b++) {
    var brand = brands[b];
    if (existingNames[brand.name]) {
      Logger.log("Brand already exists, skipping: " + brand.name);
      continue;
    }
    autoSheet.appendRow([
      Utilities.getUuid(),   // id
      brand.name,            // name
      brand.niche,           // niche
      brand.narrative_prompt,// narrative_prompt
      brand.format_prompt,   // format_prompt
      brand.image_style,     // image_style
      "",                    // cover_ref_image_url
      "",                    // slide_ref_image_urls
      brand.schedule_days,   // schedule_days
      brand.schedule_times,  // schedule_times
      "draft",               // status — change to 'active' when ready
      "",                    // last_run
      ""                     // tiktok_account_id — paste your TikTok account ID for this brand
    ]);
    seeded++;
    Logger.log("Seeded brand: " + brand.name);
  }

  // ── Done ──────────────────────────────────────────────────────────────────

  var msg = "Setup complete!\n\n"
    + "✓ 3 tabs created: Automations, Slideshows, Slides\n"
    + "✓ " + seeded + " brand(s) seeded (status=draft)\n\n"
    + "Next: set status → 'active' for the brands you want to run, then start main.py";

  SpreadsheetApp.getUi().alert(msg);
  Logger.log(msg);
}

#!/usr/bin/env python3
"""
Builds the interactive Side-by-Side IIIF Facsimile, Diplomatic Transcription,
TEI P5 XML, and Aligned Translation Explorer (ms990_explorer.html) for
Wellcome Collection MS.990 (Work ID: ceuwj8kj / Sierra ID: b18775275).

Features:
- Expandable / Maximizable Facsimile Viewer:
    * 50/50 Balanced Split
    * 75% Wide Facsimile (Hero View)
    * 100% Full-Screen Manuscript View (Zero distraction, full page width)
- Direct Overlaid Text on Manuscript Page:
    * Interactive line bounding boxes overlaid directly on the manuscript handwriting
    * Text-on-Page Mode: renders translation or diplomatic text directly over the manuscript lines
    * Floating HUD Popover on hover/click: tells you exactly what that line/area says in German and English, with editorial notes and live zoomed IIIF crop
    * Lock/Pin popover feature
- Continuous Manuscript Scroll vs Single Page Focus Modes
- Global Cross-Page Corpus Search across all 745 canvases / transcribed leaves
- Container-aware reliable image loading with local and IIIF fallbacks
- 23 transcribed pages (Canvases 2, 3, 7–26, 723)
"""
import json
from pathlib import Path
import generate_edition_outputs as geo

WORKSPACE_DIR = Path(__file__).resolve().parent
ARTIFACT_DIR = Path("/Users/jonathancates/.gemini/antigravity/brain/71b1f38a-1aa5-4bb4-9e45-85957482a837")


def build_compact_payload():
    pages_compact = []
    for p in geo.PAGES:
        cols_compact = []
        for c in p["columns"]:
            lines_compact = []
            for ln in c["lines"]:
                lines_compact.append([
                    ln["line_id"],
                    ln["line_num"],
                    ln["line_type"],
                    ln["ulx"],
                    ln["uly"],
                    ln["lrx"],
                    ln["lry"],
                    ln["de"],
                    ln["en"],
                    ln["note"] or "",
                ])
            cols_compact.append({
                "col_id": c["col_id"],
                "col_label": c["col_label"],
                "ulx": c["ulx"],
                "uly": c["uly"],
                "lrx": c["lrx"],
                "lry": c["lry"],
                "lines": lines_compact,
            })
        pages_compact.append({
            "page_id": p["page_id"],
            "canvas_num": p["canvas_num"],
            "jp2": p["jp2"],
            "orig_page": p["orig_page"],
            "folio_side": p["folio_side"],
            "width": p["width"],
            "height": p["height"],
            "frame_box": list(p["frame_box"]),
            "center_rule_x": p.get("center_rule_x"),
            "summary": p["summary"],
            "figures": p.get("figures", []),
            "flap_canvases": p.get("flap_canvases", []),
            "columns": cols_compact,
        })
    return {
        "manifest_v2": geo.IIIF_MANIFEST_V2,
        "manifest_v3": geo.IIIF_MANIFEST_V3,
        "work_url": geo.WORK_URL,
        "glyphs": [
            {"id": g[0], "glyph": g[1], "unicode": g[2], "latin": g[3], "meaning": g[4]}
            for g in geo.GLYPH_TABLE
        ],
        "pages": pages_compact,
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Wellcome MS.990 (ceuwj8kj) — Interactive IIIF &amp; TEI P5 Scholarly Explorer</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    *, *::before, *::after {
      box-sizing: border-box;
    }

    html, body {
      margin: 0;
      padding: 0;
      width: 100%;
      height: 100%;
      overflow: hidden;
    }

    /* CSS Custom Highlight API for non-destructive DOM range search hit highlighting */
    ::highlight(search-results) {
      background-color: #fde047;
      color: #000000;
      text-decoration: underline;
    }

    /* Standardized scrollbars */
    .scroll-pane {
      --scrollbar-thumb: rgba(148, 163, 184, 0.55);
      --scrollbar-track: transparent;
      scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track);
      scrollbar-width: thin;
    }

    @supports not (scrollbar-color: auto) {
      .scroll-pane::-webkit-scrollbar {
        width: 8px;
        height: 8px;
      }
      .scroll-pane::-webkit-scrollbar-track {
        background: var(--scrollbar-track);
      }
      .scroll-pane::-webkit-scrollbar-thumb {
        background-color: var(--scrollbar-thumb);
        border-radius: 9999px;
        border: 2px solid transparent;
        background-clip: content-box;
      }
    }

    .rubric-span {
      color: #dc2626;
      font-weight: 600;
    }

    .dark .rubric-span {
      color: #f87171;
    }

    .line-row-active {
      outline: 2px solid #f59e0b;
      background-color: rgba(245, 158, 11, 0.16) !important;
    }

    /* Prominent Overlaid SVG Line Bounding Boxes & Segmentation on Manuscript */
    .svg-zone-line {
      fill: rgba(37, 99, 235, 0.12); /* Visible translucent blue/slate highlight */
      stroke: rgba(37, 99, 235, 0.45); /* Visible crisp border */
      stroke-width: 8px;
      cursor: pointer;
      transition: fill 0.12s ease, stroke 0.12s ease, stroke-width 0.12s ease;
    }

    .svg-zone-rubric {
      fill: rgba(220, 38, 38, 0.16); /* Warm red/crimson for headings and rubrics */
      stroke: rgba(220, 38, 38, 0.60);
      stroke-width: 10px;
      cursor: pointer;
      transition: fill 0.12s ease, stroke 0.12s ease, stroke-width 0.12s ease;
    }

    .svg-zone-line:hover, .svg-zone-rubric:hover, .svg-line-group:hover .svg-zone-line, .svg-line-group:hover .svg-zone-rubric {
      fill: rgba(245, 158, 11, 0.40) !important; /* Glowing amber on hover */
      stroke: #d97706 !important;
      stroke-width: 16px !important;
      filter: drop-shadow(0 0 16px rgba(245, 158, 11, 0.75));
    }

    .svg-zone-line.active-box, .svg-zone-rubric.active-box, .svg-line-group.active-group .svg-zone-line, .svg-line-group.active-group .svg-zone-rubric {
      fill: rgba(245, 158, 11, 0.52) !important;
      stroke: #b45309 !important;
      stroke-width: 22px !important;
      filter: drop-shadow(0 0 20px rgba(217, 119, 6, 0.85));
    }

    .svg-zone-line.search-hit-box, .svg-zone-rubric.search-hit-box {
      fill: rgba(250, 204, 21, 0.45) !important;
      stroke: #ca8a04 !important;
      stroke-width: 20px !important;
    }

    /* On-page Text Overlay ribbons */
    .svg-text-bg {
      fill: rgba(255, 255, 255, 0.88);
      stroke: rgba(37, 99, 235, 0.35);
      stroke-width: 4px;
      transition: fill 0.12s ease, stroke 0.12s ease;
    }

    .svg-text-bg-rubric {
      fill: rgba(254, 242, 242, 0.94);
      stroke: rgba(220, 38, 38, 0.45);
      stroke-width: 5px;
    }

    .svg-line-group:hover .svg-text-bg {
      fill: rgba(254, 243, 199, 0.98) !important;
      stroke: #f59e0b !important;
      stroke-width: 6px !important;
    }

    .svg-line-group.active-group .svg-text-bg {
      fill: rgba(254, 243, 199, 1.0) !important;
      stroke: #d97706 !important;
      stroke-width: 8px !important;
    }

    .svg-text-label {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      font-weight: 700;
      fill: #0f172a;
      user-select: none;
      pointer-events: none;
    }

    .svg-text-label-de {
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-weight: 700;
      fill: #1e293b;
    }

    .svg-text-label-rubric {
      fill: #991b1b;
      font-weight: 800;
    }

    .active-page-tab {
      background-color: var(--primary) !important;
      color: var(--primary-foreground) !important;
      font-weight: 700 !important;
    }

    .page-divider-sticky {
      position: sticky;
      top: 0;
      z-index: 20;
      backdrop-filter: blur(8px);
    }

    /* Resizable Facsimile Layout Transitions */
    #facsimilePane, #textPane {
      transition: width 0.18s ease-in-out, flex 0.18s ease-in-out;
    }

    /* Floating Manuscript HUD Popover */
    #manuscriptHud {
      box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 8px 10px -6px rgba(0, 0, 0, 0.25);
    }
  </style>
</head>
<body class="bg-[var(--background)] text-[var(--foreground)] font-sans antialiased h-screen flex flex-col overflow-hidden">

  <!-- TOP HEADER & GLOBAL SEARCH BAR -->
  <header class="bg-[var(--card)] border-b border-[var(--border)] px-4 py-2 flex flex-wrap items-center justify-between gap-3 shrink-0 z-30">
    <div class="flex items-center gap-3">
      <span class="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-semibold bg-[var(--primary)] text-[var(--primary-foreground)] shadow-sm">
        Wellcome MS.990
      </span>
      <div>
        <h1 class="text-sm sm:text-base font-bold tracking-tight">
          Arzneibuch (c. 1675) — IIIF Facsimile, Diplomatic Transcription, TEI P5 &amp; Translation Explorer
        </h1>
        <p class="text-xs text-[var(--muted-foreground)]">
          Work <span class="font-mono">ceuwj8kj</span> · Sierra <span class="font-mono">b18775275</span> · Acc. <span class="font-mono">41913</span> · Franciscan House, Austria / South Germany (745 Canvases)
        </p>
      </div>
    </div>

    <!-- GLOBAL CROSS-PAGE SEARCH CONTROLS -->
    <div class="flex flex-wrap items-center gap-2">
      <div class="relative flex items-center">
        <input
          id="searchInput"
          type="search"
          placeholder="Search all pages (e.g. Wienn, Copauia, Zant, Kropff, Angina, 🜔, ℞)..."
          class="w-64 sm:w-80 px-3 py-1.5 text-xs rounded-md bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] focus:outline-none focus:ring-2 focus:ring-[var(--ring)] shadow-inner"
        />
        <button id="clearSearchBtn" type="button" class="absolute right-2 text-xs text-[var(--muted-foreground)] hover:text-[var(--foreground)] hidden">✕</button>
      </div>

      <!-- Scope Filter Select -->
      <select id="searchScopeSelect" class="px-2 py-1.5 text-xs rounded-md bg-[var(--background)] border border-[var(--border)] text-[var(--foreground)] focus:outline-none focus:ring-1 focus:ring-[var(--ring)]">
        <option value="all">Scope: All Text &amp; Notes</option>
        <option value="de">German Diplomatic Only</option>
        <option value="en">English Translation Only</option>
        <option value="notes">Notes &amp; Summaries Only</option>
      </select>

      <span id="hitCountBadge" class="px-2.5 py-1 rounded text-xs font-mono font-medium bg-[var(--secondary)] text-[var(--secondary-foreground)]">
        0 matches
      </span>

      <button id="prevHitBtn" type="button" class="px-2.5 py-1 rounded text-xs bg-[var(--secondary)] text-[var(--secondary-foreground)] hover:opacity-90 border border-[var(--border)] disabled:opacity-40" title="Previous match across all pages (Shift+Enter)">
        ◀ Prev
      </button>
      <button id="nextHitBtn" type="button" class="px-2.5 py-1 rounded text-xs bg-[var(--secondary)] text-[var(--secondary-foreground)] hover:opacity-90 border border-[var(--border)] disabled:opacity-40" title="Next match across all pages (Enter)">
        Next ▶
      </button>

      <button id="toggleResultsDrawerBtn" type="button" class="px-2.5 py-1 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-foreground)] hover:opacity-90 shadow-sm flex items-center gap-1.5">
        <span>📋 Results</span>
        <span id="drawerBadgeCount" class="px-1.5 py-0.2 rounded-full bg-[var(--primary-foreground)] text-[var(--primary)] text-[10px] font-bold hidden">0</span>
      </button>
    </div>
  </header>

  <!-- SECONDARY TOOLBAR: VIEW MODES, EXPANDABLE FACSIMILE WIDTH & PAGE SELECTOR -->
  <div class="bg-[var(--card)] border-b border-[var(--border)] px-4 py-1.5 flex flex-wrap items-center justify-between gap-3 shrink-0 z-20">
    <!-- View Mode Switches & Facsimile Width Sizing Controls -->
    <div class="flex flex-wrap items-center gap-2">
      <!-- Continuous vs Single Page -->
      <div class="inline-flex rounded-md shadow-sm border border-[var(--border)] p-0.5 bg-[var(--background)]">
        <button id="modeContinuousBtn" type="button" class="px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]">
          📜 Continuous Scroll
        </button>
        <button id="modeSingleBtn" type="button" class="px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]">
          📄 Single Page Focus
        </button>
      </div>

      <span class="text-xs text-[var(--muted-foreground)]">|</span>

      <!-- EXPANDABLE FACSIMILE SIZE SWITCHER (User Request: "The box for the manuscript facsimile is also pitifully small. it should be expandable") -->
      <div class="flex items-center gap-1">
        <span class="text-xs font-semibold text-[var(--muted-foreground)]">Facsimile Size:</span>
        <div class="inline-flex rounded-md shadow-sm border border-[var(--border)] p-0.5 bg-[var(--background)]">
          <button id="layoutSplitBtn" type="button" class="px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]" title="Balanced 50/50 Split View">
            ◨ 50% Split
          </button>
          <button id="layoutWideBtn" type="button" class="px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]" title="75% Wide Facsimile (Hero View)">
            ◧ 75% Wide
          </button>
          <button id="layoutFullBtn" type="button" class="px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]" title="100% Full Manuscript (Maximized View)">
            ⛶ 100% Full Page
          </button>
        </div>
      </div>

      <span class="text-xs text-[var(--muted-foreground)]">|</span>

      <!-- Text representation buttons (when text pane is open) -->
      <div id="textViewModeGroup" class="flex items-center gap-1">
        <button data-view="parallel" class="view-btn px-2 py-0.5 rounded text-xs font-medium bg-[var(--primary)] text-[var(--primary-foreground)]">
          Parallel (DE+EN)
        </button>
        <button data-view="diplomatic" class="view-btn px-2 py-0.5 rounded text-xs font-medium bg-[var(--secondary)] text-[var(--secondary-foreground)]">
          Diplomatic
        </button>
        <button data-view="translation" class="view-btn px-2 py-0.5 rounded text-xs font-medium bg-[var(--secondary)] text-[var(--secondary-foreground)]">
          Translation
        </button>
        <button data-view="tei" class="view-btn px-2 py-0.5 rounded text-xs font-medium bg-[var(--secondary)] text-[var(--secondary-foreground)]">
          TEI XML
        </button>
        <button data-view="glyphs" class="view-btn px-2 py-0.5 rounded text-xs font-medium bg-[var(--secondary)] text-[var(--secondary-foreground)]">
          Glyphs (23)
        </button>
      </div>
    </div>

    <!-- Active Page Indicator & Quick Jump Ribbon -->
    <div class="flex items-center gap-2 overflow-hidden">
      <span id="activePageIndicator" class="text-xs font-bold text-[var(--primary)] shrink-0">
        Page 32 (Canvas 9)
      </span>
      <div id="pageTabs" class="flex items-center gap-1 overflow-x-auto max-w-md py-0.5 scroll-pane" role="tablist"></div>
    </div>
  </div>

  <!-- QUICK SEARCH CHIPS BAR (COMPACT SINGLE ROW) -->
  <div class="bg-[var(--background)] border-b border-[var(--border)] px-4 py-1 flex items-center justify-between gap-3 shrink-0 text-xs z-10 overflow-hidden">
    <div class="flex items-center gap-1 overflow-x-auto whitespace-nowrap scroll-pane py-0.5 flex-1 min-w-0">
      <span class="text-[var(--muted-foreground)] font-semibold shrink-0 mr-1 text-[11px] uppercase tracking-wider">Filters:</span>
      <button data-chip="Wienn" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Wienn (Vienna)</button>
      <button data-chip="Copauia" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Balsamo Copauia</button>
      <button data-chip="Fröschel" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Fröschel (Ranula)</button>
      <button data-chip="Angina" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Angina (Hals Enge)</button>
      <button data-chip="Kropff" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Kropff (Goitre)</button>
      <button data-chip="scorbutisches" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Scorbut (Scurvy)</button>
      <button data-chip="Sumer fleckh" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Sumer fleckh (Freckles)</button>
      <button data-chip="Muetter Maill" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Muetter Maill (Naevi)</button>
      <button data-chip="ohrn" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-medium text-xs shrink-0">Ohrn (Otitis)</button>
      <button data-chip="℞" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono font-semibold text-xs shrink-0">℞ Recipe</button>
      <button data-chip="▽" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">▽ Wasser</button>
      <button data-chip="V̈" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">V̈ Wein</button>
      <button data-chip="✚" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">✚ Essig</button>
      <button data-chip="🜔" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">🜔 Salz</button>
      <button data-chip="🜖" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">🜖 Vitriol</button>
      <button data-chip="🜘" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">🜘 Alaun</button>
      <button data-chip="🜕" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">🜕 Salpeter</button>
      <button data-chip="♄" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">♄ Saturnus</button>
      <button data-chip="XXX" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">XXX Camphora</button>
      <button data-chip="☿" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">☿ Mercurius</button>
      <button data-chip="♁" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">♁ Antimonium</button>
      <button data-chip="⊡" class="chip-btn px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--card)] hover:bg-[var(--accent)] font-mono text-xs shrink-0">⊡ Harn</button>
    </div>
    <div id="statusMeta" class="font-mono text-xs text-[var(--muted-foreground)] shrink-0 hidden md:block"></div>
  </div>

  <!-- COLLAPSIBLE SEARCH RESULTS DRAWER -->
  <aside id="searchResultsDrawer" class="hidden bg-[var(--card)] border-b border-[var(--border)] shadow-lg transition-all duration-200 z-20 flex flex-col max-h-72">
    <div class="px-4 py-2 border-b border-[var(--border)] flex flex-wrap items-center justify-between gap-2 bg-[var(--secondary)]">
      <div class="flex items-center gap-2">
        <span class="text-xs font-bold">Corpus Search Results</span>
        <span id="resultsSummaryText" class="text-xs text-[var(--muted-foreground)]"></span>
      </div>
      <div class="flex items-center gap-2">
        <div id="pageFilterChips" class="flex items-center gap-1 overflow-x-auto max-w-xl py-0.5"></div>
        <button id="closeDrawerBtn" type="button" class="text-xs px-2 py-0.5 rounded bg-[var(--background)] hover:bg-[var(--accent)] border border-[var(--border)]">Close ✕</button>
      </div>
    </div>
    <div id="searchResultsList" class="scroll-pane flex-1 overflow-y-auto p-3 divide-y divide-[var(--border)] space-y-2"></div>
  </aside>

  <!-- MAIN EXPANDABLE WORKSPACE -->
  <main class="flex-1 flex flex-row min-h-0 overflow-hidden relative">

    <!-- LEFT / MAIN PANE: EXPANDABLE FACSIMILE VIEWER WITH OVERLAID BOUNDING BOXES -->
    <section id="facsimilePane" class="flex flex-col min-h-0 bg-[var(--card)] border-r border-[var(--border)] relative" style="width: 75%; flex: 0 0 75%;">
      <!-- Facsimile Toolbar with Overlaid Text-on-Page Controls -->
      <div class="px-3 py-1.5 border-b border-[var(--border)] flex flex-wrap items-center justify-between gap-2 text-xs shrink-0 bg-[var(--card)] z-10 shadow-xs">
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-bold text-[var(--foreground)] flex items-center gap-1">
            <span>IIIF Manuscript Facsimile</span>
            <span id="facsimileSizeBadge" class="px-1.5 py-0.2 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] text-[10px] font-mono">75% Wide</span>
          </span>

          <label class="inline-flex items-center gap-1 cursor-pointer font-medium">
            <input type="checkbox" id="toggleBoxes" checked class="rounded" />
            <span>Line Bounding Zones</span>
          </label>

          <label class="inline-flex items-center gap-1 cursor-pointer font-medium">
            <input type="checkbox" id="toggleRules" checked class="rounded" />
            <span>Red Rules &amp; Figures</span>
          </label>

          <!-- OVERLAID TEXT ON PAGE CONTROL (User Request: "I want to have the lines overlaid on the manuscript pager - i don't want a separate page") -->
          <div class="flex items-center gap-1.5 bg-[var(--background)] px-2 py-0.5 rounded border border-[var(--border)]">
            <label class="inline-flex items-center gap-1 cursor-pointer font-medium">
              <input type="checkbox" id="toggleTextOverlay" checked class="rounded" />
              <span>Overlay Text on Page:</span>
            </label>
            <select id="textOverlayLangSelect" class="px-1 py-0 text-xs rounded border border-[var(--border)] bg-[var(--card)] focus:outline-none font-medium">
              <option value="en" selected>English Translation</option>
              <option value="de">German Diplomatic</option>
            </select>
          </div>
        </div>

        <div class="flex items-center gap-1.5">
          <!-- Zoom Controls -->
          <button data-zoom="100" class="zoom-btn px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] text-xs font-medium">Fit</button>
          <button data-zoom="130" class="zoom-btn px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] text-xs font-medium">130%</button>
          <button data-zoom="180" class="zoom-btn px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] text-xs font-medium">180%</button>
          <button data-zoom="240" class="zoom-btn px-2 py-0.5 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] text-xs font-medium">240%</button>

          <!-- Maximize / Toggle Full Screen Button -->
          <button id="quickMaximizeBtn" type="button" class="px-2 py-0.5 rounded border border-[var(--border)] bg-[var(--background)] hover:bg-[var(--accent)] font-medium text-xs flex items-center gap-1" title="Toggle 100% Full-Screen Manuscript View">
            <span>⛶ Maximize</span>
          </button>

          <a id="iiifFullLink" href="#" target="_blank" rel="noopener" class="px-2 py-0.5 rounded border border-[var(--border)] hover:bg-[var(--accent)] font-mono text-xs">
            IIIF ↗
          </a>
        </div>
      </div>

      <!-- Optional Laminated Flap Switcher (Shown on Page 48 / Canvas 25) -->
      <div id="flapControlBar" class="hidden px-3 py-2 bg-[var(--secondary)] border-b border-[var(--border)] text-xs shrink-0 z-10">
        <div class="font-semibold mb-1">Interactive 3D Laminated Eye Dissection Flap Switcher (p. 48, Canvases 25 &amp; 727–730):</div>
        <div id="flapButtons" class="flex flex-wrap gap-1.5"></div>
        <div id="flapStateDesc" class="mt-1 text-xs text-[var(--muted-foreground)]"></div>
      </div>

      <!-- Facsimile Scroll Pane (Holds all pages in continuous mode, or single page in single mode) -->
      <div id="imageScrollPane" class="scroll-pane flex-1 overflow-auto p-4 space-y-8 bg-[var(--background)] relative"></div>

      <!-- Bottom Live Zoomed IIIF Line-Crop Inspector Bar -->
      <div class="p-2.5 border-t border-[var(--border)] bg-[var(--card)] shrink-0 z-10 shadow-sm">
        <div class="flex items-center justify-between text-xs mb-1">
          <span id="cropInspectorTitle" class="font-semibold truncate">Hover or click any line or box to inspect live IIIF #xywh crop</span>
          <span id="cropInspectorCoord" class="font-mono text-[var(--muted-foreground)]"></span>
        </div>
        <div class="h-16 bg-[var(--background)] border border-[var(--border)] rounded overflow-hidden flex items-center justify-center">
          <img id="iiifLineCropImg" src="" alt="Selected line IIIF crop" class="max-h-full w-auto object-contain hidden" />
          <span id="iiifLineCropPlaceholder" class="text-xs text-[var(--muted-foreground)]">Select or hover over a manuscript line or bounding box</span>
        </div>
      </div>

      <!-- FLOATING INTERACTIVE MANUSCRIPT HUD / LINE POPOVER -->
      <!-- Appears anchored directly over or beside any hovered or clicked bounding box on the manuscript -->
      <div id="manuscriptHud" class="hidden absolute z-50 bg-[var(--card)] border border-[var(--border)] rounded-xl p-3.5 max-w-lg transition-all duration-150 backdrop-blur-md bg-opacity-95 shadow-2xl">
        <div class="flex items-center justify-between pb-2 border-b border-[var(--border)] mb-2">
          <div class="flex items-center gap-2">
            <span id="hudBadge" class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] text-xs font-bold">Line</span>
            <span id="hudCoord" class="font-mono text-xs text-[var(--muted-foreground)]"></span>
          </div>
          <div class="flex items-center gap-1.5">
            <button id="hudPinBtn" type="button" class="px-2 py-0.5 rounded text-xs border border-[var(--border)] bg-[var(--background)] hover:bg-[var(--accent)] font-medium" title="Pin / Lock card open">
              📌 Pin
            </button>
            <button id="hudCloseBtn" type="button" class="px-2 py-0.5 rounded text-xs border border-[var(--border)] bg-[var(--background)] hover:bg-[var(--accent)]">
              ✕
            </button>
          </div>
        </div>
        <div class="space-y-2 text-xs">
          <div>
            <div class="font-bold text-[var(--muted-foreground)] uppercase tracking-wider text-[10px]">What it says in German (Diplomatic):</div>
            <div id="hudDeText" class="font-mono text-sm leading-relaxed text-[var(--foreground)] mt-0.5 font-semibold"></div>
          </div>
          <div class="pt-1.5 border-t border-[var(--border)]">
            <div class="font-bold text-[var(--muted-foreground)] uppercase tracking-wider text-[10px]">Modern English Translation:</div>
            <div id="hudEnText" class="text-xs leading-relaxed text-[var(--foreground)] mt-0.5"></div>
          </div>
          <div id="hudNoteSection" class="pt-1.5 border-t border-[var(--border)] hidden">
            <div class="font-bold text-[var(--muted-foreground)] uppercase tracking-wider text-[10px]">Editorial &amp; Medical Gloss:</div>
            <div id="hudNoteText" class="text-xs italic text-[var(--muted-foreground)] mt-0.5"></div>
          </div>
          <div class="pt-2 border-t border-[var(--border)]">
            <div class="font-bold text-[var(--muted-foreground)] uppercase tracking-wider text-[10px] mb-1">Live IIIF Line-Crop Zoom:</div>
            <div class="h-16 bg-black/5 dark:bg-white/5 border border-[var(--border)] rounded overflow-hidden flex items-center justify-center">
              <img id="hudCropImg" src="" alt="Line Crop" class="max-h-full w-auto object-contain" />
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- RIGHT PANE: DOCKED TRANSCRIPTION, TRANSLATION & TEI XML (COLLAPSIBLE / EXPANDABLE) -->
    <section id="textPane" class="flex flex-col min-h-0 bg-[var(--background)] relative" style="width: 25%; flex: 0 0 25%;">
      <!-- Text Scroll Pane (Holds continuous flow of all pages, or single page) -->
      <div id="textScrollPane" class="scroll-pane flex-1 overflow-y-auto p-4 space-y-8"></div>
    </section>

  </main>

  <script>
    const EDITION_DATA = __EDITION_JSON_PAYLOAD__;

    let displayMode = "continuous"; // "continuous" | "single"
    let currentSinglePageIdx = 4;   // Default to Page 32 (Canvas 9) in single page mode
    let currentViewMode = "parallel"; // parallel | diplomatic | translation | tei | glyphs
    let currentZoom = 100;
    let activeLineId = null;

    // Layout width sizing state (50% | 75% | 100%)
    let currentLayoutMode = "wide"; // "split" | "wide" | "full"

    // Text on page overlay state
    let showTextOverlay = true;
    let textOverlayLang = "en"; // "en" | "de"

    // HUD state
    let isHudPinned = false;
    let hudTargetLid = null;

    // Search state
    let searchScope = "all";
    let currentSearchQuery = "";
    let globalSearchResults = []; // [{ pageIdx, page, col, line, lineId, matchField, deSnippet, enSnippet }]
    let currentResultCursor = -1;
    let activePageFilter = null; // null = all, or pageIdx

    // DOM Elements
    const searchInputEl = document.getElementById("searchInput");
    const clearSearchBtnEl = document.getElementById("clearSearchBtn");
    const searchScopeSelectEl = document.getElementById("searchScopeSelect");
    const hitCountBadgeEl = document.getElementById("hitCountBadge");
    const prevHitBtnEl = document.getElementById("prevHitBtn");
    const nextHitBtnEl = document.getElementById("nextHitBtn");
    const toggleResultsDrawerBtnEl = document.getElementById("toggleResultsDrawerBtn");
    const drawerBadgeCountEl = document.getElementById("drawerBadgeCount");
    const searchResultsDrawerEl = document.getElementById("searchResultsDrawer");
    const searchResultsListEl = document.getElementById("searchResultsList");
    const resultsSummaryTextEl = document.getElementById("resultsSummaryText");
    const pageFilterChipsEl = document.getElementById("pageFilterChips");
    const closeDrawerBtnEl = document.getElementById("closeDrawerBtn");

    const modeContinuousBtnEl = document.getElementById("modeContinuousBtn");
    const modeSingleBtnEl = document.getElementById("modeSingleBtn");
    const layoutSplitBtnEl = document.getElementById("layoutSplitBtn");
    const layoutWideBtnEl = document.getElementById("layoutWideBtn");
    const layoutFullBtnEl = document.getElementById("layoutFullBtn");
    const quickMaximizeBtnEl = document.getElementById("quickMaximizeBtn");
    const facsimileSizeBadgeEl = document.getElementById("facsimileSizeBadge");
    const facsimilePaneEl = document.getElementById("facsimilePane");
    const textPaneEl = document.getElementById("textPane");
    const textViewModeGroupEl = document.getElementById("textViewModeGroup");

    const toggleTextOverlayEl = document.getElementById("toggleTextOverlay");
    const textOverlayLangSelectEl = document.getElementById("textOverlayLangSelect");

    const pageTabsEl = document.getElementById("pageTabs");
    const activePageIndicatorEl = document.getElementById("activePageIndicator");
    const statusMetaEl = document.getElementById("statusMeta");

    const imageScrollPaneEl = document.getElementById("imageScrollPane");
    const textScrollPaneEl = document.getElementById("textScrollPane");
    const flapControlBarEl = document.getElementById("flapControlBar");
    const flapButtonsEl = document.getElementById("flapButtons");
    const flapStateDescEl = document.getElementById("flapStateDesc");
    const iiifFullLinkEl = document.getElementById("iiifFullLink");

    const cropInspectorTitleEl = document.getElementById("cropInspectorTitle");
    const cropInspectorCoordEl = document.getElementById("cropInspectorCoord");
    const iiifLineCropImgEl = document.getElementById("iiifLineCropImg");
    const iiifLineCropPlaceholderEl = document.getElementById("iiifLineCropPlaceholder");

    // Floating HUD Popover Elements
    const manuscriptHudEl = document.getElementById("manuscriptHud");
    const hudBadgeEl = document.getElementById("hudBadge");
    const hudCoordEl = document.getElementById("hudCoord");
    const hudDeTextEl = document.getElementById("hudDeText");
    const hudEnTextEl = document.getElementById("hudEnText");
    const hudNoteSectionEl = document.getElementById("hudNoteSection");
    const hudNoteTextEl = document.getElementById("hudNoteText");
    const hudCropImgEl = document.getElementById("hudCropImg");
    const hudPinBtnEl = document.getElementById("hudPinBtn");
    const hudCloseBtnEl = document.getElementById("hudCloseBtn");

    function escapeHtml(str) {
      return String(str || "")
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
    }

    function formatDisplayText(raw) {
      let s = escapeHtml(raw);
      s = s.replace(/\\{rubric:\\s*([^}]*)\\}/g, '<span class="rubric-span">$1</span>');
      s = s.replace(/\\{del:\\s*([^}]*)\\}/g, '<del class="opacity-70">$1</del>');
      s = s.replace(/\\{add:\\s*([^}]*)\\}/g, '<ins class="underline decoration-dotted">$1</ins>');
      return s;
    }

    function highlightSnippet(text, query) {
      if (!query) return escapeHtml(text);
      const escapedQuery = query.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&");
      const regex = new RegExp(`(${escapedQuery})`, "gi");
      return escapeHtml(text).replace(regex, '<mark class="bg-amber-300 text-black font-semibold px-0.5 rounded">$1</mark>');
    }

    function buildTeiLb(ln, cUri) {
      const [lid, lnum, ltype, ulx, uly, lrx, lry, de] = ln;
      return `<lb xml:id="${lid}" n="${lnum}" facs="#zone_${lid}" corresp="#en_${lid}"/>` + escapeHtml(de);
    }

    function buildTeiZone(ln, cUri) {
      const [lid, lnum, ltype, ulx, uly, lrx, lry] = ln;
      const xywh = `${ulx},${uly},${lrx - ulx},${lry - uly}`;
      return `<zone xml:id="zone_${lid}" type="${ltype}" ulx="${ulx}" uly="${uly}" lrx="${lrx}" lry="${lry}" corresp="${cUri}#xywh=${xywh}"/>`;
    }

    // -------------------------------------------------------------------------
    // LAYOUT SIZING CONTROLLER (Expandable Facsimile Workspace)
    // -------------------------------------------------------------------------
    function setLayoutMode(mode) {
      currentLayoutMode = mode;
      [layoutSplitBtnEl, layoutWideBtnEl, layoutFullBtnEl].forEach((b) => {
        b.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]";
      });

      if (mode === "split") {
        layoutSplitBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]";
        facsimilePaneEl.style.width = "50%";
        facsimilePaneEl.style.flex = "0 0 50%";
        textPaneEl.style.display = "flex";
        textPaneEl.style.width = "50%";
        textPaneEl.style.flex = "0 0 50%";
        textViewModeGroupEl.classList.remove("hidden");
        facsimileSizeBadgeEl.textContent = "50% Split";
      } else if (mode === "wide") {
        layoutWideBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]";
        facsimilePaneEl.style.width = "75%";
        facsimilePaneEl.style.flex = "0 0 75%";
        textPaneEl.style.display = "flex";
        textPaneEl.style.width = "25%";
        textPaneEl.style.flex = "0 0 25%";
        textViewModeGroupEl.classList.remove("hidden");
        facsimileSizeBadgeEl.textContent = "75% Wide";
      } else if (mode === "full") {
        layoutFullBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]";
        facsimilePaneEl.style.width = "100%";
        facsimilePaneEl.style.flex = "0 0 100%";
        textPaneEl.style.display = "none";
        textViewModeGroupEl.classList.add("hidden");
        facsimileSizeBadgeEl.textContent = "100% Full Page";
      }
    }

    layoutSplitBtnEl.addEventListener("click", () => setLayoutMode("split"));
    layoutWideBtnEl.addEventListener("click", () => setLayoutMode("wide"));
    layoutFullBtnEl.addEventListener("click", () => setLayoutMode("full"));
    quickMaximizeBtnEl.addEventListener("click", () => {
      setLayoutMode(currentLayoutMode === "full" ? "wide" : "full");
    });

    // Top Navigation Tabs
    function renderPageTabs() {
      pageTabsEl.innerHTML = "";
      EDITION_DATA.pages.forEach((p, idx) => {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.id = `tab_p_${idx}`;
        const isActive = (displayMode === "single" && idx === currentSinglePageIdx);
        btn.className = "px-2 py-0.5 rounded text-xs whitespace-nowrap transition-colors " + (
          isActive
            ? "active-page-tab"
            : "bg-[var(--secondary)] text-[var(--secondary-foreground)] hover:opacity-90"
        );
        btn.textContent = `p.${p.orig_page} (c.${p.canvas_num})`;
        btn.addEventListener("click", () => {
          if (displayMode === "single") {
            currentSinglePageIdx = idx;
            renderSinglePageView();
          } else {
            scrollToPage(idx);
          }
          updateActivePageIndicator(idx);
        });
        pageTabsEl.appendChild(btn);
      });
    }

    function updateActivePageIndicator(pageIdx) {
      const p = EDITION_DATA.pages[pageIdx];
      if (!p) return;
      activePageIndicatorEl.textContent = `Page ${p.orig_page} (Canvas ${p.canvas_num})`;
      statusMetaEl.textContent = `Viewing: Page ${p.orig_page} (${p.width}×${p.height}px) · Canvas #${p.canvas_num}`;
      const imgSvc = `https://iiif.wellcomecollection.org/image/${p.jp2}`;
      iiifFullLinkEl.href = `${imgSvc}/full/full/0/default.jpg`;

      // Highlight active tab
      document.querySelectorAll("#pageTabs button").forEach((b, idx) => {
        b.classList.toggle("active-page-tab", idx === pageIdx);
      });
    }

    // Scroll both left and right panes to a specific page
    function scrollToPage(pageIdx) {
      const textCard = document.getElementById(`text_page_${pageIdx}`);
      const imgCard = document.getElementById(`facs_page_${pageIdx}`);
      const targetImg = document.getElementById(`img_page_${pageIdx}`);
      if (targetImg && targetImg.dataset.src && (!targetImg.src || targetImg.src === window.location.href)) {
        targetImg.src = targetImg.dataset.src;
      }
      if (textCard) {
        textCard.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      if (imgCard) {
        imgCard.scrollIntoView({ behavior: "smooth", block: "start" });
      }
      updateActivePageIndicator(pageIdx);
    }

    // -------------------------------------------------------------------------
    // FACSIMILE RENDERING (Continuous and Single Page)
    // -------------------------------------------------------------------------
    function buildFacsimileCard(p, idx, isSingle = false) {
      const card = document.createElement("div");
      card.id = `facs_page_${idx}`;
      card.dataset.pageIdx = idx;
      card.className = "facsimile-page-card bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-sm overflow-hidden";

      // Header Bar on Facsimile Card
      const header = document.createElement("div");
      header.className = "px-3 py-1.5 bg-[var(--secondary)] border-b border-[var(--border)] flex items-center justify-between text-xs page-divider-sticky";
      header.innerHTML = `
        <div class="flex items-center gap-2">
          <span class="font-bold">Page ${escapeHtml(p.orig_page)}</span>
          <span class="text-[var(--muted-foreground)]">Canvas #${p.canvas_num} (${p.width}×${p.height}px)</span>
          <span class="text-xs text-[var(--primary)] font-medium hidden sm:inline">Hover or click any line zone below to reveal text &amp; translation</span>
        </div>
        <div class="flex items-center gap-2 font-mono text-[var(--muted-foreground)]">
          <span>${escapeHtml(p.jp2)}</span>
          <a href="https://iiif.wellcomecollection.org/image/${p.jp2}/full/full/0/default.jpg" target="_blank" rel="noopener" class="hover:text-[var(--primary)]" title="Open full-resolution IIIF image">↗</a>
        </div>
      `;
      card.appendChild(header);

      // Canvas Stage Container
      const stageWrap = document.createElement("div");
      stageWrap.className = "p-2 flex justify-center items-start";

      const stage = document.createElement("div");
      stage.id = `stage_page_${idx}`;
      stage.className = "canvas-stage relative block border border-[var(--border)] shadow transition-all duration-150 mx-auto";
      stage.style.position = "relative";
      stage.style.display = "block";
      stage.style.width = isSingle ? `${currentZoom}%` : "100%";
      stage.style.maxWidth = "100%";
      stage.style.aspectRatio = `${p.width} / ${p.height}`;
      stage.style.backgroundColor = "#f6efe3"; // Warm aged parchment placeholder

      const iiifUrl = `https://iiif.wellcomecollection.org/image/${p.jp2}/full/1000,/0/default.jpg`;
      const localUrl = `canvas_${String(p.canvas_num).padStart(4, "0")}.jpg`;
      const isLocalFile = (window.location.protocol === "file:");
      const primaryUrl = isLocalFile ? localUrl : iiifUrl;
      const fallbackUrl = isLocalFile ? iiifUrl : localUrl;

      const img = document.createElement("img");
      img.id = `img_page_${idx}`;
      img.alt = `Wellcome MS.990 Canvas #${p.canvas_num}`;
      img.dataset.src = iiifUrl;
      img.dataset.localSrc = localUrl;
      img.className = "block w-full h-auto select-none pointer-events-none transition-opacity duration-200";
      img.style.display = "block";
      img.style.width = "100%";
      img.style.height = "auto";
      img.style.position = "relative";
      img.style.zIndex = "1";

      img.onerror = () => {
        if (img.src !== fallbackUrl && !img.src.endsWith(fallbackUrl)) {
          console.warn(`Falling back to ${fallbackUrl} for Canvas #${p.canvas_num}`);
          img.src = fallbackUrl;
        }
      };

      // Load eager for first 4 pages or in single-page mode; others loaded via container-aware IntersectionObserver
      if (isSingle || idx < 4) {
        img.src = primaryUrl;
        img.dataset.loaded = "true";
      } else {
        img.className += " iiif-lazy-img";
      }

      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.id = `svg_page_${idx}`;
      svg.setAttribute("viewBox", `0 0 ${p.width} ${p.height}`);
      svg.setAttribute("preserveAspectRatio", "none");
      // Robust positioning: use setAttribute AND explicit inline styles so it NEVER fails!
      svg.setAttribute("class", "absolute inset-0 w-full h-full pointer-events-auto");
      svg.style.position = "absolute";
      svg.style.top = "0";
      svg.style.left = "0";
      svg.style.width = "100%";
      svg.style.height = "100%";
      svg.style.zIndex = "10";

      renderSvgZones(svg, p, idx);

      stage.appendChild(img);
      stage.appendChild(svg);
      stageWrap.appendChild(stage);
      card.appendChild(stageWrap);

      return card;
    }

    function renderSvgZones(svgEl, p, pIdx) {
      svgEl.innerHTML = "";
      const showRules = document.getElementById("toggleRules").checked;
      const showBoxes = document.getElementById("toggleBoxes").checked;

      // Draw red frame & center divider rule
      if (showRules) {
        const [fx, fy, flrx, flry] = p.frame_box;
        const frameRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
        frameRect.setAttribute("x", fx);
        frameRect.setAttribute("y", fy);
        frameRect.setAttribute("width", flrx - fx);
        frameRect.setAttribute("height", flry - fy);
        frameRect.setAttribute("fill", "none");
        frameRect.setAttribute("stroke", "rgba(220, 38, 38, 0.7)");
        frameRect.setAttribute("stroke-width", "14");
        svgEl.appendChild(frameRect);

        if (p.center_rule_x) {
          const midLine = document.createElementNS("http://www.w3.org/2000/svg", "line");
          midLine.setAttribute("x1", p.center_rule_x);
          midLine.setAttribute("y1", fy);
          midLine.setAttribute("x2", p.center_rule_x);
          midLine.setAttribute("y2", flry);
          midLine.setAttribute("stroke", "rgba(220, 38, 38, 0.7)");
          midLine.setAttribute("stroke-width", "12");
          svgEl.appendChild(midLine);
        }

        (p.figures || []).forEach((fig) => {
          const figRect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
          figRect.setAttribute("x", fig.ulx);
          figRect.setAttribute("y", fig.uly);
          figRect.setAttribute("width", fig.lrx - fig.ulx);
          figRect.setAttribute("height", fig.lry - fig.uly);
          figRect.setAttribute("fill", "rgba(16, 185, 129, 0.08)");
          figRect.setAttribute("stroke", "rgba(16, 185, 129, 0.85)");
          figRect.setAttribute("stroke-width", "14");
          figRect.setAttribute("stroke-dasharray", "36,20");
          const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
          title.textContent = `${fig.label}: ${fig.desc}`;
          figRect.appendChild(title);
          svgEl.appendChild(figRect);
        });
      }

      // Draw Interactive Line Bounding Boxes & Text-on-Page Overlays
      p.columns.forEach((col) => {
        col.lines.forEach((ln) => {
          const [lid, lnum, ltype, ulx, uly, lrx, lry, de, en, note] = ln;
          const isActive = (lid === activeLineId);
          const isHit = isLineInSearchResults(lid);
          const isRubric = (ltype === "rubric" || de.includes("{rubric:") || ltype === "head");

          const w = lrx - ulx;
          const h = lry - uly;

          // Group wrapper for entire segmented line
          const g = document.createElementNS("http://www.w3.org/2000/svg", "g");
          g.setAttribute("id", `svg_group_${lid}`);
          g.setAttribute("class", `svg-line-group cursor-pointer ${isActive ? 'active-group' : ''}`);

          // 1. Text-on-Page Reading Ribbon (if showTextOverlay is enabled)
          if (showTextOverlay) {
            const rawText = (textOverlayLang === "en" ? (en || de) : de);
            const cleanText = rawText.replace(/\\{rubric:\\s*([^}]*)\\}/g, "$1").replace(/\\{del:\\s*([^}]*)\\}/g, "$1").replace(/\\{add:\\s*([^}]*)\\}/g, "$1");

            const textBg = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            textBg.setAttribute("x", ulx + 8);
            textBg.setAttribute("y", uly + 4);
            textBg.setAttribute("width", Math.max(10, w - 16));
            textBg.setAttribute("height", Math.max(10, h - 8));
            textBg.setAttribute("rx", "12");
            textBg.setAttribute("class", isRubric ? "svg-text-bg svg-text-bg-rubric pointer-events-none" : "svg-text-bg pointer-events-none");
            g.appendChild(textBg);

            // Compute ideal font size to fit neatly within line box
            const targetSize = Math.max(26, Math.round(h * 0.56));
            const approxCharWidth = targetSize * 0.50;
            const textLen = cleanText.length;
            const availWidth = Math.max(100, w - 80);
            let fontSize = targetSize;
            if (textLen * approxCharWidth > availWidth && textLen > 0) {
              fontSize = Math.max(20, Math.floor(availWidth / (textLen * 0.50)));
            }

            const textEl = document.createElementNS("http://www.w3.org/2000/svg", "text");
            textEl.setAttribute("x", ulx + 35);
            textEl.setAttribute("y", uly + Math.round(h * 0.70));
            textEl.setAttribute("font-size", `${fontSize}px`);
            textEl.setAttribute("class", isRubric 
              ? "svg-text-label svg-text-label-rubric pointer-events-none select-none" 
              : (textOverlayLang === "en" ? "svg-text-label pointer-events-none select-none" : "svg-text-label svg-text-label-de pointer-events-none select-none"));
            textEl.textContent = cleanText;
            g.appendChild(textEl);
          }

          // 2. Interactive Line Bounding Box Overlay
          if (showBoxes || isActive || isHit) {
            const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
            rect.setAttribute("id", `svg_box_${lid}`);
            rect.setAttribute("x", ulx);
            rect.setAttribute("y", uly);
            rect.setAttribute("width", w);
            rect.setAttribute("height", h);
            rect.setAttribute("rx", "12");

            let cls = isRubric ? "svg-zone-rubric" : "svg-zone-line";
            if (isActive) cls += " active-box";
            if (isHit) cls += " search-hit-box";
            rect.setAttribute("class", cls);

            const title = document.createElementNS("http://www.w3.org/2000/svg", "title");
            title.textContent = `[${lid}] ${de} — ${en}`;
            rect.appendChild(title);

            g.appendChild(rect);
          }

          // Interactive Events: Hover opens/updates HUD popover, Click pins HUD and activates line
          g.addEventListener("mouseenter", (ev) => {
            updateCropInspector(p, ln);
            if (!isHudPinned) {
              showManuscriptHud(p, ln, g, ev);
            }
          });

          g.addEventListener("mouseleave", () => {
            if (!isHudPinned) {
              hideManuscriptHud();
            }
          });

          g.addEventListener("click", (ev) => {
            ev.stopPropagation();
            selectLine(p, ln, true, false, pIdx);
            showManuscriptHud(p, ln, g, ev, true);
          });

          svgEl.appendChild(g);
        });
      });
    }

    function isLineInSearchResults(lid) {
      return globalSearchResults.some((r) => r.lineId === lid);
    }

    // -------------------------------------------------------------------------
    // FLOATING MANUSCRIPT HUD POPOVER CONTROLLER
    // (User Request: "highlight an area and it tells me what it says")
    // -------------------------------------------------------------------------
    function showManuscriptHud(page, ln, targetEl, mouseEvent, forcePin = false) {
      const [lid, lnum, ltype, ulx, uly, lrx, lry, de, en, note] = ln;
      hudTargetLid = lid;

      hudBadgeEl.textContent = `Page ${page.orig_page} · Canvas #${page.canvas_num} · Line ${lnum}`;
      const xywh = `${ulx},${uly},${lrx - ulx},${lry - uly}`;
      hudCoordEl.textContent = `#xywh=${xywh}`;

      hudDeTextEl.innerHTML = formatDisplayText(de);
      hudEnTextEl.innerHTML = formatDisplayText(en);

      if (note) {
        hudNoteSectionEl.classList.remove("hidden");
        hudNoteTextEl.textContent = note;
      } else {
        hudNoteSectionEl.classList.add("hidden");
      }

      const cropUrl = `https://iiif.wellcomecollection.org/image/${page.jp2}/${xywh}/800,/0/default.jpg`;
      hudCropImgEl.src = cropUrl;

      // Position Popover dynamically inside the facsimile pane near the line
      const paneRect = facsimilePaneEl.getBoundingClientRect();
      const targetRect = targetEl.getBoundingClientRect();

      let top = (targetRect.top - paneRect.top) + (targetRect.height / 2) - 80;
      let left = (targetRect.left - paneRect.left) + 40;

      // Position to the left or right of column depending on which side of pane line is on
      if ((targetRect.left - paneRect.left) > (paneRect.width * 0.52)) {
        left = Math.max(20, (targetRect.left - paneRect.left) - 490);
      } else {
        left = Math.max(20, Math.min(paneRect.width - 490, (targetRect.right - paneRect.left) + 20));
      }

      top = Math.max(20, Math.min(paneRect.height - 330, top));

      manuscriptHudEl.style.top = `${top}px`;
      manuscriptHudEl.style.left = `${left}px`;
      manuscriptHudEl.classList.remove("hidden");

      if (forcePin) {
        isHudPinned = true;
        hudPinBtnEl.textContent = "📌 Pinned (Click to unlock)";
        hudPinBtnEl.classList.add("bg-[var(--primary)]", "text-[var(--primary-foreground)]");
      }
    }

    function hideManuscriptHud() {
      if (!isHudPinned) {
        manuscriptHudEl.classList.add("hidden");
        hudTargetLid = null;
      }
    }

    hudCloseBtnEl.addEventListener("click", () => {
      isHudPinned = false;
      hudPinBtnEl.textContent = "📌 Pin";
      hudPinBtnEl.classList.remove("bg-[var(--primary)]", "text-[var(--primary-foreground)]");
      manuscriptHudEl.classList.add("hidden");
    });

    hudPinBtnEl.addEventListener("click", () => {
      isHudPinned = !isHudPinned;
      if (isHudPinned) {
        hudPinBtnEl.textContent = "📌 Pinned (Click to unlock)";
        hudPinBtnEl.classList.add("bg-[var(--primary)]", "text-[var(--primary-foreground)]");
      } else {
        hudPinBtnEl.textContent = "📌 Pin";
        hudPinBtnEl.classList.remove("bg-[var(--primary)]", "text-[var(--primary-foreground)]");
      }
    });

    // In-place instant SVG overlay refresh (preserves scroll position & avoids image reload)
    function refreshSvgOverlays() {
      if (displayMode === "continuous") {
        EDITION_DATA.pages.forEach((p, idx) => {
          const svg = document.getElementById(`svg_page_${idx}`);
          if (svg) renderSvgZones(svg, p, idx);
        });
      } else {
        const p = EDITION_DATA.pages[currentSinglePageIdx];
        const svg = document.getElementById(`svg_page_${currentSinglePageIdx}`);
        if (svg && p) renderSvgZones(svg, p, currentSinglePageIdx);
      }
    }

    // Toggle Text on Page mode
    toggleTextOverlayEl.addEventListener("change", () => {
      showTextOverlay = toggleTextOverlayEl.checked;
      refreshSvgOverlays();
    });

    textOverlayLangSelectEl.addEventListener("change", (e) => {
      textOverlayLang = e.target.value;
      if (showTextOverlay) {
        refreshSvgOverlays();
      }
    });

    // -------------------------------------------------------------------------
    // TEXT RENDERING (Right Docked Pane)
    // -------------------------------------------------------------------------
    function buildTextPageCard(p, idx) {
      const card = document.createElement("div");
      card.id = `text_page_${idx}`;
      card.dataset.pageIdx = idx;
      card.className = "text-page-card bg-[var(--card)] border border-[var(--border)] rounded-lg shadow-sm overflow-hidden space-y-4 p-4";

      // Sticky Page Header & Summary Banner
      const header = document.createElement("div");
      header.className = "p-3 bg-[var(--secondary)] border border-[var(--border)] rounded-md space-y-1.5 page-divider-sticky";
      header.innerHTML = `
        <div class="flex flex-wrap items-baseline justify-between gap-2">
          <div class="flex items-center gap-2">
            <span class="px-2 py-0.5 rounded bg-[var(--primary)] text-[var(--primary-foreground)] text-xs font-bold">
              Page ${escapeHtml(p.orig_page)}
            </span>
            <span class="text-xs font-bold">Wellcome MS.990 · Canvas #${p.canvas_num}</span>
          </div>
          <span class="text-xs font-mono text-[var(--muted-foreground)]">Folio ${escapeHtml(p.folio_side)} · ${p.width}×${p.height}px</span>
        </div>
        <p class="text-xs text-[var(--muted-foreground)] leading-relaxed searchable-text">${escapeHtml(p.summary)}</p>
      `;
      card.appendChild(header);

      // Embedded Figures Banner if present
      if (p.figures && p.figures.length > 0) {
        const figCard = document.createElement("div");
        figCard.className = "bg-[var(--background)] border border-[var(--border)] rounded p-2.5 space-y-1 text-xs";
        let fhtml = `<div class="font-bold text-[var(--muted-foreground)] uppercase tracking-wide">Illustrations / Drawings on Canvas #${p.canvas_num}</div>`;
        p.figures.forEach((fig) => {
          const fw = fig.lrx - fig.ulx;
          const fh = fig.lry - fig.uly;
          fhtml += `
            <div class="pt-1 border-t border-[var(--border)]">
              <div class="flex items-baseline justify-between gap-2">
                <span class="font-semibold text-emerald-600 dark:text-emerald-400">${escapeHtml(fig.label)}</span>
                <span class="font-mono text-[var(--muted-foreground)]">#xywh=${fig.ulx},${fig.uly},${fw},${fh}</span>
              </div>
              <p class="text-[var(--muted-foreground)] mt-0.5">${escapeHtml(fig.desc)}</p>
            </div>`;
        });
        figCard.innerHTML = fhtml;
        card.appendChild(figCard);
      }

      // Columns and Lines
      const cUri = `https://iiif.wellcomecollection.org/presentation/b18775275/canvases/${p.jp2}`;
      p.columns.forEach((col) => {
        const colWrap = document.createElement("div");
        colWrap.className = "border border-[var(--border)] rounded-md overflow-hidden bg-[var(--background)]";
        const cw = col.lrx - col.ulx;
        const ch = col.lry - col.uly;

        const colHeader = document.createElement("div");
        colHeader.className = "px-3 py-1.5 bg-[var(--secondary)] border-b border-[var(--border)] flex flex-wrap items-center justify-between gap-2 text-xs";
        colHeader.innerHTML = `
          <span class="font-bold">${escapeHtml(col.col_label)}</span>
          <span class="font-mono text-[var(--muted-foreground)]">Zone #xywh=${col.ulx},${col.uly},${cw},${ch} (${col.lines.length} lines)</span>
        `;
        colWrap.appendChild(colHeader);

        const list = document.createElement("div");
        list.className = "divide-y divide-[var(--border)]";

        col.lines.forEach((ln) => {
          const [lid, lnum, ltype, ulx, uly, lrx, lry, de, en, note] = ln;
          const xywh = `${ulx},${uly},${lrx - ulx},${lry - uly}`;
          const row = document.createElement("div");
          row.id = `row_${lid}`;
          row.dataset.lineId = lid;
          row.dataset.pageIdx = idx;
          row.className = "line-row-item px-3 py-1.5 hover:bg-[var(--accent)] transition-colors cursor-pointer text-xs " + (lid === activeLineId ? "line-row-active" : "");

          if (currentViewMode === "parallel") {
            row.innerHTML = `
              <div class="grid grid-cols-1 md:grid-cols-12 gap-2 items-baseline">
                <div class="md:col-span-2 flex items-center gap-1.5 font-mono text-[var(--muted-foreground)]">
                  <span class="px-1.5 py-0.5 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] font-semibold">${escapeHtml(lnum)}</span>
                  <span title="#xywh=${xywh}" class="truncate">${escapeHtml(lid)}</span>
                </div>
                <div class="md:col-span-5 font-mono leading-relaxed searchable-text">${formatDisplayText(de)}</div>
                <div class="md:col-span-5 leading-relaxed searchable-text">
                  ${formatDisplayText(en)}
                  ${note ? `<div class="mt-0.5 text-xs italic text-[var(--muted-foreground)] searchable-text">Note: ${escapeHtml(note)}</div>` : ""}
                </div>
              </div>
            `;
          } else if (currentViewMode === "diplomatic") {
            row.innerHTML = `
              <div class="flex items-baseline gap-3">
                <span class="w-28 shrink-0 font-mono text-[var(--muted-foreground)]">[${escapeHtml(lid)}]</span>
                <span class="w-36 shrink-0 font-mono text-[var(--muted-foreground)]">#xywh=${xywh}</span>
                <div class="font-mono leading-relaxed searchable-text">${formatDisplayText(de)}</div>
              </div>
            `;
          } else if (currentViewMode === "translation") {
            row.innerHTML = `
              <div class="flex items-baseline gap-3">
                <span class="w-28 shrink-0 font-mono text-[var(--muted-foreground)]">[${escapeHtml(lid)}]</span>
                <div class="leading-relaxed searchable-text">
                  ${formatDisplayText(en)}
                  ${note ? `<span class="ml-2 italic text-[var(--muted-foreground)]">// ${escapeHtml(note)}</span>` : ""}
                </div>
              </div>
            `;
          } else if (currentViewMode === "tei") {
            row.innerHTML = `
              <div class="space-y-1 font-mono">
                <div class="text-[var(--muted-foreground)]">${escapeHtml(buildTeiZone(ln, cUri))}</div>
                <div class="searchable-text">${escapeHtml(buildTeiLb(ln, cUri))}</div>
              </div>
            `;
          }

          row.addEventListener("mouseenter", () => updateCropInspector(p, ln));
          row.addEventListener("click", () => selectLine(p, ln, false, true, idx));
          list.appendChild(row);
        });

        colWrap.appendChild(list);
        card.appendChild(colWrap);
      });

      return card;
    }

    // Render Glyphs Lexicon View
    function renderGlyphsView() {
      textScrollPaneEl.innerHTML = "";
      const card = document.createElement("div");
      card.className = "bg-[var(--card)] border border-[var(--border)] rounded-lg p-4 space-y-4";
      let html = `
        <div class="border-b border-[var(--border)] pb-3">
          <h2 class="text-base font-bold">Alchemical, Planetary &amp; Apothecary Symbol Lexicon (TEI &lt;charDecl&gt;)</h2>
          <p class="text-xs text-[var(--muted-foreground)] mt-1">23 historical scribal glyphs and apothecary weight measures transcribed throughout MS.990.</p>
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">`;

      EDITION_DATA.glyphs.forEach((g) => {
        html += `
          <div class="p-3 rounded-lg border border-[var(--border)] bg-[var(--background)] flex items-start gap-3 hover:border-[var(--primary)] transition-colors cursor-pointer" onclick="quickFilterGlyph('${escapeHtml(g.glyph)}')">
            <span class="text-2xl font-mono px-3 py-1.5 rounded bg-[var(--secondary)] text-[var(--secondary-foreground)] shadow-sm">${escapeHtml(g.glyph)}</span>
            <div class="text-xs space-y-0.5">
              <div class="font-bold text-sm">${escapeHtml(g.latin)} <span class="font-mono text-xs text-[var(--muted-foreground)] font-normal">(${escapeHtml(g.unicode)})</span></div>
              <div class="text-[var(--muted-foreground)]">${escapeHtml(g.meaning)}</div>
              <div class="text-[10px] text-[var(--primary)] mt-1">Click to search occurrences across edition ↗</div>
            </div>
          </div>`;
      });
      html += `</div>`;
      card.innerHTML = html;
      textScrollPaneEl.appendChild(card);
    }

    function quickFilterGlyph(glyph) {
      searchInputEl.value = glyph;
      executeGlobalSearch(glyph);
    }

    // -------------------------------------------------------------------------
    // VIEW CONTROLLERS (Continuous Scroll vs Single Page)
    // -------------------------------------------------------------------------
    function renderContinuousView() {
      imageScrollPaneEl.innerHTML = "";
      textScrollPaneEl.innerHTML = "";
      flapControlBarEl.classList.add("hidden");

      if (currentViewMode === "glyphs") {
        renderGlyphsView();
        return;
      }

      EDITION_DATA.pages.forEach((p, idx) => {
        const facsCard = buildFacsimileCard(p, idx, false);
        imageScrollPaneEl.appendChild(facsCard);

        const textCard = buildTextPageCard(p, idx);
        textScrollPaneEl.appendChild(textCard);
      });

      setupScrollSpy();
      setupImageObserver();
      applySearchHighlightingToDom();
    }

    function renderSinglePageView() {
      imageScrollPaneEl.innerHTML = "";
      textScrollPaneEl.innerHTML = "";

      if (currentViewMode === "glyphs") {
        renderGlyphsView();
        return;
      }

      const p = EDITION_DATA.pages[currentSinglePageIdx];
      updateActivePageIndicator(currentSinglePageIdx);

      // Flap controls if Page 48
      if (p.flap_canvases && p.flap_canvases.length > 0) {
        flapControlBarEl.classList.remove("hidden");
        flapButtonsEl.innerHTML = "";
        p.flap_canvases.forEach((fc) => {
          const b = document.createElement("button");
          b.type = "button";
          const isCurrent = fc.jp2 === p.jp2;
          b.className = "px-2.5 py-1 rounded text-xs font-medium " + (
            isCurrent
              ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
              : "bg-[var(--card)] text-[var(--foreground)] border border-[var(--border)]"
          );
          b.textContent = `State ${fc.state} (c.${fc.canvas_num})`;
          b.addEventListener("click", () => {
            flapStateDescEl.textContent = fc.label;
            const singleImg = document.getElementById(`img_page_${currentSinglePageIdx}`);
            if (singleImg) singleImg.src = `https://iiif.wellcomecollection.org/image/${fc.jp2}/full/1000,/0/default.jpg`;
          });
          flapButtonsEl.appendChild(b);
          if (isCurrent) {
            flapStateDescEl.textContent = fc.label;
          }
        });
      } else {
        flapControlBarEl.classList.add("hidden");
      }

      const facsCard = buildFacsimileCard(p, currentSinglePageIdx, true);
      imageScrollPaneEl.appendChild(facsCard);

      const textCard = buildTextPageCard(p, currentSinglePageIdx);
      textScrollPaneEl.appendChild(textCard);

      applySearchHighlightingToDom();
    }

    // Scroll-Spy to automatically detect current page as user scrolls through facsimile pane
    let scrollSpyObserver = null;
    function setupScrollSpy() {
      if (scrollSpyObserver) scrollSpyObserver.disconnect();
      if (displayMode !== "continuous") return;

      const options = {
        root: imageScrollPaneEl,
        threshold: 0.20,
      };

      scrollSpyObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const pageIdx = parseInt(entry.target.dataset.pageIdx, 10);
            updateActivePageIndicator(pageIdx);
          }
        });
      }, options);

      document.querySelectorAll(".facsimile-page-card").forEach((el) => {
        scrollSpyObserver.observe(el);
      });
    }

    // Container-aware IntersectionObserver for IIIF Facsimile Images in Continuous Scroll Pane
    let imageObserver = null;
    function setupImageObserver() {
      if (imageObserver) imageObserver.disconnect();
      if (displayMode !== "continuous") return;

      imageObserver = new IntersectionObserver((entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const img = entry.target;
            const src = img.dataset.src;
            const localSrc = img.dataset.localSrc;
            if (img.dataset.loaded !== "true") {
              img.dataset.loaded = "true";
              const isLocalFile = (window.location.protocol === "file:");
              img.src = isLocalFile ? (localSrc || src) : src;
            }
            obs.unobserve(img);
          }
        });
      }, {
        root: imageScrollPaneEl,
        rootMargin: "800px 0px 800px 0px"
      });

      document.querySelectorAll(".iiif-lazy-img").forEach((img) => {
        imageObserver.observe(img);
      });
    }

    // -------------------------------------------------------------------------
    // LINE SELECTION & CROP INSPECTOR
    // -------------------------------------------------------------------------
    function updateCropInspector(page, ln) {
      const [lid, lnum, ltype, ulx, uly, lrx, lry, de] = ln;
      const xywh = `${ulx},${uly},${lrx - ulx},${lry - uly}`;
      const cropUrl = `https://iiif.wellcomecollection.org/image/${page.jp2}/${xywh}/800,/0/default.jpg`;
      cropInspectorTitleEl.textContent = `[${lid}] ${de.replace(/\\{rubric:\\s*([^}]*)\\}/g, "$1")}`;
      cropInspectorCoordEl.textContent = `#xywh=${xywh}`;
      iiifLineCropImgEl.src = cropUrl;
      iiifLineCropImgEl.classList.remove("hidden");
      iiifLineCropPlaceholderEl.classList.add("hidden");
    }

    function selectLine(page, ln, scrollText = false, scrollImage = false, pageIdx = null) {
      const [lid, lnum, ltype, ulx, uly, lrx, lry] = ln;
      activeLineId = lid;
      updateCropInspector(page, ln);

      document.querySelectorAll(".line-row-item").forEach((el) => {
        el.classList.toggle("line-row-active", el.dataset.lineId === lid);
      });
      document.querySelectorAll(".svg-zone-line, .svg-zone-rubric").forEach((el) => {
        el.classList.toggle("active-box", el.id === `svg_box_${lid}`);
      });
      document.querySelectorAll(".svg-line-group").forEach((el) => {
        el.classList.toggle("active-group", el.id === `svg_group_${lid}`);
      });

      if (displayMode === "single" && pageIdx !== null && pageIdx !== currentSinglePageIdx) {
        currentSinglePageIdx = pageIdx;
        renderSinglePageView();
      } else if (displayMode === "continuous" && pageIdx !== null) {
        const targetImg = document.getElementById(`img_page_${pageIdx}`);
        if (targetImg && targetImg.dataset.src && (!targetImg.src || targetImg.src === window.location.href)) {
          targetImg.src = targetImg.dataset.src;
        }
      }

      if (scrollText) {
        const rowEl = document.getElementById(`row_${lid}`);
        if (rowEl) rowEl.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      if (scrollImage) {
        const svgBox = document.getElementById(`svg_box_${lid}`);
        if (svgBox) svgBox.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    // -------------------------------------------------------------------------
    // GLOBAL CORPUS SEARCH ENGINE ACROSS ALL PAGES
    // -------------------------------------------------------------------------
    function executeGlobalSearch(query) {
      currentSearchQuery = query.trim();
      clearSearchBtnEl.classList.toggle("hidden", !currentSearchQuery);

      if (!currentSearchQuery) {
        globalSearchResults = [];
        currentResultCursor = -1;
        hitCountBadgeEl.textContent = "0 matches";
        drawerBadgeCountEl.classList.add("hidden");
        searchResultsDrawerEl.classList.add("hidden");
        applySearchHighlightingToDom();
        return;
      }

      const q = currentSearchQuery.toLowerCase();
      const results = [];

      EDITION_DATA.pages.forEach((p, pIdx) => {
        p.columns.forEach((col) => {
          col.lines.forEach((ln) => {
            const [lid, lnum, ltype, ulx, uly, lrx, lry, de, en, note] = ln;
            let matched = false;
            let matchField = "";

            if (searchScope === "all") {
              if (de.toLowerCase().includes(q)) { matched = true; matchField = "de"; }
              else if (en.toLowerCase().includes(q)) { matched = true; matchField = "en"; }
              else if (note && note.toLowerCase().includes(q)) { matched = true; matchField = "note"; }
              else if (lid.toLowerCase().includes(q)) { matched = true; matchField = "id"; }
            } else if (searchScope === "de" && de.toLowerCase().includes(q)) {
              matched = true; matchField = "de";
            } else if (searchScope === "en" && en.toLowerCase().includes(q)) {
              matched = true; matchField = "en";
            } else if (searchScope === "notes" && note && note.toLowerCase().includes(q)) {
              matched = true; matchField = "note";
            }

            if (matched) {
              results.push({
                pageIdx: pIdx,
                page: p,
                col: col,
                line: ln,
                lineId: lid,
                matchField: matchField,
                de: de,
                en: en,
                note: note || "",
              });
            }
          });
        });
      });

      globalSearchResults = results;
      currentResultCursor = results.length > 0 ? 0 : -1;

      // Update Top Badge
      const distinctPages = new Set(results.map((r) => r.pageIdx)).size;
      hitCountBadgeEl.textContent = results.length === 1
        ? "1 match"
        : `${results.length} matches in ${distinctPages} p.`;

      drawerBadgeCountEl.textContent = results.length;
      drawerBadgeCountEl.classList.toggle("hidden", results.length === 0);

      renderSearchResultsDrawer();
      applySearchHighlightingToDom();

      if (results.length > 0) {
        jumpToResult(0);
      }
    }

    function renderSearchResultsDrawer() {
      if (globalSearchResults.length === 0) {
        searchResultsDrawerEl.classList.add("hidden");
        return;
      }

      searchResultsDrawerEl.classList.remove("hidden");
      const distinctPages = new Set(globalSearchResults.map((r) => r.pageIdx)).size;
      resultsSummaryTextEl.textContent = `${globalSearchResults.length} hits across ${distinctPages} pages for "${currentSearchQuery}"`;

      // Page Filter Chips
      pageFilterChipsEl.innerHTML = "";
      const allChip = document.createElement("button");
      allChip.type = "button";
      allChip.className = "px-2 py-0.5 rounded text-xs font-semibold whitespace-nowrap " + (
        activePageFilter === null
          ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
          : "bg-[var(--card)] border border-[var(--border)]"
      );
      allChip.textContent = `All (${globalSearchResults.length})`;
      allChip.addEventListener("click", () => {
        activePageFilter = null;
        renderSearchResultsDrawer();
      });
      pageFilterChipsEl.appendChild(allChip);

      // Group by page
      const pageCounts = {};
      globalSearchResults.forEach((r) => {
        pageCounts[r.pageIdx] = (pageCounts[r.pageIdx] || 0) + 1;
      });

      Object.keys(pageCounts).forEach((pIdxStr) => {
        const pIdx = parseInt(pIdxStr, 10);
        const p = EDITION_DATA.pages[pIdx];
        const btn = document.createElement("button");
        btn.type = "button";
        const isActive = activePageFilter === pIdx;
        btn.className = "px-2 py-0.5 rounded text-xs whitespace-nowrap " + (
          isActive
            ? "bg-[var(--primary)] text-[var(--primary-foreground)] font-semibold"
            : "bg-[var(--card)] border border-[var(--border)] text-[var(--foreground)]"
        );
        btn.textContent = `p. ${p.orig_page} (${pageCounts[pIdx]})`;
        btn.addEventListener("click", () => {
          activePageFilter = pIdx;
          renderSearchResultsDrawer();
          const firstMatchInPage = globalSearchResults.findIndex((r) => r.pageIdx === pIdx);
          if (firstMatchInPage !== -1) jumpToResult(firstMatchInPage);
        });
        pageFilterChipsEl.appendChild(btn);
      });

      // Filtered Snippet List
      searchResultsListEl.innerHTML = "";
      const filtered = activePageFilter === null
        ? globalSearchResults
        : globalSearchResults.filter((r) => r.pageIdx === activePageFilter);

      filtered.forEach((res) => {
        const globalIdx = globalSearchResults.indexOf(res);
        const isCurrent = globalIdx === currentResultCursor;
        const item = document.createElement("div");
        item.className = "p-2 rounded hover:bg-[var(--accent)] transition-colors cursor-pointer text-xs " + (isCurrent ? "bg-[var(--secondary)] ring-2 ring-[var(--primary)]" : "");

        const deClean = res.de.replace(/\\{rubric:\\s*([^}]*)\\}/g, "$1");
        const enClean = res.en;

        item.innerHTML = `
          <div class="flex items-baseline justify-between gap-2 mb-1">
            <div class="flex items-center gap-1.5 font-bold">
              <span class="px-1.5 py-0.2 rounded bg-[var(--primary)] text-[var(--primary-foreground)] text-[10px]">p. ${escapeHtml(res.page.orig_page)}</span>
              <span>Canvas #${res.page.canvas_num} · Line ${res.line[1]}</span>
              <span class="font-mono text-[10px] text-[var(--muted-foreground)]">[${res.lineId}]</span>
            </div>
            <span class="text-[10px] text-[var(--primary)] font-semibold">Jump to line ↗</span>
          </div>
          <div class="font-mono text-xs leading-relaxed text-[var(--foreground)]">
            ${highlightSnippet(deClean, currentSearchQuery)}
          </div>
          <div class="text-xs leading-relaxed text-[var(--muted-foreground)] mt-0.5">
            ${highlightSnippet(enClean, currentSearchQuery)}
          </div>
          ${res.note ? `<div class="text-[10px] italic text-[var(--muted-foreground)] mt-0.5">Note: ${highlightSnippet(res.note, currentSearchQuery)}</div>` : ""}
        `;

        item.addEventListener("click", () => {
          jumpToResult(globalIdx);
        });

        searchResultsListEl.appendChild(item);
      });
    }

    function jumpToResult(targetIdx) {
      if (globalSearchResults.length === 0) return;
      currentResultCursor = (targetIdx + globalSearchResults.length) % globalSearchResults.length;
      const res = globalSearchResults[currentResultCursor];

      // Update badge with position
      hitCountBadgeEl.textContent = `${currentResultCursor + 1} of ${globalSearchResults.length} (p. ${res.page.orig_page})`;

      if (displayMode === "single") {
        if (currentSinglePageIdx !== res.pageIdx) {
          currentSinglePageIdx = res.pageIdx;
          renderSinglePageView();
        }
      }

      selectLine(res.page, res.line, true, true, res.pageIdx);
      renderSearchResultsDrawer();
    }

    function applySearchHighlightingToDom() {
      const q = currentSearchQuery.trim();

      // CSS Custom Highlight API with <mark> fallback
      if (!CSS.highlights) {
        textScrollPaneEl.querySelectorAll(".searchable-text").forEach((el) => {
          if (!el.dataset.origHtml) el.dataset.origHtml = el.innerHTML;
          if (!q) {
            el.innerHTML = el.dataset.origHtml;
            return;
          }
          const escaped = q.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&");
          const regex = new RegExp(`(${escaped})`, "gi");
          el.innerHTML = el.dataset.origHtml.replace(regex, "<mark class='bg-amber-300 text-black font-semibold px-0.5 rounded'>$1</mark>");
        });
      } else {
        CSS.highlights.clear();
        if (q) {
          const ranges = [];
          const walker = document.createTreeWalker(textScrollPaneEl, NodeFilter.SHOW_TEXT);
          const lowerQuery = q.toLowerCase();

          while (walker.nextNode()) {
            const node = walker.currentNode;
            const text = node.textContent.toLowerCase();
            let start = 0;

            while ((start = text.indexOf(lowerQuery, start)) !== -1) {
              const range = new Range();
              range.setStart(node, start);
              range.setEnd(node, start + q.length);
              ranges.push(range);
              start += q.length;
            }
          }
          const searchHighlight = new Highlight(...ranges);
          CSS.highlights.set("search-results", searchHighlight);
        }
      }

      // Highlight SVG bounding boxes across all rendered canvases
      document.querySelectorAll(".svg-zone-line, .svg-zone-rubric").forEach((el) => {
        const lid = el.id.replace("svg_box_", "");
        el.classList.toggle("search-hit-box", isLineInSearchResults(lid));
      });
    }

    // -------------------------------------------------------------------------
    // EVENT LISTENERS & INITIALIZATION
    // -------------------------------------------------------------------------
    let searchDebounceTimer = null;
    searchInputEl.addEventListener("input", (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        executeGlobalSearch(e.target.value);
      }, 150);
    });

    searchInputEl.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        if (e.shiftKey) {
          jumpToResult(currentResultCursor - 1);
        } else {
          jumpToResult(currentResultCursor + 1);
        }
      } else if (e.key === "Escape") {
        searchInputEl.value = "";
        executeGlobalSearch("");
      }
    });

    searchScopeSelectEl.addEventListener("change", (e) => {
      searchScope = e.target.value;
      executeGlobalSearch(searchInputEl.value);
    });

    clearSearchBtnEl.addEventListener("click", () => {
      searchInputEl.value = "";
      executeGlobalSearch("");
    });

    prevHitBtnEl.addEventListener("click", () => jumpToResult(currentResultCursor - 1));
    nextHitBtnEl.addEventListener("click", () => jumpToResult(currentResultCursor + 1));

    toggleResultsDrawerBtnEl.addEventListener("click", () => {
      searchResultsDrawerEl.classList.toggle("hidden");
    });
    closeDrawerBtnEl.addEventListener("click", () => {
      searchResultsDrawerEl.classList.add("hidden");
    });

    // Quick Search Chips
    document.querySelectorAll(".chip-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        const term = btn.dataset.chip;
        searchInputEl.value = term;
        executeGlobalSearch(term);
      });
    });

    // View Mode Toggle (Continuous Scroll vs Single Page Focus)
    modeContinuousBtnEl.addEventListener("click", () => {
      displayMode = "continuous";
      modeContinuousBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]";
      modeSingleBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]";
      renderContinuousView();
      renderPageTabs();
    });

    modeSingleBtnEl.addEventListener("click", () => {
      displayMode = "single";
      modeSingleBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors bg-[var(--primary)] text-[var(--primary-foreground)]";
      modeContinuousBtnEl.className = "px-2.5 py-1 text-xs font-medium rounded transition-colors text-[var(--muted-foreground)] hover:text-[var(--foreground)]";
      renderSinglePageView();
      renderPageTabs();
    });

    // Text View Buttons (Parallel, Diplomatic, Translation, TEI, Glyphs)
    document.querySelectorAll(".view-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        currentViewMode = btn.dataset.view;
        document.querySelectorAll(".view-btn").forEach((b) => {
          const active = b.dataset.view === currentViewMode;
          b.className = "view-btn px-2 py-0.5 rounded text-xs font-medium " + (
            active
              ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
              : "bg-[var(--secondary)] text-[var(--secondary-foreground)]"
          );
        });

        if (displayMode === "continuous") {
          renderContinuousView();
        } else {
          renderSinglePageView();
        }
      });
    });

    // Zoom Buttons
    document.querySelectorAll(".zoom-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        currentZoom = parseInt(btn.dataset.zoom, 10);
        document.querySelectorAll(".canvas-stage").forEach((s) => {
          s.style.width = `${currentZoom}%`;
        });
        document.querySelectorAll(".zoom-btn").forEach((b) => {
          const active = parseInt(b.dataset.zoom, 10) === currentZoom;
          b.className = "zoom-btn px-2 py-0.5 rounded text-xs font-medium " + (
            active
              ? "bg-[var(--primary)] text-[var(--primary-foreground)]"
              : "bg-[var(--secondary)] text-[var(--secondary-foreground)]"
          );
        });
      });
    });

    // Overlay Toggles (fast in-place refresh preserving scroll & image cache)
    document.getElementById("toggleBoxes").addEventListener("change", refreshSvgOverlays);
    document.getElementById("toggleRules").addEventListener("change", refreshSvgOverlays);

    // Keyboard Shortcuts
    window.addEventListener("keydown", (e) => {
      if ((e.metaKey || e.ctrlKey) && e.key === "f") {
        e.preventDefault();
        searchInputEl.focus();
        searchInputEl.select();
      }
    });

    // Close HUD when clicking outside
    document.addEventListener("click", (e) => {
      if (!isHudPinned && !manuscriptHudEl.contains(e.target) && !e.target.closest(".svg-zone-line, .svg-zone-rubric, .svg-line-group")) {
        manuscriptHudEl.classList.add("hidden");
      }
    });

    // Initialize Explorer with 75% Wide Facsimile layout by default!
    setLayoutMode("wide");
    renderPageTabs();
    renderContinuousView();
    updateActivePageIndicator(0);
  </script>
</body>
</html>
"""


def main():
    payload = build_compact_payload()
    payload_str = json.dumps(payload, ensure_ascii=False)
    html_out = HTML_TEMPLATE.replace("__EDITION_JSON_PAYLOAD__", payload_str)

    ws_out = WORKSPACE_DIR / "ms990_explorer.html"
    art_out = ARTIFACT_DIR / "ms990_explorer.html"

    ws_out.write_text(html_out, encoding="utf-8")
    art_out.write_text(html_out, encoding="utf-8")
    print(f"Wrote {ws_out} ({len(html_out)} bytes)")
    print(f"Wrote {art_out} ({len(html_out)} bytes)")


if __name__ == "__main__":
    main()

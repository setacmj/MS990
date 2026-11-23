#!/usr/bin/env python3
"""
Builds:
1. MS990_parallel_edition_with_facsimiles.md
   Scholarly Markdown parallel edition with embedded high-resolution facsimile images
   for every canvas, followed by diplomatic transcription and modern English translation.
2. MS990_parallel_edition_with_facsimiles.html
   Interactive, responsive parallel edition viewer featuring side-by-side manuscript facsimile,
   zoomable image inspection, synchronized parallel translation tables, page navigation,
   and instant search across all 132 transcribed pages.
"""
import json
import re
import html
from pathlib import Path

WORKSPACE_DIR = Path(__file__).resolve().parent
DATA_FILE = WORKSPACE_DIR / "MS990_edition_data.json"
MD_OUT_FILE = WORKSPACE_DIR / "MS990_parallel_edition_with_facsimiles.md"
HTML_OUT_FILE = WORKSPACE_DIR / "MS990_parallel_edition_with_facsimiles.html"


def format_md_text(raw: str) -> str:
    if not raw:
        return ""
    s = raw.replace("|", "\\|")
    s = re.sub(r"\{rubric:\s*([^}]*)\}", r"**[Rubric] \1**", s)
    s = re.sub(r"\{del:\s*([^}]*)\}", r"~~\1~~", s)
    s = re.sub(r"\{add:\s*([^}]*)\}", r"‹\1›", s)
    return s


def format_html_text(raw: str) -> str:
    if not raw:
        return ""
    s = html.escape(raw)
    s = re.sub(r"\{rubric:\s*([^}]*)\}", r'<span class="rubric">\1</span>', s)
    s = re.sub(r"\{del:\s*([^}]*)\}", r'<del class="scribal-del">\1</del>', s)
    s = re.sub(r"\{add:\s*([^}]*)\}", r'<ins class="scribal-add">&lsaquo;\1&rsaquo;</ins>', s)
    return s


def build_front_matter(total_pages: int, total_lines: int, total_figs: int, page_min: str, page_max: str) -> str:
    return f"""# Wellcome Collection MS.990 (*Arzneibuch*, c. 1675): Parallel German–English Critical Edition with Facsimiles

**Repository:** Wellcome Collection, London (Work ID: `ceuwj8kj` · Sierra ID: `b18775275` · Accession No.: `41913`)  
**IIIF Manifest (v3):** https://iiif.wellcomecollection.org/presentation/b18775275  
**Current Coverage:** {total_pages} Canvases (Canvases 2, 3, 7–135, and 723; {total_lines:,} transcribed lines and {total_figs} annotated figure zones; Pages {page_min} through {page_max})  
**Features:** Includes embedded high-resolution facsimile of each manuscript canvas paired directly with Early New High German diplomatic transcription, modern English translation, alchemical expansions, and paleographic commentary.

---

## Summary of the Transcribed Corpus

This parallel edition presents {total_pages} digitized canvases of Wellcome Collection MS.990, a richly illustrated seventeenth-century Austro-Bavarian medical and surgical compendium (*Arzneibuch*). The edition encompasses the documentary paratexts on the Front Pastedown (Canvas 2), Front Flyleaf 1r (Canvas 3), and 20th-century Binding Spine (Canvas 723), together with a continuous run of manuscript pages spanning `[p. 29]` through `p. 164` (Canvases 7–135, with early modern pagination quirks `30 → 32`, `55 → 60`, and `75 → 78` without textual loss, and including the four physical flap states of the eye dissection on `p. 48` linked to Canvases 727–730). 

Across these {total_lines:,} lines of Early New High German (*Frühneuhochdeutsch*), the compendium spans:
1. **Household and Iatrochemical Remedies (`pp. [29]–30`):** Gravel, hematuria, plague waters, and compound decoctions.
2. **Head, Cervical, and Dental Surgery (`pp. 32–47`):** Scorbutic mouth ulcers, dentifrices, tooth extraction mechanics, parotid swellings (*Kropff* / *Päulen*), facial birthmarks, and goitre cures.
3. **The Great Ophthalmology Compendium (`pp. 48–135+`):**
   - **Anatomy of the Eye (`pp. 48–51`):** Multi-layered anatomical flap fugitive sheet (tunics, humors, optic nerve).
   - **Cataract Treatise (`pp. 73–82`):** Pathogenesis, needle couching (*Katarakt-Stich*), operative instruments, bandages, taffeta shades, and the management of ten post-couching complications.
   - **Lacrimal Fistulae & Trepanation (`pp. 82–88`):** Operative scenes of a Franciscan surgeon operating on a nun, cautery irons, and bone drills for trephining the *os cribrum*.
   - **Corneal Films, Ulcers, and Pterygia (`pp. 89–99`):** Illustrated patient portraits `.A.` through `.E.`, ophthalmic hooks, shears, and unguents.
   - **Ocular Fluxes & Catarrhal Defluxions (`pp. 99–104`):** Hot and cold ocular catarrhs, brass distilling apparatus, and sternutatories.
   - **Traumatic Ocular Injuries, Chemical Burns, and Severe Fluxes (`pp. 105–122`):** Lime burns, foreign bodies, gunpowder burns, and anti-inflammatory collyria.
   - **Eyelid Deformities, Inverted Lashes, and Blepharoplasty (`pp. 123–134`):** Trichiasis, ectropion, entropion, surgical excisions, and fine sutures.
   - **Amaurosis, Glaucoma, and Optic Nerve Atrophy (`pp. 135–164`):** The *Gutta Serena* (black cataract), cephalic purges, masticatories, fontanelles, and cranial vesicants.

## Historical Context and Provenance

Internal linguistic, pharmacological, and archival evidence places MS.990 squarely within an Austro-Bavarian Franciscan milieu around 1675. On Front Flyleaf 1r (Canvas 3), a penciled bookseller's note records that the Wellcome Historical Medical Library acquired the volume in 1922 (Accession No. `41913`) from the Viennese antiquarian firm Gilhofer & Ranschburg. Within the text itself, the compiler provides a decisive geographic anchor on `p. 32` (Canvas 9), praising the newly imported South American resin *Balsam of Copaiba* (*Balsamo Copauia*, brought *auß India*) for the remarkable cures performed with it *in Wienn* (in Vienna). The dialectal phonology reinforces this Danubian-Bavarian origin, exhibiting characteristic Upper German features such as initial `kh-` for Standard German `k-` (*khochen*, *khrankh*, *Khröpff*), `p-` for `b-` (*präne*, *Päulen*), the retention of `ai/aÿ` and `eu/eü`, and regional lexical items including *Krenwurzel* (horseradish), *Schlier* (abscess/bubo), and *Sumer fleckh* (freckles).

## Alchemical and Apothecary Glyph Key

| Glyph | Unicode | Latin / Apothecary Term | German / English Expansion |
| :--- | :--- | :--- | :--- |
| `℞` | U+211E | *Recipe* | Nimm / Take |
| `▽` | U+25BD | *Aqua* | Wasser / Water |
| `V̈` | U+0056 U+0308 | *Vinum* | Wein / Wine |
| `✚` | U+271A | *Acetum* | Essig / Vinegar |
| `🜔` | U+1F714 | *Sal* | Salz / Salt |
| `🜔▽` | U+1F714 U+25BD | *Aqua salis* | Salzwasser / Salt water (brine) |
| `ꝑll̵` | U+A751 U+006C U+006C U+0335 | *Pulvis* | Pulver / Powder |
| `✗` | U+2717 | *Calx* | Kalk / Calcined powder |
| `⊡` | U+22A1 | *Urina* | Harn / Urine |
| `☉` | U+2609 | *Sol* | Sonne / Sun (or Gold) |
| `☿` | U+263F | *Mercurius* | Quecksilber / Mercury |
| `♁` | U+2641 | *Antimonium* | Spießglas / Antimony |
| `🜖` | U+1F716 | *Vitriolum* | Vitriol |
| `🜘` | U+1F718 | *Alumen* | Alaun / Alum |
| `🜕` | U+1F715 | *Nitrum* | Salpeter / Saltpetre |
| `♄` | U+2644 | *Saturnus* | Blei / Lead (e.g. *Sachari ♄* = lead acetate) |
| `XXX` | U+0058 × 3 | *Camphora* | Kampfer / Camphor |
| `△` | U+25B3 | *Ignis* | Feuer / Fire |
| `℔`, `℥`, `ℨ`, `℈`, `ß` | U+2114, U+2125, U+2128, U+2108, U+00DF | *Libra, Uncia, Drachma, Scrupulus, Semis* | Pound, Ounce, Drachm, Scruple, Half (`ß`) |

---
"""


def generate_markdown(data: dict):
    pages = data["pages"]
    total_pages = len(pages)
    total_lines = sum(len(c["lines"]) for p in pages for c in p["columns"])
    total_figs = sum(len(p.get("figures", [])) for p in pages)
    numbered = [p["orig_page"] for p in pages if p["orig_page"] not in ["Front Pastedown", "Flyleaf 1r", "Spine"]]
    page_min = numbered[0] if numbered else "[29]"
    page_max = numbered[-1] if numbered else "164"

    out = [build_front_matter(total_pages, total_lines, total_figs, page_min, page_max)]

    for p in pages:
        cnum = p["canvas_num"]
        orig_p = p["orig_page"]
        jp2 = p["jp2"]
        fside = p.get("folio_side", "")
        w = p.get("width", "")
        h = p.get("height", "")
        canvas_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        full_img_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/full/0/default.jpg"
        iiif_1200_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/1200,/0/default.jpg"
        local_img = f"canvas_{cnum:04d}.jpg"

        out.append(f"\n## Page {orig_p} — IIIF Canvas #{cnum}\n\n")

        # Metadata
        meta_bits = [
            f"**Folio / Side:** {fside}",
            f"**Dimensions:** {w} × {h} px",
            f"[IIIF Canvas]({canvas_uri})",
            f"[Full-Res Image]({full_img_uri})",
        ]
        if 15 <= cnum <= 24:
            meta_bits.append("**Model:** Gemini 3.8 Flash")
        elif p.get("model"):
            meta_bits.append(f"**Model:** {p['model']}")
        if p.get("input_tokens") is not None and p.get("output_tokens") is not None:
            meta_bits.append(f"**Tokens (In / Out):** {p['input_tokens']:,} / {p['output_tokens']:,}")
        out.append(" · ".join(meta_bits) + "\n\n")

        # Embedded Facsimile Image (Responsive centered figure with local image & live IIIF fallback)
        img_block = (
            f"<p align=\"center\" style=\"margin: 1.5rem 0;\">\n"
            f"  <a href=\"{full_img_uri}\" target=\"_blank\" title=\"Click to view full-resolution IIIF facsimile\">\n"
            f"    <img src=\"{local_img}\" alt=\"Facsimile: Wellcome MS.990 Canvas #{cnum} (Page {orig_p})\" style=\"max-height: 720px; max-width: 100%; border: 1px solid #c5bba8; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);\" onerror=\"this.onerror=null; this.src='{iiif_1200_uri}';\" />\n"
            f"  </a>\n"
            f"  <br>\n"
            f"  <em>Facsimile: Canvas #{cnum} ({fside}, Page {orig_p}) · <a href=\"{full_img_uri}\" target=\"_blank\">View Full-Resolution IIIF</a></em>\n"
            f"</p>\n\n"
        )
        out.append(img_block)

        # Summary
        if p.get("summary"):
            out.append(f"{p['summary']}\n\n")

        # Figures
        figs = p.get("figures", [])
        if figs:
            out.append("### Illustrations and Anatomical Diagrams\n\n")
            for fig in figs:
                xywh = f"{fig['ulx']},{fig['uly']},{fig['lrx']-fig['ulx']},{fig['lry']-fig['uly']}"
                out.append(f"- **{fig['label']}** (`#xywh={xywh}`): {fig['desc']}\n")
            out.append("\n")

        # Transcription and Translation Columns
        for col in p["columns"]:
            col_label = col.get("col_label", "Text")
            out.append(f"### {col_label}\n\n")
            out.append("| Line | German Diplomatic (Original) | English Translation & Editorial Notes |\n")
            out.append("| :---: | :--- | :--- |\n")
            for ln in col["lines"]:
                lnum = ln["line_num"]
                de_txt = format_md_text(ln.get("de", ""))
                en_txt = format_md_text(ln.get("en", ""))
                note_txt = format_md_text(ln.get("note") or "")
                if note_txt:
                    en_cell = f"{en_txt} *— Note: {note_txt}*"
                else:
                    en_cell = en_txt
                out.append(f"| {lnum} | {de_txt} | {en_cell} |\n")
            out.append("\n")

        out.append("---\n")

    content = "".join(out)
    MD_OUT_FILE.write_text(content, encoding="utf-8")
    print(f"Generated {MD_OUT_FILE} ({len(content):,} chars, {len(content.splitlines()):,} lines)")


def generate_html(data: dict):
    pages = data["pages"]
    total_pages = len(pages)
    total_lines = sum(len(c["lines"]) for p in pages for c in p["columns"])
    total_figs = sum(len(p.get("figures", [])) for p in pages)

    # Pre-render page options for fast switching
    page_options = [
        '<option value="landing">Overview &amp; Summary (Landing Page)</option>',
        '<option value="index">Index: Ingredients, People, Places &amp; Terms</option>',
        f'<option value="figures">Figures &amp; Diagrams ({total_figs})</option>',
    ]
    cnum_to_idx = {}
    for idx, p in enumerate(pages):
        cnum = p["canvas_num"]
        cnum_to_idx[cnum] = idx
        op = p["orig_page"]
        fs = p.get("folio_side", "")
        page_options.append(f'<option value="{idx}">Page {op} (Canvas #{cnum} {fs})</option>')

    entity_path = Path("MS990_entity_index.json")
    entities = json.loads(entity_path.read_text(encoding="utf-8")) if entity_path.exists() else []

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Wellcome MS.990 — Illustrated Parallel Critical Edition</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@500;700&family=Cormorant+Garamond:ital,wght@0,400;0,600;0,700;1,400;1,600&family=Fira+Code:wght@400;500&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg-cream: #fbf9f4;
      --bg-card: #ffffff;
      --text-dark: #221f1d;
      --text-muted: #5e5852;
      --border-parchment: #e0d8c8;
      --border-accent: #b8860b;
      --rubric-red: #a31d1d;
      --del-color: #8c7373;
      --add-color: #1e5a28;
      --accent-gold: #c59b27;
      --shadow-soft: 0 4px 14px rgba(0,0,0,0.06);
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'Inter', system-ui, sans-serif;
      background: var(--bg-cream);
      color: var(--text-dark);
      line-height: 1.5;
    }}
    header {{
      background: #2a231d;
      color: #f7f3ec;
      padding: 1rem 1.5rem;
      border-bottom: 3px solid var(--accent-gold);
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 10px rgba(0,0,0,0.3);
    }}
    .header-titles h1 {{
      font-family: 'Cinzel', serif;
      font-size: 1.25rem;
      letter-spacing: 0.05em;
      color: #fcefd4;
    }}
    .header-titles p {{
      font-size: 0.8rem;
      color: #c9bea9;
    }}
    .nav-controls {{
      display: flex;
      align-items: center;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    select, input, button {{
      font-family: inherit;
      font-size: 0.85rem;
      padding: 0.45rem 0.75rem;
      border-radius: 4px;
      border: 1px solid #5a4f44;
      background: #3b322a;
      color: #f7f3ec;
    }}
    button {{
      cursor: pointer;
      background: var(--accent-gold);
      color: #1a1612;
      font-weight: 600;
      border: none;
      transition: all 0.15s ease;
    }}
    button:hover {{
      background: #e0b034;
    }}
    .btn-secondary {{
      background: #473e34;
      color: #e6decb;
    }}
    .btn-secondary:hover {{
      background: #594e42;
    }}
    main {{
      max-width: 1680px;
      margin: 1.5rem auto;
      padding: 0 1rem;
    }}
    .page-card {{
      display: none;
      background: var(--bg-card);
      border: 1px solid var(--border-parchment);
      border-radius: 8px;
      box-shadow: var(--shadow-soft);
      overflow: hidden;
    }}
    .page-card.active {{
      display: block;
    }}
    .page-header {{
      background: #f4eee2;
      border-bottom: 1px solid var(--border-parchment);
      padding: 1rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .page-title {{
      font-family: 'Cinzel', serif;
      font-size: 1.25rem;
      color: #3b2f22;
    }}
    .page-meta {{
      font-size: 0.82rem;
      color: var(--text-muted);
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
    }}
    .page-meta a {{
      color: #8c5b05;
      text-decoration: none;
      font-weight: 500;
    }}
    .page-meta a:hover {{
      text-decoration: underline;
    }}
    .split-layout {{
      display: grid;
      grid-template-columns: minmax(360px, 48%) 1fr;
      min-height: calc(100vh - 180px);
    }}
    @media (max-width: 1024px) {{
      .split-layout {{
        grid-template-columns: 1fr;
      }}
    }}
    .facsimile-pane {{
      background: #181512;
      border-right: 1px solid var(--border-parchment);
      padding: 1.5rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: flex-start;
      position: sticky;
      top: 68px;
      max-height: calc(100vh - 70px);
      overflow-y: auto;
    }}
    .facsimile-container {{
      position: relative;
      width: 100%;
      text-align: center;
    }}
    .facsimile-img {{
      max-width: 100%;
      max-height: calc(100vh - 160px);
      object-fit: contain;
      border-radius: 4px;
      box-shadow: 0 4px 20px rgba(0,0,0,0.6);
      transition: transform 0.2s ease;
      cursor: zoom-in;
    }}
    .facsimile-caption {{
      color: #c9bea9;
      font-size: 0.75rem;
      margin-top: 0.75rem;
      text-align: center;
    }}
    .facsimile-caption a {{
      color: var(--accent-gold);
      text-decoration: none;
    }}
    .text-pane {{
      padding: 1.5rem 2rem;
      overflow-y: auto;
      max-height: calc(100vh - 70px);
    }}
    .summary-box {{
      background: #fbf7ee;
      border-left: 3px solid var(--accent-gold);
      padding: 0.85rem 1.25rem;
      margin-bottom: 1.5rem;
      font-family: 'Cormorant Garamond', serif;
      font-size: 1.15rem;
      line-height: 1.55;
      color: #3f362d;
    }}
    .figures-box {{
      background: #f3efe6;
      border: 1px dashed #c0b39c;
      border-radius: 6px;
      padding: 0.85rem 1.25rem;
      margin-bottom: 1.5rem;
      font-size: 0.85rem;
    }}
    .figures-box h4 {{
      font-family: 'Cinzel', serif;
      font-size: 0.85rem;
      margin-bottom: 0.5rem;
      color: #4a3c2c;
    }}
    .col-title {{
      font-family: 'Cinzel', serif;
      font-size: 1rem;
      margin: 1.5rem 0 0.75rem 0;
      color: #4a3824;
      border-bottom: 1px solid var(--border-parchment);
      padding-bottom: 0.25rem;
    }}
    .parallel-table {{
      width: 100%;
      border-collapse: collapse;
      margin-bottom: 2rem;
    }}
    .parallel-table th {{
      background: #ede4d3;
      color: #3b2d1c;
      font-family: 'Cinzel', serif;
      font-size: 0.78rem;
      letter-spacing: 0.04em;
      padding: 0.6rem 0.75rem;
      border: 1px solid var(--border-parchment);
      text-align: left;
    }}
    .parallel-table td {{
      padding: 0.65rem 0.85rem;
      border: 1px solid var(--border-parchment);
      vertical-align: top;
      font-size: 0.92rem;
    }}
    .col-num {{
      width: 44px;
      text-align: center !important;
      font-family: 'Fira Code', monospace;
      font-size: 0.78rem;
      color: #8c8275;
      background: #faf6ee;
    }}
    .col-de {{
      width: 48%;
      font-family: 'Cormorant Garamond', serif;
      font-size: 1.15rem;
      line-height: 1.45;
      color: #1a1612;
      background: #fffdf9;
    }}
    .col-en {{
      font-family: 'Inter', system-ui, sans-serif;
      font-size: 0.88rem;
      line-height: 1.48;
      color: #2b2621;
    }}
    .rubric {{
      color: var(--rubric-red);
      font-weight: 600;
    }}
    .scribal-del {{
      color: var(--del-color);
      text-decoration: line-through;
    }}
    .scribal-add {{
      color: var(--add-color);
      font-style: italic;
    }}
    .editorial-note {{
      display: block;
      margin-top: 0.3rem;
      font-size: 0.78rem;
      color: #706354;
      font-style: italic;
    }}
    .badge {{
      display: inline-block;
      font-size: 0.72rem;
      padding: 0.15rem 0.45rem;
      border-radius: 3px;
      background: #e2d7c3;
      color: #4a3f32;
      font-weight: 500;
    }}
    .view-toggle {{
      display: flex;
      gap: 0.25rem;
      background: #251e18;
      padding: 0.2rem;
      border-radius: 4px;
    }}
    .view-toggle button {{
      padding: 0.3rem 0.6rem;
      font-size: 0.75rem;
    }}
    .view-toggle button.active {{
      background: var(--accent-gold);
      color: #1a1612;
    }}
    .visually-hidden {{
      position: absolute;
      clip-path: inset(50%);
      overflow: hidden;
      width: 1px;
      height: 1px;
      margin: -1px;
      padding: 0;
      border: 0;
      white-space: nowrap;
    }}
    search form {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
    }}
    .search-status {{
      font-size: 0.78rem;
      color: #e2d7c3;
      white-space: nowrap;
    }}
    dialog:modal {{
      overscroll-behavior: contain;
      max-width: min(920px, 92vw);
      width: 100%;
      max-height: 82vh;
      margin: auto;
      padding: 0;
      border: 1px solid #cbbba2;
      border-radius: 8px;
      background: #fdfaf3;
      color: #2b231b;
      box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
    }}
    dialog[open] {{
      display: flex;
      flex-direction: column;
    }}
    dialog::backdrop {{
      background: rgba(20, 16, 12, 0.65);
      overflow: hidden;
      overscroll-behavior: contain;
    }}
    .search-dialog-header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      padding: 0.9rem 1.2rem;
      background: #2b231b;
      color: #fdfaf3;
      border-bottom: 1px solid #4a3f32;
    }}
    .search-dialog-header h2 {{
      margin: 0;
      font-size: 1.05rem;
    }}
    .search-dialog-bar {{
      padding: 0.75rem 1.2rem;
      background: #f8f3e8;
      border-bottom: 1px solid #dfd3be;
    }}
    .search-dialog-bar form {{
      display: flex;
      gap: 0.5rem;
      width: 100%;
    }}
    .search-dialog-bar input[type="search"] {{
      flex: 1;
      font: inherit;
      font-size: max(1rem, 1em);
      padding: 0.5rem 0.75rem;
      border: 1px solid #b5a387;
      border-radius: 5px;
      background: #ffffff;
      color: #2b231b;
    }}
    .search-dialog-meta {{
      padding: 0.6rem 1.2rem;
      background: #f2eadc;
      border-bottom: 1px solid #dfd3be;
      font-size: 0.85rem;
      color: #4a3f32;
    }}
    .search-results-list {{
      overflow-y: auto;
      padding: 0.8rem 1.2rem;
      display: flex;
      flex-direction: column;
      gap: 0.65rem;
    }}
    .search-result-btn {{
      display: block;
      width: 100%;
      text-align: left;
      padding: 0.75rem 0.9rem;
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 6px;
      cursor: pointer;
      color: #2b231b;
      font: inherit;
    }}
    .search-result-btn:hover,
    .search-result-btn:focus-visible {{
      border-color: #8b5a2b;
      background: #fcf7ec;
      outline: 2px solid #8b5a2b;
      outline-offset: 1px;
    }}
    .search-result-loc {{
      font-size: 0.78rem;
      font-weight: 700;
      color: #7c3f1d;
      margin-bottom: 0.25rem;
    }}
    .search-result-pair {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 0.75rem;
      font-size: 0.88rem;
      line-height: 1.4;
    }}
    @media (max-width: 700px) {{
      .search-result-pair {{
        grid-template-columns: 1fr;
      }}
    }}
    mark {{
      background: #fde68a;
      color: #1f160d;
      padding: 0 2px;
      border-radius: 2px;
    }}
    tr.search-target-row {{
      background: #fef3c7 !important;
      outline: 2px solid #b45309;
    }}
    .landing-wrap {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 2rem 1.5rem 3rem;
    }}
    .landing-hero {{
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 10px;
      padding: 2rem;
      margin-bottom: 1.75rem;
      box-shadow: 0 4px 18px rgba(43, 35, 27, 0.06);
    }}
    .landing-hero h2 {{
      font-family: 'Cinzel', serif;
      font-size: 1.75rem;
      color: #2b231b;
      margin: 0 0 0.75rem;
    }}
    .landing-hero p {{
      font-size: 1rem;
      line-height: 1.65;
      color: #3d3328;
      margin: 0 0 1rem;
    }}
    .landing-stats {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.6rem;
      margin: 1rem 0 1.4rem;
    }}
    .landing-actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.75rem;
    }}
    .btn-primary {{
      background: #7c3f1d;
      color: #fdfaf3;
      border: 1px solid #5e2e14;
      padding: 0.6rem 1.1rem;
      border-radius: 5px;
      font: inherit;
      font-weight: 600;
      cursor: pointer;
    }}
    .btn-primary:hover {{
      background: #5e2e14;
    }}
    .landing-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
      gap: 1rem;
    }}
    .section-card {{
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 8px;
      padding: 1.1rem 1.2rem;
      text-align: left;
      cursor: pointer;
      font: inherit;
      color: #2b231b;
      transition: border-color 0.15s, transform 0.15s;
    }}
    .section-card:hover,
    .section-card:focus-visible {{
      border-color: #7c3f1d;
      transform: translateY(-2px);
      outline: 2px solid #7c3f1d;
      outline-offset: 2px;
    }}
    .section-card h3 {{
      margin: 0 0 0.35rem;
      font-size: 1rem;
      color: #7c3f1d;
    }}
    .section-card p {{
      margin: 0;
      font-size: 0.86rem;
      line-height: 1.45;
      color: #4a3f32;
    }}
    .index-controls {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: 0.6rem;
      margin-bottom: 1.25rem;
      padding: 1rem;
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 8px;
    }}
    .cat-btn {{
      background: #f2eadc;
      color: #2b231b;
      border: 1px solid #cbbba2;
      padding: 0.4rem 0.8rem;
      border-radius: 4px;
      cursor: pointer;
      font: inherit;
      font-size: 0.85rem;
      font-weight: 600;
    }}
    .cat-btn.active {{
      background: #7c3f1d;
      color: #fdfaf3;
      border-color: #5e2e14;
    }}
    .index-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
      gap: 1rem;
    }}
    .entity-card {{
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 8px;
      padding: 1rem 1.1rem;
    }}
    .entity-head {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 0.5rem;
      margin-bottom: 0.35rem;
    }}
    .entity-name {{
      font-weight: 700;
      font-size: 1rem;
      color: #2b231b;
    }}
    .entity-wd {{
      display: inline-block;
      font-size: 0.78rem;
      color: #1d4ed8;
      text-decoration: none;
      margin-bottom: 0.4rem;
    }}
    .entity-wd:hover {{
      text-decoration: underline;
    }}
    .entity-desc {{
      font-size: 0.82rem;
      color: #5a4d3f;
      margin: 0 0 0.6rem;
    }}
    .entity-pages {{
      display: flex;
      flex-wrap: wrap;
      gap: 0.35rem;
    }}
    .page-chip {{
      background: #f2eadc;
      border: 1px solid #d4c6af;
      color: #2b231b;
      border-radius: 4px;
      padding: 0.18rem 0.45rem;
      font-size: 0.75rem;
      cursor: pointer;
      font-family: inherit;
    }}
    .page-chip:hover {{
      background: #e2d7c3;
      border-color: #7c3f1d;
    }}
    .figures-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 1.1rem;
    }}
    .figure-card {{
      background: #ffffff;
      border: 1px solid #dfd3be;
      border-radius: 8px;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }}
    .figure-thumb-wrap {{
      background: #f2eadc;
      border-bottom: 1px solid #dfd3be;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 200px;
      max-height: 280px;
      overflow: hidden;
    }}
    .figure-thumb-wrap img {{
      width: 100%;
      height: 240px;
      object-fit: contain;
      display: block;
    }}
    .figure-body {{
      padding: 0.9rem 1rem;
      display: flex;
      flex-direction: column;
      gap: 0.4rem;
      flex: 1;
    }}
    .figure-body h3 {{
      margin: 0;
      font-size: 0.96rem;
      color: #2b231b;
    }}
    .figure-body p {{
      margin: 0;
      font-size: 0.83rem;
      line-height: 1.45;
      color: #4a3f32;
      flex: 1;
    }}
    .figure-foot {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 0.5rem;
      margin-top: 0.4rem;
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-titles">
      <h1>Wellcome MS.990 · Parallel Critical Edition</h1>
      <p>Austro-Bavarian Medical &amp; Surgical Compendium (ca. 1650–1680) · {total_pages} Canvases · {total_lines:,} Lines</p>
    </div>
    <div class="nav-controls">
      <button type="button" class="btn-secondary" id="btn-home" onclick="showLanding()">Overview</button>
      <button type="button" class="btn-secondary" id="btn-index" onclick="showIndex()">Index</button>
      <button type="button" class="btn-secondary" id="btn-figures" onclick="showFigures()">Figures ({total_figs})</button>
      <button type="button" class="btn-secondary" id="btn-prev" onclick="changePage(-1)">&#9664; Prev</button>
      <select id="page-select" aria-label="Select manuscript page" onchange="jumpToPage(this.value)">
        {''.join(page_options)}
      </select>
      <button type="button" class="btn-secondary" id="btn-next" onclick="changePage(1)">Next &#9654;</button>
      <search>
        <form id="corpus-search-form" action="#" method="GET">
          <label for="filter-input" class="visually-hidden">Search across all pages</label>
          <input type="search" id="filter-input" name="q" placeholder="Search all {total_pages} pages..." autocorrect="off" autocapitalize="none" spellcheck="false" enterkeyhint="search" oninput="filterText(this.value)" />
          <button type="submit" class="btn-secondary" id="btn-search-all">Search Edition</button>
        </form>
      </search>
      <span id="search-status" class="search-status" role="status" aria-live="polite"></span>
    </div>
  </header>

  <main id="edition-container">
"""

    # Build Landing Page Card (active by default) — Notable Illustrated Highlights
    sections_jump = [
        ("p. 36 (c.13) · Dental Anatomy & Fumigation", 13, "Watercolour study of four human teeth and a profile portrait of a patient using a brass throat-fumigation tube."),
        ("p. 48 (c.25) · Eye Anatomy Flap Plate (Klappbild)", 25, "Multi-layered anatomical dissection of the eye, extraocular muscles, and seven tunics (flap states on c.727–730)."),
        ("p. 84 (c.55) · Lacrimal Fistula Surgery", 55, "Operative portrait of a nun after lacrimal fistula incision alongside three illustrated surgical knives and lancets."),
        ("p. 166 (c.137) · Distillation & Alchemical Furnaces", 137, "Full-page watercolor plate of six serpentine distillation trains, alembics, and receivers (pp. 166–168)."),
        ("p. 257 (c.230) · Viscera: Intestines & Omentum", 230, "Four anatomical watercolor drawings of the intestines (Därm), omentum (das Nötz), and peritoneum (pp. 254–257)."),
        ("p. 352 (c.322) · Early Modern Apothecary Interior", 322, "Full-page watercolor scene depicting the interior of an early modern apothecary and alchemical dispensary."),
        ("p. 393 (c.358) · Illustrated Materia Medica: Myrobalans", 358, "Five botanical watercolor studies of medicinal myrobalans (Bellerica, Emblica, Chebula, Citrine, and Indica)."),
        ("p. 542 (c.733) · Monastic Eye-Remedy Apothecary", 733, "Full-page watercolor of a friar dispensing eye remedies beneath five labeled shelves to blindfolded patients."),
        ("p. 765 (c.699) · Limb Amputation Preparation", 699, "Clinical scene showing a seated patient, surgeon, assistants with curved amputation knife, and instrument table."),
        ("p. 781 (c.705) · Peasants' & Poor People's Apothecary", 705, "Watercolor of two apothecary shelves opening Paurn, Vnd Armer Leüdt apotecken (remedies for the poor)."),
    ]
    sec_cards_html = []
    for stitle, scnum, sdesc in sections_jump:
        sidx = cnum_to_idx.get(scnum, 0)
        sec_cards_html.append(
            f'          <button type="button" class="section-card" onclick="showPage({sidx})">\n'
            f'            <h3>{html.escape(stitle)}</h3>\n'
            f'            <p>{html.escape(sdesc)}</p>\n'
            f'          </button>\n'
        )

    landing_html = f"""    <section class="page-card active" id="landing-card">
      <div class="landing-wrap">
        <div class="landing-hero">
          <h2>Wellcome Collection MS.990: Parallel German–English Edition</h2>
          <p>
            Compiled in an Austro-Bavarian Franciscan milieu around 1650–1680 (and acquired by Henry Wellcome in 1922 from the Viennese firm Gilhofer &amp; Ranschburg), <b>MS.990</b> is a richly illustrated Early New High German (<i>Frühneuhochdeutsch</i>) medical, surgical, and iatrochemical compendium (<i>Arzneibuch</i>). Although the opening 28 pages are wanting, the surviving codex spans <b>{total_pages} digitized canvases</b> across <b>{total_lines:,} aligned lines</b> and <b>{total_figs} catalogued illustrations and diagrams</b>, uniting Galenic humoral pathology, Paracelsian chemical pharmacy, operative surgery, and vernacular charitable medicine.
          </p>
          <div class="landing-stats">
            <span class="badge">{total_pages} Canvases</span>
            <span class="badge">{total_lines:,} Aligned Lines</span>
            <span class="badge">{total_figs} Figures &amp; Diagrams</span>
            <span class="badge">{len(entities)} Indexed Entities (Wikidata-Linked)</span>
          </div>
          <div class="landing-actions">
            <button type="button" class="btn-primary" onclick="showPage(0)">Start Reading Edition &rarr;</button>
            <button type="button" class="btn-secondary" onclick="showIndex()">Browse Index (Ingredients, People, Places &amp; Terms)</button>
            <button type="button" class="btn-secondary" onclick="showFigures()">Browse Figures &amp; Diagrams ({total_figs})</button>
            <button type="button" class="btn-secondary" onclick="openCorpusSearch('')">Search All {total_pages} Pages</button>
          </div>
        </div>
        <div class="landing-grid">
{''.join(sec_cards_html)}        </div>
      </div>
    </section>
"""

    # Build Entity Index Card (Ingredients, People, Places, Terms linked to Wikidata)
    entity_cards_html = []
    for ent in entities:
        cat = ent.get("category", "Terms")
        ename = ent.get("name", "")
        qid = ent.get("qid", "")
        wdesc = ent.get("wd_desc", "")
        lhits = ent.get("line_hits", 0)
        phits = ent.get("page_hits", 0)
        refs = ent.get("refs", [])
        chips = []
        for r in refs[:14]:
            ridx = r["pIdx"]
            rop = r.get("orig_page") or f"c.{r['canvas_num']}"
            chips.append(f'<button type="button" class="page-chip" onclick="showPage({ridx})" title="Canvas #{r["canvas_num"]} ({r["lines"]} hits)">p. {html.escape(str(rop))}</button>')
        if len(refs) > 14:
            chips.append(f'<span class="badge">+{len(refs)-14} more pages</span>')
        wd_link = (
            f'<a class="entity-wd" href="https://www.wikidata.org/wiki/{html.escape(qid)}" target="_blank" rel="noopener">Wikidata: {html.escape(qid)} &#8599;</a>'
            if qid else '<span class="entity-desc">No Wikidata link assigned</span>'
        )
        desc_p = f'<p class="entity-desc">{html.escape(wdesc)}</p>' if wdesc else ""
        entity_cards_html.append(
            f'          <article class="entity-card" data-cat="{html.escape(cat)}" data-name="{html.escape(ename.lower())} {html.escape(wdesc.lower())}">\n'
            f'            <div class="entity-head"><span class="entity-name">{html.escape(ename)}</span><span class="badge">{html.escape(cat)} &middot; {lhits} lines / {phits} pp.</span></div>\n'
            f'            {wd_link}\n'
            f'            {desc_p}\n'
            f'            <div class="entity-pages">{"".join(chips)}</div>\n'
            f'          </article>\n'
        )

    index_html = f"""    <section class="page-card" id="index-card">
      <div class="landing-wrap">
        <div class="landing-hero">
          <h2>Index of Ingredients, People, Places &amp; Terms</h2>
          <p>Curated entities extracted across all {total_pages} pages of Wellcome MS.990, linked to verified Wikidata identifiers (<code>Q-IDs</code>) and clickable page occurrences.</p>
        </div>
        <div class="index-controls">
          <button type="button" class="cat-btn active" onclick="setIndexCategory('All', this)">All ({len(entities)})</button>
          <button type="button" class="cat-btn" onclick="setIndexCategory('Ingredients', this)">Ingredients</button>
          <button type="button" class="cat-btn" onclick="setIndexCategory('People', this)">People</button>
          <button type="button" class="cat-btn" onclick="setIndexCategory('Places', this)">Places</button>
          <button type="button" class="cat-btn" onclick="setIndexCategory('Terms', this)">Terms</button>
          <label for="index-filter" class="visually-hidden">Filter index terms</label>
          <input type="search" id="index-filter" placeholder="Filter index..." oninput="filterIndex(this.value)" style="margin-left:auto;padding:0.4rem 0.65rem;border:1px solid #cbbba2;border-radius:4px;" />
        </div>
        <div class="index-grid" id="index-grid">
{''.join(entity_cards_html)}        </div>
      </div>
    </section>
"""

    # Build Figures & Diagrams Gallery Card (IIIF region crops where custom bbox exists)
    fig_cards_html = []
    cropped_count = 0
    fullpage_count = 0
    for pIdx, p in enumerate(pages):
        cnum = p["canvas_num"]
        op = p.get("orig_page") or f"c.{cnum}"
        jp2 = p["jp2"]
        pw = p.get("width", 2400)
        crx = (300 + pw - 800) // 2
        for fg in p.get("figures", []):
            ulx, uly, lrx, lry = fg.get("ulx"), fg.get("uly"), fg.get("lrx"), fg.get("lry")
            is_placeholder = (
                (ulx, uly, lrx, lry) == (400, 400, crx - 50, 1400)
                or None in (ulx, uly, lrx, lry)
                or lrx <= ulx
                or lry <= uly
            )
            if is_placeholder:
                fullpage_count += 1
                img_url = f"https://iiif.wellcomecollection.org/image/{jp2}/full/600,/0/default.jpg"
                full_url = f"https://iiif.wellcomecollection.org/image/{jp2}/full/full/0/default.jpg"
                crop_mode = "full"
                crop_badge = "Full-page view"
            else:
                cropped_count += 1
                rw, rh = lrx - ulx, lry - uly
                ph = p.get("height", 3000)
                px = round(100.0 * ulx / pw, 2)
                py = round(100.0 * uly / ph, 2)
                pw_pct = round(100.0 * rw / pw, 2)
                ph_pct = round(100.0 * rh / ph, 2)
                pct_region = f"pct:{px},{py},{pw_pct},{ph_pct}"
                img_url = f"https://iiif.wellcomecollection.org/image/{jp2}/{pct_region}/600,/0/default.jpg"
                full_url = f"https://iiif.wellcomecollection.org/image/{jp2}/{pct_region}/full/0/default.jpg"
                crop_mode = "crop"
                crop_badge = f"IIIF Crop ({px}%,{py}%,{pw_pct}%,{ph_pct}%)"
            flabel = fg.get("label", "Figure")
            fdesc = fg.get("desc", "")
            search_blob = f"{flabel} {fdesc} p. {op} canvas {cnum}".lower()
            fig_cards_html.append(
                f'          <article class="figure-card" data-crop="{crop_mode}" data-text="{html.escape(search_blob)}">\n'
                f'            <a class="figure-thumb-wrap" href="{full_url}" target="_blank" rel="noopener" title="Open full-resolution IIIF image">\n'
                f'              <img src="{img_url}" alt="{html.escape(flabel)} (Page {html.escape(str(op))}, Canvas #{cnum})" loading="lazy" />\n'
                f'            </a>\n'
                f'            <div class="figure-body">\n'
                f'              <h3>{html.escape(flabel)}</h3>\n'
                f'              <p>{html.escape(fdesc)}</p>\n'
                f'              <div class="figure-foot">\n'
                f'                <span class="badge">p. {html.escape(str(op))} &middot; c.{cnum} &middot; {html.escape(crop_badge)}</span>\n'
                f'                <button type="button" class="page-chip" onclick="showPage({pIdx})">Go to Page &rarr;</button>\n'
                f'              </div>\n'
                f'            </div>\n'
                f'          </article>\n'
            )

    figures_html = f"""    <section class="page-card" id="figures-card">
      <div class="landing-wrap">
        <div class="landing-hero">
          <h2>Figures &amp; Diagrams ({total_figs})</h2>
          <p>All {total_figs} catalogued watercolor illustrations, anatomical diagrams, surgical instruments, and conservation plates across Wellcome MS.990. {cropped_count} figures with recorded pixel coordinates are cropped directly via the Wellcome IIIF Image API; {fullpage_count} figures without tight region coordinates display the full-page thumbnail.</p>
        </div>
        <div class="index-controls">
          <button type="button" class="cat-btn active" onclick="setFigureFilter('all', this)">All ({total_figs})</button>
          <button type="button" class="cat-btn" onclick="setFigureFilter('crop', this)">IIIF Cropped ({cropped_count})</button>
          <button type="button" class="cat-btn" onclick="setFigureFilter('full', this)">Full Page ({fullpage_count})</button>
          <label for="figures-filter" class="visually-hidden">Filter figures</label>
          <input type="search" id="figures-filter" placeholder="Filter figures..." oninput="filterFigures(this.value)" style="margin-left:auto;padding:0.4rem 0.65rem;border:1px solid #cbbba2;border-radius:4px;" />
        </div>
        <div class="figures-grid" id="figures-grid">
{''.join(fig_cards_html)}        </div>
      </div>
    </section>
"""
    html_content += landing_html + index_html + figures_html

    # Generate page blocks
    cards_html = []
    for idx, p in enumerate(pages):
        cnum = p["canvas_num"]
        orig_p = p["orig_page"]
        jp2 = p["jp2"]
        fside = p.get("folio_side", "")
        w = p.get("width", "")
        h = p.get("height", "")
        canvas_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        full_img_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/full/0/default.jpg"
        iiif_1200_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/1200,/0/default.jpg"
        local_img = f"canvas_{cnum:04d}.jpg"

        card = [f'    <div class="page-card" id="page-card-{idx}" data-index="{idx}">\n']
        card.append('      <div class="page-header">\n')
        card.append(f'        <h2 class="page-title">Page {orig_p} &mdash; Canvas #{cnum} ({fside})</h2>\n')
        card.append('        <div class="page-meta">\n')
        card.append(f'          <span><b>Dimensions:</b> {w} &times; {h} px</span>\n')
        if p.get("model"):
            card.append(f'          <span class="badge">{html.escape(p["model"])}</span>\n')
        if p.get("input_tokens") is not None and p.get("output_tokens") is not None:
            card.append(f'          <span class="badge">Tokens: {p["input_tokens"]:,} in / {p["output_tokens"]:,} out</span>\n')
        card.append(f'          <a href="{canvas_uri}" target="_blank">IIIF Canvas</a> &middot;\n')
        card.append(f'          <a href="{full_img_uri}" target="_blank">Full-Resolution Image</a>\n')
        card.append('        </div>\n')
        card.append('      </div>\n\n')

        card.append('      <div class="split-layout">\n')
        card.append('        <div class="facsimile-pane">\n')
        card.append('          <div class="facsimile-container">\n')
        card.append(f'            <a href="{full_img_uri}" target="_blank" title="Click to view full-resolution IIIF image in new tab">\n')
        card.append(f'              <img class="facsimile-img" src="{local_img}" alt="Wellcome MS.990 Canvas #{cnum}" onerror="this.onerror=null; this.src=\'{iiif_1200_uri}\';" />\n')
        card.append('            </a>\n')
        card.append(f'            <div class="facsimile-caption">Canvas #{cnum} ({fside}, Page {orig_p}) &middot; <a href="{full_img_uri}" target="_blank">Open Full-Res IIIF &#8599;</a></div>\n')
        card.append('          </div>\n')
        card.append('        </div>\n\n')

        card.append('        <div class="text-pane">\n')
        if p.get("summary"):
            card.append(f'          <div class="summary-box"><b>Editorial Summary:</b> {html.escape(p["summary"])}</div>\n')

        figs = p.get("figures", [])
        if figs:
            card.append('          <div class="figures-box">\n')
            card.append('            <h4>Illustrations &amp; Diagrams</h4>\n')
            card.append('            <ul>\n')
            for fig in figs:
                xywh = f"{fig['ulx']},{fig['uly']},{fig['lrx']-fig['ulx']},{fig['lry']-fig['uly']}"
                card.append(f'              <li><b>{html.escape(fig["label"])}</b> (<code>#xywh={xywh}</code>): {html.escape(fig["desc"])}</li>\n')
            card.append('            </ul>\n')
            card.append('          </div>\n')

        for col in p["columns"]:
            col_label = col.get("col_label", "Text")
            card.append(f'          <h3 class="col-title">{html.escape(col_label)}</h3>\n')
            card.append('          <table class="parallel-table">\n')
            card.append('            <thead>\n')
            card.append('              <tr>\n')
            card.append('                <th class="col-num">#</th>\n')
            card.append('                <th>Transcription</th>\n')
            card.append('                <th>English Translation &amp; Editorial Glosses</th>\n')
            card.append('              </tr>\n')
            card.append('            </thead>\n')
            card.append('            <tbody>\n')
            for ln in col["lines"]:
                lnum = ln["line_num"]
                de_h = format_html_text(ln.get("de", ""))
                en_h = format_html_text(ln.get("en", ""))
                note_h = format_html_text(ln.get("note") or "")
                note_span = f'<span class="editorial-note">&mdash; Note: {note_h}</span>' if note_h else ""
                card.append(f'              <tr><td class="col-num">{lnum}</td><td class="col-de">{de_h}</td><td class="col-en">{en_h}{note_span}</td></tr>\n')
            card.append('            </tbody>\n')
            card.append('          </table>\n')

        card.append('        </div>\n')
        card.append('      </div>\n')
        card.append('    </div>\n')
        cards_html.append("".join(card))

    html_content += "".join(cards_html)
    html_content += """
  </main>

  <dialog id="search-dialog" closedby="any" aria-labelledby="search-dialog-title">
    <div class="search-dialog-header">
      <h2 id="search-dialog-title">Search Across All {total_pages} Pages</h2>
      <form method="dialog">
        <button type="submit" class="btn-secondary" value="close">Close</button>
      </form>
    </div>
    <div class="search-dialog-bar">
      <search>
        <form id="dialog-search-form" action="#" method="GET">
          <label for="dialog-search-input" class="visually-hidden">Search across all {total_pages} pages</label>
          <input type="search" id="dialog-search-input" name="dq" placeholder="Type German, English, or editorial term (e.g. cataract, antimony, Wienn)..." autocorrect="off" autocapitalize="none" spellcheck="false" enterkeyhint="search" autofocus />
          <button type="submit" class="btn-primary">Search</button>
        </form>
      </search>
    </div>
    <div id="search-dialog-meta" class="search-dialog-meta" role="status" aria-live="polite"></div>
    <div id="search-results-list" class="search-results-list"></div>
  </dialog>

  <script>
    let currentIndex = -1;
    const total = """ + str(total_pages) + """;
    let corpusIndex = null;
    let activeIndexCat = 'All';

    function buildCorpusIndex() {
      if (corpusIndex !== null) return corpusIndex;
      corpusIndex = [];
      const cards = document.querySelectorAll('.page-card[data-index]');
      cards.forEach((card, pIdx) => {
        const titleEl = card.querySelector('.page-title');
        const pageLabel = titleEl ? titleEl.textContent.trim() : ('Canvas #' + (pIdx + 1));
        const rows = card.querySelectorAll('tbody tr');
        rows.forEach((tr) => {
          const numEl = tr.querySelector('.col-num');
          const deEl = tr.querySelector('.col-de');
          const enEl = tr.querySelector('.col-en');
          const deText = deEl ? deEl.textContent : '';
          const enText = enEl ? enEl.textContent : '';
          const combined = (deText + ' ' + enText).toLowerCase();
          corpusIndex.push({
            pIdx,
            pageLabel,
            lineNum: numEl ? numEl.textContent.trim() : '',
            deText,
            enText,
            combined,
            tr
          });
        });
      });
      return corpusIndex;
    }

    function showLanding() {
      currentIndex = -1;
      document.querySelectorAll('.page-card').forEach(el => el.classList.remove('active'));
      document.getElementById('landing-card').classList.add('active');
      document.getElementById('page-select').value = 'landing';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function showIndex() {
      currentIndex = -1;
      document.querySelectorAll('.page-card').forEach(el => el.classList.remove('active'));
      document.getElementById('index-card').classList.add('active');
      document.getElementById('page-select').value = 'index';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    let activeFigMode = 'all';
    function showFigures() {
      currentIndex = -1;
      document.querySelectorAll('.page-card').forEach(el => el.classList.remove('active'));
      document.getElementById('figures-card').classList.add('active');
      document.getElementById('page-select').value = 'figures';
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function setFigureFilter(mode, btn) {
      activeFigMode = mode;
      const controls = btn.parentElement;
      controls.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      filterFigures(document.getElementById('figures-filter').value);
    }

    function filterFigures(q) {
      const ql = q.trim().toLowerCase();
      document.querySelectorAll('#figures-grid .figure-card').forEach(card => {
        const modeOk = activeFigMode === 'all' || card.dataset.crop === activeFigMode;
        const textOk = !ql || card.dataset.text.includes(ql);
        card.style.display = (modeOk && textOk) ? '' : 'none';
      });
    }

    function setIndexCategory(cat, btn) {
      activeIndexCat = cat;
      document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
      if (btn) btn.classList.add('active');
      filterIndex(document.getElementById('index-filter').value);
    }

    function filterIndex(q) {
      const ql = q.trim().toLowerCase();
      document.querySelectorAll('#index-grid .entity-card').forEach(card => {
        const catOk = activeIndexCat === 'All' || card.dataset.cat === activeIndexCat;
        const textOk = !ql || card.dataset.name.includes(ql);
        card.style.display = (catOk && textOk) ? '' : 'none';
      });
    }

    function showPage(index) {
      if (index < 0) index = 0;
      if (index >= total) index = total - 1;
      currentIndex = index;
      document.querySelectorAll('.page-card').forEach(el => el.classList.remove('active'));
      const activeCard = document.getElementById('page-card-' + index);
      if (activeCard) activeCard.classList.add('active');
      document.getElementById('page-select').value = String(index);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    function changePage(delta) {
      if (currentIndex < 0) {
        showPage(delta > 0 ? 0 : total - 1);
      } else {
        showPage(currentIndex + delta);
      }
    }

    function jumpToPage(val) {
      if (val === 'landing') return showLanding();
      if (val === 'index') return showIndex();
      if (val === 'figures') return showFigures();
      showPage(parseInt(val, 10));
    }

    function filterText(q) {
      const raw = q.trim();
      const ql = raw.toLowerCase();
      const activeCard = document.getElementById('page-card-' + currentIndex);
      if (activeCard) {
        activeCard.querySelectorAll('tbody tr').forEach(tr => {
          tr.classList.remove('search-target-row');
          if (!ql) {
            tr.style.display = '';
          } else {
            const match = tr.textContent.toLowerCase().includes(ql);
            tr.style.display = match ? '' : 'none';
          }
        });
      }
      const statusEl = document.getElementById('search-status');
      if (!ql) {
        statusEl.textContent = '';
        return;
      }
      const idx = buildCorpusIndex();
      let hits = 0;
      for (let i = 0; i < idx.length; i++) {
        if (idx[i].combined.includes(ql)) hits++;
      }
      statusEl.textContent = hits + ' hits across edition';
    }

    function appendHighlighted(container, text, queryLower) {
      if (!queryLower) {
        container.textContent = text;
        return;
      }
      const lower = text.toLowerCase();
      let pos = 0;
      let matchIdx = lower.indexOf(queryLower, pos);
      while (matchIdx !== -1) {
        if (matchIdx > pos) {
          container.appendChild(document.createTextNode(text.slice(pos, matchIdx)));
        }
        const mark = document.createElement('mark');
        mark.textContent = text.slice(matchIdx, matchIdx + queryLower.length);
        container.appendChild(mark);
        pos = matchIdx + queryLower.length;
        matchIdx = lower.indexOf(queryLower, pos);
      }
      if (pos < text.length) {
        container.appendChild(document.createTextNode(text.slice(pos)));
      }
    }

    function renderCorpusResults(query) {
      const q = query.trim();
      const ql = q.toLowerCase();
      const metaEl = document.getElementById('search-dialog-meta');
      const listEl = document.getElementById('search-results-list');
      const dialog = document.getElementById('search-dialog');
      listEl.textContent = '';

      if (!ql) {
        metaEl.textContent = 'Type a German, English, or editorial term above to search across all ' + total + ' pages.';
        return;
      }

      const idx = buildCorpusIndex();
      const matches = [];
      const pageSet = new Set();
      for (let i = 0; i < idx.length; i++) {
        if (idx[i].combined.includes(ql)) {
          matches.push(idx[i]);
          pageSet.add(idx[i].pIdx);
        }
      }

      const maxShow = 300;
      const shown = matches.slice(0, maxShow);
      metaEl.textContent =
        matches.length === 0
          ? 'No matches found for "' + q + '" across ' + total + ' pages.'
          : 'Found ' + matches.length.toLocaleString() + ' matching lines across ' + pageSet.size + ' pages' +
            (matches.length > maxShow ? ' (showing first ' + maxShow + ').' : '.');

      const frag = document.createDocumentFragment();
      shown.forEach((m) => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'search-result-btn';

        const loc = document.createElement('div');
        loc.className = 'search-result-loc';
        loc.textContent = m.pageLabel + ' · Line ' + m.lineNum;

        const pair = document.createElement('div');
        pair.className = 'search-result-pair';

        const deDiv = document.createElement('div');
        appendHighlighted(deDiv, m.deText, ql);

        const enDiv = document.createElement('div');
        appendHighlighted(enDiv, m.enText, ql);

        pair.appendChild(deDiv);
        pair.appendChild(enDiv);
        btn.appendChild(loc);
        btn.appendChild(pair);

        btn.addEventListener('click', () => {
          dialog.close();
          showPage(m.pIdx);
          const activeCard = document.getElementById('page-card-' + m.pIdx);
          if (activeCard) {
            activeCard.querySelectorAll('tbody tr').forEach(tr => {
              tr.style.display = '';
              tr.classList.remove('search-target-row');
            });
          }
          m.tr.classList.add('search-target-row');
          m.tr.scrollIntoView({ behavior: 'smooth', block: 'center' });
        });

        frag.appendChild(btn);
      });
      listEl.appendChild(frag);
    }

    function openCorpusSearch(query) {
      const dialog = document.getElementById('search-dialog');
      const dInput = document.getElementById('dialog-search-input');
      dInput.value = query || '';
      renderCorpusResults(dInput.value);
      if (!dialog.open) dialog.showModal();
      dInput.focus();
    }

    const searchForm = document.getElementById('corpus-search-form');
    const searchInput = document.getElementById('filter-input');
    const dialogSearchForm = document.getElementById('dialog-search-form');
    const dialogSearchInput = document.getElementById('dialog-search-input');

    searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      openCorpusSearch(searchInput.value);
    });
    searchInput.addEventListener('keydown', (e) => {
      if (e.isComposing) return;
      if (e.key === 'Enter') {
        e.preventDefault();
        openCorpusSearch(searchInput.value);
      }
    });
    dialogSearchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      searchInput.value = dialogSearchInput.value;
      filterText(dialogSearchInput.value);
      renderCorpusResults(dialogSearchInput.value);
    });
    dialogSearchInput.addEventListener('input', () => {
      searchInput.value = dialogSearchInput.value;
      filterText(dialogSearchInput.value);
      renderCorpusResults(dialogSearchInput.value);
    });

    if (!('closedBy' in HTMLDialogElement.prototype)) {
      const outside = (e, dialog) => {
        const r = dialog.getBoundingClientRect();
        return e.clientX < r.left || e.clientX > r.right || e.clientY < r.top || e.clientY > r.bottom;
      };
      for (const dialog of document.querySelectorAll('dialog[closedby="any"]')) {
        let pressedOutside = false;
        dialog.addEventListener('pointerdown', (e) => { pressedOutside = outside(e, dialog); });
        dialog.addEventListener('pointerup', (e) => { if (pressedOutside && outside(e, dialog)) dialog.close(); });
      }
    }

    document.addEventListener('keydown', (e) => {
      if (document.getElementById('search-dialog').open) return;
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'SELECT') return;
      if (e.key === 'ArrowLeft') changePage(-1);
      if (e.key === 'ArrowRight') changePage(1);
    });
  </script>
</body>
</html>
"""
    HTML_OUT_FILE.write_text(html_content, encoding="utf-8")
    print(f"Generated {HTML_OUT_FILE} ({len(html_content):,} chars, {len(html_content.splitlines()):,} lines)")


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"Loaded {len(data['pages'])} pages from {DATA_FILE}")
    generate_markdown(data)
    generate_html(data)


if __name__ == "__main__":
    main()

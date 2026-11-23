#!/usr/bin/env python3
"""
Generates:
1. MS990_parallel_edition.md
   Scholarly text-only parallel edition.
2. MS990_parallel_edition_with_facsimiles.md
   Scholarly Markdown parallel edition with embedded high-resolution facsimile images.
3. MS990_parallel_edition_with_facsimiles.html
   Interactive, responsive parallel edition viewer with side-by-side facsimile inspection.
"""
import json
import re
from pathlib import Path
from build_parallel_with_facsimiles import generate_html

WORKSPACE_DIR = Path(__file__).resolve().parent
DATA_FILE = WORKSPACE_DIR / "MS990_edition_data.json"
OUT_FILE = WORKSPACE_DIR / "MS990_parallel_edition.md"
OUT_FACSIMILE_FILE = WORKSPACE_DIR / "MS990_parallel_edition_with_facsimiles.md"


def format_md_text(raw: str) -> str:
    if not raw:
        return ""
    s = raw.replace("|", "\\|")
    s = re.sub(r"\{rubric:\s*([^}]*)\}", r"**[Rubric] \1**", s)
    s = re.sub(r"\{del:\s*([^}]*)\}", r"~~\1~~", s)
    s = re.sub(r"\{add:\s*([^}]*)\}", r"‹\1›", s)
    return s


def build_front_matter(total_pages: int, total_lines: int, total_figs: int, page_min: str, page_max: str, with_images: bool = False) -> str:
    title_suffix = " with Embedded Facsimiles" if with_images else ""
    return f"""# Wellcome Collection MS.990 (*Arzneibuch*, c. 1675): Parallel German–English Critical Edition{title_suffix}

**Repository:** Wellcome Collection, London (Work ID: `ceuwj8kj` · Sierra ID: `b18775275` · Accession No.: `41913`)  
**IIIF Manifest (v3):** https://iiif.wellcomecollection.org/presentation/b18775275  
**Current Coverage:** {total_pages} Canvases (Canvases 2, 3, 7–135, and 723; {total_lines:,} transcribed lines and {total_figs} annotated figure zones; Pages {page_min} through {page_max})  
**Model Attribution:** Transcribed and encoded using Google Gemini 3.8 Flash and Gemini 4 models with structured validation.

---

## Summary of the Transcribed Corpus

This parallel edition presents {total_pages} digitized canvases of Wellcome Collection MS.990, a richly illustrated seventeenth-century German medical and surgical compendium (*Arzneibuch*). In its current state, the edition encompasses the documentary paratexts on the Front Pastedown (Canvas 2), Front Flyleaf 1r (Canvas 3), and 20th-century Binding Spine (Canvas 723), together with an unbroken continuous run of manuscript pages spanning `[p. 29]` through `p. 164` (Canvases 7–135, with early modern pagination jumping `30 → 32`, `55 → 60`, and `75 → 78` without textual loss, and including the four physical flap states of the eye dissection on `p. 48` linked to Canvases 727–730). 

Across these {total_lines:,} lines of Early New High German (*Frühneuhochdeutsch*), the text moves through:
1. **Household and Iatrochemical Remedies (`pp. [29]–30`):** Gravel, hematuria, plague waters, and compound decoctions.
2. **Head, Cervical, and Dental Surgery (`pp. 32–47`):** Scorbutic mouth ulcers, dentifrices, tooth extraction mechanics, parotid swellings (*Kropff* / *Päulen*), facial birthmarks, and goitre cures.
3. **The Ophthalmology Compendium (`pp. 48–164+`):**
   - **Anatomical plates and tunics of the eye (`pp. 48–51`):** Multi-layered fugitive sheet dissection.
   - **Cataract diagnostics and couching surgery (`pp. 73–74`):** Operative needles, post-operative bandages, and taffeta eye-shades.
   - **The ten post-couching complications (`pp. 74–82`):** Pain, ocular inflammation, intraocular hemorrhage, and suppuration.
   - **Lacrimal fistulae and trepanation (`pp. 82–88`):** Operative scenes of a Franciscan friar-surgeon operating on a nun, cautery irons, and bone drills for trephining the *os cribrum*.
   - **External ocular films, corneal burns, and pterygia (`pp. 89–99`):** Illustrated patient portraits `.A.` through `.E.`, ophthalmic hooks, and forceps.
   - **Ocular fluxes and catarrhs (`pp. 99–104`):** Hot and cold defluxions with Portrait `.F.` and brass distillation vessels.
   - **Traumatic eye injuries, chemical/lime burns, and severe defluxions (`pp. 105–122`):** Anti-inflammatory collyria, mucilages, and ocular poultices.
   - **Eyelid deformities, trichiasis, and blepharoplasty (`pp. 123–134`):** Surgical excision of inverted cilia, lid clamps, and suture techniques.
   - **Gutta Serena, amaurosis, and optic nerve paralysis (`pp. 135–164`):** Radical cephalic purgations, fontanelles, and vesicatory plasters.

## Historical Context and Provenance

Internal linguistic, pharmacological, and archival evidence places MS.990 squarely within an Austro-Bavarian Franciscan milieu around 1675. On Front Flyleaf 1r (Canvas 3), a penciled bookseller's note records that the Wellcome Historical Medical Library acquired the volume in 1922 (Accession No. `41913`) from the prominent Viennese antiquarian firm Gilhofer & Ranschburg. Within the text itself, the compiler provides a decisive geographic anchor on `p. 32` (Canvas 9), praising the newly imported South American resin *Balsam of Copaiba* (*Balsamo Copauia*, brought *auß India*) for the remarkable cures performed with it *in Wienn* (in Vienna). The dialectal phonology reinforces this Danubian-Bavarian origin, exhibiting characteristic Upper German features such as initial `kh-` for Standard German `k-` (*khochen*, *khrankh*, *Khröpff*), `p-` for `b-` (*präne*, *Päulen*), the retention of `ai/aÿ` and `eu/eü`, and regional lexical items including *Krenwurzel* (horseradish), *Schlier* (abscess/bubo), and *Sumer fleckh* (freckles).

As a monastic *Arzneibuch*, the manuscript reflects the eclectic medical pluralism of Counter-Reformation Central Europe, where Franciscan infirmarians and lay practitioners mediated between academic Galenic humoralism, Paracelsian chemical pharmacy, and vernacular empirical medicine. Alongside standard herbal simples, the compiler prescribes mineral and metallic preparations—white lead acetate (*bleÿ Zukher* / *Sachari ♄*), mercuric sublimate, vitriol (*🜖*), alum (*🜘*), and antimony (*♁*)—as well as New World imports like guaiacum and copaiba. At the same time, the text retains a strong charitable and practical orientation: on `p. 32`, for instance, after detailing costly compound washes for scorbutic mouth ulcers, the scribe adds an explicit pauper's alternative (*arme leüd die nichts Vermögen*) made from locally gathered watercress, scurvy-grass, and horseradish.

## Critical Review and Paleographic Assessment

Codicologically, MS.990 survives in a mutilated yet remarkably legible state. The first twenty-eight pages are lost, so the main text begins abruptly mid-sentence at the top of `[p. 29]` (Canvas 7), which is unnumbered and precedes `p. 30` (Canvas 8). A quirk of early modern pagination occurs immediately thereafter: `p. 30` on the verso faces `p. 32` on the facing recto (Canvas 9), omitting the number `31` without any loss of textual continuity. The main body is laid out in neat double columns framed by double red rules with a central red vertical divider, shifting to a full-width single-column format on `p. 49` (Canvas 26) to accommodate the denser theoretical exposition of ocular anatomy. The script is a disciplined seventeenth-century German *Kurrentschrift* written in iron-gall ink, punctuated by vivid red-ink rubrics for recipe titles and Latin pharmaceutical terms written in humanist *Antiqua*.

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


def render_edition(data: dict, with_images: bool = False) -> str:
    pages = data["pages"]
    total_pages = len(pages)
    total_lines = sum(len(c["lines"]) for p in pages for c in p["columns"])
    total_figs = sum(len(p.get("figures", [])) for p in pages)
    numbered = [p["orig_page"] for p in pages if p["orig_page"] not in ["Front Pastedown", "Flyleaf 1r", "Spine"]]
    page_min = numbered[0] if numbered else "[29]"
    page_max = numbered[-1] if numbered else "164"

    out_parts = [build_front_matter(total_pages, total_lines, total_figs, page_min, page_max, with_images)]

    for p in pages:
        cnum = p["canvas_num"]
        orig_p = p["orig_page"]
        jp2 = p["jp2"]
        fside = p.get("folio_side", "")
        w = p.get("width", "")
        h = p.get("height", "")
        canvas_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        img_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/full/0/default.jpg"
        iiif_1200_uri = f"https://iiif.wellcomecollection.org/image/{jp2}/full/1200,/0/default.jpg"
        local_img = f"canvas_{cnum:04d}.jpg"

        out_parts.append(f"## Page {orig_p} — IIIF Canvas #{cnum}\n\n")
        meta_bits = [f"**Folio / Side:** {fside}", f"**Image:** `{jp2}` ({w} × {h} px)", f"[IIIF Canvas]({canvas_uri})", f"[Full-Resolution Image]({img_uri})"]
        if p.get("model"):
            meta_bits.append(f"**Transcription Model:** {p['model']}")
        if p.get("input_tokens") is not None and p.get("output_tokens") is not None:
            meta_bits.append(f"**Tokens (In / Out):** {p['input_tokens']:,} / {p['output_tokens']:,}")
        out_parts.append(" · ".join(meta_bits) + "\n\n")

        if with_images:
            img_block = (
                f"<p align=\"center\" style=\"margin: 1.5rem 0;\">\n"
                f"  <a href=\"{img_uri}\" target=\"_blank\" title=\"Click to view original full-resolution IIIF facsimile\">\n"
                f"    <img src=\"{local_img}\" alt=\"Facsimile: Wellcome MS.990 Canvas #{cnum} (Page {orig_p})\" style=\"max-height: 720px; max-width: 100%; border: 1px solid #c5bba8; border-radius: 6px; box-shadow: 0 4px 12px rgba(0,0,0,0.15);\" onerror=\"this.onerror=null; this.src='{iiif_1200_uri}';\" />\n"
                f"  </a>\n"
                f"  <br>\n"
                f"  <em>Facsimile: Canvas #{cnum} ({fside}, Page {orig_p}) · <a href=\"{img_uri}\" target=\"_blank\">View Full-Resolution IIIF</a></em>\n"
                f"</p>\n\n"
            )
            out_parts.append(img_block)

        if p.get("summary"):
            out_parts.append(f"{p['summary']}\n\n")

        figs = p.get("figures", [])
        if figs:
            out_parts.append("### Illustrations and Anatomical Diagrams\n\n")
            for fig in figs:
                xywh = f"{fig['ulx']},{fig['uly']},{fig['lrx']-fig['ulx']},{fig['lry']-fig['uly']}"
                out_parts.append(f"**{fig['label']}** (`#xywh={xywh}`): {fig['desc']}\n\n")

        for col in p["columns"]:
            col_label = col.get("col_label", "Text")
            out_parts.append(f"### {col_label}\n\n")
            out_parts.append("| Line | German Diplomatic (Original) | English Translation & Editorial Notes |\n")
            out_parts.append("| :---: | :--- | :--- |\n")
            for ln in col["lines"]:
                lnum = ln["line_num"]
                de_txt = format_md_text(ln.get("de", ""))
                en_txt = format_md_text(ln.get("en", ""))
                note_txt = format_md_text(ln.get("note") or "")
                if note_txt:
                    en_cell = f"{en_txt} *— Note: {note_txt}*"
                else:
                    en_cell = en_txt
                out_parts.append(f"| {lnum} | {de_txt} | {en_cell} |\n")
            out_parts.append("\n")

        out_parts.append("---\n\n")

    return "".join(out_parts)


def main():
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Standard parallel text edition
    content_text = render_edition(data, with_images=False)
    OUT_FILE.write_text(content_text, encoding="utf-8")
    print(f"Wrote text edition: {OUT_FILE} ({len(content_text):,} chars, {len(content_text.splitlines()):,} lines)")

    # 2. Parallel edition with embedded facsimiles
    content_facsimiles = render_edition(data, with_images=True)
    OUT_FACSIMILE_FILE.write_text(content_facsimiles, encoding="utf-8")
    print(f"Wrote facsimile edition: {OUT_FACSIMILE_FILE} ({len(content_facsimiles):,} chars, {len(content_facsimiles.splitlines()):,} lines)")

    # 3. Interactive HTML parallel edition
    generate_html(data)


if __name__ == "__main__":
    main()

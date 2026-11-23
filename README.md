# Wellcome Collection MS.990 — Digital Diplomatic Edition & English Translation

A complete digital diplomatic transcription, English translation, TEI P5 XML edition, and parallel German–English edition for **Wellcome Collection MS.990** (*Compendium of Medicine and Surgery*, compiled in or after **July 1696** by **Frater Bernardin, OFMCap**, a Capuchin lay-brother surgeon-apothecary at *"the old friary in the city"* of **Graz, Styria**; previously catalogued anonymously as *ca. 1650–1680, Franciscan Order*), derived from the Wellcome IIIF digitisation (`b18775275`).

## Browse the Parallel Editions & Historical Study Online
- **Parallel German–English Facsimile Edition (GitHub Pages):** https://setacmj.github.io/MS990/ — includes an **Overview** landing page with 14 illustrated highlights, an interactive **Historical Study** tab detailing the discovery of Frater Bernardin, the July 1696 dating, printed precedents, and eyewitness paintings of the Graz Capuchin *Klosterapotheke*, cross-edition full-text search across all 741 pages, a Wikidata-linked **Index** of 110 ingredients, people, places, and terms, and a **Figures & Diagrams (385)** gallery with IIIF `pct:` region crops.
- **Historical Provenance, Authorship & Printed Sources Study:** [MS990_Historical_Sources_and_Research_Study.md](MS990_Historical_Sources_and_Research_Study.md)
- **Parallel German–English Markdown (Browsable in GitHub):** [editions/parallel/README.md](editions/parallel/README.md) (split into 25 ~30-page sections so every page renders directly inside GitHub's web viewer)
- **Methodology, Consistency Audit & Textual Summary:** [MS990_Methodology_and_Corpus_Review.md](MS990_Methodology_and_Corpus_Review.md)

## Downloadable Full-Corpus Files
GitHub's web UI does not render individual Markdown/HTML/XML files larger than ~512 KB–1 MB, so the full monolithic files are provided for download or local use:
- **TEI P5 XML Edition:** `MS990_tei.xml` (741 pages, 55,875 aligned German/English lines, 189,488 lines of validated TEI XML)
- **Structured JSON Dataset (63 MB):** Attached to [Release v1.0.0](https://github.com/setacmj/MS990/releases/tag/v1.0.0) (`MS990_edition_data.json`)
- **Monolithic Parallel & Monolingual Editions:** `MS990_parallel_edition.md`, `MS990_parallel_edition_with_facsimiles.md`, `MS990_parallel_edition_with_facsimiles.html`, `MS990_transcription.txt/.md`, and `MS990_translation.txt/.md`
- **Build Pipeline:** `generate_edition_outputs.py`, `build_parallel_md.py`, `build_parallel_with_facsimiles.py`, `extract_iiif_structure.py`, and batch modules `pages_batch2.py`–`pages_batch28.py`

## Note on Facsimile Images
Local facsimile JPEGs (`*.jpg`, `images/`) are excluded from Git; the HTML and Markdown editions automatically resolve images via Wellcome Collection's public IIIF endpoints.

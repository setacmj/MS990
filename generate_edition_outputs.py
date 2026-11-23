#!/usr/bin/env python3
"""
Generates the 3 IIIF-anchored scholarly outputs for Wellcome Collection MS.990 (ceuwj8kj / b18775275):
  1. MS990_transcription.txt (and .md) — Exact Diplomatic Transcription with IIIF #xywh coordinates
  2. MS990_tei.xml                     — TEI P5 XML Edition with <facsimile>, <charDecl>, <surface>/<zone> coordinates
  3. MS990_translation.txt (and .md)   — Line-by-Line Aligned English Translation with IIIF #xywh coordinates
"""
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from pages_batch2 import PAGES_BATCH2
from pages_batch3 import PAGES_BATCH3
from pages_batch4 import PAGES_BATCH4
from pages_batch5 import PAGES_BATCH5
from pages_batch6 import PAGES_BATCH6
from pages_batch7 import PAGES_BATCH7
from pages_batch8 import PAGES_BATCH8
from pages_batch9 import PAGES_BATCH9
from pages_batch10 import PAGES_BATCH10
from pages_batch11 import PAGES_BATCH11
from pages_batch12 import PAGES_BATCH12
from pages_batch13 import PAGES_BATCH13
from pages_batch14 import PAGES_BATCH14
from pages_batch15 import PAGES_BATCH15
from pages_batch16 import PAGES_BATCH16
from pages_batch17 import PAGES_BATCH17
from pages_batch18 import PAGES_BATCH18
from pages_batch19 import PAGES_BATCH19
from pages_batch20 import PAGES_BATCH20
from pages_batch21 import PAGES_BATCH21
from pages_batch22 import PAGES_BATCH22
from pages_batch23 import PAGES_BATCH23
from pages_batch24 import PAGES_BATCH24
from pages_batch25 import PAGES_BATCH25
from pages_batch26 import PAGES_BATCH26
from pages_batch27 import PAGES_BATCH27
from pages_batch28 import PAGES_BATCH28

OUT_DIR = Path(__file__).resolve().parent

IIIF_MANIFEST_V2 = "https://iiif.wellcomecollection.org/presentation/v2/b18775275"
IIIF_MANIFEST_V3 = "https://iiif.wellcomecollection.org/presentation/b18775275"
WORK_URL = "https://wellcomecollection.org/works/ceuwj8kj/items"

# Complete table of alchemical, planetary, and apothecary glyphs in MS.990
GLYPH_TABLE = [
    ("rx", "℞", "U+211E", "Recipe", "Nimm / Recipe (Take)"),
    ("aqua", "▽", "U+25BD", "Aqua / Wasser", "Wasser (Water)"),
    ("vinum", "V̈", "U+0056 U+0308", "Vinum / Wein", "Wein (Wine — scribal V with supralinear two-dot flourish)"),
    ("acetum", "✚", "U+271A", "Acetum / Essig", "Essig (Vinegar — cruciform glyph)"),
    ("sal", "🜔", "U+1F714", "Sal / Salz", "Salz (Salt — circle bisected by horizontal bar)"),
    ("salzwasser", "🜔▽", "U+1F714 U+25BD", "Aqua salis / Salzwasser", "Salzwasser (Brine / Salt water)"),
    ("pulvis", "ꝑll̵", "U+A751 U+006C U+006C U+0335", "Pulvis / Pulver", "Pulver (Powder — loop p/o with crossed double-l)"),
    ("calx", "✗", "U+2717", "Calx / Kalk / Pulver", "Kalk / gebranntes Pulver (Calcined powder / Lime)"),
    ("urina", "⊡", "U+22A1", "Urina / Harn", "Harn / Urin (Urine — square with central dot)"),
    ("sol", "☉", "U+2609", "Sol / Sonne / Gold", "Sonne / Gold (Sun / Gold)"),
    ("mercurius", "☿", "U+263F", "Mercurius / Quecksilber", "Quecksilber / Mercurius (Mercury)"),
    ("antimonium", "♁", "U+2641", "Antimonium / Spießglas", "Antimonium / Spießglas (Antimony)"),
    ("vitriolum", "🜖", "U+1F716", "Vitriolum / Vitriol", "Vitriol (Sulfate of iron/copper)"),
    ("alumen", "🜘", "U+1F718", "Alumen / Alaun", "Alaun (Alum — astringent potassium aluminum sulfate)"),
    ("nitrum", "🜕", "U+1F715", "Nitrum / Salpeter", "Salpeter (Nitre / Potassium nitrate — circle bisected by vertical bar)"),
    ("saturnus", "♄", "U+2644", "Saturnus / Blei", "Blei / Saturnus (Lead — e.g. 🜔 ♄ Sal Saturni, Sachari ♄ = lead acetate)"),
    ("camphora", "XXX", "U+0058x3", "Camphora / Kampfer", "Kampfer (Camphor — scribal triple-X cipher in dental anodynes)"),
    ("ignis", "△", "U+25B3", "Ignis / Feuer", "Feuer (Fire)"),
    ("libra", "℔", "U+2114", "Libra / Pfund", "Pfund (Apothecary pound, ~12 oz)"),
    ("uncia", "℥", "U+2125", "Uncia / Unze", "Unze (Apothecary ounce, 8 drachms)"),
    ("drachma", "ℨ", "U+2128", "Drachma / Quintlein", "Drachme / Quintlein (Apothecary drachm, 3 scruples)"),
    ("scrupulus", "℈", "U+2108", "Scrupulus / Skrupel", "Skrupel (Apothecary scruple, 20 grains)"),
    ("semis", "ß", "U+00DF", "Semis / halb", "Halb (Half unit, e.g. ℥iß = 1½ ounces)"),
]

# Calibrated helper to generate line bounding boxes within a column/block zone
def make_lines(prefix, canvas_num, col_id, ulx, uly, lrx, lry, line_tuples):
    n = len(line_tuples)
    step = (lry - uly) / max(1, n)
    img_svc = f"https://iiif.wellcomecollection.org/image/b18775275_MS_990_{canvas_num:04d}.JP2"
    canvas_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/b18775275_MS_990_{canvas_num:04d}.JP2"
    out = []
    for idx, (lno, ltype, de_text, en_text, note) in enumerate(line_tuples):
        y0 = int(round(uly + idx * step))
        y1 = int(round(uly + (idx + 1) * step))
        w = lrx - ulx
        h = y1 - y0
        xywh = f"{ulx},{y0},{w},{h}"
        line_id = f"{prefix}_{col_id}_l{lno:02d}" if isinstance(lno, int) else f"{prefix}_{col_id}_{lno}"
        out.append({
            "line_id": line_id,
            "line_num": str(lno),
            "line_type": ltype,  # "rubric", "line", "mixed", "caption", "fw"
            "ulx": ulx,
            "uly": y0,
            "lrx": lrx,
            "lry": y1,
            "xywh": xywh,
            "iiif_canvas_xywh": f"{canvas_uri}#xywh={xywh}",
            "iiif_image_crop": f"{img_svc}/{xywh}/800,/0/default.jpg",
            "de": de_text,
            "en": en_text,
            "note": note,
        })
    return out


# ==============================================================================
# STRUCTURED MANUSCRIPT DATA ANCHORED TO WELLCOME IIIF CANVASES
# ==============================================================================

PAGES = [
    # --------------------------------------------------------------------------
    # 1. CANVAS 2: Inside Front Cover / Pastedown (b18775275_MS_990_0002.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0002_pastedown",
        "canvas_num": 2,
        "jp2": "b18775275_MS_990_0002.JP2",
        "orig_page": "Front Pastedown",
        "folio_side": "verso (inside front board)",
        "width": 5508,
        "height": 6853,
        "frame_box": (275, 220, 5120, 6610),
        "summary": "Inside front cover pastedown containing modern pencil cataloguing inscription (identifying MS. 990 as an Austro-Bavarian Franciscan medical and surgical compendium, c. 1675) and the pasted bookplate of the Wellcome Historical Medical Library (Accession No. 41913).",
        "figures": [
            {
                "fig_id": "fig_c0002_bookplate",
                "label": "Wellcome Historical Medical Library Bookplate (Acc. 41913, MS.990)",
                "ulx": 620, "uly": 2880, "lrx": 2920, "lry": 6350,
                "desc": "Printed red-and-black heraldic ex-libris of the Wellcome Historical Medical Library with manuscript blue-ink accession number '41913' and shelfmark 'MS.990'.",
            }
        ],
        "columns": [
            {
                "col_id": "inscription",
                "col_label": "Upper Pastedown Pencil Inscription",
                "ulx": 1150, "uly": 520, "lrx": 4560, "lry": 2860,
                "lines": make_lines("c0002", 2, "ins", 1150, 520, 4560, 2860, [
                    (1, "fw", "767 = MS 990", "767 = MS 990", "Former shelfmark 767 equated to Wellcome MS.990."),
                    (2, "line", "[ME] ARZNEIBUCH", "[ME] PHARMACOPOEIA / MEDICAL COMPENDIUM [Arzneibuch]", "Faint erased 'ME' before capital pencil title 'ARZNEIBUCH'."),
                    (3, "line", "Compendium of medicine and surgery.", "Compendium of medicine and surgery.", "20th-century English cataloguer's hand (pencil)."),
                    (4, "line", "Compiled for the use of a Community", "Compiled for the use of a Community", None),
                    (5, "line", "of the Franciscan Order probably in", "of the Franciscan Order probably in", None),
                    (6, "line", "Austria or South Germany", "Austria or South Germany", None),
                    (7, "line", "[c. 1675]", "[c. 1675]", "Estimated date of compilation."),
                ]),
            },
            {
                "col_id": "bookplate",
                "col_label": "Wellcome Bookplate Text (Lower Left)",
                "ulx": 1200, "uly": 3600, "lrx": 2400, "lry": 5600,
                "lines": make_lines("c0002", 2, "bkp", 1200, 3600, 2400, 5600, [
                    (8, "fw", "WELLCOME HISTORICAL MEDICAL LIBRARY", "WELLCOME HISTORICAL MEDICAL LIBRARY", "Printed in red ink around emblem."),
                    (9, "fw", "ACCESSION NUMBER 41913", "ACCESSION NUMBER 41913", "41913 in blue ink."),
                    (10, "fw", "PRESS MARK MS. 990", "PRESS MARK MS. 990", "MS. 990 in blue ink."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 2. CANVAS 3: Flyleaf 1r (b18775275_MS_990_0003.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0003_flyleaf1r",
        "canvas_num": 3,
        "jp2": "b18775275_MS_990_0003.JP2",
        "orig_page": "Flyleaf 1r",
        "folio_side": "recto",
        "width": 5292,
        "height": 6853,
        "frame_box": (360, 240, 5090, 6610),
        "summary": "First front flyleaf recto recording the 1922 purchase provenance from the Viennese antiquarian booksellers Gilhofer & Ranschburg and the Wellcome accession number 41913.",
        "figures": [],
        "columns": [
            {
                "col_id": "provenance",
                "col_label": "Diagonal Pencil Provenance Note & Accession Stamp",
                "ulx": 1120, "uly": 380, "lrx": 4820, "lry": 1920,
                "lines": make_lines("c0003", 3, "prov", 1120, 380, 4820, 1920, [
                    (1, "fw", "41913", "41913", "Upper right corner in pencil, underlined."),
                    (2, "line", "Gilhofer & Ranschburg", "Gilhofer & Ranschburg", "Antiquarian booksellers at Bognergasse 2, Vienna."),
                    (3, "line", "Vienna", "Vienna", None),
                    (4, "line", "600 Swi[ss] fr. £24 [struck through]", "600 Swiss francs / £24 [struck through]", "Purchase price note from the 1922 acquisition."),
                    (5, "line", "[44177?] 100?", "[44177?] 100?", "Stock/inventory cipher."),
                ]),
            }
        ],
    },

    # --------------------------------------------------------------------------
    # 3. CANVAS 7: [Page 29] — First Extant Compendium Leaf (b18775275_MS_990_0007.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0007_p29",
        "canvas_num": 7,
        "jp2": "b18775275_MS_990_0007.JP2",
        "orig_page": "[29]",
        "folio_side": "recto",
        "width": 5012,
        "height": 6853,
        "frame_box": (240, 314, 4777, 6464),
        "center_rule_x": 2656,
        "summary": "First extant text page of the Arzneibuch ([p. 29], recto preceding p. 30; pages 1–28 wanting). Written in double column within red rules with red rubrics. Contains iatrochemical and folk-medical recipes using eggshells (for urinary calculus, hemorrhage, proud flesh), chimney soot (for cancer and plague anthrax), and sourdough bread (pharmacological properties, maturing poultice, febrile headache, inflamed eyes, post-febrile halitosis, and sustaining life by the aroma of bread).",
        "figures": [],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=240..2656, Y=314..6464)",
                "ulx": 240, "uly": 314, "lrx": 2656, "lry": 6464,
                "lines": make_lines("p29", 7, "colA", 240, 314, 2656, 6464, [
                    (1, "rubric", "{rubric: Für Sandt vnd stain.}", "{rubric: For sand and stone [urinary gravel and calculus].}", "Red rubric; upper right margin of col. A slightly abraded."),
                    (2, "line", "℞ die aierschallen Von denen Jungen außgebro=", "Take [℞] the eggshells from which young chicks have hatched", "℞ = Recipe."),
                    (3, "line", "chenen hienlen, das weiche weise häutl thüe", "out, remove the soft white inner membrane,", "hienlen = Hühnlein (chicks); häutl = Häutlein."),
                    (4, "line", "hin wekh mach die schallen zu ꝑll̵ [Pulver], vnd nimb ℨj", "make the shells into powder [ꝑll̵], and take 1 drachm [ℨj]", "ꝑll̵ = Pulver (powder); ℨj = 1 drachm."),
                    (5, "line", "in V̈ [Wein], ist ein khöstliches mitl wider den sandt", "in wine [V̈]; it is a precious remedy against sand,", "V̈ = Vinum / Wein."),
                    (6, "line", "stain vnd verstopfften ⊡ [Harn].", "stone, and obstructed urine [⊡].", "⊡ = Urina / Harn (strangury / urinary retention)."),
                    (7, "line", "andere Nemen ein Jede aierschallen vnd richten sÿe", "Others take any eggshell and strip out", None),
                    (8, "line", "das weisse auß.", "the white [inner lining] from it.", None),
                    (9, "rubric", "{rubric: Blüett stöllen.}", "{rubric: To staunch blood [Hemostasis].}", "Red rubric."),
                    (10, "line", "℞. waiche aierschallen in ✚ [Essig] biß sÿe waich", "Take [℞] and soak eggshells in vinegar [✚] until they become", "✚ = Acetum / Essig (vinegar)."),
                    (11, "line", "werden, hernach drikhnes an der ☉ [Sonne] vnd machs", "soft; afterwards dry them in the sun [☉] and make them", "☉ = Sol / Sonne."),
                    (12, "line", "zu ꝑll̵ [Pulver], vnd sträe es auf ein blüett fluß, es", "into powder [ꝑll̵], and strew it upon a hemorrhage, wherever", None),
                    (13, "line", "seÿ wo es will, so stilt es von stund an.", "it may be, and it staunches it immediately.", "von stund an = instantaneously."),
                    (14, "line", "die schallen allein zu ✗ [Kalk/Pulver] gemacht, vnd auf die", "The shells alone calcined to powder [✗] and strewed upon", "✗ = calcined powder / lime."),
                    (15, "line", "fliesente gulden ader gesträet so stehts.", "bleeding hemorrhoids [fließende goldene Ader] stops the flow.", "gulden ader = vena aurea (hemorrhoidal vein)."),
                    (16, "line", "Zu dem erhizten Mänlichen glidt, khoche aier", "For the inflamed male member, boil egg-", None),
                    (17, "line", "schallen vnd lehm in guetten weisen V̈ [Wein], vnd bahe", "shells and clay in good white wine [V̈], and foment", "bahe = bathe/foment (warm compress)."),
                    (18, "line", "dich darmit so wirst wunder erfahren.", "yourself therewith, and you will experience wonders.", None),
                    (19, "mixed", "{rubric: Özen.} Präne aierschallen in offen das sÿe weis", "{rubric: Cauterizing [Escharotic].} Burn eggshells in the furnace until they turn", "Inline red rubric 'Özen' (= Ätzen)."),
                    (20, "line", "werden, dises ꝑll̵ [Pulver] dient zum özen das", "white; this powder [ꝑll̵] serves for eating away", "Quicklime (CaO) produced by calcining eggshells."),
                    (21, "line", "wilde fleisch.", "proud flesh [exuberant granulation tissue].", "wildes Fleisch = caro luxurians."),
                    (22, "rubric", "{rubric: Für den khrebs —}", "{rubric: For cancer [ulcerated carcinoma / phagedenic ulcer] —}", "Red rubric."),
                    (23, "line", "℞ ruess auß dem rauchfang, wain leger", "Take [℞] soot out of the chimney, wine-lees,", "wain leger = Weinleger (wine lees / tartar)."),
                    (24, "line", "Eisen rost, gaiss khääß, mach auß allen ein", "iron rust, [and] goat's cheese; make out of them all a", None),
                    (25, "line", "Pflaster legs über den khrebs 48 stundt,", "plaster, lay it over the cancer for 48 hours,", None),
                    (26, "line", "so stirbt der khrebs, oder wenigist halt", "and the cancer dies, or at the very least one", None),
                    (27, "line", "man ihn darmit auf, vnd benimbt ihm", "arrests it therewith and deprives it of", None),
                    (28, "line", "sein bosshait. {add: volgentes}", "its malignancy. {add: the following}", "'volgentes' added supralinearly above 'obgemeltes' in l. 29."),
                    (29, "mixed", "{rubric: Pöß.} in der Pöß, ist {del: obgemeltes} Pflaster", "{rubric: Plague.} In the plague, {del: the aforesaid} {add: the following} plaster is", "Inline red rubric 'Pöß.' (= Pest); 'obgemeltes' struck through."),
                    (30, "line", "ein hörliches mitl für den antrax, Nimb", "a glorious remedy for the carbuncle [anthrax]: Take", "antrax = plague carbuncle / bubo."),
                    (31, "line", "den härten ruess auß den Camin, ℥x.", "the hard soot out of the chimney, 10 ounces [℥x],", None),
                    (32, "line", "Saur daig, Therpentin, vnd Putter āā ℥j.", "sourdough, turpentine, and butter, of each 1 ounce [āā ℥j],", "āā = ana (of each an equal quantity)."),
                    (33, "line", "Venedische saiffen ℥iß., 3 aier dotter.", "Venetian soap 1½ ounces [℥iß], 3 egg yolks,", None),
                    (34, "line", "Theriac, Medridat, āā ℨij. stoss in Morser", "theriac [and] mithridatium, of each 2 drachms [āā ℨij]; pound in a mortar", "Classic alexipharmic electuaries."),
                    (35, "line", "wider ein ander zu einen Pflaster.", "together into a plaster.", None),
                    (36, "rubric", "{rubric: Saur daig khrafft —}", "{rubric: Virtue of sourdough —}", "Red rubric."),
                    (37, "line", "der saur daig hat ein vermischte aigenschafft", "Sourdough possesses a mixed [galenic] quality", None),
                    (38, "line", "einer Temperierten wärme vnd zu khielen:", "of a temperate warmth and of cooling,", None),
                    (39, "line", "also das er nit zu vill khielt vnd nit zu vill", "such that it neither cools too much nor heats", None),
                    (40, "line", "wärmet. er resoluieret, zeittiget, auch zu er", "too much; it resolves, ripens [matures], and also [serves] to", "Continues across column break to col. B, l. 1 ('waichen'). Quire mark '2.' below."),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B (Right Column, within red rules X=2656..4777, Y=314..6464)",
                "ulx": 2656, "uly": 314, "lrx": 4777, "lry": 6464,
                "lines": make_lines("p29", 7, "colB", 2656, 314, 4777, 6464, [
                    (1, "line", "waichen, Saur daig mit geschmalznen", "soften [emolliate]. Sourdough mixed with lard/greased", "Completes 'zu er-waichen' from col. A, l. 40."),
                    (2, "line", "öl vermischt, gibt ein guettes maturier", "oil yields a good maturating [suppurative]", None),
                    (3, "line", "Sälbel. Saur daig in Prandt wein ver=", "ointment. Sourdough mixed in brandy [aqua vitae]", "Prandt wein = Branntwein."),
                    (4, "line", "mischt vnd über geschlagen stillet alle schmer=", "and applied as a poultice relieves all pains", None),
                    (5, "line", "zen von khälte her khumen.", "that arise from cold.", None),
                    (6, "mixed", "{rubric: Haubtwehe.} in hizigen fiebern vnd andern", "{rubric: Headache.} In ardent fevers and other", "Inline red rubric 'Haubtwehe.'"),
                    (7, "line", "khrankheiten wo grose haubt wehe seindt", "illnesses where there are severe headaches,", None),
                    (8, "line", "wie auch in der gelbsucht, nimb saur daig", "as also in jaundice, take sourdough,", None),
                    (9, "line", "℥v, oder 6, stöss khrenns wurzel ꝑll̵ [Pulver] ℨv", "5 or 6 ounces [℥v–vj], pound horseradish root powder [ꝑll̵] 5 drachms [ℨv],", "khrenns wurzel = Krenwurzel (Armoracia rusticana, rubefacient)."),
                    (10, "line", "holler Essig, oder andern ✚ [Essig] zu einen", "elder-vinegar, or other vinegar [✚], made into a", "holler Essig = Sambucus nigra vinegar."),
                    (11, "line", "muess gemacht, wasche dem khrankhen vor=", "poultice-mash; first wash the patient's", None),
                    (12, "line", "hero die füess woll mit warmen V̈ [Wein], oder", "feet well with warm wine [V̈], or", "Note direct contrast between V̈ (wine) and 🜔▽ (salt water)."),
                    (13, "line", "🜔▽ [Salzwasser], als dan legs über, vnd so es drukhen", "salt water [🜔▽], then apply it [to the soles], and when it dries", "Galenic revulsive cataplasm to draw humors down from the head."),
                    (14, "line", "legs wider umb über.", "apply it afresh.", None),
                    (15, "line", "Saur daig mit 🜔 [Salz] vnd öl vermischt, waichet", "Sourdough mixed with salt [🜔] and oil softens", None),
                    (16, "line", "die Pestilenzische Blattern, vnd harte", "pestilential pustules and hard", None),
                    (17, "line", "Päulen, vnd öffnets baldt.", "boils [buboes], and opens them quickly.", "Päulen = Beulen."),
                    (18, "line", "Saur daig mit scharffer laugen vermischt", "Sourdough mixed with sharp lye", None),
                    (19, "line", "vnd über faulle löcher gelegt, zicht alle", "and laid over putrid ulcers draws out all", None),
                    (20, "line", "vnrainigkhait herauß.", "impurity.", None),
                    (21, "mixed", "{rubric: Erhizte augen.} ℞. Prot von rokhen", "{rubric: Inflamed eyes.} Take [℞] bread of rye", "Inline red rubric 'Erhizte augen.'"),
                    (22, "line", "oder waizen, waiche es in rosen ▽ [Wasser],", "or wheat, steep it in rose-water [▽] [and]", None),
                    (23, "line", "frische milch, biß woll angesogen, drukh", "fresh milk until well soaked, press it", None),
                    (24, "line", "ein wenig auß, vnd bindts über die erhizten", "out a little, and bind it over the inflamed", None),
                    (25, "line", "augen.", "eyes.", None),
                    (26, "rubric", "{rubric: Stinkhenten Mund nach einer khrankheit}", "{rubric: Fetid breath [halitosis] after an illness}", "Red rubric."),
                    (27, "line", "Wan nach einen fieber od[er] andern khrank=", "When after a fever or other illness", None),
                    (28, "line", "heit, der mund schmäkht, so Nimb khalte", "the mouth smells foul, take cold", "Austro-Bavarian 'schmäkht' = smells/stinks."),
                    (29, "line", "Prun ▽ [Wasser] halbe voll, lege darein rokhen", "spring-water [▽] half full, lay rye", None),
                    (30, "line", "Prodt, vnd Esse es darauß, souill er mag", "bread therein, and let him eat thereof as much as he can;", None),
                    (31, "line", "thue es 3 tag nach ein ander nüchter,", "do this for 3 days in succession fasting,", None),
                    (32, "line", "wird der mund woll riechendt werden", "and the mouth will become sweet-smelling.", None),
                    (33, "line", "Welliche khrankhe sehr Verzehrt vnd nit Essen", "Those patients who are greatly wasted and cannot", None),
                    (34, "line", "khünen, sollen an frischen Prodt offter mal", "eat should frequently smell fresh bread;", None),
                    (35, "line", "riechen, es erhalt den Menschen Natirlicher", "it naturally sustains a person", None),
                    (36, "line", "weiss ein Zeit lang beÿ dem leben, wie", "alive for a time, just as", None),
                    (37, "line", "dan einer 3 Jahr [Tag] sein leben also erhalten", "one man thus preserved his life for 3 years [days];", "Allusion to Democritus sustaining life for 3 days by the smell of hot bread."),
                    (38, "line", "andere legens in Maluasier geweikht", "others lay it steeped in Malmsey wine", "Maluasier = Malvasia wine."),
                    (39, "line", "aufs herz. der stotts gersten Prodt Ißet", "upon the heart. Whoever constantly eats barley bread", None),
                    (40, "line", "Soll Von Podagra vnd dergleichen füessen", "shall be freed from podagra [gout] and similar", None),
                    (41, "line", "khrankheiten befreiet sein —", "diseases of the feet —", None),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 4. CANVAS 8: Page 30 — First Numbered Page (b18775275_MS_990_0008.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0008_p30",
        "canvas_num": 8,
        "jp2": "b18775275_MS_990_0008.JP2",
        "orig_page": "30",
        "folio_side": "verso",
        "width": 5425,
        "height": 6853,
        "frame_box": (575, 274, 5157, 6498),
        "center_rule_x": 2776,
        "summary": "Page 30 (verso, numbered '30' in upper-left margin; first numbered page cited in Wellcome catalogue 'pages 30-790'). Contains recipes for colic (Grimen), stiffening of the nerves (Nerven Erstarrung), pleurisy (Seiden stechen), plague prophylaxis (Pöß), the folk pediatric 'heart-worm or goat-worm' tested via a live gudgeon fish bound to the navel (Gaiß Würm den khindern), joint-water discharge (Glidt Wasser), consumption (Dörsucht / Dörsichtigen), snail oil for wasted limbs (Schwinden der glider), cough and hemoptysis (Hüesten vnd außwurff), and plague/poisoned wounds.",
        "figures": [],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=575..2776, Y=274..6498)",
                "ulx": 575, "uly": 274, "lrx": 2776, "lry": 6498,
                "lines": make_lines("p30", 8, "colA", 575, 274, 2776, 6498, [
                    (1, "mixed", "[30 |] {rubric: Grimen.} Nime ein [schniten]", "[30 |] {rubric: Colic [Griping of the bowels].} Take a [slice of]", "Page number '30' in upper-left corner box; inline red rubric 'Grimen.'"),
                    (2, "line", "haissen Waizenbrodt, vnd über den Nabel des", "hot wheat-bread, and bound over the navel of the", None),
                    (3, "line", "khrankhen gebunden, benimbt also baldt das", "patient, it immediately takes away the", None),
                    (4, "mixed", "grimen. {rubric: Nerven Erstarrung —}", "colic. {rubric: Stiffening of the nerves [sinews] —}", "Inline red rubric 'Nerven Erstarrung —'."),
                    (5, "line", "Nüß öll mit holler blüe infundiert, ist", "Walnut oil infused with elder-blossoms is", None),
                    (6, "line", "khöstlich zu den ein geschrumpfften Nerven.", "precious for shrunken [contracted] nerves/sinews;", None),
                    (7, "line", "es Zertheilt die harte geschwulst, heilt alle", "it disperses hard swelling [and] heals all", None),
                    (8, "line", "laidt gifftige wunden.", "kinds of venomous wounds.", "laidt / allerhandt gifftige wunden."),
                    (9, "mixed", "{rubric: Seiden stechen.} das kreüz in der", "{rubric: Pleurisy [Stitch in the side].} The woody cross [septum] inside the", "Inline red rubric 'Seiden stechen'; woodyJuglans regia septum (signatura rerum)."),
                    (10, "line", "Nüß zu ꝑll̵ [Pulver] gemacht. ℨj ein geben hilfft", "walnut made into powder [ꝑll̵], 1 drachm [ℨj] administered, helps", None),
                    (11, "mixed", "für seiden stechen. {rubric: Pöß.} Nimb 2 gedörte", "for pleurisy. {rubric: Plague.} Take 2 dried", "Inline red rubric 'Pöß.' (= Pest)."),
                    (12, "line", "nüß mit 2 feigen, vnd 20 rauten Plätlein", "walnuts with 2 figs, and 20 rue leaves [Ruta graveolens],", "Famous Mithridatic plague prophylactic."),
                    (13, "line", "vnd ein wenig 🜔 [Salz], vnder ein ander gestosen,", "and a little salt [🜔], pounded together,", None),
                    (14, "line", "vnd nüchter ein genomen, preseruiert vor", "and taken fasting, it preserves against", None),
                    (15, "line", "der Pöst. —", "the plague. —", None),
                    (16, "rubric", "{rubric: Gaiß Würm den khindern —}", "{rubric: Goat-worms [Heart-worms] in children —}", "Red rubric."),
                    (17, "line", "Die khinder, so den herz oder gaiß wurm", "Children who have the heart-worm or goat-worm,", "Early Modern folk pediatric diagnosis for marasmus/infantile wasting."),
                    (18, "line", "haben, stättigs schreien, vnd am leib abnemen", "who cry continually and waste away in body,", None),
                    (19, "line", "wird geholffen, wan man Venedisches glas", "are helped when one takes Venetian glass", None),
                    (20, "line", "mit wenig habern, zu ✗ [Pulver] macht, hernach", "with a little oats, makes it into fine powder [✗], afterwards", None),
                    (21, "line", "mit hönig Vermischt, vnd den khind in einer", "mixes it with honey, and binds it upon the child in a", None),
                    (22, "line", "Nußschallen über den Nabel bindt, so khumbt", "walnut-shell over the navel: then comes", None),
                    (23, "line", "als der wurm auß begierde zum hönig", "the worm out of craving for the honey", None),
                    (24, "line", "mit dem khopf auß den Nabel her für vnd", "forth with its head out of the navel and", None),
                    (25, "line", "frißt darvon, vnd wirdt also durch das glas", "eats thereof, and is thus killed by the glass.", None),
                    (26, "line", "erdött. das aber das khind den wurm", "That the child truly has the worm,", None),
                    (27, "line", "habe ist nit gnueg das es stätts schreÿe, vnd", "however, it is not enough that it continually cries and", None),
                    (28, "line", "abnembe, sondern es wirdt also probieret", "wastes away, but it is tested in this manner:", None),
                    (29, "line", "man nimbt ein lebendige grundl, vnd", "one takes a live gudgeon [Gobio gobio / loach], and", "grundl = Grundel / Bartgrundel (small freshwater fish)."),
                    (30, "line", "bind es dem khind über das Näbl, laß es", "binds it upon the child over the navel; leave it", None),
                    (31, "line", "3, 4 oder 8 stund darauff, wans ein", "for 3, 4, or 8 hours thereon; if it has a", None),
                    (32, "line", "wurm hat, so sicht mans wan mans", "worm, one sees when one unbinds", None),
                    (33, "line", "auf bind, das die grundl angnagdt, oder", "it that the gudgeon has been gnawed at, or", None),
                    (34, "line", "schier halb Verzehrt, als dan legt man", "almost half consumed; only then does one apply", None),
                    (35, "line", "erst das glas vnd hönig auf. vnd so man", "the glass and honey. And when one", None),
                    (36, "line", "sicht, das der wurm auch darvon gef=", "sees that the worm has also eaten thereof,", None),
                    (37, "line", "ressen, gibt man dem khind gequöksilber=", "one gives the child mercury-infused", "gequöksilbertes wasser = aqua mercurialis (water boiled over metallic mercury)."),
                    (38, "line", "tes wasser 2 oder 3 tag in khöchel, das", "water for 2 or 3 days in its pap [porridge], which", "khöchel = Köchel (infant pap/gruel)."),
                    (39, "line", "treibt den todten stükh weiss auß.", "expels the dead [worm] piecemeal.", None),
                    (40, "mixed", "{rubric: Glidt Wasser —} schnekhen zu aschen", "{rubric: Joint-water [Synovial discharge] —} Snails burned", "Inline red rubric 'Glidt Wasser —' (synovia escaping from deep joint wounds)."),
                    (41, "line", "gebrent, vnd in die wunden gesträet, stölt", "to ash and strewed into the wounds staunches", None),
                    (42, "line", "das glidt wasser, khräfftigkhlich.", "the joint-water powerfully.", None),
                    (43, "mixed", "{rubric: Dörsucht.} Wasser schnekhen, schnekhen ℨj:", "{rubric: Consumption [Phthisis].} Water-snails, [dried] snails 1 drachm [ℨj]:", "Continues across column break to col. B, l. 1."),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B (Right Column, within red rules X=2776..5157, Y=274..6498)",
                "ulx": 2776, "uly": 274, "lrx": 5157, "lry": 6498,
                "lines": make_lines("p30", 8, "colB", 2776, 274, 5157, 6498, [
                    (1, "line", "ist ein khöstliches mitl wider die dör vnd", "is a precious remedy against consumption and", "Completes sentence from col. A, l. 43."),
                    (2, "line", "lungl sucht, morgens vnd abents auf 1 M[esserspitz] woll", "pulmonary phthisis, taken morning and evening by the knife-point", None),
                    (3, "line", "Suppen genomen.", "in broth.", None),
                    (4, "rubric", "{rubric: Schwinden der glider — oder}", "{rubric: Wasting [atrophy] of the limbs — or}", "Red rubric."),
                    (5, "rubric", "{rubric: grossen schmerzen der Nerven.}", "{rubric: severe pains of the nerves.}", "Red rubric."),
                    (6, "line", "℞ der rothen waldt schnekhen, souill du haben khanst,", "Take [℞] red forest slugs [Arion rufus], as many as you can get,", None),
                    (7, "line", "thue in ein Zügkhern glaß gethan, mach mit 🜔 [Salz] schicht", "put them into a confection-jar, layer them with salt [🜔] [stratum super stratum],", "Zügkhern glaß = Zuckerglas (wide-mouthed apothecary jar)."),
                    (8, "line", "vnd Verbindt es woll, sez 14 tag in ein warmes", "bind it up well, set it for 14 days in a warm", None),
                    (9, "line", "hauffen, so werden die schnekhen zergehen, vnd zu", "[dung-]heap [digestion in fimo equino], and the slugs will dissolve and turn into", None),
                    (10, "line", "einen öll, seichs durch ein duch, vnd behalts, las", "an oil [liquor limacum]; strain it through a cloth and keep it; let", None),
                    (11, "line", "dier lieb sein, dan wo Nerven ein schrumpffen", "it be dear to you, for wherever nerves/sinews contract", None),
                    (12, "line", "oder ein glidt schwind, oder schmerzen in", "or a limb wastes away, or there are pains in", None),
                    (13, "line", "Nerven sein, so schmier täglich 2 mall.", "the nerves, anoint therewith twice daily.", None),
                    (14, "rubric", "{rubric: Dörsichtigen}", "{rubric: For the consumptive [phthisical patients]}", "Red rubric."),
                    (15, "line", "Die ganzen schnekhen mit den heislein, sÿe", "Whole snails with their shells", None),
                    (16, "line", "seind hard zu verdäuen, der aber ein guetten", "are hard to digest, but to one who has a good", None),
                    (17, "line", "Magen hat, dem geben sÿe ein reiche vnd", "stomach they provide a rich and", None),
                    (18, "line", "wolkhumbne nahrung, dero wegen seind sÿe", "welcome nourishment; therefore they are", None),
                    (19, "line", "denen dörsichtigen, beÿ denen die Natirliche", "for consumptive patients, in whom the natural", None),
                    (20, "line", "khräfften garz dörrt mit Putter gekhocht", "powers are wholly parched, when boiled with butter,", None),
                    (21, "line", "sehr khöstlich. oder machs also.", "most precious. Or prepare it thus:", None),
                    (22, "line", "Nimb der schnekhen, beÿ 60. welliche Vom allen", "Take about 60 snails which have been thoroughly", None),
                    (23, "line", "schleim woll gesäubert sein, thue darzue", "cleansed of all slime; add thereto", None),
                    (24, "line", "farfara blöder, ℥ij. frische khüe milch ℔ij.", "coltsfoot leaves [Tussilago farfara] 2 ounces [℥ij], fresh cow's milk 2 pounds [℔ij];", None),
                    (25, "line", "khoch alles woll mit ein ander, biß die schnekhen", "boil everything well together until the snails", None),
                    (26, "line", "woll gekhocht seind, hernach thue Zukher dar=", "are thoroughly cooked; afterwards add sugar", None),
                    (27, "line", "zue, vnd gibs den dörsichtigen es ist ein her=", "thereto, and give it to the consumptive: it is a", None),
                    (28, "line", "liche medicin", "splendid medicine.", None),
                    (29, "rubric", "{rubric: Hüesten vnd außwurff.}", "{rubric: Cough and expectoration.}", "Red rubric."),
                    (30, "line", "Nimb die schnekhen auß den heisel, vnd mit", "Take the snails out of their shells, and boiled", None),
                    (31, "line", "gersten khocht, vnd solche Prue genossen, stilt", "with barley, and partaking of this broth, it calms", None),
                    (32, "line", "das hüesten vnd beförderet den auß wurff", "the cough and promotes expectoration;", None),
                    (33, "line", "Ist auch guett Vor das Blüett speiben vnd", "it is also good for spitting of blood [hemoptysis] and", None),
                    (34, "mixed", "gebrechen der lungel. {rubric: ☿c maj.} [Die] roh zer=", "afflictions of the lungs. {rubric: Haemorrhagia major [or Consolida major].} Crushed raw", "Inline red symbol/abbreviation '☿c maj.'"),
                    (35, "line", "stossen vnd frisch über geschlagen, stölt das ☿c maj", "and applied fresh as a poultice, it stops major hemorrhage", None),
                    (36, "line", "welliches lang ge wesen, übers stirn gelegt,", "which has lasted a long time; laid across the forehead,", None),
                    (37, "line", "stölt es das Nasen blüetten, vnd hindert die", "it staunches nosebleeds and prevents the", None),
                    (38, "line", "flüß so in die augen fallen.", "rheums [fluxions] that descend into the eyes.", None),
                    (39, "mixed", "{rubric: Pöß vnd Gifftige Kügle} Prenn schnekhen", "{rubric: Plague and poisoned bullets [or pestilential airs].} Burn snails", "Inline red rubric."),
                    (40, "line", "zu ꝑll̵ [Pulver] mit rotten korallen, maull Pör", "to powder [ꝑll̵] with red coral, mulberry", None),
                    (41, "line", "oder pfirsich, ein wenig weisen pfeffer vnd.", "or peach, a little white pepper, and...", "Continues onto p. 32 (Canvas 9), col. A, l. 1 ('iß es 6. dult...'). Notice p. 31 is skipped in pagination!"),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 5. CANVAS 9: Page 32 — Dental Fistulae, Balsam of Copaiba in Vienna & Stomatitis (b18775275_MS_990_0009.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0009_p32",
        "canvas_num": 9,
        "jp2": "b18775275_MS_990_0009.JP2",
        "orig_page": "32",
        "folio_side": "recto",
        "width": 4977,
        "height": 6853,
        "frame_box": (214, 287, 4756, 6444),
        "center_rule_x": 2501,
        "summary": "Page 32 (recto, numbered '32' in upper-right margin; faces p. 30 on verso Canvas 8, skipping '31' in pagination without text loss). Column A completes the recipe from p. 30, then gives an important historical note on Balsam of Copaiba ('Balsamo Copauia') recently imported from the Indies ('auß India') and used for remarkable cures in Vienna ('in Wienn' — confirming the manuscript's Austrian provenance), followed by surgical management of carious jawbone (incision, actual cautery, oil of vitriol, exfoliation) and syringe-injections for dental fistulae. Column B features a half-column watercolour bust portrait of a mustachioed gentleman in a red doublet and wide pleated ruff, above remedies for putrefaction/ulceration of the mouth ('Von fälung des Mundts', stomatitis/scurvy), including a pauper's remedy ('arme leüd die nichts Vermögen') of watercress, scurvy-grass, and horseradish.",
        "figures": [
            {
                "fig_id": "fig_p32_gentleman",
                "label": "Watercolour Bust Portrait of a Gentleman in Red Doublet and Pleated Ruff (p. 32, Col. B Upper)",
                "ulx": 2501, "uly": 287, "lrx": 4756, "lry": 3280,
                "desc": "Half-column watercolour portrait showing a dark-haired, mustachioed man in a crimson doublet and broad scalloped lace-edged ruff Collar (representing a patient afflicted with oral/dental disease), bordered below by a double red-and-ochre rule.",
            }
        ],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=214..2501, Y=287..6444)",
                "ulx": 214, "uly": 287, "lrx": 2501, "lry": 6444,
                "lines": make_lines("p32", 9, "colA", 214, 287, 2501, 6444, [
                    (1, "line", "iß es 6. dult. ℨj. in Saccharo solut. mer in", "eat thereof 6 doses, 1 drachm [ℨj] dissolved in sugar; further, in", "Continues from p. 30, col. B, l. 41."),
                    (2, "line", "mel. persicar. āā ℨvj. mis. f. l. ad Vs: diß", "peach-honey, of each 6 drachms [āā ℨvj]; mix, make a linctus for use. This", "mis. f. l. ad Vs: = misce, fiat linctus ad usum."),
                    (3, "line", "ist khöstlich man solles aber nit zu lang brauchen", "is precious, yet one should not use it too long,", None),
                    (4, "line", "damit die Zand nit ledig werden. nach disen khan", "lest the teeth become loose. After this, one may", None),
                    (5, "line", "man Volgents brauchen, welliches ein sehr khö=", "use the following, which is a most pre-", None),
                    (6, "line", "stlicher Balsam ist", "cious balsam:", None),
                    (7, "rubric", "{rubric: NB: du Wirst Vileicht fragen}", "{rubric: NB: You will perhaps ask,}", "Red rubric."),
                    (8, "rubric", "{rubric: Was ist das Balsamo Copauia.}", "{rubric: What is this Balsamo Copaiba?}", "Balsam of Copaiba (oleoresin of South American Copaifera species, introduced into European pharmacy in the mid-17th century)."),
                    (9, "line", "so sag ich dir das ein khöstlicher Balsam ist", "Then I tell you that it is a precious balsam,", None),
                    (10, "line", "vnd vor Etlichen Jahren auß India gebracht", "and was brought some years ago out of the Indies,", None),
                    (11, "line", "worden, vnd darmit in Wienn grosse", "and therewith in Vienna great [wounds/ulcers]", "Explicit internal reference to Vienna ('in Wienn'), corroborating Austrian compilation and Gilhofer & Ranschburg's Viennese provenance!"),
                    (12, "line", "geheült seindt als wie zu [sehen], vnd brauch", "have been healed, as may be seen; and use it", None),
                    (13, "line", "also Nimb dises Balsam Copauia. ℨj. mel.", "thus: Take of this Balsam of Copaiba 1 drachm [ℨj], honey", None),
                    (14, "line", "rosat. ℥ij lise 2 stukh Vreinig, thue es ein", "of roses 2 ounces [℥ij]; unite these 2 ingredients, put it in", "Vreinig = vereinig (unite/incorporate)."),
                    (15, "line", "[... wä]rme nit gar zu lang, damit die khrafft", "[... wa]rm it not all too long, lest the virtue", "Left margin of lines 15–22 covered by a narrow vertical paper repair strip."),
                    (16, "line", "[des] Indianischen Balsam nicht wekh gehe", "[of the] Indian balsam evaporate away", None),
                    (17, "line", "[vnd] werde. hernach thue darein.", "[and] be lost. Afterwards put therein:", None),
                    (18, "line", "[...] 🜖 alb. [Vitriolum album] āā ℨß. mirrh. Elb. ℥iiß", "[...] white vitriol [🜖 alb., zinc sulfate], of each ½ drachm [āā ℨß], choice myrrh 2½ ounces [℥iiß],", "mirrh. Elb. = Myrrha electa."),
                    (19, "line", "[extr.] tabaci ℈j. ol. ♁ris [olei Sulphuris] G. xj. mis. ad", "[extract of] tobacco 1 scruple [℈j], oil of sulphur [ol. ♁ris] 11 drops [G. xj]; mix for", "G. xj = guttae 11 (11 drops)."),
                    (20, "line", "[Vsu]m.", "use.", None),
                    (21, "line", "[Wa]n aber das Bain Cariös vnd angangen ist", "When, however, the [jaw]bone is carious and decayed,", "Bain = Bein (bone); Cariös = necrotic/carious osteomyelitis of the jaw."),
                    (22, "line", "[vnd] mit disen arzney nit zue khumen", "and one cannot get at it with these medicines,", None),
                    (23, "line", "khan, so muess man mit den mäser lufft", "then one must make an opening and space with", "mäser = Messer (surgical knife / scalpel)."),
                    (24, "line", "vnd plaz machen, vnd auf das Cauterium actual", "the knife, and apply the actual cautery [red-hot iron],", "Cauterium actual = hot iron cautery, contrasted with potential (chemical) cautery."),
                    (25, "line", "vnd als dan das ol. Vitriol 3 oder 4 dropffen", "and then apply 3 or 4 drops of oil of vitriol [sulfuric acid];", None),
                    (26, "line", "brauchen, wan aber das Pain Cariös ist, so", "for when the bone is carious, which", None),
                    (27, "line", "er khant wirdt auß der Materi vnd gestankh", "is recognized from the purulent matter and stench,", None),
                    (28, "line", "als dan muess man darzue raumen, vnd die", "then one must clear a passage to it, and", None),
                    (29, "line", "Separacio promouiern —", "promote the separation [exfoliation of the dead bone sequestrum] —", None),
                    (30, "line", "Wan man nun beÿ den fistlen alle Ent=", "When now in dental fistulae all in-", None),
                    (31, "line", "zündung abgeschafft, so muess man alle tag", "flammation has been abolished, one must every day", None),
                    (32, "line", "den Canall verändern, durch das mäser", "dilate/renew the fistula tract by means of the knife", None),
                    (33, "line", "oder schwam, als dan solle man alle tag 2 mall", "or sponge-tent, and then twice every day one should", "schwam = prepared sponge tent used to dilate fistulous tracts."),
                    (34, "line", "mit volgenten ▽ [Wasser] ein sprüzen.", "inject [syringe] it with the following water [▽]:", "ein sprüzen = inject with a wound syringe."),
                    (35, "line", "℞ flor 🜘 [Alaun] ℨij. lixiu. è Calce uiu[a] ℥xij.", "Take [℞] flowers of alum [🜘] 2 drachms [ℨij], lye of quicklime 12 ounces [℥xij],", "lixivium e calce viva = limewater / caustic lye."),
                    (36, "line", "▽ [Wasser] solan. C. B. [Cardui Benedicti] ℥iß. rad. aristolochia", "water [▽] of nightshade [and] blessed thistle 1½ ounces [℥iß], root of birthwort", "rad. aristolochia long. = Aristolochia longa (classic vulnerary for bone/fistulae)."),
                    (37, "line", "long. mirrha. āā ℨiß. ▽ [Wasser] Veronica. ℥iiij.", "[Aristolochia longa] [and] myrrh, of each 1½ drachms [āā ℨiß], speedwell water [▽] 4 ounces [℥iiij],", None),
                    (38, "line", "☿ dulc. [Mercurius dulcis] ℨj. mis. ad Vsum.", "sweet mercury [☿ dulc., calomel / mercurous chloride] 1 drachm [ℨj]; mix for use.", None),
                    (39, "line", "Dises heilt Von den fistlen beÿ den", "This heals the fistulae beside the", None),
                    (40, "line", "Zänten. Von andern fistlen wirdst an sein", "teeth. Of other fistulae you will hear more", None),
                    (41, "line", "[or]dt ein Bladt mehrers Vernehmen —", "in its proper place on a later leaf —", "Quire/sheet signature '2' in lower margin."),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B Lower (Text below Portrait Rule, within red rules X=2501..4756, Y=3660..6444)",
                "ulx": 2501, "uly": 3660, "lrx": 4756, "lry": 6444,
                "lines": make_lines("p32", 9, "colB", 2501, 3660, 4756, 6444, [
                    (1, "rubric", "{rubric: Von fälung des Mundts.}", "{rubric: Of putrefaction [ulceration / scurvy] of the mouth.}", "Red rubric below double yellow/red divider; fälung = Fäulung (putrid stomatitis / scorbutic gums)."),
                    (2, "line", "℞ Praun wegerich, weggraß, Paum khnoß,", "Take [℞] ribwort plantain, knotgrass [Polygonum aviculare], tree-buds,", None),
                    (3, "line", "löffel khraut, saluia, rotte rosen, an 1 H. in", "scurvy-grass [Cochlearia officinalis], sage, red roses, of each 1 handful [1 H.], boiled in", "löffel khraut = Löffelkraut (antiscorbutic); 1 H. = 1 Handvoll (manipulus)."),
                    (4, "line", "▽ [Wasser] gesoden, mit ein wenig ✚ [Essig] das es woll", "water [▽] with a little vinegar [✚] so that it becomes", None),
                    (5, "line", "zu samen ziehe, darmit solle er sich im tag Et=", "well astringent; therewith let him gargle", None),
                    (6, "line", "lich mall gurglen.", "several times a day.", None),
                    (7, "rubric", "{rubric: arme leüd die nichts Vermögen brauchen}", "{rubric: Poor folk who cannot afford anything use}", "Red rubric explicitly addressing charity medicine for the poor ('Armenarznei')."),
                    (8, "rubric", "{rubric: dises}", "{rubric: this:}", "Red rubric."),
                    (9, "line", "℞ Prun khreß, woll zerstossen, löffl khraut", "Take [℞] watercress [Nasturtium officinale], well bruised, scurvy-grass,", None),
                    (10, "line", "den Päuern khren dar mit auß gepräst safft, ein", "common [peasant] horseradish, the juice pressed out therewith, a", "Päuern khren = Bauernkren (horseradish)."),
                    (11, "line", "wenig hönig vnd 🜘 [Alaun] darein gethan, darmit das", "little honey and alum [🜘] put therein; wash the", None),
                    (12, "line", "Zant fleisch gewaschen.", "gums therewith.", None),
                    (13, "rubric", "{rubric: Ein Anders —}", "{rubric: Another —}", "Red rubric."),
                    (14, "line", "℞ wegerich vnd Prun khreß ▽ [Wasser], āā ℥iiij. rosen", "Take [℞] plantain and watercress water [▽], of each 4 ounces [āā ℥iiij], rose-", None),
                    (15, "line", "hönig vnd maull Pör safft, āā ℥j. sp[iritus] 🜖 [Vitrioli] souil", "honey and mulberry juice [diamoron], of each 1 ounce [āā ℥j], spirit of vitriol [sp. 🜖] as much", None),
                    (16, "line", "das es saurlecht wirdt, darmit das Zantfleisch", "as makes it pleasant-sour [acidulated]; wash the gums", None),
                    (17, "mixed", "ge waschen. {rubric: Ein anderes}", "therewith. {rubric: Another}", "Inline red rubric 'Ein anderes'."),
                    (18, "line", "℞ Praun wegerich vnd Prunelle ▽ [Wasser] āā ℥iij. 🜖 [Vitriol]", "Take [℞] plantain and self-heal [Prunella vulgaris] water [▽], of each 3 ounces [āā ℥iij], vitriol [🜖],", "Prunelle = Braunelle (specific for throat/mouth inflammations)."),
                    (19, "line", "🜘 [Alaun], od[er] ♁ [Antimonium], āā ℨiij. rosen hönig, ℥j 🜔 [Salz]", "alum [🜘], or antimony [♁], of each 3 drachms [āā ℨiij], rose-honey 1 ounce [℥j], burnt salt [🜔]", None),
                    (20, "line", "ust. ℈ß. Vermisch zu samen darmit gurglet.", "½ scruple [℈ß]; mix together and gargle therewith.", None),
                    (21, "rubric", "{rubric: Wan die fällung in dem Mundt souill}", "{rubric: When the putrefaction in the mouth has so}", "Red rubric."),
                    (22, "rubric", "{rubric: hete über hand genomen das es vmb die}", "{rubric: gained the upper hand that it}", "Red rubric."),
                    (23, "rubric", "{rubric: obgemelte mitl nichts geben wolte so}", "{rubric: will not yield to the aforesaid remedies, then}", "Red rubric."),
                    (24, "rubric", "{rubric: brauch Volgentes —}", "{rubric: use the following —}", "Red rubric."),
                    (25, "line", "℞ Vng. Ægipciacum ℥ij. maulbör safft ℥iß.", "Take [℞] Unguentum Aegyptiacum 2 ounces [℥ij], mulberry syrup 1½ ounces [℥iß],", "Unguentum Aegyptiacum = escharotic ointment of verdigris (copper acetate), vinegar, and honey."),
                    (26, "line", "sp[iritus] 🜖 [Vitrioli], od[er] ♁ [Sulphuris], āā ℨß. oder ℈ß nach dem", "spirit of vitriol [🜖] or sulphur [♁], of each ½ drachm [ℨß] or ½ scruple [℈ß], according as", None),
                    (27, "line", "einer solches die schärffe Vonnötten zu sein. darmit", "one judges the sharpness to be needful; rub", None),
                    (28, "line", "reibe das Zant fleisch, biß sich die fäule Verliert", "the gums therewith until the putrefaction disappears.", None),
                    (29, "line", "Wegen des gestankh so auß dem Mund geht, ist", "Against the stench that issues from the mouth, there is", None),
                    (30, "line", "nichts bösers als rosen marin Zukher, vnd solche", "nothing better than rosemary-sugar [conserve of rosemary], and such", "bösers = bessers (better)."),
                    (31, "line", "küechlein, Zimet vnd nägl. —", "troches/lozenges, cinnamon, and cloves. —", None),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 6. CANVAS 10: Page 33 — Regrowing Gums, Tonsils/Uvula & Four Extracted Molar Teeth (b18775275_MS_990_0010.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0010_p33",
        "canvas_num": 10,
        "jp2": "b18775275_MS_990_0010.JP2",
        "orig_page": "33",
        "folio_side": "verso",
        "width": 5423,
        "height": 6853,
        "frame_box": (528, 368, 5081, 6531),
        "center_rule_x": 2785,
        "summary": "Page 33 (verso, numbered '33' in upper-left margin). Column A treats scraping necrotic gum roots with a razor ('schar mäser'), incarnative powders to make rotted gums grow back, tightening loose teeth ('Zant wagel'), a potent sublimate-and-alum water applied with a small screw/swab, and remedies for halitosis. Column B treats inflammation and swelling of the tonsils and uvula ('Mandl vnd Zäpffel'), including lead acetate ('bleÿ Zukher') gargles and the folk-surgical maneuver of pulling the patient hard by the earlobes to raise a fallen uvula ('Wan das Zäpffel abgefallen ziehe ihm Woll beÿ den ohr läpel'), followed by a watercolour drawing of four multi-rooted human molar teeth and the opening of the treatise on toothache ('Von den Zänten Zuestänten vnd khrankheiten').",
        "figures": [
            {
                "fig_id": "fig_p33_teeth",
                "label": "Watercolour Study of Four Extracted Human Molar Teeth (p. 33, Col. B Middle)",
                "ulx": 2850, "uly": 3720, "lrx": 5050, "lry": 4650,
                "desc": "Shaded watercolour anatomical illustration of four extracted human molars in lateral/oblique view, depicting crown cusps and bifurcated/trifurcated roots, above a double yellow-and-red horizontal rule.",
            }
        ],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=528..2785, Y=368..6531)",
                "ulx": 528, "uly": 368, "lrx": 2785, "lry": 6531,
                "lines": make_lines("p33", 10, "colA", 528, 368, 2785, 6531, [
                    (1, "line", "[33 |] [abgesott]ens biß d[ie] ...", "[33 |] [decoct]ed until the ...", "Upper-left corner around page number '33' abraded/stained."),
                    (2, "line", "auf gequöld, vnd za[rt gemacht, soll die]", "swollen up and made tender, [the]", None),
                    (3, "line", "wurz hernach mit den schar mäser abgeschäbt", "root should afterwards be scraped clean with the razor [scalpel],", "schar mäser = Schermesser (surgical razor/scalpel)."),
                    (4, "line", "werden, vnd als dan dar auf streichen das Egiptische", "and then spread thereupon the Egyptian", None),
                    (5, "line", "Sälbel, oder Prandten 🜘 [Alaun] mit rosen hönig Ver=", "ointment [Unguentum Aegyptiacum], or burnt alum [🜘] mixed with", None),
                    (6, "line", "mischt.", "rose-honey.", None),
                    (7, "rubric", "{rubric: Wan aber das Zant fleisch alles hin}", "{rubric: When, however, the gum-flesh has all}", "Red rubric."),
                    (8, "rubric", "{rubric: wekh gefäult ist, solle mans mit Vol=}", "{rubric: rotted away, one should make it grow back}", "Red rubric."),
                    (9, "rubric", "{rubric: genden ꝑll̵ [Pulver] widerumb wachsen machen.}", "{rubric: again with the following powder [ꝑll̵]:}", "Red rubric."),
                    (10, "line", "℞. weisen samen, ℨj. Calam. ℨß. Veronica Vbe=", "Take [℞] white seed [or vetch/orris] 1 drachm [ℨj], calamus ½ drachm [ℨß], speedwell,", None),
                    (11, "line", "rist vnd die Zant dar mit gebriben, Vnd besträet.", "prepared, and rub and strew the teeth therewith.", None),
                    (12, "line", "Wan aber die Zant wagel werden ist nichts bö=", "When, however, the teeth become loose [mobile], there is nothing", "wagel = wackelig (loose/shaky)."),
                    (13, "line", "sers, als rosen hönig mit sp[iritus] 🜖 [Vitrioli] Vermischt", "better than rose-honey mixed with spirit of vitriol [sp. 🜖],", None),
                    (14, "line", "täglich 2 mall das Zant fleisch dar mit bestrichen", "coating the gums therewith twice daily.", None),
                    (15, "rubric", "{rubric: auch macht man gar ein heillsames sälbel}", "{rubric: One also makes a very salutary ointment}", "Red rubric."),
                    (16, "line", "Von rosen hönig vnd maull bör safft mit", "of rose-honey and mulberry syrup mixed with", None),
                    (17, "line", "sp[iritus] 🜖 [Vitrioli] Ver mischt, das es säurlecht wird.", "spirit of vitriol [sp. 🜖] until it becomes pleasantly sour.", None),
                    (18, "line", "In grosen Zue fällen ist Volgendes ▽ [Wasser] ein hör=", "In severe cases [accidents] the following water [▽] is a", None),
                    (19, "line", "liches mitl, allein es muess bedachtsam", "glorious remedy, only it must be used with", None),
                    (20, "line", "gebraucht werden.", "great caution:", None),
                    (21, "line", "℞. ☿ sublimat. [Mercurius sublimatus] ℨij. 🜘 usti [Alaun] ℥iiß zusamen ge=", "Take [℞] corrosive sublimate of mercury [☿ sublimat., HgCl2] 2 drachms [ℨij], burnt alum [🜘 usti] 2½ ounces [℥iiß];", "Mercurius sublimatus = mercuric chloride, explaining the scribe's caution in ll. 19–20!"),
                    (22, "line", "stossen, nimb den Neunten thaill dises ꝑ. [Pulvers] mit", "pounded together, take the ninth part of this powder [ꝑ.] mixed with", None),
                    (23, "line", "einer halben Seidl wegerich ▽ [Wasser] Vermischt, in ein", "half a Seidel [~0.18 L] of plantain water [▽], in a", "Seidl = Austrian liquid measure (~0.35 L; a half Seidel = Pfiff)."),
                    (24, "line", "glaß woll Ver macht, hernach mit ein schräubel", "glass vessel well stoppered; afterwards with a little screw-probe [swab]", None),
                    (25, "line", "ganz subdtill aplicieret. NB: mans zu", "apply it most delicately. NB: If it should be too", None),
                    (26, "line", "starkh wehre, khan man mehr des gedachten", "strong, one may pour in more of the", None),
                    (27, "line", "▽ [Wasser] zue giessen.", "aforesaid water [▽].", None),
                    (28, "rubric", "{rubric: Wan das Zant fleisch fault, vnd der}", "{rubric: When the gums rot, and the}", "Red rubric."),
                    (29, "rubric", "{rubric: Mund sehr stinkht —}", "{rubric: mouth stinks greatly —}", "Red rubric."),
                    (30, "line", "℞. ein löffel Voll hönig, ein Muschat nuß, halben", "Take [℞] a spoonful of honey, one nutmeg, half a", None),
                    (31, "line", "löffel Voll nägl, ein löffel Voll alua safft, reibs", "spoonful of cloves, a spoonful of aloe [or sage] juice; rub it", None),
                    (32, "line", "alles woll vnderein ander, vnd druckhs durch ein", "all well together, and press it through a", None),
                    (33, "line", "düechel, das es wird wie ein sälbel, darmit best=", "little cloth so that it becomes like a liniment; anoint", None),
                    (34, "line", "reiche die Zant.", "the teeth therewith.", None),
                    (35, "line", "Oder nimb weihrauch vnd mastix, āā ℨß. siede es", "Or take frankincense and mastic, of each ½ drachm [āā ℨß]; boil it", None),
                    (36, "line", "in rothen V̈ [Wein] ℔j. las halb ein sieden, wasch die", "in 1 pound [℔j] of red wine [V̈], let it boil down by half; wash the", None),
                    (37, "line", "Zant ab, alle tag 2 mall, bringt ein guetten gruch.", "teeth therewith twice every day: it brings a pleasant odor.", None),
                    (38, "line", "Für die fällung im Mund brauch dises.", "For putrefaction in the mouth, use this:", None),
                    (39, "line", "℞. aichen laub, khraußte minzen, weisen saluia", "Take [℞] oak leaves, curled mint, white sage,", None),
                    (40, "line", "löffl,khrüffen ꝑ. āā 4 gestossen muschat nuß,", "scurvy-grass powder, of each 4 [parts], pounded nutmeg,", None),
                    (41, "line", "🜘 usti [Alaun], das ein wenig härb dar Von wird, machs", "burnt alum [🜘 usti] enough to make it somewhat astringent; make it", "härb = herb (tart/astringent)."),
                    (42, "line", "mit hönig an wie ein dines latt wergel, das brauch", "up with honey like a thin electuary, and use that.", "latt wergel = Latwerglein (small electuary)."),
                ]),
            },
            {
                "col_id": "colB_upper",
                "col_label": "Column B Upper (Tonsils & Uvula Treatise, above Molar Teeth Illustration, X=2785..5081, Y=368..3720)",
                "ulx": 2785, "uly": 368, "lrx": 5081, "lry": 3720,
                "lines": make_lines("p33", 10, "colB_up", 2785, 368, 5081, 3720, [
                    (1, "rubric", "{rubric: Mandl vnd Zäpffel Entzüntung}", "{rubric: Inflammation and swelling of the}", "Red rubric; Mandl = tonsils, Zäpffel = uvula."),
                    (2, "rubric", "{rubric: vnd geschwulst. —}", "{rubric: tonsils and uvula. —}", "Red rubric."),
                    (3, "line", "℞. holler wurz ▽ [Wasser], darmit gurgle dich es heilt", "Take [℞] elder-root water [▽]; gargle therewith: it heals", None),
                    (4, "line", "die mundt geschwär, vnd alle Ver sehrung des hals", "ulcers of the mouth and all excoriations of the throat,", None),
                    (5, "line", "vnd Zäpffel, vnd mandl.", "uvula, and tonsils.", None),
                    (6, "line", "Oder siede deüffels abiß wurzel Mj. in ▽ [Wasser]", "Or boil devil's-bit scabious root [Succisa pratensis] 1 handful [Mj.] in water [▽]", "deüffels abiß wurzel = Radix Morsus Diaboli, famous specific for quinsy/angina."),
                    (7, "line", "℔j. halben thaill ein sieden lasen, dar mit gurgle", "1 pound [℔j], let it boil down by half; gargle therewith", None),
                    (8, "line", "dich offt warm, ist ein sonder bahres mitl", "often while warm: it is a singular remedy", None),
                    (9, "line", "wider die hals geschwär, dan es hilfft sehr baldt", "against throat ulcers [quinsy], for it helps very quickly", None),
                    (10, "line", "vnd dienet wider geschwulst der mandl.", "and serves against swelling of the tonsils.", None),
                    (11, "rubric", "{rubric: Wan die Mandl hizig vnd Wundt.}", "{rubric: When the tonsils are hot [inflamed] and raw:}", "Red rubric."),
                    (12, "line", "so gurgle dich offt warm mit andini ▽ [Wasser]", "Then gargle often while warm with endive water [▽]", "andini = Endivien / Intybus."),
                    (13, "line", "darein souill bleÿ Zukher zergangen [biß]", "wherein so much sugar of lead [lead acetate, Saccharum Saturni] has dissolved", "bleÿ Zukher = lead(II) acetate, sweet-tasting iatrochemical astringent."),
                    (14, "line", "es ein wenig süess darvon wirdt, be=", "that it becomes slightly sweet therefrom; it takes", None),
                    (15, "line", "nimbt alle Entzüntung der Mandl [vnd] Zäpffel", "away all inflammation of the tonsils and uvula.", None),
                    (16, "rubric", "{rubric: Wan das Zäpffel abgefallen ziehe}", "{rubric: When the uvula has fallen [prolapsed], pull}", "Red rubric."),
                    (17, "rubric", "{rubric: ihm Woll beÿ den ohr läpel so}", "{rubric: him hard by the earlobes, and}", "Classic Alpine/South German folk-surgical manipulation to reposition a relaxed uvula."),
                    (18, "rubric", "{rubric: wirdt baldt böser. oder brauch die}", "{rubric: it will soon get better; or use the}", "Red rubric."),
                    (19, "rubric", "{rubric: obgemelte gurgel ▽ [Wasser] die zu allen}", "{rubric: aforesaid gargle-waters [▽] which serve for}", "Red rubric."),
                    (20, "rubric", "{rubric: samen ziehend seindt —}", "{rubric: all astringent purposes —}", "Red rubric directly above the watercolour drawing of the 4 molar teeth."),
                ]),
            },
            {
                "col_id": "colB_lower",
                "col_label": "Column B Lower (Treatise on Teeth & Toothache, below Molar Teeth Illustration, X=2785..5081, Y=4690..6531)",
                "ulx": 2785, "uly": 4690, "lrx": 5081, "lry": 6531,
                "lines": make_lines("p33", 10, "colB_low", 2785, 4690, 5081, 6531, [
                    (21, "rubric", "{rubric: Von den Zänten Zuestänten}", "{rubric: Of the conditions and diseases}", "Red rubric below the double yellow-red rule under the 4 molar teeth."),
                    (22, "rubric", "{rubric: vnd khrankheiten —}", "{rubric: of the teeth —}", "Red rubric."),
                    (23, "rubric", "{rubric: Vnd Erstlich Von Zant schmerzen}", "{rubric: And first, of toothache:}", "Red rubric."),
                    (24, "line", "Der Zantschmerzen hat sein Vrsach Von scharffen", "Toothache has its cause from sharp,", None),
                    (25, "line", "gesalznen, oder galigen flüß, so Vom haubt vnd", "salty, or bilious rheums [catarrhal fluxions] that sink down from", "Humoral pathology of odontalgia: acrid defluxions descending from the brain along the dental nerves."),
                    (26, "line", "hirn herab sinkhen, vnd mit ihrer schärffe stechen", "the head and brain, and with their sharpness prick", None),
                    (27, "line", "vnd nagen sÿe die subtille Nerven, welliche Vom", "and gnaw the subtle nerves which go from the", None),
                    (28, "line", "hirn zu den Zänten, vnd derselbigen wurzel gehen", "brain to the teeth and their roots;", None),
                    (29, "line", "dahero wan selbige Nerven Von den scharffen", "wherefore, when those nerves are tormented by the", None),
                    (30, "line", "flüßen gequält werden, so gibt es schmerzen ab, vnd", "sharp fluxions, it produces pain, and", None),
                    (31, "line", "ie stärkher der fluß, ie gröser der schmerz", "the stronger the fluxion, the greater the pain...", "Continues onto p. 34 (Canvas 11)."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 7. CANVAS 11: Page 34 — Toothache Anodynes, Temporal Plasters & Solar Herbalism (b18775275_MS_990_0011.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0011_p34",
        "canvas_num": 11,
        "jp2": "b18775275_MS_990_0011.JP2",
        "orig_page": "34",
        "folio_side": "recto",
        "width": 5031,
        "height": 6853,
        "frame_box": (271, 296, 4824, 6475),
        "center_rule_x": 2550,
        "summary": "Page 34 (recto, numbered '34' in upper-right margin). Continues the treatise on toothache ('Von Zant schmerzen') from p. 33. Distinguishes hot vs. cold catarrhal fluxions, observes that extraction ('herauß reiß') is the only permanent cure for carious teeth, and provides anodyne cotton-wool pellets, aural instillation of castoreum or horseradish juice, temporal plasters (Gum Elemi, mastic, opium), Laudanum opiatum, camphor ('XXX'), guaiacum-wine solar digests, and astrological/solar remedies using ash-wood ('lign. fraxino') gathered on St. John's Day (Midsummer) before sunrise ('Vor auf gang der ☉') and sorrel gathered in June before sunrise.",
        "figures": [],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=271..2550, Y=296..6475)",
                "ulx": 271, "uly": 296, "lrx": 2550, "lry": 6475,
                "lines": make_lines("p34", 11, "colA", 271, 296, 2550, 6475, [
                    (1, "line", "auch weillen seind solche flüß hizig, oder khalt.", "Moreover, at times such fluxions are hot, or cold.", "Continues from p. 33, col. B lower, l. 31."),
                    (2, "line", "die hizigen flüß machen grösern schmerzen.", "The hot fluxions cause greater pain.", None),
                    (3, "line", "Die faullen Zant haben khain bösers mitl als", "Rotten [carious] teeth have no better remedy than", None),
                    (4, "line", "das mans herauß reiß. Man khan zwar", "that one pull them out. One can indeed", None),
                    (5, "line", "woll auf ein Zeit den schmerzen stillen, es hat", "well calm the pain for a time, yet in", None),
                    (6, "line", "aber in die lange khain bestandt.", "the long run it has no permanence.", None),
                    (7, "rubric", "{rubric: Zu Zant Schmerzen brauch Volg=}", "{rubric: For toothache, use the follow-}", "Red rubric."),
                    (8, "rubric", "{rubric: ente mitl.}", "{rubric: ing remedies:}", "Red rubric."),
                    (9, "line", "℞. langen Pfeffer. G. xij. schwarzen Pfeffer G. iiij", "Take [℞] long pepper 12 grains [G. xij], black pepper 4 grains [G. iiij],", None),
                    (10, "line", "saffran. ℈j. opi G. vj. starckhen V̈ [Wein] ℥ß. siede", "saffron 1 scruple [℈j], opium 6 grains [G. vj], strong wine [V̈] ½ ounce [℥ß]; boil", None),
                    (11, "line", "Erstlich den saffran biß der drite thaill eingesoden", "first the saffron until the third part has boiled away;", None),
                    (12, "line", "hernach thue den Pfeffer grob zerstossen darein", "afterwards put the coarsely crushed pepper therein", None),
                    (13, "line", "vnd ein wenig gesoden. hernach das opi dabey 3 stundt", "and boil it a little; afterwards steep the opium therein for 3 hours", None),
                    (14, "line", "auf thue. in disen Neze ein Paum woll. legs auf", "to dissolve; in this moisten a piece of cotton-wool, lay it upon", None),
                    (15, "line", "die Zant, so wirdst wunder sehen.", "the teeth, and you will see wonders.", None),
                    (16, "rubric", "{rubric: Ein Anders.}", "{rubric: Another.}", "Red rubric."),
                    (17, "line", "℞. biber gaill in öll zertriben, vnd in das ohr", "Take [℞] castoreum triturated in oil, and put into the ear", "biber gaill = Bibergeil (castoreum)."),
                    (18, "line", "selbiger seiden gethan.", "of that same [affected] side.", None),
                    (19, "line", "Safft Von khrön in selbiger seiden in das ohr ge=", "Juice of horseradish put into the ear on that same side;", None),
                    (20, "line", "than. Oder den safft Von Ringel Plumen in", "or the juice of marigold [Calendula officinalis] drawn", None),
                    (21, "line", "die Nasen gezogen.", "up into the nostrils [errhine].", None),
                    (22, "rubric", "{rubric: Balsam für die Zant schmerzen.}", "{rubric: Balsam for toothache.}", "Red rubric."),
                    (23, "line", "℞. muscatnuß sälbel. ℨß. nägel. vnd XXX [Camphora]. āā", "Take [℞] expressed balm of nutmeg ½ drachm [ℨß], [oil of] cloves and camphor [XXX], of each", "XXX = scribal triple-X cipher for Camphora (camphor)."),
                    (24, "line", "G. xv. misch vnd legs auf den Zant.", "15 grains [G. xv]; mix and lay it upon the tooth.", None),
                    (25, "rubric", "{rubric: Ein anders.}", "{rubric: Another.}", "Red rubric."),
                    (26, "line", "geüß ✚ [Essig]. oder khaltes ▽ [Wasser] in das ohr vnd lege", "Pour vinegar [✚] or cold water [▽] into the ear, and lay", None),
                    (27, "line", "auf die schläff Volgentes Pflaster", "upon the temples the following plaster:", None),
                    (28, "line", "℞. Gumi Elemi. q. s. f. Emplast: legs auf", "Take [℞] Gum Elemi as much as suffices [q.s.], make a plaster; lay it upon", None),
                    (29, "line", "den schlaff.", "the temple.", None),
                    (30, "line", "oder ℞. mastich. q. v. ol. Carioph q. s. f.", "Or take [℞] mastic as much as you will [q.v.], oil of cloves as much as suffices [q.s.]; make", None),
                    (31, "line", "Emplast: Temporale —", "a temporal plaster [Emplastrum temporale] —", None),
                    (32, "rubric", "{rubric: oder}", "{rubric: or}", "Red rubric."),
                    (33, "line", "℞. Gum. Elemj. ℨß. Thuris. opij. āā. ℈j. picis", "Take [℞] Gum Elemi ½ drachm [ℨß], frankincense, opium, of each 1 scruple [āā ℈j], pitch", None),
                    (34, "line", "ℨiß. mis. f. Emplastrum", "1½ drachms [ℨiß]; mix, make a plaster.", None),
                    (35, "rubric", "{rubric: in Mundt halte Volgentes} ✚ [Essig]", "{rubric: In the mouth hold the following} vinegar [✚]:", "Red rubric with black glyph ✚ at end."),
                    (36, "line", "℞. Laudanum opiatum. G. iiij. XXX [Camphora]. ℈j. V̈ [Wein].", "Take [℞] Laudanum opiatum 4 grains [G. iiij], camphor [XXX] 1 scruple [℈j], wine [V̈]", None),
                    (37, "line", "℥iij. misch vnd brauchs.", "3 ounces [℥iij]; mix and use it.", None),
                    (38, "rubric", "{rubric: Oder brauch Volgentes}", "{rubric: Or use the following:}", "Red rubric."),
                    (39, "line", "Geußt V̈ [Wein] mit XXX [Camphora] Vermischt, an statt XXX [Camphora]", "Pour wine [V̈] mixed with camphor [XXX]; instead of camphor [XXX]", None),
                    (40, "mixed", "nimb ℨ. {rubric: oder —}", "take a drachm. {rubric: Or —}", "Small quire numeral '3' in brown ink beside 'ℨ.'."),
                    (41, "line", "℞. ✚ [Essig]. ℥iij. XXX [Camphora]. ℨj. 🜘 [Alaun]. ℨiij. opij ℈ß. 🜔 ♄ [Sal Saturni]. G. vi", "Take [℞] vinegar [✚] 3 ounces [℥iij], camphor [XXX] 1 drachm [ℨj], alum [🜘] 3 drachms [ℨiij], opium ½ scruple [℈ß], salt of lead [🜔 ♄] 6 grains [G. vi]...", "Continues across column break to col. B, l. 1."),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B (Right Column, within red rules X=2550..4824, Y=296..6475)",
                "ulx": 2550, "uly": 296, "lrx": 4824, "lry": 6475,
                "lines": make_lines("p34", 11, "colB", 2550, 296, 4824, 6475, [
                    (1, "line", "sem. Stafisagria. rad. piretro. āā [34]", "stavesacre seed [Delphinium staphisagria], pellitory root [Anacyclus pyrethrum], of each [34]", "Completes recipe from col. A, l. 41; page number '34' in upper-right box."),
                    (2, "line", "ℨß. mis.", "½ drachm [ℨß]; mix.", None),
                    (3, "rubric", "{rubric: Ein Anders —}", "{rubric: Another —}", "Red rubric."),
                    (4, "line", "℞. V̈ [Wein] opt. ℥iiiß. rasur. lig. Guaiaco ℥iß.", "Take [℞] best wine [V̈] 3½ ounces [℥iiiß], raspings of guaiacum wood [lignum sanctum] 1½ ounces [℥iß];", None),
                    (5, "line", "misch zu samen in ein [Kolben-Glaß]. Vermach es woll mit", "mix together in a glass cucurbit [drawn flask glyph], seal it well with", "Small horizontal pictogram of a long-necked glass matrass/cucurbit drawn inline!"),
                    (6, "line", "🜔 [Salz/Luto], vnd seze es an die ☉ [Sonne] od[er] warmen offen rühre", "lute/salt [🜔], and set it in the sun [☉] or on a warm stove; stir", None),
                    (7, "line", "im Tag offt, vnd laß so lang stehn, biß sich der", "often during the day, and let it stand so long until the", None),
                    (8, "line", "V̈ [Wein] gefärbt, seich ihn durch ein dichel, halte", "wine [V̈] has become colored; strain it through a little cloth, hold", None),
                    (9, "line", "nimb ein löffel Voll in mundt, so stölt es den", "a spoonful in the mouth, and it stops the", None),
                    (10, "line", "schmerzen Von stundt an, wan es Von", "pain immediately, when it arises from", None),
                    (11, "line", "khalten flüßen ist.", "cold fluxions.", None),
                    (12, "line", "Ist es aber Von groser hiz, so Vermische XXX [Camphora]", "If, however, it is from great heat, then mix camphor [XXX]", None),
                    (13, "line", "mit Praun wegerich ▽ [Wasser], vnd in mund genomen", "with ribwort plantain water [▽], and take it in the mouth,", None),
                    (14, "line", "oder gib ein grän laudanum opiatum", "or place one grain of Laudanum opiatum", None),
                    (15, "line", "in hollen Zandt. —", "into the hollow [carious] tooth. —", None),
                    (16, "rubric", "{rubric: In Zant schmerzen Welliche Vmb khain}", "{rubric: In toothaches which will not yield}", "Red rubric."),
                    (17, "rubric", "{rubric: arzneÿ nichts geben, solle man brauchen}", "{rubric: to any medicine, one should employ}", "Red rubric."),
                    (18, "rubric", "{rubric: Purgation, Zauffen, aderlaß, schröpff}", "{rubric: purgation, blistering/traction, bloodletting, cupping}", "Red rubric."),
                    (19, "line", "lassen, also das der leib Von der scharffen gall", "[and scarification], so that the body is evacuated of the sharp bile", None),
                    (20, "line", "vnd hizigen geblüett Endtlähret wird.", "and hot blood.", None),
                    (21, "line", "im übrigen khünen auch Volgente mitl gebraucht", "For the rest, the following remedies may also be", None),
                    (22, "line", "werden", "employed:", None),
                    (23, "line", "℞ nim in den Mund ✚ [Essig] darinen gesoden seÿ,", "Take [℞] into the mouth vinegar [✚] wherein has been boiled", None),
                    (24, "line", "saur ampffer wurzel, darmit den mund offt auß", "sorrel root [Rumex acetosa], rinsing the mouth often", None),
                    (25, "line", "gewaschen.", "therewith.", None),
                    (26, "line", "Das Pux öll, ist ein khöstliches mitl in den hollen", "Oil of boxwood [Oleum buxi] is a precious remedy laid into the hollow", None),
                    (27, "line", "Zan gelegt, mit Paum woll ein tropffen. das", "tooth, one drop with cotton-wool. That", None),
                    (28, "line", "[von] dem lign. fraxino, wan solches an S.", "[oil] from ash-wood [lignum fraxini], when it is gathered on St.", None),
                    (29, "line", "Johanes Tag Vor auf gang der ☉ [Sonne] gesamblod", "John's Day [Midsummer, 24 June] before sunrise [☉],", "Astrological/solar herbal harvest at Midsummer dawn."),
                    (30, "line", "wird, vnd gebraucht wie das Pux öll, hat auch die", "and used like the boxwood oil, also possesses the", None),
                    (31, "line", "khrafft.", "[same] virtue.", None),
                    (32, "line", "So hat die spizige saur ampffer, sonderliche", "Likewise the pointed sorrel [Rumex] has a singular", None),
                    (33, "line", "khrafft vnd wirkhung, wan solche im", "virtue and efficacy when it is gathered in", None),
                    (34, "line", "Junij gesamelt wird Vor auf gang der ☉ [Sonne],", "June before the rising of the sun [☉],", None),
                    (35, "line", "im lufft gedört vnd auf den schmerzhafften Zant", "dried in the air, and laid upon the painful tooth.", None),
                    (36, "line", "gelegt. Des gleichen thuett auch die grose", "The great nettle-root [Urtica dioica] does", None),
                    (37, "line", "nösel wurz.", "the same.", None),
                    (38, "rubric", "{rubric: Volgentes Ist auch gar guett.}", "{rubric: The following is also very good:}", "Red rubric."),
                    (39, "line", "℞ öll Cariophilorum. rodi. ℨij. XXX [Camphora] G. xx", "Take [℞] oil of cloves [and] rhodium wood 2 drachms [ℨij], camphor [XXX] 20 grains [G. xx],", None),
                    (40, "line", "[ol.] Therebinth. opt. ℨij misch vnd brauchs auf", "best oil of turpentine 2 drachms [ℨij]; mix and apply it upon", None),
                    (41, "line", "den schmerzhafften Zant.", "the painful tooth.", None),
                    (42, "line", "So ist auch die grose khletten wurz ein", "Likewise the great burdock root [Arctium lappa] is a...", "Continues onto p. 35 (Canvas 12), col. A, l. 1 ('ein gewises mitl')."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 8. CANVAS 12: Page 35 — Dental Caries, Teething & Sublingual Ranula ("Fröschel") with Frog Illustration (b18775275_MS_990_0012.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0012_p35",
        "canvas_num": 12,
        "jp2": "b18775275_MS_990_0012.JP2",
        "orig_page": "35",
        "folio_side": "verso",
        "width": 5417,
        "height": 6853,
        "frame_box": (211, 243, 5189, 6555),
        "center_rule_x": 2819,
        "summary": "Page 35 (verso, numbered '35' in upper-left margin). Column A covers remedies for carious teeth, non-surgical chemical shedding of rotten teeth ('Das die Zant auß falen') using mulberry root steeped in strong vinegar, tooth-preserving and whitening powders (burnt hartshorn, mastic, calcined salt), and infant teething remedies ('Das den khindern die Zant Paldt Wachsen') using butter, honey, and hare's brain ('hasen hirn') rubbed on the gums ('Zant Piller'). Column B opens with a watercolour illustration of a spotted frog ('Fröschel')—a visual pun on sublingual ranula ('Von Fröschel vnder der Zungen / ranula', literally 'little frog')—followed by medical and surgical treatment of ranula (astringent gargles, lancet incision, or venesection of the sublingual vein).",
        "figures": [
            {
                "fig_id": "fig_p35_frog",
                "label": "Watercolour Illustration of a Spotted Frog ('Fröschel' / Ranula Visual Mnemonic, p. 35, Col. B Upper)",
                "ulx": 2819, "uly": 243, "lrx": 5189, "lry": 2030,
                "desc": "Watercolour painting of a brown-and-ochre spotted frog in dorsal view with four webbed feet, serving as a visual-etymological emblem for 'Fröschel vnder der Zungen' (Latin 'ranula', 'little frog', sublingual retention cyst/swelling), above a double yellow-ochre rule.",
            }
        ],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=211..2819, Y=243..6555)",
                "ulx": 211, "uly": 243, "lrx": 2819, "lry": 6555,
                "lines": make_lines("p35", 12, "colA", 211, 243, 2819, 6555, [
                    (1, "line", "[35 |] ein gewises mitl", "[35 |] a certain [sure] remedy.", "Completes sentence from p. 34, col. B, l. 42."),
                    (2, "line", "Oder Nimb 🜘 [Alaun]. 🜖 [Vitriol]. ♁ [Sulphur], ains souil, vnd zerlaß gieß", "Or take alum [🜘], vitriol [🜖], sulphur [♁], of each an equal part, melt it, pour", None),
                    (3, "line", "auf ein stain, vnd brauchs.", "it out upon a stone, and use it.", None),
                    (4, "line", "Pilsen sam gesoden, oder thue Mastix darein", "Henbane seed [Hyoscyamus niger] boiled, or put mastic therein,", None),
                    (5, "line", "wan Vor hero mit 🜔▽ [Salzwasser] gewaschen, hernach", "when washed beforehand with salt water [🜔▽]; afterwards", None),
                    (6, "line", "das philonium romanum gebraucht stilet", "using Philonium Romanum [classic opiate electuary] calms", None),
                    (7, "line", "alle schmerzen.", "all pains.", None),
                    (8, "rubric", "{rubric: Für faule Zant}", "{rubric: For rotten [carious] teeth}", "Red rubric."),
                    (9, "line", "℞. salua. Isop. Rosen marin. Maieran. Minzen", "Take [℞] sage, hyssop, rosemary, marjoram, mint,", None),
                    (10, "line", "āā. pj. Muschat nuß Imber, pertram. āā ℨij", "of each 1 pugil [pinch, pj.], nutmeg, ginger, pellitory-of-Spain, of each 2 drachms [āā ℨij];", None),
                    (11, "line", "stoß alles grob, infudiere es 12 stundt im bösten", "bruise everything coarsely, infuse it for 12 hours in the best", None),
                    (12, "line", "V̈ [Wein], Preß auß vnd nimbs in Mundt, wan man", "wine [V̈], press it out, and take it into the mouth when one", None),
                    (13, "line", "schlaffen geht, also machs offt so hilfft es.", "goes to sleep; do this often and it helps.", None),
                    (14, "rubric", "{rubric: Für die fälung der Zant mach}", "{rubric: For putrefaction [caries] of the teeth, make}", "Red rubric."),
                    (15, "rubric", "{rubric: ein decoctum —}", "{rubric: a decoction —}", "Red rubric."),
                    (16, "line", "Von guetten ✚ [Essig] oder V̈ [Wein] mit Pertram wurzel", "Of good vinegar [✚] or wine [V̈] with pellitory root,", None),
                    (17, "line", "oder Imber, oder lor pör, oder holz wurz", "or ginger, or bayberries, or birthwort [radix cava],", None),
                    (18, "line", "mit disen wasche offt warm den Mund", "with this wash the mouth often while warm;", None),
                    (19, "line", "so ist auch Minzen in ✚ [Essig] gesoden vnd gebraucht,", "mint boiled in vinegar [✚] and used is likewise", None),
                    (20, "line", "gar guett —", "very good —", None),
                    (21, "rubric", "{rubric: Das die Zant auß falen —}", "{rubric: To make [rotten] teeth fall out [without iron] —}", "Red rubric."),
                    (22, "line", "℞. ein starckhen ✚ [Essig] darein thue rad. Moro", "Take [℞] a strong vinegar [✚], put therein mulberry root [radix mori];", None),
                    (23, "line", "hernach thue es auf ein faullen Zant, so falt", "afterwards apply it upon a rotten tooth, and it falls", None),
                    (24, "line", "er [ohne] Mühsal drauß herauß.", "out without trouble.", None),
                    (25, "rubric", "{rubric: Zant Vor der fällung Zu erhalten}", "{rubric: To preserve teeth from decay}", "Red rubric."),
                    (26, "line", "℞. origano Montano, ℨij Isop. glaskhraut", "Take [℞] mountain oregano 2 drachms [ℨij], hyssop, pellitory-of-the-wall [Parietaria],", None),
                    (27, "line", "misch, mit hönig mit gebrandten 🜔 [Salz] ℥iiij", "mix with honey [and] with burnt salt [🜔] 4 ounces [℥iiij],", None),
                    (28, "line", "Pfeffer. ℨiij. mach alles zu ꝑll̵ [Pulver] darmit reib", "pepper 3 drachms [ℨiij]; make everything into powder [ꝑll̵], [and] rub", None),
                    (29, "line", "die Zant. —", "the teeth therewith. —", None),
                    (30, "rubric", "{rubric: Zant Schön Weiß Zu erhalten.}", "{rubric: To keep the teeth beautifully white.}", "Red rubric."),
                    (31, "line", "℞. C. C. ust. ℥iß. Mastich. ℨß. 🜔 [Salz] ✗ [Kalk/Pulver] ℨß", "Take [℞] burnt hartshorn [Cornu Cervi ustum] 1½ ounces [℥iß], mastic ½ drachm [ℨß], calcined salt [🜔 ✗] ½ drachm [ℨß];", None),
                    (32, "line", "f. ꝑll̵ [Pulver]. mis. vnd brauchs, darmit reib die", "make a powder [f. ꝑll̵], mix and use it; rub the", None),
                    (33, "line", "Zandt —", "teeth therewith —", None),
                    (34, "rubric", "{rubric: Das den khindern die Zant Paldt}", "{rubric: That children's teeth may quickly}", "Red rubric."),
                    (35, "rubric", "{rubric: Wachsen.}", "{rubric: grow [teething remedy].}", "Red rubric."),
                    (36, "line", "Putter mit hönig Vermischt, dar mit die", "Butter mixed with honey, rubbing the", None),
                    (37, "line", "Zant Piller geriben.", "gum-ridges [Zahnbiller] therewith.", "Zant Piller = Austro-Bavarian Zahnbiller (alveolar gum-ridges)."),
                    (38, "line", "Wan man die Zantt Piller mit hasen hirn", "When one rubs the gum-ridges with hare's brain,", "Classical Plinian/Galenic sympathetic remedy for painless infant dentition."),
                    (39, "line", "reibt so wachsen die Zant ohne schmerzen.", "the teeth grow forth without pain.", None),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B Lower (Treatise on Sublingual Ranula / 'Fröschel', below Frog Illustration, X=2819..5189, Y=2030..6555)",
                "ulx": 2819, "uly": 2030, "lrx": 5189, "lry": 6555,
                "lines": make_lines("p35", 12, "colB", 2819, 2030, 5189, 6555, [
                    (1, "rubric", "{rubric: Von Fröschel vnder der Zungen}", "{rubric: Of the 'little frog' [Ranula] under the tongue}", "Red rubric below the double yellow-ochre rule under the painted frog."),
                    (2, "line", "ranula. oder fröschel vnder der Zungen, ist ein geschw=", "Ranula, or the 'little frog' under the tongue, is a swel-", None),
                    (3, "line", "ulst vnder der Zungen, so groß als ein Poon oder", "ling under the tongue, as large as a bean or", None),
                    (4, "line", "Muschat nuß, darin ist gemeinigkhlich ein schleim", "nutmeg; therein is commonly a mucus [phlegm]", None),
                    (5, "line", "oder blüett, so in Entzündung Verursacht, vnd", "or blood, which in inflammation causes [pain] and", None),
                    (6, "line", "zu eüter gehen will. Wan die geschwulst ohne", "tends to suppurate. When the swelling is without", None),
                    (7, "line", "Entzündung, Von ledigen schleim ist, soll man", "inflammation, arising from simple phlegm/mucus, one should", None),
                    (8, "line", "Volgentes gurgel ▽ [Wasser] brauchen.", "use the following gargle-water [▽]:", None),
                    (9, "line", "℞. rad. pentafilon. rad. althea. āā ℥ij. rad. piri=", "Take [℞] cinquefoil root [Potentilla reptans], marshmallow root, of each 2 ounces [āā ℥ij], pellitory", None),
                    (10, "line", "trom. ℨj. salbeÿ, hendrichl blüe, hasel wurtzen,", "root 1 drachm [ℨj], sage, ground-ivy blossoms, asarabacca root,", None),
                    (11, "line", "āā. Mj. anis, lorchen schwam, āā. ℨj. siede alles", "of each 1 handful [āā Mj.], anise, larch agaric [Polyporus officinalis], of each 1 drachm [āā ℨj]; boil everything", None),
                    (12, "line", "in ℔v frischen ▽ [Wasser] biß der drite Thaill ein gesoden", "in 5 pounds [℔v] of fresh water [▽] until the third part has boiled away;", None),
                    (13, "line", "hernach seichs, vnd thue dar zue Nuß safft vnd rosen", "afterwards strain it, and add thereto walnut-juice [Rob nucum] and rose-", None),
                    (14, "line", "hönig, āā. ℥j. 🜘 [Alaun]. ℨj. Darmit muess man den", "honey, of each 1 ounce [āā ℥j], alum [🜘] 1 drachm [ℨj]. Therewith one must", None),
                    (15, "line", "Mund offt warm auß schwenkhen, vnd allezeit dar", "rinse out the mouth often while warm, and always", None),
                    (16, "line", "nach Volgetes lattwergl, einer Nuß groß", "afterwards hold the following electuary, the size of a walnut,", None),
                    (17, "line", "Vnder die Zung halten.", "under the tongue:", None),
                    (18, "line", "℞. Nuß safft, Rosen hönig, āā ℥j. Rauten sam ꝑll̵ [Pulver] ℨij", "Take [℞] walnut-juice, rose-honey, of each 1 ounce [āā ℥j], rue-seed powder [ꝑll̵] 2 drachms [ℨij],", None),
                    (19, "line", "Mithridato ℨj. gewürz Nägel 20. grän misch", "mithridatium 1 drachm [ℨj], cloves 20 grains; mix", None),
                    (20, "line", "alles vnder ein ander, zu einer latt wergl. Wan", "everything together into an electuary. When", None),
                    (21, "line", "darauf die geschwulst weich vnd lind wird muess", "thereupon the swelling becomes soft and yielding, one must", None),
                    (22, "line", "mans eröffnen, mit einer Lanzet, so wird ein", "open [incise] it with a lancet, and a", "Classic surgical marsupialization/incision of a sublingual ranula."),
                    (23, "line", "schleimige rozige Materj herauß lauffen. man khan", "slimy, mucoid matter will run out; one can", None),
                    (24, "line", "hernach die öffnung schaden mit den Mund ▽ [Wasser] auß", "afterwards heal the incised lesion with the mouth-water [▽]", None),
                    (25, "line", "heillen, mit den Nuß safft Vermischt.", "mixed with the walnut-juice.", None),
                    (26, "line", "Im übrigen muess man würklich die Evacuation nit", "For the rest, one must indeed not neglect systemic", None),
                    (27, "line", "Vergessen. — Wan aber die geschwulst mit", "evacuation. — When, however, the swelling is accompanied by", None),
                    (28, "line", "einer hiz ist soll man warme Milch, darinen feigen", "heat [inflammation], one should hold warm milk wherein figs,", None),
                    (29, "line", "Eibisch, vnd saffran gesoden, im mund halten, so wird", "marshmallow, and saffron have been boiled, in the mouth, and the", None),
                    (30, "line", "sich die geschwär baldt zeittigen, vnd öffnen, wan es", "abscess will quickly mature [ripen] and open; when it is", None),
                    (31, "line", "offen, so khan mans mit rosen hönig, mit Bolus", "open, one can heal it with rose-honey mixed with Armenian", None),
                    (32, "mixed", "armeni Vermischt heillen. {rubric: Oder brauch}", "bole [Bolus armena]. {rubric: Or use:}", "Inline red rubric 'Oder brauch'."),
                    (33, "line", "℞. Nuß khern rosen hönig Pfeffer 🜔 [Salz] Vnder ein", "Take [℞] walnut kernels, rose-honey, pepper, [and] salt [🜔], pounded", None),
                    (34, "line", "woll Zerstossen, vnd offt dar mit geriben, wan es", "well together, and rub often therewith; if it", None),
                    (35, "line", "nit baldt darauff böser wirdt, so eröffne die", "does not soon get better thereupon, then open the", None),
                    (36, "line", "ader Vnder der Zungen biß es woll auß", "vein under the tongue [sublingual venesection, vena ranina] until it", None),
                    (37, "line", "anfangt blüetten —", "bleeds out freely —", None),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 9. CANVAS 13: Page 36 — Loose Teeth Disclaimer, Four Teeth Study & Oral Syringe Portrait (b18775275_MS_990_0013.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0013_p36",
        "canvas_num": 13,
        "jp2": "b18775275_MS_990_0013.JP2",
        "orig_page": "36",
        "folio_side": "recto",
        "width": 5047,
        "height": 6853,
        "frame_box": (257, 282, 4824, 6479),
        "center_rule_x": 2543,
        "summary": "Page 36 (recto, numbered '36' in upper-right margin). Upper Column A displays a watercolour study of four human teeth (single-, two-, and three-rooted) above a candid first-person clinical warning on treating loose teeth ('Rogle Zant föst machen'): 'one reaps more disgrace than honor therewith... if it does not help you, do not blame me, blame your own sour scorbutic blood!'. Includes astringent electuaries, Croll's Lapis medicamentosus with Gum Lac, and live crayfish pounded with burdock root to regenerate gums. Column B treats tooth whitening and features a watercolour profile portrait of a patient injecting his mouth with a brass syringe, introducing 'Vnderschidtliche Mundt oder Einspritz Wasser' (mouth- and syringe-waters for loose teeth and mercurial salivation).",
        "figures": [
            {
                "fig_id": "fig_p36_teeth",
                "label": "Watercolour Study of Four Single- and Multi-Rooted Human Teeth (p. 36, Col. A Upper)",
                "ulx": 257, "uly": 282, "lrx": 2543, "lry": 1450,
                "desc": "Watercolour anatomical row of four extracted human teeth showing a single-rooted premolar, conical canine/incisor, bifurcated molar, and trifurcated molar above a double yellow-ochre rule.",
            },
            {
                "fig_id": "fig_p36_syringe",
                "label": "Watercolour Profile Portrait of a Patient Using a Brass Oral Syringe (p. 36, Col. B Middle)",
                "ulx": 2543, "uly": 3780, "lrx": 4824, "lry": 5400,
                "desc": "Watercolour half-length profile of a male patient wearing a striped cap and red tunic with a turned brass wound/oral syringe ('Einspritz-Spritze') inserted into his mouth, above a double yellow-ochre rule.",
            },
        ],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A Lower (Treatise on Loose Teeth below Four-Teeth Illustration, X=257..2543, Y=1450..6479)",
                "ulx": 257, "uly": 1450, "lrx": 2543, "lry": 6479,
                "lines": make_lines("p36", 13, "colA", 257, 1450, 2543, 6479, [
                    (1, "rubric", "{rubric: Rogle Zant föst machen}", "{rubric: To make loose [mobile] teeth firm}", "Red rubric below the double yellow-ochre rule; rogle = locker/wackelig."),
                    (2, "line", "Diser Zuestand ist hart vnd schwär zu Curiern", "This condition is hard and difficult to cure,", None),
                    (3, "line", "Vnd man hebt mehr schandt als Ehr darmit auf", "and one reaps more disgrace than honor therewith,", "Candid 17th-century practitioner's aside on the prognosis of severe periodontal disease."),
                    (4, "line", "weillen selten ein guetter Effect erfolgt", "because a good effect rarely follows.", None),
                    (5, "line", "die Vrsach ist dises, weillen zum öfftern vnd mehr=", "The reason is this: because most often and repeat-", None),
                    (6, "line", "mallen ein saures scharffes scorbutisches geblüet", "edly a sour, sharp, scorbutic blood", None),
                    (7, "line", "die Zant rogel macht, Welches häutlein vnd Ner=", "makes the teeth loose, which consumes the membranes [periodontium] and", None),
                    (8, "line", "vlen sambt den fleisch Verzehrt vnd wekh", "small nerves together with the gum-flesh and eats them", None),
                    (9, "line", "frißt, also brauch dises vnd hernach mehr Volg=", "away; therefore use this and afterwards more of the follow-", None),
                    (10, "line", "ente sachen, die Zant fest zu machen, hilfft es", "ing things to make the teeth firm: if it does not", None),
                    (11, "line", "nit so schadt es nit, hilfft dich nit sag nit", "help, it does no harm; if it does not help you, do not say", None),
                    (12, "line", "ich hab die schlechte, der Zunge schon Vorgehalten", "I gave you bad [remedies], for my tongue has already forewarned you", None),
                    (13, "line", "du hast es braucht vnd nit geholffen, sondern sage", "that you used it and it did not help; rather say", None),
                    (14, "line", "dein blüett seÿ schlecht vnd scharff, die Zant vnd", "that your own blood is bad and sharp, eating away the teeth and", None),
                    (15, "line", "fleisch wekh friß, gib also die schuldt nicht mir sonder", "flesh—so do not lay the blame on me, but on", None),
                    (16, "line", "Dier.", "yourself!", None),
                    (17, "line", "℞. Mangranden schallen ℥ß, saluia Mj. khoche in", "Take [℞] pomegranate rind ½ ounce [℥ß], sage 1 handful [Mj.]; boil in", None),
                    (18, "line", "rothen V̈ [Wein], vnd wasch den mund darmit, zum öfftern", "red wine [V̈], and wash the mouth therewith; most often,", None),
                    (19, "line", "mall, aber thue noch dar zue nach dem es", "however, add thereto after it has", None),
                    (20, "line", "gesoden, vnd gesigen, des decocto ℥xij. 🜔 ♄ [Sal Saturni] ℨj.", "boiled and been strained, to 12 ounces [℥xij] of the decoction, salt of lead [🜔 ♄] 1 drachm [ℨj];", None),
                    (21, "mixed", "misch vnd brauchs. {rubric: Oder dises.}", "mix and use it. {rubric: Or this:}", "Inline red rubric 'Oder dises.'."),
                    (22, "line", "℞. 🜘 [Alaun]. ℨß. 🜖 [Vitriol] uirid. ℨj ol. Cariophilor", "Take [℞] alum [🜘] ½ drachm [ℨß], green vitriol [🜖 virid.] 1 drachm [ℨj], oil of cloves", None),
                    (23, "line", "G. vj. mis f. ꝑll̵ [Pulver]. darmit reibe täglich 2 mall die", "6 drops [G. vj]; mix, make a powder [ꝑll̵]; rub the teeth therewith twice daily,", None),
                    (24, "line", "Zant, vnd mit rosen ▽ [Wasser] widerumb auß gewaschen", "and rinse out again with rose-water [▽].", None),
                    (25, "rubric", "{rubric: Lattwergung für Rogle Zant.}", "{rubric: Electuary for loose teeth.}", "Red rubric."),
                    (26, "line", "℞. G. A. Sarcocolla. Sang: dracon: Galla:", "Take [℞] Gum Arabic, sarcocolla, dragon's blood, oak galls,", None),
                    (27, "line", "🜘 [Alaun] usti Bol. arm. alloe Epatica. āā. ℨj.", "burnt alum [🜘 usti], Armenian bole, hepatic aloe, of each 1 drachm [āā ℨj],", None),
                    (28, "line", "Conserua. rosar. alles Zusamen Vermischt Zu", "conserve of roses; mix everything together into", None),
                    (29, "line", "einer lattwerg, vnd alle tag 3 od[er] 4 mall apliciert.", "an electuary, and apply 3 or 4 times every day.", None),
                    (30, "rubric", "{rubric: Ein anders}", "{rubric: Another}", "Red rubric."),
                    (31, "line", "℞. Lap. medicamentos. ℥iß dissolut. in ▽ [Wasser] Torm=", "Take [℞] Lapis medicamentosus [Croll's medicinal stone] 1½ ounces [℥iß], dissolved in tormentil", None),
                    (32, "line", "endil q. s. darzue thue gebrandten 🜘 [Alaun] ℨß. wan", "water [▽] as much as suffices [q.s.]; add thereto burnt alum [🜘] ½ drachm [ℨß]; when", None),
                    (33, "line", "sich der 🜘 [Alaun] hat soluieret, so thue dar zue, Gum:", "the alum [🜘] has dissolved, add thereto Gum", None),
                    (34, "line", "Laca ℨj. laß in der Wärm stehn so wird es", "Lac [Gummi laccae] 1 drachm [ℨj]; let it stand in the warmth and it will", "Tinctura laccae = classic 17th-century antiscorbutic gingival tincture."),
                    (35, "line", "schön rott, als dan filtrieres vnd brauchs —", "turn beautifully red; then filter it and use it —", None),
                    (36, "rubric", "{rubric: Das Zant fleisch Widerumb Wachsen}", "{rubric: To make the gum-flesh grow back again}", "Red rubric; small quire numeral '4' at left."),
                    (37, "rubric", "{rubric: machen}", "{rubric: [grow back]:}", "Red rubric."),
                    (38, "line", "℞. 6. lebendige Kg [Krebse]. auß einen frischen ▽ [Wasser].", "Take [℞] 6 live river-crayfish out of fresh running water [▽],", "Continues across column break to col. B upper, l. 1."),
                ]),
            },
            {
                "col_id": "colB_upper",
                "col_label": "Column B Upper (Gingival Regeneration & Tooth Whitening, above Syringe Portrait, X=2543..4824, Y=282..3780)",
                "ulx": 2543, "uly": 282, "lrx": 4824, "lry": 3780,
                "lines": make_lines("p36", 13, "colB_up", 2543, 282, 4824, 3780, [
                    (1, "line", "khletten wurzel ℥j. stoße mit ein ander [36]", "burdock root 1 ounce [℥j]; pound them together [36]", "Completes recipe from col. A, l. 38; page number '36' in upper-right box."),
                    (2, "line", "Zu einen Mueß, das treibe durch mit thut khra=", "into a pulp; strain this through with red corn-", None),
                    (3, "line", "Plumen ▽ [Wasser], seichs vnd drukhs hart auß, dar Von nimb.", "poppy [or cornflower] water [▽], strain and press it out hard; thereof take", None),
                    (4, "line", "alle 2 stundt in Mundt, 2 od[er] 3 löffel Voll. —", "into the mouth every 2 hours, 2 or 3 spoonfuls. —", None),
                    (5, "rubric", "{rubric: Ein Anders}", "{rubric: Another}", "Red rubric."),
                    (6, "line", "℞. flor. malua Melampem ℨß. Mell rosar.", "Take [℞] hollyhock [black mallow] flowers ½ drachm [ℨß], honey of roses", None),
                    (7, "line", "q. s. 🜘 [Alaun]. Crud. ℨj ☿ [Tartarus]. ℨj. fischen Pägel ℨß. dises", "as much as suffices [q.s.], crude alum [🜘] 1 drachm [ℨj], tartar 1 drachm [ℨj], cuttlefish bone [os sepiae] ½ drachm [ℨß]; all", None),
                    (8, "line", "alles Vnder ein ander in ein Morser zer riben, vnd", "this ground together in a mortar, and", None),
                    (9, "line", "täglich 2 mall das Zant fleisch darmit geriben.", "rub the gums therewith twice daily.", None),
                    (10, "rubric", "{rubric: Die Zant Schön Weiß machen.}", "{rubric: To make the teeth beautifully white.}", "Red rubric."),
                    (11, "line", "Wan die Zant, faul, schwarz stinkhet vnd Vn=", "When the teeth are foul, black, stinking, and un-", None),
                    (12, "line", "flättig seind, so mach sÿe sauber vnd weiß auf", "clean, make them clean and white in the", None),
                    (13, "line", "Volgente manier.", "following manner:", None),
                    (14, "line", "℞. sp[iritus] 🜔 [Salis], uel. ♁ [Sulphuris], uel 🜖 [Vitrioli], mit khran ▽ [Wasser]", "Take [℞] spirit of salt [hydrochloric acid], or of sulphur, or of vitriol, mixed with", "Mineral acid scaling/bleaching followed by immediate alkaline/mucilaginous rinse."),
                    (15, "line", "oder Violen safft Vermischt, vnd saluia, Nez Paum=", "horseradish water [▽] or violet syrup, and sage; moisten cotton-", None),
                    (16, "line", "woll darein, vnd reibe die Zant darmit, so werden", "wool therein, and rub the teeth therewith, and they will", None),
                    (17, "line", "sÿe gleich weiß, man muess aber gleich widerumb, den", "immediately turn white; yet one must immediately afterwards", None),
                    (18, "line", "Mund mit Potten [Pappeln] ▽ [Wasser] oder wegerich ▽ [Wasser] widerumb", "rinse out the mouth again with mallow water [▽] or plantain water [▽].", None),
                    (19, "line", "auß waschen. der es aber hernach sauber erhalten", "Whoever wishes afterwards to keep them clean,", None),
                    (20, "line", "will, das sÿ nit widerumb Vnsauber werden,", "so that they do not become foul again,", None),
                    (21, "line", "der solle alle morgen das Volgente ꝑll̵ [Pulver] brauchen", "should every morning use the following tooth-powder [ꝑll̵]:", None),
                    (22, "line", "℞. C. C. ust. Corallor. rub. osso sepie. Perle od[er]", "Take [℞] burnt hartshorn [C. C. ust.], red coral, cuttlefish bone [os sepiae], pearl or", None),
                    (23, "line", "gedörte Prot rinden ☿ [Tartarus]. āā ℨß. löffel khraut sam", "toasted bread-crust, cream of tartar, of each ½ drachm [āā ℨß], scurvy-grass seed,", None),
                    (24, "line", "allabaster, Cimet āā. ℨj. mach ein groblechtes Zant", "alabaster, cinnamon, of each 1 drachm [āā ℨj]; make a coarse tooth-", None),
                    (25, "line", "ꝑll̵ [Pulver] darauß.", "powder [ꝑll̵] thereof.", None),
                ]),
            },
            {
                "col_id": "colB_lower",
                "col_label": "Column B Lower (Mouth & Syringe-Injection Waters, below Syringe Portrait, X=2543..4824, Y=5400..6479)",
                "ulx": 2543, "uly": 5400, "lrx": 4824, "lry": 6479,
                "lines": make_lines("p36", 13, "colB_low", 2543, 5400, 4824, 6479, [
                    (26, "rubric", "{rubric: Vnderschidtliche Mundt oder}", "{rubric: Various Mouth- or}", "Red rubric below the double yellow-ochre rule under the syringe portrait."),
                    (27, "rubric", "{rubric: Einspritz Wasser —}", "{rubric: Syringe-Injection Waters —}", "Red rubric."),
                    (28, "rubric", "{rubric: Ein khöstliches gurgel Wasser in den}", "{rubric: A precious gargle-water in}", "Red rubric."),
                    (29, "rubric", "{rubric: Roglen Zanten vnd saliuation.}", "{rubric: loose teeth and [mercurial] salivation.}", "Red rubric; saliuation = ptyalism induced by mercury therapy."),
                    (30, "line", "℞. schlehen wurzel rinden, gipffel Von felber,", "Take [℞] blackthorn root-bark [Prunus spinosa], tops of willow,", None),
                    (31, "line", "āā. Mj. Papel blie, ros. rub. āā. Miiij schlehen", "of each 1 handful [āā Mj.], mallow flowers, red roses, of each 4 handfuls [āā Miiij], sloes", None),
                    (32, "line", "Miiij. wegerich ām Mij. Cipres nuß, linsen,", "4 handfuls [Miiij], both plantains 2 handfuls [Mij.], cypress nuts, lentils...", "Continues onto p. 37 (Canvas 14), col. A, l. 1."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 10. CANVAS 14: Page 37 — Tormentil Gargle, Stored Dry Gargle Herbs & Throat Ulcers (b18775275_MS_990_0014.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0014_p37",
        "canvas_num": 14,
        "jp2": "b18775275_MS_990_0014.JP2",
        "orig_page": "37",
        "folio_side": "verso",
        "width": 5352,
        "height": 6853,
        "frame_box": (470, 246, 5111, 6542),
        "center_rule_x": 2783,
        "summary": "Page 37 (verso, numbered '37' in upper-left margin). Column A completes the syringe-injection water from p. 36, then gives a comprehensive Tormentil-root gargle for scurvy ('Mund fäul Scharbokh'), a honey-electuary for eroded gums, and a compound herbal mixture to be kept dried in a box ('in einer geschachtl behalten') for instant preparation of gargle-waters. Column B gives insufflation and gargle remedies for a prolapsed uvula (blowing celandine root powder, nitre '🜕', or sugar of lead 'Sachari ♄'), tonsillar abscesses, deep throat ulcers ('dieffe löcher im hals'), and mercurial salivation using oak bark and Album Graecum.",
        "figures": [],
        "columns": [
            {
                "col_id": "colA",
                "col_label": "Column A (Left Column, within red rules X=470..2783, Y=246..6542)",
                "ulx": 470, "uly": 246, "lrx": 2783, "lry": 6542,
                "lines": make_lines("p37", 14, "colA", 470, 246, 2783, 6542, [
                    (1, "line", "[37 |] sumac. āā. ℥ß. Zerstoß alles darzue", "[37 |] sumac, of each ½ ounce [āā ℥ß]; bruise everything and add thereto", "Completes recipe from p. 36, col. B lower, l. 32."),
                    (2, "line", "thue, Mj gersten, vnd siede es in ✚ [Essig] vnd V̈ [Wein], biß daß", "1 handful [Mj.] of barley, and boil it in vinegar [✚] and wine [V̈] until", None),
                    (3, "line", "der drite Thaill ein gesoden. Zu der abgesigen", "the third part has boiled away. To the strained", None),
                    (4, "line", "Prüe, thuet man rosen hönig vnd maull Pör", "broth [decoction] one adds rose-honey and mulberry", None),
                    (5, "line", "safft, āā ℥iß 🜘 [Alaun] usti ℨij. darmit sprüze ein vnd", "syrup, of each 1½ ounces [āā ℥iß], burnt alum [🜘 usti] 2 drachms [ℨij]; syringe [inject] therewith and", None),
                    (6, "line", "gurgle dich —", "gargle —", None),
                    (7, "rubric", "{rubric: Mundt oder Gurgel Wasser. Von der}", "{rubric: Mouth- or Gargle-Water of}", "Red rubric."),
                    (8, "rubric", "{rubric: Tormendil wurzel.}", "{rubric: Tormentil root [Potentilla erecta].}", "Red rubric."),
                    (9, "line", "℞. Tormendill wurzel, Calmuß wurz, āā. ℥j.", "Take [℞] tormentil root, calamus root, of each 1 ounce [āā ℥j],", None),
                    (10, "line", "Cort. Granat: rad. achacia, āā. ℥ß. flor.", "pomegranate rind, acacia [sloe] root, of each ½ ounce [āā ℥ß], pomegranate", None),
                    (11, "line", "Granator. 🜘 [Alaun]. āā. ℨiij. rosen marin, fünfffinger", "blossoms [balaustines], alum [🜘], of each 3 drachms [āā ℨiij], rosemary, cinquefoil", None),
                    (12, "line", "khraut vnd wurtzen, khleine hauß wurz, saluia", "herb and root, lesser houseleek [Sedum], sage,", None),
                    (13, "line", "wegerich, Isop, āā. ℥ij. Calendula, rosa rub. āā", "plantain, hyssop, of each 2 ounces [āā ℥ij], marigold, red roses, of each", None),
                    (14, "line", "℥j. stoß vnd schneidt alles grob, siede es in ▽ [Wasser] vnd", "1 ounce [āā ℥j]; bruise and chop everything coarsely, boil it in water [▽] and", None),
                    (15, "line", "✚ [Essig] āā ℔iß. laß den driten Thaill ein sieden,", "vinegar [✚], of each 1½ pounds [āā ℔iß], let a third part boil away,", None),
                    (16, "line", "seichs vnd druckhs, misch mit gnueg hönig das es", "strain and press it, mix with sufficient honey so that it", None),
                    (17, "line", "süeß seÿ. dises wasser heillet die rogle Zant,", "becomes sweet. This water heals loose teeth,", None),
                    (18, "line", "Mund fäul Scharbokh, das Verlohrne Zant fleisch,", "mouth-rot, scurvy [Scharbock], lost gum-flesh,", None),
                    (19, "line", "vnd dienet Zu allen Gebrechen des Mundts vnd Zäpffel", "and serves for all afflictions of the mouth and uvula.", None),
                    (20, "rubric", "{rubric: Wan das Zant fleisch Verfault}", "{rubric: When the gum-flesh is rotted}", "Red rubric."),
                    (21, "rubric", "{rubric: Vnd durch fressen Ist —}", "{rubric: and eaten through —}", "Red rubric."),
                    (22, "line", "℞. agleÿ ꝑll̵ [Pulver], salua, khraußte Minzen, Muscatnuß", "Take [℞] columbine [Aquilegia] powder [ꝑll̵], sage, curled mint, nutmeg,", None),
                    (23, "line", "āā. ℨß. 🜘 [Alaun] ustj ℨj. guettes hönig, ℥iij. laß", "of each ½ drachm [āā ℨß], burnt alum [🜘 ustj] 1 drachm [ℨj], good honey 3 ounces [℥iij]; let", None),
                    (24, "line", "das hönig gemach sieden, vnd Verschaumbs, hernach", "the honey boil gently and skim off the foam; afterwards", None),
                    (25, "line", "Rühre das ꝑll̵ [Pulver] darein, mit disen bestreich täg=", "stir the powder [ꝑll̵] therein; anoint the gums therewith", None),
                    (26, "line", "lich das Zant fleisch, 3 oder 4 mall.", "3 or 4 times daily.", None),
                    (27, "rubric", "{rubric: Khräuter Zum Gurgel Wasser}", "{rubric: Herbs for Gargle-Water}", "Red rubric."),
                    (28, "rubric", "{rubric: dürr Zu behalten}", "{rubric: to keep dried [in store]}", "Red rubric."),
                    (29, "line", "℞. Praunellen, Erd bör khraut, vnd wurzel", "Take [℞] self-heal [Prunella], strawberry herb and root,", None),
                    (30, "line", "Praun wegerich, Ehren Preiß, oder menig,", "ribwort plantain, speedwell [Veronica], agrimony [Odermennig],", None),
                    (31, "line", "Rotte Papel rosen, Teüffels abiß khraut vnd", "red hollyhock flowers, devil's-bit scabious herb and", None),
                    (32, "line", "wurzel āā Mj. Isop, Mij. feigen No: 12", "root, of each 1 handful [āā Mj.], hyssop 2 handfuls [Mij.], 12 figs.", None),
                    (33, "line", "Die khräuter werden grob Zerschniden, vnd in", "The herbs are coarsely chopped and kept in", None),
                    (34, "line", "einer geschachtl behalten Zum gebrauch. Von disen", "a box for use. Of these", "Monastic apothecary stock-formulary instruction ('in einer geschachtl behalten')."),
                    (35, "line", "Nimbt man hernach ein oder 2 od[er] 3 händl", "one afterwards takes 1, 2, or 3 small handfuls,", None),
                    (36, "line", "Voll, nach dem man will Vill wasser sieden", "according as one wishes to boil much water,", None),
                    (37, "line", "siede es in wasser, mach es mit hönig ein", "boils it in water, sweetens it a little with", None),
                    (38, "line", "wenig süeß, vnd souill allaun das man", "honey, and adds so much alum that one", None),
                    (39, "line", "mörkht, oder empfind das ein wenig Zusam", "perceives or feels that it is slightly", None),
                    (40, "line", "Ziehent ist, so hast ein perfectes gurgel od[er]", "astringent; thus you have a perfect gargle- or", None),
                    (41, "line", "mund wasser —", "mouth-water —", None),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B (Right Column, within red rules X=2783..5111, Y=246..6542)",
                "ulx": 2783, "uly": 246, "lrx": 5111, "lry": 6542,
                "lines": make_lines("p37", 14, "colB", 2783, 246, 5111, 6542, [
                    (1, "rubric", "{rubric: Zum ab gefallnen Zäpffel Thuet}", "{rubric: For a fallen [prolapsed] uvula, this works}", "Red rubric."),
                    (2, "rubric", "{rubric: Wunder Wirkhen}", "{rubric: wonders:}", "Red rubric."),
                    (3, "line", "Wan man nimbt rad: Chelidonia ꝑll̵ [Pulver] vnd", "When one takes greater celandine root [Chelidonium majus] powder [ꝑll̵] and", None),
                    (4, "line", "ein geblasen.", "blows it in [insufflates it upon the uvula].", None),
                    (5, "line", "Die Entzündung des Zäpffel Nimbt ein Jedes", "Every gargle-water [▽] takes away inflammation of the", None),
                    (6, "line", "gurgel ▽ [Wasser] wan man 🜕 [Salpeter], oder Sachari", "uvula when one mixes nitre [🜕, saltpetre] or sugar", "🜕 = Nitrum / Salpeter (circle with vertical bar)."),
                    (7, "line", "♄ [Saturni] darein Vermischt.", "of lead [Saccharum Saturni, ♄] therein.", "♄ = Saturnus / Blei (lead)."),
                    (8, "rubric", "{rubric: In den Mandl geschwär —}", "{rubric: In tonsillar abscess [quinsy] —}", "Red rubric."),
                    (9, "line", "℞ holler wurzel ▽ [Wasser], darmit gurgle dich, es", "Take [℞] elder-root water [▽], gargle therewith; it", None),
                    (10, "line", "heillet alle geschwär des mundts.", "heals all ulcers of the mouth.", None),
                    (11, "line", "oder Nimb Mors diabuli, siede es in ℔j ▽ [Wasser]", "Or take devil's-bit [Morsus diaboli], boil it in 1 pound [℔j] of water [▽],", None),
                    (12, "line", "laß halb einsieden, darmit gurgle dich, ist", "let it boil down by half, gargle therewith: it is", None),
                    (13, "line", "ein sonderliches Experiment, wider die hals", "a singular experiment [proven specific] against throat", None),
                    (14, "line", "geschwär, vnd mandl geschwulst.", "ulcers and swelling of the tonsils.", None),
                    (15, "rubric", "{rubric: Oder —}", "{rubric: Or —}", "Red rubric."),
                    (16, "line", "℞. süeß holz, ℨij. wein börl ℥ß. feigen 6.", "Take [℞] licorice root 2 drachms [ℨij], currants/raisins ½ ounce [℥ß], 6 figs,", None),
                    (17, "line", "Papel rosen, No: v. siede alles in frischer milch", "5 hollyhock flowers; boil everything in fresh milk", None),
                    (18, "line", "mit 2 löffel rosen hönig.", "with 2 spoonfuls of rose-honey.", None),
                    (19, "rubric", "{rubric: Oder —}", "{rubric: Or —}", "Red rubric."),
                    (20, "line", "℞. frische milch darein siede papel Eibisch, Veigl", "Take [℞] fresh milk, boil therein mallow, marshmallow, violet", None),
                    (21, "line", "khraut, feigen Jedes nach beliben, hönig seichs durch", "herb, figs, of each at pleasure, [and] honey; strain it through", None),
                    (22, "line", "vnd gurgle dich.", "and gargle.", None),
                    (23, "rubric", "{rubric: Mundt Wasser Wan dieffe löcher}", "{rubric: Mouth-Water when deep holes [ulcers]}", "Red rubric."),
                    (24, "rubric", "{rubric: im hals seindt.}", "{rubric: are in the throat.}", "Red rubric."),
                    (25, "line", "℞. Cipres nuß, gebrandten 🜘 [Alaun], lebendigen ♁ [Schwefel]", "Take [℞] cypress nuts, burnt alum [🜘], native sulphur [♁],", None),
                    (26, "line", "Pertram weixach, Mastix, guetten Gallus,", "pellitory, frankincense, mastic, good oak-galls,", None),
                    (27, "line", "margranden schallen, rosen Plöder, āā. ℨj.", "pomegranate rind, rose petals, of each 1 drachm [āā ℨj];", None),
                    (28, "line", "machs Zu ꝑll̵ [Pulver], vnd misch, mit V̈ [Wein] od[er] ▽ [Wasser] Von", "make into powder [ꝑll̵], and mix with wine [V̈] or water [▽] of", None),
                    (29, "line", "aichen laub āā. ℥v. schlehen safft, vnd Citronen", "oak leaves, of each 5 ounces [āā ℥v], sloe juice, and lemon", None),
                    (30, "line", "safft āā. ℥ß. misch vnd brauchs.", "juice, of each ½ ounce [āā ℥ß]; mix and use it.", None),
                    (31, "rubric", "{rubric: Mundt Wasser in der saliuaion}", "{rubric: Mouth-Water in [mercurial] salivation}", "Red rubric."),
                    (32, "line", "℞. Nimb aiches laub, Mj. saluia, Pron Pör", "Take [℞] oak leaves 1 handful [Mj.], sage, blackberry", None),
                    (33, "line", "laub, löffel khraut, āā. Miß. mitl rinden Von", "leaves, scurvy-grass, of each 1½ handfuls [āā Miß.], middle bark of", None),
                    (34, "line", "Jungen aich Paum, ℥j. 🜘 [Alaun]. ℨij. alb. Grecum. ℨj", "a young oak tree 1 ounce [℥j], alum [🜘] 2 drachms [ℨij], Album Graecum 1 drachm [ℨj];", None),
                    (35, "line", "thue alles in ein saubern haffen, vnd gieß dar", "put everything into a clean pot, and pour thereon", None),
                    (36, "line", "auf Prun ▽ [Wasser] ℔iiij. vnd ℔j. V̈ [Wein] ein löffel Voll", "spring-water [▽] 4 pounds [℔iiij] and 1 pound [℔j] of wine [V̈], a spoonful of", None),
                    (37, "line", "Rosen hönig, darmit gurgle den mund des tags", "rose-honey; gargle the mouth therewith", None),
                    (38, "line", "wenigist 4 mall, biß die Zant widerumb föst", "at least 4 times a day, until the teeth become firm", None),
                    (39, "mixed", "werden. {rubric: Mundt Wasser Wan}", "again. {rubric: Mouth-Water when}", "Inline red rubric."),
                    (40, "rubric", "{rubric: Löcher vnd Schrunden im halß.}", "{rubric: there are ulcers and fissures in the throat.}", "Continues onto p. 38 (Canvas 15)."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # CANVASES 15–24: Pages 38–47 (Transcribed & Translated with Gemini 3.8 Flash)
    # --------------------------------------------------------------------------
    *PAGES_BATCH2,

    # --------------------------------------------------------------------------
    # 11. CANVAS 25 (+ CANVASES 727–730): Page 48 — Laminated Flap Anatomy of the Eye
    # --------------------------------------------------------------------------
    {
        "page_id": "c0025_p48",
        "canvas_num": 25,
        "jp2": "b18775275_MS_990_0025.JP2",
        "orig_page": "48",
        "folio_side": "recto",
        "width": 5283,
        "height": 6853,
        "frame_box": (220, 334, 4881, 6464),
        "center_rule_x": 2551,
        "flap_canvases": [
            {
                "state": 1,
                "canvas_num": 25,
                "alt_canvas_num": 727,
                "jp2": "b18775275_MS_990_0025.JP2",
                "alt_jp2": "b18775275_MS_990_0727.JP2",
                "ulx": 910, "uly": 1520, "lrx": 2360, "lry": 3790,
                "label": "State 1 (Flaps Closed): Outer Tunic F (Conjunctiva/Sclera with vascular arborization), Cornea G, Pupil H, Optic Stalk A/B/D/E.",
            },
            {
                "state": 2,
                "canvas_num": 728,
                "jp2": "b18775275_MS_990_0728.JP2",
                "ulx": 850, "uly": 1520, "lrx": 2250, "lry": 3790,
                "label": "State 2 (First Flap F Lifted): Reveals Optic Nerve Sheath K-K, Dark Choroid/Uvea Tunic I (with vascular arborization), and Pupil/Iris H/R.",
            },
            {
                "state": 3,
                "canvas_num": 729,
                "jp2": "b18775275_MS_990_0729.JP2",
                "ulx": 850, "uly": 1350, "lrx": 2250, "lry": 3790,
                "label": "State 3 (Second Flap I Lifted): Reveals Net-like Retina Tunic L (Tunica retiformis ò retina) enclosing the Vitreous Humor.",
            },
            {
                "state": 4,
                "canvas_num": 730,
                "jp2": "b18775275_MS_990_0730.JP2",
                "ulx": 850, "uly": 1350, "lrx": 2250, "lry": 3790,
                "label": "State 4 (Third Flap L Lifted — Deepest Interior): Reveals Optic Nerve Core m, Vitreous Humor n, Crystalline Lens o, and Aqueous Humor P.",
            },
        ],
        "summary": "Page 48 (recto, numbered '48' in upper-right margin; opening anatomical plate of the Ophthalmology treatise). Features watercolour diagrams of the extraocular muscles, isolated ocular humors, and a multi-layered physical paper flap dissection ('fugitive sheet' / anatomical volvelle) of the human eye in Column A (whose lifted states are photographed on Canvases 727–730), paired with an anatomical treatise in Column B explaining labels A–R and the origin of the seven tunics from the cerebral meninges.",
        "figures": [
            {
                "fig_id": "fig_p48_muscles_lat",
                "label": "Diagram A: Eye in its form with extraocular muscles elevated",
                "ulx": 250, "uly": 280, "lrx": 1520, "lry": 1560,
                "desc": "Watercolour drawing of the eyeball ('A') with the rectus muscles splayed upward toward the optic apex.",
            },
            {
                "fig_id": "fig_p48_muscles_post",
                "label": "Diagram A–I, a: Posterior/frontal stellate view of the six extraocular muscles, trochlea G, sclera H, optic nerve I, and motor nerve twigs a",
                "ulx": 1220, "uly": 250, "lrx": 2540, "lry": 2080,
                "desc": "Watercolour anatomical rosette showing muscles A–F radiating from globe H/I, pulley G on the superior oblique F, and nerve branches a.",
            },
            {
                "fig_id": "fig_p48_lens_aranea",
                "label": "Diagram B: Crystalline humor with the tunica aranea",
                "ulx": 450, "uly": 1820, "lrx": 910, "lry": 2230,
                "desc": "Concentric circular watercolour diagram of the lens encircled by the arachnoid/ciliary membrane.",
            },
            {
                "fig_id": "fig_p48_lens_bare",
                "label": "Diagram D: Crystalline humor bare and alone",
                "ulx": 520, "uly": 2470, "lrx": 790, "lry": 2740,
                "desc": "Small circular watercolour diagram of the isolated crystalline lens ('D').",
            },
            {
                "fig_id": "fig_p48_vitreus",
                "label": "Diagram C: Posterior white vitreous humor with the crystalline lens",
                "ulx": 1950, "uly": 2120, "lrx": 2370, "lry": 2440,
                "desc": "Crescentic watercolour diagram of the vitreous body ('C') cradling the spherical crystalline lens.",
            },
            {
                "fig_id": "fig_p48_flap_eye",
                "label": "Laminated Multi-Layer Flap Dissection of the Eye (Labels A–R across 4 physical states, Canvases 25 & 727–730)",
                "ulx": 910, "uly": 1520, "lrx": 2360, "lry": 3790,
                "desc": "Interactive 3-flap watercolour anatomical cut-out pasted onto p. 48, lifting sequentially to reveal Tunica Conjunctiva/Cornea (F, G, H), Tunica Uvea/Choroid (I, K, R), Tunica Retina (L), and the internal humors (m, n, o, P).",
            },
        ],
        "columns": [
            {
                "col_id": "colA_diag",
                "col_label": "Column A Upper (Anatomical Diagram Captions & Laminated Flap Labels, X=220..2551, Y=334..3848)",
                "ulx": 220, "uly": 1500, "lrx": 2551, "lry": 3848,
                "lines": make_lines("p48", 25, "colA_diag", 220, 1500, 2551, 3200, [
                    (1, "caption", "A das aug in seiner form", "A. The eye in its natural form.", "Caption beneath top-left muscle diagram."),
                    (2, "caption", "B die Cristalinische", "B. The crystalline", "Caption beneath middle-left inset B (line 1 of 3)."),
                    (3, "caption", "feichtigkeit sambt den", "humor together with the", "Caption beneath inset B (line 2 of 3)."),
                    (4, "caption", "häutlein aranea.", "arachnoid membrane [tunica aranea / anterior capsule].", "Caption beneath inset B (line 3 of 3)."),
                    (5, "caption", "Die hinder weisse feicht=", "C. The posterior white humor,", "Caption beneath middle-right inset C (line 1 of 3)."),
                    (6, "caption", "heit Vitreus mit", "the vitreous, with", "Caption beneath inset C (line 2 of 3)."),
                    (7, "caption", "dem Cristalinum", "the crystalline [lens].", "Caption beneath inset C (line 3 of 3)."),
                    (8, "caption", "die Cristalinische", "D. The crystalline", "Caption beneath lower-left inset D (line 1 of 3)."),
                    (9, "caption", "feichte ganz bloß", "humor completely bare", "Caption beneath inset D (line 2 of 3)."),
                    (10, "caption", "vnd allein.", "and alone.", "Caption beneath inset D (line 3 of 3)."),
                    (11, "caption", "[Flap Labels: State 1 (c.25/727): A, B, D, E, F, G, H | State 2 (c.728): I, K, K, H | State 3 (c.729): L | State 4 (c.730): m, n, o, P]", "[Flap Labels: State 1 (c.25/727): A, B, D, E, F, G, H | State 2 (c.728): I, K, K, H | State 3 (c.729): L | State 4 (c.730): m, n, o, P]", "Composite transcription of letter-keys painted on the 4 physical layers of the laminated flap."),
                ]),
            },
            {
                "col_id": "colA_key",
                "col_label": "Column A Lower (Key to the Extraocular Muscles A–I, a and the 7 Tunics, below red rule X=220..2551, Y=3848..6464)",
                "ulx": 220, "uly": 3848, "lrx": 2551, "lry": 6464,
                "lines": make_lines("p48", 25, "colA_key", 220, 3848, 2551, 6464, [
                    (1, "line", "A das erste aufhebente hochfertige meislein", "A. The first lifting, 'haughty' muscle [superior rectus, musculus attollens/superbus].", "Traditional physiognomic names of the recti muscles."),
                    (2, "line", "B. das erste Nider drukhente meislein diemietige", "B. The first depressing, 'humble' muscle [inferior rectus, musculus deprimens/humilis].", None),
                    (3, "line", "C das erste an ziehente meislein.", "C. The first drawing-in [adducting] muscle [medial rectus, musculus adducens].", None),
                    (4, "line", "D das erste abziehente meislein.", "D. The first drawing-away [abducting] muscle [lateral rectus, musculus abducens].", None),
                    (5, "line", "E das vnder schlimme meislein des herumb.", "E. The lower oblique muscle that winds around [inferior oblique, musculus obliquus inferior].", "schlimme = schräge (oblique)."),
                    (6, "line", "F das obere schlimme meislein", "F. The upper oblique muscle [superior oblique, musculus obliquus superior].", None),
                    (7, "line", "G die augen Roll dises meislein.", "G. The eye-pulley [trochlea] of this muscle.", None),
                    (8, "line", "H das harte augen häutlein welliches zum hindersten", "H. The hard tunic of the eye [sclera] which at the rear", None),
                    (9, "line", "das aug bedökht.", "covers the eye.", None),
                    (10, "line", "I. der Nervus opticus.", "I. The optic nerve [nervus opticus].", None),
                    (11, "line", "a a a a a a. der augen span adern, welliche den", "a a a a a a. The motor nerves of the eyes, which", "Cranial nerves III, IV, VI supplying the extraocular muscles."),
                    (12, "line", "augen ihr bewegung, khrafft vnd empfindtligkhait auß den", "convey to the eyes their movement, power, and sensitivity out of the", None),
                    (13, "line", "gehirn zue fiehret", "brain.", None),
                    (14, "rubric", "{rubric: Es werden heidlein der augen 7.}", "{rubric: Seven tunics [membranes] of the eyes are}", "Red rubric."),
                    (15, "rubric", "{rubric: gezölt, wie Volgt.}", "{rubric: enumerated, as follows:}", "Red rubric."),
                    (16, "line", "1 Coniunctiva. 2 Cornea. 3 Sclerotica.", "1. Conjunctiva. 2. Cornea. 3. Sclerotica.", None),
                    (17, "line", "4 Uvea. 5 Secundina. 6 Aranea.", "4. Uvea [iris/choroid]. 5. Secundina [choroid]. 6. Aranea [lens capsule/zonule].", None),
                    (18, "line", "7. retina.", "7. Retina.", "Pencil '10' in modern hand below l. 18."),
                ]),
            },
            {
                "col_id": "colB",
                "col_label": "Column B (Anatomical Treatise & Key to the Laminated Flap A–R, within red rules X=2551..4881, Y=334..6464)",
                "ulx": 2551, "uly": 334, "lrx": 4881, "lry": 6464,
                "lines": make_lines("p48", 25, "colB", 2551, 334, 4881, 6464, [
                    (1, "rubric", "{rubric: Anatomia oder Zerleg} [48]", "{rubric: Anatomy or Dissection} [48]", "Red rubric; page number '48' in upper-right corner box."),
                    (2, "rubric", "{rubric: ung des Augs, wie es durch}", "{rubric: of the Eye, how by}", "Red rubric."),
                    (3, "rubric", "{rubric: gottes ordtnung zusamen gefiegt}", "{rubric: God's ordinance it is joined together}", "Red rubric."),
                    (4, "rubric", "{rubric: vnd zu Vnder schaiden seÿ.}", "{rubric: and is to be distinguished.}", "Red rubric."),
                    (5, "line", "A. Zaigt an das Tenis membrana das markhichte so von den", "A. Indicates the tenuis membrana [pia mater], the marrow-like substance that", "Refers to label A on the optic stalk of the central flap figure."),
                    (6, "line", "gehirn erwachsen, Substanzia medularis ò Cerebri Substanzia", "grows forth from the brain, substantia medullaris or cerebri substantia", None),
                    (7, "line", "pronata.", "prognata [sprung from the brain substance].", None),
                    (8, "line", "B. Nervus opticus span adern. C C C das fette so", "B. Nervus opticus, the visual nerve. C C C. The fat [orbital adipose tissue] that", None),
                    (9, "line", "zwischen den meislein gefunden wirdt.", "is found between the muscles.", None),
                    (10, "line", "D D D. die 3 meislein, so einer seiten des augs zu sehen seindt,", "D D D. The 3 muscles that are to be seen on one side of the eye.", None),
                    (11, "line", "E. das Rollerl.", "E. The little pulley [trochlea].", None),
                    (12, "line", "F das handte häutlein, Coniunctiva", "F. The outer/investing membrane, Conjunctiva.", "Visible on State 1 of the central flap (Canvas 25 / 727)."),
                    (13, "line", "G. Tunica Cornea oder horn häutlein genandt.", "G. Tunica Cornea, or called the horny membrane.", None),
                    (14, "line", "H. das loch dardurch der aug apffel her sichet.", "H. The aperture through which the eyeball looks out.", None),
                    (15, "line", "I. das Trauben häutlein Uvea Tunica, auch secundina genandt.", "I. The grape-like membrane, Tunica Uvea, also called secundina.", "Revealed when lifting Flap 1 -> State 2 (Canvas 728)."),
                    (16, "line", "K K. der gesichts span adern nervus opticus,", "K K. The visual nerve, nervus opticus.", "Revealed on the stalk in State 2 (Canvas 728)."),
                    (17, "line", "L das Nötz förmige häutlein, retiformis Tunica ò retina", "L. The net-shaped membrane, Tunica retiformis or retina.", "Revealed when lifting Flap 2 -> State 3 (Canvas 729)."),
                    (18, "line", "m m. des gesichts span adern nervus opticus.", "m m. The visual nerve, nervus opticus.", "Revealed when lifting Flap 3 -> State 4 (Canvas 730)."),
                    (19, "line", "n. die gläserne feichtigkeit.", "n. The glassy [vitreous] humor.", "Revealed in State 4 (Canvas 730)."),
                    (20, "line", "o. der Cristalinische humor.", "o. The crystalline humor [lens].", "Revealed in State 4 (Canvas 730)."),
                    (21, "line", "P der wäßrige oder fordere humor, albugineus", "P. The watery or anterior humor, called albugineus", "Revealed in State 4 (Canvas 730)."),
                    (22, "line", "genandt.", "[aqueous humor].", None),
                    (23, "line", "R. das loch in dem Trauben häutlein Uvea Tunica, pup=", "R. The aperture in the grape-like membrane [Tunica Uvea], called pupilla,", None),
                    (24, "line", "ila, oder das schwarze, oder stern genandt.", "or the black [of the eye], or the star.", None),
                    (25, "line", "Die augen werden Von vornembsten 4 stukhen zusamen", "The eyes are joined together out of 4 principal parts,", None),
                    (26, "line", "gefiegt, als Von hirn Vnd von denen 3 Vornembsten", "namely from the brain and from the 3 principal", None),
                    (27, "line", "häutlein des haubts, als von den pericranium vnd", "membranes of the head: namely from the pericranium, and", None),
                    (28, "line", "dura mater, vnd pia mater.", "dura mater, and pia mater.", None),
                    (29, "rubric", "{rubric: dise bishero felein oder heidlein}", "{rubric: These aforesaid membranes or tunics}", "Red rubric."),
                    (30, "rubric", "{rubric: haben Ihren Vrsprung wie Volgt}", "{rubric: have their origin as follows:}", "Red rubric."),
                    (31, "line", "Von solchen obangezaigten Nerus opticus, welliches", "From the above-indicated nervus opticus, which", None),
                    (32, "line", "der rechte grund vnd wurzel der augen vnd des gesichts", "is the true foundation and root of the eyes and of sight,", None),
                    (33, "line", "ist, Endtspringt das Erste in wendige häutlein so ret=", "springs the first inner membrane, which is called", None),
                    (34, "line", "ina, oder retiformis genandt wirdt. dises häutlein", "retina or retiformis. This membrane", None),
                    (35, "line", "halt in sich den humor Vitreum.", "holds within itself the humor vitreus.", None),
                    (36, "line", "Von disen häutlein retina, Endtspringt widerumb", "From this membrane retina springs in turn", None),
                    (37, "line", "ein anders vnd gar dünes häutlein, das faßt in sich den", "another and exceedingly thin membrane, which encloses within itself the", None),
                    (38, "line", "humor Cristalinum, vnd bedökht den fordern Thaill", "humor crystallinus, and covers the anterior part", None),
                    (39, "line", "des Vitrei, vnd wirdt genandt aranea Ciliaris.", "of the vitreus, and is called aranea ciliaris.", None),
                    (40, "line", "Widerumb Endtspringt ein häutlein von dem zarten", "Again there springs a membrane from the delicate", None),
                    (41, "line", "hirn fell pia mater, dise wirdt genand Tenuis membrana", "brain-meninx pia mater; this is called tenuis membrana,", None),
                    (42, "line", "sonst ins gemein secundina genandt.", "otherwise commonly called secundina [choroid].", None),
                    (43, "line", "Von diser Secundina Endtspringt widerumb ein anders", "From this secundina springs in turn another", None),
                    (44, "line", "häutlein Uvea genandt, oder acinosa. das ist das graue", "membrane called Uvea, or acinosa [berry-like]: that is the grey", None),
                    (45, "line", "oder Praune in den aug, wirdt auch genandt das", "or brown part in the eye [iris], and is also called the", None),
                    (46, "line", "wein Pörlein, dises häutlein hat das loch des augs", "little grape-berry [Weinbeerlein]; this membrane has the aperture of the eye", None),
                    (47, "line", "dar durch das liecht glanz vnd schein geht.", "through which the light, gleam, and radiance pass.", None),
                    (48, "line", "dise baide häutlein vmbgeben den humor albugin=", "Both these membranes surround the humor albugineus", None),
                    (49, "line", "eum biß an das loch, als dan helt es die Cornea", "up to the aperture, and from there the Cornea retains it.", None),
                    (50, "line", "das loch der Uvea des augs, wirdt genandt Pupila", "The aperture of the Uvea of the eye is called Pupilla,", None),
                    (51, "line", "das schwarze khindl, oder stern.", "the 'little black child' [Kindlein], or the star [of the eye].", "khindl = calque of Latin pupilla ('little doll/girl reflected in the pupil')."),
                    (52, "line", "Widerumb Endtspringt ein anders häutlein Vor der", "Again there springs another membrane from the", None),
                    (53, "line", "dura mater, so das ganze aug vmb gibt, vnd wird", "dura mater, which surrounds the entire eye, and is", "Continues mid-sentence onto p. 49 (Canvas 26), l. 1 ('genand Cornea.')."),
                ]),
            },
        ],
    },

    # --------------------------------------------------------------------------
    # 6. CANVAS 26: Page 49 — Opening of Ophthalmology Text (b18775275_MS_990_0026.JP2)
    # --------------------------------------------------------------------------
    {
        "page_id": "c0026_p49",
        "canvas_num": 26,
        "jp2": "b18775275_MS_990_0026.JP2",
        "orig_page": "49",
        "folio_side": "verso",
        "width": 5532,
        "height": 6853,
        "frame_box": (688, 274, 5331, 6545),
        "summary": "Page 49 (verso, numbered '49' in upper-left margin; full-width single-column layout across the red-ruled frame, cited in Wellcome catalogue 'Pp. 49-165 are devoted to ophthalmology'). Completes the sentence from p. 48 col. B l. 53 ('genand Cornea'), then treats: (1) The Three Humors of the Eye (Vitreus, Crystallinus, Albugineus/Aquosus, noting that cataract arises in the anterior aqueous humor); (2) The Six Extraocular Muscles (noting the Vesalian observation that the 7th retractor bulbi muscle exists only in beasts/cattle and not in humans); and (3) A scholastic Latin-German synthesis of the parts, nerves, vessels, glands, and tunics constituting the eye.",
        "figures": [],
        "columns": [
            {
                "col_id": "fullWidth",
                "col_label": "Full-Width Text Block (within red rules X=688..5331, Y=274..6545)",
                "ulx": 688, "uly": 274, "lrx": 5331, "lry": 6545,
                "lines": make_lines("p49", 26, "full", 688, 274, 5331, 6545, [
                    (1, "line", "[49 |] genand Cornea. Zu lözt ist noch ein häutlein, das hat sein Ersten Vrsprung von der", "[49 |] called Cornea. Finally there is yet another membrane, which takes its first origin from the", "Completes sentence from p. 48, col. B, l. 53."),
                    (2, "line", "harten häutlein pericranio, darvon Endtspringt das Eüsseriste fällein, die Coniunctiva genandt,", "hard membrane pericranium; therefrom springs the outermost pellicle, called the Conjunctiva,", None),
                    (3, "line", "das ist das weise in dem aug, vnd hat sein Verbindtnuß mit den 6. musculn so die augen", "which is the white in the eye, and has its connection with the 6 muscles that move the", None),
                    (4, "line", "bewegen. —", "eyes. —", None),
                    (5, "rubric", "{rubric: Von den dreÿ feichtigkeiten der Augen}", "{rubric: Of the Three Humors of the Eyes}", "Centered red rubric."),
                    (6, "line", "In den augen werden 3 feichtigkeiten beschlosen, Von wellichen die augen erfült, werden aber vnder=", "Within the eyes are enclosed 3 humors by which the eyes are filled, which are variously", None),
                    (7, "line", "schidlich genand wie Volgt. 1 Vitrus. 2 Cristalinus. 3 albugineus. die hindere feichtig=", "named as follows: 1. Vitreus. 2. Crystallinus. 3. Albugineus. The posterior humor,", None),
                    (8, "line", "khait, als Vitreus wird von hinden mit den häutlein retina Vmbfangen. — Die ander feichtig=", "namely the Vitreus, is embraced from behind by the membrane retina. — The second humor,", None),
                    (9, "line", "khait, Cristalinus ist miten in dem aug, ist in der gröse einer erbes, doch nit ganz rundt,", "the Crystallinus [lens], lies in the middle of the eye; it is of the size of a pea, yet not completely round,", "erbes = Erbse (pea)."),
                    (10, "line", "sonder Etwas braidtlecht, sonderlich an den hindern Thail gegen dem Vitreo dise ist nit recht hart", "but somewhat flattened [lenticular], especially on the posterior part toward the Vitreus; this is neither truly hard", None),
                    (11, "line", "auch nit recht waich, an der farb gleich ein weissen saphier, oder gefrornen Eiß, doch Etwas", "nor truly soft, in colour like a white sapphire or frozen ice, yet somewhat", None),
                    (12, "line", "gilblecht. dise feichtigkhait sambt den Vordern Thaill des Vitrei wirdt mit den häutlein", "yellowish. This humor, together with the anterior part of the Vitreus, is covered over by the membrane", None),
                    (13, "line", "aranea über zogen, vnd schaidet den humor albugineum Von den andern baiden.", "aranea, which separates the humor albugineus from the other two.", None),
                    (14, "line", "Die drite feichtigkhait, ligt in den Vordern thaill des augs, wird genand albugineus aquosus. dise", "The third humor lies in the anterior part of the eye [and] is called albugineus aquosus [aqueous humor]. This", None),
                    (15, "line", "feichtigkhait wirdt mit den häutlein Uvea vmb geben, biß an das loch, darnach hält es die Cornea", "humor is surrounded by the membrane Uvea up to the aperture [pupil], and thereafter the Cornea retains it;", None),
                    (16, "line", "in diser Vordern feichtigkhait, erheben sich die Cataracta der starn", "in this anterior humor arise the Cataracta, the couching-cataract [Star].", "Classical Galenic/medieval locus of cataract as a suffusion in the aqueous chamber."),
                    (17, "rubric", "{rubric: Von den meislein der Augen}", "{rubric: Of the Muscles of the Eyes}", "Centered red rubric."),
                    (18, "line", "Das aug hat 6 meislein oder musculis, die 1. so das aug übersich zicht. das 2 das das aug vndersich zicht", "The eye has 6 muscles [musculi]: the 1st which draws the eye upward; the 2nd which draws the eye downward;", None),
                    (19, "line", "das 3 so das aug übersich nach der seiten zicht. das 4 so das aug vndersich nach der seiten zicht. Darnach", "the 3rd which draws the eye upward toward the side; the 4th which draws the eye downward toward the side. Thereafter", None),
                    (20, "line", "seind noch 2 andere musculi, eine die das aug nach den grosen winkhel ziecht, vnd eins so nach den", "there are 2 further muscles: one that draws the eye toward the great [medial] canthus, and one that draws it toward the", None),
                    (21, "line", "khlainen winkhel zicht, Es seind auch andere Auctores, welliche auf den 7ten musculn bestehen wellicher", "lesser [lateral] canthus. There are also other authors who insist upon a 7th muscle which", None),
                    (22, "line", "den Nervum opticum Vmb geben, welliches aber allein in den Vich augen gefunden wirdt, aber in des", "surrounds the nervus opticus [retractor bulbi], which however is found only in the eyes of beasts/cattle, whereas in", "Vesalius (Fabrica, 1543) refuted Galen's 7th human eye muscle as an ungulate/bovine structure."),
                    (23, "line", "menschen augen befinden sich nur 6 meislein. —", "human eyes only 6 muscles are found. —", None),
                    (24, "rubric", "{rubric: Volgt Weider, von den augen Ihren Thaillen, Wie sÿe von Gott}", "{rubric: Follows Further concerning the Eyes and Their Parts, How They Are by God}", "Red rubric."),
                    (25, "rubric", "{rubric: erschaffen vnd Zusamen gesezt}", "{rubric: Created and Joined Together}", "Red rubric with ornamental flourish."),
                    (26, "line", "Eß befindet sich vnder denen oculisten ein streidt, wegen der Thaill oder häutlein der augen", "There exists among the oculists a controversy regarding the parts or tunics of the eyes:", None),
                    (27, "line", "Vnd wollen Etliche behaubten es wehren nur 2 häutl, andere bestehen 3. andere wollen", "and some wish to maintain there are only 2 tunics, others insist on 3, others will have", None),
                    (28, "line", "4. andere 5. oder 6. die mehristen aber khumen über ains vnd sagen Von siben", "4, others 5 or 6; the majority, however, agree and speak of seven", None),
                    (29, "line", "häutlein,", "tunics.", None),
                    (30, "line", "Dise häutlein werden auf Volgente weiß genand, Erstlich die Coniunctiva Cornea", "These tunics are named in the following manner: first the Conjunctiva, Cornea,", None),
                    (31, "line", "Uvea, aranea, retiformis, et vitrea, dura sive, sclirotica ist ein pars Cornea", "Uvea, Aranea, Retiformis, and Vitrea; the dura or sclerotica is a part of the Cornea,", None),
                    (32, "line", "{del: [red cancellation bar: et Uvea]}, interstitium Ciliare ist ein pars Uvea, pupilla ist das", "{del: [cancelled in red: et Uvea]}, the interstitium ciliare is a part of the Uvea, the pupilla is the", "Two words at left of l. 32 obliterated by a thick red bar."),
                    (33, "line", "löchlein fornen Uvea. Iris ist auch ein Thaill Uvea", "little aperture in the front of the Uvea; the Iris is also a part of the Uvea.", None),
                    (34, "line", "über dises sind auch in den aug dreÿ humores, Nemblich aquosus, Christalinus, vnd", "Beyond this there are also in the eye three humores, namely aquosus, crystallinus, and", None),
                    (35, "line", "Vitreus. Zur Constitution des augs khumen Zusamen, nerus opticus, spiri=", "vitreus. To the constitution of the eye come together: the nervus opticus, spiritus", None),
                    (36, "line", "tus Visiuus atq: facultas, Visiua, alda auch Etwas faistes ist, adeps, seind", "visivus atque facultas visiva [visual spirit and visual faculty], where there is also some fat, adeps; there are", None),
                    (37, "line", "auch Etlich neruli ex secunda Coniugatione anguli duo, auch Caruncula,", "also several small nerves from the second pair [ex secunda coniugatione], the two canthi [anguli duo], also the caruncula", "Galenic 2nd pair of cranial nerves = oculomotor nerve."),
                    (38, "line", "Lacrimalis, wie auch Zwaÿ glandulæ, über dises gehören zue den augen, Super", "lacrimalis, as well as two glandulae [lacrimal glands]; beyond this belong to the eyes the super-", None),
                    (39, "line", "Cilia, et ipsa orbita, Vnd dises alles ohne die arterias vnd Venas.", "cilia [eyebrows] and the orbita itself, and all this besides the arteriae and venae.", None),
                    (40, "line", "Tunica oculorum sind membrana so das aug Constituiern, deren wir 6 Erzölt", "The tunicae oculorum are membranes that constitute the eye, of which we have enumerated 6:", None),
                    (41, "line", "haben, Coniungtiva wird auch adnata genand, albuginea adherens alba. Crasa", "the Conjunctiva is also called adnata, albuginea adhaerens alba, crassa,", None),
                    (42, "line", "Consolidativa album oculi et fuda, ist des augs weise eüsseriste haut, ent=", "consolidativa, album oculi, and fuda; it is the white outermost membrane of the eye, originates", None),
                    (43, "line", "springt auß den pericranio überzicht vnd bedökht das ganze aug, biß an den regen=", "out of the pericranium, coats and covers the entire eye up to the rainbow", "regenbogen = iris."),
                    (44, "line", "bogen, iridis Cornea, ist ein Tunica welliche die runde des augs, Vmb gibt,", "[iris]; the Cornea is a tunic which surrounds the globe of the eye...", "Continues onto p. 50 (Canvas 27)."),
                ]),
            }
        ],
    },

    # --------------------------------------------------------------------------
    # CANVASES 27–30: Pages 50–53 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH3,

    # --------------------------------------------------------------------------
    # CANVASES 31–35: Pages 54–55, 60–62 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH4,

    # --------------------------------------------------------------------------
    # CANVASES 36–45: Pages 63–72 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH5,

    # --------------------------------------------------------------------------
    # CANVASES 46–55: Pages 73–75, 78–84 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH6,

    # --------------------------------------------------------------------------
    # CANVASES 56–75: Pages 85–104 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH7,

    # --------------------------------------------------------------------------
    # CANVASES 76–93: Pages 105–122 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH8,

    # --------------------------------------------------------------------------
    # CANVASES 94–105: Pages 123–134 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH9,

    # --------------------------------------------------------------------------
    # CANVASES 106–120: Pages 135–149 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH10,

    # --------------------------------------------------------------------------
    # CANVASES 121–135: Pages 150–164 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH11,

    # --------------------------------------------------------------------------
    # CANVASES 136–150: Pages 165–179 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH12,

    # --------------------------------------------------------------------------
    # CANVASES 151–165: Batch 13 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH13,

    # --------------------------------------------------------------------------
    # CANVASES 166–180: Batch 14 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH14,

    # --------------------------------------------------------------------------
    # CANVASES 181–195: Batch 15 (Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH15,

    # --------------------------------------------------------------------------
    # CANVASES 196–240: Batch 16 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH16,

    # --------------------------------------------------------------------------
    # CANVASES 241–285: Batch 17 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH17,

    # --------------------------------------------------------------------------
    # CANVASES 286–330: Batch 18 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH18,

    # --------------------------------------------------------------------------
    # CANVASES 331–375: Batch 19 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH19,

    # --------------------------------------------------------------------------
    # CANVASES 376–420: Batch 20 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH20,

    # --------------------------------------------------------------------------
    # CANVASES 421–465: Batch 21 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH21,

    # --------------------------------------------------------------------------
    # CANVASES 466–510: Batch 22 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH22,

    # --------------------------------------------------------------------------
    # CANVASES 511–555: Batch 23 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH23,

    # --------------------------------------------------------------------------
    # CANVASES 556–600: Batch 24 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH24,

    # --------------------------------------------------------------------------
    # CANVASES 601–645: Batch 25 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH25,

    # --------------------------------------------------------------------------
    # CANVASES 646–690: Batch 26 (45 pages; Transcribed & Translated with Gemini 4)
    # --------------------------------------------------------------------------
    *PAGES_BATCH26,

    # --------------------------------------------------------------------------
    # CANVASES 691–735: Batch 27 (45 pages; Transcribed & Translated with Gemini 4 Hydrogen)
    # --------------------------------------------------------------------------
    *PAGES_BATCH27,

    # --------------------------------------------------------------------------
    # CANVASES 736–747 (excl. 738–739): Batch 28 (10 pages; Transcribed & Translated with Gemini 4 Hydrogen)
    # --------------------------------------------------------------------------
    *PAGES_BATCH28,
]


# ==============================================================================
# 1. GENERATE EXACT DIPLOMATIC TRANSCRIPTION (.txt and .md)
# ==============================================================================
def write_transcription():
    lines_out = []
    lines_out.append("================================================================================")
    lines_out.append("WELLCOME COLLECTION MS.990 (Work ID: ceuwj8kj | Sierra ID: b18775275)")
    lines_out.append("Title:      Arzneibuch (Compendium of Popular Medicine and Surgery, c. 1675)")
    lines_out.append("Origin:     Franciscan House, Austria or South Germany (Austro-Bavarian ENHG)")
    lines_out.append("IIIF v2:    " + IIIF_MANIFEST_V2)
    lines_out.append("IIIF v3:    " + IIIF_MANIFEST_V3)
    lines_out.append("Catalogue:  " + WORK_URL)
    lines_out.append("Output 1/3: EXACT DIPLOMATIC TRANSCRIPTION (IIIF-Anchored with Line Coordinates)")
    lines_out.append("================================================================================")
    lines_out.append("")
    lines_out.append("EDITORIAL & PALEOGRAPHIC CONVENTIONS:")
    lines_out.append("  * Original Early New High German (Frühneuhochdeutsch) orthography, vocalic")
    lines_out.append("    diacritics (ÿ, ü, ö, ä), consonant clusters (kh-, p-, cz, ß), capitalization,")
    lines_out.append("    and punctuation are strictly preserved.")
    lines_out.append("  * Line breaks and line numbers match the physical manuscript lineation.")
    lines_out.append("  * End-of-line hyphenation is represented by '=' (matching the scribal double")
    lines_out.append("    or single oblique hyphen).")
    lines_out.append("  * Red-ink headings and inline rubrics are marked as {rubric: ...}.")
    lines_out.append("  * Scribal deletions are marked {del: ...} and supralinear additions {add: ...}.")
    lines_out.append("  * Alchemical, planetary, and apothecary symbols are rendered with their")
    lines_out.append("    Unicode glyph followed by diplomatic expansion in brackets, e.g. ▽ [Wasser].")
    lines_out.append("  * Every page, column, figure, flap state, and line is anchored to its exact")
    lines_out.append("    Wellcome IIIF Canvas pixel bounding box (#xywh=x,y,w,h).")
    lines_out.append("")
    lines_out.append("ALCHEMICAL, PLANETARY & APOTHECARY GLYPH KEY:")
    for gid, glyph, ucode, lat, meaning in GLYPH_TABLE:
        lines_out.append(f"  {glyph:<4} ({ucode:<15}) = {lat:<26} -> {meaning}")
    lines_out.append("")

    for p in PAGES:
        c_num = p["canvas_num"]
        jp2 = p["jp2"]
        c_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        img_svc = f"https://iiif.wellcomecollection.org/image/{jp2}"
        fx, fy, flrx, flry = p["frame_box"]
        f_xywh = f"{fx},{fy},{flrx - fx},{flry - fy}"

        lines_out.append("--------------------------------------------------------------------------------")
        lines_out.append(f"PAGE / FOLIO: {p['orig_page']} ({p['folio_side']}) | IIIF Canvas #{c_num} ({jp2})")
        lines_out.append(f"Canvas URI:   {c_uri}")
        lines_out.append(f"Image API:    {img_svc}/full/full/0/default.jpg (Dimensions: {p['width']} x {p['height']} px)")
        lines_out.append(f"Red-Rule Box: {c_uri}#xywh={f_xywh}" + (f" | Center Rule X={p['center_rule_x']}" if "center_rule_x" in p else ""))
        lines_out.append(f"Summary:      {p['summary']}")
        if p.get("transcribed_with") or p.get("model"):
            lines_out.append(f"Model:        {p.get('transcribed_with') or p.get('model')}")
        if p.get("input_tokens") is not None and p.get("output_tokens") is not None:
            lines_out.append(f"Tokens Used:  Input: {p['input_tokens']:,} | Output: {p['output_tokens']:,}")
        if p.get("flap_canvases"):
            lines_out.append("Laminated Flap States (Multi-Canvas IIIF Composite):")
            for fc in p["flap_canvases"]:
                f_w = fc["lrx"] - fc["ulx"]
                f_h = fc["lry"] - fc["uly"]
                lines_out.append(
                    f"  * State {fc['state']} (Canvas #{fc['canvas_num']}, {fc['jp2']}): "
                    f"#xywh={fc['ulx']},{fc['uly']},{f_w},{f_h} — {fc['label']}"
                )
        if p.get("figures"):
            lines_out.append("Illustrations / Figures on Canvas:")
            for fig in p["figures"]:
                fw = fig["lrx"] - fig["ulx"]
                fh = fig["lry"] - fig["uly"]
                lines_out.append(
                    f"  * [{fig['fig_id']}] #xywh={fig['ulx']},{fig['uly']},{fw},{fh} : {fig['label']}"
                )
        lines_out.append("--------------------------------------------------------------------------------")

        for col in p["columns"]:
            cw = col["lrx"] - col["ulx"]
            ch = col["lry"] - col["uly"]
            lines_out.append("")
            lines_out.append(f"### [{p['orig_page']} — {col['col_label']}]")
            lines_out.append(f"### Column Zone: {c_uri}#xywh={col['ulx']},{col['uly']},{cw},{ch}")
            lines_out.append("")
            for ln in col["lines"]:
                l_tag = f"[{ln['line_id']}]"
                coord_tag = f"(#xywh={ln['xywh']})"
                lines_out.append(f"{l_tag:<22} {coord_tag:<26} {ln['de']}")
        lines_out.append("")

    txt_content = "\n".join(lines_out)
    (OUT_DIR / "MS990_transcription.txt").write_text(txt_content, encoding="utf-8")
    (OUT_DIR / "MS990_transcription.md").write_text(txt_content, encoding="utf-8")
    print("Wrote MS990_transcription.txt and MS990_transcription.md")


# ==============================================================================
# 2. GENERATE LINE-BY-LINE ENGLISH TRANSLATION (.txt and .md)
# ==============================================================================
def write_translation():
    lines_out = []
    lines_out.append("================================================================================")
    lines_out.append("WELLCOME COLLECTION MS.990 (Work ID: ceuwj8kj | Sierra ID: b18775275)")
    lines_out.append("Title:      Arzneibuch (Compendium of Popular Medicine and Surgery, c. 1675)")
    lines_out.append("Origin:     Franciscan House, Austria or South Germany (Austro-Bavarian ENHG)")
    lines_out.append("IIIF v2:    " + IIIF_MANIFEST_V2)
    lines_out.append("IIIF v3:    " + IIIF_MANIFEST_V3)
    lines_out.append("Catalogue:  " + WORK_URL)
    lines_out.append("Output 3/3: LINE-BY-LINE ENGLISH TRANSLATION (Aligned to Transcription & IIIF)")
    lines_out.append("================================================================================")
    lines_out.append("")
    lines_out.append("TRANSLATION PRINCIPLES:")
    lines_out.append("  * Strictly preserves the exact line numbering ([line_id]) and column/page")
    lines_out.append("    boundaries of the diplomatic transcription and TEI XML edition.")
    lines_out.append("  * Expands all iatrochemical, planetary, and apothecary symbols inline while")
    lines_out.append("    retaining the symbol in brackets for cross-reference.")
    lines_out.append("  * Preserves technical Latin anatomical nomenclature alongside English glosses.")
    lines_out.append("  * Includes paleographic, medical, and historical notes after lines where needed.")
    lines_out.append("")

    for p in PAGES:
        c_num = p["canvas_num"]
        jp2 = p["jp2"]
        c_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        fx, fy, flrx, flry = p["frame_box"]
        f_xywh = f"{fx},{fy},{flrx - fx},{flry - fy}"

        lines_out.append("--------------------------------------------------------------------------------")
        lines_out.append(f"PAGE / FOLIO: {p['orig_page']} ({p['folio_side']}) | IIIF Canvas #{c_num} ({jp2})")
        lines_out.append(f"Canvas URI:   {c_uri}#xywh={f_xywh}")
        lines_out.append(f"Summary:      {p['summary']}")
        if p.get("transcribed_with") or p.get("model"):
            lines_out.append(f"Model:        {p.get('transcribed_with') or p.get('model')}")
        if p.get("input_tokens") is not None and p.get("output_tokens") is not None:
            lines_out.append(f"Tokens Used:  Input: {p['input_tokens']:,} | Output: {p['output_tokens']:,}")
        lines_out.append("--------------------------------------------------------------------------------")

        for col in p["columns"]:
            cw = col["lrx"] - col["ulx"]
            ch = col["lry"] - col["uly"]
            lines_out.append("")
            lines_out.append(f"### [{p['orig_page']} — {col['col_label']}]")
            lines_out.append(f"### Column Zone: {c_uri}#xywh={col['ulx']},{col['uly']},{cw},{ch}")
            lines_out.append("")
            for ln in col["lines"]:
                l_tag = f"[{ln['line_id']}]"
                coord_tag = f"(#xywh={ln['xywh']})"
                note_str = f"  // Note: {ln['note']}" if ln["note"] else ""
                lines_out.append(f"{l_tag:<22} {coord_tag:<26} {ln['en']}{note_str}")
        lines_out.append("")

    txt_content = "\n".join(lines_out)
    (OUT_DIR / "MS990_translation.txt").write_text(txt_content, encoding="utf-8")
    (OUT_DIR / "MS990_translation.md").write_text(txt_content, encoding="utf-8")
    print("Wrote MS990_translation.txt and MS990_translation.md")


# ==============================================================================
# 3. GENERATE TEI P5 XML EDITION (MS990_tei.xml)
# ==============================================================================
def format_diplomatic_xml_text(de_str: str) -> str:
    """Converts inline markers {rubric: ...}, {del: ...}, {add: ...}, and glyphs into TEI XML markup."""
    s = html.escape(de_str)
    # Replace glyphs with <g ref="#...">
    glyph_map = [
        ("🜔▽ [Salzwasser]", '<g ref="#g_salzwasser">🜔▽</g><expan>Salzwasser</expan>'),
        ("℞", '<g ref="#g_rx">℞</g>'),
        ("▽ [Wasser]", '<g ref="#g_aqua">▽</g><expan>Wasser</expan>'),
        ("V̈ [Wein]", '<g ref="#g_vinum">V̈</g><expan>Wein</expan>'),
        ("✚ [Essig]", '<g ref="#g_acetum">✚</g><expan>Essig</expan>'),
        ("🜔 [Salz]", '<g ref="#g_sal">🜔</g><expan>Salz</expan>'),
        ("ꝑll̵ [Pulver]", '<g ref="#g_pulvis">ꝑll̵</g><expan>Pulver</expan>'),
        ("✗ [Kalk/Pulver]", '<g ref="#g_calx">✗</g><expan>Kalk/Pulver</expan>'),
        ("✗ [Pulver]", '<g ref="#g_calx">✗</g><expan>Pulver</expan>'),
        ("⊡ [Harn]", '<g ref="#g_urina">⊡</g><expan>Harn</expan>'),
        ("☉ [Sonne]", '<g ref="#g_sol">☉</g><expan>Sonne</expan>'),
        ("🜘 usti [Alaun]", '<g ref="#g_alumen">🜘</g> usti<expan>Alaun</expan>'),
        ("🜘 [Alaun]", '<g ref="#g_alumen">🜘</g><expan>Alaun</expan>'),
        ("🜖 alb. [Vitriolum album]", '<g ref="#g_vitriolum">🜖</g> alb.<expan>Vitriolum album</expan>'),
        ("sp[iritus] 🜖 [Vitrioli]", 'sp<expan>iritus</expan> <g ref="#g_vitriolum">🜖</g><expan>Vitrioli</expan>'),
        ("🜖 [Vitriol]", '<g ref="#g_vitriolum">🜖</g><expan>Vitriol</expan>'),
        ("ol. ♁ris [olei Sulphuris]", 'ol. <g ref="#g_antimonium">♁</g>ris<expan>olei Sulphuris</expan>'),
        ("♁ [Antimonium]", '<g ref="#g_antimonium">♁</g><expan>Antimonium</expan>'),
        ("♁ [Sulphuris]", '<g ref="#g_antimonium">♁</g><expan>Sulphuris</expan>'),
        ("☿ dulc. [Mercurius dulcis]", '<g ref="#g_mercurius">☿</g> dulc.<expan>Mercurius dulcis</expan>'),
        ("☿ sublimat. [Mercurius sublimatus]", '<g ref="#g_mercurius">☿</g> sublimat.<expan>Mercurius sublimatus</expan>'),
        ("☿ [Tartarus]", '<g ref="#g_mercurius">☿</g><expan>Tartarus</expan>'),
        ("🜕 [Salpeter]", '<g ref="#g_nitrum">🜕</g><expan>Salpeter</expan>'),
        ("🜔 ♄ [Sal Saturni]", '<g ref="#g_sal">🜔</g> <g ref="#g_saturnus">♄</g><expan>Sal Saturni</expan>'),
        ("♄ [Saturni]", '<g ref="#g_saturnus">♄</g><expan>Saturni</expan>'),
        ("XXX [Camphora]", '<g ref="#g_camphora">XXX</g><expan>Camphora</expan>'),
        ("sp[iritus] 🜔 [Salis]", 'sp<expan>iritus</expan> <g ref="#g_sal">🜔</g><expan>Salis</expan>'),
        ("♁ [Sulphur]", '<g ref="#g_antimonium">♁</g><expan>Sulphur</expan>'),
        ("♁ [Schwefel]", '<g ref="#g_antimonium">♁</g><expan>Schwefel</expan>'),
        ("🜖 [Vitrioli]", '<g ref="#g_vitriolum">🜖</g><expan>Vitrioli</expan>'),
    ]
    for k, v in glyph_map:
        s = s.replace(html.escape(k), v)

    # Replace {del: ...}, {add: ...} first (in case nested inside {rubric: ...}), then {rubric: ...}
    import re
    s = re.sub(r"\{del:\s*([^}]*)\}", r"<del>\1</del>", s)
    s = re.sub(r"\{add:\s*([^}]*)\}", r'<add place="supralinear">\1</add>', s)
    s = re.sub(r"\{rubric:\s*([^}]*)\}", r'<hi rend="rubric">\1</hi>', s)
    return s


def write_tei_xml():
    xml_lines = []
    xml_lines.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_lines.append('<TEI xmlns="http://www.tei-c.org/ns/1.0" xml:id="Wellcome_MS990_ceuwj8kj">')
    xml_lines.append("  <teiHeader>")
    xml_lines.append("    <fileDesc>")
    xml_lines.append("      <titleStmt>")
    xml_lines.append("        <title type=" + '"main"' + ">Arzneibuch (Wellcome Collection MS.990): Diplomatic Transcription, Facsimile Coordinates, and Aligned English Translation</title>")
    xml_lines.append("        <title type=" + '"sub"' + ">Compendium of Popular Medicine, Surgery, Ophthalmology, and Materia Medica for a Franciscan House in Austria or South Germany (c. 1675)</title>")
    xml_lines.append("        <respStmt>")
    xml_lines.append("          <resp>Paleographic transcription, IIIF coordinate anchoring, TEI P5 encoding, and English translation</resp>")
    xml_lines.append("          <name>Antigravity Scholarly Edition Pipeline</name>")
    xml_lines.append("        </respStmt>")
    xml_lines.append("        <respStmt>")
    xml_lines.append("          <resp>Paleographic transcription, diplomatic collation, and translation of Pages 38–47 (Canvases 15–24)</resp>")
    xml_lines.append("          <name>Gemini 3.8 Flash</name>")
    xml_lines.append("        </respStmt>")
    xml_lines.append("        <respStmt>")
    xml_lines.append("          <resp>Paleographic transcription, diplomatic collation, and translation of Pages 50–55, 60–75, 78–104 (Canvases 27–75)</resp>")
    xml_lines.append("          <name>Gemini 4</name>")
    xml_lines.append("        </respStmt>")
    xml_lines.append("      </titleStmt>")
    xml_lines.append("      <publicationStmt>")
    xml_lines.append("        <publisher>Wellcome Collection Digital Edition (Local Workspace)</publisher>")
    xml_lines.append('        <idno type="wellcome-work">ceuwj8kj</idno>')
    xml_lines.append('        <idno type="sierra-system">b18775275</idno>')
    xml_lines.append('        <idno type="shelfmark">MS.990</idno>')
    xml_lines.append('        <idno type="previous-shelfmark">WMS 990</idno>')
    xml_lines.append('        <idno type="accession-number">41913</idno>')
    xml_lines.append('        <idno type="iiif-manifest-v2">' + IIIF_MANIFEST_V2 + "</idno>")
    xml_lines.append('        <idno type="iiif-manifest-v3">' + IIIF_MANIFEST_V3 + "</idno>")
    xml_lines.append("        <availability status=" + '"free"' + ">")
    xml_lines.append('          <licence target="https://creativecommons.org/publicdomain/mark/1.0/">Public Domain Mark (PDM 1.0)</licence>')
    xml_lines.append("        </availability>")
    xml_lines.append("      </publicationStmt>")
    xml_lines.append("      <sourceDesc>")
    xml_lines.append("        <msDesc>")
    xml_lines.append("          <msIdentifier>")
    xml_lines.append("            <settlement>London</settlement>")
    xml_lines.append("            <repository>Wellcome Collection</repository>")
    xml_lines.append("            <idno>MS.990</idno>")
    xml_lines.append('            <altIdentifier type="former"><idno>WMS 990</idno></altIdentifier>')
    xml_lines.append('            <altIdentifier type="accession"><idno>41913</idno></altIdentifier>')
    xml_lines.append('            <altIdentifier type="work-id"><idno>ceuwj8kj</idno></altIdentifier>')
    xml_lines.append("          </msIdentifier>")
    xml_lines.append("          <msContents>")
    xml_lines.append("            <summary>Compendium of popular medicine and surgery, receipts, etc., in Early New High German (Austro-Bavarian dialect), compiled c. 1675 for a House of the Franciscan Order in Austria or South Germany. Pages 49–165 contain a specialized treatise on ophthalmology preceded on p. 48 (Canvas 25) by a multi-layered laminated anatomical flap dissection of the eye (photographed in lifted states on Canvases 727–730).</summary>")
    xml_lines.append('            <textLang mainLang="de" otherLangs="la">Early New High German (Austro-Bavarian dialect) with Latin anatomical and pharmaceutical terminology.</textLang>')
    xml_lines.append("          </msContents>")
    xml_lines.append("          <physDesc>")
    xml_lines.append("            <objectDesc form=" + '"codex"' + ">")
    xml_lines.append("              <supportDesc material=" + '"paper"' + ">")
    xml_lines.append("                <support>Laid paper with watermarks (documented in transmitted-light shots on Canvases 736–743).</support>")
    xml_lines.append("                <extent>1 volume: pp. [29], 30–790 + 4 index leaves, 4to (20.5 x 15 cm); 745 IIIF canvases.<dimensions unit=" + '"cm"' + "><height>20.5</height><width>15.0</width></dimensions></extent>")
    xml_lines.append("                <collation><p>Pages 1–28 (or 1–29 in catalogue, though unnumbered recto [p. 29] survives on Canvas 7), 56–59, 76, 77, 251, 252, 435–438, 484–487, 490–499, 652–659, 725, 762, 783–786 are wanting, as well as the end of the alphabetical index after the middle of letter P. A large piece is torn away from pp. 417/418 (Canvases 733–735). Pagination is irregular (e.g. p. 30 on verso Canvas 8 faces p. 32 on recto Canvas 9, skipping 31 without text loss).</p></collation>")
    xml_lines.append("              </supportDesc>")
    xml_lines.append("              <layoutDesc>")
    xml_lines.append('                <layout columns="2" ruledLines="40 53"><p>Written in double column within red rules (with occasional full-width single-column pages such as p. 49), headings and section rubrics in red ink.</p></layout>')
    xml_lines.append("              </layoutDesc>")
    xml_lines.append("            </objectDesc>")
    xml_lines.append("            <handDesc hands=" + '"1"' + ">")
    xml_lines.append('              <handNote xml:id="hand_main" script="kurrent" medium="brown-and-red-ink"><p>Main 17th-century Austro-Bavarian scribal hand writing German Kurrentschrift for vernacular text, humanist cursiva antiqua for Latin technical terms, and red ink for rubrics and ruling.</p></handNote>')
    xml_lines.append('              <handNote xml:id="hand_cat" script="modern-cursive" medium="pencil"><p>20th-century bookseller and library cataloguer hands on pastedown and flyleaf 1r.</p></handNote>')
    xml_lines.append("            </handDesc>")
    xml_lines.append("            <decoDesc>")
    xml_lines.append("              <decoNote><p>Contains over 300 watercolour illustrations (including 15 nearly full-page paintings of Franciscan friar-surgeons, operations, laboratories, apothecary shops, instruments, and chemical apparatus), ~60 ophthalmic drawings on pp. 48–165, and a 3-layer movable anatomical eye flap on p. 48 (Canvas 25 + Canvases 727–730).</p></decoNote>")
    xml_lines.append("            </decoDesc>")
    xml_lines.append("            <bindingDesc>")
    xml_lines.append("              <binding><p>Modern stamped brown morocco binding with gilt spine lettering: COMPENDIUM OF MEDICINE AND SURGERY / M. S. GERMAN. / CA 1650–1680 (Canvas 1, Canvas 722, Canvas 723).</p></binding>")
    xml_lines.append("            </bindingDesc>")
    xml_lines.append("          </physDesc>")
    xml_lines.append("          <history>")
    xml_lines.append('            <origin><origDate notBefore="1650" notAfter="1685" cert="medium">c. 1675</origDate><origPlace>Austria or South Germany (Franciscan House)</origPlace></origin>')
    xml_lines.append("            <acquisition>Purchased in 1922 from Gilhofer &amp; Ranschburg, Vienna (600 Swiss francs / £24), Accession No. 41913.</acquisition>")
    xml_lines.append("          </history>")
    xml_lines.append("        </msDesc>")
    xml_lines.append("      </sourceDesc>")
    xml_lines.append("    </fileDesc>")
    xml_lines.append("    <encodingDesc>")
    xml_lines.append("      <editorialDecl>")
    xml_lines.append("        <p>Diplomatic transcription preserving original Early New High German spelling, vocalic diacritics, capitalization, punctuation, and lineation. Line breaks (<lb/>) and zones (<zone/>) are anchored to pixel coordinates (#xywh=x,y,w,h) on the Wellcome IIIF canvases.</p>")
    xml_lines.append("      </editorialDecl>")
    xml_lines.append("      <charDecl>")
    for gid, glyph, ucode, lat, meaning in GLYPH_TABLE:
        xml_lines.append(f'        <char xml:id="g_{gid}">')
        xml_lines.append(f"          <localProp name=" + '"name"' + f' value="{html.escape(lat)}"/>')
        xml_lines.append(f"          <localProp name=" + '"unicode"' + f' value="{html.escape(ucode)}"/>')
        xml_lines.append(f"          <localProp name=" + '"meaning"' + f' value="{html.escape(meaning)}"/>')
        xml_lines.append(f"          <mapping type=" + '"diplomatic"' + f">{html.escape(glyph)}</mapping>")
        xml_lines.append("        </char>")
    xml_lines.append("      </charDecl>")
    xml_lines.append("    </encodingDesc>")
    xml_lines.append("  </teiHeader>")

    # ==========================================================================
    # FACSIMILE SECTION WITH EXACT IIIF CANVAS & ZONE COORDINATES
    # ==========================================================================
    xml_lines.append(f'  <facsimile corresp="{IIIF_MANIFEST_V3}">')
    for p in PAGES:
        c_num = p["canvas_num"]
        jp2 = p["jp2"]
        c_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{jp2}"
        img_svc = f"https://iiif.wellcomecollection.org/image/{jp2}"
        fx, fy, flrx, flry = p["frame_box"]

        xml_lines.append(
            f'    <surface xml:id="surf_{p["page_id"]}" n="{html.escape(p["orig_page"])}" '
            f'ulx="0" uly="0" lrx="{p["width"]}" lry="{p["height"]}" '
            f'corresp="{c_uri}">'
        )
        xml_lines.append(
            f'      <graphic url="{img_svc}/full/full/0/default.jpg" '
            f'width="{p["width"]}px" height="{p["height"]}px" '
            f'mimeType="image/jpeg" corresp="{img_svc}"/>'
        )
        # Page frame zone
        xml_lines.append(
            f'      <zone xml:id="zone_{p["page_id"]}_frame" type="red-ruled-frame" '
            f'ulx="{fx}" uly="{fy}" lrx="{flrx}" lry="{flry}" '
            f'corresp="{c_uri}#xywh={fx},{fy},{flrx - fx},{flry - fy}"/>'
        )
        # Laminated flap states (if present on p. 48)
        for fc in p.get("flap_canvases", []):
            fc_jp2 = fc["jp2"]
            fc_uri = f"https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{fc_jp2}"
            fw = fc["lrx"] - fc["ulx"]
            fh = fc["lry"] - fc["uly"]
            xml_lines.append(
                f'      <zone xml:id="zone_{p["page_id"]}_flap_state{fc["state"]}" type="laminated-flap-state" '
                f'ulx="{fc["ulx"]}" uly="{fc["uly"]}" lrx="{fc["lrx"]}" lry="{fc["lry"]}" '
                f'corresp="{fc_uri}#xywh={fc["ulx"]},{fc["uly"]},{fw},{fh}">'
            )
            xml_lines.append(f'        <desc>{html.escape(fc["label"])}</desc>')
            xml_lines.append("      </zone>")
        # Figure zones
        for fig in p.get("figures", []):
            fw = fig["lrx"] - fig["ulx"]
            fh = fig["lry"] - fig["uly"]
            xml_lines.append(
                f'      <zone xml:id="{fig["fig_id"]}" type="illustration" '
                f'ulx="{fig["ulx"]}" uly="{fig["uly"]}" lrx="{fig["lrx"]}" lry="{fig["lry"]}" '
                f'corresp="{c_uri}#xywh={fig["ulx"]},{fig["uly"]},{fw},{fh}">'
            )
            xml_lines.append(f'        <desc>{html.escape(fig["label"] + " — " + fig["desc"])}</desc>')
            xml_lines.append("      </zone>")
        # Column zones and individual line zones
        for col in p["columns"]:
            cw = col["lrx"] - col["ulx"]
            ch = col["lry"] - col["uly"]
            col_zid = f'zone_{p["page_id"]}_{col["col_id"]}'
            xml_lines.append(
                f'      <zone xml:id="{col_zid}" type="column" '
                f'ulx="{col["ulx"]}" uly="{col["uly"]}" lrx="{col["lrx"]}" lry="{col["lry"]}" '
                f'corresp="{c_uri}#xywh={col["ulx"]},{col["uly"]},{cw},{ch}">'
            )
            for ln in col["lines"]:
                xml_lines.append(
                    f'        <zone xml:id="zone_{ln["line_id"]}" type="{ln["line_type"]}" '
                    f'ulx="{ln["ulx"]}" uly="{ln["uly"]}" lrx="{ln["lrx"]}" lry="{ln["lry"]}" '
                    f'corresp="{ln["iiif_canvas_xywh"]}"/>'
                )
            xml_lines.append("      </zone>")
        xml_lines.append("    </surface>")
    xml_lines.append("  </facsimile>")

    # ==========================================================================
    # TEXT SECTION: 1. DIPLOMATIC TRANSCRIPTION + 2. ALIGNED TRANSLATION
    # ==========================================================================
    xml_lines.append("  <text>")
    xml_lines.append("    <body>")

    # Division 1: Diplomatic Transcription
    xml_lines.append('      <div xml:id="div_transcription" type="transcription" xml:lang="de">')
    xml_lines.append("        <head>Part I: Exact Diplomatic Transcription (Anchored to IIIF Facsimile Zones)</head>")
    for p in PAGES:
        xml_lines.append(
            f'        <div xml:id="tr_{p["page_id"]}" type="page" n="{html.escape(p["orig_page"])}" '
            f'facs="#surf_{p["page_id"]}">'
        )
        xml_lines.append(
            f'          <pb n="{html.escape(p["orig_page"])}" facs="#surf_{p["page_id"]}" '
            f'corresp="https://iiif.wellcomecollection.org/presentation/b18775275/canvases/{p["jp2"]}"/>'
        )
        for fig in p.get("figures", []):
            xml_lines.append(f'          <figure xml:id="tr_{fig["fig_id"]}" facs="#{fig["fig_id"]}">')
            xml_lines.append(f'            <head>{html.escape(fig["label"])}</head>')
            xml_lines.append(f'            <figDesc>{html.escape(fig["desc"])}</figDesc>')
            xml_lines.append("          </figure>")
        for col in p["columns"]:
            col_zid = f'zone_{p["page_id"]}_{col["col_id"]}'
            xml_lines.append(f'          <cb n="{col["col_id"]}" facs="#{col_zid}"/>')
            xml_lines.append(f'          <ab xml:id="ab_tr_{p["page_id"]}_{col["col_id"]}" type="column-block" facs="#{col_zid}">')
            for ln in col["lines"]:
                formatted_de = format_diplomatic_xml_text(ln["de"])
                xml_lines.append(
                    f'            <lb xml:id="{ln["line_id"]}" n="{ln["line_num"]}" '
                    f'facs="#zone_{ln["line_id"]}" corresp="#en_{ln["line_id"]}"/>{formatted_de}'
                )
            xml_lines.append("          </ab>")
        xml_lines.append("        </div>")
    xml_lines.append("      </div>")

    # Division 2: Line-Aligned English Translation
    xml_lines.append('      <div xml:id="div_translation" type="translation" xml:lang="en">')
    xml_lines.append("        <head>Part II: Line-Aligned English Translation (Preserving Line Numbering and IIIF Links)</head>")
    for p in PAGES:
        xml_lines.append(
            f'        <div xml:id="en_{p["page_id"]}" type="page" n="{html.escape(p["orig_page"])}" '
            f'facs="#surf_{p["page_id"]}" corresp="#tr_{p["page_id"]}">'
        )
        xml_lines.append(f'          <pb n="{html.escape(p["orig_page"])}" facs="#surf_{p["page_id"]}"/>')
        for col in p["columns"]:
            col_zid = f'zone_{p["page_id"]}_{col["col_id"]}'
            xml_lines.append(f'          <cb n="{col["col_id"]}" facs="#{col_zid}"/>')
            xml_lines.append(
                f'          <ab xml:id="ab_en_{p["page_id"]}_{col["col_id"]}" type="column-block" '
                f'facs="#{col_zid}" corresp="#ab_tr_{p["page_id"]}_{col["col_id"]}">'
            )
            for ln in col["lines"]:
                en_escaped = format_diplomatic_xml_text(ln["en"])
                note_xml = f'<note type="gloss">{html.escape(ln["note"])}</note>' if ln["note"] else ""
                xml_lines.append(
                    f'            <lb xml:id="en_{ln["line_id"]}" n="{ln["line_num"]}" '
                    f'facs="#zone_{ln["line_id"]}" corresp="#{ln["line_id"]}"/>{en_escaped}{note_xml}'
                )
            xml_lines.append("          </ab>")
        xml_lines.append("        </div>")
    xml_lines.append("      </div>")

    xml_lines.append("    </body>")
    xml_lines.append("  </text>")
    xml_lines.append("</TEI>")

    xml_str = "\n".join(xml_lines)
    tei_path = OUT_DIR / "MS990_tei.xml"
    tei_path.write_text(xml_str, encoding="utf-8")

    # Validate XML well-formedness via ElementTree
    ET.fromstring(xml_str)
    print(f"Wrote and validated TEI P5 XML: {tei_path} ({len(xml_lines)} lines)")


def write_edition_json():
    data = {
        "manifest_v2": IIIF_MANIFEST_V2,
        "manifest_v3": IIIF_MANIFEST_V3,
        "work_url": WORK_URL,
        "glyphs": [
            {"id": g[0], "glyph": g[1], "unicode": g[2], "latin": g[3], "meaning": g[4]}
            for g in GLYPH_TABLE
        ],
        "pages": [],
    }
    for p in PAGES:
        p_copy = dict(p)
        p_copy["frame_box"] = list(p["frame_box"])
        cols = []
        for c in p["columns"]:
            c_copy = dict(c)
            lines = []
            for ln in c["lines"]:
                ln_copy = dict(ln)
                lid = ln["line_id"]
                lnum = ln["line_num"]
                ltype = ln["line_type"]
                ulx, uly, lrx, lry = ln["ulx"], ln["uly"], ln["lrx"], ln["lry"]
                c_xywh = ln["iiif_canvas_xywh"]
                ln_copy["tei_lb"] = (
                    f'<lb xml:id="{lid}" n="{lnum}" facs="#zone_{lid}" corresp="#en_{lid}"/>'
                    + format_diplomatic_xml_text(ln["de"])
                )
                ln_copy["tei_zone"] = (
                    f'<zone xml:id="zone_{lid}" type="{ltype}" ulx="{ulx}" uly="{uly}" '
                    f'lrx="{lrx}" lry="{lry}" corresp="{c_xywh}"/>'
                )
                lines.append(ln_copy)
            c_copy["lines"] = lines
            cols.append(c_copy)
        p_copy["columns"] = cols
        data["pages"].append(p_copy)

    json_path = OUT_DIR / "MS990_edition_data.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote edition JSON: {json_path} ({len(data['pages'])} pages)")


if __name__ == "__main__":
    write_transcription()
    write_translation()
    write_tei_xml()
    write_edition_json()

# Herbarium MGRS Validator

A single-file, browser-based tool for digitizing herbarium specimen labels. It reads a photo of a specimen sheet, extracts the taxonomic and collection data, validates or derives its MGRS grid reference, geocodes localities that don't already have coordinates, assigns a unique barcode, and exports the whole batch as a BRAHMS-ready workbook plus a matching ZIP of photos.

Built for digitizing Kenyan herbarium collections (originally for DRSRS), but the extraction prompts, geocoding bounds, and known-landmark anchors are the only Kenya-specific pieces — everything else generalizes to other regions with modest edits.

## What it does

- **Vision-based extraction** — sends each label photo to a vision-capable LLM (`qwen3-vl-plus` by default) to read species name, author citation, collector, field number, date, habitat, habit, MGRS grid reference, and every place name mentioned on the label.
- **OCR fallback** — if the vision call fails, falls back to Tesseract OCR (tuned page-segmentation mode for label layouts) plus a text-only LLM pass over the raw OCR text.
- **MGRS cross-validation** — cross-checks the recorded grid reference against a second, narrower vision re-read and a regex scan of the OCR text, and picks the reading that parses cleanly when they disagree.
- **Character-confusion-aware parsing** — corrects common OCR/vision misreads within the numeric easting/northing digits (e.g. `O`/`D`/`Q`→`0`, `I`/`L`→`1`, `B`→`8`) before giving up on a malformed-looking grid reference.
- **AL → AA scheme conversion** — detects and converts legacy AL-scheme 100 km-square lettering to the current AA (WGS84/NGA) scheme, based on the specimen's collection date and a configurable cutoff year. Specimens with an unknown date are left unconverted by default rather than risking a silent, incorrect shift; a per-specimen override is available.
- **Tiered geocoding** — when no MGRS is present on the label, geocodes the extracted locality candidates against GeoNames and Nominatim, trying exact matches on specifically-named places first, then fuzzy matches, then bare generic feature words (river, hill, valley, etc.) as a last resort. Known landmark anchors (Mount Kenya, Tsavo, Maasai Mara, major towns, etc.) are used as a distance sanity check to reject implausible matches, and county/district names on the label are used to disambiguate places with duplicate names.
- **Inline correction** — every extracted field is click-to-edit directly in the results panel, with an explicit "Save corrections" step (nothing auto-saves per keystroke) and a "re-geocode from corrected locality" action.
- **Unique barcode generation** — assigns each processed specimen a sequential barcode (`PREFIX000001`, `PREFIX000002`, …) and a matching photo filename in the form `barcode_genus_species_ddmmyyyy_collectornumber`, so the barcode, photo, and workbook row all line up for BRAHMS's image importer.
- **Batch processing** — drag/drop or select multiple images; they queue and process one at a time, with every result kept in a running table.
- **BRAHMS export** — exports the full batch as an `.xlsx` workbook matching BRAHMS's standard field set (taxonomic, collection-event, geographic, and voucher columns), and a ZIP of photos named to match.

## Quick start

This is a single static HTML file with no build step. To run it:

1. Download `herbarium_mgrs_batch.html`.
2. Open it directly in a modern desktop browser (Chrome, Edge, or Firefox), **or** serve it locally:
   ```bash
   python3 -m http.server 8000
   # then open http://localhost:8000/herbarium_mgrs_batch.html
   ```
3. Click **Test connection** to confirm the backend (see below) is reachable.
4. Drop in one or more specimen photos and let them process.

> Opening the file with `file://` works for most features, but some browsers restrict certain APIs (e.g. clipboard, some fetches) under `file://`. Serving it over `http://localhost` avoids any of that friction.

## Backend requirement

This tool does **not** call an LLM API directly from the browser (that would expose an API key client-side). Instead it calls a small proxy backend at:

```
https://mgrs-validator-backend.onrender.com/api/chat
```

which forwards requests to the vision/text models and returns an OpenAI-style `choices[0].message.content` response. You'll need your own equivalent backend — a minimal server that accepts `{ model, messages, temperature }` and proxies it to your LLM provider of choice. Point `BACKEND_URL` (near the top of the `<script>` block) at your own deployment.

Model IDs used by default (also configurable at the top of the script):

| Constant | Default | Purpose |
|---|---|---|
| `VISION_MODEL` | `qwen3-vl-plus` | Reads the label photo directly |
| `TEXT_MODEL` | `qwen-plus` | OCR-fallback extraction, locality spelling suggestions |

Because the backend is often on a free-tier host (e.g. Render's free plan), the first request after idling can take 20–30 seconds to wake up — the connection test surfaces this rather than failing silently.

## Configuration

All of the following are editable directly in the running app (no code changes needed for day-to-day use):

| Setting | Where | Purpose |
|---|---|---|
| **AL → AA cutoff year** | Status bar | Specimens dated before this year are treated as legacy AL-scheme MGRS and converted; on/after, left as current AA scheme. Default `2001` — adjust to match when your region's surveys switched schemes. |
| **Barcode prefix** | Status bar | Prefix for generated barcodes (e.g. `DRSRS` → `DRSRS000001`). The counter is stored per-prefix in the browser's `localStorage`, so it persists across sessions and reloads. |
| **Reset counter** | Status bar | Resets the barcode counter for the *current* prefix back to zero. Only use this before starting a genuinely new batch — resetting mid-project risks duplicate barcodes if earlier numbers are already in use elsewhere (BRAHMS, prior exports, printed labels). |
| **Grid Scheme override** | Per-specimen, results panel | Forces a specimen's recorded MGRS to be interpreted as AL or AA, overriding the date-based default — useful when a label has no parseable date or the date parsing misfires. |

Code-level configuration (top of the `<script>` block, or the `GEONAMES_USER` constant):

- `BACKEND_URL`, `VISION_MODEL`, `TEXT_MODEL` — see above.
- `GEONAMES_USER` — your [GeoNames](https://www.geonames.org/login) account username (free registration; needed for the GeoNames geocoding tier). Nominatim (OpenStreetMap) is used as a fallback and needs no key.
- `KENYA_BOUNDS`, `KENYA_COUNTIES`, `KNOWN_ANCHORS` — adjust or replace these if you're digitizing a different country's collections. `KNOWN_ANCHORS` in particular is what gives the geocoder a sanity-check radius around well-known landmarks; add your own region's equivalents.

## Barcode & filename convention

Each processed specimen is assigned:

- **Barcode:** `PREFIX` + 6-digit zero-padded sequence, e.g. `DRSRS000001`. Editable per-specimen if you need to correct or reassign it.
- **Image filename:** `barcode_genus_species_ddmmyyyy_collectornumber.<ext>`, e.g. `DRSRS000001_Uvaria_lucida_11011981_13880.jpg`.
  - `genus_species` comes from the extracted species name (author citation excluded).
  - `ddmmyyyy` is zero-padded from the extracted collection date; unknown day/month/year fall back to `00` and `0000` respectively rather than being guessed.
  - `collectornumber` is the extracted field/collector number, or `sn` (*sine numero* — "without number") if none was found on the label.

This filename is written into the exported workbook's **Image Filename** column and is exactly how the photo is named in the downloaded ZIP, so BRAHMS's image importer can match photo files to specimen records directly on import.

## BRAHMS export column mapping

The exported `.xlsx` follows BRAHMS's standard field structure:

- **Taxonomic:** Family *(blank — not extracted from labels)*, Genus, Species, Author, #Full Name
- **Collection event:** Collector, Field Number, Date Collected, Day, Month, Year, Determined By / Determination Date *(blank — filled in during identification, not present on collection labels)*
- **Geographic:** Country, Gazetteer (matched/most specific place name), Locality Notes (other candidates), Latitude, Longitude, Map Grid Area (final MGRS), Georef Source
- **Descriptive:** Habitat, Habit
- **Linking:** Image Filename
- **Voucher:** Barcode (generated by this tool), Accession Number / Herbarium Code / Type Status / Duplicates *(blank — assigned at accessioning)*
- **Provenance:** Extraction Method, Notes

Rename headers in `exportBRAHMSXLSX()` if your BRAHMS import template differs — row content is unaffected either way.

## Tech stack

Pure client-side HTML/CSS/JS — no framework, no build step, no server component beyond the LLM proxy.

- [Tailwind CSS](https://tailwindcss.com/) (CDN) — base styling utility classes
- [Tesseract.js](https://github.com/naptha/tesseract.js) — in-browser OCR fallback
- [JSZip](https://stuk.github.io/jszip/) — bundling exported photos into a ZIP
- [SheetJS (xlsx)](https://github.com/SheetJS/sheetjs) — building the `.xlsx` workbook
- [mgrs](https://github.com/proj4js/mgrs) — MGRS ↔ lat/lon conversion
- [GeoNames](https://www.geonames.org/) and [Nominatim](https://nominatim.org/) — geocoding
- A small self-hosted backend proxying to an LLM provider (vision + text)

## Known limitations

- Geocoding and the known-landmark anchors are scoped to Kenya (`KENYA_BOUNDS`, `KENYA_COUNTIES`, `KNOWN_ANCHORS`) — using this for another country's collections requires updating those constants.
- Handwritten labels remain the hardest case for both the vision model and Tesseract; always spot-check extracted fields, especially the MGRS reading, against the source image.
- Family is not extracted (not reliably present on most labels) and is left blank in the export for manual entry.
- The barcode counter lives in browser `localStorage`, scoped to one browser/profile — it is **not** synchronized across machines or shared with collaborators. If more than one person is digitizing into the same barcode sequence, coordinate prefixes/ranges out of band (e.g. assign each digitizer a distinct prefix, or agree on non-overlapping counter ranges) to avoid collisions.
- No authentication or access control — this is a single-user local tool, not a multi-user web service.

## Roadmap ideas

- Export barcodes as printable labels (e.g. Code128/QR) alongside the workbook.
- Optional server-side persistence so a batch can be resumed across devices.
- Region-agnostic geocoding config (swap country bounds/anchors via a settings panel instead of code edits).

## License

Add your preferred license here (e.g. MIT) before publishing.

## Acknowledgments

Built for herbarium specimen digitization workflows at the Directorate of Resource Surveys and Remote Sensing (DRSRS), Kenya.

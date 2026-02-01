---
name: transcribe-pdf
description: Render a scanned PDF to per-page images, auto-crop UI/header bars, then transcribe page-by-page using LLM vision (no OCR) into a single Markdown file.
---

# Transcribe a scanned PDF to Markdown (vision-only)

## Make it autonomous (reduce prompts)

This skill writes images and a running `transcription.md`. If your Copilot CLI asks for approval on each file write, **have the user run** `/allow-all` (or `/yolo`) once at the start of the session so you can proceed without repeated interruptions.

## Hard rules (must follow)

- **NO OCR**: do not run OCR tools or OCR libraries. Transcription must be done using **LLM vision**.
- **No web search**: do not search the web for any content.
- **Whole document, one page at a time**: render/prepare images for the whole PDF once, but **transcribe sequentially page-by-page** (never batch multiple pages into one vision prompt).
- **Don’t overdo it**: transcribe what’s legible in the page image; use placeholders for uncertain/unreadable parts.
- **No zoom / no slicing unless necessary**: prefer the already-cropped full-page image.
- **Do not stop to ask**: after starting, continue through all pages, appending as you go.
- **Use Markdown**: transcribe into a single Markdown file, with headings for each page. Append directly to the file.
- **Use the provided scripts**: use the included Python scripts for rendering/cropping; do not invent your own methods.
- **Write scripts to a file**: especially if running on Windows PowerShell, if you need to run a script, write it to a file and then execute it. When running on any Linux shell, you can run scripts inline.

## Why cropping matters (key finding)

Many archival viewers add header/footer UI bars (e.g., “PARES …”). These reduce effective resolution and can confuse transcription.
**Always crop those bars out** before transcribing.

## Workflow

### 0) Install dependencies (once)

It is recommended to use a virtual environment to avoid conflicts with system packages.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r "<skill_root>/scripts/requirements.txt"
```

### 1) (Optional) Confirm there is no usable text layer

This is a quick sanity check to avoid wasting time trying to extract text that isn’t there.

```bash
python "<skill_root>/scripts/check_text_layer_sample.py" "<pdf_path>"
```

If the samples show ~0 characters or only metadata, proceed with image transcription.

### 2) Prepare images for the whole PDF (single command)

This skill uses an intelligent script that:

1. Automatically analyzes a random sample of pages to check for headers/footers.
2. Automatically detects content bounding boxes (smart crop).
3. Splits double-page scans (landscape) into single pages.
4. Skips blank pages.

Run the smart processing command:

```bash
python "<skill_root>/scripts/render_and_crop_pdf.py" "<pdf_path>" "<out_dir>" --zoom 2.0
```

**Note**: The script ignores `--top`, `--bottom`, etc. as it uses computer vision to find the content.

Outputs:

- `"<out_dir>/cropped/page-01.png"`, `page-02.png`, etc.
- Logs indicating which pages were split or skipped.

Verify the first few output images to ensure headers are removed and content is preserved. If automatic cropping fails, you may need to modify the `smart_crop` function in `render_and_crop_pdf.py`.

### 3) Transcribe the whole document, one page at a time (LLM vision)

Create the transcript file if it doesn’t exist, then append each page immediately (never hold results in chat).

- Transcript path: `"<out_dir>/transcription.md"`
- For each page image in `"<out_dir>/cropped"`:
  - **Sorting Order**:
    - Sort files alphabetically.
    - If a page was split into `page-###L.png` and `page-###R.png`:
      - Process `L` (Left) first.
      - Process `R` (Right) second.
      - E.g. `page-006L.png` then `page-006R.png`.
  1. Open/view **exactly one** image (e.g., `page-021.png` or `page-006L.png`).
  2. Transcribe what you can see into Markdown.
  3. Append immediately to the transcript under a heading `## Page N` (use the file name suffix if useful, e.g. `## Page 6 (Left)`).
  4. Move to the next page and repeat until the final page.

### Transcription conventions

- Preserve original spelling/orthography when possible (old Spanish is expected).
- Use placeholders instead of guessing:
  - `[ilegible]` for unreadable words/lines
  - `[¿…?]` for uncertain readings
- If a page is blank or non-text: write `[Página en blanco]` or `[Blank page]` or a short note.

## Helper scripts included

- `render_and_crop_pdf.py`: render + smart crop in one command (preferred).
- `check_text_layer_sample.py`: sample embedded PDF text layer (non-OCR).

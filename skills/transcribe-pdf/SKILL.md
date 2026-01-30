---
name: transcribe-pdf
description: Render a scanned PDF to per-page images, auto-crop UI/header bars, then transcribe page-by-page using LLM vision (no OCR) into a single Markdown file.
---

# Transcribe a scanned PDF to Markdown (vision-only)

## Make it autonomous (reduce prompts)

This skill writes images and a running `transcription.md`. If your Copilot CLI asks for approval on each file write, **have the user run** `/allow-all` (or `/yolo`) once at the start of the session so you can proceed without repeated interruptions.

## Hard rules (must follow)

- **NO OCR**: do not run OCR tools or OCR libraries. Transcription must be done using **LLM vision**.
- **Whole document, one page at a time**: render/prepare images for the whole PDF once, but **transcribe sequentially page-by-page** (never batch multiple pages into one vision prompt).
- **Don’t overdo it**: transcribe what’s legible in the page image; use placeholders for uncertain/unreadable parts.
- **No zoom / no slicing unless necessary**: prefer the already-cropped full-page image.
- **Do not stop to ask**: after starting, continue through all pages, appending as you go.

## Why cropping matters (key finding)

Many archival viewers add header/footer UI bars (e.g., “PARES …”). These reduce effective resolution and can confuse transcription.
**Always crop those bars out** before transcribing.

## Workflow

### 0) Install dependencies (once)

```powershell
pip install -r "<skill_root>\scripts\requirements.txt"
```

### 1) (Optional) Confirm there is no usable text layer

This is a quick sanity check to avoid wasting time trying to extract text that isn’t there.

```powershell
python "<skill_root>\scripts\check_text_layer_sample.py" "<pdf_path>"
```

If the samples show ~0 characters or only metadata, proceed with image transcription.

### 2) Prepare images for the whole PDF (single command)

If the workspace already contains correctly-cropped `page-*.png` images, **skip to Step 3**.

**Recommended**: render + crop in one run.

```powershell
python "<skill_root>\scripts\render_and_crop_pdf.py" "<pdf_path>" "<out_dir>" --zoom 2.0
```

Outputs:
- `"<out_dir>\cropped\page-01.png"`, `page-02.png`, … (canonical inputs for transcription)

Crop defaults are tuned to remove common header/footer bars at `--zoom 2.0`:
- `--top 280 --bottom 140` (adjust if needed)

### 3) Transcribe the whole document, one page at a time (LLM vision)

Create the transcript file if it doesn’t exist, then append each page immediately (never hold results in chat).

- Transcript path: `"<out_dir>\transcription.md"`
- For each page image in `"<out_dir>\cropped"`:
  1. Open/view **exactly one** image (e.g., `page-21.png`).
  2. Transcribe what you can see into Markdown.
  3. Append immediately to the transcript under a heading `## Page N`.
  4. Move to the next page and repeat until the final page.

### Transcription conventions

- Preserve original spelling/orthography when possible (old Spanish is expected).
- Use placeholders instead of guessing:
  - `[ilegible]` for unreadable words/lines
  - `[¿…?]` for uncertain readings
- If a page is blank or non-text: write `[Página en blanco]` or a short note.

## Helper scripts included

- `render_pdf_to_images.py`: render PDF pages to PNGs.
- `render_and_crop_pdf.py`: render + crop in one command (preferred).
- `crop_images.py`: crop an existing set of `page-*.png` images.
- `check_text_layer_sample.py`: sample embedded PDF text layer (non-OCR).

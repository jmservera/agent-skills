---
name: transcribe-pdf
description: Extracts the PNG images from a PDF into per-page PNG images using a bundled Python script (PyMuPDF). Then uses the LLM vision capabilites to transcribe each page into Markdown and appends each page's content to a single Markdown file. Use when the user asks to convert/render/extract PDF pages as images, especially for scanned PDFs.
---

# Transcribe a scanned PDF to text

Always follow this process:

1. Use the bundled script to render each page of a PDF to PNG images in one run (the script writes all files itself, so you only need to approve a single command).
2. Use the LLM vision capabilities to transcribe each PNG image to Markdown, one at a time. Never send all the pictures at once as this will exceed context limits.

## Workflow

1. Ensure Python is available.
2. Install the dependency once per environment:
   - pip install -r "<skill_root>\scripts\requirements.txt"

3. Render pages (single command):
   - python "<skill_root>\scripts\render_pdf_to_images.py" "<pdf_path>" "<out_dir>" --zoom 2.0
4. For each PNG image in out_dir:
   - Use the LLM vision capabilities to transcribe the image to Markdown.

## Notes

- The script creates out_dir if it does not exist.
- Output files are named page-01.png, page-02.png, ...
- Increase --zoom if text is too small.
- Ensure to handle multi-page PDFs by processing each image sequentially.
- Append each page's transcribed Markdown content to a single Markdown file for the entire PDF.

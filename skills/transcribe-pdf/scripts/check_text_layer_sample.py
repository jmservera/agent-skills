import argparse

import fitz  # PyMuPDF


def parse_pages(pages: str) -> list[int]:
    # "1,2,3,14" -> [0,1,2,13]
    out: list[int] = []
    for part in pages.split(","):
        part = part.strip()
        if not part:
            continue
        n = int(part)
        if n <= 0:
            continue
        out.append(n - 1)
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Quickly sample a PDF text layer (if any). Useful to confirm the manuscript is image-only."
        )
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument(
        "--pages",
        default="1,2,3,14",
        help='Comma-separated 1-based page numbers to sample (default: "1,2,3,14")',
    )
    parser.add_argument(
        "--preview-chars",
        type=int,
        default=800,
        help="How many characters of extracted text to print (default: 800)",
    )
    args = parser.parse_args()

    doc = fitz.open(args.pdf_path)
    print("pages", doc.page_count)

    for i in parse_pages(args.pages):
        if i >= doc.page_count:
            continue
        page = doc.load_page(i)
        text = (page.get_text("text") or "").strip()
        print(f"\n--- page {i+1} text chars: {len(text)} ---")
        if text:
            print(text[: args.preview_chars])

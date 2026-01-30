import argparse
import os
import time
import fitz  # PyMuPDF


def render_pdf_to_images(pdf_path: str, out_dir: str, zoom: float = 2.0) -> None:
    """Render each page of a PDF to a PNG image.

    Args:
        pdf_path: Path to the input PDF file.
        out_dir: Directory to save the output images.
        zoom: Zoom factor for rendering (default 2.0, increase if text is too small).
    """
    os.makedirs(out_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(zoom, zoom)

    for i in range(doc.page_count):
        t0 = time.time()
        pix = doc.load_page(i).get_pixmap(matrix=mat, alpha=False)
        out_path = os.path.join(out_dir, f"page-{i+1:02d}.png")
        pix.save(out_path)
        print(
            f"{i+1}/{doc.page_count} saved {out_path} ({os.path.getsize(out_path)} bytes) in {time.time()-t0:.2f}s",
            flush=True,
        )

    print("done", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render PDF pages to PNG images.")
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("out_dir", help="Directory to save the output images")
    parser.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="Zoom factor for rendering (default: 2.0)",
    )
    args = parser.parse_args()

    render_pdf_to_images(args.pdf_path, args.out_dir, args.zoom)

import argparse
import os
import time
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image


def render_and_crop(pdf_path: str, out_dir: str, zoom: float, top: int, bottom: int, left: int, right: int, keep_rendered: bool) -> None:
    out_root = Path(out_dir)
    rendered_dir = out_root / "rendered"
    cropped_dir = out_root / "cropped"
    rendered_dir.mkdir(parents=True, exist_ok=True)
    cropped_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(zoom, zoom)

    print(f"pages {doc.page_count}")
    print(f"rendered_dir {rendered_dir}")
    print(f"cropped_dir {cropped_dir}")

    for i in range(doc.page_count):
        t0 = time.time()
        pix = doc.load_page(i).get_pixmap(matrix=mat, alpha=False)
        rendered_path = rendered_dir / f"page-{i+1:02d}.png"
        pix.save(str(rendered_path))

        img = Image.open(rendered_path)
        w, h = img.size
        cropped = img.crop((left, top, w - right, h - bottom))
        cropped_path = cropped_dir / rendered_path.name
        cropped.save(cropped_path)

        if not keep_rendered:
            try:
                rendered_path.unlink()
            except OSError:
                pass

        print(
            f"{i+1}/{doc.page_count} saved {cropped_path} ({os.path.getsize(cropped_path)} bytes) in {time.time()-t0:.2f}s",
            flush=True,
        )

    print("done", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Render a scanned PDF to page images and crop them to remove viewer headers/footers.",
    )
    parser.add_argument("pdf_path", help="Path to the input PDF file")
    parser.add_argument("out_dir", help="Output directory (will create 'cropped' and optionally 'rendered')")
    parser.add_argument(
        "--zoom",
        type=float,
        default=2.0,
        help="Zoom factor for rendering (default: 2.0)",
    )
    parser.add_argument("--top", type=int, default=280, help="Pixels to remove from top (default: 280)")
    parser.add_argument(
        "--bottom",
        type=int,
        default=140,
        help="Pixels to remove from bottom (default: 140)",
    )
    parser.add_argument("--left", type=int, default=0, help="Pixels to remove from left (default: 0)")
    parser.add_argument("--right", type=int, default=0, help="Pixels to remove from right (default: 0)")
    parser.add_argument(
        "--keep-rendered",
        action="store_true",
        help="Keep intermediate rendered images in out_dir\\rendered (default: delete them)",
    )
    args = parser.parse_args()

    render_and_crop(
        args.pdf_path,
        args.out_dir,
        args.zoom,
        args.top,
        args.bottom,
        args.left,
        args.right,
        args.keep_rendered,
    )

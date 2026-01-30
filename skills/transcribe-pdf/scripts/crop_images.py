import argparse
from pathlib import Path

from PIL import Image


def crop_pages(in_dir: Path, out_dir: Path, top: int, bottom: int, left: int, right: int) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    pages = sorted(in_dir.glob("page-*.png"))
    if not pages:
        raise SystemExit(f"No page-*.png found in: {in_dir}")

    print(f"pages {len(pages)}")
    for p in pages:
        img = Image.open(p)
        w, h = img.size
        cropped = img.crop((left, top, w - right, h - bottom))
        out_path = out_dir / p.name
        cropped.save(out_path)
        print(f"saved {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crop rendered PDF page images to remove viewer headers/footers.",
    )
    parser.add_argument("in_dir", help="Directory containing page-*.png")
    parser.add_argument("out_dir", help="Directory to write cropped page-*.png")
    parser.add_argument("--top", type=int, default=280, help="Pixels to remove from top (default: 280)")
    parser.add_argument(
        "--bottom",
        type=int,
        default=140,
        help="Pixels to remove from bottom (default: 140)",
    )
    parser.add_argument("--left", type=int, default=0, help="Pixels to remove from left (default: 0)")
    parser.add_argument("--right", type=int, default=0, help="Pixels to remove from right (default: 0)")
    args = parser.parse_args()

    crop_pages(Path(args.in_dir), Path(args.out_dir), args.top, args.bottom, args.left, args.right)

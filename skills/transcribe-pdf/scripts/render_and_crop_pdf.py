import fitz
import cv2
import numpy as np
import os
import argparse
from pathlib import Path

def is_blank(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean, stddev = cv2.meanStdDev(gray)
    if stddev[0][0] < 15: 
        return True
    edges = cv2.Canny(gray, 50, 150)
    edge_pixels = cv2.countNonZero(edges)
    total_pixels = image.shape[0] * image.shape[1]
    if edge_pixels / total_pixels < 0.01:
        return True
    return False

def smart_crop(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    if not contours:
        return image
        
    x_min, y_min = float('inf'), float('inf')
    x_max, y_max = float('-inf'), float('-inf')
    found_content = False
    h, w = image.shape[:2]
    
    for cnt in contours:
        x, y, cw, ch = cv2.boundingRect(cnt)
        if cw < 20 or ch < 20: continue
        if cw > w * 0.95 and ch > h * 0.95: continue
            
        found_content = True
        x_min = min(x_min, x)
        y_min = min(y_min, y)
        x_max = max(x_max, x + cw)
        y_max = max(y_max, y + ch)
        
    if not found_content:
        return image
        
    padding = 20
    x_min = max(0, int(x_min - padding))
    y_min = max(0, int(y_min - padding))
    x_max = min(w, int(x_max + padding))
    y_max = min(h, int(y_max + padding))
    
    if (x_max - x_min) < 50 or (y_max - y_min) < 50:
        return image
        
    return image[y_min:y_max, x_min:x_max]

def process_pdf(pdf_path, out_dir, zoom=2.0, keep_rendered=False, **kwargs):
    doc = fitz.open(pdf_path)
    mat = fitz.Matrix(zoom, zoom)
    
    out_root = Path(out_dir)
    out_cropped = out_root / "cropped"
    out_rendered = out_root / "rendered"
    
    # Clean up previous cropped files to avoid mixing
    if out_cropped.exists():
        for f in out_cropped.glob("*.png"):
            f.unlink()
            
    out_cropped.mkdir(parents=True, exist_ok=True)
    if keep_rendered:
        out_rendered.mkdir(parents=True, exist_ok=True)
    
    print(f"Processing {pdf_path}...")
    print(f"Total pages: {doc.page_count}")
    
    saved_count = 0
    
    for i in range(doc.page_count):
        page = doc.load_page(i)
        pix = page.get_pixmap(matrix=mat)
        
        if keep_rendered:
            render_path = out_rendered / f"page-{i+1:03d}.png"
            pix.save(str(render_path))
        
        img_array = np.frombuffer(pix.samples, dtype=np.uint8)
        if pix.n == 4:
            img = img_array.reshape(pix.h, pix.w, 4)
            img = cv2.cvtColor(img, cv2.COLOR_RGBA2RGB)
        elif pix.n == 3:
            img = img_array.reshape(pix.h, pix.w, 3)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        elif pix.n == 1:
            img = img_array.reshape(pix.h, pix.w, 1)
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        else:
            continue
            
        h, w = img.shape[:2]
        aspect = w / h
        
        pages_to_process = []
        if aspect > 1.3: 
            # Smart split logic
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            h_gray, w_gray = gray.shape
            
            # Focus on the middle 20% of the page
            mid_start = int(w_gray * 0.4)
            mid_end = int(w_gray * 0.6)
            mid_region = gray[:, mid_start:mid_end]
            
            # Invert to count dark pixels
            inverted = 255 - mid_region
            
            # Sum pixel values vertically
            col_sums = np.sum(inverted, axis=0)
            
            # Smooth to find the gutter (minimum ink)
            kernel_size = 20
            kernel = np.ones(kernel_size) / kernel_size
            smoothed_sums = np.convolve(col_sums, kernel, mode='same')
            
            # Smart split logic: Look for gutter (white) or binding line (dark)
            mid_start = int(w_gray * 0.45) # 45%
            mid_end = int(w_gray * 0.55)   # 55%
            
            mid_region = gray[:, mid_start:mid_end]
            inverted = 255 - mid_region
            col_sums = np.sum(inverted, axis=0)
            
            # Check for dark binding line
            # If peak darkness is high relative to height (e.g. > 100 avg inverted val), assume binding line
            # Text columns are usually mostly white (low inverted sum), binding lines are dark (high inverted sum)
            max_val = np.max(col_sums)
            height = mid_region.shape[0]
            
            if max_val > (100 * height): 
                 split_offset = np.argmax(col_sums) # Find darkest column (binding)
            else:
                 split_offset = np.argmin(col_sums) # Find whitest column (gutter)
                 
            split_x = mid_start + split_offset
            
            left_page = img[:, :split_x]

            right_page = img[:, split_x:]
            pages_to_process = [("L", left_page), ("R", right_page)]
        else:
            pages_to_process = [("", img)]
            
        for suffix, sub_img in pages_to_process:
            cropped = smart_crop(sub_img)
            if is_blank(cropped):
                print(f"Page {i+1}{suffix}: Blank - Skipped")
                continue
            
            filename = f"page-{i+1:03d}{suffix}.png"
            full_path = out_cropped / filename
            cv2.imwrite(str(full_path), cropped)
            saved_count += 1
            print(f"Page {i+1}{suffix}: Saved")

    print(f"Done. Saved {saved_count} images to {out_cropped}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("pdf_path")
    parser.add_argument("out_dir")
    parser.add_argument("--zoom", type=float, default=2.0)
    parser.add_argument("--top", type=int, default=0)
    parser.add_argument("--bottom", type=int, default=0)
    parser.add_argument("--left", type=int, default=0)
    parser.add_argument("--right", type=int, default=0)
    parser.add_argument("--keep-rendered", action="store_true")
    
    args = parser.parse_args()
    process_pdf(**vars(args))

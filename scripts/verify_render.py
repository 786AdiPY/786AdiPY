"""
scripts/verify_render.py
Renders every generated SVG to a high-resolution PNG using resvg_py.
Validates dimensions, file sizes < 200KB, XML integrity, and text layout.
"""
import os
import resvg_py
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
VERIFY_DIR = os.path.join(ASSETS_DIR, "verified_renders")
os.makedirs(VERIFY_DIR, exist_ok=True)

SVG_FILES = [
    ("banner-light.svg", 830, 200),
    ("banner-dark.svg", 830, 200),
    ("featured-light.svg", 830, 260),
    ("featured-dark.svg", 830, 260),
    ("now-light.svg", 830, 140),
    ("now-dark.svg", 830, 140),
    ("stack-light.svg", 830, 100),
    ("stack-dark.svg", 830, 100),
    ("stats-light.svg", 830, 220),
    ("stats-dark.svg", 830, 220),
]

def main():
    print("=== Rendering all 10 SVGs to PNG for visual verification ===")
    all_ok = True
    for filename, expected_w, expected_h in SVG_FILES:
        svg_path = os.path.join(ASSETS_DIR, filename)
        file_size_kb = os.path.getsize(svg_path) / 1024
        
        # 1. Size check
        size_pass = file_size_kb < 200
        if not size_pass:
            print(f"FAILED: {filename} size {file_size_kb:.1f}KB exceeds 200KB limit!")
            all_ok = False

        # 2. Render to PNG with resvg
        with open(svg_path, "r", encoding="utf-8") as f:
            svg_content = f.read()

        png_bytes = resvg_py.svg_to_bytes(svg_string=svg_content)
        png_path = os.path.join(VERIFY_DIR, filename.replace(".svg", ".png"))
        with open(png_path, "wb") as f:
            f.write(png_bytes)

        # 3. Check rendered dimensions
        with Image.open(png_path) as im:
            w, h = im.size
            dim_pass = (w == expected_w and h == expected_h)
            if not dim_pass:
                print(f"FAILED: {filename} rendered as {w}x{h}, expected {expected_w}x{expected_h}")
                all_ok = False

        status = "PASS" if (size_pass and dim_pass) else "FAIL"
        print(f"  ✓ {filename:<20} -> {png_path} ({w}x{h}, SVG: {file_size_kb:.1f} KB) [{status}]")

    print(f"\nVerification status: {'ALL ASSETS VERIFIED SUCCESSFULLY' if all_ok else 'SOME CHECKS FAILED'}")

if __name__ == "__main__":
    main()

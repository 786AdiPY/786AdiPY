"""
generate_avatar.py
Fetches the user's GitHub avatar and creates a retro newsprint halftone / dithered portrait.
Palette: Cream #F1EDE4, Ink #111111.
"""
import io
import os
import urllib.request
from PIL import Image, ImageEnhance
import numpy as np

def generate_avatar(username="786AdiPY", output_path="assets/avatar-halftone.png"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    avatar_url = f"https://github.com/{username}.png"
    img = None
    try:
        req = urllib.request.Request(avatar_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            img = Image.open(io.BytesIO(data))
    except Exception as e:
        print(f"Warning: Could not fetch avatar online ({e}), trying existing output path fallback...")
        if os.path.exists(output_path):
            img = Image.open(output_path)
        else:
            img = Image.new("RGB", (460, 460), (200, 200, 200))
    
    # Convert to grayscale
    gray = img.convert("L")
    
    # Resize to standard high-res square (460x460)
    gray = gray.resize((460, 460), Image.Resampling.LANCZOS)
    
    # Enhance contrast and sharpness for newsprint reproduction
    enhanced = ImageEnhance.Contrast(gray).enhance(1.6)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.8)
    
    # Floyd-Steinberg error diffusion dithering (1-bit)
    dithered = enhanced.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    
    # Map to newsprint palette: False (0, black) -> #111111, True (1, white) -> #F1EDE4
    arr = np.array(dithered)
    h, w = arr.shape
    newsprint = np.zeros((h, w, 3), dtype=np.uint8)
    newsprint[arr == False] = [0x11, 0x11, 0x11]
    newsprint[arr == True] = [0xF1, 0xED, 0xE4]
    
    out_img = Image.fromarray(newsprint, "RGB")
    out_img.save(output_path, "PNG", optimize=True)
    print(f"Generated {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_avatar()

"""
generate_banner.py
Generates the retro newsprint 1280x220 banner SVG.
Self-contained with embedded base64 fonts and halftone artwork.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fonts_data import FONT_STYLESHEET
from illustrations_data import ILLUSTRATION_MOUNTAIN

def generate_banner(output_path="assets/banner.svg", brand_title="Adithya"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 114px font size for 'Adithya' gives the giant serif masthead style
    font_size = 114 if len(brand_title) <= 8 else (98 if len(brand_title) <= 12 else 86)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 220" width="1280" height="220">
  <defs>
    <style>
      {FONT_STYLESHEET}
      .bg {{ fill: #F1EDE4; }}
      .ink {{ fill: #111111; }}
      .rule {{ stroke: #111111; }}
      .meta-text {{
        font-family: 'IBM Plex Mono', 'Courier Prime', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        fill: #111111;
      }}
      .brand-title {{
        font-family: 'DM Serif Display', 'Playfair Display', Georgia, serif;
        font-size: {font_size}px;
        font-weight: 400;
        letter-spacing: 0.5px;
        fill: #111111;
      }}
    </style>
  </defs>

  <!-- Paper background -->
  <rect width="1280" height="220" class="bg" />

  <!-- Top Metadata -->
  <text x="24" y="27" class="meta-text">ENGINEERING / SYSTEMS / EXPERIMENTS</text>
  <text x="1256" y="27" class="meta-text" text-anchor="end">EST. 2023</text>

  <!-- Top rule -->
  <line x1="20" y1="36" x2="1260" y2="36" class="rule" stroke-width="1.5" />

  <!-- Giant serif brand -->
  <text x="24" y="156" class="brand-title">{brand_title}</text>

  <!-- Dithered mountain range and sun illustration -->
  <image href="data:image/png;base64,{ILLUSTRATION_MOUNTAIN}" x="660" y="42" width="600" height="148" preserveAspectRatio="xMidYMid meet" />

  <!-- Bottom rules (Double newsprint masthead rule) -->
  <line x1="20" y1="194" x2="1260" y2="194" class="rule" stroke-width="1.5" />
  <line x1="20" y1="198" x2="1260" y2="198" class="rule" stroke-width="0.75" />
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.strip())
        
    print(f"Generated {output_path} with title '{brand_title}' ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_banner()

"""
generate_header.py
Generates the retro newsprint header block SVG (optional SVG embed for README).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fonts_data import FONT_STYLESHEET

def generate_header(output_path="assets/header.svg"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 90" width="980" height="90">
  <defs>
    <style>
      {FONT_STYLESHEET}
      .head-bg {{ fill: #F1EDE4; }}
      .head-rule {{ stroke: #111111; }}
      .head-name {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 24px;
        font-weight: 400;
        fill: #111111;
      }}
      .head-handle {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        fill: #555555;
      }}
      .head-tagline {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        fill: #111111;
      }}
      .head-slash {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        fill: #222222;
      }}
      .head-link {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        fill: #111111;
        font-weight: 700;
      }}
    </style>
  </defs>

  <rect width="980" height="90" class="head-bg" />
  
  <!-- Subtle newsprint enclosure -->
  <rect x="1" y="1" width="978" height="88" rx="6" ry="6" fill="#F1EDE4" stroke="#111111" stroke-width="1.2" />

  <!-- Name & Handle & Tagline -->
  <text x="24" y="32" class="head-name">Adithya A M</text>
  <text x="180" y="30" class="head-handle">@786AdiPY</text>
  <text x="280" y="30" class="head-tagline">&#9632; TECH ENTHUSIAST</text>

  <!-- Slash list -->
  <text x="24" y="62" class="head-slash">/ Full-Stack Developer &nbsp;&nbsp;&nbsp; / AI Engineer &nbsp;&nbsp;&nbsp; / Systems &amp; Security</text>

  <!-- LinkedIn link indicator -->
  <text x="956" y="48" class="head-link" text-anchor="end">&#128279; in/adithya-am-adi &#8599;</text>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.strip())
    print(f"Generated {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_header()

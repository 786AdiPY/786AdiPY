"""
generate_footer.py
Generates the retro newsprint "ACTIVITY OVERVIEW | CODE REVIEW" divider SVG.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from fonts_data import FONT_STYLESHEET

def generate_footer(output_path="assets/footer.svg"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 44" width="980" height="44">
  <defs>
    <style>
      {FONT_STYLESHEET}
      .footer-bg {{ fill: #F1EDE4; }}
      .footer-rule {{ stroke: #111111; }}
      .footer-text {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 2px;
        fill: #111111;
      }}
      .footer-icon {{ fill: #111111; }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="980" height="44" class="footer-bg" />

  <!-- Top double rules -->
  <line x1="0" y1="1" x2="980" y2="1" class="footer-rule" stroke-width="1.5" />
  <line x1="0" y1="4" x2="980" y2="4" class="footer-rule" stroke-width="0.5" />

  <!-- Left: Activity Overview -->
  <g transform="translate(18, 14)">
    <!-- Bar chart icon -->
    <rect x="0" y="8" width="3" height="8" class="footer-icon" />
    <rect x="5" y="4" width="3" height="12" class="footer-icon" />
    <rect x="10" y="1" width="3" height="15" class="footer-icon" />
    <rect x="15" y="6" width="3" height="10" class="footer-icon" />
    <text x="28" y="13" class="footer-text">ACTIVITY OVERVIEW</text>
  </g>

  <!-- Center vertical divider -->
  <line x1="490" y1="10" x2="490" y2="34" stroke="#888888" stroke-width="1" />

  <!-- Right: Code Review -->
  <g transform="translate(515, 14)">
    <!-- Code bracket icon < > -->
    <text x="0" y="13" class="footer-text" font-weight="700">&lt; &gt;</text>
    <text x="36" y="13" class="footer-text">CODE REVIEW</text>
  </g>

  <!-- Bottom rule -->
  <line x1="0" y1="43" x2="980" y2="43" class="footer-rule" stroke-width="1" />
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.strip())
    print(f"Generated {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_footer()

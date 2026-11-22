"""
generate_cards.py
Generates the 4 custom retro newsprint pinned repository cards (SVG).
Pulls repository metadata from GitHub REST API, with fallback to curated descriptions.
Self-contained with embedded base64 fonts and halftone illustrations.
"""
import os
import sys
import urllib.request
import json

sys.path.insert(0, os.path.dirname(__file__))
from fonts_data import FONT_STYLESHEET
from illustrations_data import (
    ILLUSTRATION_LAYERS,
    ILLUSTRATION_ROAD,
    ILLUSTRATION_CUBES,
    ILLUSTRATION_TERMINAL
)

CARDS_CONFIG = [
    {
        "repo": "Kompress",
        "name": "Kompress",
        "default_desc": "A modern file compression tool with high performance and clean UI.",
        "default_lang": "Python",
        "illustration_b64": ILLUSTRATION_LAYERS,
        "output": "assets/card-kompress.svg"
    },
    {
        "repo": "RangeShield-AI",
        "name": "RangeShield-AI",
        "default_desc": "EV range optimization using GenAI and Google Cloud.",
        "default_lang": "TypeScript",
        "illustration_b64": ILLUSTRATION_ROAD,
        "output": "assets/card-rangeshield.svg"
    },
    {
        "repo": "Arize",
        "name": "Arize",
        "default_desc": "MLOps agent that eases ML lifecycle.",
        "default_lang": "Python",
        "illustration_b64": ILLUSTRATION_CUBES,
        "output": "assets/card-arize.svg"
    },
    {
        "repo": "LeetGeek",
        "name": "LeetGeek",
        "default_desc": "A lightweight LeetCode tracker and analytics dashboard.",
        "default_lang": "JavaScript",
        "illustration_b64": ILLUSTRATION_TERMINAL,
        "output": "assets/card-leetgeek.svg"
    }
]

def fetch_repo_meta(username, repo):
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GH_PAT")
    url = f"https://api.github.com/repos/{username}/{repo}"
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data
    except Exception as e:
        print(f"Notice: Using default metadata for {repo} ({e})")
        return None

def wrap_text(text, max_chars=34):
    words = text.split()
    lines = []
    current = []
    current_len = 0
    for w in words:
        if current_len + len(w) + (1 if current else 0) <= max_chars:
            current.append(w)
            current_len += len(w) + (1 if len(current) > 1 else 0)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
            current_len = len(w)
    if current:
        lines.append(" ".join(current))
    return lines[:2] # Up to 2 lines

def create_card_svg(card_data):
    name = card_data["name"]
    desc = card_data["desc"]
    lang = card_data["lang"]
    stars = card_data.get("stars", 0)
    ill_b64 = card_data["illustration_b64"]

    # Calculate pill x based on name length
    # DM Serif Display approximate width per char at 22px is ~11px
    name_width = int(len(name) * 11.5)
    pill_x = 44 + name_width + 12

    desc_lines = wrap_text(desc, max_chars=34)
    line1 = desc_lines[0] if len(desc_lines) > 0 else ""
    line2 = desc_lines[1] if len(desc_lines) > 1 else ""

    # Star badge if stars > 0
    stars_svg = ""
    if stars > 0:
        star_x = 48 + int(len(lang) * 8.2) + 16
        stars_svg = f"""
    <!-- Star count -->
    <svg x="{star_x}" y="137" width="16" height="16" viewBox="0 0 16 16" fill="#111111">
      <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
    </svg>
    <text x="{star_x + 20}" y="150" class="card-meta">{stars}</text>
        """

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 560 180" width="560" height="180">
  <defs>
    <style>
      {FONT_STYLESHEET}
      .card-bg {{ fill: #F1EDE4; }}
      .card-border {{ stroke: #111111; stroke-width: 1.5; }}
      .card-title {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 21px;
        font-weight: 400;
        fill: #111111;
      }}
      .card-pill-border {{ stroke: #888888; stroke-width: 1; fill: none; }}
      .card-pill-text {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 400;
        fill: #444444;
      }}
      .card-desc {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        fill: #222222;
      }}
      .card-meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        font-weight: 700;
        fill: #111111;
      }}
    </style>
  </defs>

  <!-- Card container with rounded border -->
  <rect x="1" y="1" width="558" height="178" rx="8" ry="8" class="card-bg card-border" />

  <!-- Repo Icon -->
  <svg x="20" y="18" width="18" height="18" viewBox="0 0 16 16" fill="#111111">
    <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-.967a.25.25 0 0 0-.27 0l-1.45.967a.25.25 0 0 1-.4-.2Z"/>
  </svg>

  <!-- Title -->
  <text x="44" y="34" class="card-title">{name}</text>

  <!-- Public Pill -->
  <rect x="{pill_x}" y="19" width="52" height="19" rx="9.5" ry="9.5" class="card-pill-border" />
  <text x="{pill_x + 26}" y="33" class="card-pill-text" text-anchor="middle">Public</text>

  <!-- One-line / two-line monospace description -->
  <text x="22" y="66" class="card-desc">{line1}</text>
  <text x="22" y="84" class="card-desc">{line2}</text>

  <!-- Language dot and name -->
  <circle cx="27" cy="146" r="5" fill="#111111" />
  <text x="38" y="150" class="card-meta">{lang}</text>
{stars_svg}

  <!-- Dithered halftone illustration -->
  <image href="data:image/png;base64,{ill_b64}" x="340" y="24" width="202" height="132" preserveAspectRatio="xMidYMid meet" />
</svg>"""
    return svg

def generate_all_cards(username="786AdiPY"):
    os.makedirs("assets", exist_ok=True)
    for cfg in CARDS_CONFIG:
        meta = fetch_repo_meta(username, cfg["repo"])
        desc = cfg["default_desc"]
        lang = cfg["default_lang"]
        stars = 0
        
        if meta:
            # If description in GitHub is non-empty, we can use it or keep curated concise one
            api_desc = meta.get("description")
            if api_desc and len(api_desc.strip()) > 0:
                # If api desc is very long, prefer curated or clean it
                if len(api_desc) <= 90:
                    desc = api_desc
            if meta.get("language"):
                lang = meta["language"]
            stars = meta.get("stargazers_count", 0)

        card_data = {
            "name": cfg["name"],
            "desc": desc,
            "lang": lang,
            "stars": stars,
            "illustration_b64": cfg["illustration_b64"]
        }
        svg_content = create_card_svg(card_data)
        out_path = cfg["output"]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg_content.strip())
        print(f"Generated {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == "__main__":
    generate_all_cards()

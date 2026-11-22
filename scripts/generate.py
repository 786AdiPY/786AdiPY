"""
scripts/generate.py
Builds the complete retro newsprint & halftone SVG design system for @786AdiPY.
Generates 10 self-contained SVGs (5 light, 5 dark) at 830px width:
  - banner-light.svg, banner-dark.svg
  - featured-light.svg, featured-dark.svg
  - now-light.svg, now-dark.svg
  - stack-light.svg, stack-dark.svg
  - stats-light.svg, stats-dark.svg
Also generates assets/avatar-halftone.png (460x460).
"""
import io
import json
import os
import sys
import base64
import urllib.request
from datetime import datetime
from collections import defaultdict
from PIL import Image, ImageEnhance
import numpy as np
from fontTools.subset import Subsetter, Options
from fontTools.ttLib import TTFont

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(REPO_ROOT, "assets")
DATA_DIR = os.path.join(REPO_ROOT, "data")
FONTS_DIR = os.path.join(REPO_ROOT, "scripts", "fonts")

# Design System Colors
THEMES = {
    "light": {
        "bg": "#F1EDE4",
        "ink": "#111111",
        "grey": "#888888",
        "rule": "#111111",
        "pill_border": "#888888",
        "pill_text": "#444444",
        "muted": "#555555",
        "bar_bg": "#E5DFD4",
    },
    "dark": {
        "bg": "#0D1117",
        "ink": "#E8E4DA",
        "grey": "#7A7A7A",
        "rule": "#E8E4DA",
        "pill_border": "#7A7A7A",
        "pill_text": "#9E9A90",
        "muted": "#9E9A90",
        "bar_bg": "#161B22",
    }
}

def get_auth_token():
    return (
        os.environ.get("PROFILE_TOKEN")
        or os.environ.get("GITHUB_TOKEN")
        or os.environ.get("GH_TOKEN")
        or os.environ.get("GH_PAT")
    )

def fetch_json(url, token=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode("utf-8"))

def subset_font(font_path, text_corpus):
    """Subsets a TTF font using fonttools pyftsubset logic and returns base64 woff2."""
    options = Options()
    options.flavor = "woff2"
    subsetter = Subsetter(options=options)
    unicodes = {ord(c) for c in text_corpus} | {ord(" "), ord("\t"), ord("\n")}
    # Add common punctuation and math symbols
    unicodes |= {0x25A0, 0x25A1, 0x2605, 0x22C6, 0x2442, 0x25B8, 0x00B7, 0x2014, 0x2013, 0x2197, 0x2192}
    subsetter.populate(unicodes=unicodes)
    
    font = TTFont(font_path)
    subsetter.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")

def build_font_css(serif_b64, mono_b64):
    return f"""
@font-face {{
  font-family: 'DM Serif Display';
  font-style: normal;
  font-weight: 400;
  src: url('data:font/woff2;charset=utf-8;base64,{serif_b64}') format('woff2');
}}
@font-face {{
  font-family: 'IBM Plex Mono';
  font-style: normal;
  font-weight: 400;
  src: url('data:font/woff2;charset=utf-8;base64,{mono_b64}') format('woff2');
}}
@font-face {{
  font-family: 'IBM Plex Mono';
  font-style: normal;
  font-weight: 700;
  src: url('data:font/woff2;charset=utf-8;base64,{mono_b64}') format('woff2');
}}
"""

def xml_escape(text):
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )

def get_bayer_patterns(ink_color):
    """Returns 1-bit Bayer / stipple SVG pattern definitions for halftone bars."""
    return f"""
    <!-- 1-bit dither halftone patterns -->
    <pattern id="dither-100" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="4" fill="{ink_color}" />
    </pattern>
    <pattern id="dither-75" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="4" fill="none" />
      <rect x="0" y="0" width="2" height="2" fill="{ink_color}" />
      <rect x="2" y="0" width="1" height="2" fill="{ink_color}" />
      <rect x="2" y="2" width="2" height="2" fill="{ink_color}" />
      <rect x="0" y="2" width="1" height="2" fill="{ink_color}" />
    </pattern>
    <pattern id="dither-50" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="2" height="2" fill="{ink_color}" />
      <rect x="2" y="2" width="2" height="2" fill="{ink_color}" />
    </pattern>
    <pattern id="dither-25" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect x="0" y="0" width="2" height="2" fill="{ink_color}" />
    </pattern>
    <pattern id="dither-12" width="8" height="8" patternUnits="userSpaceOnUse">
      <rect x="0" y="0" width="2" height="2" fill="{ink_color}" />
      <rect x="4" y="4" width="2" height="2" fill="{ink_color}" />
    </pattern>
    """

# ----------------------------------------------------------------------
# 1. BANNER SVG (830 x 200)
# ----------------------------------------------------------------------
def generate_banner(theme_name, font_css, mountain_b64):
    c = THEMES[theme_name]
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 200" width="830" height="200">
  <defs>
    <style>
      {font_css}
      .bg {{ fill: {c["bg"]}; }}
      .ink {{ fill: {c["ink"]}; }}
      .rule {{ stroke: {c["rule"]}; }}
      .meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10.5px;
        font-weight: 700;
        letter-spacing: 2px;
        fill: {c["ink"]};
      }}
      .brand {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 76px;
        font-weight: 400;
        letter-spacing: 0.5px;
        fill: {c["ink"]};
      }}
    </style>
  </defs>

  <!-- Canvas background -->
  <rect width="830" height="200" class="bg" />

  <!-- Top Metadata -->
  <text x="24" y="26" class="meta">ENGINEERING / SYSTEMS / EXPERIMENTS</text>
  <text x="806" y="26" class="meta" text-anchor="end">EST. 2023</text>

  <!-- Top Rule -->
  <line x1="24" y1="34" x2="806" y2="34" class="rule" stroke-width="1" />

  <!-- Giant serif brand -->
  <text x="24" y="138" class="brand">786ADIPY</text>

  <!-- Dithered mountain range and sun illustration -->
  <image href="data:image/png;base64,{mountain_b64}" x="420" y="38" width="386" height="134" preserveAspectRatio="xMidYMid meet" />

  <!-- Bottom double rules (newspaper masthead standard) -->
  <line x1="24" y1="176" x2="806" y2="176" class="rule" stroke-width="1" />
  <line x1="24" y1="180" x2="806" y2="180" class="rule" stroke-width="0.5" />
</svg>"""
    return svg

# ----------------------------------------------------------------------
# 2. FEATURED CARD SVG (830 x 260)
# ----------------------------------------------------------------------
def generate_featured(theme_name, font_css, road_b64, stars=2, forks=1):
    c = THEMES[theme_name]
    
    # Calculate pill x
    # 'RangeShield-AI' in DM Serif Display 24px is ~175px
    pill_x = 48 + 180 + 12
    
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 260" width="830" height="260">
  <defs>
    <style>
      {font_css}
      .bg {{ fill: {c["bg"]}; }}
      .box {{ stroke: {c["rule"]}; stroke-width: 1; fill: {c["bg"]}; }}
      .title {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 24px;
        font-weight: 400;
        fill: {c["ink"]};
      }}
      .pill-border {{ stroke: {c["pill_border"]}; stroke-width: 1; fill: none; }}
      .pill-text {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10px;
        fill: {c["pill_text"]};
      }}
      .desc {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12.5px;
        fill: {c["ink"]};
      }}
      .meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        fill: {c["ink"]};
      }}
    </style>
  </defs>

  <rect width="830" height="260" class="bg" />

  <!-- Outer enclosed box -->
  <rect x="24" y="16" width="782" height="228" rx="6" ry="6" class="box" />

  <!-- Repo Icon -->
  <svg x="48" y="38" width="18" height="18" viewBox="0 0 16 16" fill="{c["ink"]}">
    <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-.967a.25.25 0 0 0-.27 0l-1.45.967a.25.25 0 0 1-.4-.2Z"/>
  </svg>

  <!-- Repo Name -->
  <text x="74" y="54" class="title">RangeShield-AI</text>

  <!-- Public Pill -->
  <rect x="{pill_x}" y="39" width="50" height="18" rx="9" ry="9" class="pill-border" />
  <text x="{pill_x + 25}" y="52" class="pill-text" text-anchor="middle">Public</text>

  <!-- 2-line mono description -->
  <text x="48" y="96" class="desc">EV range optimization using GenAI and Google Cloud.</text>
  <text x="48" y="118" class="desc">Real-time, flexible arrival predictions.</text>

  <!-- Language dot + name -->
  <circle cx="53" cy="164" r="4.5" fill="{c["ink"]}" />
  <text x="64" y="168" class="meta">TypeScript</text>

  <!-- Stars live -->
  <svg x="180" y="156" width="14" height="14" viewBox="0 0 16 16" fill="{c["ink"]}">
    <path d="M8 .25a.75.75 0 0 1 .673.418l1.882 3.815 4.21.612a.75.75 0 0 1 .416 1.279l-3.046 2.97.719 4.192a.75.75 0 0 1-1.088.791L8 12.347l-3.766 1.98a.75.75 0 0 1-1.088-.79l.72-4.194L.818 6.374a.75.75 0 0 1 .416-1.28l4.21-.611L7.327.668A.75.75 0 0 1 8 .25Z"/>
  </svg>
  <text x="200" y="168" class="meta">{stars}</text>

  <!-- Forks live -->
  <svg x="238" y="156" width="14" height="14" viewBox="0 0 16 16" fill="{c["ink"]}">
    <path d="M5 3.25a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm0 2.122a2.25 2.25 0 1 0-1.5 0v.878A2.25 2.25 0 0 0 5.75 8.5h4.5A2.25 2.25 0 0 0 12.5 6.25v-.878a2.25 2.25 0 1 0-1.5 0v.878a.75.75 0 0 1-.75.75h-4.5A.75.75 0 0 1 5 6.25v-.878ZM10.5 4a.75.75 0 1 1 0-1.5.75.75 0 0 1 0 1.5Zm-2.5 7a.75.75 0 1 1-1.5 0 .75.75 0 0 1 1.5 0Zm0 2.122a2.25 2.25 0 1 0-1.5 0v1.128a.75.75 0 0 0 1.5 0v-1.128Z"/>
  </svg>
  <text x="258" y="168" class="meta">{forks}</text>

  <!-- Dithered road illustration -->
  <image href="data:image/png;base64,{road_b64}" x="470" y="32" width="310" height="194" preserveAspectRatio="xMidYMid meet" />
</svg>"""
    return svg

# ----------------------------------------------------------------------
# 3. NOW SVG (830 x 140)
# ----------------------------------------------------------------------
def generate_now(theme_name, font_css, building_text, learning_text, reading_text):
    c = THEMES[theme_name]
    
    # Clean text lengths to fit in 830px width safely
    def truncate(text, max_len=62):
        return text if len(text) <= max_len else text[:max_len-3] + "..."

    b_text = xml_escape(truncate(building_text))
    l_text = xml_escape(truncate(learning_text))
    r_text = xml_escape(truncate(reading_text))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 140" width="830" height="140">
  <defs>
    <style>
      {font_css}
      .bg {{ fill: {c["bg"]}; }}
      .box {{ stroke: {c["rule"]}; stroke-width: 1; fill: {c["bg"]}; }}
      .lbl {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        fill: {c["grey"]};
      }}
      .val {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11.5px;
        fill: {c["ink"]};
      }}
    </style>
  </defs>

  <rect width="830" height="140" class="bg" />

  <!-- Outer enclosed box -->
  <rect x="24" y="12" width="782" height="116" rx="6" ry="6" class="box" />

  <!-- Line 1: BUILDING -->
  <text x="48" y="44" class="lbl">BUILDING  /</text>
  <text x="145" y="44" class="val">{b_text}</text>

  <!-- Line 2: LEARNING -->
  <text x="48" y="76" class="lbl">LEARNING  /</text>
  <text x="145" y="76" class="val">{l_text}</text>

  <!-- Line 3: READING -->
  <text x="48" y="108" class="lbl">READING   /</text>
  <text x="145" y="108" class="val">{r_text}</text>
</svg>"""
    return svg

# ----------------------------------------------------------------------
# 4. STACK SVG (830 x 100)
# ----------------------------------------------------------------------
def generate_stack(theme_name, font_css, tech_list):
    c = THEMES[theme_name]
    
    # Split into 2 balanced lines separated by slashes
    mid = len(tech_list) // 2 + 1
    line1 = xml_escape("  /  ".join([t.upper() for t in tech_list[:mid]]))
    line2 = xml_escape("  /  ".join([t.upper() for t in tech_list[mid:]]))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 100" width="830" height="100">
  <defs>
    <style>
      {font_css}
      .bg {{ fill: {c["bg"]}; }}
      .box {{ stroke: {c["rule"]}; stroke-width: 1; fill: {c["bg"]}; }}
      .stack-line {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
        fill: {c["ink"]};
      }}
    </style>
  </defs>

  <rect width="830" height="100" class="bg" />

  <!-- Outer enclosed box -->
  <rect x="24" y="10" width="782" height="80" rx="6" ry="6" class="box" />

  <!-- Tech strip lines centered -->
  <text x="415" y="42" class="stack-line" text-anchor="middle">{line1}</text>
  <text x="415" y="66" class="stack-line" text-anchor="middle">{line2}</text>
</svg>"""
    return svg

# ----------------------------------------------------------------------
# 5. STATS SVG (830 x 220)
# ----------------------------------------------------------------------
def generate_stats(theme_name, font_css, top_langs, total_contribs, streak_days):
    c = THEMES[theme_name]
    bayer_patterns = get_bayer_patterns(c["ink"])

    # Build Top 5 language rows
    pattern_names = ["dither-100", "dither-75", "dither-50", "dither-25", "dither-12"]
    bar_svg = []
    y_start = 66
    for i, (lang, pct) in enumerate(top_langs[:5]):
        y = y_start + i * 28
        # max bar width = 190px (from x=150 to x=340)
        bw = max(int(pct * 1.9), 4)
        pat = pattern_names[i % len(pattern_names)]
        bar_svg.append(f"""
    <!-- Row {i+1}: {lang} -->
    <text x="48" y="{y + 8}" class="stat-lbl">{lang}</text>
    <rect x="150" y="{y}" width="190" height="10" rx="2" ry="2" class="bar-bg" />
    <rect x="150" y="{y}" width="{bw}" height="10" rx="2" ry="2" fill="url(#{pat})" stroke="{c["ink"]}" stroke-width="0.8" />
    <text x="350" y="{y + 8}" class="stat-meta">{pct:.1f}%</text>
        """)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 830 220" width="830" height="220">
  <defs>
    <style>
      {font_css}
      .bg {{ fill: {c["bg"]}; }}
      .box {{ stroke: {c["rule"]}; stroke-width: 1; fill: {c["bg"]}; }}
      .rule {{ stroke: {c["grey"]}; stroke-width: 0.8; }}
      .title {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.5px;
        fill: {c["grey"]};
      }}
      .stat-lbl {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11.5px;
        font-weight: 700;
        fill: {c["ink"]};
      }}
      .stat-meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 10.5px;
        fill: {c["muted"]};
      }}
      .bar-bg {{
        fill: {c["bar_bg"]};
        stroke: {c["grey"]};
        stroke-width: 0.6;
      }}
      .num {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 44px;
        font-weight: 400;
        fill: {c["ink"]};
      }}
      .num-streak {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 36px;
        font-weight: 400;
        fill: {c["ink"]};
      }}
    </style>
    {bayer_patterns}
  </defs>

  <rect width="830" height="220" class="bg" />

  <!-- Outer enclosed box -->
  <rect x="24" y="12" width="782" height="196" rx="6" ry="6" class="box" />

  <!-- Column 1: Top Languages -->
  <text x="48" y="38" class="title">TOP LANGUAGES (BY BYTES)</text>
  {"".join(bar_svg)}

  <!-- Vertical Dividing Rule -->
  <line x1="430" y1="22" x2="430" y2="198" class="rule" />

  <!-- Column 2: Annual Activity & Streak -->
  <text x="460" y="38" class="title">ANNUAL ACTIVITY &amp; STREAK</text>

  <!-- Metric 1: Total Contributions -->
  <text x="460" y="94" class="num">{total_contribs}</text>
  <text x="460" y="114" class="stat-meta" letter-spacing="1.5">CONTRIBUTIONS IN THE LAST YEAR</text>

  <!-- Metric 2: Current Streak -->
  <text x="460" y="166" class="num-streak">{streak_days} DAYS</text>
  <text x="460" y="186" class="stat-meta" letter-spacing="1.5">CURRENT CONTRIBUTION STREAK</text>
</svg>"""
    return svg

# ----------------------------------------------------------------------
# 6. DITHERED AVATAR (460 x 460)
# ----------------------------------------------------------------------
def generate_avatar(username="786AdiPY", output_path="assets/avatar-halftone.png"):
    avatar_url = f"https://github.com/{username}.png"
    img = None
    try:
        req = urllib.request.Request(avatar_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            img = Image.open(io.BytesIO(data))
    except Exception as e:
        print(f"Notice: Fetching avatar online failed ({e}), checking existing avatar...")
        if os.path.exists(output_path):
            img = Image.open(output_path)
        else:
            img = Image.new("RGB", (460, 460), (200, 200, 200))

    gray = img.convert("L").resize((460, 460), Image.Resampling.LANCZOS)
    enhanced = ImageEnhance.Contrast(gray).enhance(1.6)
    enhanced = ImageEnhance.Sharpness(enhanced).enhance(1.8)
    dithered = enhanced.convert("1", dither=Image.Dither.FLOYDSTEINBERG)

    arr = np.array(dithered)
    h, w = arr.shape
    newsprint = np.zeros((h, w, 3), dtype=np.uint8)
    newsprint[arr == False] = [0x11, 0x11, 0x11]
    newsprint[arr == True] = [0xF1, 0xED, 0xE4]

    out_img = Image.fromarray(newsprint, "RGB")
    out_img.save(output_path, "PNG", optimize=True)
    print(f"Generated {output_path} ({os.path.getsize(output_path)} bytes)")

# ----------------------------------------------------------------------
# MASTER GENERATE PIPELINE
# ----------------------------------------------------------------------
def main():
    username = "786AdiPY"
    token = get_auth_token()
    print(f"=== Starting Retro Newsprint Generation for @{username} ===")
    print(f"Token available: {'Yes' if token else 'No (using public endpoints)'}")

    os.makedirs(ASSETS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    # 1. Load Data Files
    now_path = os.path.join(DATA_DIR, "now.json")
    if not os.path.exists(now_path):
        with open(now_path, "w", encoding="utf-8") as f:
            json.dump({
                "learning": "Distributed Systems & LLM Agent Architectures",
                "reading": "Designing Data-Intensive Applications (Martin Kleppmann)"
            }, f, indent=2)

    with open(now_path, "r", encoding="utf-8") as f:
        now_data = json.load(f)

    stack_path = os.path.join(DATA_DIR, "stack.json")
    if not os.path.exists(stack_path):
        with open(stack_path, "w", encoding="utf-8") as f:
            json.dump({
                "technologies": [
                    "TYPESCRIPT", "PYTHON", "REACT", "NEXT.JS", "NODE.JS", "FASTAPI",
                    "DOCKER", "POSTGRESQL", "GRAPHQL", "GOOGLE CLOUD", "GIT"
                ]
            }, f, indent=2)

    with open(stack_path, "r", encoding="utf-8") as f:
        stack_data = json.load(f)

    # 2. Fetch Live Repo Data (RangeShield-AI & Most Recently Pushed)
    rs_stars = 2
    rs_forks = 1
    building_text = "RangeShield-AI — EV range co-pilot with GenAI & Google Cloud"
    try:
        repos_url = f"https://api.github.com/users/{username}/repos?sort=pushed&direction=desc&per_page=100"
        repos = fetch_json(repos_url, token)
        non_forks = [r for r in repos if not r.get("fork") and r["name"] != username]
        if non_forks:
            top_r = non_forks[0]
            desc = top_r.get("description") or "Active development and experiments"
            building_text = f"{top_r['name']} — {desc}"

        rs_meta = fetch_json(f"https://api.github.com/repos/{username}/RangeShield-AI", token)
        rs_stars = rs_meta.get("stargazers_count", 2)
        rs_forks = rs_meta.get("forks_count", 1)
        print(f"RangeShield-AI live stats: ★ {rs_stars}  ⑂ {rs_forks}")
        print(f"Building text: {building_text}")
    except Exception as e:
        print(f"Notice: Live repo fetch fallback ({e})")

    # 3. Aggregate Language Bytes
    top_languages = [("TypeScript", 43.3), ("Python", 29.3), ("CSS", 11.8), ("JavaScript", 10.9), ("Java", 2.5)]
    try:
        lang_bytes = defaultdict(int)
        for r in non_forks[:12]: # Check top 12 non-fork repos
            url = f"https://api.github.com/repos/{username}/{r['name']}/languages"
            ldata = fetch_json(url, token)
            for lang, b in ldata.items():
                lang_bytes[lang] += b
        total_b = sum(lang_bytes.values())
        if total_b > 0:
            sorted_l = sorted(lang_bytes.items(), key=lambda x: x[1], reverse=True)[:5]
            top_languages = [(l, (b / total_b) * 100) for l, b in sorted_l]
            print(f"Live top languages: {top_languages}")
    except Exception as e:
        print(f"Notice: Language bytes calculation fallback ({e})")

    # 4. Fetch Contributions and Streak
    total_contribs = 792
    streak_days = 31
    try:
        c_url = f"https://github-contributions-api.jogruber.de/v4/{username}"
        c_data = fetch_json(c_url)
        today_str = datetime.now().strftime("%Y-%m-%d")
        all_days = [d for d in c_data.get("contributions", []) if d["date"] <= today_str]
        all_days = sorted(all_days, key=lambda x: x["date"])
        
        last_365 = all_days[-365:]
        total_contribs = sum(d["count"] for d in last_365)
        
        # Streak calculation
        st = 0
        for i, d in enumerate(reversed(all_days)):
            if d["count"] > 0:
                st += 1
            else:
                if i == 0: # Today grace
                    continue
                break
        streak_days = st
        print(f"Live contributions: {total_contribs}, Streak: {streak_days} days")
    except Exception as e:
        print(f"Notice: Contributions fetch fallback ({e})")

    # 5. Font Subsetting
    print("\nSubsetting DM Serif Display and IBM Plex Mono fonts...")
    serif_ttf = os.path.join(FONTS_DIR, "DMSerifDisplay-Regular.ttf")
    mono_ttf = os.path.join(FONTS_DIR, "IBMPlexMono-Regular.ttf")

    # Gather all glyphs used across the design system
    corpus = (
        "786ADIPY ENGINEERING SYSTEMS EXPERIMENTS EST. 2023 "
        "RangeShield-AI Public EV range optimization using GenAI and Google Cloud. "
        "Real-time, flexible arrival predictions. TypeScript JavaScript Python CSS Java HTML Shell "
        "BUILDING LEARNING READING " + building_text + now_data.get("learning", "") + now_data.get("reading", "") +
        " ".join(stack_data.get("technologies", [])) +
        " TOP LANGUAGES (BY BYTES) ANNUAL ACTIVITY & STREAK CONTRIBUTIONS IN THE LAST YEAR "
        "CURRENT CONTRIBUTION STREAK 0123456789% DAYS / . - — : ( ) ★ ⑂ "
    )

    serif_b64 = subset_font(serif_ttf, corpus)
    mono_b64 = subset_font(mono_ttf, corpus)
    font_css = build_font_css(serif_b64, mono_b64)
    print(f"Subset complete! Serif: {len(serif_b64)} chars, Mono: {len(mono_b64)} chars")

    # 6. Load Base64 Illustrations
    with open(os.path.join(ASSETS_DIR, "illustrations", "mountain_light.png"), "rb") as f:
        mountain_light_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(os.path.join(ASSETS_DIR, "illustrations", "mountain_dark.png"), "rb") as f:
        mountain_dark_b64 = base64.b64encode(f.read()).decode("ascii")

    with open(os.path.join(ASSETS_DIR, "illustrations", "road_light.png"), "rb") as f:
        road_light_b64 = base64.b64encode(f.read()).decode("ascii")
    with open(os.path.join(ASSETS_DIR, "illustrations", "road_dark.png"), "rb") as f:
        road_dark_b64 = base64.b64encode(f.read()).decode("ascii")

    # 7. Generate all 10 SVGs
    assets_to_build = [
        ("banner-light.svg", generate_banner("light", font_css, mountain_light_b64)),
        ("banner-dark.svg", generate_banner("dark", font_css, mountain_dark_b64)),
        ("featured-light.svg", generate_featured("light", font_css, road_light_b64, rs_stars, rs_forks)),
        ("featured-dark.svg", generate_featured("dark", font_css, road_dark_b64, rs_stars, rs_forks)),
        ("now-light.svg", generate_now("light", font_css, building_text, now_data["learning"], now_data["reading"])),
        ("now-dark.svg", generate_now("dark", font_css, building_text, now_data["learning"], now_data["reading"])),
        ("stack-light.svg", generate_stack("light", font_css, stack_data["technologies"])),
        ("stack-dark.svg", generate_stack("dark", font_css, stack_data["technologies"])),
        ("stats-light.svg", generate_stats("light", font_css, top_languages, total_contribs, streak_days)),
        ("stats-dark.svg", generate_stats("dark", font_css, top_languages, total_contribs, streak_days)),
    ]

    print("\nWriting SVGs to assets/...")
    for filename, content in assets_to_build:
        out_p = os.path.join(ASSETS_DIR, filename)
        with open(out_p, "w", encoding="utf-8") as f:
            f.write(content.strip())
        size_kb = os.path.getsize(out_p) / 1024
        print(f"  ✓ {filename} ({size_kb:.1f} KB) [<200KB check: {'PASS' if size_kb < 200 else 'FAIL'}]")

    # 8. Halftone Avatar
    print("\nGenerating 460x460 Halftone Avatar...")
    generate_avatar(username, os.path.join(ASSETS_DIR, "avatar-halftone.png"))

    print("\n=== Generation Complete! ===")

if __name__ == "__main__":
    main()

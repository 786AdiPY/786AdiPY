"""
generate_contributions.py
Generates the retro newsprint contribution calendar SVG.
Pulls real contribution data via GitHub GraphQL API (with public API / HTML fallback).
Renders a 4-level greyscale / halftone grid matching the newsprint design language.
"""
import os
import sys
import json
import urllib.request
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(__file__))
from fonts_data import FONT_STYLESHEET

# Greyscale / newsprint 4-level ink palette
PALETTE = {
    0: {"fill": "#F1EDE4", "stroke": "#D5CFC3"}, # Paper background (no contribs)
    1: {"fill": "#C4BEB2", "stroke": "#B2ACA0"}, # Light grey / stipple
    2: {"fill": "#888277", "stroke": "#767066"}, # Mid grey
    3: {"fill": "#45413D", "stroke": "#33302C"}, # Dark ink grey
    4: {"fill": "#111111", "stroke": "#111111"}  # Full black ink
}

def fetch_via_graphql(username, token):
    url = "https://api.github.com/graphql"
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
                weekday
              }
            }
            months {
              name
              firstDay
              totalWeeks
            }
          }
        }
      }
    }
    """
    data = json.dumps({"query": query, "variables": {"login": username}}).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "User-Agent": "Mozilla/5.0",
            "Content-Type": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=12) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        cal = res["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        return cal

def fetch_via_fallback(username):
    url = f"https://github-contributions-api.jogruber.de/v4/{username}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        res = json.loads(resp.read().decode("utf-8"))
    
    # Sort contributions by date ascending
    contributions = sorted(res.get("contributions", []), key=lambda x: x["date"])
    if not contributions:
        return None
        
    # Build weeks structure: 53 weeks (371 days ending at last contribution date)
    # Align to Saturday end
    last_date = datetime.strptime(contributions[-1]["date"], "%Y-%m-%d")
    # GitHub weeks run Sunday (0) to Saturday (6)
    days_to_sat = (5 - last_date.weekday()) % 7
    end_date = last_date + timedelta(days=days_to_sat)
    start_date = end_date - timedelta(days=53 * 7 - 1)

    contrib_map = {c["date"]: c["count"] for c in contributions}
    
    weeks = []
    current_date = start_date
    total_in_range = 0
    
    for w in range(53):
        days = []
        for d in range(7):
            d_str = current_date.strftime("%Y-%m-%d")
            cnt = contrib_map.get(d_str, 0)
            total_in_range += cnt
            days.append({
                "date": d_str,
                "contributionCount": cnt,
                "weekday": (current_date.weekday() + 1) % 7 # 0 is Sunday
            })
            current_date += timedelta(days=1)
        weeks.append({"contributionDays": days})

    # Build months list
    months = []
    curr_month = ""
    for idx, w in enumerate(weeks):
        first_day_date = datetime.strptime(w["contributionDays"][0]["date"], "%Y-%m-%d")
        m_name = first_day_date.strftime("%b")
        if m_name != curr_month:
            curr_month = m_name
            months.append({"name": m_name, "col": idx})

    return {
        "totalContributions": total_in_range,
        "weeks": weeks,
        "months": months
    }

def get_level(count):
    if count <= 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 5:
        return 2
    elif count <= 8:
        return 3
    else:
        return 4

def generate_contributions(username="786AdiPY", output_path="assets/contributions.svg"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GH_PAT")
    cal_data = None

    if token:
        try:
            print("Querying GitHub GraphQL API for contribution calendar...")
            raw_cal = fetch_via_graphql(username, token)
            # Adapt raw_cal format
            weeks = raw_cal.get("weeks", [])
            months = []
            curr_m = ""
            for idx, w in enumerate(weeks):
                days = w.get("contributionDays", [])
                if days:
                    d_dt = datetime.strptime(days[0]["date"], "%Y-%m-%d")
                    m_name = d_dt.strftime("%b")
                    if m_name != curr_m:
                        curr_m = m_name
                        months.append({"name": m_name, "col": idx})
            cal_data = {
                "totalContributions": raw_cal.get("totalContributions", 0),
                "weeks": weeks,
                "months": months
            }
            print("Successfully fetched via GraphQL.")
        except Exception as e:
            print(f"GraphQL request failed ({e}), falling back to public contributions data...")
    
    if not cal_data:
        try:
            cal_data = fetch_via_fallback(username)
            print("Successfully fetched contributions via public API fallback.")
        except Exception as e:
            print(f"Fallback fetch failed ({e}), using default mock contributions...")
            # Create a 53-week structure with realistic mock data
            weeks = []
            for w in range(53):
                days = [{"date": "2026-01-01", "contributionCount": (w % 4), "weekday": d} for d in range(7)]
                weeks.append({"contributionDays": days})
            months = [{"name": m, "col": i * 4} for i, m in enumerate(["Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov"])]
            cal_data = {"totalContributions": 874, "weeks": weeks, "months": months}

    total = cal_data["totalContributions"]
    weeks = cal_data["weeks"]
    months = cal_data["months"]

    # Calculate layout
    # 53 columns, cell 11x11, gap 3.5 => step 14.5
    # Total grid width: 53 * 14.5 = 768.5
    grid_x0 = 64
    grid_y0 = 66
    cell_size = 11
    step = 14.5

    cells_svg = []
    for col_idx, w in enumerate(weeks[-53:]): # Ensure 53 weeks
        days = w.get("contributionDays", [])
        for day in days:
            # day['weekday']: 0=Sun, 1=Mon, ..., 6=Sat
            row_idx = day.get("weekday", 0)
            cnt = day.get("contributionCount", 0)
            lvl = get_level(cnt)
            style = PALETTE[lvl]
            cx = grid_x0 + col_idx * step
            cy = grid_y0 + row_idx * step
            d_str = day.get("date", "")
            title_text = f"{cnt} contributions on {d_str}" if cnt > 0 else f"No contributions on {d_str}"
            
            cells_svg.append(
                f'<rect x="{cx:.1f}" y="{cy:.1f}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" '
                f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="0.8">'
                f'<title>{title_text}</title></rect>'
            )

    # Month labels
    month_svg = []
    # Avoid overlapping months by keeping minimal gap
    last_col = -5
    for m in months:
        col = m.get("col", 0)
        # Adjust if weeks list is longer
        if len(weeks) > 53:
            col = col - (len(weeks) - 53)
        if 0 <= col <= 51 and (col - last_col) >= 3:
            mx = grid_x0 + col * step
            month_svg.append(f'<text x="{mx:.1f}" y="{grid_y0 - 8}" class="cal-label">{m["name"]}</text>')
            last_col = col

    # Day labels (Mon, Wed, Fri)
    day_labels_svg = [
        f'<text x="{grid_x0 - 12}" y="{grid_y0 + 1 * step + 9:.1f}" class="cal-label" text-anchor="end">Mon</text>',
        f'<text x="{grid_x0 - 12}" y="{grid_y0 + 3 * step + 9:.1f}" class="cal-label" text-anchor="end">Wed</text>',
        f'<text x="{grid_x0 - 12}" y="{grid_y0 + 5 * step + 9:.1f}" class="cal-label" text-anchor="end">Fri</text>'
    ]

    # Legend at bottom right
    legend_x = grid_x0 + 53 * step - 130
    legend_y = grid_y0 + 7 * step + 22
    legend_cells = []
    for l in range(5):
        lx = legend_x + 36 + l * 15
        ly = legend_y - 9
        st = PALETTE[l]
        legend_cells.append(
            f'<rect x="{lx}" y="{ly}" width="{cell_size}" height="{cell_size}" rx="2" ry="2" fill="{st["fill"]}" stroke="{st["stroke"]}" stroke-width="0.8" />'
        )

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 980 230" width="980" height="230">
  <defs>
    <style>
      {FONT_STYLESHEET}
      .cal-bg {{ fill: #F1EDE4; }}
      .cal-border {{ stroke: #111111; stroke-width: 1.5; }}
      .cal-title {{
        font-family: 'DM Serif Display', Georgia, serif;
        font-size: 19px;
        font-weight: 400;
        letter-spacing: 0.5px;
        fill: #111111;
      }}
      .cal-label {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11px;
        fill: #555555;
      }}
      .cal-meta {{
        font-family: 'IBM Plex Mono', monospace;
        font-size: 11.5px;
        fill: #444444;
      }}
      .year-active-bg {{ fill: #111111; }}
      .year-active-text {{ fill: #F1EDE4; font-family: 'IBM Plex Mono', monospace; font-size: 11px; font-weight: 700; }}
      .year-link {{ fill: #555555; font-family: 'IBM Plex Mono', monospace; font-size: 11px; }}
    </style>
  </defs>

  <!-- Container Box -->
  <rect x="1" y="1" width="978" height="228" rx="8" ry="8" class="cal-bg cal-border" />

  <!-- Section Title -->
  <rect x="24" y="24" width="8" height="8" fill="#111111" />
  <text x="38" y="33" class="cal-title">{total} contributions in the last year</text>

  <!-- Right-side settings / years -->
  <text x="730" y="32" class="cal-meta">Contribution settings &#9662;</text>
  <rect x="890" y="20" width="48" height="18" rx="3" ry="3" class="year-active-bg" />
  <text x="914" y="33" class="year-active-text" text-anchor="middle">2026</text>

  <!-- Month labels -->
  {"".join(month_svg)}

  <!-- Day labels (Mon, Wed, Fri) -->
  {"".join(day_labels_svg)}

  <!-- Contribution cells (53x7) -->
  {"".join(cells_svg)}

  <!-- Footer link / Learn how we count -->
  <text x="{grid_x0}" y="{legend_y}" class="cal-meta" font-style="italic">Learn how we count contributions.</text>

  <!-- Legend (Less -> More) -->
  <text x="{legend_x}" y="{legend_y}" class="cal-label">Less</text>
  {"".join(legend_cells)}
  <text x="{legend_x + 118}" y="{legend_y}" class="cal-label">More</text>
</svg>"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg.strip())
    print(f"Generated {output_path} ({os.path.getsize(output_path)} bytes)")

if __name__ == "__main__":
    generate_contributions()

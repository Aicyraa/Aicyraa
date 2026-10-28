import os
import json
import base64

def get_font_base64(font_filename):
    font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", font_filename)
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def generate_stats_svg(data):
    bold_b64 = get_font_base64("JBM-Bold.subset.woff2")
    medium_b64 = get_font_base64("JBM-Medium.subset.woff2")
    
    font_style = f"""
        @font-face {{
          font-family: 'JBM Bold';
          src: url(data:font/woff2;base64,{bold_b64}) format('woff2');
          font-weight: 700;
          font-style: normal;
        }}
        @font-face {{
          font-family: 'JBM Medium';
          src: url(data:font/woff2;base64,{medium_b64}) format('woff2');
          font-weight: 500;
          font-style: normal;
        }}
        text {{ font-family: 'JBM Medium', ui-monospace, monospace; }}
        .b {{ font-family: 'JBM Bold', ui-monospace, monospace; }}
    """

    total_contribs = data.get("total_contributions", 0)
    active_days = data.get("active_days", 0)
    best_week = data.get("best_week", 0)
    total_commits = data.get("total_commits") if data.get("total_commits") is not None else "—"
    total_prs = data.get("total_prs") if data.get("total_prs") is not None else "—"
    repos_contributed = data.get("public_repos", 0)
    
    weekly = data.get("weekly_contributions", [0] * 52)
    if not weekly or len(weekly) == 0:
        weekly = [0] * 52
        
    max_val = max(weekly) if max(weekly) > 0 else 1
    
    # Redesigned Dimensions & Spacing
    chart_width = 580
    chart_height = 100
    start_x = 20
    
    num_points = len(weekly)
    dx = chart_width / max((num_points - 1), 1)
    
    # Calculate chart points
    points = []
    for i, val in enumerate(weekly):
        x = round(start_x + i * dx, 1)
        y = round(chart_height - (val / max_val * chart_height), 1)
        points.append((x, y, val))
        
    # Build smooth cubic Bezier line path
    def get_control_point(p_prev, p_curr, p_next, p_nextnext, tension=0.2):
        d1 = ((p_next[0] - p_prev[0]) * tension, (p_next[1] - p_prev[1]) * tension)
        d2 = ((p_nextnext[0] - p_curr[0]) * tension, (p_nextnext[1] - p_curr[1]) * tension)
        
        cp1_x = p_curr[0] + d1[0]
        cp1_y = p_curr[1] + d1[1]
        
        cp2_x = p_next[0] - d2[0]
        cp2_y = p_next[1] - d2[1]
        
        # Clamp Y coordinates to prevent overshooting local min/max (monotone behavior)
        min_y = min(p_curr[1], p_next[1])
        max_y = max(p_curr[1], p_next[1])
        
        cp1_y = max(min_y, min(max_y, cp1_y))
        cp2_y = max(min_y, min(max_y, cp2_y))
        
        return (
            (round(cp1_x, 1), round(cp1_y, 1)),
            (round(cp2_x, 1), round(cp2_y, 1))
        )

    path_cmds = [f"M {points[0][0]} {points[0][1]}"]
    for i in range(len(points) - 1):
        p0 = points[max(i - 1, 0)]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[min(i + 2, len(points) - 1)]
        
        cp1, cp2 = get_control_point(p0, p1, p2, p3)
        path_cmds.append(f"C {cp1[0]} {cp1[1]}, {cp2[0]} {cp2[1]}, {p2[0]} {p2[1]}")
        
    line_path = " ".join(path_cmds)
    area_path = f"{line_path} L {start_x + chart_width} {chart_height} L {start_x} {chart_height} Z"
    
    # Peak dots (find top 2 peak points)
    sorted_points = sorted(enumerate(points), key=lambda item: item[1][2], reverse=True)
    peak_dots_svg = ""
    seen_x = set()
    peaks_added = 0
    
    for idx, (x, y, val) in sorted_points:
        if val > 0 and peaks_added < 2:
            too_close = any(abs(x - prev_x) < 50 for prev_x in seen_x)
            if not too_close:
                seen_x.add(x)
                peaks_added += 1
                peak_dots_svg += f'''
      <circle cx="{x}" cy="{y}" r="3.5" fill="#1A1C23" stroke="#B7A9DE" stroke-width="1.5" opacity="0.9"/>
      <text x="{x}" y="{y - 8}" text-anchor="middle" font-size="9" fill="#B7A9DE" class="b">{val}</text>'''

    # Month labels
    months = data.get("month_labels", [])
    if not months:
        m_names = ["Aug", "Sep", "Oct", "Nov", "Dec", "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
        months = [{"index": int(i * 4.33), "month": m_names[i]} for i in range(12)]
        
    month_texts_svg = ""
    previous_label_x = -100
    for m in months:
        idx = m.get("index", 0)
        x_pos = round(start_x + idx * dx, 1)
        if x_pos < start_x + chart_width - 15 and x_pos - previous_label_x >= 30:
            previous_label_x = x_pos
            month_texts_svg += f'\n      <text x="{x_pos}" y="120" text-anchor="middle" font-size="9" fill="#555">{m["month"]}</text>'

    svg_content = f'''<svg width="620" height="260" viewBox="0 0 620 260" xmlns="http://www.w3.org/2000/svg">
<defs>
<style>
{font_style}
</style>
<linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0%" stop-color="#B7A9DE" stop-opacity="0.35"/>
  <stop offset="100%" stop-color="#B7A9DE" stop-opacity="0.0"/>
</linearGradient>
</defs>

  <!-- Header Layout -->
  <!-- Left Side: Total Contributions -->
  <g transform="translate(20, 10)">
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.6s" fill="freeze" />
      <text x="0" y="45" class="b" font-size="44" fill="#E7E3DC" letter-spacing="-0.5">{total_contribs}</text>
      <text x="2" y="65" font-size="11" fill="#8B877E" letter-spacing="0.2">contributions in the last year</text>
    </g>
  </g>

  <!-- Right Side: Secondary Metrics as Dashboard Cards -->
  <g opacity="0" transform="translate(0, 10)"><animate attributeName="opacity" from="0" to="1" begin="0.15s" dur="0.6s" fill="freeze" />
    <g transform="translate(420, 30)">
      <text x="35" y="0" text-anchor="middle" class="b" font-size="24" fill="#B7A9DE">{active_days}</text>
      <text x="35" y="16" text-anchor="middle" font-size="9" fill="#8B877E" text-transform="uppercase" letter-spacing="1">Active Days</text>
    </g>
    
    <g transform="translate(520, 30)">
      <text x="35" y="0" text-anchor="middle" class="b" font-size="24" fill="#78A6C2">{best_week}</text>
      <text x="35" y="16" text-anchor="middle" font-size="9" fill="#8B877E" text-transform="uppercase" letter-spacing="1">Best Week</text>
    </g>
  </g>

  <!-- Chart area -->
  <g transform="translate(0, 100)">
    <!-- Horizontal grid lines -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="0.3" begin="0.2s" dur="0.5s" fill="freeze" />
      <line x1="{start_x}" y1="0" x2="{start_x + chart_width}" y2="0" stroke="#2A2D33" stroke-width="0.5" stroke-dasharray="2 4"/>
      <line x1="{start_x}" y1="{chart_height / 2}" x2="{start_x + chart_width}" y2="{chart_height / 2}" stroke="#2A2D33" stroke-width="0.5" stroke-dasharray="2 4"/>
      <line x1="{start_x}" y1="{chart_height}" x2="{start_x + chart_width}" y2="{chart_height}" stroke="#2A2D33" stroke-width="1"/>
    </g>

    <!-- Area fill under line -->
    <path d="{area_path}" fill="url(#areaFill)" opacity="0">
      <animate attributeName="opacity" from="0" to="1" begin="0.6s" dur="0.8s" fill="freeze"/>
    </path>

    <!-- Main line -->
    <path d="{line_path}" fill="none" stroke="#B7A9DE" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round" stroke-dasharray="1000" stroke-dashoffset="1000">
      <animate attributeName="stroke-dashoffset" from="1000" to="0" begin="0.3s" dur="1.6s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </path>

    <!-- Peak dots -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="1.2s" dur="0.4s" fill="freeze" />{peak_dots_svg}
    </g>

    <!-- Month labels -->
    <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.5s" dur="0.5s" fill="freeze" />{month_texts_svg}
    </g>
  </g>

  <!-- Footer Layout -->
  <g transform="translate(310, 245)" opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.7s" dur="0.5s" fill="freeze" />
    <text text-anchor="middle" font-size="10" letter-spacing="0.5">
      <tspan class="b" fill="#8FBF9F">{repos_contributed}</tspan> <tspan fill="#8B877E">PUBLIC REPOSITORIES</tspan>
    </text>
  </g>
</svg>
'''
    return svg_content

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        svg = generate_stats_svg(data)
        output_svg_path = os.path.join(os.path.dirname(__file__), "..", "stats.svg")
        with open(output_svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("Generated stats.svg successfully!")

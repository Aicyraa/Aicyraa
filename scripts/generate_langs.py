import os
import json
import base64

def get_font_base64(font_filename):
    font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", font_filename)
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def generate_langs_svg(data):
    medium_b64 = get_font_base64("JBM-Medium.subset.woff2")
    
    font_style = f"""
        @font-face {{
          font-family: 'JBM Medium';
          src: url(data:font/woff2;base64,{medium_b64}) format('woff2');
          font-weight: 500;
          font-style: normal;
        }}
text {{ font-family: 'JBM Medium', ui-monospace, monospace; }}
.b {{ font-family: 'JBM Bold', ui-monospace, monospace; }}
"""

    languages = data.get("languages", [])
    if not languages:
        # Return a minimal SVG with an empty-state message instead of fake data
        return f'''<svg width="620" height="170" viewBox="0 0 620 170" xmlns="http://www.w3.org/2000/svg">
<defs>
<style>
{font_style}
</style>
</defs>
  <text x="310" y="85" text-anchor="middle" font-size="12" fill="#8B877E">Waiting for language data…</text>
</svg>
'''
        
    rows_svg = []
    max_bar_width = 464
    
    for i, lang in enumerate(languages[:6]):
        name = lang.get("name", "")
        pct = lang.get("pct", 0.0)
        color = lang.get("color", "#B7A9DE")
        
        y_text = 14 + (i * 20)
        y_rect = 5 + (i * 20)
        width_val = round((pct / 100.0) * max_bar_width, 1)
        begin_g = round(0.05 + (i * 0.06), 2)
        begin_anim = round(0.15 + (i * 0.06), 2)
        
        row = f'''  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="{begin_g}s" dur="0.45s" fill="freeze" />
    <text x="0" y="{y_text}" font-size="11" fill="#8B877E">{name}</text>
    <rect x="96" y="{y_rect}" width="464" height="7" rx="3.5" fill="#2A2D33"/>
    <rect x="96" y="{y_rect}" height="7" rx="3.5" fill="{color}" width="0">
      <animate attributeName="width" from="0" to="{width_val}" begin="{begin_anim}s" dur="0.7s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/>
    </rect>
    <text x="620" y="{y_text}" text-anchor="end" font-size="11" fill="#8B877E">{pct:.2f}%</text>
  </g>'''
        rows_svg.append(row)

    height = 20 + len(languages[:6]) * 25
    if height < 170:
        height = 170

    svg_content = f'''<svg width="620" height="{height}" viewBox="0 0 620 {height}" xmlns="http://www.w3.org/2000/svg">
<defs>
<style>
{font_style}
</style>
</defs>

{chr(10).join(rows_svg)}
</svg>
'''
    return svg_content

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        svg = generate_langs_svg(data)
        output_svg_path = os.path.join(os.path.dirname(__file__), "..", "langs.svg")
        with open(output_svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("Generated langs.svg successfully!")

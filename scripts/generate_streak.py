import os
import json
import base64

def get_font_base64(font_filename):
    font_path = os.path.join(os.path.dirname(__file__), "..", "fonts", font_filename)
    if os.path.exists(font_path):
        with open(font_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""

def generate_streak_svg(data):
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

    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    
    svg_content = f'''<svg width="620" height="96" viewBox="0 0 620 96" xmlns="http://www.w3.org/2000/svg">
<defs>
<style>
{font_style}
</style>
</defs>

  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.05s" dur="0.5s" fill="freeze" />
    <text x="0" y="34" class="b" font-size="30" fill="#E7E3DC">{current_streak}</text>
    <text x="0" y="54" font-size="11" fill="#8B877E">current streak</text>
  </g>
  <g opacity="0"><animate attributeName="opacity" from="0" to="1" begin="0.15s" dur="0.5s" fill="freeze" />
    <text x="310.0" y="34" class="b" font-size="30" fill="#B7A9DE">{longest_streak}</text>
    <text x="310.0" y="54" font-size="11" fill="#8B877E">longest streak &#183; days</text>
  </g>
  <line x1="0" y1="72" x2="620" y2="72" stroke="#2A2D33" stroke-width="1"
        stroke-dasharray="620" stroke-dashoffset="620"><animate attributeName="stroke-dashoffset" from="620" to="0" begin="0.3s" dur="0.9s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></line>
</svg>
'''
    return svg_content

if __name__ == "__main__":
    data_path = os.path.join(os.path.dirname(__file__), "data.json")
    if os.path.exists(data_path):
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        svg = generate_streak_svg(data)
        output_svg_path = os.path.join(os.path.dirname(__file__), "..", "streak.svg")
        with open(output_svg_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print("Generated streak.svg successfully!")

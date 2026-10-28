"""Quiet, borderless profile graphics in the original lavender palette."""
import base64
import json
import re
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', 'http://www.w3.org/2000/svg')


def font_style():
    styles = []
    for name, weight in [('JBM-Medium.subset.woff2', 500), ('JBM-Bold.subset.woff2', 700)]:
        font = base64.b64encode((ROOT / 'fonts' / name).read_bytes()).decode()
        styles.append(f"@font-face{{font-family:JBM;src:url(data:font/woff2;base64,{font});font-weight:{weight}}}")
    return ''.join(styles) + 'text{font-family:JBM,monospace}'


def frame(height, body, width=620):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><style>{font_style()}</style>{body}</svg>'


def finish_svg(source):
    """Show the final graphic immediately, including renderers without SMIL."""
    root = ET.fromstring(source)
    for parent in root.iter():
        for child in list(parent):
            if child.tag == NS + 'animate':
                if child.get('to') is not None:
                    parent.set(child.get('attributeName'), child.get('to'))
                parent.remove(child)
    # Keep the original palette, with enough contrast on GitHub's dark theme.
    for node in root.iter():
        if node.get('fill') in ('#555', '#8B877E'):
            node.set('fill', '#9B9AA3')
    return ET.tostring(root, encoding='unicode')


def write_static():
    title = frame(130, '<text x="310" y="66" text-anchor="middle" font-size="45" font-weight="700" letter-spacing="5" fill="#B7A9DE">aicyraa</text><text x="310" y="99" text-anchor="middle" font-size="11" letter-spacing="2" fill="#9B9AA3">Jee Daguman</text>')
    (ROOT / 'aicyraa.svg').write_text(title)
    for name, label in [('about','about'), ('projects','selected work'), ('stack','tools I use'), ('stats','a little more in numbers')]:
        length = 18 + len(label) * 8
        body = f'<text x="0" y="28" font-size="11" letter-spacing="2" fill="#B7A9DE">{label}</text><path d="M{length+20}24H620" stroke="#30323c" stroke-width="1"/>'
        (ROOT / f'hd-{name}.svg').write_text(frame(48, body))
    # Original monochrome logos, arranged into a more compact 6 × 2 grid.
    source = (ROOT / 'assets/stack-reference.svg').read_text()
    groups = re.findall(r'<g[^>]*>\s*(<path[^>]+/>)\s*</g>\s*<text[^>]*>([^<]+)</text>', source)
    paths = {label: path for path, label in groups}
    labels = ['HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Node.js', 'Express', 'Python', 'Java', 'Git', 'GitHub', 'Vite']
    body = ''
    for i, label in enumerate(labels):
        x, y = (i % 6) * (620 / 6) + 620 / 12, 37 + (i // 6) * 96
        if label == 'Vite':
            icon = '<path d="M2 3L12 22 22 3 12 5Z" fill="#92939c"/><path d="M13 1L7 12 12 11 10 18 17 8 12 9Z" fill="#B7A9DE"/>'
        else:
            icon = paths[label].replace('#888888', '#92939c')
        body += f'<g transform="translate({x-18:.2f},{y-18}) scale(1.5)">{icon}</g>'
        body += f'<text x="{x:.2f}" y="{y+39}" text-anchor="middle" font-size="10" fill="#9B9AA3">{escape(label)}</text>'
    (ROOT / 'stack-icons.svg').write_text(frame(208, body))


def render_saved():
    from generate_stats import generate_stats_svg
    from generate_streak import generate_streak_svg
    from generate_langs import generate_langs_svg
    data = json.loads((ROOT / 'scripts/data.json').read_text())
    write_static()
    for name, render in [('stats',generate_stats_svg), ('streak',generate_streak_svg), ('langs',generate_langs_svg)]:
        (ROOT / f'{name}.svg').write_text(finish_svg(render(data)), encoding='utf-8')


if __name__ == '__main__':
    render_saved()

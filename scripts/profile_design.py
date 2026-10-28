"""Profile layout: terminal and contributions, centered tools, gray with muted orange accents."""
import base64
import json
import re
import textwrap
from html import escape
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
NS = '{http://www.w3.org/2000/svg}'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
INK, MUTED, ACCENT, HIGHLIGHT = '#d4d4d4', '#969696', '#b4b4b4', '#d9a078'


def font_style():
    styles = []
    for name, weight in [('JBM-Medium.subset.woff2', 500), ('JBM-Bold.subset.woff2', 700)]:
        font = base64.b64encode((ROOT / 'fonts' / name).read_bytes()).decode()
        styles.append(f"@font-face{{font-family:JBM;src:url(data:font/woff2;base64,{font});font-weight:{weight}}}")
    return ''.join(styles) + 'text{font-family:JBM,monospace}'


def frame(height, body, width=620):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><style>{font_style()}</style>{body}</svg>'


def text(x, y, value, size=12, color=INK, extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" xml:space="preserve" {extra}>{escape(str(value))}</text>'


def finish_svg(source):
    """Resolve animation and apply the shared palette, including gradients."""
    root = ET.fromstring(source)
    palette = {'#B7A9DE': ACCENT, '#78A6C2': HIGHLIGHT, '#8FBF9F': '#aaaaaa',
               '#E7E3DC': INK, '#8B877E': MUTED, '#555': MUTED,
               '#2A2D33': '#303030', '#1A1C23': '#191919'}
    for parent in root.iter():
        for child in list(parent):
            if child.tag == NS + 'animate':
                if child.get('to') is not None:
                    parent.set(child.get('attributeName'), child.get('to'))
                parent.remove(child)
        for key, value in list(parent.attrib.items()):
            if value in palette:
                parent.set(key, palette[value])
    return ET.tostring(root, encoding='unicode')


def profile_panel(stats_svg):
    body = '<rect x=".5" y=".5" width="959" height="325" rx="12" fill="none" stroke="#393939"/>'
    body += '<path d="M1 40H959M317 40V325" stroke="#393939"/>'
    for x in [22,35,48]:
        body += f'<circle cx="{x}" cy="21" r="3" fill="#626262"/>'
    body += text(168,25,'~/profile',10,MUTED,'text-anchor="middle"')
    body += text(342,25,'contributions',10,MUTED)
    body += text(935,25,'github / last year',9,MUTED,'text-anchor="end"')
    body += text(24,73,'$ whoami',12,HIGHLIGHT)
    body += text(24,97,'Jee Daguman',13,INK)
    body += text(24,135,'$ cat profile.json',12,HIGHLIGHT)
    lines = [('{',MUTED), ('  "handle": "aicyraa",',INK), ('  "based_in": "Philippines",',INK),
             ('  "current focus": [',INK), ('    "backend", "agentic"',INK),
             ('  ]',INK), ('}',MUTED)]
    for i,(line,color) in enumerate(lines):
        body += text(24,160+i*20,line,11,color)
    body += text(24,306,'$ ',12,HIGHLIGHT)
    body += '<rect x="39" y="295" width="7" height="13" fill="#b4b4b4" opacity=".75"/>'
    root = ET.fromstring(stats_svg)
    root.set('x','331'); root.set('y','49'); root.set('width','610'); root.set('height','256')
    root.insert(0, ET.Element(NS+'title'))
    root[0].text = 'Public GitHub contributions over the last year'
    body += ET.tostring(root,encoding='unicode')
    return frame(326,body,960)


def about_panel():
    body = '<rect x=".5" y=".5" width="959" height="391" rx="12" fill="none" stroke="#393939"/>'
    body += '<path d="M1 40H959M343 40V391" stroke="#393939"/>'
    for x in [22, 35, 48]:
        body += f'<circle cx="{x}" cy="21" r="3" fill="#626262"/>'
    body += text(652, 25, '~/about', 10, MUTED, 'text-anchor="middle"')
    body += text(172, 25, 'avatar.ascii', 10, MUTED, 'text-anchor="middle"')
    body += text(367, 73, '$ cat about.txt', 12, HIGHLIGHT)
    body += text(367, 100, 'A builder', 14, ACCENT, 'font-weight="700"')
    y = 123
    for line in textwrap.wrap('Based in the Philippines. I build useful software around everyday problems.', width=76):
        body += text(367, y, line, 12)
        y += 22
    sections = [
        ('work', 'I work with React and TypeScript on web applications, alongside Python and Java. My projects span grocery budgeting, student case management, data structures, and algorithms.'),
        ('focus', 'My current focus is backend development and agentic systems. I’m exploring how APIs, data workflows, and tool-using agents fit together in practical applications.'),
    ]
    for name, paragraph in sections:
        y += 17
        body += text(367, y, f'$ cat {name}.txt', 12, HIGHLIGHT)
        y += 27
        for line in textwrap.wrap(paragraph, width=76):
            body += text(367, y, line, 12)
            y += 22
    # Fixed-width characters sampled from the real GitHub avatar, with sampled colors.
    portrait = json.loads((ROOT/'assets/avatar-ascii.json').read_text())
    body += '<g aria-label="Grayscale ASCII rendering of the current GitHub profile picture">'
    for row_index, row in enumerate(portrait['rows']):
        for col_index, (char, color) in enumerate(row):
            if char != ' ':
                luminance = round(sum(int(color[i:i+2], 16) * weight for i, weight in [(1, .2126), (3, .7152), (5, .0722)]))
                color = f'#{luminance:02x}{luminance:02x}{luminance:02x}'
                body += text(round(29 + col_index * 5.1, 2), round(79 + row_index * 9.3, 2), char, 8.5, color)
    body += '</g>'
    return frame(392, body, 960)



def terminal_body(height, title):
    body = f'<rect x=".5" y=".5" width="959" height="{height-1}" rx="12" fill="none" stroke="#393939"/>'
    body += '<path d="M1 40H959" stroke="#393939"/>'
    for x in [22, 35, 48]:
        body += f'<circle cx="{x}" cy="21" r="3" fill="#626262"/>'
    return body + text(480, 25, title, 10, MUTED, 'text-anchor="middle"')


def embed_svg(source, x, y, width, height):
    root = ET.fromstring(source)
    for key, value in [('x',x), ('y',y), ('width',width), ('height',height)]:
        root.set(key, str(value))
    return ET.tostring(root, encoding='unicode')


def tools_panel(source):
    body = terminal_body(470, '~/tools')
    body += text(24, 74, '$ ls tools/', 12, HIGHLIGHT)
    body += embed_svg(source, 60, 100, 840, 350)
    return frame(470, body, 960)


def analytics_panel(streak, languages):
    body = terminal_body(450, '~/stats')
    body += text(24, 74, '$ github streaks', 12, HIGHLIGHT)
    body += embed_svg(streak, 100, 87, 760, 103)
    body += text(24, 207, '$ github languages --by bytes', 12, HIGHLIGHT)
    body += embed_svg(languages, 100, 231, 760, 208)
    return frame(450, body, 960)


def write_static():
    (ROOT/'about-panel.svg').write_text(about_panel(), encoding='utf-8')
    for name,label in [('about','about'), ('stack','tools I use'), ('stats','languages & streaks')]:
        body = '<path d="M100 27H350M610 27H860" stroke="#393939"/>'
        body += text(480,31,label,11,ACCENT,'text-anchor="middle" letter-spacing="1.5"')
        (ROOT/f'hd-{name}.svg').write_text(frame(54,body,960))
    source = (ROOT/'assets/stack-reference.svg').read_text()
    groups = re.findall(r'<g[^>]*>\s*(<path[^>]+/>)\s*</g>\s*<text[^>]*>([^<]+)</text>',source)
    paths = {label:path for path,label in groups}
    labels = ['HTML','CSS','JavaScript','TypeScript','React','Node.js','Express','Python','Java','Git',
              'GitHub','Vite','Prisma','Neon','Supabase','Vercel','Vitest','Jest','Bruno','Postman']
    body = ''
    for i,label in enumerate(labels):
        x,y = 84+(i%5)*168, 33+(i//5)*88
        local = ROOT/'assets/icons'/f'{label.lower()}.svg'
        if local.is_file():
            icon_root = ET.fromstring(local.read_text())
            # Keep the source viewBox: logos remain correct if an upstream mark changes size.
            icon_root.set('x',str(x-17)); icon_root.set('y',str(y-17))
            icon_root.set('width','34'); icon_root.set('height','34')
            icon_root.set('fill','#aaaaaa')
            icon = ET.tostring(icon_root,encoding='unicode')
        else:
            path = paths[label].replace('#888888','#aaaaaa')
            icon = f'<g transform="translate({x-17},{y-17}) scale({34/24})">{path}</g>'
        body += icon + text(x,y+38,label,10,MUTED,'text-anchor="middle"')
    tools = frame(350,body,840)
    (ROOT/'stack-icons.svg').write_text(tools)
    (ROOT/'tools-panel.svg').write_text(tools_panel(tools), encoding='utf-8')


def render_all(data):
    from generate_stats import generate_stats_svg
    from generate_skyline import generate_skyline_svg
    from generate_streak import generate_streak_svg
    from generate_langs import generate_langs_svg
    write_static()
    # Keep skyline CSS animations; finish_svg intentionally freezes older charts.
    (ROOT/'skyline.svg').write_text(generate_skyline_svg(data), encoding='utf-8')
    stats = finish_svg(generate_stats_svg(data))
    (ROOT/'stats.svg').write_text(stats,encoding='utf-8')
    (ROOT/'profile-panel.svg').write_text(profile_panel(stats),encoding='utf-8')
    streak = finish_svg(generate_streak_svg(data))
    languages = finish_svg(generate_langs_svg(data))
    (ROOT/'streak.svg').write_text(streak, encoding='utf-8')
    (ROOT/'langs.svg').write_text(languages, encoding='utf-8')
    (ROOT/'analytics-panel.svg').write_text(analytics_panel(streak, languages), encoding='utf-8')


if __name__ == '__main__':
    render_all(json.loads((ROOT/'scripts/data.json').read_text()))

"""Refresh the saved ASCII portrait; retain it on download or decoding failure."""
import io
import json
import urllib.request
from urllib.parse import quote, urlsplit, urlunsplit, parse_qsl, urlencode

from profile_design import ROOT


def image_to_ascii(raw, source):
    from PIL import Image, ImageOps

    with Image.open(io.BytesIO(raw)) as image:
        image = image.convert('RGB').resize((56, 32), Image.Resampling.LANCZOS)
    colors = image.quantize(colors=32).convert('RGB')
    gray = ImageOps.autocontrast(ImageOps.grayscale(image), cutoff=2)
    chars = ' .:-=+*#%@'
    rows = []
    for y in range(32):
        row = []
        for x in range(56):
            brightness = gray.getpixel((x, y))
            char = chars[min(len(chars)-1, brightness * len(chars) // 256)]
            color = '#' + ''.join(f'{min(255, round(c*.82+30)):02x}' for c in colors.getpixel((x, y)))
            row.append([char, color])
        rows.append(row)
    return {'source': source, 'columns': 56, 'rows': rows}


def refresh_avatar(username, token=None):
    try:
        headers = {'User-Agent': 'Aicyraa-profile', 'Accept': 'application/vnd.github+json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        request = urllib.request.Request(f'https://api.github.com/users/{quote(username, safe="")}', headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            source = json.load(response)['avatar_url']
        parts = urlsplit(source)
        query = dict(parse_qsl(parts.query))
        query['s'] = '400'
        url = urlunsplit(parts._replace(query=urlencode(query)))
        request = urllib.request.Request(url, headers={'User-Agent': 'Aicyraa-profile'})
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read()
        portrait = image_to_ascii(raw, source)
        path = ROOT / 'assets/avatar-ascii.json'
        path.write_text(json.dumps(portrait, separators=(',', ':')) + '\n', encoding='utf-8')
        print('Refreshed ASCII portrait from the current GitHub avatar.')
        return True
    except (OSError, ValueError, KeyError, ImportError) as error:
        print(f'Avatar refresh unavailable; keeping the saved portrait: {error}')
        return False

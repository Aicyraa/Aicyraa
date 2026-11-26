"""Checks for the about panel, tools grid, icon SVGs, and avatar refresh headers."""
import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import MagicMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import profile_design
import refresh_avatar

NS = {'s': 'http://www.w3.org/2000/svg'}


class ProfileTests(unittest.TestCase):
    def test_about_panel_contains_updated_work_text_and_avatar(self):
        svg = profile_design.about_panel()
        root = ET.fromstring(svg)
        texts = root.findall('.//s:text', NS)
        joined = ' '.join(t.text or '' for t in texts)
        self.assertIn('full-stack web applications and backend services', joined)
        self.assertIn('reliable APIs, clean data models, and practical software design.', joined)
        self.assertNotIn('grocery budgeting', joined)
        self.assertNotIn('student case management', joined)
        for node in texts:
            self.assertLessEqual(float(node.get('y')), 380.0)
        self.assertIsNotNone(root.find('.//s:g[@class="avatar"]', NS))

    def test_tools_panel_has_22_tools_with_hono_and_zod_and_centered_bottom_row(self):
        profile_design.write_static()
        tools_svg = (ROOT / 'tools-panel.svg').read_text(encoding='utf-8')
        root = ET.fromstring(tools_svg)
        expected = [
            'HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Node.js',
            'Express', 'Hono', 'Zod', 'Python', 'Java', 'Git',
            'GitHub', 'Vite', 'Prisma', 'Neon', 'Supabase', 'Vercel',
            'Vitest', 'Jest', 'Bruno', 'Postman',
        ]
        label_nodes = {
            node.text: float(node.get('x'))
            for node in root.findall('.//s:text', NS)
            if node.text in expected
        }
        self.assertEqual(set(label_nodes), set(expected))
        bottom_xs = [label_nodes[name] for name in ('Vitest', 'Jest', 'Bruno', 'Postman')]
        self.assertEqual(bottom_xs, [210.0, 350.0, 490.0, 630.0])
        for name in ('hono', 'zod'):
            icon_root = ET.parse(ROOT / 'assets/icons' / f'{name}.svg').getroot()
            self.assertIsNone(icon_root.get('fill'))
            for path in icon_root.findall('.//s:path', NS):
                self.assertIsNone(path.get('fill'))

    def test_refresh_avatar_sends_no_cache_headers(self):
        seen_requests = []

        def fake_urlopen(req, timeout=30):
            seen_requests.append(req)
            resp = MagicMock()
            resp.__enter__.return_value = resp
            resp.__exit__.return_value = False
            if len(seen_requests) == 1:
                resp.read.return_value = json.dumps({'avatar_url': 'https://avatars.githubusercontent.com/u/1?v=4'}).encode()
            else:
                resp.read.return_value = b'fake-png-bytes'
            return resp

        fake_portrait = {'source': 'https://avatars.githubusercontent.com/u/1?v=4', 'columns': 56, 'rows': []}
        with patch.object(refresh_avatar.urllib.request, 'urlopen', side_effect=fake_urlopen), \
             patch.object(refresh_avatar, 'image_to_ascii', return_value=fake_portrait), \
             patch.object(Path, 'write_text'):
            ok = refresh_avatar.refresh_avatar('Aicyraa')

        self.assertTrue(ok)
        self.assertEqual(len(seen_requests), 2)
        for req in seen_requests:
            headers = {k.lower(): v for k, v in req.header_items()}
            self.assertEqual(headers.get('cache-control'), 'no-cache')
            self.assertEqual(headers.get('pragma'), 'no-cache')


if __name__ == '__main__':
    unittest.main()

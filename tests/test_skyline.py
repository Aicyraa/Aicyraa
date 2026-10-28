"""Checks for calendar placement, source fidelity, and SVG animation behavior."""
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fetch_data import CalendarParser
from generate_skyline import generate_skyline_svg

NS = {'s': 'http://www.w3.org/2000/svg'}


class SkylineTests(unittest.TestCase):
    def test_calendar_preserves_github_levels_and_exact_counts(self):
        parser = CalendarParser()
        parser.feed('<td id="d" data-date="2026-10-28" data-level="4"></td>'
                    '<tool-tip for="d">1,234 contributions on October 28th.</tool-tip>')
        self.assertEqual(parser.dates['d'], '2026-10-28')
        self.assertEqual(parser.counts['d'], 1234)
        self.assertEqual(parser.levels['d'], 4)

    def test_partial_week_uses_actual_weekdays_and_draws_back_to_front(self):
        days = [{'date': '2026-10-24', 'count': 3, 'level': 1},  # Saturday, front
                {'date': '2026-10-25', 'count': 20, 'level': 4}]  # Sunday, back
        root = ET.fromstring(generate_skyline_svg({'daily_contributions': days}))
        groups = root.findall('.//s:g[@data-date]', NS)
        self.assertEqual([g.get('data-date') for g in groups], ['2026-10-25', '2026-10-24'])
        self.assertIn('week-1', groups[0].get('class'))
        self.assertIn('week-0', groups[1].get('class'))
        self.assertEqual([g.get('data-count') for g in groups], ['20', '3'])
        labels = [n.text for n in root.findall('.//s:text', NS)]
        self.assertIn('23', labels)
        self.assertIn('20 contributions', labels)
        self.assertIn('25 Oct 2026 / best day', labels)

    def test_zero_and_missing_data_do_not_invent_peak_activity(self):
        for days in [[], [{'date': '2026-10-28', 'count': 0, 'level': 0}]]:
            source = generate_skyline_svg({'daily_contributions': days})
            root = ET.fromstring(source)
            self.assertEqual(len(root.findall('.//s:g[@data-date]', NS)), len(days))
            self.assertNotIn(' / best day', source)

    def test_animation_has_readable_static_and_reduced_motion_fallbacks(self):
        source = generate_skyline_svg({'daily_contributions': [
            {'date': '2026-10-28', 'count': 10, 'level': 2}]})
        root = ET.fromstring(source)
        css = ''.join(n.text or '' for n in root.findall('s:style', NS))
        self.assertIn('prefers-reduced-motion:reduce', css)
        self.assertIn('animation:none!important', css)
        self.assertIn('16s', css)
        self.assertNotIn('<script', source)
        self.assertNotIn('<foreignObject', source)
        self.assertEqual(len(root.findall('.//s:g[@data-date]/s:path', NS)), 3)


if __name__ == '__main__':
    unittest.main()

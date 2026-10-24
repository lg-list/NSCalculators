import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class SecondsHoursTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_existing_url_has_duration_components_and_accurate_metadata(self):
        calc = self.calcs['seconds-to-hours-calculator']
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('id="seconds_hours_value"', 'data-engine="seconds_hours_advanced"',
                     '99 hours, 0 minutes, and 42 seconds', '4 days, 3 hours, 0 minutes, and 42 seconds',
                     'integer microsecond arithmetic', 'nist-guide-si-chapter-5-units-outside-si',
                     'href="/time-duration-calculator/"'):
            self.assertIn(text, html)
        self.assertIn('hours, minutes, seconds', build.seo_description(calc))
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertNotIn('id="genericChart"', html)

    def test_related_clock_tool_and_sibling_index_policy_are_preserved(self):
        html = build.calculator_page(self.data['site'], self.calcs['time-duration-calculator'], [])
        self.assertIn('seconds to hours converter', html)
        self.assertIn('data-engine="time_duration"', html)
        self.assertEqual(self.calcs['minutes-to-seconds-calculator']['engine'], 'linear_convert')
        self.assertFalse(build.is_indexable_calculator(self.calcs['seconds-to-minutes-calculator']))


if __name__ == '__main__':
    unittest.main()

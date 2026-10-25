import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class CalendarDaysTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_existing_calendar_routes_have_date_only_results_and_original_examples(self):
        for slug in ('date-calculator', 'day-counter', 'day-of-the-week-calculator'):
            with self.subTest(slug=slug):
                calc = self.calcs[slug]
                html = build.calculator_page(self.data['site'], calc, [])
                self.assertEqual(calc['engine'], 'cn_date')
                self.assertTrue(build.is_indexable_calculator(calc))
                for text in ('Calendar Date Results', 'Date Difference Details',
                             'January 1 to January 2, 2026 is 1 day', 'Thursday and Friday',
                             'not a fixed number of days', 'href="/time-duration-calculator/"',
                             'href="/age-calculator/"', 'id="start"', 'id="end"'):
                    self.assertIn(text, html)
                self.assertNotIn('id="genericChart"', html)

    def test_pregnancy_engine_is_not_switched_to_calendar_difference(self):
        calc = self.calcs['due-date-calculator']
        self.assertEqual(calc['engine'], 'cn_due_date')
        self.assertNotIn('Calendar Date Results', build.analysis_extra_html(calc))


if __name__ == '__main__':
    unittest.main()

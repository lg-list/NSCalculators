import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class PensionPageTests(unittest.TestCase):
    def test_existing_route_replaces_savings_engine_without_extra_indexable_pages(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'pension-calculator')
        self.assertEqual(calc['engine'], 'pension_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        html = build.calculator_page(data['site'], calc, [])
        for text in ('id="pen_mode"', 'id="pen_survivor"', 'id="pensionChart"', 'id="pensionSchedule"',
                     'data-engine="pension_advanced"', 'midpoint', 'death age-year', 'PBGC', '0% COLA',
                     'https://nscalculators.com/pension-calculator/'):
            self.assertIn(text, html)
        self.assertNotIn('data-engine="cn_retirement"', html)
        self.assertNotIn('id="principal"', html)
        self.assertNotIn('noindex,follow', html)
        self.assertIn('pension payout calculator', build.seo_keywords(calc))


if __name__ == '__main__':
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class NewUsedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_purpose_built_comparison_has_metadata_inputs_and_complete_output(self):
        calc = self.calcs['new-vs-used-car-calculator']
        self.assertEqual(calc['engine'], 'new_used_cost')
        self.assertEqual(calc['cat'], 'Automotive')
        self.assertEqual(build.calculator_group(calc), 'Car Value')
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertFalse(calc['keyword_data'])
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('id="nu_years"', 'id="nu_new_price"', 'id="nu_used_resale"',
                     'id="nu_new_months"', 'id="nu_used_maintenance"',
                     'data-engine="new_used_cost"', 'Cost and Cash Flow Details',
                     'data-chart-type="bars"', '$34,000', '$32,900',
                     'remaining loan balance', 'consumerfinance.gov',
                     'consumer.ftc.gov', 'not live market quotes'):
            self.assertIn(text, html)
        self.assertIn('Ownership Costs', build.seo_title(calc))
        self.assertIn('sale equity', build.seo_description(calc))

    def test_current_value_resale_and_financing_pages_link_to_distinct_comparison(self):
        for slug in ('used-car-value-calculator', 'car-resale-value-calculator', 'auto-loan-calculator'):
            with self.subTest(slug=slug):
                html = build.calculator_page(self.data['site'], self.calcs[slug], [])
                self.assertIn('href="/new-vs-used-car-calculator/"', html)
                self.assertNotIn('data-engine="new_used_cost"', html)


if __name__ == '__main__':
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class IraComparisonTests(unittest.TestCase):
    def test_existing_route_uses_dedicated_equal_budget_comparison(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'ira-calculator')
        self.assertEqual(calc['engine'], 'ira_compare')
        self.assertTrue(build.is_indexable_calculator(calc))
        html = build.calculator_page(data['site'], calc, [])
        for text in ('data-engine="ira_compare"', 'id="ira_current_tax"', 'id="ira_retire_tax"',
                     'id="iraSchedule"', 'data-chart-type="bars"', 'equal pre-tax', 'five-year requirement',
                     'year end', 'no tax credit assumed for losses', 'Publication 590-A'):
            self.assertIn(text, html)
        self.assertNotIn('id="inflation"', html)
        self.assertNotIn('data-engine="cn_retirement"', html)

    def test_retirement_cluster_routes_accumulation_and_drawdown_distinctly(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        html = build.calculator_page(data['site'], calculators['retirement-calculator'], [])
        self.assertIn('href="/ira-calculator/"', html)
        ira = build.calculator_page(data['site'], calculators['ira-calculator'], [])
        self.assertIn('withdrawal or longevity mode', ira)
        self.assertIn('href="/rmd-calculator/"', ira)
        self.assertNotIn('href="/annuity-payout-calculator/"', ira)


if __name__ == '__main__':
    unittest.main()

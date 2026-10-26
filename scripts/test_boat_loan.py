import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class BoatLoanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_dedicated_purchase_budget_and_schedule(self):
        calc = self.calcs['boat-loan-calculator']
        self.assertEqual(calc['engine'], 'boat_loan_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('id="bl_price"', 'id="bl_down_unit"', 'id="bl_add_costs"',
                     'id="bl_fee_method"', 'id="boatSchedule"', 'type="month"',
                     'data-chart-type="pie"', '$474.81', '$510.42', '$13,000',
                     'not economic ownership cost', 'not a fee-inclusive APR',
                     'href="/loan-calculator/"', 'href="/personal-loan-calculator/"'):
            self.assertIn(text, html)
        self.assertIn('Down Payment', build.seo_title(calc))
        self.assertIn('amortization schedule', build.seo_description(calc))

    def test_general_loans_link_to_boat_purchase_workflow(self):
        for slug in ('loan-calculator', 'amortization-calculator'):
            html = build.calculator_page(self.data['site'], self.calcs[slug], [])
            self.assertIn('href="/boat-loan-calculator/"', html)
            self.assertNotIn('data-engine="boat_loan_advanced"', html)


if __name__ == '__main__':
    unittest.main()

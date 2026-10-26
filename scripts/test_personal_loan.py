import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class PersonalLoanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_personal_loan_has_own_fields_schedule_and_cash_flow_explanation(self):
        calc = self.calcs['personal-loan-calculator']
        self.assertEqual(calc['engine'], 'personal_loan_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('id="pl_add_costs"', 'id="pl_fee_unit"', 'id="pl_fee_method"',
                     'type="month"', 'id="personalSchedule"', 'data-chart-type="pie"',
                     '$9,500', 'not a lender disclosure', 'not an effective annual yield',
                     'href="/loan-calculator/"', 'href="/amortization-calculator/"'):
            self.assertIn(text, html)
        self.assertIn('Net Proceeds', build.seo_title(calc))
        self.assertIn('origination fees', build.seo_description(calc))

    def test_business_loan_keeps_its_model_and_general_loans_have_contextual_route(self):
        self.assertEqual(self.calcs['business-loan-calculator']['engine'], 'loan')
        for slug in ('loan-calculator', 'amortization-calculator'):
            html = build.calculator_page(self.data['site'], self.calcs[slug], [])
            self.assertIn('href="/personal-loan-calculator/"', html)
            self.assertNotIn('data-engine="personal_loan_advanced"', html)


if __name__ == '__main__':
    unittest.main()

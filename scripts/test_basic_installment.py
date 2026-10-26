import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class BasicInstallmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_four_existing_installment_routes_explain_scope(self):
        specific = {
            'repayment-calculator': 'chosen payment',
            'student-loan-calculator': 'income-driven payments',
            'business-loan-calculator': 'SBA fees',
            'home-equity-loan-calculator': 'not a HELOC',
        }
        for slug, limitation in specific.items():
            calc = self.calcs[slug]
            html = build.calculator_page(self.data['site'], calc, [])
            self.assertEqual(calc['engine'], 'loan')
            self.assertTrue(build.is_indexable_calculator(calc))
            self.assertIn('nominal annual note rate', calc['desc'])
            for text in ('Fixed-rate payment scope', limitation, '$212.47', '$166.67',
                         '1-600 whole monthly payments', 'Fractional years are accepted',
                         'not a lender payoff quote', 'data-engine="loan"'):
                self.assertIn(text, html)

    def test_unfinished_fha_and_redirects_do_not_become_indexable(self):
        fha = self.calcs['fha-loan-calculator']
        html = build.calculator_page(self.data['site'], fha, [])
        self.assertFalse(build.is_indexable_calculator(fha))
        self.assertNotIn('data-engine="loan"', html)
        self.assertFalse(build.is_indexable_calculator(self.calcs['loan-payment-calculator']))


if __name__ == '__main__':
    unittest.main()

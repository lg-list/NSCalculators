import unittest
import build


class AmortizationPageTests(unittest.TestCase):
    def test_original_route_explains_payments_dates_and_cost_totals(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'amortization-calculator')
        html = build.calculator_page(data['site'], calc, [])
        for text in ('data-engine="amortization_advanced"', 'First payment month', 'id="amort_include_extras"',
                     'id="amort_monthly_start"', 'id="amort_yearly_start"', 'id="amort_once_10"',
                     'id="amort_date_10"', 'Regular payments versus total paid', '$293,886.58',
                     'June 2040', 'twelve loan payments, not calendar tax years', 'CFPB explains'):
            self.assertIn(text, html)
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertEqual(build.calculator_group(calc), 'Loans')
        self.assertEqual(html.count('id="amort_include_extras"'), 1)
        self.assertIn('https://nscalculators.com/amortization-calculator/', html)


if __name__ == '__main__':
    unittest.main()

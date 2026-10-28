import unittest
import build


class K401PageTests(unittest.TestCase):
    def test_projection_scope_and_withdrawal_examples_are_visible(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == '401k-calculator')
        html = build.calculator_page(data['site'], calc, [])
        for text in ('More projection assumptions', 'Exception assumptions', 'Uncapped salary-based projection',
                     'not a contribution-compliance forecast', '$31,500', '$36,500', 'age 59.5',
                     'calendar-year assumption', 'additional funds required', 'id="k401Schedule"'):
            self.assertIn(text, html)
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertEqual(html.count('id="k401_age"'), 1)


if __name__ == '__main__':
    unittest.main()

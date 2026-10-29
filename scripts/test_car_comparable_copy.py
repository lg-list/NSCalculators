import unittest
import build


class CarComparableCopy(unittest.TestCase):
    def test_optional_benchmark_and_channel_chart(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'used-car-value-calculator')
        html = build.calculator_page(data['site'], calc, [])
        for text in ('used_comparable_prices', 'Use median asking price', 'not parts of a combined total',
                     'not a substitute for choosing comparable', '$23,000', 'data-chart-type="bars"'):
            self.assertIn(text, html)
        self.assertNotIn('data-center-label="total"', html)
        self.assertEqual(html.count('id="retail_benchmark"'), 1)
        self.assertTrue(build.is_indexable_calculator(calc))

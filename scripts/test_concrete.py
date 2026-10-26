import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class ConcreteTests(unittest.TestCase):
    def test_existing_concrete_route_has_label_yield_units_and_original_examples(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'concrete-volume-calculator')
        html = build.calculator_page(data['site'], calc, [])
        self.assertTrue(build.is_indexable_calculator(calc))
        for text in ('id="concrete_units"', 'id="concrete_custom_yield"', 'id="concrete_yield_unit"',
                     'QUIKRETE 1101', 'value="0.375"', 'value="0.675"', 'value="liters"',
                     'Volume Breakdown (Cubic Feet)', '45 bags', '50 whole bags', '54 bags',
                     '6.096 m', '101.6 mm', 'not a net surround or footing design',
                     'not universal weight-to-volume conversions', 'Blank optional prices',
                     'data-engine="concrete_advanced"'):
            self.assertIn(text, html)
        self.assertNotIn('Volume and Cost Comparison', html)
        self.assertIn('80 lb or custom-yield bags', build.seo_description(calc))

    def test_existing_alias_and_index_scope_are_not_expanded(self):
        self.assertEqual(build.CALCULATOR_REDIRECTS['concrete-calculator'], 'concrete-volume-calculator')
        data = build.read_data()
        calcs = build.base_and_supplemental(data)
        self.assertEqual(sum(c['slug'] == 'concrete-volume-calculator' for c in calcs), 1)
        self.assertNotIn('80lb-concrete-bag-calculator', {c['slug'] for c in calcs})


if __name__ == '__main__':
    unittest.main()

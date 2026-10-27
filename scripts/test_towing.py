import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class TowingPageTests(unittest.TestCase):
    def test_existing_route_has_independent_limits_and_explicit_load_basis(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'towing-capacity-calculator')
        self.assertTrue(build.is_indexable_calculator(calc))
        html = build.calculator_page(data['site'], calc, [])
        for text in ('data-engine="towing"', 'data-chart-type="bars"', 'Independent Trailer-Weight Limits',
                     'Cargo + hitch hardware', 'Blank is unknown; 0 means no capacity.',
                     '5,416 lb', '7,500 lb', '13,300 lb', '2026-Ford-RV-and-Trailer-Towing-Guide-v3.pdf'):
            self.assertIn(text, html)
        self.assertNotIn('data-chart-type="pie"', html)
        self.assertIn('GCWR, Payload &amp; Hitch Limits', html)

    def test_related_tools_are_real_purpose_built_routes(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        for slug in ('payload-capacity-calculator', 'trailer-payload-calculator', 'trailer-tongue-weight-calculator'):
            self.assertTrue(build.has_purpose_built_calculation(calculators[slug]))


if __name__ == '__main__':
    unittest.main()

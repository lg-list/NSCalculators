import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class FuelFields(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_details = False
        self.primary = []
        self.advanced = []

    def handle_starttag(self, tag, attrs):
        if tag == 'details':
            self.in_details = True
        if tag in {'input', 'select'}:
            (self.advanced if self.in_details else self.primary).append(dict(attrs)['id'])

    def handle_endtag(self, tag):
        if tag == 'details':
            self.in_details = False


class FuelCostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = build.read_data()
        cls.calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'trip-fuel-cost-calculator')
        cls.html = build.calculator_page(data['site'], cls.calc, [])

    def test_existing_indexable_route_uses_cost_comparison_not_generic_pie(self):
        self.assertTrue(build.is_indexable_calculator(self.calc))
        self.assertIn('data-engine="fuel_cost_advanced"', self.html)
        self.assertIn('data-chart-type="bars"', self.html)
        self.assertNotIn('data-chart-type="pie"', self.html)
        self.assertNotIn('content="noindex,follow"', self.html)

    def test_alias_targets_are_unchanged(self):
        for slug in ('car-fuel-cost-calculator', 'fuel-cost-calculator'):
            self.assertEqual(build.CALCULATOR_REDIRECTS[slug], 'trip-fuel-cost-calculator')

    def test_worked_example_adds_detour_once_and_explains_units(self):
        self.assertIn('650 x 2 x 2 + 40 = 2,640 miles', self.html)
        self.assertIn('$93.34', self.html)
        self.assertIn('NIST conversion tables', self.html)
        self.assertIn('Currency', self.html)

    def test_core_fields_are_paired_and_repeat_count_remains_available(self):
        fields = FuelFields()
        fields.feed(build.trip_fuel_cost_input_html())
        self.assertEqual(fields.primary, ['distance', 'distance_unit', 'trip_type', 'currency', 'efficiency', 'efficiency_unit', 'fuelprice', 'price_unit'])
        self.assertEqual(fields.advanced, ['trips', 'extra_distance', 'reserve_percent', 'other_costs', 'people'])


if __name__ == '__main__':
    unittest.main()

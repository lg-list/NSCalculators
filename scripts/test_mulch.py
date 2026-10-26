import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class MulchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_existing_route_has_distinct_volume_label_workflow_and_original_scope(self):
        calc = self.calcs['mulch-calculator']
        self.assertEqual(calc['engine'], 'mulch_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertFalse(calc['keyword_data'])
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('data-engine="mulch_advanced"', 'id="mulch_bag_volume"', 'id="mulch_bulk_unit"',
                     'Quantity and Cost Details', 'Cubic Feet', '28 whole bags',
                     'separate scenarios', 'not a universal', 'existing mulch',
                     'extension.iastate.edu', 'ucanr.edu', 'Bag-label units are independent'):
            self.assertIn(text, html)
        self.assertNotIn('currently unavailable', html)
        self.assertNotIn('content="noindex,follow"', html)
        self.assertIn('Bags', build.seo_title(calc))
        self.assertIn('bag-label volume', build.seo_description(calc))
        self.assertEqual(build.calculator_schema(self.data['site'], calc)['@type'], 'SoftwareApplication')

    def test_discovery_and_internal_routing_without_unfinished_expansion(self):
        entries = {c['slug']: c for c in build.calculator_search_index(list(self.calcs.values()))}
        self.assertIn('mulch-calculator', entries)
        self.assertNotIn('fha-loan-calculator', entries)
        for slug in ('gravel-calculator', 'square-footage-calculator'):
            self.assertIn('href="/mulch-calculator/"', build.calculator_page(self.data['site'], self.calcs[slug], []))


if __name__ == '__main__':
    unittest.main()

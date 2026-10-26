import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class GravelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_existing_route_restored_with_original_content_and_correct_metadata(self):
        calc = self.calcs['gravel-calculator']
        self.assertEqual(calc['engine'], 'gravel_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertFalse(calc['keyword_data'])
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('data-engine="gravel_advanced"', 'id="gravel_units"', 'id="gravel_density"',
                     'id="gravel_price_unit"', 'Quantity and Cost Details', 'Cubic Feet',
                     '50/27', '2.75 US short tons', '25% volume reduction',
                     'dirtandgravel.psu.edu', 'nist.gov', 'Blank density', 'No supplier affiliation'):
            self.assertIn(text, html)
        self.assertNotIn('currently unavailable', html)
        self.assertNotIn('content="noindex,follow"', html)
        self.assertIn('US Tons', build.seo_title(calc))
        self.assertIn('supplier density', build.seo_description(calc))
        self.assertIn('https://nscalculators.com/gravel-calculator/', html)
        self.assertEqual(build.calculator_schema(self.data['site'], calc)['@type'], 'SoftwareApplication')
        self.assertEqual(build.calculator_schema(self.data['site'], calc)['applicationCategory'], 'UtilitiesApplication')

    def test_discovery_and_context_links_restore_only_reviewed_tool(self):
        entries = {c['slug']: c for c in build.calculator_search_index(list(self.calcs.values()))}
        self.assertIn('gravel-calculator', entries)
        self.assertNotIn('mulch-calculator', entries)
        self.assertFalse(build.is_indexable_calculator(self.calcs['mulch-calculator']))
        for slug in ('concrete-volume-calculator', 'square-footage-calculator'):
            self.assertIn('href="/gravel-calculator/"', build.calculator_page(self.data['site'], self.calcs[slug], []))


if __name__ == '__main__':
    unittest.main()

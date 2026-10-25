import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class SiteSearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calculators = [c for c in build.base_and_supplemental(cls.data) if c['slug'] not in build.CALCULATOR_REDIRECTS and c['slug'] not in build.CATEGORY_PAGE_REDIRECTS]
        cls.entries = build.calculator_search_index(cls.calculators)

    def test_search_uses_current_page_descriptions_for_existing_tools(self):
        entries = {c['slug']: c for c in self.entries}
        for slug in ['used-car-value-calculator', 'time-duration-calculator', 'trip-fuel-cost-calculator']:
            calc = next(c for c in self.calculators if c['slug'] == slug)
            self.assertEqual(entries[slug]['desc'], build.seo_description(calc))
        self.assertIn('price estimate', entries['used-car-value-calculator']['desc'])
        self.assertIn('elapsed time', entries['time-duration-calculator']['desc'])

    def test_search_update_does_not_expand_discovery_scope(self):
        baseline = [c for c in self.entries if c['slug'] != 'new-vs-used-car-calculator']
        self.assertEqual(len(baseline), 2456)
        self.assertEqual(len({c['slug'] for c in baseline}), 2456)
        self.assertEqual(sum(c['slug'] == 'new-vs-used-car-calculator' for c in self.entries), 1)
        self.assertNotIn('fha-loan-calculator', {c['slug'] for c in self.entries})

    def test_homepage_requests_new_search_asset(self):
        html = build.home(self.data['site'], self.calculators)
        self.assertIn(f'/assets/search.js?v={build.SEARCH_ASSET_VERSION}', html)
        self.assertNotIn('/assets/search.js?v=20261019d', html)


if __name__ == '__main__':
    unittest.main()

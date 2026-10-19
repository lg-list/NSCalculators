import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class DiscoveryQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calculators = [
            c for c in build.base_and_supplemental(cls.data)
            if c["slug"] not in build.CALCULATOR_REDIRECTS
        ]
        cls.entries = build.calculator_search_index(cls.calculators)
        cls.search_slugs = {c["slug"] for c in cls.entries}

    def test_unfinished_tools_are_not_promoted(self):
        unfinished = {
            c["slug"] for c in self.calculators
            if not build.has_purpose_built_calculation(c)
            and c["slug"] != "scientific-calculator"
        }
        self.assertTrue(unfinished)
        self.assertFalse(unfinished & self.search_slugs)

    def test_working_noindex_tools_remain_searchable(self):
        working_noindex = {
            c["slug"] for c in self.calculators
            if build.has_purpose_built_calculation(c)
            and not build.is_indexable_calculator(c)
        }
        self.assertTrue(working_noindex)
        self.assertTrue(working_noindex <= self.search_slugs)

    def test_indexable_tools_remain_searchable(self):
        indexable = {c["slug"] for c in self.calculators if build.is_indexable_calculator(c)}
        self.assertTrue(indexable <= self.search_slugs)

    def test_scientific_calculator_has_one_dedicated_entry(self):
        scientific = [c for c in self.entries if c["slug"] == "scientific-calculator"]
        self.assertEqual(len(scientific), 1)
        self.assertIn("trigonometry", scientific[0]["desc"])
        self.assertEqual(len(self.entries), len(self.search_slugs))

    def test_unfinished_routes_do_not_offer_unrelated_calculations(self):
        related = [next(c for c in self.calculators if c["slug"] == "compound-interest-calculator")]
        for slug in ("currency-calculator", "time-card-calculator", "tax-calculator"):
            with self.subTest(slug=slug):
                calc = next(c for c in self.calculators if c["slug"] == slug)
                html = build.calculator_page(self.data["site"], calc, related)
                self.assertIn("This calculator is currently unavailable.", html)
                self.assertIn('content="noindex,follow"', html)
                self.assertIn('href="/compound-interest-calculator/"', html)
                self.assertNotIn('data-engine=', html)
                self.assertNotIn('"SoftwareApplication"', html)

    def test_time_duration_release_is_discoverable(self):
        calc = next(c for c in self.calculators if c["slug"] == "time-duration-calculator")
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertIn(calc["slug"], self.search_slugs)
        html = build.calculator_page(self.data["site"], calc, [])
        self.assertIn('data-engine="time_duration"', html)
        self.assertIn('id="duration_start_time"', html)
        self.assertIn('id="duration_end_date"', html)
        self.assertNotIn('content="noindex,follow"', html)


if __name__ == "__main__":
    unittest.main()

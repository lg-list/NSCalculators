import sys
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class DiscoveryQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calculators = [
            c for c in build.base_and_supplemental(cls.data)
            if c["slug"] not in build.CALCULATOR_REDIRECTS and c["slug"] not in build.CATEGORY_PAGE_REDIRECTS
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

    def test_working_noindex_calculations_remain_represented(self):
        working_noindex = [
            c for c in self.calculators
            if build.has_purpose_built_calculation(c)
            and not build.is_indexable_calculator(c)
        ]
        self.assertTrue(working_noindex)
        shown_conversions = {
            build.conversion_search_signature(c) for c in self.calculators
            if c["slug"] in self.search_slugs and build.conversion_search_signature(c) is not None
        }
        for calc in working_noindex:
            if calc["slug"] not in self.search_slugs:
                signature = build.conversion_search_signature(calc)
                self.assertIsNotNone(signature, calc["slug"])
                self.assertIn(signature, shown_conversions, calc["slug"])

    def test_equivalent_conversion_has_one_primary_result(self):
        entries = [c for c in self.entries if c["title"].casefold() == "millimeters to rods calculator"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["slug"], "millimeters-to-rods-calculator")
        self.assertIn("Scientific Length Science", entries[0]["aliases"])
        self.assertIn("Body Height Health", entries[0]["aliases"])

    def test_indexable_conversion_is_preferred_independent_of_order(self):
        group = [c for c in self.calculators if c["title"].casefold() == "milligrams to grams calculator"]
        self.assertGreater(len(group), 1)
        for candidates in (group, list(reversed(group))):
            entries = [c for c in build.calculator_search_index(candidates) if c["slug"] != "scientific-calculator"]
            self.assertEqual([c["slug"] for c in entries], ["milligrams-to-grams-calculator"])

    def test_distinct_conversion_definitions_are_not_merged(self):
        original = next(c for c in self.calculators if c["slug"] == "millimeters-to-rods-calculator")
        for difference in ("factor", "target", "source"):
            with self.subTest(difference=difference):
                variant = deepcopy(original)
                variant["slug"] = "different-definition-calculator"
                fields = {f[0]: f for f in variant["inputs"]}
                if difference == "source":
                    fields["value"][1] = "Value in another unit"
                elif difference == "factor":
                    fields["factor"][3] *= 2
                else:
                    fields["target"][3] = "another unit"
                entries = build.calculator_search_index([original, variant])
                self.assertTrue({original["slug"], variant["slug"]} <= {c["slug"] for c in entries})

    def test_multiple_indexable_routes_stay_visible(self):
        original = deepcopy(next(c for c in self.calculators if c["slug"] == "millimeters-to-rods-calculator"))
        original["generated"] = False
        variant = deepcopy(original)
        variant["slug"] = "another-primary-converter"
        entries = build.calculator_search_index([original, variant])
        self.assertTrue({original["slug"], variant["slug"]} <= {c["slug"] for c in entries})

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

    def test_401k_uses_current_calculator_bundle_version(self):
        calc = next(c for c in self.calculators if c["slug"] == "401k-calculator")
        html = build.calculator_page(self.data["site"], calc, [])
        self.assertIn(f'<script src="/assets/calculator.js?v={build.ASSET_VERSION}">', html)
        self.assertNotIn('calculator.js?v=20260920a', html)


if __name__ == "__main__":
    unittest.main()

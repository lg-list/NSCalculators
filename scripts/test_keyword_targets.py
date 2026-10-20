import csv
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts.build_indexable_keyword_targets import SOURCE, keyword_targets


class CanonicalTargetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calculators = {c["slug"]: c for c in build.base_and_supplemental(build.read_data())}

    def row(self, slug, keyword="loan payment calculator"):
        return {"keyword": keyword, "url_path": f"/{slug}/", "seo_priority": "P3",
                "avg_monthly_searches": "50"}

    def test_redirect_sources_are_not_indexable_tools(self):
        for slug in build.CALCULATOR_REDIRECTS.keys() | build.CATEGORY_PAGE_REDIRECTS.keys():
            with self.subTest(slug=slug):
                self.assertFalse(build.is_indexable_calculator({"slug": slug, "generated": False}))

    def test_tool_redirect_targets_are_indexable_and_direct(self):
        for target in build.CALCULATOR_REDIRECTS.values():
            self.assertNotIn(target, build.CALCULATOR_REDIRECTS)
            self.assertTrue(build.is_indexable_calculator(self.calculators[target]), target)

    def test_category_imports_target_directories_not_individual_tools(self):
        expected = {"financial-calculator": "/financial-calculators/",
                    "fitness-and-health-calculator": "/health-calculators/",
                    "math-calculator": "/math-calculators/", "other-calculator": "/"}
        self.assertEqual({k: v[1] for k, v in build.CATEGORY_PAGE_REDIRECTS.items()}, expected)
        directory_paths = {f"/{build.slugify_cat(cat)}/" for cat in build.CATEGORY_ORDER} | {"/"}
        self.assertTrue(set(expected.values()) <= directory_paths)

    def test_keyword_alias_resolves_to_canonical_tool(self):
        targets = keyword_targets([self.row("loan-payment-calculator")], self.calculators)
        self.assertEqual(targets[0]["url_path"], "/loan-calculator/")
        self.assertEqual(targets[0]["keyword"], "loan payment calculator")

    def test_alias_and_destination_rows_have_one_target(self):
        targets = keyword_targets([self.row("loan-payment-calculator"), self.row("loan-calculator")], self.calculators)
        self.assertEqual(len(targets), 1)
        self.assertEqual(targets[0]["nonindexable_variants_excluded"], "1")

    def test_different_indexable_targets_remain_an_error(self):
        with self.assertRaisesRegex(ValueError, "found 2"):
            keyword_targets([self.row("loan-calculator"), self.row("mortgage-calculator")], self.calculators)

    def test_redirect_cycle_is_an_error(self):
        with patch.dict(build.CALCULATOR_REDIRECTS, {"loan-calculator": "loan-payment-calculator"}):
            with self.assertRaisesRegex(ValueError, "Redirect cycle"):
                keyword_targets([self.row("loan-payment-calculator")], self.calculators)

    def test_all_source_keywords_keep_one_indexable_canonical_target(self):
        with SOURCE.open(newline="", encoding="utf-8-sig") as source:
            rows = list(csv.DictReader(source))
        targets = keyword_targets(rows, self.calculators)
        normalize = lambda value: " ".join(value.casefold().split())
        self.assertEqual({normalize(r["keyword"]) for r in rows}, {normalize(r["keyword"]) for r in targets})
        self.assertEqual(len(targets), 174)
        for row in targets:
            self.assertTrue(build.is_indexable_calculator(self.calculators[row["url_path"].strip("/")]))


if __name__ == "__main__":
    unittest.main()

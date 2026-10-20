import csv
import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts.build_indexable_keyword_targets import SOURCE, keyword_targets


class KeywordProvenanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calculators = {c["slug"]: c for c in build.base_and_supplemental(build.read_data())}

    def test_current_stats_are_verified_china_not_us(self):
        metrics = build.load_google_keyword_metrics()
        self.assertEqual(len(metrics), 174)
        for record in metrics.values():
            self.assertEqual(record["country"], "CN")
            self.assertTrue(record["market_verified"])
            self.assertEqual(record["period_start"], "2025-08-01")
            self.assertEqual(record["period_end"], "2026-07-31")
            self.assertEqual(build.keyword_score({"keyword_data": record}), 0)

    def test_missing_or_changed_provenance_never_assumes_us(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            rows = [{"keyword": "example calculator", "volume": 100}]
            stats, metadata = root / "stats.json", root / "metadata.json"
            stats.write_text(json.dumps(rows), encoding="utf-8")
            with patch.object(build, "KEYWORD_STATS", stats), patch.object(build, "KEYWORD_STATS_PROVENANCE", metadata):
                record = build.load_google_keyword_metrics()["example-calculator"]
                self.assertEqual(record["country"], "unknown")
                self.assertEqual(build.keyword_score({"keyword_data": record}), 0)
                metadata.write_text(json.dumps({"country": "US", "normalized_data_sha256": build.keyword_data_fingerprint(rows)}), encoding="utf-8")
                record = build.load_google_keyword_metrics()["example-calculator"]
                self.assertEqual(record["country"], "US")
                self.assertEqual(build.keyword_score({"keyword_data": record}), 100)
                rows[0]["volume"] = 101
                stats.write_text(json.dumps(rows), encoding="utf-8")
                record = build.load_google_keyword_metrics()["example-calculator"]
                self.assertEqual(record["country"], "unknown")
                self.assertFalse(record["market_verified"])
                self.assertEqual(build.keyword_score({"keyword_data": record}), 0)

    def test_ads_competition_is_not_an_organic_difficulty_score(self):
        base = {"country": "US", "market_verified": True, "monthly_searches": 100}
        for competition in [0, 50, 100]:
            self.assertEqual(build.keyword_score({"keyword_data": dict(base, competition_index=competition, yoy="+100%")}), 100)
        self.assertEqual(build.keyword_score({"keyword_data": dict(base, country="CN", monthly_searches=10**9)}), 0)
        self.assertEqual(build.keyword_score({"keyword_data": dict(base, market_verified=False)}), 0)

    def test_homepage_features_reviewed_tools_not_china_volume_ranks(self):
        calculators = list(self.calculators.values())
        for items in (calculators, list(reversed(calculators))):
            selected = build.homepage_featured_calculators(items)
            self.assertEqual([c["slug"] for c in selected], list(build.HOME_FEATURED_SLUGS))
            self.assertEqual(len(selected), 12)
            self.assertTrue(all(build.is_indexable_calculator(c) and build.has_purpose_built_calculation(c) for c in selected))
        html = build.home_new(build.read_data()["site"], calculators)
        self.assertIn("Featured Calculators", html)
        self.assertNotIn("Most Popular Calculators", html)

    def test_mapping_countries_belong_to_the_mapping_source(self):
        with SOURCE.open(newline="", encoding="utf-8-sig") as source:
            rows = list(csv.DictReader(source))
        targets = keyword_targets(rows, self.calculators)
        self.assertEqual(len(targets), 174)
        for target in targets:
            self.assertEqual(target["search_volume_country"], "CN")
            self.assertEqual(target["us_avg_monthly_searches"], "")
            self.assertEqual(target["priority_scope"], "legacy_source_market_not_US")
        altered = deepcopy(rows)
        altered[0]["avg_monthly_searches"] = "123"
        changed = keyword_targets(altered, self.calculators)
        self.assertTrue(all(row["search_volume_country"] == "unknown" for row in changed))
        self.assertTrue(all(row["us_avg_monthly_searches"] == "" for row in changed))

    def test_reviewed_index_scope_is_not_driven_by_china_metrics(self):
        # Two mismatched financial models remain withheld; dedicated down payment is restored.
        self.assertEqual(sum(build.is_indexable_calculator(c) for c in self.calculators.values()), 283)

    def test_fingerprint_ignores_json_object_key_formatting(self):
        self.assertEqual(build.keyword_data_fingerprint([{"keyword": "a", "volume": 50}]),
                         build.keyword_data_fingerprint([{"volume": 50, "keyword": "a"}]))


if __name__ == "__main__":
    unittest.main()

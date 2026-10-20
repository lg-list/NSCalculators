import json
import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts.check_calculator_assets import check_assets


class CalculatorAssetTests(unittest.TestCase):
    def tearDown(self):
        build.calculator_assets.cache_clear()

    def test_version_matches_final_bundle_including_embedded_table(self):
        bundle, version = build.calculator_assets()
        self.assertNotIn("__RMD_JOINT_TABLE__", bundle)
        self.assertIn("const RMD_JOINT_TABLE=", bundle)
        self.assertEqual(version, sha256(bundle.encode("utf-8")).hexdigest()[:16])
        self.assertEqual(build.calculator_assets(), (bundle, version))

    def test_calculation_edit_changes_version(self):
        original = build.calculator_assets()[1]
        with patch.object(build, "CALC_JS", build.CALC_JS + "\n// calculation update\n"):
            build.calculator_assets.cache_clear()
            self.assertNotEqual(build.calculator_assets()[1], original)

    def test_embedded_data_edit_changes_version(self):
        original = build.calculator_assets()[1]
        with tempfile.TemporaryDirectory() as directory:
            table = Path(directory) / "table.json"
            table.write_text(json.dumps({"rows": {"72": [1]}}), encoding="utf-8")
            with patch.object(build, "RMD_JOINT_LIFE_TABLE", table):
                build.calculator_assets.cache_clear()
                self.assertNotEqual(build.calculator_assets()[1], original)

    def test_previously_pinned_pages_use_one_content_version(self):
        data = build.read_data()
        calculators = {c["slug"]: c for c in build.base_and_supplemental(data)}
        version = build.calculator_assets()[1]
        for slug in ("401k-calculator", "area-calculator", "amortization-calculator", "time-duration-calculator",
                     "towing-capacity-calculator", "rmd-calculator", "loan-calculator", "feet-to-meters-calculator"):
            with self.subTest(slug=slug):
                html = build.calculator_page(data["site"], calculators[slug], [])
                self.assertIn(f'/assets/calculator.js?v={version}', html)

    def test_build_checker_accepts_base_paths_and_rejects_stale_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            bundle = b"console.log('test');\n"
            (root / "assets" / "calculator.js").write_bytes(bundle)
            version = sha256(bundle).hexdigest()[:16]
            html = root / "index.html"
            html.write_text(f'<script src="/NSCalculators/assets/calculator.js?v={version}"></script>', encoding="utf-8")
            self.assertEqual(check_assets(root), (1, version))
            for query in ("v=old", "", f"v={version}&v=old"):
                html.write_text(f'<script src="/assets/calculator.js?{query}"></script>', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "does not match"):
                    check_assets(root)
            html.write_text("<p>No scripts</p>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No calculator"):
                check_assets(root)


if __name__ == "__main__":
    unittest.main()

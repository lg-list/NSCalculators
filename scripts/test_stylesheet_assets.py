import sys
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts.check_stylesheet_assets import check_stylesheets


class StylesheetAssetTests(unittest.TestCase):
    def tearDown(self):
        build.stylesheet_assets.cache_clear()

    def test_version_matches_exact_utf8_stylesheet_bytes(self):
        stylesheet, version = build.stylesheet_assets()
        self.assertEqual(stylesheet, build.CSS.strip() + "\n")
        self.assertEqual(version, sha256(stylesheet.encode("utf-8")).hexdigest()[:16])
        self.assertEqual(build.stylesheet_assets(), (stylesheet, version))

    def test_css_change_automatically_changes_version(self):
        original = build.stylesheet_assets()[1]
        with patch.object(build, "CSS", build.CSS + "\n.example{color:red}\n"):
            build.stylesheet_assets.cache_clear()
            self.assertNotEqual(build.stylesheet_assets()[1], original)

    def test_pinned_and_regular_pages_use_one_css_version(self):
        site = build.read_data()["site"]
        version = build.stylesheet_assets()[1]
        for slug in ("", "mortgage-calculator", "wheel-offset-calculator", "geodesic-dome-calculator",
                     "years-to-minutes-calculator", "watts-to-amps-calculator", "amps-to-watts-calculator",
                     "wire-size-calculator", "tire-size-calculator", "volume-calculator", "cd-calculator",
                     "roman-numeral-converter", "commission-calculator", "house-affordability-calculator",
                     "area-calculator", "conversion-calculator", "debt-payoff-calculator", "time-duration-calculator",
                     "body-fat-calculator", "about", "financial-calculators"):
            with self.subTest(slug=slug):
                html = build.page(site, "Test", "Description", f"/{slug}/" if slug else "/", "<main>Test</main>")
                self.assertIn(f'/assets/site.css?v={version}', html)

    def test_checker_accepts_base_paths_and_rejects_bad_versions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            stylesheet = b"body{color:red}\n"
            (root / "assets" / "site.css").write_bytes(stylesheet)
            version = sha256(stylesheet).hexdigest()[:16]
            html = root / "index.html"
            html.write_text(f'<link rel="stylesheet" href="/NSCalculators/assets/site.css?v={version}">', encoding="utf-8")
            self.assertEqual(check_stylesheets(root), (1, version))
            for query in ("v=20261002a", "", f"v={version}&v=old"):
                html.write_text(f'<link rel="stylesheet" href="/assets/site.css?{query}">', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "does not match"):
                    check_stylesheets(root)
            html.write_text('<link rel="preload" href="/assets/site.css">', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "No shared stylesheet"):
                check_stylesheets(root)

    def test_checker_detects_post_build_byte_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "assets").mkdir()
            stylesheet = b"body{color:red}\n"
            version = sha256(stylesheet).hexdigest()[:16]
            (root / "index.html").write_text(f'<link rel="stylesheet" href="/assets/site.css?v={version}">', encoding="utf-8")
            (root / "assets" / "site.css").write_bytes(stylesheet.replace(b"\n", b"\r\n"))
            with self.assertRaisesRegex(ValueError, "does not match"):
                check_stylesheets(root)


if __name__ == "__main__":
    unittest.main()

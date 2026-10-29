import tempfile
import unittest
from pathlib import Path
from hashlib import sha256
from scripts.check_calculator_assets import check_assets


class SpecializedAssets(unittest.TestCase):
    def test_area_asset_is_scoped_and_required(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'assets').mkdir()
            (root / 'area-calculator').mkdir()
            for name in ('calculator.js', 'calculator-area.js'):
                (root / 'assets' / name).write_bytes(b'example')
            tag = '<script src="/assets/calculator-area.js?v=' + sha256(b'example').hexdigest()[:16] + '"></script>'
            page = root / 'area-calculator/index.html'
            page.write_text(tag)
            self.assertEqual(check_assets(root)[0], 1)
            page.write_text(tag.replace('calculator-area.js', 'calculator.js'))
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                check_assets(root)
            page.write_text(tag)
            (root / 'index.html').write_text(tag)
            with self.assertRaisesRegex(ValueError, 'unsupported page'):
                check_assets(root)

    def test_specialized_scope_and_hash(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'assets').mkdir()
            (root / '401k-calculator').mkdir()
            full, special = b'full', b'special'
            (root / 'assets/calculator.js').write_bytes(full)
            (root / 'assets/calculator-401k.js').write_bytes(special)
            tag = '<script src="/assets/calculator-401k.js?v=' + sha256(special).hexdigest()[:16] + '"></script>'
            page = root / '401k-calculator/index.html'
            page.write_text(tag)
            self.assertEqual(check_assets(root)[0], 1)
            page.write_text(tag.replace(sha256(special).hexdigest()[:16], 'old'))
            with self.assertRaises(ValueError):
                check_assets(root)
            page.write_text(tag + tag)
            with self.assertRaisesRegex(ValueError, 'exactly one'):
                check_assets(root)
            page.write_text(tag)
            (root / 'index.html').write_text(tag)
            with self.assertRaisesRegex(ValueError, 'unsupported page'):
                check_assets(root)

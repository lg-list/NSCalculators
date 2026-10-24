import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class TipPageTests(unittest.TestCase):
    def test_tip_content_and_input_contract(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'tip-calculator')
        html = build.calculator_page(data['site'], calc, [])
        self.assertIn('id="people" type="number" min="1" step="1"', html)
        self.assertIn('id="bill" type="number" min="0" step="0.01"', html)
        self.assertIn('When a split leaves a penny', html)
        self.assertIn('One person pays $33.34 and two pay $33.33', html)
        self.assertIn('Tax and included service charges', html)
        self.assertIn('data-engine="cn_tip"', html)


if __name__ == '__main__':
    unittest.main()

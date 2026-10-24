import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class UsedCarValueTests(unittest.TestCase):
    def test_adjustments_are_explicit_and_current_future_intents_link(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        html = build.calculator_page(data['site'], calculators['used-car-value-calculator'], [])
        self.assertIn('id="condition_adjustment" type="number"', html)
        self.assertIn('Use 0 for matching condition', html)
        self.assertIn('Estimating a poor-condition car without double deductions', html)
        self.assertIn('$4,888 private-party and $4,576 trade-in', html)
        self.assertNotIn('built-in presets', html)
        self.assertIn('href="/car-resale-value-calculator/"', html)
        resale = build.calculator_page(data['site'], calculators['car-resale-value-calculator'], [])
        self.assertIn('current used car value estimator', resale)
        self.assertIn('does not apply a poor-condition discount', resale)


if __name__ == '__main__':
    unittest.main()

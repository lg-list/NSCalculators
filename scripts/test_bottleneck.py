import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class BottleneckTests(unittest.TestCase):
    def test_existing_page_explains_entered_ranges_without_claiming_a_frame_cap(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'bottleneck-calculator')
        html = build.calculator_page(data['site'], calc, [])
        for text in ('108-132 FPS', 'not a measured confidence interval',
                     '200 FPS exceeds a 144 FPS target by 56 FPS',
                     'not proof of a frame cap', 'does not contain a hardware model database',
                     'data-engine="bottleneck_advanced"'):
            self.assertIn(text, html)
        self.assertTrue(build.is_indexable_calculator(calc))


if __name__ == '__main__':
    unittest.main()

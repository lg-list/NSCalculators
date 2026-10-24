import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class SampleSizeTests(unittest.TestCase):
    def test_mean_inputs_sources_and_scope(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        page = build.calculator_page(data['site'], calculators['sample-size-calculator'], [])
        for token in ('id="sample_target"', 'id="sample_sd"', 'id="sample_mean_margin"',
                      '385 completed responses', '16 observations', '15.3664',
                      'handbook/ppc/section3/ppc333.htm', 'Known SD versus a pilot estimate',
                      'These modes do not estimate the sample size needed to measure SD itself.',
                      'href="/standard-deviation-calculator/"'):
            self.assertIn(token, page)
        self.assertNotIn('or a target for estimating a population mean', page)
        self.assertTrue(build.is_indexable_calculator(calculators['sample-size-calculator']))
        other = build.calculator_page(data['site'], calculators['standard-deviation-calculator'], [])
        self.assertIn('sample size calculator\'s mean mode', other)


if __name__ == '__main__':
    unittest.main()

import unittest
import build


class ComputeCharts(unittest.TestCase):
    def test_units_and_chart_scope(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        for slug in ('gpu-calculator', 'ai-compute-calculator'):
            html = build.analysis_extra_html(calculators[slug])
            self.assertNotIn('<canvas', html)
            self.assertIn('not shares of a combined total', html)
            self.assertIn('id="genericTable"', html)
            self.assertIn('id="genericSummary"', html)
        cost = build.analysis_extra_html(calculators['ai-cost-calculator'])
        self.assertIn('Input and Output Cost', cost)
        self.assertIn('data-chart-type="pie"', cost)
        self.assertIn('not an additional charge', cost)
        self.assertIn('data-chart-type="pie"', build.analysis_extra_html(calculators['simple-interest-calculator']))

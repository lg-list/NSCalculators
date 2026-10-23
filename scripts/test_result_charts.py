import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class ResultChartTests(unittest.TestCase):
    def test_energy_and_weight_charts_are_not_money_pies(self):
        calculators = build.base_and_supplemental(build.read_data())
        matching = [c for c in calculators if c.get("engine") in {"cn_calorie", "cn_body_metric"}]
        self.assertEqual(len(matching), 8)
        for calc in matching:
            with self.subTest(slug=calc["slug"]):
                html = build.analysis_extra_html(calc)
                self.assertIn('data-chart-type="bars"', html)
                self.assertNotIn('data-chart-type="pie"', html)
                self.assertIn('id="genericTable"', html)

    def test_dedicated_body_composition_pie_is_preserved(self):
        html = build.analysis_extra_html({"slug": "body-fat-calculator", "engine": "body_fat_advanced"})
        self.assertIn('data-chart-type="pie"', html)
        self.assertIn('data-value-format="percent"', html)


if __name__ == "__main__":
    unittest.main()

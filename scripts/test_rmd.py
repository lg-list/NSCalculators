import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class RmdPageTests(unittest.TestCase):
    def test_shared_verified_factor_data_and_lookup_table(self):
        source = json.loads(build.RMD_UNIFORM_LIFE_TABLE.read_text(encoding='utf-8'))
        fixture = json.loads((build.ROOT / 'exports/rmd-irs-factors-2026-10-27.json').read_text(encoding='utf-8'))
        self.assertEqual(source['rows'], fixture['uniform'])
        self.assertEqual(len(source['rows']), 49)
        self.assertEqual(source['rows']['75'], 24.6)
        self.assertEqual(build.rmd_uniform_table_html().count('<tr>'), 50)
        bundle, _ = build.calculator_assets()
        self.assertNotIn('__RMD_UNIFORM_FACTORS__', bundle)

    def test_existing_route_exposes_scope_and_current_year_table(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        calc = calculators['rmd-calculator']
        html = build.calculator_page(data['site'], calc, [])
        for text in ('id="rmd_birth_half"', 'data-rmd-spouse', 'Modeled funding gap',
                     'data-chart-type="bars"', '2026 RMD table', '2024 proposed clarification',
                     '2020 waiver', 'id="rmdUniformTable"', 'Own-account lifetime RMDs only'):
            self.assertIn(text, html)
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertIn('rmd table 2026', build.seo_keywords(calc))
        retirement = build.calculator_page(data['site'], calculators['retirement-calculator'], [])
        self.assertIn('RMD calculator and IRS factor table', retirement)


if __name__ == '__main__':
    unittest.main()

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class AreaRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_area_has_local_export_and_measurement_record_context(self):
        calc = self.calcs['area-calculator']
        html = build.calculator_page(self.data['site'], calc, [])
        for text in ('id="geo_export_sections"', 'aria-label="Download room total CSV"',
                     'id="geo_export_status"', 'original dimensions, units',
                     'Lucide download icon', 'ISC License'):
            self.assertIn(text, html)
        self.assertEqual(calc['engine'], 'area_advanced')
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertNotIn('downloadGeometryAreaSections', build.analysis_extra_html(self.calcs['mortgage-calculator']))


if __name__ == '__main__':
    unittest.main()

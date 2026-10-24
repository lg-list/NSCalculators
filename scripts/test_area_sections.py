import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class Buttons(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []

    def handle_starttag(self, tag, attrs):
        if tag == 'button':
            self.ids.append(dict(attrs).get('id'))


class AreaSectionTests(unittest.TestCase):
    def test_boundary_and_numerical_limits_are_explained(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'area-calculator')
        html = build.calculator_page(data['site'], calc, [])
        self.assertIn('no radial cut edges', html)
        self.assertIn('37.6991 feet, not 49.6991 feet', html)
        self.assertIn('https://people.eecs.berkeley.edu/~wkahan/Triangle.pdf', html)
        self.assertIn('cannot recover precision missing from the original measurements', html)

    def test_add_and_subtract_commands_share_existing_area_tool(self):
        data = build.read_data()
        calc = next(c for c in build.base_and_supplemental(data) if c['slug'] == 'area-calculator')
        html = build.calculator_page(data['site'], calc, [])
        parser = Buttons()
        parser.feed(html)
        self.assertEqual(parser.ids.count('geo_add_section'), 1)
        self.assertEqual(parser.ids.count('geo_subtract_section'), 1)
        self.assertTrue(build.is_indexable_calculator(calc))
        self.assertIn('deducting the same cutout twice', html)
        self.assertIn('calculate-square-footage-irregular-room', html)


if __name__ == '__main__':
    unittest.main()

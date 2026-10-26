import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            self.links.append(dict(attrs).get('href'))


class RoofAreaIntentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build.read_data()
        cls.calcs = {c['slug']: c for c in build.base_and_supplemental(cls.data)}

    def test_existing_pages_have_contextual_two_way_links_and_distinct_scope(self):
        for slug, destination, phrase in [
            ('square-footage-calculator', '/roof-pitch-calculator/', 'Roof square footage versus floor area'),
            ('roof-pitch-calculator', '/square-footage-calculator/', 'Roof square footage with a known pitch'),
        ]:
            calc = self.calcs[slug]
            html = build.calculator_page(self.data['site'], calc, [])
            parser = Links()
            parser.feed(html)
            self.assertTrue(build.is_indexable_calculator(calc))
            self.assertIn(destination, parser.links)
            self.assertIn(phrase, html)
            self.assertIn('1,341.64', html)
            self.assertIn('eaves', html)
            self.assertIn('pitch', html)

    def test_roof_content_explains_overhang_and_material_limits(self):
        html = build.calculator_page(self.data['site'], self.calcs['roof-pitch-calculator'], [])
        for text in ('does not enlarge the entered plan area automatically',
                     'not a bundle count', 'do not climb onto a roof',
                     'calculate each roof section', '/area-calculator/'):
            self.assertIn(text, html)
        self.assertNotIn('roof-square-footage-calculator', self.calcs)


if __name__ == '__main__':
    unittest.main()

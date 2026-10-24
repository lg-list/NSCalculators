import sys
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class Images(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == 'img':
            self.images.append(dict(attrs))


class RoomAreaGuideTests(unittest.TestCase):
    def test_diagram_geometry_matches_both_worked_methods(self):
        svg = ET.parse(build.ROOT / 'src/images/l-shaped-room-232-sq-ft.svg').getroot()
        rects = {element.attrib['id']: {key: float(element.attrib[key]) for key in ('x', 'y', 'width', 'height')}
                 for element in svg.iter('{http://www.w3.org/2000/svg}rect')}
        a, b, cutout = (rects[key] for key in ('section-a', 'section-b', 'cutout'))
        scale = (a['width'] + b['width']) / 20
        self.assertEqual(a['height'] / scale, 14)
        self.assertEqual(a['width'] / scale, 12)
        self.assertEqual(b['width'] / scale, 8)
        self.assertEqual(b['height'] / scale, 8)
        self.assertEqual(cutout['height'] / scale, 6)
        self.assertEqual(cutout['width'], b['width'])
        self.assertEqual(a['x'] + a['width'], b['x'])
        self.assertEqual(cutout['x'], b['x'])
        self.assertEqual(cutout['y'], a['y'])
        self.assertEqual(cutout['y'] + cutout['height'], b['y'])
        self.assertEqual(a['y'] + a['height'], b['y'] + b['height'])
        area = lambda rect: rect['width'] * rect['height'] / scale**2
        self.assertEqual((area(a), area(b), area(cutout)), (168, 64, 48))
        self.assertEqual(area(a) + area(b), 20 * 14 - area(cutout))
        self.assertEqual(area(a) + area(b), 232)
        self.assertEqual(svg.attrib['viewBox'], '0 0 360 350')
        self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}title'))
        self.assertIsNotNone(svg.find('{http://www.w3.org/2000/svg}desc'))

    def test_guide_has_accessible_sized_lazy_image_and_matching_table(self):
        page = build.info_pages(build.read_data()['site'])['/guides/calculate-square-footage-irregular-room/']
        parser = Images()
        parser.feed(page)
        images = [image for image in parser.images if 'l-shaped-room-232-sq-ft' in image.get('src', '')]
        self.assertEqual(len(images), 1)
        self.assertEqual(images[0]['width'], '360')
        self.assertEqual(images[0]['height'], '350')
        self.assertEqual(images[0]['loading'], 'lazy')
        self.assertIn('upper-right cutout', images[0]['alt'])
        self.assertIn('280 - 48', page)
        self.assertIn('168 + 64', page)
        self.assertIn('Clear the room total between methods', page)
        self.assertNotIn('content="noindex', page)


if __name__ == '__main__':
    unittest.main()

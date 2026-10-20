import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build


class ProseLinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div":
            if self.depth:
                self.depth += 1
            elif "prose" in attrs.get("class", "").split():
                self.depth = 1
        if tag == "a" and self.depth:
            self.links.append(attrs)

    def handle_endtag(self, tag):
        if tag == "div" and self.depth:
            self.depth -= 1


class MathClusterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        data = build.read_data()
        cls.calculators = {c["slug"]: c for c in build.base_and_supplemental(data)}
        cls.slugs = {"ratio-calculator", "fraction-calculator", "percent-calculator"}
        cls.pages = {slug: build.calculator_page(data["site"], cls.calculators[slug], []) for slug in cls.slugs}

    def test_contextual_links_connect_existing_indexable_tools(self):
        for slug, html in self.pages.items():
            with self.subTest(slug=slug):
                self.assertTrue(build.is_indexable_calculator(self.calculators[slug]))
                parser = ProseLinkParser()
                parser.feed(html)
                for target in self.slugs - {slug}:
                    matches = [link for link in parser.links if link.get("href") == f"/{target}/"]
                    self.assertEqual(len(matches), 1, (slug, target))
                    self.assertNotIn("nofollow", matches[0].get("rel", ""))
                self.assertNotIn('content="noindex,follow"', html)

    def test_ratio_example_distinguishes_part_and_whole(self):
        html = self.pages["ratio-calculator"]
        self.assertIn("<caption>Two-part ratio 2:3", html)
        self.assertIn('class="data-table ratio-conversion-table"', html)
        self.assertIn(".prose .ratio-conversion-table{table-layout:fixed;font-size:16px", build.CSS)
        self.assertIn("2/(2+3) = 2/5", html)
        self.assertIn("40%", html)
        self.assertIn("66.6667%", html)
        self.assertIn("2/10 = 1/5 = 20%", html)

    def test_percentage_example_uses_the_correct_denominator(self):
        html = self.pages["percent-calculator"]
        self.assertIn("X = 2, Y = 5", html)
        self.assertIn("Using Y = 3 answers the part-to-part question", html)
        self.assertIn("https://openstax.org/books/prealgebra-2e/pages/6-1-understand-percent", html)


if __name__ == "__main__":
    unittest.main()

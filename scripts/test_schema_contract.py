import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts.check_schema_contract import check_schema


class SchemaContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = 'https://nscalculators.com/'
        self.setup_pages()

    def setup_pages(self):
        urls = [self.site + part for part in ('', 'category/', 'tool/')]
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>', encoding='utf-8')
        for part, title in (('', 'Home'), ('category/', 'Category')):
            self.page(part, title, [{'@type': 'WebPage', 'url': self.site + part, 'description': 'Description'}], '<div id="tools"></div>')
        self.nodes = [
            {'@type': 'WebPage', 'url': self.site + 'tool/', 'description': 'Description'},
            {'@type': 'SoftwareApplication', 'name': 'Example Calculator', 'url': self.site + 'tool/', 'description': 'Description', 'applicationCategory': 'UtilitiesApplication', 'isAccessibleForFree': True, 'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'USD'}},
            {'@type': 'BreadcrumbList', 'itemListElement': [
                {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': self.site},
                {'@type': 'ListItem', 'position': 2, 'name': 'Category', 'item': self.site + 'category/#tools'},
                {'@type': 'ListItem', 'position': 3, 'name': 'Example Calculator', 'item': self.site + 'tool/'},
            ]},
        ]
        self.tool()

    def page(self, part, title, nodes, body='', graph=False):
        file = self.root / part / 'index.html'
        file.parent.mkdir(parents=True, exist_ok=True)
        blocks = [json.dumps({'@context': 'https://schema.org', '@graph': nodes})] if graph else [json.dumps({'@context': 'https://schema.org', **node}) for node in nodes]
        scripts = ''.join('<script type="application/ld+json">' + block + '</script>' for block in blocks)
        file.write_text(f'<html><head><link rel="canonical" href="{self.site}{part}"><meta name="description" content="Description">{scripts}</head><body><h1>{title}</h1>{body}</body></html>', encoding='utf-8')

    def tool(self, nodes=None, graph=False, body='<section class="calc"></section>'):
        self.page('tool/', 'Example Calculator', self.nodes if nodes is None else nodes, body, graph)

    def test_valid_flat_and_graph_payloads(self):
        expected = {'pages': 3, 'applications': 1, 'breadcrumb_items': 3, 'breadcrumb_lists': 1}
        self.assertEqual(check_schema(self.root), expected)
        self.tool(graph=True)
        self.assertEqual(check_schema(self.root), expected)

    def test_invalid_or_missing_json_fails(self):
        file = self.root / 'tool/index.html'
        original = file.read_text(encoding='utf-8')
        for bad in ('{', '{"bad":NaN}'):
            file.write_text(original.replace(json.dumps({'@context': 'https://schema.org', **self.nodes[0]}), bad), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Invalid JSON-LD'):
                check_schema(self.root)
        self.tool(nodes=self.nodes[1:])
        with self.assertRaisesRegex(ValueError, 'WebPage schema'):
            check_schema(self.root)

    def test_application_metadata_must_match_visible_tool(self):
        for key, value in (('name', 'Other Calculator'), ('url', self.site + 'other/'), ('description', 'Old description')):
            nodes = copy.deepcopy(self.nodes)
            nodes[1][key] = value
            self.tool(nodes)
            with self.assertRaisesRegex(ValueError, 'visible tool/metadata'):
                check_schema(self.root)

    def test_unsupported_application_category_fails(self):
        nodes = copy.deepcopy(self.nodes)
        nodes[1]['applicationCategory'] = 'CalculatorApplication'
        self.tool(nodes)
        with self.assertRaisesRegex(ValueError, 'Unsupported application category'):
            check_schema(self.root)

    def test_rating_and_inconsistent_free_offer_need_review(self):
        for change in ({'aggregateRating': {'ratingValue': 5}}, {'review': {'reviewBody': 'Great'}}, {'isAccessibleForFree': False}, {'offers': {'@type': 'Offer', 'price': 10, 'priceCurrency': 'USD'}}):
            nodes = copy.deepcopy(self.nodes)
            nodes[1].update(change)
            self.tool(nodes)
            with self.assertRaises(ValueError):
                check_schema(self.root)

    def test_breadcrumb_positions_and_endpoints(self):
        for index, change in ((1, {'position': 4}), (2, {'name': 'Other'}), (2, {'item': self.site + 'category/'})):
            nodes = copy.deepcopy(self.nodes)
            nodes[2]['itemListElement'][index].update(change)
            self.tool(nodes)
            with self.assertRaisesRegex(ValueError, 'Breadcrumb'):
                check_schema(self.root)

    def test_breadcrumb_targets_and_fragments(self):
        for item in (self.site + 'category/#missing', self.site + 'missing/', 'http://nscalculators.com/category/', 'https://old.example/category/', self.site + '%2e%2e/outside/'):
            nodes = copy.deepcopy(self.nodes)
            nodes[2]['itemListElement'][1]['item'] = item
            self.tool(nodes)
            with self.assertRaises(ValueError):
                check_schema(self.root)

    def test_calculator_application_and_breadcrumb_presence(self):
        for nodes in (self.nodes[:1] + self.nodes[2:], self.nodes[:2], self.nodes + [self.nodes[1]]):
            self.tool(nodes)
            with self.assertRaisesRegex(ValueError, 'Calculator needs one'):
                check_schema(self.root)
        self.tool(body='No calculator')
        with self.assertRaisesRegex(ValueError, 'visible calculator UI'):
            check_schema(self.root)

    def test_project_base_path(self):
        self.site = 'https://lg-list.github.io/NSCalculators/'
        self.setup_pages()
        self.assertEqual(check_schema(self.root, self.site)['applications'], 1)

    def test_current_calculator_builder_has_supported_category(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        for slug in ('area-calculator', 'mortgage-calculator', 'sample-size-calculator'):
            payload = build.calculator_schema(data['site'], calculators[slug])
            self.assertEqual(payload['applicationCategory'], 'UtilitiesApplication')
            self.assertNotIn('aggregateRating', payload)
            self.assertEqual(payload['description'], build.seo_description(calculators[slug]))


if __name__ == '__main__':
    unittest.main()

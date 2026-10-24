import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.check_indexation_contract import check_indexation


class IndexationContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.site = 'https://nscalculators.com/'
        self.paths = ['', 'category/', 'calculator/']
        self.sitemap()
        self.robots()
        self.page('', '<a href="category/#tools">Category</a>')
        self.page('category/', '<a href="../calculator/">Calculator</a>')
        self.page('calculator/')

    def sitemap(self, urls=None):
        urls = urls if urls is not None else [self.site + path for path in self.paths]
        (self.root / 'sitemap.xml').write_text('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{url}</loc></url>' for url in urls) + '</urlset>', encoding='utf-8')

    def robots(self, rules='Allow: /'):
        (self.root / 'robots.txt').write_text(f'User-agent: *\n{rules}\nSitemap: {self.site}sitemap.xml\n', encoding='utf-8')

    def page(self, path, body='', head=''):
        file = self.root / path / 'index.html'
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f'<html><head><link rel="canonical" href="{self.site}{path}"><meta name="description" content="Description">{head}</head><body>{body}</body></html>', encoding='utf-8')

    def test_relative_links_and_fragments_reach_every_page(self):
        self.assertEqual(check_indexation(self.root), {'sitemap_urls': 3, 'depths': {0: 1, 1: 1, 2: 1}, 'max_depth': 2})

    def test_indexing_exclusions_combine_across_tags(self):
        for head in ('<meta name="ROBOTS" content="index, NOINDEX">', '<meta name="googlebot" content="none">', '<meta name="robots" content="index"><meta name="googlebot" content="noindex">'):
            with self.subTest(head=head):
                self.page('calculator/', head=head)
                with self.assertRaisesRegex(ValueError, 'indexing exclusion'):
                    check_indexation(self.root)

    def test_missing_wrong_or_multiple_canonicals_fail(self):
        file = self.root / 'calculator/index.html'
        original = file.read_text(encoding='utf-8')
        canonical = f'<link rel="canonical" href="{self.site}calculator/">'
        for replacement in ('', canonical + canonical, '<link rel="canonical" href="https://old.example/">'):
            file.write_text(original.replace(canonical, replacement), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'self-canonical'):
                check_indexation(self.root)

    def test_noncanonical_unsafe_and_duplicate_sitemap_urls_fail(self):
        for url in ('http://nscalculators.com/calculator/', 'https://other.example/calculator/', self.site + 'calculator/#section', self.site + 'calculator/?x=1', self.site + '%2e%2e/calculator/', self.site + 'missing/'):
            with self.subTest(url=url):
                self.sitemap([self.site, url])
                with self.assertRaises(ValueError):
                    check_indexation(self.root)
        self.sitemap([self.site, self.site])
        with self.assertRaisesRegex(ValueError, 'unique'):
            check_indexation(self.root)

    def test_robots_blocks_and_unsupported_patterns_fail(self):
        for rules in ('Disallow: /calculator/', 'User-agent: Googlebot\nDisallow: /', 'Disallow: /*calculator*', 'Allow: /\nDisallow: /calculator/'):
            self.robots(rules)
            with self.assertRaises(ValueError):
                check_indexation(self.root)
        (self.root / 'robots.txt').write_text('User-agent: *\nAllow: /\nSitemap: https://old.example/sitemap.xml', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'canonical sitemap'):
            check_indexation(self.root)

    def test_nofollow_and_missing_links_do_not_prove_discovery(self):
        for body, head in (('', ''), ('<a rel="nofollow" href="../calculator/">Calculator</a>', ''), ('<a href="../calculator/">Calculator</a>', '<meta name="robots" content="nofollow">')):
            self.page('category/', body, head)
            with self.assertRaisesRegex(ValueError, 'unreachable'):
                check_indexation(self.root)
        self.page('category/', '<a href="../calculator/">Calculator</a>')
        with self.assertRaisesRegex(ValueError, 'beyond 1 clicks'):
            check_indexation(self.root, max_depth=1)

    def test_base_refresh_and_description_drift_fail(self):
        for head in ('<base href="https://elsewhere.example/">', '<meta http-equiv="Refresh" content="0;url=/">', '<meta name="description" content="Another">'):
            self.page('calculator/', head=head)
            with self.assertRaises(ValueError):
                check_indexation(self.root)

    def test_project_base_path_is_supported(self):
        self.site += 'NSCalculators/'
        self.sitemap()
        self.robots()
        for path in self.paths:
            self.page(path, '<a href="category/">Category</a>' if not path else '<a href="../calculator/">Tool</a>' if path == 'category/' else '')
        self.assertEqual(check_indexation(self.root, self.site)['max_depth'], 2)


if __name__ == '__main__':
    unittest.main()

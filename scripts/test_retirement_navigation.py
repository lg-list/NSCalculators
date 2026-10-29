import unittest
import build


class RetirementNavigationTests(unittest.TestCase):
    def test_task_links_are_in_explanatory_content(self):
        data = build.read_data()
        calculators = {c['slug']: c for c in build.base_and_supplemental(data)}
        routes = {
            '401k-calculator': ('ira-calculator', 'rmd-calculator'),
            'ira-calculator': ('401k-calculator', 'rmd-calculator'),
            'pension-calculator': ('ira-calculator', 'rmd-calculator'),
            'rmd-calculator': ('ira-calculator', '401k-calculator'),
        }
        for slug, targets in routes.items():
            with self.subTest(slug=slug):
                html = build.calculator_page(data['site'], calculators[slug], [])
                start = html.index('<h2>Continue your retirement estimate</h2>')
                end = html.index('<h2>Frequently asked questions</h2>', start)
                block = html[start:end]
                self.assertEqual(block.count('<a '), 2)
                for target in targets:
                    self.assertIn(f'href="/{target}/"', block)
                    self.assertTrue(build.is_indexable_calculator(calculators[target]))
                self.assertNotIn(f'href="/{slug}/"', block)
                self.assertEqual(html.count('<h1'), 1)


if __name__ == '__main__':
    unittest.main()

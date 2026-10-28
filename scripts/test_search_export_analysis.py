import copy
import unittest
from datetime import date, timedelta
from unittest.mock import patch
import analyze_us_search_exports as analysis


class SearchExportAnalysisTests(unittest.TestCase):
    def fixtures(self):
        start, end = date(2026, 9, 28), date(2026, 10, 25)
        header = ['Key', 'Clicks', 'Impressions', 'CTR', 'Position']
        filters = [['过滤器', '值'], ['国家/地区', '美国'], ['搜索类型', '网页（基于文本）'], ['日期', '2026年9月28日-2026年10月25日']]
        single = {'filters': filters, 'dates': [header]+[[(start+timedelta(days=i)).isoformat(), '3' if i == 27 else '0', '10', '0%', '54.4'] for i in range(28)],
                  'countries': [header, ['美国', '3', '280', '1%', '54.4']], 'devices': [header, ['桌面', '3', '280', '1%', '54.4']],
                  'queries': [header, ['area calculator', '0', '5', '0%', '8']],
                  'pages': [header, ['https://nscalculators.com/area-calculator/', '0', '5', '0%', '8']]}
        h = ['Key', '2026/9/28 - 2026/10/25 Clicks', '2026/8/31 - 2026/9/27 Clicks', 'Current impressions', 'Prior impressions', 'Current CTR', 'Prior CTR', 'Current position', 'Prior position']
        comparison = {'filters': copy.deepcopy(filters), 'countries': [h, ['美国', '3', '2', '280', '100', '1%', '2%', '54.4', '64']],
                      'devices': [h, ['桌面', '3', '2', '280', '100', '1%', '2%', '54.4', '64']],
                      'queries': [h, ['area calculator', '0', '0', '5', '0', '0%', '0%', '8', '0']],
                      'pages': [h, ['https://nscalculators.com/area-calculator/', '0', '0', '5', '0', '0%', '0%', '8', '0']]}
        return single, comparison, start, end

    def run_analysis(self, single, comparison, start, end):
        with patch.object(analysis, 'read_zip', side_effect=[(single, {'sha256': 'single'}), (comparison, {'sha256': 'comparison'})]):
            return analysis.analyze('single.zip', 'comparison.zip', start, end)

    def test_reconciles_counts_preserves_incomplete_detail_and_does_not_mutate_sources(self):
        s, c, start, end = self.fixtures()
        original = copy.deepcopy((s, c))
        out = self.run_analysis(s, c, start, end)
        self.assertEqual(out['current_period']['impressions'], 280)
        self.assertEqual(out['prior_period']['clicks'], 2)
        self.assertEqual(out['changes']['clicks_absolute'], 1)
        self.assertAlmostEqual(out['current_period']['ctr_percent_calculated'], 100*3/280)
        self.assertEqual(out['row_totals_not_site_totals']['queries']['clicks'], 0)
        self.assertIsNone(out['selected_query_comparisons'][0]['prior_position'])
        self.assertEqual((s, c), original)

    def test_rejects_wrong_country(self):
        s, c, start, end = self.fixtures(); s['filters'][1][1] = '中国'
        with self.assertRaisesRegex(ValueError, 'USA'): self.run_analysis(s, c, start, end)

    def test_rejects_duplicate_daily_date_even_if_totals_match(self):
        s, c, start, end = self.fixtures(); s['dates'][2][0] = s['dates'][1][0]
        with self.assertRaisesRegex(ValueError, 'daily dates'): self.run_analysis(s, c, start, end)

    def test_rejects_device_total_mismatch(self):
        s, c, start, end = self.fixtures(); s['devices'][1][2] = '281'
        with self.assertRaisesRegex(ValueError, 'total mismatch'): self.run_analysis(s, c, start, end)

    def test_rejects_overlapping_comparison_period(self):
        s, c, start, end = self.fixtures(); c['queries'][0] = list(c['queries'][0]); c['queries'][0][2] = '2026/9/24 - 2026/10/21 Clicks'
        with self.assertRaisesRegex(ValueError, 'Comparison dates'): self.run_analysis(s, c, start, end)

    def test_rejects_changed_counts_across_same_window_exports(self):
        s, c, start, end = self.fixtures(); c['queries'][1][3] = '6'
        with self.assertRaisesRegex(ValueError, 'Changed counts'): self.run_analysis(s, c, start, end)

    def test_rejects_duplicate_page_keys(self):
        s, c, start, end = self.fixtures(); s['pages'].append(list(s['pages'][1]))
        with self.assertRaisesRegex(ValueError, 'Duplicate'): self.run_analysis(s, c, start, end)

    def test_rejects_unexpected_page_domains(self):
        s, c, start, end = self.fixtures(); s['pages'][1][0] = 'https://other.example/private'
        with self.assertRaisesRegex(ValueError, 'page URL'): self.run_analysis(s, c, start, end)


if __name__ == '__main__':
    unittest.main()

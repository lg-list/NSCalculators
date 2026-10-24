import csv
import io
import sys
import tempfile
import unittest
import zipfile
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.audit_gsc_export import audit_export

URL = 'https://search.google.com/u/1/search-console/performance/search-analytics?resource_id=sc-domain%3Anscalculators.com&time_granularity=DAY&start_date=20200101&end_date=20200102&country=usa'
HEADER = ['Clicks', 'Impressions', 'CTR', 'Position']
TABLES = {
    'dates': [['Date', *HEADER], ['2020-01-01', '1', '10', '10%', '12'], ['2020-01-02', '0', '20', '0%', '14']],
    'queries': [['Top queries', *HEADER], ['area calculator', '0', '10', '0%', '8']],
    'pages': [['Top pages', *HEADER], ['https://nscalculators.com/area-calculator/', '1', '15', '6.67%', '10']],
    'countries': [['Country', *HEADER], ['United States', '1', '30', '3.33%', '13.3']],
    'devices': [['Device', *HEADER], ['Desktop', '1', '30', '3.33%', '13.3']],
    'filters': [['Filters', 'Value'], ['Search type', 'Web'], ['Date', '2020-01-01 - 2020-01-02'], ['Country', 'United States']],
}


class GscExportTests(unittest.TestCase):
    def audit(self, tables=None, url=URL):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'report.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                for name, rows in (tables or TABLES).items():
                    text = io.StringIO(newline='')
                    csv.writer(text).writerows(rows)
                    archive.writestr(name + '.csv', text.getvalue().encode('utf-8-sig'))
            return audit_export(path, url)

    def test_totals_reconcile_without_manufacturing_pairs_or_market_volume(self):
        result = self.audit()
        self.assertEqual(result['totals']['clicks'], 1)
        self.assertEqual(result['totals']['impressions'], 30)
        self.assertEqual(result['totals']['days'], 2)
        self.assertAlmostEqual(result['totals']['ctr_percent_calculated'], 100 / 30)
        self.assertIsNone(result['us_monthly_market_search_volume'])
        self.assertEqual(result['row_totals_vs_site']['queries']['clicks'], 0)
        self.assertEqual(result['row_totals_vs_site']['pages']['impressions_row_to_site_ratio'], .5)
        self.assertNotIn('page', result['near_page_one_queries'][0])
        self.assertEqual(len(result['source_sha256']), 64)

    def test_wrong_geography_is_rejected(self):
        for country in ['China', 'Worldwide', 'Unknown']:
            data = deepcopy(TABLES)
            data['filters'][-1][1] = country
            data['countries'][1][0] = country
            with self.subTest(country=country), self.assertRaises(ValueError):
                self.audit(data)
        with self.assertRaises(ValueError):
            self.audit(url=URL.replace('&country=usa', ''))

    def test_property_and_additional_filters_are_checked(self):
        data = deepcopy(TABLES)
        data['pages'][1][0] = 'https://other.example/area/'
        with self.assertRaises(ValueError):
            self.audit(data)
        for url in [URL.replace('nscalculators.com', 'other.example'), URL + '&query=area', URL + '&query=', URL + '&start_date=20200101', URL.replace('DAY', 'HOUR'), URL.replace('search-analytics?', 'search-analytics/ai?')]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                self.audit(url=url)

    def test_gaps_duplicates_and_contradictory_aggregates_are_rejected(self):
        for problem in ['gap', 'duplicate', 'device_total', 'date_filter']:
            data = deepcopy(TABLES)
            if problem == 'gap':
                data['dates'].pop()
            elif problem == 'duplicate':
                data['dates'].append(data['dates'][1])
            elif problem == 'device_total':
                data['devices'][1][2] = '99'
            else:
                data['filters'][2][1] = '2020-01-01 - 2020-01-03'
            with self.subTest(problem=problem), self.assertRaises(ValueError):
                self.audit(data)

    def test_missing_and_invalid_metrics_do_not_turn_into_zero(self):
        for value in ['', '-', '-1', 'NaN', '1.5']:
            data = deepcopy(TABLES)
            data['dates'][1][1] = value
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.audit(data)
        data = deepcopy(TABLES)
        del data['pages']
        with self.assertRaises(ValueError):
            self.audit(data)
        data = deepcopy(TABLES)
        data['queries'][1][0] = ''
        with self.assertRaises(ValueError):
            self.audit(data)

    def test_unexpected_or_duplicate_export_filters_are_rejected(self):
        for extra in [['Query', 'area'], ['Country', 'United States']]:
            data = deepcopy(TABLES)
            data['filters'].append(extra)
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                self.audit(data)


if __name__ == '__main__':
    unittest.main()

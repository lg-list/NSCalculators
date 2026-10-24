"""Validate a full-site US Search Console CSV export without altering raw data."""
import argparse
import csv
import hashlib
import io
import json
import math
import re
import zipfile
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

TABLES = {
    'Date': 'dates', '\u65e5\u671f': 'dates',
    'Top queries': 'queries', '\u70ed\u95e8\u67e5\u8be2': 'queries',
    'Top pages': 'pages', '\u6392\u540d\u9760\u524d\u7684\u7f51\u9875': 'pages',
    'Country': 'countries', '\u56fd\u5bb6/\u5730\u533a': 'countries',
    'Device': 'devices', '\u8bbe\u5907': 'devices',
    'Filters': 'filters', '\u8fc7\u6ee4\u5668': 'filters',
}
FILTERS = {'Search type': 'type', '\u641c\u7d22\u7c7b\u578b': 'type', 'Date': 'dates', '\u65e5\u671f': 'dates', 'Country': 'country', '\u56fd\u5bb6/\u5730\u533a': 'country'}
METRICS = [('Clicks', '\u70b9\u51fb\u6b21\u6570'), ('Impressions', '\u5c55\u793a'), ('CTR', '\u70b9\u51fb\u7387'), ('Position', '\u6392\u540d')]
US_NAMES = {'united states', 'usa', 'us', '\u7f8e\u56fd'}
WEB_NAMES = {'web', 'web (text-based)', '\u7f51\u9875\uff08\u57fa\u4e8e\u6587\u672c\uff09'}


def metric_rows(rows):
    header = rows[0]
    if len(set(header)) != len(header):
        raise ValueError('Duplicate metric headers')
    columns = [next((header.index(name) for name in names if name in header), None) for names in METRICS]
    if any(column is None for column in columns):
        raise ValueError('Missing metric columns')
    result = []
    for row in rows[1:]:
        if len(row) != len(header):
            raise ValueError('Malformed CSV row')
        if not row[0].strip():
            raise ValueError('Missing dimension key')
        clicks, impressions, ctr, position = [row[column].strip() for column in columns]
        if not re.fullmatch(r'\d+', clicks) or not re.fullmatch(r'\d+', impressions):
            raise ValueError('Counts must be nonnegative integers')
        record = {'key': row[0], 'clicks': int(clicks), 'impressions': int(impressions), 'ctr_percent_reported': float(ctr.removesuffix('%')), 'position': float(position)}
        if not all(math.isfinite(record[key]) and record[key] >= 0 for key in ('ctr_percent_reported', 'position')):
            raise ValueError('Invalid rate or position')
        if record['impressions'] > 0 and record['position'] <= 0:
            raise ValueError('Positive impressions require a positive position')
        result.append(record)
    if len({row['key'] for row in result}) != len(result):
        raise ValueError('Duplicate dimension keys')
    return result


def totals(rows):
    return {key: sum(row[key] for row in rows) for key in ('clicks', 'impressions')}


def audit_export(path, report_url):
    path = Path(path)
    url = urlsplit(report_url)
    parameters = parse_qs(url.query, keep_blank_values=True)
    if url.scheme != 'https' or url.hostname != 'search.google.com' or not re.fullmatch(r'/(?:u/\d+/)?search-console/performance/search-analytics', url.path):
        raise ValueError('Use the observed Search Console performance report URL')
    if parameters.get('resource_id') != ['sc-domain:nscalculators.com'] or parameters.get('country') != ['usa']:
        raise ValueError('Expected the NS Calculators domain property with a US filter')
    if parameters.get('last_24_hours') == ['true'] or parameters.get('time_granularity') != ['DAY']:
        raise ValueError('Use a completed daily date range, not partial hourly data')
    allowed = {'resource_id', 'country', 'time_granularity', 'start_date', 'end_date'}
    if set(parameters) - allowed:
        raise ValueError('Additional report filters require a separate scoped analysis')
    if not {'start_date', 'end_date'} <= parameters.keys() or any(len(values) != 1 for values in parameters.values()):
        raise ValueError('Report parameters must contain one explicit date range')
    start = date.fromisoformat(parameters['start_date'][0])
    end = date.fromisoformat(parameters['end_date'][0])
    if start > end or end >= date.today():
        raise ValueError('Use a completed historical interval')
    tables, source_files, raw_filters = {}, {}, None
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith('.csv'):
                continue
            raw = archive.read(name)
            rows = list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))))
            kind = TABLES.get(rows[0][0]) if rows and rows[0] else None
            if kind is None:
                continue
            if kind in source_files:
                raise ValueError('Duplicate source table')
            source_files[kind] = {'name': name, 'sha256': hashlib.sha256(raw).hexdigest(), 'rows': len(rows) - 1}
            if kind == 'filters':
                raw_filters = rows[1:]
            else:
                tables[kind] = metric_rows(rows)
    if set(tables) != {'dates', 'queries', 'pages', 'countries', 'devices'} or raw_filters is None:
        raise ValueError('Export is missing required source tables')
    filters = {}
    for row in raw_filters:
        if len(row) != 2 or row[0] not in FILTERS or FILTERS[row[0]] in filters:
            raise ValueError('Unknown, extra or duplicate export filter')
        filters[FILTERS[row[0]]] = row[1]
    if set(filters) != {'type', 'dates', 'country'} or filters['country'].casefold() not in US_NAMES or filters['type'].casefold() not in WEB_NAMES:
        raise ValueError('Export filters must be US, Web and the explicit date interval only')
    expected_dates = [start.year, start.month, start.day, end.year, end.month, end.day]
    if [int(part) for part in re.findall(r'\d+', filters['dates'])] != expected_dates:
        raise ValueError('Export date filter does not match the observed URL; unsupported locale or wrong range')
    dates = {date.fromisoformat(row['key']) for row in tables['dates']}
    if dates != {start + timedelta(days=i) for i in range((end - start).days + 1)}:
        raise ValueError('Daily rows must cover the complete interval exactly')
    if len(tables['countries']) != 1 or tables['countries'][0]['key'].casefold() not in US_NAMES:
        raise ValueError('Country rows do not independently confirm the US-only scope')
    for row in tables['pages']:
        host = urlsplit(row['key']).hostname
        if not host or not (host == 'nscalculators.com' or host.endswith('.nscalculators.com')):
            raise ValueError('Page belongs to another property')
    overall = totals(tables['dates'])
    if totals(tables['countries']) != overall or totals(tables['devices']) != overall:
        raise ValueError('Daily, country and device aggregates do not reconcile')
    coverage = {}
    for kind in ('queries', 'pages'):
        subtotal = totals(tables[kind])
        coverage[kind] = {**subtotal, **{key + '_row_to_site_ratio': subtotal[key] / overall[key] if overall[key] else None for key in overall}, 'rows': len(tables[kind])}
    shortlist = [row for row in tables['queries'] if row['impressions'] >= 8 and 3 <= row['position'] <= 30]
    return {
        'source': 'Google Search Console browser CSV export', 'report_url': report_url,
        'source_filename': path.name, 'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'source_tables': source_files,
        'site': 'sc-domain:nscalculators.com', 'country': 'usa', 'search_type': 'web_unspecified' if filters['type'].casefold() == 'web' else 'web_text_based', 'search_type_source_label': filters['type'], 'period_start': start.isoformat(), 'period_end': end.isoformat(),
        'totals': {**overall, 'ctr_percent_calculated': 100 * overall['clicks'] / overall['impressions'] if overall['impressions'] else None, 'position_reported': tables['countries'][0]['position'], 'days': len(dates)},
        'row_totals_vs_site': coverage, 'query_rows_at_export_limit': len(tables['queries']) >= 1000,
        'near_page_one_queries': sorted(shortlist, key=lambda row: -row['impressions']),
        'page_rows': sorted(tables['pages'], key=lambda row: -row['impressions'])[:20],
        'devices': tables['devices'], 'us_monthly_market_search_volume': None,
        'limitations': ['Separate query/page tables are not query-page pairs.', 'Named rows are incomplete; missing rows are not zero.', 'Clicks are not sessions or visitors.', 'This lagged interval cannot measure releases after its end date.', 'Daily/country/device totals reconcile here; page/property aggregation and table limits prevent treating row ratios as exact completeness measures.', 'Google exports unavailable placeholders as zeros; the CSV alone cannot distinguish every such value from a real zero.'],
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('archive')
    parser.add_argument('--report-url', required=True)
    parser.add_argument('--output')
    args = parser.parse_args()
    summary = audit_export(args.archive, args.report_url)
    text = json.dumps(summary, indent=2, ensure_ascii=True) + '\n'
    if args.output:
        Path(args.output).write_text(text, encoding='utf-8')
    else:
        print(text, end='')

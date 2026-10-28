"""Read untouched GSC CSV ZIPs; write an aggregate JSON, never raw/account data."""
import argparse
import csv
import hashlib
import io
import json
import re
import zipfile
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urlparse

TABLES = {'dates': '图表.csv', 'queries': '查询数.csv', 'pages': '网页.csv',
          'countries': '国家_地区.csv', 'devices': '设备.csv', 'filters': '过滤器.csv'}
PUBLIC_QUERIES = {'area calculator', 'trade-in calculator', '401k calculator', 'calculate 401k',
                  'trade in value calculator', 'personal loan calculator', 'trade in car values calculator',
                  'trade in car calculator', 'boat loan calculator', 'new vs used car calculator',
                  'fuel cost calculator', 'car price estimate', '0.54 g to mcg',
                  '356442 seconds to hours minutes and seconds', '401k matching calculator',
                  '401 k employer match calculator', '401k calculator with match',
                  'tiered 401k match calculator', '401k safe harbor match calculator',
                  '401k cash out calculator', '401k early withdrawal calculator'}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def read_zip(path):
    raw = Path(path).read_bytes()
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        tables = {name: list(csv.reader(io.StringIO(archive.read(filename).decode('utf-8-sig'))))
                  for name, filename in TABLES.items() if filename in archive.namelist()}
        provenance = {name: {'filename': TABLES[name], 'sha256': hashlib.sha256(archive.read(TABLES[name])).hexdigest(),
                             'rows': len(rows)-1} for name, rows in tables.items()}
    return tables, {'filename': Path(path).name, 'sha256': hashlib.sha256(raw).hexdigest(), 'tables': provenance}


def date_tokens(text):
    return [date(int(y), int(m), int(d)) for y, m, d in re.findall(r'(\d{4})[年/-](\d{1,2})[月/-](\d{1,2})', text)]


def check_scope(tables, start, end):
    require(set(tables['filters'][0]) == {'过滤器', '值'}, 'Unknown filter headers')
    filters = dict(tables['filters'][1:])
    require(len(filters) == 3 and filters.get('国家/地区') == '美国', 'Expected USA only, without query/page filters')
    require(filters.get('搜索类型') == '网页（基于文本）', 'Expected text-based Web search')
    require(date_tokens(filters.get('日期', '')) == [start, end], 'Date scope mismatch')


def nonnegative(value):
    n = int(value)
    require(n >= 0, 'Negative search counts')
    return n


def metrics(row):
    clicks, impressions = nonnegative(row[1]), nonnegative(row[2])
    return {'key': row[0], 'clicks': clicks, 'impressions': impressions,
            'ctr_percent_calculated': 100*clicks/impressions if impressions else None,
            'position_reported': float(row[4]) if impressions else None}


def totals(rows, click_column=1, impression_column=2):
    return {'clicks': sum(nonnegative(r[click_column]) for r in rows),
            'impressions': sum(nonnegative(r[impression_column]) for r in rows)}


def analyze(single_path, comparison_path, start, end):
    require((end-start).days == 27, 'Expected 28 completed days')
    prior_end, prior_start = start-timedelta(days=1), start-timedelta(days=28)
    single, single_source = read_zip(single_path)
    comparison, comparison_source = read_zip(comparison_path)
    check_scope(single, start, end)
    check_scope(comparison, start, end)
    dates = single['dates'][1:]
    require(len(dates) == 28 and sorted(date.fromisoformat(r[0]) for r in dates) == [start+timedelta(days=i) for i in range(28)], 'Missing/duplicate daily dates')
    require(len(single['countries'][1:]) == len(comparison['countries'][1:]) == 1, 'Expected one country')
    require(single['countries'][1][0] == comparison['countries'][1][0] == '美国', 'Expected USA country row')
    current = totals(dates)
    require(totals(single['countries'][1:]) == current == totals(single['devices'][1:]), 'Single-window total mismatch')
    for table in ('queries', 'pages', 'countries', 'devices'):
        header = comparison[table][0]
        require(len(header) == 9 and date_tokens(header[1]) == [start, end] and date_tokens(header[2]) == [prior_start, prior_end], 'Comparison dates/columns mismatch')
    prior = totals(comparison['countries'][1:], 2, 4)
    require(totals(comparison['countries'][1:], 1, 3) == current == totals(comparison['devices'][1:], 1, 3), 'Comparison current totals mismatch')
    require(totals(comparison['devices'][1:], 2, 4) == prior, 'Prior country/device total mismatch')
    current['position_reported'] = float(comparison['countries'][1][7])
    prior['position_reported'] = float(comparison['countries'][1][8])
    for item in (current, prior):
        item['ctr_percent_calculated'] = 100*item['clicks']/item['impressions'] if item['impressions'] else None
        item['daily_clicks_calculated'] = item['clicks']/28
    query_rows = [metrics(r) for r in single['queries'][1:]]
    page_rows = [metrics(r) for r in single['pages'][1:]]
    require(all(urlparse(r['key']).scheme == 'https' and urlparse(r['key']).netloc == 'nscalculators.com'
                and not urlparse(r['key']).query for r in page_rows), 'Unexpected/private page URL')
    for tables in (single, comparison):
        for name in ('queries', 'pages'):
            require(len({r[0] for r in tables[name][1:]}) == len(tables[name])-1, 'Duplicate query/page keys')
    row_totals = {name: totals(single[name][1:]) for name in ('queries', 'pages')}
    for name in row_totals:
        row_totals[name]['rows'] = len(single[name])-1
    selected_comparison = []
    for row in comparison['queries'][1:]:
        if row[0] in PUBLIC_QUERIES:
            selected_comparison.append({'query': row[0], 'current_clicks': nonnegative(row[1]), 'prior_clicks': nonnegative(row[2]),
                                        'current_impressions': nonnegative(row[3]), 'prior_impressions_exported': nonnegative(row[4]),
                                        'current_position': float(row[7]) if int(row[3]) else None,
                                        'prior_position': float(row[8]) if int(row[4]) else None})
    single_queries = {r[0]: (r[1], r[2]) for r in single['queries'][1:]}
    compared_queries = {r[0]: (r[1], r[3]) for r in comparison['queries'][1:]}
    require(all(compared_queries.get(k) == v for k, v in single_queries.items()), 'Changed counts for overlapping query rows')
    return {'schema_version': 1, 'source': 'Untouched Google Search Console browser CSV ZIP exports',
            'property': 'sc-domain:nscalculators.com', 'country': 'usa', 'search_type': 'web_text_based',
            'current_period': {'start': start.isoformat(), 'end': end.isoformat(), 'days': 28, **current},
            'prior_period': {'start': prior_start.isoformat(), 'end': prior_end.isoformat(), 'days': 28, **prior},
            'changes': {'impressions_absolute': current['impressions']-prior['impressions'],
                        'impressions_percent': 100*(current['impressions']/prior['impressions']-1) if prior['impressions'] else None,
                        'clicks_absolute': current['clicks']-prior['clicks'],
                        'ctr_percentage_points': current['ctr_percent_calculated']-prior['ctr_percent_calculated']},
            'sources': {'single': single_source, 'comparison': comparison_source},
            'row_totals_not_site_totals': row_totals,
            'comparison_row_totals_not_site_totals': {name: {'current': totals(comparison[name][1:], 1, 3), 'prior': totals(comparison[name][1:], 2, 4), 'union_rows': len(comparison[name])-1} for name in ('queries', 'pages')},
            'single_query_rows_at_1000': len(query_rows) == 1000,
            'selected_query_comparisons': selected_comparison,
            'page_rows': page_rows,
            'devices': [metrics(r) for r in single['devices'][1:]],
            'daily_rows': [{'date': r[0], 'clicks': int(r[1]), 'impressions': int(r[2]), 'position_reported': float(r[4])} for r in dates],
            'limitations': ['Clicks are not visitors or GA4 sessions. The daily-1000-visit objective is unproven.',
                            'Comparison windows are equal and non-overlapping. The older October 24 baseline overlaps the current window and is not a valid before/after control.',
                            'Query and page tables are separate aggregates. No query/page pairs are inferred from them.',
                            'Single query detail hits 1000 rows. Comparison union has a different row scope and is not proof of complete named-query coverage.',
                            'Exported zero impressions/positions in comparison can represent unavailable detail, not a proven newly gained/lost query.',
                            'Average position changes with query mix. Three versus two clicks is too small to establish a reliable treatment effect.',
                            'This window ends before the October 27-28 repairs. Most recent releases cannot be evaluated with it.',
                            'Observed site impressions are not US monthly market search volume. Raw archives and account identifiers are not published.']}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('single', type=Path)
    parser.add_argument('comparison', type=Path)
    parser.add_argument('--start', type=date.fromisoformat, required=True)
    parser.add_argument('--end', type=date.fromisoformat, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(args.output.suffix.lower() == '.json' and args.output.resolve() not in (args.single.resolve(), args.comparison.resolve()), 'Output must be a separate JSON file, never an input archive')
    output = analyze(args.single, args.comparison, args.start, args.end)
    args.output.write_text(json.dumps(output, ensure_ascii=True, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({key: output[key] for key in ('current_period', 'prior_period', 'changes')}, indent=2))

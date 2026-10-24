"""Check this site's static JSON-LD contract, not Google rich-result eligibility."""
import argparse
from collections import Counter
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
APP_CATEGORIES = {
    'GameApplication', 'SocialNetworkingApplication', 'TravelApplication',
    'ShoppingApplication', 'SportsApplication', 'LifestyleApplication',
    'BusinessApplication', 'DesignApplication', 'DeveloperApplication',
    'DriverApplication', 'EducationalApplication', 'HealthApplication',
    'FinanceApplication', 'SecurityApplication', 'BrowserApplication',
    'CommunicationApplication', 'DesktopEnhancementApplication',
    'EntertainmentApplication', 'MultimediaApplication', 'HomeApplication',
    'UtilitiesApplication', 'ReferenceApplication',
}


class SchemaSignals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.blocks, self.ids, self.h1s, self.canonicals, self.descriptions = [], set(), [], [], []
        self.capture = None
        self.heading = None
        self.calculator = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if 'calc' in attrs.get('class', '').split():
            self.calculator = True
        if tag == 'h1':
            self.heading = []
        if tag == 'link' and 'canonical' in attrs.get('rel', '').split():
            self.canonicals.append(attrs.get('href'))
        if tag == 'meta' and attrs.get('name') == 'description':
            self.descriptions.append(attrs.get('content'))
        if tag == 'script' and attrs.get('type', '').lower() == 'application/ld+json':
            self.capture = []

    def handle_data(self, text):
        if self.capture is not None:
            self.capture.append(text)
        elif self.heading is not None:
            self.heading.append(text)

    def handle_endtag(self, tag):
        if tag == 'script' and self.capture is not None:
            self.blocks.append(''.join(self.capture))
            self.capture = None
        if tag == 'h1' and self.heading is not None:
            self.h1s.append(' '.join(''.join(self.heading).split()))
            self.heading = None


def schema_nodes(value):
    if isinstance(value, list):
        return [node for item in value for node in schema_nodes(item)]
    if not isinstance(value, dict):
        raise ValueError('JSON-LD root must be an object or array of objects')
    return schema_nodes(value['@graph']) if '@graph' in value else [value]


def reject_constant(value):
    raise ValueError(f'Non-JSON numeric constant: {value}')


def check_schema(root, site='https://nscalculators.com/'):
    root, origin = Path(root).resolve(), urlsplit(site)
    if origin.scheme != 'https' or not origin.netloc or origin.query or origin.fragment or not site.endswith('/'):
        raise ValueError('Site must be an absolute HTTPS URL ending in /')
    cache = {}

    def read_url(url):
        parsed = urlsplit(url)
        if (parsed.scheme, parsed.netloc) != (origin.scheme, origin.netloc) or not parsed.path.startswith(origin.path) or parsed.query:
            raise ValueError(f'Schema URL outside canonical site: {url}')
        relative = unquote(parsed.path[len(origin.path):])
        if '\\' in relative or any(part in ('.', '..') for part in relative.split('/')):
            raise ValueError(f'Unsafe schema URL: {url}')
        file = root / relative / 'index.html' if parsed.path.endswith('/') else root / relative
        if not file.resolve().is_relative_to(root) or not file.is_file():
            raise ValueError(f'Schema target missing: {url}')
        if file not in cache:
            signals = SchemaSignals()
            signals.feed(file.read_text(encoding='utf-8'))
            if signals.capture is not None:
                raise ValueError(f'Unclosed JSON-LD script: {url}')
            cache[file] = signals
        page = cache[file]
        if parsed.fragment and unquote(parsed.fragment) not in page.ids:
            raise ValueError(f'Schema fragment missing: {url}')
        return page

    locations = [node.text for node in ET.parse(root / 'sitemap.xml').getroot().findall(NS + 'url/' + NS + 'loc')]
    if not locations or len(set(locations)) != len(locations):
        raise ValueError('Expected nonempty unique sitemap URLs')
    counts = Counter(pages=len(locations))
    for url in locations:
        page = read_url(url)
        if page.canonicals != [url] or len(page.descriptions) != 1 or len(page.h1s) != 1:
            raise ValueError(f'Schema needs an unambiguous canonical, description and H1: {url}')
        try:
            nodes = [node for block in page.blocks for node in schema_nodes(json.loads(block, parse_constant=reject_constant))]
        except (ValueError, TypeError) as error:
            raise ValueError(f'Invalid JSON-LD at {url}: {error}') from error
        types = lambda node: node.get('@type') if isinstance(node.get('@type'), list) else [node.get('@type')]
        pages = [node for node in nodes if set(types(node)) & {'WebPage', 'CollectionPage'}]
        if len(pages) != 1 or pages[0].get('url') != url or pages[0].get('description') != page.descriptions[0]:
            raise ValueError(f'WebPage schema does not match page metadata: {url}')
        apps = [node for node in nodes if set(types(node)) & {'SoftwareApplication', 'WebApplication'}]
        if page.calculator and len(apps) != 1:
            raise ValueError(f'Calculator needs one application entity: {url}')
        if apps and not page.calculator:
            raise ValueError(f'Application lacks this site\'s visible calculator UI: {url}')
        breadcrumbs = [node for node in nodes if 'BreadcrumbList' in types(node)]
        if page.calculator and len(breadcrumbs) != 1:
            raise ValueError(f'Calculator needs one breadcrumb trail: {url}')
        for app in apps:
            if app.get('url') != url or app.get('name') != page.h1s[0] or app.get('description') != page.descriptions[0]:
                raise ValueError(f'Application does not match visible tool/metadata: {url}')
            if app.get('applicationCategory') not in APP_CATEGORIES:
                raise ValueError(f'Unsupported application category: {url}')
            offer = app.get('offers', {})
            if app.get('isAccessibleForFree') is not True or offer.get('@type') != 'Offer' or str(offer.get('price')) != '0' or offer.get('priceCurrency') != 'USD':
                raise ValueError(f'Application does not match free-tool offer: {url}')
            if 'aggregateRating' in app or 'review' in app:
                raise ValueError(f'Rating/review markup requires an explicit source audit: {url}')
            counts['applications'] += 1
        for node in breadcrumbs:
            items = node.get('itemListElement', [])
            if len(items) < 2 or [item.get('position') for item in items] != list(range(1, len(items) + 1)):
                raise ValueError(f'Breadcrumb positions are incomplete: {url}')
            if items[0].get('item') != site or items[-1].get('item') != url or items[-1].get('name') != page.h1s[0]:
                raise ValueError(f'Breadcrumb endpoints do not match page: {url}')
            for item in items:
                if item.get('@type') != 'ListItem' or not str(item.get('name', '')).strip() or not isinstance(item.get('item'), str):
                    raise ValueError(f'Incomplete breadcrumb item: {url}')
                read_url(item['item'])
                counts['breadcrumb_items'] += 1
            counts['breadcrumb_lists'] += 1
    return dict(counts)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default='dist')
    parser.add_argument('--site', default='https://nscalculators.com/')
    args = parser.parse_args()
    print(check_schema(args.root, args.site))

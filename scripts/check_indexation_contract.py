"""Check static sitemap eligibility and crawl paths; not proof of Google indexing."""
import argparse
from collections import Counter, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit
from urllib.robotparser import RobotFileParser
import xml.etree.ElementTree as ET

NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'


class PageSignals(HTMLParser):
    def __init__(self):
        super().__init__()
        self.canonicals, self.links, self.descriptions, self.robots = [], [], [], set()
        self.refresh = False
        self.base = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        rel = (a.get('rel') or '').lower().split()
        if tag == 'link' and 'canonical' in rel:
            self.canonicals.append(a.get('href'))
        if tag == 'a' and a.get('href') and not {'nofollow', 'sponsored', 'ugc'} & set(rel):
            self.links.append(a['href'])
        if tag == 'base':
            self.base = True
        if tag == 'meta':
            name, content = (a.get('name') or '').lower(), a.get('content') or ''
            if name in ('robots', 'googlebot'):
                self.robots.update(content.lower().replace(',', ' ').split())
            if name == 'description':
                self.descriptions.append(content)
            if (a.get('http-equiv') or '').lower() == 'refresh':
                self.refresh = True


def check_indexation(root, site='https://nscalculators.com/', max_depth=3):
    root = Path(root).resolve()
    origin = urlsplit(site)
    if origin.scheme != 'https' or not origin.netloc or origin.query or origin.fragment or not site.endswith('/'):
        raise ValueError('Site must be an absolute HTTPS URL ending in /')
    tree = ET.parse(root / 'sitemap.xml').getroot()
    if tree.tag != NS + 'urlset':
        raise ValueError('Expected a sitemap urlset with the protocol namespace')
    urls = []
    for entry in tree:
        locations = entry.findall(NS + 'loc')
        if entry.tag != NS + 'url' or len(locations) != 1 or not locations[0].text:
            raise ValueError('Each sitemap entry must have exactly one URL')
        urls.append(locations[0].text)
    if not urls or len(set(urls)) != len(urls) or site not in urls:
        raise ValueError('Sitemap must include the homepage and unique nonempty URLs')
    robots = RobotFileParser()
    robot_lines = (root / 'robots.txt').read_text(encoding='utf-8').splitlines()
    rule_paths = []
    for line in robot_lines:
        key, _, value = line.split('#', 1)[0].partition(':')
        if key.strip().lower() in ('allow', 'disallow'):
            value = value.strip()
            if any(symbol in value for symbol in ('*', '$')):
                raise ValueError('Wildcard robots rules require a Google-compatible rule audit')
            if value:
                rule_paths.append(value)
    if any(a.startswith(b) or b.startswith(a) for index, a in enumerate(rule_paths) for b in rule_paths[index + 1:]):
        raise ValueError('Overlapping robots rules require a longest-match rule audit')
    robots.parse(robot_lines)
    if site + 'sitemap.xml' not in (robots.site_maps() or []):
        raise ValueError('robots.txt must reference the canonical sitemap URL')
    pages = {}
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != origin.scheme or parsed.netloc != origin.netloc or not parsed.path.startswith(origin.path) or parsed.query or parsed.fragment:
            raise ValueError(f'Sitemap URL outside the canonical site: {url}')
        relative = unquote(parsed.path[len(origin.path):])
        if any(part in ('.', '..') for part in relative.split('/')) or '\\' in relative:
            raise ValueError(f'Unsafe sitemap path: {url}')
        file = (root / relative / 'index.html') if parsed.path.endswith('/') else (root / relative)
        if not file.resolve().is_relative_to(root) or not file.is_file():
            raise ValueError(f'Sitemap HTML file missing: {url}')
        if not robots.can_fetch('Googlebot', url):
            raise ValueError(f'robots.txt blocks sitemap URL: {url}')
        page = PageSignals()
        page.feed(file.read_text(encoding='utf-8'))
        if page.canonicals != [url]:
            raise ValueError(f'Sitemap URL must have one exact self-canonical: {url}')
        if page.robots & {'noindex', 'none'}:
            raise ValueError(f'Sitemap URL has an indexing exclusion: {url}')
        if page.refresh or page.base:
            raise ValueError(f'Redirect/base markup requires a separate audit: {url}')
        if len(page.descriptions) != 1 or not page.descriptions[0].strip():
            raise ValueError(f'Sitemap page needs one nonempty description: {url}')
        pages[url] = page
    graph = {url: {urljoin(url, href).split('#')[0] for href in page.links} & pages.keys()
             if not page.robots & {'nofollow', 'none'} else set() for url, page in pages.items()}
    depth, queue = {site: 0}, deque([site])
    while queue:
        source = queue.popleft()
        for target in graph[source]:
            if target not in depth:
                depth[target] = depth[source] + 1
                queue.append(target)
    unreachable = sorted(set(pages) - depth.keys())
    too_deep = sorted(url for url, steps in depth.items() if steps > max_depth)
    if unreachable or too_deep:
        raise ValueError(f'Sitemap crawl-path failure: unreachable={unreachable}; beyond {max_depth} clicks={too_deep}')
    return {'sitemap_urls': len(urls), 'depths': dict(sorted(Counter(depth.values()).items())), 'max_depth': max(depth.values())}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', nargs='?', default='dist')
    parser.add_argument('--site', default='https://nscalculators.com/')
    args = parser.parse_args()
    print(check_indexation(args.root, args.site))

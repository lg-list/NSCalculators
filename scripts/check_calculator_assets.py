import argparse
import json
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse

SPECIALIZED = {row['asset']: row['slug'] + '/index.html' for row in json.loads((Path(__file__).resolve().parents[1] / 'tools/asset-optimizer/engine-assets.json').read_text())}


class CalculatorScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            src = dict(attrs).get("src", "")
            if urlparse(src).path.endswith(tuple('/assets/' + name for name in ['calculator.js', *SPECIALIZED])):
                self.sources.append(src)


def check_assets(root):
    root = Path(root)
    version = sha256((root / "assets" / "calculator.js").read_bytes()).hexdigest()[:16]
    checked = 0
    for html in root.rglob("*.html"):
        parser = CalculatorScriptParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for asset, target in SPECIALIZED.items():
            if (root / 'assets' / asset).exists() and html.relative_to(root).as_posix() == target:
                if len(parser.sources) != 1 or not urlparse(parser.sources[0]).path.endswith('/assets/' + asset):
                    raise ValueError(target + ' must use exactly one specialized runtime')
        for src in parser.sources:
            expected = version
            asset = Path(urlparse(src).path).name
            if asset in SPECIALIZED:
                if html.relative_to(root).as_posix() != SPECIALIZED[asset]:
                    raise ValueError(f"{html}: specialized runtime on unsupported page")
                expected = sha256((root / 'assets' / asset).read_bytes()).hexdigest()[:16]
            if parse_qs(urlparse(src).query).get("v") != [expected]:
                raise ValueError(f"{html}: calculator bundle version does not match {version}: {src}")
            checked += 1
    if not checked:
        raise ValueError("No calculator bundle references found")
    return checked, version


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="dist")
    checked, version = check_assets(parser.parse_args().root)
    print(f"Verified {checked} calculator script references against bundle {version}.")

import argparse
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class CalculatorScriptParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        if tag == "script":
            src = dict(attrs).get("src", "")
            if urlparse(src).path.endswith(("/assets/calculator.js", "/assets/calculator-401k.js")):
                self.sources.append(src)


def check_assets(root):
    root = Path(root)
    version = sha256((root / "assets" / "calculator.js").read_bytes()).hexdigest()[:16]
    checked = 0
    for html in root.rglob("*.html"):
        parser = CalculatorScriptParser()
        parser.feed(html.read_text(encoding="utf-8"))
        if (root / 'assets/calculator-401k.js').exists() and html.relative_to(root).as_posix() == '401k-calculator/index.html':
            if len(parser.sources) != 1 or not urlparse(parser.sources[0]).path.endswith('/assets/calculator-401k.js'):
                raise ValueError('401k page must use exactly one specialized runtime')
        for src in parser.sources:
            expected = version
            if urlparse(src).path.endswith('/assets/calculator-401k.js'):
                if html.relative_to(root).as_posix() != '401k-calculator/index.html':
                    raise ValueError(f"{html}: specialized runtime on unsupported page")
                expected = sha256((root / 'assets/calculator-401k.js').read_bytes()).hexdigest()[:16]
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

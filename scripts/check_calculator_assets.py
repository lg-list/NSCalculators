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
            if urlparse(src).path.endswith("/assets/calculator.js"):
                self.sources.append(src)


def check_assets(root):
    root = Path(root)
    version = sha256((root / "assets" / "calculator.js").read_bytes()).hexdigest()[:16]
    checked = 0
    for html in root.rglob("*.html"):
        parser = CalculatorScriptParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for src in parser.sources:
            if parse_qs(urlparse(src).query).get("v") != [version]:
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

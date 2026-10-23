import argparse
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse


class StylesheetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.sources = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "link" and "stylesheet" in attributes.get("rel", "").lower().split():
            href = attributes.get("href", "")
            if urlparse(href).path.endswith("/assets/site.css"):
                self.sources.append(href)


def check_stylesheets(root):
    root = Path(root)
    version = sha256((root / "assets" / "site.css").read_bytes()).hexdigest()[:16]
    checked = 0
    for html in root.rglob("*.html"):
        parser = StylesheetParser()
        parser.feed(html.read_text(encoding="utf-8"))
        for href in parser.sources:
            if parse_qs(urlparse(href).query).get("v") != [version]:
                raise ValueError(f"{html}: stylesheet version does not match {version}: {href}")
            checked += 1
    if not checked:
        raise ValueError("No shared stylesheet references found")
    return checked, version


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default="dist")
    checked, version = check_stylesheets(parser.parse_args().root)
    print(f"Verified {checked} stylesheet references against CSS {version}.")

import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import build


SOURCE = ROOT / "exports" / "seo-priority-keywords.csv"
OUTPUT = ROOT / "exports" / "seo-priority-keywords-indexable.csv"


def keyword_targets(rows, calculators):
    provenance = json.loads(build.KEYWORD_STATS_PROVENANCE.read_text(encoding="utf-8")) if build.KEYWORD_STATS_PROVENANCE.exists() else {}
    mapping = provenance.get("priority_mapping", {})
    mapping_verified = build.keyword_data_fingerprint(rows) == mapping.get("normalized_data_sha256")
    grouped = defaultdict(list)
    for row in rows:
        key = " ".join(row["keyword"].casefold().split())
        grouped[key].append(row)

    targets = []
    for keyword, candidates in grouped.items():
        indexable = {}
        for row in candidates:
            slug = row["url_path"].strip("/")
            visited = set()
            while slug in build.CALCULATOR_REDIRECTS:
                if slug in visited:
                    raise ValueError(f"Redirect cycle for {row['url_path']}")
                visited.add(slug)
                slug = build.CALCULATOR_REDIRECTS[slug]
            calc = calculators.get(slug)
            if calc is None:
                raise ValueError(f"No calculator found for {row['url_path']}")
            if build.is_indexable_calculator(calc):
                indexable.setdefault(slug, dict(row, url_path=f"/{slug}/"))
        if len(indexable) != 1:
            raise ValueError(f"Expected one indexable target for {keyword!r}; found {len(indexable)}")

        target = next(iter(indexable.values()))
        target["nonindexable_variants_excluded"] = str(len(candidates) - 1)
        country = mapping.get("country", "unknown") if mapping_verified else "unknown"
        target["search_volume_country"] = country
        target["us_avg_monthly_searches"] = target["avg_monthly_searches"] if country == "US" and mapping_verified else ""
        target["priority_scope"] = mapping.get("priority_scope", "unverified") if mapping_verified else "unverified"
        targets.append(target)

    priority_order = {"P1": 0, "P2": 1, "P3": 2}
    targets.sort(key=lambda row: (
        priority_order.get(row["seo_priority"], 3),
        -float(row["avg_monthly_searches"] or 0),
        row["keyword"].casefold(),
    ))
    return targets


def main():
    data = json.loads((ROOT / "src" / "data" / "calculators.json").read_text(encoding="utf-8"))
    calculators = {calc["slug"]: calc for calc in build.base_and_supplemental(data)}
    with SOURCE.open(newline="", encoding="utf-8-sig") as source_file:
        rows = list(csv.DictReader(source_file))
    targets = keyword_targets(rows, calculators)

    fields = list(rows[0]) + ["nonindexable_variants_excluded", "search_volume_country", "us_avg_monthly_searches", "priority_scope"]
    with OUTPUT.open("w", newline="", encoding="utf-8-sig") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(targets)

    excluded = len(rows) - len(targets)
    print(f"Wrote {len(targets)} unique indexable keyword targets; excluded {excluded} nonindexable variants.")


if __name__ == "__main__":
    main()

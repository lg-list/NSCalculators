from collections import Counter, defaultdict
from datetime import date
from html import escape
from pathlib import Path
import json
import os
import re
import shutil

ROOT = Path(__file__).parent
SRC = ROOT / "src" / "data" / "calculators.json"
DIST = ROOT / "dist"
KEYWORD_STATS = ROOT / "exports" / "keyword-stats-positive.json"
SEO_STRATEGY = ROOT / "exports" / "seo-keyword-strategy-2026-09-05.json"
PUBLIC_BASE_PATH = os.environ.get("PUBLIC_BASE_PATH", "").strip().rstrip("/")
PUBLIC_SITE_DOMAIN = os.environ.get("PUBLIC_SITE_DOMAIN", "").strip()

CATEGORY_ORDER = [
    "Automotive",
    "Construction",
    "Conversion",
    "Cooking",
    "Electrical",
    "Financial",
    "Health",
    "Math",
    "Pets",
    "Science",
    "Time & Date",
    "Video",
]

GROUP_LABELS = {
    "Automotive": ["Car Value", "Payload & Towing", "Fuel & Performance", "Tires & Wheels"],
    "Construction": ["Concrete & Area", "Roofing & Framing", "Flooring & Tile", "Domes & Materials", "Materials & Outdoor"],
    "Conversion": ["Length", "Weight", "Volume", "Area", "Speed", "Pressure", "Energy", "Power", "Data Storage"],
    "Cooking": ["Kitchen Volume"],
    "Electrical": ["Wire & Breakers", "Power Conversion", "Load & Voltage Drop", "Technical Tools"],
    "Financial": ["Mortgages", "Loans", "Savings & Growth", "Retirement", "Taxes & Pay", "Credit & Debt", "Investment"],
    "Health": ["Body Metrics", "Nutrition", "Pregnancy", "Fitness", "Clinical Reference", "Body Height", "Body Weight"],
    "Math": ["Core Math", "Statistics", "Geometry", "Education", "Random & Utility", "Angle"],
    "Pets": ["Pet Food Amount", "Pet Weight"],
    "Science": ["Conversion & Science", "Energy", "Frequency", "Pressure", "Scientific Length", "Scientific Mass"],
    "Time & Date": ["Age & Dates", "Time"],
    "Video": ["Bitrate", "Storage"],
}

CALCULATOR_GROUPS = {
    "car-trade-in-value-calculator": "Car Value",
    "used-car-value-calculator": "Car Value",
    "car-depreciation-calculator": "Car Value",
    "car-resale-value-calculator": "Car Value",
    "private-party-car-value-calculator": "Car Value",
    "car-loan-payment-calculator-with-taxes": "Loans",
    "loan-payment-calculator": "Loans",
    "compound-interest-calculator": "Savings & Growth",
    "discount-calculator": "Salary & Discounts",
    "salary-increase-calculator": "Salary & Discounts",
    "vehicle-payload-calculator": "Payload & Towing",
    "truck-payload-calculator": "Payload & Towing",
    "payload-capacity-calculator": "Payload & Towing",
    "gvwr-calculator": "Payload & Towing",
    "trailer-weight-calculator": "Payload & Towing",
    "trailer-tongue-weight-calculator": "Payload & Towing",
    "trailer-payload-calculator": "Payload & Towing",
    "tongue-weight-percentage-calculator": "Payload & Towing",
    "car-towing-capacity-calculator": "Payload & Towing",
    "towing-capacity-calculator": "Payload & Towing",
    "car-fuel-cost-calculator": "Fuel & Performance",
    "mpg-calculator": "Fuel & Performance",
    "trip-fuel-cost-calculator": "Fuel & Performance",
    "horsepower-calculator": "Fuel & Performance",
    "power-to-weight-ratio-calculator": "Fuel & Performance",
    "f150-bed-dimensions": "Payload & Towing",
    "tire-size-calculator": "Tires & Wheels",
    "wheel-offset-calculator": "Tires & Wheels",
    "wheel-backspacing-calculator": "Tires & Wheels",
    "bolt-pattern-calculator": "Tires & Wheels",
    "geodesic-dome-calculator": "Domes & Materials",
    "geodesic-dome-size-calculator": "Domes & Materials",
    "geodesic-dome-surface-area-calculator": "Domes & Materials",
    "geodesic-dome-material-calculator": "Domes & Materials",
    "concrete-volume-calculator": "Concrete & Area",
    "square-footage-calculator": "Concrete & Area",
    "board-foot-calculator": "Roofing & Framing",
    "stud-spacing-calculator": "Roofing & Framing",
    "roof-pitch-calculator": "Roofing & Framing",
    "rafter-length-calculator": "Roofing & Framing",
    "flooring-calculator": "Flooring & Tile",
    "tile-calculator": "Flooring & Tile",
    "tile-spacer-calculator": "Flooring & Tile",
    "deck-board-calculator": "Flooring & Tile",
    "voltage-drop-calculator": "Load & Voltage Drop",
    "wire-size-calculator": "Wire & Breakers",
    "breaker-size-calculator": "Wire & Breakers",
    "amps-to-watts-calculator": "Power Conversion",
    "watts-to-amps-calculator": "Power Conversion",
    "electrical-load-calculator": "Load & Voltage Drop",
}

# Full static generator for the Northstar calculator site.
def read_data():
    return json.loads(SRC.read_text(encoding="utf-8"))


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def h(value):
    text = str(value).replace("\u2013", "-").replace("\u2014", "-")
    return escape(text, quote=True)


def slugify_cat(cat):
    return f"{cat.lower().replace(' & ', '-').replace(' ', '-')}-calculators"


def slugify_text(text):
    return (
        text.lower()
        .replace("&", "and")
        .replace("/", " ")
        .replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .replace(":", "")
        .replace("  ", " ")
        .strip()
        .replace(" ", "-")
    )


def load_google_keyword_metrics():
    if not KEYWORD_STATS.exists():
        return {}
    rows = json.loads(KEYWORD_STATS.read_text(encoding="utf-8"))
    metrics = {}
    for row in rows:
        keyword = str(row.get("keyword") or "").strip().lower()
        if not keyword:
            continue
        monthly = int(float(row.get("volume") or row.get("avg_monthly_searches") or 0))
        record = {
            "keyword": keyword,
            "monthly_searches": monthly,
            "ads_competition": row.get("competition") or row.get("ads_competition") or "",
            "competition_index": int(float(row.get("competition_index") or 0)),
            "bid_low": row.get("bid_low"),
            "bid_high": row.get("bid_high"),
            "source": "Google Keyword Planner stats",
        }
        metrics[slugify_text(keyword)] = record
    return metrics


def smart_title(text):
    titled = str(text).strip().title()
    for src, dest in {
        "Inches Of Mercury": "inHg",
        "Millimeters Of Mercury": "mmHg",
        "Pounds Per Square Inch": "PSI",
        "Bmi": "BMI",
        "Pmi": "PMI",
        "Hoa": "HOA",
        "Mpg": "MPG",
        "Apr": "APR",
        "Us": "US",
        "Uk": "UK",
        "Fha": "FHA",
        "Va": "VA",
    }.items():
        titled = re.sub(rf"\b{src}\b", dest, titled)
    return titled


def group_slug(group):
    return slugify_text(group)


def subgroup_path(cat, group):
    return f"/{slugify_cat(cat)}/{group_slug(group)}/"


CATEGORY_ICON_PATHS = {
    "Automotive": '<path d="M7 24h26l-3-9H10z"/><path d="M11 24v5M29 24v5"/><circle cx="13" cy="29" r="3"/><circle cx="27" cy="29" r="3"/>',
    "Construction": '<path d="M9 29l15-15"/><path d="M18 8l14 14"/><path d="M15 11l6-6 8 8-6 6"/>',
    "Conversion": '<path d="M9 14h20"/><path d="M24 9l5 5-5 5"/><path d="M31 26H11"/><path d="M16 21l-5 5 5 5"/>',
    "Cooking": '<path d="M12 7v12"/><path d="M8 7v8a4 4 0 0 0 8 0V7"/><path d="M25 7v26"/><path d="M25 7c5 3 6 9 2 13"/>',
    "Electrical": '<path d="M22 5 10 23h10l-2 12 12-18H20z"/>',
    "Financial": '<path d="M20 6v28"/><path d="M28 12c-2-2-5-3-8-3-5 0-8 2-8 5s3 4 8 5 8 2 8 5-3 7-8 7c-4 0-7-1-9-4"/>',
    "Health": '<path d="M20 33S8 25 8 15a7 7 0 0 1 12-5 7 7 0 0 1 12 5c0 10-12 18-12 18z"/>',
    "Math": '<rect x="9" y="6" width="22" height="28" rx="3"/><path d="M13 13h14"/><path d="M14 20h3M20 20h3M26 20h1M14 26h3M20 26h3M26 26h1"/>',
    "Pets": '<circle cx="14" cy="15" r="3"/><circle cx="26" cy="15" r="3"/><circle cx="18" cy="10" r="3"/><circle cx="22" cy="10" r="3"/><path d="M12 27c0-5 4-8 8-8s8 3 8 8c0 3-2 5-5 4-1 0-2-1-3-1s-2 1-3 1c-3 1-5-1-5-4z"/>',
    "Science": '<circle cx="20" cy="20" r="3"/><ellipse cx="20" cy="20" rx="14" ry="5"/><ellipse cx="20" cy="20" rx="14" ry="5" transform="rotate(60 20 20)"/><ellipse cx="20" cy="20" rx="14" ry="5" transform="rotate(120 20 20)"/>',
    "Time & Date": '<circle cx="20" cy="20" r="14"/><path d="M20 12v9l6 3"/><path d="M10 8l-3 4M30 8l3 4"/>',
    "Video": '<rect x="8" y="10" width="24" height="20" rx="3"/><path d="m17 16 9 4-9 4z"/>',
}


def category_icon(cat, extra=""):
    path = CATEGORY_ICON_PATHS.get(cat, CATEGORY_ICON_PATHS["Math"])
    classes = "cat-icon" + (f" {extra}" if extra else "")
    return f'<span class="{h(classes)}" aria-hidden="true"><svg viewBox="0 0 40 40" focusable="false">{path}</svg></span>'


def calculator_group(calc):
    return calc.get("group") or CALCULATOR_GROUPS.get(calc["slug"]) or "General"


def display_group(group):
    return group.title() if group.islower() else group


def normalized_calc(calc):
    item = dict(calc)
    if item.get("cat") == "Finance":
        item["cat"] = "Financial"
    return item


def site_url(site, path):
    return site["domain"].rstrip("/") + path


def apply_base_path(html):
    if not PUBLIC_BASE_PATH:
        return html
    return (
        html.replace('href="/', f'href="{PUBLIC_BASE_PATH}/')
        .replace('src="/', f'src="{PUBLIC_BASE_PATH}/')
        .replace('action="/', f'action="{PUBLIC_BASE_PATH}/')
    )


def breadcrumb_schema(site, crumbs):
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": index + 1,
                "name": name,
                "item": site_url(site, path),
            }
            for index, (name, path) in enumerate(crumbs)
        ],
    }


def calculator_schema(site, calc):
    keywords = seo_keywords(calc)
    return {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": calc["title"],
        "applicationCategory": "CalculatorApplication",
        "operatingSystem": "Any",
        "url": site_url(site, f"/{calc['slug']}/"),
        "description": seo_description(calc),
        "keywords": keywords,
        "isAccessibleForFree": True,
        "offers": {
            "@type": "Offer",
            "price": "0",
            "priceCurrency": "USD",
        },
    }


def website_schema(site):
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": site["name"],
        "url": site_url(site, "/"),
        "potentialAction": {
            "@type": "SearchAction",
            "target": site_url(site, "/") + "?q={search_term_string}",
            "query-input": "required name=search_term_string",
        },
    }


LOGO_MARK = """<svg viewBox="0 0 40 40" aria-hidden="true"><rect class="logo-body" x="8" y="5" width="24" height="30" rx="5"/><path class="logo-screen" d="M13 12h14"/><path d="M14 19h3M20 19h3M26 19h1M14 25h3M20 25h3M26 25h1"/><path class="logo-accent" d="M14 31h13"/></svg>"""


def nav():
    menu_links = "".join(
        f"""<a href="/{slugify_cat(cat)}/#{h(group_slug(group))}">{category_icon(cat, "nav-icon")}<span>{h(display_group(group))}</span><small>{h(cat)}</small></a>"""
        for cat in CATEGORY_ORDER
        for group in GROUP_LABELS.get(cat, [])
    )
    return """<header class="site-header"><div class="wrap nav">
<a class="brand" href="/" aria-label="NS Calculators home"><span class="brand-mark">""" + LOGO_MARK + """</span><span class="brand-name"><strong>NS</strong><b>Calculators</b></span></a>
<nav class="navlinks" aria-label="Main navigation"><div class="menu-group all-calculators-menu"><a class="menu-top" href="/">Calculators</a><div class="submenu mega-menu">""" + menu_links + """</div></div></nav>
</div></header>"""


def footer():
    return """<footer class="footer"><div class="wrap footer-grid">
<div><a class="brand footer-brand" href="/"><span class="brand-mark">""" + LOGO_MARK + """</span><span class="brand-name"><strong>NS</strong><b>Calculators</b></span></a><p>Practical browser-based tools for US users. Verify critical results with authoritative sources.</p></div>
<div class="footer-links"><a href="/about/">About</a><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/contact/">Contact</a></div>
</div></footer>"""


def json_ld(payload):
    return '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"


def page(site, title, desc, path, body, keywords=None, extra_schema=None, page_type="WebPage"):
    keywords = keywords or []
    extra_schema = extra_schema or []
    schema = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title.replace(" | Northstar Calculators", ""),
        "description": desc,
        "url": site_url(site, path),
    }
    if keywords:
        schema["keywords"] = keywords
    keyword_meta = f'<meta name="keywords" content="{h(", ".join(keywords))}">' if keywords else ""
    schema_html = "\n".join(json_ld(item) for item in [schema] + extra_schema)
    html = f"""<!doctype html><html lang="{h(site['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)}</title><meta name="description" content="{h(desc)}">{keyword_meta}
<meta property="og:type" content="website"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{h(site_url(site, path))}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{h(title)}"><meta name="twitter:description" content="{h(desc)}">
<link rel="canonical" href="{h(site_url(site, path))}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.svg"><link rel="stylesheet" href="/assets/site.css">
{schema_html}<script>window.NORTHSTAR_BASE_PATH={json.dumps(PUBLIC_BASE_PATH)};</script></head><body>{nav()}{body}{footer()}</body></html>"""
    return apply_base_path(html)


def category_desc(cat):
    return {
        "Automotive": "Trade-in values, towing limits, payload, fuel cost, tires, wheels, and truck reference tools.",
        "Construction": "Area, materials, roof geometry, tile, decking, dome, concrete, and framing calculators.",
        "Conversion": "Length, weight, volume, area, speed, pressure, energy, power, and data unit converters.",
        "Cooking": "Kitchen volume, recipe scaling, ingredient weight, oven, and serving-size converters.",
        "Financial": "Payments, compound growth, discounts, raises, and auto-loan planning calculators.",
        "Health": "Everyday wellness calculators for body metrics, hydration, pace, nutrition, and activity planning.",
        "Math": "Percentage, ratio, exponent, fraction, geometry, and classroom-friendly math calculators.",
        "Pets": "Pet age, food amount, medication planning, weight, crate, and care calculators.",
        "Science": "Metric, physics, chemistry, astronomy, data, and lab unit conversion tools.",
        "Time & Date": "Seconds, minutes, hours, days, weeks, months, years, and date planning converters.",
        "Video": "Aspect ratio, bitrate, frame rate, duration, storage, and creator workflow calculators.",
        "Electrical": "Wire, breaker, load, voltage drop, watts, and amps planning tools.",
    }.get(cat, "Focused tools with formulas, examples, and related pages.")


def unit_slug(name):
    return (
        name.lower()
        .replace(" per ", "-per-")
        .replace("square ", "sq-")
        .replace("cubic ", "cu-")
        .replace("/", "-per-")
        .replace(" ", "-")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
    )


def unit_groups():
    length = [
        ("millimeters", 0.001), ("centimeters", 0.01), ("meters", 1), ("kilometers", 1000),
        ("inches", 0.0254), ("feet", 0.3048), ("yards", 0.9144), ("miles", 1609.344),
        ("nautical miles", 1852), ("micrometers", 0.000001), ("nanometers", 0.000000001),
        ("decimeters", 0.1), ("hectometers", 100), ("chains", 20.1168), ("furlongs", 201.168),
        ("rods", 5.0292), ("fathoms", 1.8288), ("light seconds", 299792458), ("astronomical units", 149597870700),
        ("parsecs", 3.085677581491367e16), ("light years", 9.4607304725808e15), ("mils", 0.0000254),
    ]
    mass = [
        ("milligrams", 0.000001), ("grams", 0.001), ("kilograms", 1), ("metric tons", 1000),
        ("ounces", 0.028349523125), ("pounds", 0.45359237), ("stones", 6.35029318), ("short tons", 907.18474),
        ("long tons", 1016.0469088), ("micrograms", 0.000000001), ("carats", 0.0002), ("grains", 0.00006479891),
        ("drams", 0.0017718451953125), ("slugs", 14.59390294), ("pennyweights", 0.00155517384),
        ("troy ounces", 0.0311034768), ("troy pounds", 0.3732417216), ("quintals", 100),
    ]
    volume = [
        ("milliliters", 0.001), ("liters", 1), ("cubic meters", 1000), ("cubic centimeters", 0.001),
        ("cubic inches", 0.016387064), ("cubic feet", 28.316846592), ("cubic yards", 764.554857984),
        ("teaspoons", 0.00492892159375), ("tablespoons", 0.01478676478125), ("fluid ounces", 0.0295735295625),
        ("cups", 0.2365882365), ("pints", 0.473176473), ("quarts", 0.946352946), ("gallons", 3.785411784),
        ("imperial fluid ounces", 0.0284130625), ("imperial pints", 0.56826125), ("imperial quarts", 1.1365225),
        ("imperial gallons", 4.54609), ("barrels", 158.987294928), ("drops", 0.00005),
    ]
    area = [
        ("square millimeters", 0.000001), ("square centimeters", 0.0001), ("square meters", 1),
        ("square kilometers", 1000000), ("square inches", 0.00064516), ("square feet", 0.09290304),
        ("square yards", 0.83612736), ("acres", 4046.8564224), ("hectares", 10000), ("square miles", 2589988.110336),
        ("ares", 100), ("barns", 1e-28), ("roods", 1011.7141056), ("sections", 2589988.110336),
    ]
    speed = [
        ("meters per second", 1), ("kilometers per hour", 0.2777777778), ("miles per hour", 0.44704),
        ("feet per second", 0.3048), ("knots", 0.5144444444), ("mach", 343), ("inches per second", 0.0254),
        ("centimeters per second", 0.01), ("yards per second", 0.9144), ("minutes per mile", 0.44704),
        ("minutes per kilometer", 0.2777777778),
    ]
    pressure = [
        ("pascals", 1), ("kilopascals", 1000), ("megapascals", 1000000), ("bar", 100000),
        ("millibar", 100), ("psi", 6894.757293), ("ksi", 6894757.293), ("atmospheres", 101325),
        ("torr", 133.322368), ("inches of mercury", 3386.389), ("millimeters of mercury", 133.322368),
    ]
    energy = [
        ("joules", 1), ("kilojoules", 1000), ("megajoules", 1000000), ("calories", 4.184),
        ("kilocalories", 4184), ("watt hours", 3600), ("kilowatt hours", 3600000), ("electronvolts", 1.602176634e-19),
        ("british thermal units", 1055.05585262), ("therms", 105505585.262), ("foot pounds", 1.3558179483314004),
    ]
    power = [
        ("watts", 1), ("kilowatts", 1000), ("megawatts", 1000000), ("horsepower", 745.6998715822702),
        ("metric horsepower", 735.49875), ("btu per hour", 0.2930710702), ("tons of refrigeration", 3516.8528421),
        ("foot pounds per second", 1.3558179483), ("calories per second", 4.184),
    ]
    data = [
        ("bits", 0.125), ("bytes", 1), ("kilobytes", 1000), ("megabytes", 1000000), ("gigabytes", 1000000000),
        ("terabytes", 1000000000000), ("petabytes", 1000000000000000), ("kibibytes", 1024),
        ("mebibytes", 1048576), ("gibibytes", 1073741824), ("tebibytes", 1099511627776),
        ("megabits", 125000), ("gigabits", 125000000), ("terabits", 125000000000),
    ]
    time = [
        ("nanoseconds", 1e-9), ("microseconds", 1e-6), ("milliseconds", 0.001), ("seconds", 1),
        ("minutes", 60), ("hours", 3600), ("days", 86400), ("weeks", 604800), ("months", 2629746),
        ("years", 31556952), ("decades", 315569520), ("centuries", 3155695200), ("fortnights", 1209600),
    ]
    angle = [
        ("degrees", 1), ("radians", 57.29577951308232), ("gradians", 0.9), ("arc minutes", 1 / 60),
        ("arc seconds", 1 / 3600), ("turns", 360), ("quadrants", 90), ("sextants", 60),
    ]
    frequency = [
        ("hertz", 1), ("kilohertz", 1000), ("megahertz", 1000000), ("gigahertz", 1000000000),
        ("terahertz", 1000000000000), ("rpm", 1 / 60), ("cycles per minute", 1 / 60), ("beats per minute", 1 / 60),
    ]
    video = [
        ("kilobits per second", 1000), ("megabits per second", 1000000), ("gigabits per second", 1000000000),
        ("kilobytes per second", 8000), ("megabytes per second", 8000000), ("gigabytes per hour", 2222222.2222),
        ("frames per second", 1), ("frames per minute", 1 / 60), ("frames per hour", 1 / 3600),
    ]
    cooking = [
        ("teaspoons", 0.00492892159375), ("tablespoons", 0.01478676478125), ("cups", 0.2365882365),
        ("fluid ounces", 0.0295735295625), ("pints", 0.473176473), ("quarts", 0.946352946), ("gallons", 3.785411784),
        ("milliliters", 0.001), ("liters", 1), ("grams water", 0.001), ("ounces water", 0.028349523125),
        ("pounds water", 0.45359237),
    ]
    return [
        ("Conversion", "length", length), ("Conversion", "weight", mass), ("Conversion", "volume", volume),
        ("Conversion", "area", area), ("Conversion", "speed", speed), ("Conversion", "pressure", pressure),
        ("Conversion", "energy", energy), ("Conversion", "power", power), ("Conversion", "data storage", data),
        ("Cooking", "kitchen volume", cooking), ("Science", "scientific length", length),
        ("Health", "body weight", mass), ("Health", "body height", length),
        ("Pets", "pet weight", mass), ("Pets", "pet food amount", cooking),
        ("Science", "scientific mass", mass), ("Science", "pressure", pressure), ("Science", "energy", energy),
        ("Science", "frequency", frequency), ("Time & Date", "time", time), ("Math", "angle", angle),
        ("Video", "bitrate", video), ("Video", "storage", data),
    ]


def supplemental_calculators():
    generated = []
    seen = set()
    for cat, group, units in unit_groups():
        for from_name, from_factor in units:
            for to_name, to_factor in units:
                if from_name == to_name:
                    continue
                slug = f"{unit_slug(from_name)}-to-{unit_slug(to_name)}-calculator"
                if slug in seen:
                    slug = f"{unit_slug(group)}-{slug}"
                if slug in seen:
                    continue
                seen.add(slug)
                factor = from_factor / to_factor
                title = f"{from_name.title()} to {to_name.title()} Calculator"
                generated.append({
                    "slug": slug,
                    "title": title,
                    "cat": cat,
                    "engine": "linear_convert",
                    "desc": f"Convert {from_name} to {to_name} with a direct unit conversion factor.",
                    "formula": f"{to_name} = {from_name} × {factor:.12g}.",
                    "example": f"A value of 1 in {from_name} equals {factor:.12g} {to_name}.",
                    "inputs": [
                        ["value", f"Value in {from_name}", "number", 1],
                        ["factor", "Conversion factor", "hidden", factor],
                        ["target", "Target unit", "hidden", to_name],
                    ],
                    "keyword_data": {},
                    "generated": True,
                    "group": group,
                })
    return generated


CN_KEYWORDS = ROOT / "exports" / "calculator-net-keywords.json"


def calculator_net_category(keyword, source_category):
    text = keyword.lower()
    if source_category == "Financial":
        return "Financial"
    if source_category == "Fitness & Health":
        return "Health"
    if source_category == "Construction":
        return "Construction"
    if source_category == "Technical & Electrical":
        return "Electrical"
    if source_category == "Math":
        return "Math"
    if source_category == "Conversion & Science":
        return "Science"
    if any(word in text for word in ["financial", "finance", "currency", "inflation", "tax", "retirement", "loan", "mortgage", "investment", "savings", "credit", "debt", "annuity", "salary"]):
        return "Financial"
    if any(word in text for word in ["age", "date", "time", "hours", "day counter", "day of the week"]):
        return "Time & Date"
    if any(word in text for word in ["tip", "gpa", "grade", "password", "dice", "love", "basic calculator"]):
        return "Math"
    if any(word in text for word in ["height", "weight", "sleep"]):
        return "Health"
    if any(word in text for word in ["concrete", "roofing", "tile", "mulch", "gravel", "stair"]):
        return "Construction"
    if any(word in text for word in ["horsepower", "mileage", "tire"]):
        return "Automotive"
    return "Financial" if "calculator" in text and any(word in text for word in ["cost", "pay", "fee", "bond", "fund"]) else "Math"


def calculator_net_group(keyword, cat):
    text = keyword.lower()
    if cat == "Financial":
        if any(word in text for word in ["mortgage", "house", "home equity", "heloc", "rent vs buy", "down payment"]):
            return "Mortgages"
        if any(word in text for word in ["loan", "lease", "repayment", "payoff", "refinance"]):
            return "Loans"
        if any(word in text for word in ["retirement", "401k", "ira", "rmd", "pension", "social security"]):
            return "Retirement"
        if any(word in text for word in ["tax", "salary", "commission", "take home", "vat"]):
            return "Taxes & Pay"
        if any(word in text for word in ["credit", "debt"]):
            return "Credit & Debt"
        if any(word in text for word in ["investment", "annuity", "roi", "irr", "return", "fund", "bond", "present value", "future value", "cd"]):
            return "Investment"
        return "Savings & Growth"
    if cat == "Health":
        if any(word in text for word in ["pregnancy", "due date", "conception", "ovulation", "period"]):
            return "Pregnancy"
        if any(word in text for word in ["calorie", "macro", "protein", "carbohydrate", "fat intake", "tdee"]):
            return "Nutrition"
        if any(word in text for word in ["pace", "one rep", "heart rate", "calories burned"]):
            return "Fitness"
        if any(word in text for word in ["gfr", "bac", "surface area"]):
            return "Clinical Reference"
        return "Body Metrics"
    if cat == "Math":
        if any(word in text for word in ["standard deviation", "sample size", "probability", "statistics", "z score", "confidence", "p value", "average"]):
            return "Statistics"
        if any(word in text for word in ["triangle", "area", "circle", "surface", "distance", "pythagorean", "slope"]):
            return "Geometry"
        if any(word in text for word in ["gpa", "grade", "fraction", "percent", "long division"]):
            return "Education"
        if any(word in text for word in ["random", "password", "dice", "love"]):
            return "Random & Utility"
        return "Core Math"
    if cat == "Construction":
        if any(word in text for word in ["roof", "tile", "stair", "mulch", "gravel"]):
            return "Materials & Outdoor"
        return "Concrete & Area"
    if cat == "Electrical":
        if any(word in text for word in ["subnet", "bandwidth", "encode", "decode"]):
            return "Technical Tools"
        return "Load & Voltage Drop"
    if cat == "Time & Date":
        return "Age & Dates"
    if cat == "Science":
        return "Conversion & Science"
    if cat == "Automotive":
        return "Fuel & Performance" if any(word in text for word in ["horsepower", "mileage"]) else "Tires & Wheels"
    return "General"


def calculator_net_template(keyword, slug, cat):
    text = keyword.lower()
    base = {
        "engine": "cn_generic",
        "desc": f"Estimate {keyword.lower()} values with a practical browser-based calculator.",
        "formula": "Result = entered values applied to the selected calculator model.",
        "example": f"Enter sample values to generate an illustrative {keyword.lower()} result.",
        "inputs": [["amount", "Amount", "number", 1000], ["rate", "Rate (%)", "number", 5], ["years", "Years", "number", 10]],
    }
    if "mortgage" in text:
        base.update({"engine": "cn_mortgage", "desc": "Estimate a mortgage payment with principal, interest, taxes, insurance, PMI, HOA, extra payments, and total payoff costs.", "formula": "Monthly payment = principal and interest + optional annual taxes, insurance, PMI, HOA, and other costs divided by 12. Extra payments reduce payoff time and total interest.", "inputs": [["price", "Home price ($)", "number", 400000], ["down", "Down payment ($)", "number", 20], ["apr", "Interest rate (%)", "number", 6.81], ["years", "Loan term (years)", "number", 30], ["start", "Start month", "month", "2026-09"], ["tax", "Property tax", "number", 1.2], ["insurance", "Home insurance", "number", 1500], ["pmi", "PMI", "number", 0], ["hoa", "HOA", "number", 0], ["other", "Other costs", "number", 4000], ["increase", "Annual tax/insurance increase (%)", "number", 0], ["extra_monthly", "Extra monthly pay ($)", "number", 0], ["extra_yearly", "Extra yearly pay ($)", "number", 0], ["extra_once", "One-time extra pay ($)", "number", 0]]})
    elif slug == "loan-calculator":
        base.update({"engine": "loan_page", "desc": "Calculate amortized loan payments, deferred payment loan maturity value, and bond present value using the same three loan models shown on Calculator.net.", "formula": "Amortized payment uses an effective payback-period rate. Deferred payment compounds principal to maturity. Bond value discounts the predetermined due amount to the loan start.", "inputs": []})
    elif "auto loan" in text or ("car" in text and "loan" in text):
        base.update({"engine": "car_loan", "desc": "Estimate an auto loan payment including price, tax, fees, cash incentives, down payment, trade-in, amount owed on trade-in, and whether taxes and fees are financed.", "formula": "Loan amount = auto price - cash incentives - down payment - trade-in value + amount owed on trade-in, plus taxes and fees when included in the loan. Payment uses monthly amortization.", "inputs": [["price", "Auto Price ($)", "number", 50000], ["months", "Loan Term (months)", "number", 60], ["apr", "Interest Rate (%)", "number", 5], ["incentives", "Cash Incentives ($)", "number", 0], ["down", "Down Payment ($)", "number", 10000], ["trade", "Trade-in Value ($)", "number", 0], ["owed", "Amount Owed on Trade-in ($)", "number", 0], ["tax", "Sales Tax (%)", "number", 3], ["fees", "Title, Registration and Other Fees ($)", "number", 2800], ["include_fees", "Include taxes and fees in loan", "select", [["0", "No"], ["1", "Yes"]]]]})
    elif "loan" in text or "payment calculator" in text:
        base.update({"engine": "loan", "desc": "Calculate an installment loan payment, total paid, and interest cost from loan amount, term, and APR.", "formula": "Payment = P x r x (1+r)^n / ((1+r)^n - 1).", "inputs": [["amount", "Loan amount ($)", "number", 10000], ["apr", "Interest rate (%)", "number", 10], ["years", "Loan term (years)", "number", 5], ["months_extra", "Extra months", "number", 0]]})
    elif "compound interest" in text or "investment" in text or "savings" in text or "future value" in text:
        base.update({"engine": "compound", "desc": "Project future value from current principal, contribution amount, compound frequency, return, and time.", "formula": "Future value = principal growth + recurring contribution growth, compounded monthly.", "inputs": [["principal", "Initial investment ($)", "number", 10000], ["monthly", "Monthly contribution ($)", "number", 100], ["rate", "Annual return (%)", "number", 5], ["years", "Years to grow", "number", 10]]})
    elif "interest calculator" in text or "simple interest" in text:
        base.update({"engine": "cn_simple_interest", "desc": "Calculate simple interest and ending balance.", "formula": "Interest = principal x rate x time.", "inputs": [["principal", "Principal ($)", "number", 10000], ["rate", "Annual rate (%)", "number", 5], ["years", "Years", "number", 3]]})
    elif "retirement" in text or "401k" in text or "ira" in text or "pension" in text:
        base.update({"engine": "cn_retirement", "desc": "Estimate retirement savings from current balance, contribution, return, and years to grow.", "formula": "Retirement balance = current balance growth + recurring contribution growth.", "inputs": [["principal", "Current savings ($)", "number", 50000], ["monthly", "Monthly contribution ($)", "number", 600], ["rate", "Annual return (%)", "number", 6], ["years", "Years to grow", "number", 25], ["inflation", "Inflation (%)", "number", 3]]})
    elif "inflation" in text:
        base.update({"engine": "cn_inflation", "desc": "Adjust an amount for inflation over time.", "formula": "Future cost = amount x (1 + inflation rate)^years.", "inputs": [["amount", "Current amount ($)", "number", 1000], ["rate", "Inflation rate (%)", "number", 3], ["years", "Years", "number", 10]]})
    elif "tax" in text or "salary" in text or "take home" in text:
        base.update({"engine": "cn_tax_salary", "desc": "Estimate tax, after-tax pay, and monthly take-home pay.", "formula": "Take-home pay = income - estimated tax.", "inputs": [["income", "Annual income ($)", "number", 75000], ["taxrate", "Effective tax rate (%)", "number", 22], ["deductions", "Annual deductions ($)", "number", 0]]})
    elif "bmi" in text:
        base.update({"engine": "cn_bmi", "desc": "Calculate body mass index from height and weight.", "formula": "BMI = 703 x weight(lb) / height(in)^2.", "inputs": [["weight", "Weight (lb)", "number", 175], ["feet", "Height feet", "number", 5], ["inches", "Height inches", "number", 10]]})
    elif any(word in text for word in ["calorie", "bmr", "tdee", "macro", "protein", "carbohydrate"]):
        base.update({"engine": "cn_calorie", "desc": "Estimate daily calories using age, sex, height, weight, and activity level.", "formula": "Mifflin-St Jeor BMR adjusted by activity factor.", "inputs": [["weight", "Weight (lb)", "number", 175], ["feet", "Height feet", "number", 5], ["inches", "Height inches", "number", 10], ["age", "Age", "number", 35], ["sex", "Sex", "select", [["male", "Male"], ["female", "Female"]]], ["activity", "Activity", "select", [["1.2", "Sedentary"], ["1.375", "Light"], ["1.55", "Moderate"], ["1.725", "Active"]]] ]})
    elif "body fat" in text or "ideal weight" in text or "healthy weight" in text:
        base.update({"engine": "cn_body_metric", "desc": "Estimate healthy body metrics from height and weight.", "formula": "Uses BMI-based reference ranges for a quick planning estimate.", "inputs": [["weight", "Weight (lb)", "number", 175], ["feet", "Height feet", "number", 5], ["inches", "Height inches", "number", 10]]})
    elif any(word in text for word in ["pregnancy", "due date", "conception", "ovulation", "period"]):
        base.update({"engine": "cn_due_date", "desc": "Estimate a pregnancy due date or cycle milestone from a start date.", "formula": "Estimated due date = last menstrual period + 280 days.", "inputs": [["date", "Last period or start date", "date", "2026-01-01"], ["days", "Cycle length or offset days", "number", 280]]})
    elif "pace" in text:
        base.update({"engine": "cn_pace", "desc": "Calculate pace from distance and elapsed time.", "formula": "Pace = time / distance.", "inputs": [["distance", "Distance (miles)", "number", 3.1], ["hours", "Hours", "number", 0], ["minutes", "Minutes", "number", 30], ["seconds", "Seconds", "number", 0]]})
    elif "percent" in text or "discount" in text:
        base.update({"engine": "discount" if "discount" in text else "cn_percent", "desc": "Calculate percentages, percent change, and part-of-total values.", "formula": "Percentage = part / whole x 100.", "inputs": [["part", "Part", "number", 25], ["whole", "Whole", "number", 200], ["old", "Old value", "number", 100], ["new", "New value", "number", 125]]})
    elif "triangle" in text or "pythagorean" in text:
        base.update({"engine": "cn_triangle", "desc": "Calculate right-triangle sides, area, perimeter, and angles.", "formula": "c = sqrt(a^2 + b^2); area = a x b / 2.", "inputs": [["a", "Side a", "number", 3], ["b", "Side b", "number", 4]]})
    elif any(word in text for word in ["standard deviation", "statistics", "average", "mean median", "z score"]):
        base.update({"engine": "cn_stats", "desc": "Calculate summary statistics from a comma-separated number list.", "formula": "Mean = sum / count; standard deviation uses sample variance.", "inputs": [["values", "Values, comma-separated", "text", "12, 15, 19, 21, 22"]]})
    elif "random" in text or "dice" in text:
        base.update({"engine": "cn_random", "desc": "Generate a random number or dice-style result between two bounds.", "formula": "Random result = integer between minimum and maximum.", "inputs": [["min", "Minimum", "number", 1], ["max", "Maximum", "number", 6]]})
    elif "age" in text:
        base.update({"engine": "cn_age", "desc": "Calculate age from a birth date to a target date.", "formula": "Age = target date - birth date.", "inputs": [["birth", "Birth date", "date", "1990-01-01"], ["target", "Target date", "date", str(date.today())]]})
    elif "date" in text or "day counter" in text or "day of the week" in text:
        base.update({"engine": "cn_date", "desc": "Calculate days between dates and identify the day of the week.", "formula": "Day difference = end date - start date.", "inputs": [["start", "Start date", "date", "2026-01-01"], ["end", "End date", "date", str(date.today())]]})
    elif "time" in text or "hours" in text:
        base.update({"engine": "cn_hours", "desc": "Add hours and minutes or calculate a time duration.", "formula": "Total hours = hours + minutes / 60.", "inputs": [["hours", "Hours", "number", 8], ["minutes", "Minutes", "number", 30], ["rate", "Hourly rate ($)", "number", 25]]})
    elif "gpa" in text or "grade" in text:
        base.update({"engine": "cn_grade", "desc": "Calculate a weighted grade or GPA-style average.", "formula": "Weighted score = earned points / possible points x 100.", "inputs": [["earned", "Earned points", "number", 450], ["possible", "Possible points", "number", 500], ["credits", "Credits or weight", "number", 3]]})
    elif "concrete" in text:
        base.update({"engine": "concrete", "desc": "Estimate concrete volume in cubic yards from length, width, depth, and waste.", "formula": "Cubic yards = length x width x depth(ft) / 27.", "inputs": [["length", "Length (ft)", "number", 20], ["width", "Width (ft)", "number", 10], ["depth", "Depth (in)", "number", 4], ["waste", "Waste (%)", "number", 10]]})
    elif "subnet" in text:
        base.update({"engine": "cn_subnet", "desc": "Estimate IPv4 subnet size from a CIDR prefix.", "formula": "Addresses = 2^(32 - prefix).", "inputs": [["prefix", "CIDR prefix", "number", 24]]})
    elif "password" in text:
        base.update({"engine": "cn_password", "desc": "Generate a browser-side password from selected length.", "formula": "Password uses random characters from letters, numbers, and symbols.", "inputs": [["length", "Length", "number", 16]]})
    elif "tip" in text:
        base.update({"engine": "cn_tip", "desc": "Calculate tip, total bill, and split amount.", "formula": "Tip = bill x tip percentage.", "inputs": [["bill", "Bill amount ($)", "number", 80], ["tip", "Tip (%)", "number", 20], ["people", "People", "number", 2]]})
    return base


def calculator_net_calculators():
    if not CN_KEYWORDS.exists():
        return []
    imported = []
    for row in json.loads(CN_KEYWORDS.read_text(encoding="utf-8")):
        if row.get("page_type") == "widget":
            continue
        keyword = row["keyword"].replace(" widget", " Widget").strip()
        slug = row["slug"].replace(".html", "").replace(".php", "")
        if not row.get("is_tool_keyword"):
            continue
        cat = calculator_net_category(keyword, row.get("category", ""))
        group = calculator_net_group(keyword, cat)
        tpl = calculator_net_template(keyword, slug, cat)
        imported.append({
            "slug": slug,
            "title": keyword,
            "cat": cat,
            "group": group,
            "engine": tpl["engine"],
            "desc": tpl["desc"],
            "formula": tpl["formula"],
            "example": tpl["example"],
            "inputs": tpl["inputs"],
            "keyword_data": {},
            "generated": True,
            "source": "calculator.net keyword model",
        })
    return imported


def base_and_supplemental(data):
    existing = [normalized_calc(c) for c in data["calculators"]]
    existing_slugs = {c["slug"] for c in existing}
    cn_extra = [c for c in calculator_net_calculators() if c["slug"] not in existing_slugs]
    existing_slugs.update(c["slug"] for c in cn_extra)
    extra = [c for c in supplemental_calculators() if c["slug"] not in existing_slugs]
    calculators = existing + cn_extra + extra
    metrics = load_google_keyword_metrics()
    for calc in calculators:
        match = metrics.get(calc["slug"])
        if not match and not calc.get("generated"):
            match = metrics.get(slugify_text(calc["title"]))
        if match:
            calc["keyword_data"] = dict(match)
            calc["seo_keyword"] = match["keyword"]
            calc["title"] = smart_title(calc["title"])
        else:
            calc["keyword_data"] = {}
    title_counts = Counter(slugify_text(calc["title"]) for calc in calculators)
    for calc in calculators:
        if title_counts[slugify_text(calc["title"])] > 1 and not calc.get("seo_keyword"):
            calc["seo_context_label"] = f"{display_group(calculator_group(calc))} {calc['cat']}"
    return calculators


def primary_keyword(calc):
    return calc.get("seo_keyword") or str(calc["title"]).lower()


def seo_keywords(calc):
    keyword = primary_keyword(calc)
    group = display_group(calculator_group(calc)).lower()
    cat = f"{calc['cat'].lower()} calculators"
    variants = [
        keyword,
        f"free {keyword}",
        f"online {keyword}",
        f"{keyword} with formula",
        group,
        cat,
    ]
    seen = []
    for item in variants:
        clean = " ".join(str(item).lower().split())
        if clean and clean not in seen:
            seen.append(clean)
    return seen[:7]


def seo_title(calc):
    title = smart_title(primary_keyword(calc))
    if calc.get("seo_context_label"):
        context = smart_title(calc["seo_context_label"])
        candidate = f"{title} | {context}"
        if len(candidate) <= 62:
            return candidate
        candidate = f"{title} | {smart_title(calc['cat'])}"
        if len(candidate) <= 62:
            return candidate
    candidate = f"{title} | Free Online Calculator"
    if len(candidate) <= 62:
        return candidate
    return f"{smart_title(calc['title'])} | NS Calculators"


def seo_description(calc):
    keyword = primary_keyword(calc)
    if calc.get("engine") == "linear_convert":
        return f"Use this free {keyword} to convert units instantly with the formula, example, and related conversion calculators."
    if calc.get("engine") in ("cn_mortgage", "loan_page", "car_loan"):
        return f"Use this free {keyword} for US planning with instant results, payment details, charts, formulas, and no signup."
    return f"Use this free {keyword} for instant answers with clear inputs, formulas, examples, related tools, and no signup."


def keyword_section(calc):
    return ""



def keyword_score(calc):
    kd = calc.get("keyword_data") or {}
    searches = int(kd.get("monthly_searches") or 0)
    comp = int(kd.get("competition_index") or 0)
    yoy = str(kd.get("yoy") or "")
    growth = 20 if yoy.startswith("+") else -8 if yoy.startswith("-") else 0
    return searches * (1 + max(0, 60 - comp) / 80) + growth


def card(calc, label=None, compact=False):
    pill_label = label or calc["cat"]
    label_html = f'<span class="pill icon-pill">{category_icon(calc["cat"], "pill-icon")}{h(pill_label)}</span>'
    klass = "tool-card compact" if compact else "tool-card"
    return f"""<a class="{klass}" href="/{h(calc['slug'])}/">{label_html}<h3>{h(calc['title'])}</h3><p>{h(calc['desc'])}</p></a>"""


def input_html(field):
    fid, label, ftype, default = field
    if ftype == "hidden":
        return f'<input id="{h(fid)}" type="hidden" value="{h(default)}">'
    if ftype == "select":
        opts = "".join(f'<option value="{h(v)}">{h(t)}</option>' for v, t in default)
        control = f'<select id="{h(fid)}">{opts}</select>'
    elif ftype in ("text", "date"):
        control = f'<input id="{h(fid)}" type="{h(ftype)}" value="{h(default)}">'
    else:
        control = f'<input id="{h(fid)}" type="{h(ftype)}" step="any" value="{h(default)}">'
    return f'<div class="field"><label for="{h(fid)}">{h(label)}</label>{control}</div>'


def compound_options(selected="monthly"):
    options = [
        ("annually", "Annually (APY)"),
        ("semiannually", "Semi-annually"),
        ("quarterly", "Quarterly"),
        ("monthly", "Monthly (APR)"),
        ("semimonthly", "Semi-monthly"),
        ("biweekly", "Biweekly"),
        ("weekly", "Weekly"),
        ("daily", "Daily"),
        ("continuously", "Continuously"),
    ]
    return "".join(f'<option value="{h(value)}"{" selected" if value == selected else ""}>{h(label)}</option>' for value, label in options)


def payback_options(selected="month"):
    options = [
        ("daily", "Every Day"),
        ("weekly", "Every Week"),
        ("biweekly", "Every 2 Weeks"),
        ("halfmonth", "Every Half Month"),
        ("month", "Every Month"),
        ("quarter", "Every Quarter"),
        ("halfyear", "Every 6 Months"),
        ("year", "Every Year"),
    ]
    return "".join(f'<option value="{h(value)}"{" selected" if value == selected else ""}>{h(label)}</option>' for value, label in options)


def loan_input_html():
    return f"""<div class="loan-mode-stack">
<section class="loan-mode-input" id="monthlyfixed"><h3>Amortized Loan</h3><p>Fixed payments paid periodically until the loan is paid off.</p><div class="fields loan-fields">
<div class="field"><label for="l_amount">Loan Amount</label><input id="l_amount" type="number" step="any" value="100000"></div>
<div class="field"><label for="l_rate">Interest Rate (%)</label><input id="l_rate" type="number" step="any" value="6"></div>
<div class="field"><label for="l_years">Loan Term Years</label><input id="l_years" type="number" step="any" value="10"></div>
<div class="field"><label for="l_months">Loan Term Months</label><input id="l_months" type="number" step="any" value="0"></div>
<div class="field"><label for="l_compound">Compound</label><select id="l_compound">{compound_options("monthly")}</select></div>
<div class="field"><label for="l_payback">Pay Back</label><select id="l_payback">{payback_options("month")}</select></div>
</div><div class="calc-actions loan-panel-actions"><button class="btn primary calc-btn" data-engine="loan_page" type="button">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div></section>
<section class="loan-mode-input" id="intheend"><h3>Deferred Payment Loan</h3><p>One lump sum due at loan maturity.</p><div class="fields loan-fields">
<div class="field"><label for="d_amount">Loan Amount</label><input id="d_amount" type="number" step="any" value="100000"></div>
<div class="field"><label for="d_rate">Interest Rate (%)</label><input id="d_rate" type="number" step="any" value="6"></div>
<div class="field"><label for="d_years">Loan Term Years</label><input id="d_years" type="number" step="any" value="10"></div>
<div class="field"><label for="d_months">Loan Term Months</label><input id="d_months" type="number" step="any" value="0"></div>
<div class="field field-wide"><label for="d_compound">Compound</label><select id="d_compound">{compound_options("annually")}</select></div>
</div><div class="calc-actions loan-panel-actions"><button class="btn primary calc-btn" data-engine="loan_page" type="button">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div></section>
<section class="loan-mode-input" id="fixedend"><h3>Bond</h3><p>Predetermined lump sum paid at loan maturity.</p><div class="fields loan-fields">
<div class="field"><label for="b_due">Predetermined Due Amount</label><input id="b_due" type="number" step="any" value="100000"></div>
<div class="field"><label for="b_rate">Interest Rate (%)</label><input id="b_rate" type="number" step="any" value="6"></div>
<div class="field"><label for="b_years">Loan Term Years</label><input id="b_years" type="number" step="any" value="10"></div>
<div class="field"><label for="b_months">Loan Term Months</label><input id="b_months" type="number" step="any" value="0"></div>
<div class="field field-wide"><label for="b_compound">Compound</label><select id="b_compound">{compound_options("annually")}</select></div>
</div><div class="calc-actions loan-panel-actions"><button class="btn primary calc-btn" data-engine="loan_page" type="button">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div></section>
</div>"""


def mortgage_input_html():
    def unit_field(fid, label, default, options, unit_default):
        opts = "".join(
            f'<option value="{h(value)}"{" selected" if value == unit_default else ""}>{h(text)}</option>'
            for value, text in options
        )
        return f"""<div class="field unit-field"><label for="{h(fid)}">{h(label)}</label><div class="input-unit"><input id="{h(fid)}" type="number" step="any" value="{h(default)}"><select id="{h(fid)}_unit" aria-label="{h(label)} unit">{opts}</select></div></div>"""

    down_units = [("percent", "%"), ("dollar", "$")]
    annual_money_percent = [("percent", "%"), ("dollar", "$/yr")]
    annual_percent = [("dollar", "$/yr"), ("percent", "%/yr")]
    return f"""
<div class="fields mortgage-fields">
<div class="field"><label for="price">Home price</label><div class="input-unit"><input id="price" type="number" step="any" value="400000"><span>$</span></div></div>
{unit_field("down", "Down payment", 20, down_units, "percent")}
<div class="field"><label for="apr">Interest rate</label><div class="input-unit"><input id="apr" type="number" step="any" value="6.81"><span>%</span></div></div>
<div class="field"><label for="years">Loan term</label><div class="input-unit"><input id="years" type="number" step="any" value="30"><span>years</span></div></div>
<div class="field"><label for="start">Start month</label><input id="start" type="month" value="2026-09"></div>
<div class="field field-wide option-field"><label class="checkline"><input id="include_costs" type="checkbox" checked> Include taxes, insurance, PMI, HOA and other costs</label></div>
</div>
<div class="fields mortgage-fields mortgage-cost-fields" id="mortgageCostFields">
{unit_field("tax", "Property tax", 1.2, annual_money_percent, "percent")}
{unit_field("insurance", "Home insurance", 1500, annual_money_percent, "dollar")}
{unit_field("pmi", "PMI", 0, annual_percent, "dollar")}
{unit_field("hoa", "HOA", 0, annual_percent, "dollar")}
{unit_field("other", "Other costs", 4000, annual_percent, "dollar")}
</div>
<details class="more-options">
<summary>More Options</summary>
<div class="fields mortgage-fields mortgage-extra-fields">
<div class="field"><label for="increase">Annual cost increase</label><div class="input-unit"><input id="increase" type="number" step="any" value="0"><span>%</span></div></div>
<div class="field"><label for="extra_monthly">Extra monthly pay</label><div class="input-unit"><input id="extra_monthly" type="number" step="any" value="0"><span>$</span></div></div>
<div class="field"><label for="extra_yearly">Extra yearly pay</label><div class="input-unit"><input id="extra_yearly" type="number" step="any" value="0"><span>$</span></div></div>
<div class="field"><label for="extra_once">One-time extra pay</label><div class="input-unit"><input id="extra_once" type="number" step="any" value="0"><span>$</span></div></div>
</div>
</details>"""


def opportunity_notice(calc):
    return ""


def home(site, calculators):
    return home_new(site, calculators)


def home_new(site, calculators):
    cats = Counter(c["cat"] for c in calculators)
    by_cat = defaultdict(list)
    for calc in calculators:
        by_cat[calc["cat"]].append(calc)
    featured = sorted(calculators, key=keyword_score, reverse=True)[:24]
    all_items_json = json.dumps(
        [{"title": c["title"], "slug": c["slug"], "desc": c["desc"], "cat": c["cat"], "keyword": primary_keyword(c)} for c in calculators],
        ensure_ascii=False,
    )
    popular_links = "".join(
        f"""<a href="/{h(c['slug'])}/"><span>{h(c['title'])}</span></a>"""
        for c in featured[:12]
    )
    category_cards = "".join(
        f"""<a class="home-category" data-home-category="{h(cat.lower())}" href="/{slugify_cat(cat)}/">{category_icon(cat, "home-category-icon")}<strong>{h(cat)}</strong><small>{h(category_desc(cat))}</small></a>"""
        for cat in CATEGORY_ORDER
        if cats.get(cat, 0)
    )
    faq_items = [
        ("Are these calculators for US and UK users?", "Yes. The site is written for English-language users, with many tools useful for US and UK everyday searches."),
        ("Do I need an account?", "No. Calculators run in the browser and do not require sign up."),
        ("Are the results professional advice?", "No. Use results as planning aids and verify important decisions with qualified sources."),
        ("How do I find a calculator?", "Search from the homepage or open a category page, then choose the calculator link from its grouped directory."),
        ("Can I use the converters on mobile?", "Yes. Pages are responsive and built for quick use on phones, tablets, and desktops."),
        ("Why group calculators inside each category?", "Groups make large category pages easier to scan while still keeping each calculator one click away."),
    ]
    faq_list = "".join(
        f"""<details class="faq-item"><summary>{h(q)}</summary><p>{h(a)}</p></details>"""
        for q, a in faq_items
    )
    sci_keys = ["7", "8", "9", "/", "sqrt(", "4", "5", "6", "*", "^", "1", "2", "3", "-", "pi", "0", ".", "%", "+", "e", "(", ")", "sin(", "cos(", "tan(", "log(", "ln(", "C", "Del", "="]
    sci_buttons = "".join(
        f"""<button type="button" data-sci-key="{h(key)}">{h(key)}</button>"""
        for key in sci_keys
    )
    body = f"""<main>
<section class="home-hero"><div class="wrap hero-stack">
<div class="hero-copy"><h1>Calculator Tools</h1><p>Free calculators for mortgage, loans, compound interest, BMI, auto loans, and unit conversions. Built for fast answers with formulas and no signup.</p></div>
<div class="search-panel wide-search" aria-label="Calculator search"><label for="siteSearch">Search calculators</label><div class="search-wrap"><input id="siteSearch" class="search" placeholder="Search calculators..." aria-label="Search calculators"><div id="searchResults" class="search-results"></div></div></div>
</div></section>
<section class="home-block"><div class="wrap"><h2>Calculator Categories</h2><div class="category-filter"><input id="categoryFilter" type="search" placeholder="Filter categories..." aria-label="Filter categories"></div><div class="home-category-grid">{category_cards}</div></div></section>
<section class="home-block browse-all"><div class="wrap browse-panel"><div><h2>Browse All Calculators</h2><p>Start with a main category, then choose the calculator that matches your task from its grouped directory.</p></div><a class="btn primary" href="/conversion-calculators/">Browse all calculators</a></div></section>
<section class="home-block"><div class="wrap scientific-panel"><div><h2>Scientific Calculator</h2><p>Use quick math functions directly from the homepage.</p></div><div class="scientific-widget"><input id="sciExpression" value="" placeholder="0" aria-label="Scientific expression"><button class="btn primary sci-run" id="sciRun" type="button">Calculate</button><div id="sciResult" class="mini-result">Ready</div><div class="sci-keypad">{sci_buttons}</div></div></div></section>
<section class="home-block popular-block"><div class="wrap"><h2>Most Popular Calculators</h2><div class="popular-list">{popular_links}</div></div></section>
<section class="home-block faq-section"><div class="wrap"><h2>Common Questions</h2><div class="faq-list">{faq_list}</div></div></section>
<section class="ad-band"><div class="wrap"><div class="ad-slot">Advertisement</div></div></section>
</main><script>window.NORTHSTAR_ITEMS={all_items_json};</script><script src="/assets/search.js"></script><script src="/assets/scientific.js"></script><script src="/assets/home.js"></script>"""
    return page(site, "Free Online Calculators | Mortgage, Loan & Unit Converters", "Free US-focused calculators for mortgage, loan, auto loan, compound interest, BMI, and unit conversions with instant answers, charts, and formulas.", "/", body, ["free online calculators", "mortgage calculator", "loan calculator", "auto loan calculator", "compound interest calculator", "unit converter"], [website_schema(site)])


def category_page(site, cat, items):
    title = f"Free {cat} Calculators | NS Calculators"
    desc = f"Free {cat.lower()} calculators for US users with instant answers, formulas, examples, and related tools."
    groups = defaultdict(list)
    for item in items:
        groups[calculator_group(item)].append(item)
    ordered_groups = GROUP_LABELS.get(cat) or sorted(groups)
    jump_links = "".join(
        f"""<a href="#{h(group_slug(group))}">{category_icon(cat, "jump-icon")}{h(display_group(group))}</a>"""
        for group in ordered_groups
        if groups.get(group)
    )
    sections = "".join(
        f"""<section class="category-section" id="{h(group_slug(group))}"><div class="category-section-head">{category_icon(cat, "section-icon")}<div><h2>{h(display_group(group))}</h2><p><strong>{len(groups[group]):,} calculators.</strong> {h(subgroup_desc(cat, group, groups[group]))}</p></div></div><div class="calculator-link-grid">{''.join(f'<a href="/{h(calc["slug"])}/">{h(calc["title"])}</a>' for calc in sorted(groups[group], key=lambda c: c["title"]))}</div></section>"""
        for group in ordered_groups
        if groups.get(group)
    )
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / {h(cat)} Calculators</div>
<section class="article wide category-directory"><div class="page-title-icon">{category_icon(cat, "title-icon")}<h1>{h(cat)} Calculators</h1></div><p class="lead">{h(category_desc(cat))}</p><nav class="category-jump-nav" aria-label="{h(cat)} calculator groups">{jump_links}</nav><div class="category-tools">{sections}</div></section></div></main>"""
    keywords = [f"{cat.lower()} calculators", f"free {cat.lower()} calculators", "online calculator", "calculator tools"]
    crumbs = [("Home", "/"), (f"{cat} Calculators", f"/{slugify_cat(cat)}/")]
    return page(site, title, desc, f"/{slugify_cat(cat)}/", body, keywords, [breadcrumb_schema(site, crumbs)], "CollectionPage")


def subgroup_desc(cat, group, items):
    sample = ", ".join(item["title"].replace(" Calculator", "") for item in items[:3])
    return f"{len(items):,} {cat.lower()} tools including {sample}."


def conversion_copy(calc):
    if calc.get("engine") != "linear_convert":
        return None
    source = ""
    target = ""
    factor = ""
    for field in calc.get("inputs", []):
        if field[0] == "value":
            source = str(field[1]).replace("Value in ", "")
        elif field[0] == "target":
            target = str(field[3])
        elif field[0] == "factor":
            factor = str(field[3])
    if not source or not target:
        return None
    return f"""
<h2>What this calculator does</h2><p>This tool converts a value entered in {h(source)} into {h(target)}. It is useful for quick checks, comparison tables, shopping, building estimates, recipes, science homework, and everyday unit changes.</p>
<h2>How to use it</h2><p>Enter the number of {h(source)} you want to convert. The calculator multiplies that value by the stored conversion factor and returns the answer in {h(target)}.</p>
<h2>Formula</h2><p class="formula">{h(calc['formula'])}</p>
<h2>Worked example</h2><p>{h(calc['example'])} For example, entering 10 gives 10 × {h(factor)}, expressed in {h(target)}.</p>
<h2>When to verify</h2><p>For scientific reporting, regulated work, medical dosing, engineering, construction, or commercial transactions, confirm rounding rules and source units with an authoritative reference.</p>
<h2>Frequently asked questions</h2><h3>Can I enter decimals?</h3><p>Yes. Decimal values are supported, which helps with small measurements and precise conversions.</p><h3>Why is the result rounded?</h3><p>The result is rounded for readability in the browser. Use the formula if you need more precision for a specialist workflow.</p>"""


def default_calculator_copy(calc):
    return f"""
<h2>How it works</h2><p>{h(calc['desc'])} Use the units shown in the calculator and review every assumption before using the result.</p>
<h2>Formula</h2><p class="formula">{h(calc['formula'])}</p>
<h2>Worked example</h2><p>{h(calc['example'])}</p>
<h2>Important assumptions</h2><p>This tool is designed for planning and comparison. Real-world prices, manufacturer ratings, building requirements, lender terms, electrical codes, tolerances, and product specifications can vary.</p>
<h2>Frequently asked questions</h2><h3>Is this calculator free?</h3><p>Yes. It runs in your browser and does not require an account.</p><h3>Are the results exact?</h3><p>The math is deterministic for the entered values, but the result depends on inputs and assumptions. Verify safety-critical, financial, code-related, towing, fitment, and manufacturer-specific decisions with authoritative information.</p>"""


def analysis_extra_html(calc):
    if calc.get("engine") == "cn_mortgage":
        return """<section class="mortgage-dashboard" aria-label="Mortgage result details">
<div class="section-head stack"><h2>Mortgage Summary</h2><p>Monthly payment, total cost, payoff trend, and amortization details.</p></div>
<div class="summary-grid" id="mortgageSummary"></div>
<div class="chart-grid">
<div class="chart-card compact-chart"><h3>Payment Breakdown</h3><canvas id="mortgagePie" width="380" height="210" aria-label="Mortgage payment breakdown pie chart"></canvas></div>
<div class="chart-card compact-chart"><h3>Loan Balance</h3><canvas id="mortgageLine" width="360" height="190" aria-label="Mortgage balance line chart"></canvas></div>
</div>
<div class="table-card cost-card"><h3>Monthly & Total Cost</h3><div class="table-scroll"><table class="data-table" id="mortgageCostTable"><thead><tr><th>Item</th><th>Monthly</th><th>Total</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Annual Amortization Schedule</h3><div class="table-scroll"><table class="data-table" id="mortgageSchedule"><thead><tr><th>Year</th><th>Interest</th><th>Principal</th><th>Ending Balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("engine") == "loan_page":
        return """<section class="loan-results" aria-label="Loan calculator results">
<div class="loan-result-panel" id="monthlyfixedr"><div class="section-head stack"><h2>Amortized Loan Results</h2><p>Fixed payment, total payments, total interest, and amortization table.</p></div><div class="summary-grid" id="loanSummary"></div><div class="loan-chart-row"><div class="chart-card compact-chart"><h3>Principal vs Interest</h3><canvas id="loanPie" width="360" height="180" aria-label="Amortized loan principal and interest pie chart" data-center-label="total"></canvas></div><div class="table-card loan-result-table"><h3>Results</h3><div class="table-scroll"><table class="data-table" id="loanResultTable"><tbody></tbody></table></div><button class="text-link table-toggle" type="button" data-toggle-table="loanAmortTable">View Amortization Table</button></div></div><div class="table-card is-collapsed" id="loanAmortTable"><h3>Amortization Table</h3><div class="table-scroll"><table class="data-table"><thead><tr><th>Period</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Balance</th></tr></thead><tbody id="loanAmortRows"></tbody></table></div></div></div>
<div class="loan-result-panel" id="intheendr"><div class="section-head stack"><h2>Deferred Payment Loan Results</h2><p>Single amount due at maturity with compounded interest.</p></div><div class="summary-grid" id="deferredSummary"></div><div class="loan-chart-row"><div class="chart-card compact-chart"><h3>Principal vs Interest</h3><canvas id="deferredPie" width="360" height="180" aria-label="Deferred loan principal and interest pie chart" data-center-label="total"></canvas></div><div class="table-card loan-result-table"><h3>Results</h3><div class="table-scroll"><table class="data-table" id="deferredResultTable"><tbody></tbody></table></div><button class="text-link table-toggle" type="button" data-toggle-table="deferredSchedule">View Schedule Table</button></div></div><div class="table-card is-collapsed" id="deferredSchedule"><h3>Schedule Table</h3><div class="table-scroll"><table class="data-table"><thead><tr><th>Year</th><th>Starting Balance</th><th>Interest</th><th>Ending Balance</th></tr></thead><tbody id="deferredRows"></tbody></table></div></div></div>
<div class="loan-result-panel" id="fixedendr"><div class="section-head stack"><h2>Bond Results</h2><p>Amount received at the start and interest discount to the predetermined due amount.</p></div><div class="summary-grid" id="bondSummary"></div><div class="loan-chart-row"><div class="chart-card compact-chart"><h3>Principal vs Interest</h3><canvas id="bondPie" width="360" height="180" aria-label="Bond present value and interest pie chart" data-center-label="total"></canvas></div><div class="table-card loan-result-table"><h3>Results</h3><div class="table-scroll"><table class="data-table" id="bondResultTable"><tbody></tbody></table></div><button class="text-link table-toggle" type="button" data-toggle-table="bondSchedule">View Schedule Table</button></div></div><div class="table-card is-collapsed" id="bondSchedule"><h3>Schedule Table</h3><div class="table-scroll"><table class="data-table"><thead><tr><th>Year</th><th>Starting Value</th><th>Interest</th><th>Ending Value</th></tr></thead><tbody id="bondRows"></tbody></table></div></div></div>
</section>"""
    if calc.get("engine") == "cn_age":
        return """<section class="mortgage-dashboard age-dashboard" aria-label="Age result details">
<div class="section-head stack"><h2>Age Analysis</h2><p>See the result as calendar age, total time lived, birthday progress, and upcoming age milestones.</p></div>
<div class="summary-grid" id="ageSummary"></div>
<div class="chart-grid">
<div class="chart-card"><h3>Age in Time Units</h3><canvas id="ageBars" width="560" height="280" aria-label="Age in years, months, weeks and days bar chart"></canvas></div>
<div class="chart-card"><h3>Birthday Year Progress</h3><canvas id="ageProgress" width="420" height="280" aria-label="Birthday year progress chart"></canvas></div>
</div>
<div class="table-card"><h3>Age Milestones</h3><div class="table-scroll"><table class="data-table" id="ageMilestones"><thead><tr><th>Milestone</th><th>Date</th><th>Time from target date</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("engine"):
        return """<section class="mortgage-dashboard generic-dashboard" aria-label="Calculator data analysis">
<div class="section-head stack"><h2>Result Summary</h2><p>Review the main answer, supporting values, chart breakdown, and calculation details.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid">
<div class="chart-card"><h3>Result Breakdown</h3><canvas id="genericChart" width="360" height="180" aria-label="Calculator result breakdown chart" data-chart-type="pie" data-center-label="total"></canvas></div>
</div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    return ""


def subgroup_page(site, cat, group, items):
    shown_group = display_group(group)
    title = f"{shown_group} Calculators | Northstar Calculators"
    desc = f"Browse {len(items):,} {shown_group.lower()} calculators in the {cat.lower()} category."
    cards = "".join(card(c, c["cat"]) for c in items)
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/{slugify_cat(cat)}/">{h(cat)}</a> / {h(group)}</div>
<section class="article wide"><h1>{h(shown_group)} Calculators</h1><p class="lead">{h(desc)}</p><div class="tool-grid category-list">{cards}</div></section></div></main>"""
    return page(site, title, desc, subgroup_path(cat, group), body)


def calculator_page(site, calc, related):
    title = seo_title(calc)
    desc = seo_description(calc)
    group = calculator_group(calc)
    if calc.get("engine") == "cn_mortgage":
        fields = mortgage_input_html()
    elif calc.get("engine") == "loan_page":
        fields = loan_input_html()
    else:
        fields = f"""<div class="fields">{''.join(input_html(f) for f in calc["inputs"])}</div>"""
    rel = "".join(card(c, compact=True) for c in related)
    content = conversion_copy(calc) or default_calculator_copy(calc)
    extra = analysis_extra_html(calc)
    if calc.get("engine") == "loan_page":
        calc_html = f"""<section class="calc loan-page-calc"><h2>Calculator</h2>{fields}<div class="result" id="result">Enter your values and select Calculate.</div></section>"""
    else:
        calc_html = f"""<section class="calc"><h2>Calculator</h2>{fields}<div class="calc-actions"><button class="btn primary calc-btn" data-engine="{h(calc['engine'])}">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div><div class="result" id="result">Enter your values and select Calculate.</div></section>"""
    primary_tool = f"""<div class="calculator-layout split-analysis"><div class="calculator-pane">{calc_html}</div><div class="analysis-pane">{extra}</div></div>""" if extra else calc_html
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/{slugify_cat(calc['cat'])}/">{h(calc['cat'])}</a> / {h(display_group(group))} / {h(calc['title'])}</div>
<article class="article calculator-article"><span class="pill icon-pill">{category_icon(calc["cat"], "pill-icon")}{h(calc['cat'])} calculator</span><div class="page-title-icon">{category_icon(calc["cat"], "title-icon")}<h1>{h(calc['title'])}</h1></div><p class="lead">{h(calc['desc'])}</p>{opportunity_notice(calc)}{keyword_section(calc)}
{primary_tool}
<div class="prose">{content}</div>
<h2>Related calculators</h2><div class="related">{rel}</div></article></div></main><script src="/assets/calculator.js"></script>"""
    crumbs = [
        ("Home", "/"),
        (f"{calc['cat']} Calculators", f"/{slugify_cat(calc['cat'])}/"),
        (display_group(group), f"/{slugify_cat(calc['cat'])}/#{group_slug(group)}"),
        (calc["title"], f"/{calc['slug']}/"),
    ]
    return page(site, title, desc, f"/{calc['slug']}/", body, seo_keywords(calc), [breadcrumb_schema(site, crumbs), calculator_schema(site, calc)])


def simple_page(site, path, title, desc, content):
    body = f"""<main class="main"><div class="wrap"><article class="article"><h1>{h(title)}</h1><p class="lead">{h(desc)}</p><div class="prose">{content}</div></article></div></main>"""
    return page(site, f"{title} | Northstar Calculators", desc, path, body)


def scientific_page(site):
    body = """<main class="main"><div class="wrap"><article class="article"><div class="crumb"><a href="/">Home</a> / Scientific Calculator</div><span class="pill">Math calculator</span><h1>Scientific Calculator</h1><p class="lead">Run arithmetic, percentages, powers, square roots, trigonometry, and logarithms in your browser.</p><section class="calc scientific-page"><h2>Calculator</h2><div class="mini-calc full"><input id="sciExpression" value="sqrt(144)+25%" aria-label="Scientific expression"><button class="btn primary" id="sciRun" type="button">Calculate</button><div id="sciResult" class="mini-result">Ready</div></div></section><div class="prose"><h2>Supported syntax</h2><p>Use operators such as +, -, *, /, ^, parentheses, percentages, sqrt(), sin(), cos(), tan(), log(), ln(), pi, and e.</p><h2>Example</h2><p>Entering sqrt(144)+25% returns 12.25.</p></div></article></div></main><script src="/assets/scientific.js"></script>"""
    return page(site, "Scientific Calculator | Northstar Calculators", "Free browser-based scientific calculator for arithmetic, percentages, powers, roots, trig, and logarithms.", "/scientific-calculator/", body)


def redirect_page(site, from_path, to_path, title):
    return f"""<!doctype html><html lang="{h(site['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta http-equiv="refresh" content="0; url={h(to_path)}"><link rel="canonical" href="{h(site_url(site, to_path))}"><meta name="robots" content="noindex"></head><body><p><a href="{h(to_path)}">Continue to {h(title)}</a></p></body></html>"""


def info_pages(site):
    about = simple_page(site, "/about/", "About Northstar Calculators", "Northstar Calculators publishes practical, browser-based calculators and unit converters for everyday questions.", """
<h2>What we publish</h2><p>Northstar Calculators is a free calculator library for users who need quick estimates, unit conversions, formulas, and examples. The site includes automotive, construction, conversion, cooking, electrical, financial, health, math, pets, science, time and date, and video tools.</p>
<h2>Our editorial approach</h2><p>Pages are built around a clear user task. Each calculator includes a visible formula or conversion factor, a worked example, and related tools so users can continue researching a topic without guessing what to open next.</p>
<h2>Important limitations</h2><p>Calculator results are planning aids. They are not financial, legal, medical, engineering, electrical, construction, automotive, or safety advice. Always verify important decisions with qualified professionals, manufacturers, official standards, or other authoritative sources.</p>
""")
    privacy = simple_page(site, "/privacy-policy/", "Privacy Policy", "This Privacy Policy explains how Northstar Calculators handles information when you use the website.", """
<h2>Information you enter</h2><p>Calculator inputs are processed in your browser for the purpose of showing a result. The static calculator pages do not require account registration.</p>
<h2>Usage data</h2><p>Like many websites, hosting providers, analytics tools, or advertising partners may process basic technical information such as page URL, browser type, device type, approximate location, referring page, and interaction data.</p>
<h2>Cookies and advertising</h2><p>Northstar Calculators may use cookies or similar technologies for analytics, site performance, advertising measurement, and ad personalization where allowed by law. Third-party advertising partners, including Google, may use cookies to serve ads based on a user's visits to this and other websites.</p>
<h2>Your choices</h2><p>You can control cookies through your browser settings. You can also review Google's advertising settings and choices through Google's own privacy and ads controls.</p>
<h2>Children's privacy</h2><p>This website is intended for a general audience and is not designed to collect personal information from children.</p>
<h2>Contact</h2><p>Questions about this policy can be sent through the contact page.</p>
""")
    terms = simple_page(site, "/terms/", "Terms of Use", "These Terms of Use describe the rules for using Northstar Calculators.", """
<h2>Use of the site</h2><p>You may use the calculators and converters for personal, educational, and general planning purposes. You agree not to misuse the site, interfere with its operation, or attempt to access systems without permission.</p>
<h2>No professional advice</h2><p>Results are estimates based on the values entered and the assumptions shown. The site does not provide professional advice. Verify financial, health, construction, electrical, vehicle, legal, and safety-related decisions with appropriate professionals or official sources.</p>
<h2>Accuracy</h2><p>We aim to provide useful formulas, conversion factors, and examples, but errors or omissions may occur. We do not guarantee that every result is complete, current, or suitable for your specific situation.</p>
<h2>Advertising and third-party links</h2><p>The site may display advertisements or link to third-party resources. We are not responsible for third-party websites, services, claims, or policies.</p>
<h2>Changes</h2><p>We may update these terms as the site changes. Continued use of the site means you accept the current terms.</p>
""")
    contact = simple_page(site, "/contact/", "Contact", "Contact Northstar Calculators about calculator issues, corrections, privacy questions, or general feedback.", """
<h2>How to reach us</h2><p>For corrections, feedback, privacy questions, or general inquiries, open an issue in the public project repository: <a href="https://github.com/lg-list/NSCalculators/issues">NS Calculators issues</a>.</p>
<h2>What to include</h2><p>Please include the calculator URL, the values you entered, the result you expected, and any authoritative source that supports the correction. This helps us review issues faster.</p>
<h2>Advertising and partnerships</h2><p>For advertising, partnership, or business inquiries, use the same project issue tracker and include a clear subject line.</p>
""")
    return {"/about/": about, "/privacy-policy/": privacy, "/terms/": terms, "/contact/": contact}


CSS = r'''
:root{--ink:#152033;--muted:#667085;--subtle:#8b96a8;--line:#dfe5ee;--bg:#f6f8fb;--card:#fff;--card-2:#f1f5fb;--brand:#173f73;--brand-dark:#0f2d55;--accent:#c0333a;--accent-muted:#8a3f47;--accent-soft:#fff3f4;--accent-line:#f0c8cd;--soft:#edf3fb;--shadow:0 18px 50px rgba(21,32,51,.10)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Arial,"Helvetica Neue",ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}.wrap{width:min(1180px,calc(100% - 32px));margin:auto}
.site-header{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(16px)}.nav{height:68px;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{display:inline-flex;align-items:center;gap:9px;font-size:18px;font-weight:850;letter-spacing:-.03em;white-space:nowrap}.brand-name{display:grid;gap:0;line-height:1.02}.brand-name strong{font-size:22px;color:var(--brand);letter-spacing:-.045em}.brand-name b{font-size:12px;color:var(--accent);letter-spacing:.025em}.brand b{color:var(--accent)}.brand-mark{display:inline-grid;place-items:center;width:38px;height:40px;border-radius:0;background:transparent;box-shadow:none;color:var(--brand)}.brand-mark svg{width:36px;height:36px;fill:none;stroke:currentColor;filter:drop-shadow(0 5px 8px rgba(23,63,115,.22))}.brand-mark circle{fill:var(--accent)}.navlinks{display:flex;align-items:center;gap:4px;color:var(--muted);font-size:13px;white-space:nowrap}.menu-group{position:relative}.menu-top{display:inline-flex;align-items:center;height:38px;padding:0 9px;border-radius:9px}.menu-top:after{content:"";width:0;height:0;margin-left:6px;border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid #8b96a8}.menu-group:hover .menu-top,.menu-top:focus{background:var(--soft);color:var(--brand)}.submenu{position:absolute;top:42px;left:0;min-width:210px;padding:8px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);display:none}.menu-group:hover .submenu,.menu-group:focus-within .submenu{display:grid;gap:2px}.submenu a{display:block;padding:9px 10px;border-radius:8px;color:#344054}.submenu a:hover{background:var(--soft);color:var(--brand)}.navlinks a:hover,.text-link:hover{color:var(--brand)}
.hero{background:linear-gradient(180deg,#fff 0%,#f7fafb 100%);border-bottom:1px solid var(--line);padding:54px 0 44px}.hero-grid{display:grid;grid-template-columns:minmax(0,1.12fr) minmax(340px,.88fr);gap:42px;align-items:center}.eyebrow{display:inline-block;margin-bottom:16px;color:var(--brand);font-size:12px;font-weight:850;letter-spacing:.14em;text-transform:uppercase}.hero h1{max-width:760px;margin:0 0 18px;font-size:clamp(42px,6vw,68px);line-height:1.02;letter-spacing:-.055em}.hero p{max-width:630px;margin:0 0 26px;color:var(--muted);font-size:18px}.hero-actions{display:flex;gap:12px;flex-wrap:wrap}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:44px;padding:12px 18px;border-radius:10px;font-weight:800;border:1px solid transparent;cursor:pointer;transition:transform .16s ease,box-shadow .16s ease,background .16s ease}.btn:active{transform:translateY(1px)}.primary{background:var(--brand);color:#fff}.primary:hover{background:var(--brand-dark);box-shadow:0 12px 28px rgba(31,111,100,.22)}.secondary{background:#fff;color:var(--ink);border-color:var(--line)}.secondary:hover{border-color:#b9c5d4}
.search-panel{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px;box-shadow:var(--shadow)}.search-panel label{display:block;margin-bottom:10px;font-weight:800}.search-wrap{position:relative}.search{width:100%;height:54px;padding:0 16px;border:1px solid #cfd7e4;border-radius:10px;font-size:16px;outline:none;background:#fff;color:var(--ink)}.search:focus{border-color:var(--brand);box-shadow:0 0 0 4px var(--soft)}.search-results{position:absolute;left:0;right:0;top:60px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);overflow:hidden;display:none}.search-results a{display:block;padding:12px 14px;border-bottom:1px solid var(--line)}.search-results a:last-child{border-bottom:0}.search-results small{display:block;color:var(--muted)}.quick-links{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}.quick-links a{font-size:13px;color:var(--brand);background:var(--soft);border-radius:999px;padding:7px 10px}
.stat-band{background:#fff;border-bottom:1px solid var(--line)}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;padding:20px 0}.stats div{display:grid;gap:0}.stats b{font-size:28px;line-height:1;color:var(--brand)}.stats span{color:var(--muted);font-size:13px}.section{padding:58px 0}.section.alt{background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)}.section-head.stack{max-width:720px;margin-bottom:24px}.section h2,.article h1{letter-spacing:-.04em;line-height:1.08}.section h2{margin:0 0 10px;font-size:34px}.section-head p,.feature-layout p,.proof p,.directory p{margin:0;color:var(--muted)}
.category-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.category-card,.tool-card,.method-card{display:block;background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease}.category-card:hover,.tool-card:hover{transform:translateY(-2px);border-color:#b8c7d8;box-shadow:0 14px 36px rgba(23,32,51,.08)}.category-card span,.metric{display:block;color:var(--brand);font-size:12px;font-weight:850}.category-card h3,.tool-card h3,.method-card h3{margin:6px 0 8px;font-size:18px;line-height:1.25}.category-card p,.tool-card p,.method-card p{margin:0;color:var(--muted);font-size:14px}.tool-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.tool-card{min-height:178px}.tool-card.compact{min-height:auto}.pill{display:inline-block;margin-bottom:10px;padding:4px 9px;border-radius:999px;background:var(--soft);color:var(--brand);font-size:12px;font-weight:850}.metric{margin-top:14px}
.feature-layout{display:grid;grid-template-columns:minmax(0,1fr) 360px;gap:30px;align-items:start}.opportunity-list{display:grid;gap:10px;margin-top:22px}.opportunity-row{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:15px 0;border-bottom:1px solid var(--line)}.opportunity-row span{font-weight:760}.opportunity-row b{color:var(--brand);white-space:nowrap}.method-card{background:var(--card-2)}.text-link{display:inline-block;margin-top:16px;color:var(--brand);font-weight:800}
.scientific-home{display:grid;grid-template-columns:minmax(0,.8fr) minmax(360px,1.2fr);gap:28px;align-items:center}.mini-calc{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;background:#fff;border:1px solid var(--line);border-radius:16px;padding:18px;box-shadow:0 14px 36px rgba(23,32,51,.07)}.mini-calc input{height:48px;border:1px solid #cfd7e4;border-radius:10px;padding:0 14px;font-size:17px}.mini-result{grid-column:1/-1;background:#eff8f5;border:1px solid #b8d8ce;border-radius:10px;padding:13px 14px;font-weight:800}.mini-calc.full{grid-template-columns:minmax(0,1fr) auto}
.proof{background:#f1f6f4}.proof-grid{display:grid;grid-template-columns:.82fr 1.18fr;gap:36px;align-items:start}.proof-points{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.proof-points div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px}.proof-points b{display:block;margin-bottom:6px}.proof-points span{color:var(--muted);font-size:14px}
.faq-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}.faq-grid div{background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px}.faq-grid h3{margin:0 0 8px;font-size:18px}.faq-grid p{margin:0;color:var(--muted);font-size:14px}
.directory{padding-top:52px}.directory-group{margin-top:24px}.directory-group h3{margin:0 0 12px}.directory-links{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}.directory-links a{padding:10px 12px;background:#fff;border:1px solid var(--line);border-radius:10px;color:#344054;font-size:14px}.directory-links a:hover{border-color:#b8c7d8;color:var(--brand)}
.main{padding:32px 0 72px}.article{max-width:850px}.article.wide{max-width:none}.crumb{font-size:13px;color:var(--muted);margin-bottom:28px}.crumb a{color:var(--brand)}.article h1{margin:0 0 14px;font-size:clamp(38px,5vw,58px)}.lead{font-size:18px;color:var(--muted);max-width:760px}.calc{margin:28px 0 42px;padding:24px;background:#fff;border:1px solid var(--line);border-radius:16px;box-shadow:0 10px 36px rgba(23,32,51,.06)}.calc h2{margin-top:0}.fields{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.field label{display:block;margin-bottom:6px;font-size:13px;font-weight:760}.field input,.field select{width:100%;height:46px;border:1px solid #cfd7e4;border-radius:10px;background:#fff;padding:0 12px;font-size:15px;color:var(--ink)}.calc-btn{margin-top:18px}.result{margin-top:18px;padding:18px;border:1px solid #b8d8ce;border-radius:12px;background:#eff8f5}.result strong{font-size:25px}.notice{margin:18px 0;padding:14px 16px;background:#fff;border:1px solid var(--line);border-radius:12px;color:#526071;font-size:14px}.seo-keywords{display:grid;grid-template-columns:minmax(0,1fr) minmax(220px,320px);gap:16px;align-items:center;margin:18px 0 8px;padding:16px;background:#fff;border:1px solid var(--line);border-radius:12px}.seo-keywords h2{margin:0 0 4px;font-size:18px;letter-spacing:-.01em}.seo-keywords p{margin:0;color:var(--muted);font-size:14px;line-height:1.45}.keyword-chip-list{display:flex;flex-wrap:wrap;gap:8px;justify-content:flex-end}.keyword-chip-list span{display:inline-flex;align-items:center;min-height:30px;padding:5px 9px;border-radius:999px;background:var(--accent-soft);border:1px solid var(--accent-line);color:var(--accent-muted);font-size:12px;font-weight:760}.prose h2{margin-top:38px;font-size:27px;letter-spacing:-.025em}.prose h3{font-size:19px}.prose p,.prose li{color:#3c495e}.formula{padding:16px 18px;border-left:4px solid var(--brand);background:#fff}.related{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}.category-list{margin-top:26px}
.category-directory .lead{margin-bottom:30px}.category-tools{display:grid;gap:22px;margin-top:28px}.category-section{background:#fff;border:1px solid var(--line);border-radius:14px;padding:22px}.category-section-head{display:grid;grid-template-columns:48px minmax(0,1fr);gap:14px;align-items:start;margin-bottom:16px}.category-section-head span{display:grid;place-items:center;width:48px;height:48px;border-radius:12px;background:var(--soft);color:var(--brand);font-weight:850}.category-section h2{margin:0 0 6px;font-size:24px;line-height:1.15;letter-spacing:-.025em}.category-section p{margin:0;color:var(--muted)}.calculator-link-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.calculator-link-grid a{display:block;padding:12px 13px;background:#f8fafc;border:1px solid var(--line);border-radius:10px;color:#27364b;font-weight:720;line-height:1.3}.calculator-link-grid a:hover{background:#fff;border-color:#b8c7d8;color:var(--brand);box-shadow:0 8px 22px rgba(21,32,51,.06)}
.footer{border-top:1px solid var(--line);background:#fff;padding:34px 0;color:var(--muted);font-size:13px}.footer-grid{display:grid;grid-template-columns:1fr auto;gap:24px;align-items:start}.footer-brand{color:var(--ink)}.footer p{max-width:580px;margin:12px 0 0}.footer-links{display:flex;gap:16px;flex-wrap:wrap}.table{width:100%;border-collapse:collapse;background:#fff;border:1px solid var(--line)}.table th,.table td{padding:10px 12px;border-bottom:1px solid var(--line);text-align:left}
.compact-hero{padding:34px 0 28px}.hero-stack{display:grid;gap:22px;justify-items:center;text-align:center}.hero-stack .hero-copy{max-width:820px}.compact-hero h1{margin:0 0 12px;font-size:clamp(36px,5vw,56px);line-height:1.03}.compact-hero p{margin:0 auto;color:var(--muted);font-size:17px;max-width:760px}.wide-search{width:min(760px,100%);padding:16px;text-align:left;box-shadow:0 10px 30px rgba(23,32,51,.07)}.ad-band{padding:16px 0;background:#fff;border-bottom:1px solid var(--line)}.ad-slot{display:grid;place-items:center;min-height:92px;border:1px dashed #bdc8d8;border-radius:12px;background:#f8fafc;color:#7a8798;font-size:13px}.section.tight{padding:34px 0}.section-row{display:flex;align-items:end;justify-content:space-between;gap:18px;margin-bottom:18px}.section-row h2{margin:0 0 6px}.section-row p{margin:0;color:var(--muted)}.carousel-actions{display:flex;gap:8px;flex-shrink:0}.icon-btn{width:42px;height:42px;border-radius:10px;border:1px solid var(--line);background:#fff;color:var(--ink);font-size:20px;font-weight:800;cursor:pointer}.icon-btn:hover{border-color:#b8c7d8;color:var(--brand)}.carousel{display:grid;grid-auto-flow:column;grid-auto-columns:minmax(260px,310px);gap:14px;overflow-x:auto;scroll-snap-type:x mandatory;scrollbar-width:thin;padding-bottom:6px}.carousel .tool-card,.carousel .faq-card{scroll-snap-align:start}.faq-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:20px;min-height:170px}.faq-card h3{margin:0 0 10px;font-size:18px;line-height:1.28}.faq-card p{margin:0;color:var(--muted);font-size:14px}.clean-categories .category-card{min-height:150px}
.home-hero{background:#fff;border-bottom:1px solid var(--line);padding:38px 0 30px}.home-hero .hero-stack{max-width:860px}.home-hero h1{margin:0 0 12px;font-size:clamp(40px,5vw,60px);line-height:1.02;letter-spacing:-.04em;text-align:center}.home-hero p{max-width:680px;margin:0 auto;color:var(--muted);font-size:17px;text-align:center}.home-block{padding:34px 0;background:var(--bg)}.home-block:nth-of-type(even){background:#fff}.home-block h2{margin:0 0 16px;font-size:30px;line-height:1.1;letter-spacing:-.03em}.home-block p{color:var(--muted)}.category-filter{margin:0 0 18px}.category-filter input{width:min(420px,100%);height:44px;border:1px solid #cfd7e4;border-radius:10px;padding:0 13px;font-size:15px;color:var(--ink);background:#fff}.home-category-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.home-category{display:grid;grid-template-columns:42px 1fr;gap:12px;align-items:start;min-height:132px;background:#fff;border:1px solid var(--line);border-radius:14px;padding:18px;transition:box-shadow .16s ease,border-color .16s ease,transform .16s ease}.home-category:hover{transform:translateY(-2px);border-color:#b8c7d8;box-shadow:0 12px 30px rgba(21,32,51,.08)}.category-icon{display:grid;place-items:center;width:42px;height:42px;border-radius:11px;background:var(--soft);color:var(--brand);font-weight:850;font-size:13px}.home-category strong{display:block;font-size:17px;color:var(--ink)}.home-category small{grid-column:2;color:var(--muted);font-size:13px;line-height:1.45}.browse-panel,.scientific-panel{display:grid;grid-template-columns:minmax(0,1fr) minmax(320px,460px);gap:20px;align-items:center;background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px}.browse-panel p,.scientific-panel p{margin:0;max-width:620px}.scientific-widget{display:grid;gap:10px}.scientific-widget input{height:50px;border:1px solid #cfd7e4;border-radius:10px;padding:0 14px;font-size:18px;color:var(--ink)}.sci-run{width:100%}.sci-keypad{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}.sci-keypad button{height:40px;border:1px solid var(--line);border-radius:9px;background:#fff;color:var(--ink);font-weight:760;cursor:pointer}.sci-keypad button:hover{background:var(--soft);color:var(--brand)}.popular-list{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.popular-list a{display:flex;justify-content:space-between;align-items:center;gap:12px;background:#fff;border:1px solid var(--line);border-radius:12px;padding:13px;min-height:58px}.popular-list a:hover{border-color:#b8c7d8;box-shadow:0 10px 26px rgba(21,32,51,.07)}.popular-list span{font-weight:760}.popular-list small{color:var(--muted);white-space:nowrap}.faq-list{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.faq-item{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}.faq-item summary{font-weight:800;cursor:pointer;color:var(--ink)}.faq-item p{color:var(--muted);margin:10px 0 0;line-height:1.55}
.cat-icon{display:inline-grid;place-items:center;flex:0 0 auto;width:42px;height:42px;border-radius:12px;background:var(--soft);color:var(--brand)}.cat-icon svg{width:23px;height:23px;fill:none;stroke:currentColor;stroke-width:2.15;stroke-linecap:round;stroke-linejoin:round}.menu-top{gap:7px}.nav-icon{width:20px;height:20px;border-radius:6px;background:transparent}.nav-icon svg{width:17px;height:17px;stroke-width:2.3}.card-icon,.home-category-icon,.section-icon,.title-icon{box-shadow:inset 0 0 0 1px rgba(23,63,115,.08)}.category-card .cat-icon{margin-bottom:12px}.category-card span:not(.cat-icon){display:block;color:var(--brand);font-size:12px;font-weight:850}.pill{display:inline-flex;align-items:center;gap:6px}.icon-pill{padding-left:5px}.pill-icon{width:18px;height:18px;border-radius:5px;background:transparent}.pill-icon svg{width:15px;height:15px;stroke-width:2.4}.page-title-icon{display:flex;align-items:center;gap:14px;margin-bottom:14px}.page-title-icon h1{margin:0}.title-icon{width:54px;height:54px;border-radius:14px}.title-icon svg{width:29px;height:29px}.section-icon{width:48px;height:48px}.link-icon{width:22px;height:22px;border-radius:7px;background:#fff;color:var(--brand)}.link-icon svg{width:15px;height:15px;stroke-width:2.4}.category-section p strong{color:var(--ink)}.calculator-link-grid a{display:flex;align-items:center;gap:9px;min-height:48px;padding:10px 12px}.home-category-icon{grid-row:1/3}
.brand-mark svg{width:36px;height:36px;fill:none;stroke:var(--brand);stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round}.brand-mark rect{fill:rgba(232,240,251,.75);stroke:var(--brand)}.brand-mark .logo-screen{stroke:#0f2d55;stroke-width:3.1}.brand-mark .logo-accent{stroke:var(--accent);stroke-width:4}.navlinks{display:flex!important}.all-calculators-menu .menu-top{font-size:15px;font-weight:850;color:var(--ink);padding:0 13px}.all-calculators-menu .submenu{left:auto;right:0;width:min(760px,calc(100vw - 32px));grid-template-columns:repeat(3,1fr);gap:6px;padding:12px}.all-calculators-menu:hover .submenu,.all-calculators-menu:focus-within .submenu{display:grid}.mega-menu a{display:grid;grid-template-columns:22px minmax(0,1fr);column-gap:8px;row-gap:0;align-items:center;min-height:42px;padding:8px 9px}.mega-menu a span{font-weight:760;color:#27364b;line-height:1.2}.mega-menu a small{grid-column:2;color:var(--muted);font-size:11px;line-height:1.2}.mega-menu a:hover span{color:var(--brand)}
.category-directory .lead{margin-bottom:18px}.category-jump-nav{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 22px}.category-jump-nav a{display:inline-flex;align-items:center;gap:7px;min-height:34px;padding:6px 10px;background:#fff;border:1px solid var(--line);border-radius:9px;color:#344054;font-size:13px;font-weight:760}.category-jump-nav a:hover{border-color:#b8c7d8;color:var(--brand);background:var(--soft)}.jump-icon{width:18px;height:18px;border-radius:5px;background:transparent}.jump-icon svg{width:14px;height:14px;stroke-width:2.35}.category-tools{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px}.category-section{padding:16px;border-radius:12px}.category-section-head{grid-template-columns:34px minmax(0,1fr);gap:10px;margin-bottom:12px}.section-icon{width:34px;height:34px;border-radius:9px}.section-icon svg{width:19px;height:19px}.category-section h2{font-size:21px;margin-bottom:3px}.category-section p{font-size:14px;line-height:1.45}.calculator-link-grid{grid-template-columns:1fr;gap:8px}.calculator-link-grid a{min-height:42px;padding:8px 10px;border-radius:8px;font-size:13px;font-weight:720}.link-icon{width:18px;height:18px}.link-icon svg{width:13px;height:13px}
.lead,.home-hero p,.section-head p,.home-block p,.browse-panel p,.scientific-panel p,.category-section p,.faq-item p,.tool-card p,.method-card p{color:#5f6d80}.home-category small,.popular-list small,.search-results small,.mega-menu a small{color:#778295}.cat-icon,.category-icon{background:linear-gradient(135deg,#f3f7fc,#fff);color:var(--brand);box-shadow:inset 0 0 0 1px rgba(23,63,115,.09)}.cat-icon svg>*:last-child{stroke:var(--accent)}.nav-icon,.pill-icon,.jump-icon,.link-icon{background:transparent;box-shadow:none}.link-icon,.jump-icon{color:var(--brand)}.category-card span:not(.cat-icon){color:var(--brand)}.brand-name b{color:var(--accent)}.menu-group:hover .menu-top,.submenu a:hover,.sci-keypad button:hover{background:var(--accent-soft);color:var(--accent)}.category-jump-nav a:hover,.calculator-link-grid a:hover,.home-category:hover,.popular-list a:hover{border-color:var(--accent-line)}.result,.mini-result{background:#fff7f8;border-color:var(--accent-line)}.formula{border-left-color:var(--accent)}
.category-directory .calculator-link-grid a{display:block;min-height:auto;padding:9px 10px;line-height:1.32;overflow-wrap:anywhere}
.mortgage-dashboard{margin:10px 0 42px}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0 18px}.summary-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}.summary-card span{display:block;color:#667085;font-size:12px;font-weight:760}.summary-card strong{display:block;margin-top:5px;color:var(--ink);font-size:22px;line-height:1.15}.summary-card small{display:block;margin-top:5px;color:#778295;line-height:1.35}.chart-grid{display:grid;grid-template-columns:minmax(260px,1fr) minmax(320px,1.3fr);gap:14px}.chart-card,.table-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 10px 28px rgba(21,32,51,.05)}.chart-card h3,.table-card h3{margin:0 0 12px;font-size:18px}.chart-card canvas{display:block;max-width:100%;height:auto;margin:0 auto}.table-card{margin-top:14px}.table-scroll{overflow:auto}.data-table{width:100%;border-collapse:collapse;font-size:13px}.data-table th,.data-table td{padding:10px 11px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}.data-table th:first-child,.data-table td:first-child{text-align:left}.data-table th{color:#344054;background:#f8fafc;font-weight:850}.data-table td{color:#344054}
.calculator-article{max-width:960px}.calculator-article .pill{font-size:12px;padding:5px 9px;margin-bottom:10px}.calculator-article .pill-icon{width:16px;height:16px}.calculator-article .page-title-icon{gap:10px;margin-bottom:6px}.calculator-article .title-icon{width:42px;height:42px;border-radius:11px}.calculator-article .title-icon svg{width:23px;height:23px}.calculator-article h1{font-size:clamp(30px,4vw,44px);margin:0}.calculator-article .lead{font-size:16px;line-height:1.5;max-width:760px;margin:0 0 14px}.calculator-article .notice{margin:10px 0;padding:10px 12px}.calculator-article .calc{margin:14px 0 24px;padding:18px;border-radius:14px}.calculator-article .calc h2{font-size:22px;margin:0 0 12px;letter-spacing:-.02em}.calculator-article .fields{gap:10px}.calculator-article .field label{margin-bottom:5px}.calculator-article .field input,.calculator-article .field select{height:42px;border-radius:9px}.calculator-article .calc-btn{margin-top:12px}.calculator-article .result{margin-top:12px;padding:14px}.calculator-article .result strong{font-size:22px}.calculator-article .mortgage-dashboard{margin-top:6px}
.calculator-article:has(.split-analysis){max-width:none}.calculator-layout.split-analysis{display:grid;grid-template-columns:minmax(300px,380px) minmax(0,1fr);gap:18px;align-items:start;margin:14px 0 28px}.calculator-pane{position:sticky;top:88px}.calculator-pane .calc{margin:0}.analysis-pane .mortgage-dashboard{margin:0}.analysis-pane .section-head.stack{margin-bottom:12px}.analysis-pane .section-head h2{font-size:24px;margin-bottom:6px}.analysis-pane .summary-grid{grid-template-columns:repeat(2,1fr);margin:12px 0 14px}.analysis-pane .chart-grid{grid-template-columns:1fr;gap:12px}.analysis-pane .chart-card,.analysis-pane .table-card{padding:14px}.analysis-pane .chart-card canvas{max-height:none}.analysis-pane .data-table th,.analysis-pane .data-table td{padding:8px 9px}
.calculator-article:has(#mortgageSummary) .calculator-layout.split-analysis{grid-template-columns:minmax(400px,470px) minmax(0,1fr);gap:16px}.calculator-article:has(#mortgageSummary) .calc{padding:14px}.calculator-article:has(#mortgageSummary) .calc h2{font-size:20px;margin-bottom:10px}.calculator-article:has(#mortgageSummary) .fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.calculator-article:has(#mortgageSummary) .field label{font-size:12px;margin-bottom:3px}.calculator-article:has(#mortgageSummary) .field input,.calculator-article:has(#mortgageSummary) .field select{height:36px;padding:0 10px;font-size:14px}.calculator-article:has(#mortgageSummary) .calc-btn{min-height:38px;margin-top:10px;padding:9px 14px}.calculator-article:has(#mortgageSummary) .result{padding:10px 12px;margin-top:10px;font-size:13px}.calculator-article:has(#mortgageSummary) .result strong{font-size:20px}.calculator-article:has(#mortgageSummary) .analysis-pane .section-head h2{font-size:21px}.calculator-article:has(#mortgageSummary) .analysis-pane .section-head p{font-size:13px;line-height:1.35}.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:8px 0 10px}.calculator-article:has(#mortgageSummary) .summary-card{padding:10px;border-radius:10px}.calculator-article:has(#mortgageSummary) .summary-card strong{font-size:17px}.calculator-article:has(#mortgageSummary) .summary-card small{font-size:11px;line-height:1.25}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-card,.calculator-article:has(#mortgageSummary) .analysis-pane .table-card{padding:10px;border-radius:10px}.calculator-article:has(#mortgageSummary) .chart-card h3,.calculator-article:has(#mortgageSummary) .table-card h3{font-size:15px;margin-bottom:8px}.calculator-article:has(#mortgageSummary) .compact-chart canvas{max-height:230px}.calculator-article:has(#mortgageSummary) .table-card{margin-top:10px}.calculator-article:has(#mortgageSummary) .data-table{font-size:12px}.calculator-article:has(#mortgageSummary) .data-table th,.calculator-article:has(#mortgageSummary) .data-table td{padding:6px 7px}
.calculator-article .result{background:linear-gradient(135deg,#0f2d55,#173f73);border-color:#0f2d55;color:#e8f1ff;box-shadow:0 14px 32px rgba(15,45,85,.22)}.calculator-article .result strong{display:block;color:#fff;font-size:clamp(28px,3.2vw,36px);line-height:1.05;letter-spacing:-.035em;margin-bottom:5px}.calculator-article:has(#mortgageSummary) .result{padding:14px 16px;margin-top:10px;border-radius:12px;font-size:14px;line-height:1.45}.calculator-article:has(#mortgageSummary) .result strong{font-size:30px;line-height:1}
.calculator-article .field label,.calculator-article .field input,.calculator-article .field select{font-size:16px}
.input-unit{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;border:1px solid #cfd7e4;border-radius:9px;background:#fff;overflow:hidden}.input-unit input,.input-unit select{border:0!important;border-radius:0!important;height:42px!important}.input-unit input{min-width:0}.input-unit select,.input-unit span{height:42px;display:grid;place-items:center;border-left:1px solid #dfe5ee;background:#f8fafc;color:#344054;padding:0 10px;font-weight:760}.input-unit select{min-width:72px}.field-wide{grid-column:1/-1}.checkline{display:flex!important;align-items:center;gap:10px;min-height:42px;margin:0!important;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#f8fafc;color:var(--ink);font-size:16px!important}.checkline input{width:18px;height:18px;accent-color:var(--brand)}.mortgage-cost-fields[hidden],.mortgage-cost-fields.is-hidden{display:none!important}.calculator-article:has(#mortgageSummary) .field label{font-size:16px;margin-bottom:4px}.calculator-article:has(#mortgageSummary) .field input,.calculator-article:has(#mortgageSummary) .field select{font-size:16px}.calculator-article:has(#mortgageSummary) .field>input,.calculator-article:has(#mortgageSummary) .field>select{height:42px;padding:0 10px}.calculator-article:has(#mortgageSummary) .mortgage-fields{gap:9px;margin-top:9px}.calculator-article:has(#mortgageSummary) .mortgage-fields:first-child{margin-top:0}
.calc-actions{display:flex;gap:10px;align-items:center;margin-top:14px}.calc-actions .calc-btn{margin-top:0;flex:1}.clear-btn{min-width:92px}.more-options{margin-top:10px;border:1px solid var(--line);border-radius:10px;background:#fff}.more-options summary{min-height:42px;display:flex;align-items:center;padding:0 12px;cursor:pointer;color:var(--brand);font-size:16px;font-weight:850}.more-options summary::marker{color:var(--accent)}.more-options .mortgage-fields{padding:0 12px 12px}.calculator-article:has(#mortgageSummary) .calc-actions{margin-top:10px}.calculator-article:has(#mortgageSummary) .calc-actions .calc-btn,.calculator-article:has(#mortgageSummary) .clear-btn{min-height:42px;font-size:16px;padding:9px 14px}
.loan-mode-stack{display:grid;gap:12px}.loan-mode-input{padding:12px;border:1px solid var(--line);border-radius:12px;background:#f8fafc}.loan-mode-input h3{margin:0 0 4px;font-size:18px;letter-spacing:-.015em}.loan-mode-input p{margin:0 0 10px;color:var(--muted);font-size:13px;line-height:1.35}.loan-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.loan-results{display:grid;gap:14px}.loan-result-panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:0 10px 28px rgba(21,32,51,.05)}.loan-result-panel .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 12px}.loan-chart-row{display:grid;grid-template-columns:minmax(260px,.9fr) minmax(260px,1fr);gap:12px;align-items:start}.loan-result-table{margin-top:0}.table-toggle{margin-top:10px;border:0;background:transparent;padding:0;cursor:pointer}.is-collapsed{display:none}.calculator-article:has(.loan-results) .calculator-layout.split-analysis{grid-template-columns:minmax(430px,500px) minmax(0,1fr)}.calculator-article:has(.loan-results) .result strong{font-size:30px}.calculator-article:has(.loan-results) .calc{padding:14px}.calculator-article:has(.loan-results) .chart-card canvas{max-height:none}
@media(max-width:1180px){.navlinks{display:none}}
@media(max-width:1100px){.category-tools{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.hero-grid,.feature-layout,.proof-grid,.scientific-home,.browse-panel,.scientific-panel,.chart-grid,.calculator-layout.split-analysis,.seo-keywords{grid-template-columns:1fr}.calculator-pane{position:static}.keyword-chip-list{justify-content:flex-start}.category-grid,.tool-grid,.home-category-grid,.popular-list,.summary-grid{grid-template-columns:repeat(2,1fr)}.category-tools{grid-template-columns:repeat(2,1fr)}.directory-links{grid-template-columns:repeat(2,1fr)}.proof-points,.faq-grid,.faq-list,.related{grid-template-columns:1fr 1fr}.search-panel{box-shadow:none}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.nav{height:64px}.brand{font-size:16px}.brand-mark{width:34px;height:34px}.all-calculators-menu .submenu{grid-template-columns:1fr;right:-4px;max-height:72vh;overflow:auto}.hero{padding:32px 0 26px}.hero h1{font-size:36px}.home-hero{padding:30px 0 24px}.home-hero h1{font-size:38px}.hero-actions,.footer-grid,.mini-calc,.mini-calc.full{display:grid;grid-template-columns:1fr}.category-grid,.tool-grid,.home-category-grid,.fields,.directory-links,.proof-points,.faq-grid,.faq-list,.popular-list,.related,.calculator-link-grid,.summary-grid{grid-template-columns:1fr}.section{padding:42px 0}.section.tight,.home-block{padding:28px 0}.section-row{align-items:start}.article h1{font-size:36px}.calculator-article h1{font-size:30px}.calculator-article .lead{font-size:15px;margin-bottom:10px}.calculator-article .calc{padding:14px;margin:10px 0 20px}.calculator-article .calc h2{font-size:20px}.calculator-article .field input,.calculator-article .field select{height:40px}.page-title-icon{align-items:flex-start}.title-icon{width:48px;height:48px}.category-section{padding:18px}.category-section-head{grid-template-columns:1fr}.stats{gap:12px}.carousel{grid-auto-columns:82vw}.sci-keypad{grid-template-columns:repeat(4,1fr)}.ad-slot{min-height:76px}}
'''

SEARCH_JS = r'''
(function(){
  const items = window.NORTHSTAR_ITEMS || [];
  const basePath = window.NORTHSTAR_BASE_PATH || "";
  const q = document.getElementById("siteSearch");
  const box = document.getElementById("searchResults");
  if (!q || !box) return;
  q.addEventListener("input", () => {
    const s = q.value.toLowerCase().trim();
    if (!s) {
      box.style.display = "none";
      box.innerHTML = "";
      return;
    }
    const r = items.filter(x => (x.title + " " + x.desc + " " + x.cat + " " + (x.keyword || "")).toLowerCase().includes(s)).slice(0, 8);
    box.innerHTML = r.map(x => `<a href="${basePath}/${x.slug}/"><strong>${x.title}</strong><small>${x.cat}: ${x.desc}</small></a>`).join("");
    box.style.display = r.length ? "block" : "none";
  });
})();
'''

HOME_JS = r'''
(function(){
  const filter = document.getElementById("categoryFilter");
  if (filter) {
    const cards = Array.from(document.querySelectorAll("[data-home-category]"));
    filter.addEventListener("input", () => {
      const query = filter.value.toLowerCase().trim();
      cards.forEach(card => {
        card.style.display = card.textContent.toLowerCase().includes(query) ? "" : "none";
      });
    });
  }
  document.addEventListener("click", event => {
    const key = event.target.closest("[data-sci-key]");
    if (!key) return;
    const input = document.getElementById("sciExpression");
    const run = document.getElementById("sciRun");
    if (!input) return;
    const value = key.getAttribute("data-sci-key");
    if (value === "C") {
      input.value = "";
      input.focus();
      return;
    }
    if (value === "Del") {
      input.value = input.value.slice(0, -1);
      input.focus();
      return;
    }
    if (value === "=") {
      if (run) run.click();
      return;
    }
    input.value += value;
    input.focus();
  });
})();
'''

CALC_JS = r'''
const $=s=>document.querySelector(s), V=id=>parseFloat(document.getElementById(id)?.value||0);
const F=(n,d=2)=>Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:d}):'n/a';
const USD=n=>new Intl.NumberFormat('en-US',{style:'currency',currency:'USD',maximumFractionDigits:2}).format(Number.isFinite(n)?n:0);
function show(html){const r=$('#result');if(r)r.innerHTML=html}
function unitValue(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function annualCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function monthlyCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100/12:V(id)/12}
function monthDate(id){const raw=document.getElementById(id)?.value||'';return /^\d{4}-\d{2}$/.test(raw)?new Date(`${raw}-01T00:00:00`):new Date(raw||Date.now())}
function syncMortgageCosts(){const box=document.getElementById('include_costs'),panel=document.getElementById('mortgageCostFields');if(!box||!panel)return true;const on=box.checked;panel.hidden=!on;panel.classList.toggle('is-hidden',!on);panel.style.display=on?'':'none';return on}
function clearCalcForm(){const form=document.querySelector('.calc');if(!form)return;form.querySelectorAll('input').forEach(input=>{if(input.type==='checkbox')input.checked=false;else input.value=''});form.querySelectorAll('select').forEach(select=>{select.selectedIndex=0});form.querySelectorAll('details').forEach(item=>{item.open=false});syncMortgageCosts();show('<strong>$0.00 / month</strong><br>Enter values to calculate a new result.');const engine=currentEngine();if(engine==='cn_mortgage')renderMortgage(0,0,1,0,0,0,0,0,0,0,0,0,0,new Date());if(engine==='loan_page')renderLoanPage()}
function calc(e){
 switch(e){
  case'trade_value':{let price=V('price'),age=V('age'),miles=V('miles'),cond=V('condition');let ageF=Math.pow(.84,age),expected=Math.max(1,age)*12000,mileageF=Math.max(.72,Math.min(1.12,1-(miles-expected)*0.000003));let r=price*ageF*mileageF*cond;show(`<strong>${USD(Math.max(0,r))}</strong><br>Illustrative estimate, not a dealer quote or appraisal.`);break}
  case'f150_bed':{let bed=String(document.getElementById('bed').value);let d={'5.5':['67.1 in','50.6 in','~52.8 cu ft'],'6.5':['78.9 in','50.6 in','~62.3 cu ft'],'8':['97.6 in','50.6 in','~77.4 cu ft']}[bed];show(`<strong>${bed} ft bed</strong><br>Approx. inside length: ${d[0]}; width between wheelhouses: ${d[1]}; cargo volume: ${d[2]}. Verify exact model year/configuration.`);break}
  case'depreciation':{let r=V('price')*Math.pow(1-V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Estimated future value.`);break}
  case'payload':{let r=V('gvwr')-V('curb')-V('people')-V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated remaining payload.`);break}
  case'trailer_weight':{let r=V('empty')+V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated loaded trailer weight.`);break}
  case'tongue_weight':{let r=V('trailer')*V('percent')/100;show(`<strong>${F(r,0)} lb</strong><br>Estimated tongue weight.`);break}
  case'trailer_payload':{let r=V('gvwr')-V('empty');show(`<strong>${F(r,0)} lb</strong><br>Theoretical payload before other limits.`);break}
  case'tongue_pct':{let r=V('trailer')?V('tongue')/V('trailer')*100:0;show(`<strong>${F(r,2)}%</strong>`);break}
  case'towing':{let r=Math.min(V('rating'),Math.max(0,V('gcwr')-V('vehicle')));show(`<strong>${F(r,0)} lb</strong><br>Lower of tow rating and GCWR headroom; other limits may be lower.`);break}
  case'fuel_cost':{let r=V('distance')/Math.max(.01,V('mpg'))*V('fuelprice');show(`<strong>${USD(r)}</strong><br>Estimated fuel cost.`);break}
  case'mpg':{let r=V('gallons')?V('miles')/V('gallons'):0;show(`<strong>${F(r,2)} MPG</strong>`);break}
  case'tire':{let width=V('width'),aspect=V('aspect'),wheel=V('wheel');let side=width*aspect/100,diam=wheel+2*side/25.4,circ=Math.PI*diam;show(`<strong>${F(diam,2)} in diameter</strong><br>Sidewall: ${F(side,1)} mm; circumference: ${F(circ,2)} in.`);break}
  case'offset':{let r=(V('backspacing')-V('width')/2)*25.4;show(`<strong>${F(r,1)} mm offset</strong><br>Approximation using nominal wheel width.`);break}
  case'backspacing':{let r=V('width')/2+V('offset')/25.4;show(`<strong>${F(r,2)} in backspacing</strong><br>Approximation using nominal wheel width.`);break}
  case'bolt_pattern':{let r=V('adjacent')/Math.sin(Math.PI/V('lugs'));show(`<strong>${F(r,3)} in bolt-circle diameter</strong>`);break}
  case'horsepower':{let r=V('torque')*V('rpm')/5252;show(`<strong>${F(r,1)} hp</strong>`);break}
  case'power_weight':{let a=V('hp')/V('weight'),b=V('weight')/V('hp');show(`<strong>${F(a,4)} hp/lb</strong><br>${F(b,2)} lb per hp.`);break}
  case'car_loan':{let price=V('price'),tax=price*V('tax')/100,fees=V('fees'),include=(document.getElementById('include_fees')?.value||'0')==='1';let base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')),P=Math.max(0,base+(include?tax+fees:0));let rr=V('apr')/1200,n=Math.max(1,V('months'));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,upfront=V('down')+(include?0:tax+fees);show(`<strong>${USD(pay)} / month</strong><br>Total loan amount: ${USD(P)}; upfront payment: ${USD(upfront)}; sale tax: ${USD(tax)}.`);break}
  case'loan':{let P=V('amount'),rr=V('apr')/1200,n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months')));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,total=pay*n;show(`<strong>${USD(pay)} / month</strong><br>Total paid: ${USD(total)}; total interest: ${USD(total-P)}.`);break}
  case'loan_page':{renderLoanPage();break}
  case'compound':{let P=V('principal'),rr=V('rate')/1200,n=V('years')*12,pmt=V('monthly');let r=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n);show(`<strong>${USD(r)}</strong><br>Estimated future value with monthly contributions.`);break}
  case'discount':{let r=V('price')*(1-V('discount')/100);show(`<strong>${USD(r)}</strong><br>Savings: ${USD(V('price')-r)}.`);break}
  case'salary':{let r=V('salary')*(1+V('increase')/100);show(`<strong>${USD(r)}</strong><br>Annual increase: ${USD(r-V('salary'))}.`);break}
  case'dome':{let radius=V('diameter')/2,area=2*Math.PI*radius*radius,vol=2/3*Math.PI*Math.pow(radius,3);show(`<strong>${F(area,2)} sq ft</strong><br>Approx. curved area; ${F(vol,2)} cu ft volume.`);break}
  case'dome_material':{let radius=V('diameter')/2,area=2*Math.PI*radius*radius*(1+V('waste')/100);show(`<strong>${F(area,2)} sq ft</strong><br>Estimated covering area including waste.`);break}
  case'concrete':{let cf=V('length')*V('width')*(V('depth')/12),cy=cf/27*(1+V('waste')/100);show(`<strong>${F(cy,2)} cu yd</strong><br>${F(cf,2)} cu ft before waste.`);break}
  case'area':{let r=V('length')*V('width');show(`<strong>${F(r,2)} sq ft</strong>`);break}
  case'board_foot':{let r=V('thickness')*V('width')*V('length')/12*V('qty');show(`<strong>${F(r,2)} board ft</strong>`);break}
  case'studs':{let r=Math.ceil(V('wall')*12/V('spacing'))+1;show(`<strong>${F(r,0)} studs</strong><br>Basic count before corners, openings and special framing.`);break}
  case'roof_pitch':{let ratio=V('rise')/V('run'),per=ratio*100,angle=Math.atan(ratio)*180/Math.PI,pitch=ratio*12;show(`<strong>${F(pitch,2)}:12 pitch</strong><br>${F(per,1)}% slope; ${F(angle,1)} degree angle.`);break}
  case'rafter':{let r=Math.sqrt(V('run')**2+V('rise')**2)+V('overhang');show(`<strong>${F(r,2)} ft</strong><br>Approximate sloped length including entered overhang.`);break}
  case'flooring':{let r=V('length')*V('width')*(1+V('waste')/100);show(`<strong>${F(r,2)} sq ft</strong><br>Estimated order quantity.`);break}
  case'tile':{let tileArea=V('tilew')*V('tileh')/144,r=V('area')*(1+V('waste')/100)/tileArea;show(`<strong>${Math.ceil(r).toLocaleString()} tiles</strong><br>Area per tile: ${F(tileArea,3)} sq ft.`);break}
  case'tile_layout':{let count=Math.floor((V('row')+V('joint'))/(V('tile')+V('joint')));show(`<strong>${count} full tiles per row</strong><br>Approximate full-tile count before cuts.`);break}
  case'deck':{let total=V('deckwidth')*12,step=V('boardwidth')+V('gap'),r=Math.ceil(total/step);show(`<strong>${r} boards</strong><br>Approximate count across deck width.`);break}
  case'voltage_drop':{let drop=2*V('length')*V('amps')*V('resistance')/1000,per=drop/V('voltage')*100;show(`<strong>${F(drop,2)} V drop</strong><br>${F(per,2)}% of system voltage.`);break}
  case'wire_size':{let a=V('amps'),table=[[14,15],[12,20],[10,30],[8,40],[6,55],[4,70],[3,85],[2,95],[1,110],[0,125]],hit=table.find(x=>x[1]>=a)||table[table.length-1];show(`<strong>${hit[0]===0?'1/0':hit[0]} AWG reference</strong><br>Simplified planning table only; actual code-compliant sizing can differ.`);break}
  case'breaker':{let need=V('amps')*1.25,standard=[15,20,25,30,35,40,45,50,60,70,80,90,100,110,125,150,175,200],size=standard.find(x=>x>=need)||Math.ceil(need/25)*25;show(`<strong>${size} A reference breaker</strong><br>125% planning current: ${F(need,2)} A. Verify code, conductor and equipment requirements.`);break}
  case'amps_watts':{let r=V('amps')*V('volts');show(`<strong>${F(r,2)} W</strong>`);break}
  case'watts_amps':{let r=V('volts')?V('watts')/V('volts'):0;show(`<strong>${F(r,2)} A</strong>`);break}
  case'linear_convert':{let r=V('value')*V('factor'),target=document.getElementById('target')?.value||'target units';show(`<strong>${F(r,8)} ${target}</strong><br>Converted with the factor shown in the formula.`);break}
  case'cn_mortgage':{let price=V('price'),down=unitValue('down',price),P=Math.max(0,price-down),rr=V('apr')/1200,n=Math.max(1,V('years')*12);let pi=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n;let include=syncMortgageCosts(),tax=include?annualCost('tax',price)/12:0,ins=include?monthlyCost('insurance',price):0,pmi=include?monthlyCost('pmi',P):0,hoa=include?monthlyCost('hoa',price):0,other=include?monthlyCost('other',price):0,inc=include?V('increase'):0,extraM=V('extra_monthly'),extraY=V('extra_yearly'),extraO=V('extra_once'),extra=tax+ins+pmi+hoa+other;let start=monthDate('start');show(`<strong>${USD(pi)} / month</strong><br>Total monthly payment with selected taxes and costs: ${USD(pi+extra+extraM)}.`);renderMortgage(P,rr,n,pi,tax,ins,pmi,hoa,other,inc,extraM,extraY,extraO,start);break}
  case'cn_simple_interest':{let P=V('principal'),i=P*V('rate')/100*V('years');show(`<strong>${USD(P+i)}</strong><br>Simple interest: ${USD(i)}.`);break}
  case'cn_retirement':{let P=V('principal'),rr=V('rate')/1200,n=V('years')*12,pmt=V('monthly');let fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n);show(`<strong>${USD(fv)}</strong><br>Total contributions: ${USD(P+pmt*n)}; estimated growth: ${USD(fv-P-pmt*n)}.`);break}
  case'cn_inflation':{let r=V('amount')*Math.pow(1+V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Inflation-adjusted estimate after ${F(V('years'),1)} years.`);break}
  case'cn_tax_salary':{let taxable=Math.max(0,V('income')-V('deductions')),tax=taxable*V('taxrate')/100,net=V('income')-tax;show(`<strong>${USD(net)} take-home</strong><br>Estimated tax: ${USD(tax)}; monthly take-home: ${USD(net/12)}.`);break}
  case'cn_bmi':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0;let band=bmi<18.5?'underweight':bmi<25?'healthy range':bmi<30?'overweight range':'obesity range';show(`<strong>${F(bmi,1)} BMI</strong><br>This falls in the ${band} by adult BMI screening ranges.`);break}
  case'cn_calorie':{let h=(V('feet')*12+V('inches'))*2.54,kg=V('weight')*0.453592,age=V('age'),sex=document.getElementById('sex')?.value||'male';let bmr=10*kg+6.25*h-5*age+(sex==='male'?5:-161),tdee=bmr*V('activity');show(`<strong>${F(tdee,0)} calories/day</strong><br>BMR: ${F(bmr,0)}. Protein planning range: ${F(kg*1.6,0)}-${F(kg*2.2,0)} g/day.`);break}
  case'cn_body_metric':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0,low=18.5*h*h/703,high=24.9*h*h/703;show(`<strong>${F(bmi,1)} BMI</strong><br>Adult BMI reference weight range at this height: ${F(low,0)}-${F(high,0)} lb.`);break}
  case'cn_due_date':{let d=new Date(document.getElementById('date')?.value||''),days=V('days');if(isNaN(d)){show('Enter a valid date.');break}let out=new Date(d.getTime()+days*86400000);show(`<strong>${out.toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})}</strong><br>Calculated by adding ${F(days,0)} days to the start date.`);break}
  case'cn_pace':{let sec=V('hours')*3600+V('minutes')*60+V('seconds'),dist=V('distance');let pace=dist?sec/dist:0;show(`<strong>${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')} per mile</strong><br>Average speed: ${F(dist/(sec/3600),2)} mph.`);break}
  case'cn_percent':{let pct=V('whole')?V('part')/V('whole')*100:0,change=V('old')?(V('new')-V('old'))/V('old')*100:0;show(`<strong>${F(pct,2)}%</strong><br>Percent change from old to new value: ${F(change,2)}%.`);break}
  case'cn_triangle':{let a=V('a'),b=V('b'),c=Math.sqrt(a*a+b*b),area=a*b/2;show(`<strong>${F(c,4)} hypotenuse</strong><br>Area: ${F(area,4)}; perimeter: ${F(a+b+c,4)}.`);break}
  case'cn_stats':{let vals=(document.getElementById('values')?.value||'').split(/[,\s]+/).map(Number).filter(Number.isFinite);if(!vals.length){show('Enter at least one number.');break}let mean=vals.reduce((x,y)=>x+y,0)/vals.length,sorted=[...vals].sort((x,y)=>x-y),mid=Math.floor(sorted.length/2),median=sorted.length%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2,sd=Math.sqrt(vals.reduce((s,x)=>s+(x-mean)**2,0)/Math.max(1,vals.length-1));show(`<strong>${F(mean,4)} mean</strong><br>Median: ${F(median,4)}; sample standard deviation: ${F(sd,4)}; count: ${vals.length}.`);break}
  case'cn_random':{let min=Math.ceil(V('min')),max=Math.floor(V('max'));if(max<min){let t=min;min=max;max=t}let val=Math.floor(Math.random()*(max-min+1))+min;show(`<strong>${val}</strong><br>Random integer from ${min} to ${max}.`);break}
  case'cn_age':{let b=new Date(document.getElementById('birth')?.value||''),t=new Date(document.getElementById('target')?.value||'');if(isNaN(b)||isNaN(t)){show('Enter valid dates.');break}let years=t.getFullYear()-b.getFullYear();let before=t.getMonth()<b.getMonth()||(t.getMonth()===b.getMonth()&&t.getDate()<b.getDate());if(before)years--;let days=Math.floor((t-b)/86400000);show(`<strong>${years} years old</strong><br>Total days: ${F(days,0)}.`);renderAge(b,t,years,days);break}
  case'cn_date':{let s=new Date(document.getElementById('start')?.value||''),e2=new Date(document.getElementById('end')?.value||'');if(isNaN(s)||isNaN(e2)){show('Enter valid dates.');break}let days=Math.round((e2-s)/86400000);show(`<strong>${F(days,0)} days</strong><br>End date weekday: ${e2.toLocaleDateString('en-US',{weekday:'long'})}.`);break}
  case'cn_hours':{let total=V('hours')+V('minutes')/60;show(`<strong>${F(total,2)} hours</strong><br>Estimated pay at the entered rate: ${USD(total*V('rate'))}.`);break}
  case'cn_grade':{let pct=V('possible')?V('earned')/V('possible')*100:0,letter=pct>=90?'A':pct>=80?'B':pct>=70?'C':pct>=60?'D':'F';show(`<strong>${F(pct,2)}%</strong><br>Approximate letter grade: ${letter}; weighted points: ${F(pct*V('credits')/100,2)}.`);break}
  case'cn_subnet':{let p=Math.max(0,Math.min(32,V('prefix'))),addresses=Math.pow(2,32-p),usable=p>=31?addresses:Math.max(0,addresses-2);show(`<strong>${F(addresses,0)} addresses</strong><br>Approximate usable IPv4 hosts: ${F(usable,0)}.`);break}
  case'cn_password':{let len=Math.max(4,Math.min(64,Math.floor(V('length')))),chars='ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz23456789!@$%';let out='';for(let i=0;i<len;i++)out+=chars[Math.floor(Math.random()*chars.length)];show(`<strong>${out}</strong><br>Generated in your browser. Use a password manager for important accounts.`);break}
  case'cn_tip':{let tip=V('bill')*V('tip')/100,total=V('bill')+tip,people=Math.max(1,V('people'));show(`<strong>${USD(total)}</strong><br>Tip: ${USD(tip)}; split per person: ${USD(total/people)}.`);break}
  case'cn_generic':{let base=V('amount'),rate=V('rate')/100,years=V('years'),simple=base*rate*years,compound=base*Math.pow(1+rate,years);show(`<strong>${USD(compound)}</strong><br>Simple change: ${USD(simple)}; compound estimate over ${F(years,1)} years.`);break}
  case'electrical_load':{let a=V('watts')/V('volts'),b=a*V('factor')/100;show(`<strong>${F(a,2)} A load</strong><br>${F(b,2)} A planning current at ${F(V('factor'),0)}%.`);break}
 }
 renderGenericFromEngine(e);
}
function currentEngine(){return document.querySelector('[data-engine]')?.dataset.engine||''}
document.addEventListener('click',e=>{const btn=e.target.closest('[data-engine]');if(btn)calc(btn.dataset.engine)});
document.addEventListener('click',e=>{if(e.target.closest('[data-clear]'))clearCalcForm()});
document.addEventListener('input',e=>{if(e.target.closest('.calc')){const engine=currentEngine();if(engine)calc(engine)}});
document.addEventListener('change',e=>{if(e.target.closest('.calc')){const engine=currentEngine();if(engine)calc(engine)}});
document.addEventListener('DOMContentLoaded',()=>{const engine=currentEngine();if(engine)calc(engine)});

// Generic dashboard rendering
function drawGenericBars(canvas, bars) {
  if (!canvas) return;
  const ctx = clearCanvas(canvas);
  const max = Math.max(...bars.map(x => Math.abs(x.value)), 1);
  const total = bars.reduce((s, x) => s + Math.abs(x.value), 0) || 1;
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae", "#8aa4c6"];
  ctx.font = "700 13px system-ui, sans-serif";
  bars.slice(0, 6).forEach((bar, index) => {
    const y = 34 + index * 40;
    const label = String(bar.label).slice(0, 22);
    const width = (canvas.width - 210) * Math.abs(bar.value) / max;
    const pct = Math.abs(bar.value) / total * 100;
    ctx.fillStyle = "#344054";
    ctx.fillText(label, 16, y + 16);
    ctx.fillStyle = "#eef3f8";
    ctx.fillRect(158, y, canvas.width - 198, 24);
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(158, y, Math.max(4, width), 24);
    ctx.fillStyle = "#152033";
    ctx.fillText(`${bar.display || F(bar.value, 2)} (${F(pct,1)}%)`, 166 + Math.max(8, width), y + 17);
  });
}

function renderGeneric(cards, bars, rows) {
  const summary = document.getElementById("genericSummary");
  const chart = document.getElementById("genericChart");
  const table = document.querySelector("#genericTable tbody");
  if (!summary || !chart || !table) return;
  summary.innerHTML = cards.slice(0, 4).map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  if (chart.dataset.chartType === "pie") drawPie(chart, bars.map(x => Math.abs(x.value)), bars.map(x => x.label));
  else drawGenericBars(chart, bars);
  table.innerHTML = rows.map(row => `<tr><td>${row[0]}</td><td>${row[1]}</td><td>${row[2]}</td></tr>`).join("");
}

function renderGenericFromEngine(engine) {
  if (!document.getElementById("genericSummary")) return;
  let cards=[], bars=[], rows=[];
  if (engine === "loan") {
    const P=V('amount'), rr=V('apr')/1200, n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months'))), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, interest=total-P;
    cards=[["Monthly payment",USD(pay),"Estimated recurring payment."],["Total paid",USD(total),"Principal plus interest."],["Total interest",USD(interest),"Cost of borrowing."],["Loan term",`${F(n,0)} months`,"Entered repayment period."]];
    bars=[{label:"Principal",value:P,display:USD(P)},{label:"Interest",value:interest,display:USD(interest)},{label:"Monthly payment",value:pay,display:USD(pay)}];
    rows=[["Loan amount",USD(P),"Starting balance."],["APR",`${F(V('apr'),2)}%`,"Annual percentage rate."],["Term",`${F(n,0)} months`,"Number of payments."],["Total paid",USD(total),"Payment multiplied by term."]];
  } else if (engine === "car_loan") {
    const price=V('price'), tax=price*V('tax')/100, fees=V('fees'), include=(document.getElementById('include_fees')?.value||'0')==='1', base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')), P=Math.max(0,base+(include?tax+fees:0)), rr=V('apr')/1200, n=Math.max(1,V('months')), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, upfront=V('down')+(include?0:tax+fees);
    cards=[["Monthly Pay",USD(pay),"Estimated auto loan payment."],["Total Loan Amount",USD(P),"Amount financed."],["Sale Tax",USD(tax),"Estimated tax from entered rate."],["Upfront Payment",USD(upfront),"Down payment plus taxes and fees when not financed."]];
    bars=[{label:"Loan amount",value:P,display:USD(P)},{label:"Interest",value:total-P,display:USD(total-P)},{label:"Upfront",value:upfront,display:USD(upfront)}];
    rows=[["Monthly Pay",USD(pay),"Payment every month."],["Total Loan Amount",USD(P),"Balance used for amortization."],["Total of Payments",USD(total),"Monthly payment times term."],["Total Loan Interest",USD(total-P),"Total paid minus loan amount."],["Sale Tax",USD(tax),"Auto price times tax rate."],["Upfront Payment",USD(upfront),"Due at purchase if not financed."]];
  } else if (engine === "compound" || engine === "cn_retirement") {
    const P=V('principal'), rr=V('rate')/1200, n=V('years')*12, pmt=V('monthly'), fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n), contrib=P+pmt*n, growth=fv-contrib;
    cards=[["Future value",USD(fv),"Projected ending balance."],["Contributions",USD(contrib),"Starting amount plus deposits."],["Growth",USD(growth),"Estimated investment return."],["Time",`${F(V('years'),1)} years`,"Growth period."]];
    bars=[{label:"Starting amount",value:P,display:USD(P)},{label:"Deposits",value:pmt*n,display:USD(pmt*n)},{label:"Growth",value:growth,display:USD(growth)}];
    rows=[["Starting amount",USD(P),"Initial balance."],["Monthly contribution",USD(pmt),"Recurring addition."],["Annual return",`${F(V('rate'),2)}%`,"Assumed return."],["Projected balance",USD(fv),"Estimate before taxes and fees."]];
  } else if (engine === "cn_bmi" || engine === "cn_body_metric") {
    const h=V('feet')*12+V('inches'), bmi=h?703*V('weight')/(h*h):0, low=18.5*h*h/703, high=24.9*h*h/703;
    cards=[["BMI",F(bmi,1),"Adult screening estimate."],["Weight",`${F(V('weight'),1)} lb`,"Entered body weight."],["Healthy range",`${F(low,0)}-${F(high,0)} lb`,"BMI 18.5 to 24.9 range."],["Height",`${F(h,0)} in`,"Total height in inches."]];
    bars=[{label:"BMI",value:bmi,display:F(bmi,1)},{label:"Current weight",value:V('weight'),display:`${F(V('weight'),0)} lb`},{label:"Range low",value:low,display:`${F(low,0)} lb`},{label:"Range high",value:high,display:`${F(high,0)} lb`}];
    rows=[["BMI formula",`703 x weight / height^2`,"US customary formula."],["Current BMI",F(bmi,1),"Screening value."],["Lower reference",`${F(low,0)} lb`,"BMI 18.5."],["Upper reference",`${F(high,0)} lb`,"BMI 24.9."]];
  } else if (engine === "cn_calorie") {
    const h=(V('feet')*12+V('inches'))*2.54, kg=V('weight')*0.453592, age=V('age'), sex=document.getElementById('sex')?.value||'male', bmr=10*kg+6.25*h-5*age+(sex==='male'?5:-161), tdee=bmr*V('activity');
    cards=[["Daily calories",F(tdee,0),"Estimated maintenance calories."],["BMR",F(bmr,0),"Estimated resting burn."],["Protein range",`${F(kg*1.6,0)}-${F(kg*2.2,0)} g`,"Common athletic planning range."],["Activity factor",F(V('activity'),3),"Selected multiplier."]];
    bars=[{label:"BMR",value:bmr,display:F(bmr,0)},{label:"Daily calories",value:tdee,display:F(tdee,0)},{label:"Protein low",value:kg*1.6,display:`${F(kg*1.6,0)} g`},{label:"Protein high",value:kg*2.2,display:`${F(kg*2.2,0)} g`}];
    rows=[["Weight",`${F(V('weight'),1)} lb`,"Converted internally to kilograms."],["Height",`${F(h,0)} cm`,"Converted from feet and inches."],["Age",F(age,0),"Entered age."],["Formula",sex==="male"?"Male Mifflin-St Jeor":"Female Mifflin-St Jeor","Screening estimate."]];
  } else if (engine === "cn_tip") {
    const tip=V('bill')*V('tip')/100,total=V('bill')+tip,people=Math.max(1,V('people'));
    cards=[["Total bill",USD(total),"Bill plus tip."],["Tip amount",USD(tip),"Calculated from tip rate."],["Per person",USD(total/people),"Split total."],["Tip rate",`${F(V('tip'),1)}%`,"Entered percentage."]];
    bars=[{label:"Bill",value:V('bill'),display:USD(V('bill'))},{label:"Tip",value:tip,display:USD(tip)},{label:"Per person",value:total/people,display:USD(total/people)}];
    rows=[["Bill",USD(V('bill')),"Before tip."],["Tip",USD(tip),"Additional amount."],["People",F(people,0),"Split count."],["Total",USD(total),"Final amount."]];
  } else if (engine === "cn_date" || engine === "cn_due_date") {
    const start=new Date(document.getElementById(engine==="cn_date"?'start':'date')?.value||''), days=engine==="cn_date"?Math.round((new Date(document.getElementById('end')?.value||'')-start)/86400000):V('days');
    const end=engine==="cn_date"?new Date(document.getElementById('end')?.value||''):new Date(start.getTime()+days*86400000);
    if (isNaN(start)||isNaN(end)) return;
    cards=[["Day difference",`${F(days,0)} days`,"Calendar day span."],["Weeks",F(days/7,1),"Days divided by 7."],["Months",F(days/30.436875,1),"Average month estimate."],["End weekday",end.toLocaleDateString("en-US",{weekday:"long"}),"Day of week."]];
    bars=[{label:"Days",value:Math.abs(days),display:F(days,0)},{label:"Weeks",value:Math.abs(days/7),display:F(days/7,1)},{label:"Months",value:Math.abs(days/30.436875),display:F(days/30.436875,1)}];
    rows=[["Start date",start.toLocaleDateString("en-US"),"Entered start."],["End date",end.toLocaleDateString("en-US"),"Calculated or entered end."],["Days",F(days,0),"Difference in days."],["Weeks",F(days/7,2),"Approximate weeks."]];
  } else if (engine === "cn_pace") {
    const sec=V('hours')*3600+V('minutes')*60+V('seconds'), dist=Math.max(0.0001,V('distance')), pace=sec/dist, mph=dist/(sec/3600);
    cards=[["Pace",`${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')} / mile`,"Average pace."],["Speed",`${F(mph,2)} mph`,"Average speed."],["Distance",`${F(dist,2)} miles`,"Entered distance."],["Time",`${F(sec/60,1)} min`,"Total elapsed time."]];
    bars=[{label:"Time minutes",value:sec/60,display:F(sec/60,1)},{label:"Distance",value:dist,display:F(dist,2)},{label:"Speed",value:mph,display:F(mph,2)}];
    rows=[["Hours",F(V('hours'),0),"Entered time."],["Minutes",F(V('minutes'),0),"Entered time."],["Seconds",F(V('seconds'),0),"Entered time."],["Pace",`${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')}`,"Per mile."]];
  } else if (engine === "cn_simple_interest") {
    const P=V('principal'), interest=P*V('rate')/100*V('years'), total=P+interest;
    cards=[["Ending balance",USD(total),"Principal plus interest."],["Interest earned",USD(interest),"Simple interest amount."],["Principal",USD(P),"Starting amount."],["Rate",`${F(V('rate'),2)}%`,"Annual simple rate."]];
    bars=[{label:"Principal",value:P,display:USD(P)},{label:"Interest",value:interest,display:USD(interest)}];
    rows=[["Principal",USD(P),"Starting balance."],["Rate",`${F(V('rate'),2)}%`,"Annual rate."],["Time",`${F(V('years'),2)} years`,"Entered period."],["Ending balance",USD(total),"Principal plus interest."]];
  } else if (engine === "cn_tax_salary") {
    const income=V('income'), taxable=Math.max(0,income-V('deductions')), tax=taxable*V('taxrate')/100, net=income-tax;
    cards=[["Take-home pay",USD(net),"Estimated annual net pay."],["Monthly net",USD(net/12),"Estimated monthly take-home."],["Estimated tax",USD(tax),"Taxable income times rate."],["Taxable income",USD(taxable),"Income minus deductions."]];
    bars=[{label:"Take-home",value:net,display:USD(net)},{label:"Tax",value:tax,display:USD(tax)},{label:"Deductions",value:V('deductions'),display:USD(V('deductions'))}];
    rows=[["Gross income",USD(income),"Entered annual income."],["Deductions",USD(V('deductions')),"Entered deductions."],["Effective rate",`${F(V('taxrate'),2)}%`,"Applied to taxable income."],["Net pay",USD(net),"Estimated take-home."]];
  } else if (engine === "cn_percent") {
    const pct=V('whole')?V('part')/V('whole')*100:0, change=V('old')?(V('new')-V('old'))/V('old')*100:0;
    cards=[["Percentage",`${F(pct,2)}%`,"Part as a share of whole."],["Percent change",`${F(change,2)}%`,"New versus old value."],["Difference",F(V('new')-V('old'),2),"New value minus old value."],["Whole",F(V('whole'),2),"Entered denominator."]];
    bars=[{label:"Part",value:V('part'),display:F(V('part'),2)},{label:"Whole",value:V('whole'),display:F(V('whole'),2)},{label:"Old",value:V('old'),display:F(V('old'),2)},{label:"New",value:V('new'),display:F(V('new'),2)}];
    rows=[["Part / whole",`${F(V('part'),2)} / ${F(V('whole'),2)}`,"Percentage inputs."],["Percentage",`${F(pct,2)}%`,"Part divided by whole."],["Old to new",`${F(V('old'),2)} to ${F(V('new'),2)}`,"Change inputs."],["Percent change",`${F(change,2)}%`,"Relative change."]];
  } else if (engine === "discount") {
    const savings=V('price')*V('discount')/100, final=V('price')-savings;
    cards=[["Sale price",USD(final),"Price after discount."],["Savings",USD(savings),"Discount amount."],["Original price",USD(V('price')),"Entered price."],["Discount",`${F(V('discount'),1)}%`,"Entered discount rate."]];
    bars=[{label:"Sale price",value:final,display:USD(final)},{label:"Savings",value:savings,display:USD(savings)}];
    rows=[["Original price",USD(V('price')),"Before discount."],["Discount",`${F(V('discount'),2)}%`,"Rate applied."],["Savings",USD(savings),"Amount removed."],["Final price",USD(final),"After discount."]];
  } else if (engine === "cn_triangle") {
    const a=V('a'), b=V('b'), c=Math.sqrt(a*a+b*b), area=a*b/2, perimeter=a+b+c;
    cards=[["Hypotenuse",F(c,4),"Right-triangle side c."],["Area",F(area,4),"a x b / 2."],["Perimeter",F(perimeter,4),"a + b + c."],["Angle A",`${F(Math.atan2(a,b)*180/Math.PI,2)}°`,"Opposite side a."]];
    bars=[{label:"Side a",value:a,display:F(a,2)},{label:"Side b",value:b,display:F(b,2)},{label:"Side c",value:c,display:F(c,2)},{label:"Area",value:area,display:F(area,2)}];
    rows=[["Side a",F(a,4),"Entered leg."],["Side b",F(b,4),"Entered leg."],["Hypotenuse",F(c,4),"Pythagorean theorem."],["Perimeter",F(perimeter,4),"Sum of sides."]];
  } else if (engine === "cn_stats") {
    const vals=(document.getElementById('values')?.value||'').split(/[,\s]+/).map(Number).filter(Number.isFinite);
    if (!vals.length) return;
    const mean=vals.reduce((x,y)=>x+y,0)/vals.length, sorted=[...vals].sort((x,y)=>x-y), mid=Math.floor(sorted.length/2), median=sorted.length%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2, min=sorted[0], max=sorted[sorted.length-1], sd=Math.sqrt(vals.reduce((s,x)=>s+(x-mean)**2,0)/Math.max(1,vals.length-1));
    cards=[["Mean",F(mean,4),"Average value."],["Median",F(median,4),"Middle value."],["Std. dev.",F(sd,4),"Sample standard deviation."],["Count",F(vals.length,0),"Numbers included."]];
    bars=[{label:"Minimum",value:min,display:F(min,2)},{label:"Mean",value:mean,display:F(mean,2)},{label:"Median",value:median,display:F(median,2)},{label:"Maximum",value:max,display:F(max,2)}];
    rows=[["Minimum",F(min,4),"Lowest value."],["Maximum",F(max,4),"Highest value."],["Range",F(max-min,4),"Maximum minus minimum."],["Sample SD",F(sd,4),"Dispersion estimate."]];
  } else if (engine === "cn_random") {
    const min=Math.ceil(V('min')), max=Math.floor(V('max')), count=Math.max(1,max-min+1);
    cards=[["Range size",F(count,0),"Possible integer results."],["Minimum",F(min,0),"Lower bound."],["Maximum",F(max,0),"Upper bound."],["Chance each",`${F(100/count,2)}%`,"Uniform random estimate."]];
    bars=[{label:"Minimum",value:min,display:F(min,0)},{label:"Maximum",value:max,display:F(max,0)},{label:"Range size",value:count,display:F(count,0)}];
    rows=[["Minimum",F(min,0),"Included bound."],["Maximum",F(max,0),"Included bound."],["Possible results",F(count,0),"Inclusive integer count."],["Per-result chance",`${F(100/count,2)}%`,"If uniformly random."]];
  } else if (engine === "cn_hours") {
    const total=V('hours')+V('minutes')/60, pay=total*V('rate');
    cards=[["Total hours",F(total,2),"Hours plus minutes."],["Estimated pay",USD(pay),"Hours times rate."],["Minutes",F(total*60,0),"Total minutes."],["Hourly rate",USD(V('rate')),"Entered rate."]];
    bars=[{label:"Hours",value:V('hours'),display:F(V('hours'),2)},{label:"Extra minutes",value:V('minutes')/60,display:F(V('minutes')/60,2)},{label:"Pay",value:pay,display:USD(pay)}];
    rows=[["Hours",F(V('hours'),2),"Entered whole hours."],["Minutes",F(V('minutes'),0),"Converted to decimal hours."],["Total hours",F(total,2),"Combined time."],["Pay",USD(pay),"Estimated earnings."]];
  } else if (engine === "cn_grade") {
    const pct=V('possible')?V('earned')/V('possible')*100:0, letter=pct>=90?'A':pct>=80?'B':pct>=70?'C':pct>=60?'D':'F';
    cards=[["Grade",`${F(pct,2)}%`,"Earned divided by possible."],["Letter",letter,"Approximate US letter grade."],["Weighted points",F(pct*V('credits')/100,2),"Percent times credits or weight."],["Missing points",F(V('possible')-V('earned'),2),"Possible minus earned."]];
    bars=[{label:"Earned",value:V('earned'),display:F(V('earned'),2)},{label:"Missing",value:Math.max(0,V('possible')-V('earned')),display:F(Math.max(0,V('possible')-V('earned')),2)}];
    rows=[["Earned",F(V('earned'),2),"Entered earned points."],["Possible",F(V('possible'),2),"Entered possible points."],["Grade",`${F(pct,2)}%`,"Calculated percentage."],["Letter",letter,"Approximate band."]];
  } else if (engine === "cn_subnet") {
    const p=Math.max(0,Math.min(32,V('prefix'))), addresses=Math.pow(2,32-p), usable=p>=31?addresses:Math.max(0,addresses-2);
    cards=[["Addresses",F(addresses,0),"Total IPv4 addresses."],["Usable hosts",F(usable,0),"Common host estimate."],["CIDR",`/${F(p,0)}`,"Entered prefix."],["Network bits",F(p,0),"Fixed bits."]];
    bars=[{label:"Total",value:addresses,display:F(addresses,0)},{label:"Usable",value:usable,display:F(usable,0)},{label:"Reserved",value:addresses-usable,display:F(addresses-usable,0)}];
    rows=[["CIDR prefix",`/${F(p,0)}`,"Entered prefix."],["Host bits",F(32-p,0),"32 minus prefix."],["Addresses",F(addresses,0),"2^(host bits)."],["Usable hosts",F(usable,0),"Common estimate."]];
  } else if (engine === "cn_password") {
    const len=Math.max(4,Math.min(64,Math.floor(V('length')))), charset=55, entropy=len*Math.log2(charset);
    cards=[["Length",F(len,0),"Generated password length."],["Entropy",`${F(entropy,1)} bits`,"Approximate character-space entropy."],["Character set",F(charset,0),"Letters, numbers, and symbols."],["Generated locally","Yes","Runs in browser only."]];
    bars=[{label:"Length",value:len,display:F(len,0)},{label:"Entropy bits",value:entropy,display:F(entropy,1)},{label:"Character set",value:charset,display:F(charset,0)}];
    rows=[["Length",F(len,0),"Entered length."],["Approx. entropy",`${F(entropy,1)} bits`,"Planning estimate."],["Storage advice","Use a password manager","For important accounts."],["Generation","Browser-side","No account required."]];
  } else if (engine === "cn_generic") {
    const inputs=Array.from(document.querySelectorAll(".calc input,.calc select")).filter(el=>el.type!=="hidden");
    const numeric=inputs.map(el=>({label:el.previousElementSibling?.textContent||el.id,value:parseFloat(el.value)})).filter(x=>Number.isFinite(x.value));
    const primary=numeric[0]?.value||0, secondary=numeric[1]?.value||0, result=numeric.reduce((s,x)=>s+x.value,0);
    cards=[["Primary value",F(primary,2),"First entered value."],["Second value",F(secondary,2),"Second entered value when available."],["Input total",F(result,2),"Sum of numeric inputs."],["Fields used",F(numeric.length,0),"Numeric values read from the form."]];
    bars=numeric.slice(0,6).map(x=>({label:x.label,value:x.value,display:F(x.value,2)}));
    rows=numeric.map(x=>[x.label,F(x.value,4),"Entered value."]);
  } else {
    const inputs=Array.from(document.querySelectorAll(".calc input,.calc select")).filter(el=>el.type!=="hidden"&&el.type!=="checkbox");
    const numeric=inputs.map(el=>({label:el.previousElementSibling?.textContent||el.closest('.field')?.querySelector('label')?.textContent||el.id,value:parseFloat(el.value)})).filter(x=>Number.isFinite(x.value));
    const result=numeric.reduce((s,x)=>s+x.value,0);
    const largest=numeric.slice().sort((a,b)=>Math.abs(b.value)-Math.abs(a.value))[0];
    cards=[["Calculated output",document.querySelector("#result strong")?.textContent||"Ready","Main result from the calculator."],["Input total",F(result,2),"Sum of numeric values entered."],["Largest input",largest?`${largest.label}: ${F(largest.value,2)}`:"n/a","Largest numeric field."],["Fields used",F(numeric.length,0),"Inputs included in this summary."]];
    bars=numeric.slice(0,6).map(x=>({label:x.label,value:x.value,display:F(x.value,2)}));
    rows=numeric.map(x=>[x.label,F(x.value,4),"Entered value."]);
  }
  renderGeneric(cards,bars.length?bars:[{label:"Result",value:1,display:"Ready"}],rows.length?rows:[["Result","Ready","Enter values to update."]]);
}
// End generic dashboard rendering

// Loan calculator page rendering
function periodsPerYear(key) {
  return {daily:365,weekly:52,biweekly:26,halfmonth:24,month:12,quarter:4,halfyear:2,year:1,annually:1,semiannually:2,quarterly:4,monthly:12,semimonthly:24}[key] || 12;
}

function effectiveRate(annualRate, compoundKey, paybackKey) {
  const paybacks = periodsPerYear(paybackKey || "year");
  if (compoundKey === "continuously") return Math.exp(annualRate / paybacks) - 1;
  const compounds = periodsPerYear(compoundKey || "annually");
  return Math.pow(1 + annualRate / compounds, compounds / paybacks) - 1;
}

function loanTermPeriods(yearId, monthId, paybackKey) {
  const years = V(yearId) + V(monthId) / 12;
  return Math.max(1, Math.round(years * periodsPerYear(paybackKey)));
}

function loanTermYears(yearId, monthId) {
  return Math.max(0, V(yearId) + V(monthId) / 12);
}

function paybackLabel(key) {
  return {daily:"Day",weekly:"Week",biweekly:"2 Weeks",halfmonth:"Half Month",month:"Month",quarter:"Quarter",halfyear:"6 Months",year:"Year"}[key] || "Month";
}

function fillSummary(id, cards) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = cards.map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
}

function fillResultTable(id, rows) {
  const el = document.querySelector(`#${id} tbody`) || document.getElementById(id);
  if (!el) return;
  el.innerHTML = rows.map(row => `<tr><td>${row[0]}</td><td><strong>${row[1]}</strong></td></tr>`).join("");
}

function amortizationRows(principal, rate, periods, payment) {
  let balance = principal;
  const rows = [];
  for (let i = 1; i <= periods && i <= 360 && balance > 0.01; i++) {
    const interest = balance * rate;
    const principalPaid = Math.min(balance, Math.max(0, payment - interest));
    balance = Math.max(0, balance - principalPaid);
    rows.push([i, payment, principalPaid, interest, balance]);
  }
  return rows;
}

function compoundAmount(principal, annualRate, years, compoundKey) {
  if (compoundKey === "continuously") return principal * Math.exp(annualRate * years);
  const compounds = periodsPerYear(compoundKey || "annually");
  return principal * Math.pow(1 + annualRate / compounds, compounds * years);
}

function presentValue(futureValue, annualRate, years, compoundKey) {
  if (compoundKey === "continuously") return futureValue / Math.exp(annualRate * years);
  const compounds = periodsPerYear(compoundKey || "annually");
  return futureValue / Math.pow(1 + annualRate / compounds, compounds * years);
}

function scheduleRows(start, annualRate, years, compoundKey) {
  const out = [];
  const wholeYears = Math.max(1, Math.ceil(years));
  for (let i = 1; i <= wholeYears && i <= 40; i++) {
    const from = compoundAmount(start, annualRate, Math.min(i - 1, years), compoundKey);
    const to = compoundAmount(start, annualRate, Math.min(i, years), compoundKey);
    out.push([i, from, Math.max(0, to - from), to]);
  }
  return out;
}

function renderLoanPage() {
  const payback = document.getElementById("l_payback")?.value || "month";
  const compound = document.getElementById("l_compound")?.value || "monthly";
  const P = V("l_amount"), annual = V("l_rate") / 100, rate = effectiveRate(annual, compound, payback);
  const n = loanTermPeriods("l_years", "l_months", payback);
  const payment = rate ? P * rate * Math.pow(1 + rate, n) / (Math.pow(1 + rate, n) - 1) : P / n;
  const total = payment * n, interest = total - P, payLabel = paybackLabel(payback);
  show(`<strong>${USD(payment)} / ${payLabel.toLowerCase()}</strong><br>Total of ${F(n,0)} payments: ${USD(total)}; total interest: ${USD(interest)}.`);
  fillSummary("loanSummary", [["Payment Every " + payLabel, USD(payment), "Fixed amortized payment."],["Total of " + F(n,0) + " Payments", USD(total), "Payment multiplied by term."],["Total Interest", USD(interest), "Total cost of borrowing."],["Effective Period Rate", `${F(rate*100,4)}%`, "Adjusted for compound and payback frequency."]]);
  fillResultTable("loanResultTable", [["Payment Every " + payLabel, USD(payment)],["Total of " + F(n,0) + " Payments", USD(total)],["Total Interest", USD(interest)]]);
  drawPie(document.getElementById("loanPie"), [P, interest], ["Principal", "Interest"]);
  const amortRows = amortizationRows(P, rate, n, payment);
  const amortBody = document.getElementById("loanAmortRows");
  if (amortBody) amortBody.innerHTML = amortRows.map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td><td>${USD(row[4])}</td></tr>`).join("");

  const dP = V("d_amount"), dAnnual = V("d_rate") / 100, dYears = loanTermYears("d_years", "d_months"), dComp = document.getElementById("d_compound")?.value || "annually";
  const due = compoundAmount(dP, dAnnual, dYears, dComp), dInterest = due - dP;
  fillSummary("deferredSummary", [["Amount Due at Loan Maturity", USD(due), "Principal plus compounded interest."],["Total Interest", USD(dInterest), "Interest accrued to maturity."],["Loan Amount", USD(dP), "Starting principal."],["Loan Term", `${F(dYears,2)} years`, "Entered term."]]);
  fillResultTable("deferredResultTable", [["Amount Due at Loan Maturity", USD(due)],["Total Interest", USD(dInterest)]]);
  drawPie(document.getElementById("deferredPie"), [dP, dInterest], ["Principal", "Interest"]);
  const dBody = document.getElementById("deferredRows");
  if (dBody) dBody.innerHTML = scheduleRows(dP, dAnnual, dYears, dComp).map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td></tr>`).join("");

  const bDue = V("b_due"), bAnnual = V("b_rate") / 100, bYears = loanTermYears("b_years", "b_months"), bComp = document.getElementById("b_compound")?.value || "annually";
  const received = presentValue(bDue, bAnnual, bYears, bComp), bInterest = bDue - received;
  fillSummary("bondSummary", [["Amount Received When the Loan Starts", USD(received), "Present value of due amount."],["Total Interest", USD(bInterest), "Discount between start and maturity."],["Predetermined Due Amount", USD(bDue), "Face amount paid at maturity."],["Loan Term", `${F(bYears,2)} years`, "Entered term."]]);
  fillResultTable("bondResultTable", [["Amount Received When the Loan Starts", USD(received)],["Total Interest", USD(bInterest)]]);
  drawPie(document.getElementById("bondPie"), [received, bInterest], ["Principal", "Interest"]);
  const bBody = document.getElementById("bondRows");
  if (bBody) bBody.innerHTML = scheduleRows(received, bAnnual, bYears, bComp).map(row => `<tr><td>${F(row[0],0)}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td><td>${USD(row[3])}</td></tr>`).join("");
}

document.addEventListener("click", event => {
  const trigger = event.target.closest("[data-toggle-table]");
  if (!trigger) return;
  const table = document.getElementById(trigger.dataset.toggleTable);
  if (!table) return;
  table.classList.toggle("is-collapsed");
  trigger.textContent = table.classList.contains("is-collapsed") ? trigger.textContent.replace("Hide", "View") : trigger.textContent.replace("View", "Hide");
});
// End loan calculator page rendering

// Mortgage dashboard rendering
function mortgageRows(principal, monthlyRate, months, payment, extraMonthly = 0, extraYearly = 0, extraOnce = 0) {
  let balance = principal;
  const rows = [];
  for (let month = 1; month <= months && balance > 0.01; month++) {
    const interest = balance * monthlyRate;
    const scheduledPrincipal = Math.max(0, payment - interest);
    const requestedExtra = extraMonthly + (month % 12 === 0 ? extraYearly : 0) + (month === 1 ? extraOnce : 0);
    const principalPaid = Math.min(balance, scheduledPrincipal + requestedExtra);
    const extraPaid = Math.max(0, principalPaid - Math.min(balance, scheduledPrincipal));
    balance = Math.max(0, balance - principalPaid);
    rows.push({ month, interest, principal: principalPaid, extra: extraPaid, balance });
  }
  return rows;
}

function clearCanvas(canvas) {
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  return ctx;
}

function drawPie(canvas, values, labels) {
  const logicalWidth = Number(canvas.dataset.logicalWidth || canvas.getAttribute("width")) || canvas.width;
  const logicalHeight = Number(canvas.dataset.logicalHeight || canvas.getAttribute("height")) || canvas.height;
  canvas.dataset.logicalWidth = String(logicalWidth);
  canvas.dataset.logicalHeight = String(logicalHeight);
  const dpr = Math.max(1, window.devicePixelRatio || 1);
  if (canvas.width !== Math.round(logicalWidth * dpr) || canvas.height !== Math.round(logicalHeight * dpr)) {
    canvas.width = Math.round(logicalWidth * dpr);
    canvas.height = Math.round(logicalHeight * dpr);
  }
  canvas.style.width = `min(100%, ${logicalWidth}px)`;
  canvas.style.height = "auto";
  const ctx = canvas.getContext("2d");
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, logicalWidth, logicalHeight);
  const total = values.reduce((a, b) => a + Math.max(0, b), 0) || 1;
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae", "#d6a13d", "#95a3b8"];
  const compact = logicalWidth <= 380;
  const legendX = compact ? Math.max(166, logicalWidth * .52) : logicalWidth * .58;
  const cx = Math.max(62, Math.min(logicalWidth * .24, legendX - 72));
  const cy = logicalHeight / 2;
  const radius = Math.max(44, Math.min(logicalHeight * .34, legendX - cx - 28));
  const inner = radius * .52;
  let start = -Math.PI / 2;
  values.forEach((value, index) => {
    const amount = Math.max(0, value);
    const angle = amount / total * Math.PI * 2;
    if (angle <= 0) return;
    const mid = start + angle / 2;
    ctx.beginPath();
    ctx.moveTo(cx, cy);
    ctx.arc(cx, cy, radius, start, start + angle);
    ctx.closePath();
    ctx.fillStyle = colors[index % colors.length];
    ctx.fill();
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 2;
    ctx.stroke();
    const pct = amount / total * 100;
    if (pct >= 3) {
      const labelRadius = inner + (radius - inner) * .56;
      const tx = cx + Math.cos(mid) * labelRadius;
      const ty = cy + Math.sin(mid) * labelRadius;
      ctx.save();
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.font = compact ? "800 12px system-ui, sans-serif" : "800 15px system-ui, sans-serif";
      ctx.lineWidth = 4;
      ctx.strokeStyle = "rgba(21,32,51,.55)";
      ctx.strokeText(`${F(pct,1)}%`, tx, ty);
      ctx.fillStyle = "#fff";
      ctx.fillText(`${F(pct,1)}%`, tx, ty);
      ctx.restore();
    }
    start += angle;
  });
  ctx.beginPath();
  ctx.arc(cx, cy, inner, 0, Math.PI * 2);
  ctx.fillStyle = "#fff";
  ctx.fill();
  ctx.fillStyle = "#152033";
  ctx.font = compact ? "800 16px system-ui, sans-serif" : "800 17px system-ui, sans-serif";
  ctx.textAlign = "center";
  ctx.fillText(USD(total).replace(".00", ""), cx, cy - 2);
  ctx.font = compact ? "700 10px system-ui, sans-serif" : "700 11px system-ui, sans-serif";
  ctx.fillStyle = "#667085";
  ctx.fillText(canvas.dataset.centerLabel || "per month", cx, cy + 14);
  ctx.textAlign = "left";
  ctx.fillStyle = "#152033";
  ctx.font = "700 14px system-ui, sans-serif";
  labels.forEach((label, index) => {
    const amount = Math.max(0, values[index]);
    const pct = amount / total * 100;
    const rowGap = compact ? 31 : 38;
    const startY = Math.max(24, cy - ((labels.length - 1) * rowGap) / 2);
    const y = startY + index * rowGap;
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(legendX, y - 11, compact ? 11 : 14, compact ? 11 : 14);
    ctx.fillStyle = "#344054";
    ctx.font = compact ? "700 11px system-ui, sans-serif" : "700 13px system-ui, sans-serif";
    ctx.fillText(`${label} (${F(pct,1)}%)`, legendX + (compact ? 18 : 23), y);
    ctx.font = compact ? "600 10px system-ui, sans-serif" : "600 12px system-ui, sans-serif";
    ctx.fillStyle = "#667085";
    ctx.fillText(USD(amount), legendX + (compact ? 18 : 23), y + (compact ? 14 : 17));
  });
}

function drawLine(canvas, rows, principal) {
  const ctx = clearCanvas(canvas);
  const pad = { left: 54, right: 18, top: 24, bottom: 42 };
  const w = canvas.width - pad.left - pad.right;
  const h = canvas.height - pad.top - pad.bottom;
  ctx.strokeStyle = "#dfe5ee";
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = pad.top + h * i / 4;
    ctx.beginPath();
    ctx.moveTo(pad.left, y);
    ctx.lineTo(pad.left + w, y);
    ctx.stroke();
  }
  ctx.fillStyle = "#667085";
  ctx.font = "12px system-ui, sans-serif";
  ctx.fillText(USD(principal), 6, pad.top + 4);
  ctx.fillText("$0", 28, pad.top + h + 4);
  ctx.beginPath();
  rows.forEach((row, index) => {
    const x = pad.left + w * index / Math.max(1, rows.length - 1);
    const y = pad.top + h - h * row.balance / Math.max(1, principal);
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = "#173f73";
  ctx.lineWidth = 3;
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(pad.left, pad.top + h);
  rows.forEach((row, index) => {
    const x = pad.left + w * index / Math.max(1, rows.length - 1);
    const y = pad.top + h - h * row.balance / Math.max(1, principal);
    ctx.lineTo(x, y);
  });
  ctx.lineTo(pad.left + w, pad.top + h);
  ctx.closePath();
  ctx.fillStyle = "rgba(23,63,115,.08)";
  ctx.fill();
  ctx.fillStyle = "#344054";
  ctx.font = "700 12px system-ui, sans-serif";
  ctx.fillText("Start", pad.left, canvas.height - 13);
  ctx.fillText("Payoff", pad.left + w - 42, canvas.height - 13);
}

function renderMortgage(principal, monthlyRate, months, pi, tax, insurance, pmi, hoa, other, increase, extraMonthly, extraYearly, extraOnce, startDate) {
  const summary = document.getElementById("mortgageSummary");
  const pie = document.getElementById("mortgagePie");
  const line = document.getElementById("mortgageLine");
  const table = document.querySelector("#mortgageSchedule tbody");
  const costTable = document.querySelector("#mortgageCostTable tbody");
  if (!summary || !pie || !line || !table || !costTable) return;
  const rows = mortgageRows(principal, monthlyRate, months, pi, extraMonthly, extraYearly, extraOnce);
  const paidMonths = rows.length || months;
  const totalInterest = rows.reduce((s, r) => s + r.interest, 0);
  const totalExtraPaid = rows.reduce((s, r) => s + r.extra, 0);
  let taxTotal = 0, insuranceTotal = 0, pmiTotal = 0, hoaTotal = 0, otherTotal = 0;
  for (let month = 1; month <= paidMonths; month++) {
    const growth = Math.pow(1 + increase / 100, Math.floor((month - 1) / 12));
    taxTotal += tax * growth;
    insuranceTotal += insurance * growth;
    pmiTotal += pmi;
    hoaTotal += hoa;
    otherTotal += other;
  }
  const baseExtra = tax + insurance + pmi + hoa + other;
  const totalMonthlyPayment = pi + baseExtra + extraMonthly;
  const totalCost = principal + totalInterest + taxTotal + insuranceTotal + pmiTotal + hoaTotal + otherTotal;
  const payoffDate = startDate instanceof Date && !Number.isNaN(startDate.valueOf()) ? new Date(startDate) : new Date();
  payoffDate.setMonth(payoffDate.getMonth() + paidMonths);
  summary.innerHTML = [
    ["Monthly Pay", USD(pi), "Principal and interest only."],
    ["Total monthly", USD(totalMonthlyPayment), "Includes selected taxes, insurance, PMI, HOA, other costs, and extra monthly pay."],
    ["Total interest", USD(totalInterest), "Lower when extra payments shorten the loan."],
    ["Payoff date", payoffDate.toLocaleDateString("en-US", { month: "short", year: "numeric" }), `${paidMonths} scheduled payments.`]
  ].map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  drawPie(pie, [pi, tax, insurance, pmi + hoa + other], ["Principal & interest", "Property tax", "Insurance", "PMI / HOA / other"]);
  drawLine(line, rows, principal);
  costTable.innerHTML = [
    ["Principal & interest", pi, principal + totalInterest],
    ["Property tax", tax, taxTotal],
    ["Home insurance", insurance, insuranceTotal],
    ["PMI", pmi, pmiTotal],
    ["HOA", hoa, hoaTotal],
    ["Other costs", other, otherTotal],
    ["Extra payments", extraMonthly, totalExtraPaid],
    ["Total cost", totalMonthlyPayment, totalCost]
  ].map(row => `<tr><td>${row[0]}</td><td>${USD(row[1])}</td><td>${USD(row[2])}</td></tr>`).join("");
  const yearly = [];
  for (let y = 0; y < Math.ceil(rows.length / 12); y++) {
    const slice = rows.slice(y * 12, y * 12 + 12);
    yearly.push({
      year: y + 1,
      interest: slice.reduce((s, r) => s + r.interest, 0),
      principal: slice.reduce((s, r) => s + r.principal, 0),
      balance: slice.length ? slice[slice.length - 1].balance : 0
    });
  }
  table.innerHTML = yearly.map(row => `<tr><td>${row.year}</td><td>${USD(row.interest)}</td><td>${USD(row.principal)}</td><td>${USD(row.balance)}</td></tr>`).join("");
}
// End mortgage dashboard rendering

// Age dashboard rendering
function drawAgeBars(canvas, values) {
  const ctx = clearCanvas(canvas);
  const labels = ["Years", "Months", "Weeks", "Days"];
  const colors = ["#173f73", "#c0333a", "#6f91bd", "#f0a8ae"];
  const max = Math.max(...values, 1);
  ctx.font = "700 13px system-ui, sans-serif";
  values.forEach((value, index) => {
    const y = 42 + index * 54;
    const width = (canvas.width - 180) * value / max;
    ctx.fillStyle = "#344054";
    ctx.fillText(labels[index], 18, y + 17);
    ctx.fillStyle = "#eef3f8";
    ctx.fillRect(92, y, canvas.width - 130, 24);
    ctx.fillStyle = colors[index];
    ctx.fillRect(92, y, Math.max(3, width), 24);
    ctx.fillStyle = "#152033";
    ctx.fillText(F(value, 0), 102 + Math.max(8, width), y + 17);
  });
}

function drawAgeProgress(canvas, percent, daysSinceBirthday, daysToBirthday) {
  const ctx = clearCanvas(canvas);
  const cx = 128, cy = 132, radius = 82;
  ctx.beginPath();
  ctx.arc(cx, cy, radius, -Math.PI / 2, -Math.PI / 2 + Math.PI * 2 * percent);
  ctx.lineTo(cx, cy);
  ctx.closePath();
  ctx.fillStyle = "#173f73";
  ctx.fill();
  ctx.beginPath();
  ctx.arc(cx, cy, radius, -Math.PI / 2 + Math.PI * 2 * percent, Math.PI * 1.5);
  ctx.lineTo(cx, cy);
  ctx.closePath();
  ctx.fillStyle = "#eef3f8";
  ctx.fill();
  ctx.fillStyle = "#152033";
  ctx.font = "800 28px system-ui, sans-serif";
  ctx.fillText(`${F(percent * 100, 1)}%`, 255, 105);
  ctx.font = "700 13px system-ui, sans-serif";
  ctx.fillStyle = "#344054";
  ctx.fillText("of current birthday year", 255, 130);
  ctx.font = "600 12px system-ui, sans-serif";
  ctx.fillStyle = "#667085";
  ctx.fillText(`${F(daysSinceBirthday, 0)} days since last birthday`, 255, 164);
  ctx.fillText(`${F(daysToBirthday, 0)} days to next birthday`, 255, 186);
}

function addYears(date, years) {
  const next = new Date(date);
  next.setFullYear(date.getFullYear() + years);
  return next;
}

function daysBetween(a, b) {
  return Math.round((b - a) / 86400000);
}

function renderAge(birth, target, years, totalDays) {
  const summary = document.getElementById("ageSummary");
  const bars = document.getElementById("ageBars");
  const progress = document.getElementById("ageProgress");
  const table = document.querySelector("#ageMilestones tbody");
  if (!summary || !bars || !progress || !table) return;
  const months = Math.floor(totalDays / 30.436875);
  const weeks = Math.floor(totalDays / 7);
  const hours = totalDays * 24;
  const minutes = hours * 60;
  const seconds = minutes * 60;
  summary.innerHTML = [
    ["Calendar age", `${years} years`, "Full years between birth date and target date."],
    ["Total days", F(totalDays, 0), "Useful for exact day-based comparisons."],
    ["Total months", F(months, 0), "Average calendar-month estimate."],
    ["Total seconds", F(seconds, 0), "Approximate total seconds lived."]
  ].map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  drawAgeBars(bars, [years, months, weeks, totalDays]);
  let lastBirthday = addYears(birth, years);
  if (lastBirthday > target) lastBirthday = addYears(birth, years - 1);
  let nextBirthday = addYears(birth, years + 1);
  if (nextBirthday <= target) nextBirthday = addYears(birth, years + 2);
  const since = Math.max(0, daysBetween(lastBirthday, target));
  const span = Math.max(1, daysBetween(lastBirthday, nextBirthday));
  const toNext = Math.max(0, daysBetween(target, nextBirthday));
  drawAgeProgress(progress, Math.min(1, since / span), since, toNext);
  const milestones = [1, 5, 10, 13, 16, 18, 21, 25, 30, 40, 50, 60, 65, 70, 75, 80, 90, 100];
  table.innerHTML = milestones.map(age => {
    const date = addYears(birth, age);
    const diff = daysBetween(target, date);
    const timing = diff === 0 ? "Today" : diff > 0 ? `${F(diff, 0)} days later` : `${F(Math.abs(diff), 0)} days ago`;
    return `<tr><td>Age ${age}</td><td>${date.toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" })}</td><td>${timing}</td></tr>`;
  }).join("");
}
// End age dashboard rendering
'''

SCIENTIFIC_JS = r'''
(function(){
  function normalize(value) {
    return value
      .replace(/\bpi\b/gi, "Math.PI")
      .replace(/\be\b/g, "Math.E")
      .replace(/\bsqrt\(/gi, "Math.sqrt(")
      .replace(/\bsin\(/gi, "Math.sin(")
      .replace(/\bcos\(/gi, "Math.cos(")
      .replace(/\btan\(/gi, "Math.tan(")
      .replace(/\blog\(/gi, "Math.log10(")
      .replace(/\bln\(/gi, "Math.log(")
      .replace(/(\d+(?:\.\d+)?)%/g, "($1/100)")
      .replace(/\^/g, "**");
  }
  function run() {
    const input = document.getElementById("sciExpression");
    const output = document.getElementById("sciResult");
    if (!input || !output) return;
    try {
      const expr = normalize(input.value);
      if (!/^[0-9+\-*/().,\sMathPIElogsqrtincota%*]+$/.test(expr)) throw new Error("Unsupported expression");
      const result = Function(`"use strict"; return (${expr})`)();
      output.textContent = Number.isFinite(result) ? result.toLocaleString("en-US", { maximumFractionDigits: 10 }) : "Check the expression";
    } catch (error) {
      output.textContent = "Check the expression";
    }
  }
  document.addEventListener("click", event => {
    if (event.target && event.target.id === "sciRun") run();
  });
  document.addEventListener("keydown", event => {
    if (event.target && event.target.id === "sciExpression" && event.key === "Enter") run();
  });
})();
'''

LOGO_SVG = r'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Northstar Calculators">
  <rect width="512" height="512" rx="116" fill="#173f73"/>
  <rect x="128" y="72" width="256" height="368" rx="54" fill="#fff"/>
  <rect x="162" y="112" width="188" height="58" rx="18" fill="#e8f0fb"/>
  <circle cx="180" cy="230" r="24" fill="#173f73"/>
  <circle cx="256" cy="230" r="24" fill="#173f73"/>
  <circle cx="332" cy="230" r="24" fill="#b4232a"/>
  <circle cx="180" cy="306" r="24" fill="#173f73"/>
  <circle cx="256" cy="306" r="24" fill="#173f73"/>
  <circle cx="332" cy="306" r="24" fill="#173f73"/>
  <rect x="162" y="360" width="188" height="42" rx="21" fill="#b4232a"/>
</svg>
'''


def build():
    data = read_data()
    site = dict(data["site"])
    if PUBLIC_SITE_DOMAIN:
        site["domain"] = PUBLIC_SITE_DOMAIN
    calculators = base_and_supplemental(data)
    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    write(DIST / "assets" / "site.css", CSS.strip() + "\n")
    write(DIST / "assets" / "search.js", SEARCH_JS.strip() + "\n")
    write(DIST / "assets" / "home.js", HOME_JS.strip() + "\n")
    write(DIST / "assets" / "scientific.js", SCIENTIFIC_JS.strip() + "\n")
    write(DIST / "assets" / "calculator.js", CALC_JS.strip() + "\n")
    write(DIST / "favicon.svg", LOGO_SVG.strip() + "\n")
    write(DIST / "apple-touch-icon.svg", LOGO_SVG.strip() + "\n")
    write(DIST / "index.html", home_new(site, calculators))

    by_cat = defaultdict(list)
    for calc in calculators:
        by_cat[calc["cat"]].append(calc)
    for cat in CATEGORY_ORDER:
        items = by_cat.get(cat, [])
        if not items:
            continue
        write(DIST / slugify_cat(cat) / "index.html", category_page(site, cat, items))
    for calc in calculators:
        rel = [c for c in by_cat[calc["cat"]] if c["slug"] != calc["slug"] and calculator_group(c) == calculator_group(calc)][:6]
        write(DIST / calc["slug"] / "index.html", calculator_page(site, calc, rel))

    write(DIST / "scientific-calculator" / "index.html", scientific_page(site))
    for path, html in info_pages(site).items():
        write(DIST / path.strip("/") / "index.html", html)
    write(DIST / "methodology" / "index.html", simple_page(site, "/methodology/", "Methodology", "How Northstar chooses, builds, and links calculator pages.", "<p>Every new calculator should have a distinct search intent, real inputs, a formula or verified lookup, visible assumptions, a worked example, and relevant internal links.</p><p>For safety-critical, financial, construction, fitment, towing, and electrical decisions, users should verify results with authoritative sources.</p>"))
    write(DIST / "privacy" / "index.html", redirect_page(site, "/privacy/", "/privacy-policy/", "Privacy Policy"))
    write(DIST / "404.html", page(site, "Page Not Found | Northstar Calculators", "The requested calculator page could not be found.", "/404.html", '<main class="main"><div class="wrap"><article class="article"><h1>Page not found</h1><p class="lead">Try the homepage search to find the calculator you need.</p><a class="btn primary" href="/">Go to homepage</a></article></div></main>'))
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site_url(site, '/sitemap.xml')}\n")

    urls = ["/"] + [f"/{slugify_cat(cat)}/" for cat in CATEGORY_ORDER if by_cat.get(cat)] + [f"/{c['slug']}/" for c in calculators] + ["/scientific-calculator/", "/about/", "/methodology/", "/privacy-policy/", "/terms/", "/contact/"]
    sitemap = '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{h(site_url(site, u))}</loc><lastmod>{date.today().isoformat()}</lastmod></url>" for u in urls) + "</urlset>"
    write(DIST / "sitemap.xml", sitemap)
    print(f"Built {len(calculators)} calculator pages plus homepage and hubs.")


if __name__ == "__main__":
    build()

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
RMD_JOINT_LIFE_TABLE = ROOT / "src" / "data" / "rmd-joint-life-table.json"
PUBLIC_BASE_PATH = os.environ.get("PUBLIC_BASE_PATH", "").strip().rstrip("/")
PUBLIC_SITE_DOMAIN = os.environ.get("PUBLIC_SITE_DOMAIN", "").strip()
ASSET_VERSION = "20260919a"
PRIORITY_LENGTH_CONVERSIONS = {
    "millimeters-to-feet-calculator",
    "meters-to-feet-calculator",
    "inches-to-centimeters-calculator",
    "centimeters-to-feet-calculator",
    "inches-to-meters-calculator",
    "feet-to-centimeters-calculator",
    "centimeters-to-inches-calculator",
    "meters-to-inches-calculator",
}
LENGTH_UNIT_SYMBOLS = {"millimeters": "mm", "centimeters": "cm", "meters": "m", "inches": "in", "feet": "ft"}
LENGTH_UNIT_METERS = {"millimeters": 0.001, "centimeters": 0.01, "meters": 1.0, "inches": 0.0254, "feet": 0.3048}
CALCULATOR_REDIRECTS = {
    "concrete-calculator": "concrete-volume-calculator",
    "loan-payment-calculator": "loan-calculator",
    "financial-calculator": "finance-calculator",
}

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
    "Electrical": ["Computing & AI", "Wire & Breakers", "Power Conversion", "Load & Voltage Drop", "Technical Tools"],
    "Financial": ["AI & API Costs", "Crypto & Mining", "Mortgages", "Loans", "Savings & Growth", "Retirement", "Taxes & Pay", "Credit & Debt", "Investment"],
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

# Full static generator for the NS Calculators site.
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
        "Gpu": "GPU",
        "Cpu": "CPU",
        "Ai": "AI",
        "Api": "API",
        "Llm": "LLM",
        "Psu": "PSU",
        "Tflops": "TFLOPS",
        "Flops": "FLOPs",
        "Pflop": "PFLOP",
        "Pflops": "PFLOPs",
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
        "creator": {"@id": site_url(site, "/#organization")},
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
        "@id": site_url(site, "/#website"),
        "name": site["name"],
        "alternateName": "NS Calculators",
        "url": site_url(site, "/"),
        "publisher": {"@id": site_url(site, "/#organization")},
    }


def organization_schema(site):
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "@id": site_url(site, "/#organization"),
        "name": site["name"],
        "url": site_url(site, "/"),
        "logo": site_url(site, "/favicon.svg"),
    }


LOGO_MARK = """<svg viewBox="0 0 40 40" aria-hidden="true"><rect class="logo-body" x="8" y="5" width="24" height="30" rx="5"/><path class="logo-screen" d="M13 12h14"/><path d="M14 19h3M20 19h3M26 19h1M14 25h3M20 25h3M26 25h1"/><path class="logo-accent" d="M14 31h13"/></svg>"""


def nav():
    menu_links = "".join(
        f"""<a class="category-nav-link" href="/{slugify_cat(cat)}/"><span>{h(cat)}</span></a>"""
        for cat in CATEGORY_ORDER
    )
    return """<header class="site-header"><div class="wrap nav">
<a class="brand" href="/"><span class="brand-mark">""" + LOGO_MARK + """</span><span class="brand-name"><strong>NS</strong><b>Calculators</b></span></a>
<nav class="navlinks" aria-label="Main navigation"><div class="menu-group all-calculators-menu"><a class="menu-top" href="/">Calculators</a><div class="submenu mega-menu" aria-label="Calculator categories">""" + menu_links + """</div></div></nav>
</div></header>"""


def footer(include_methodology=True):
    methodology_link = '<a href="/methodology/">Methodology</a>' if include_methodology else ""
    return """<footer class="footer"><div class="wrap footer-grid">
<div><a class="brand footer-brand" href="/"><span class="brand-mark">""" + LOGO_MARK + """</span><span class="brand-name"><strong>NS</strong><b>Calculators</b></span></a><p>Practical browser-based tools for US users. Verify critical results with authoritative sources.</p></div>
<div class="footer-links"><a href="/about/">About</a>""" + methodology_link + """<a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/contact/">Contact</a></div>
</div></footer>"""


def json_ld(payload):
    return '<script type="application/ld+json">' + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "</script>"


def page(site, title, desc, path, body, keywords=None, extra_schema=None, page_type="WebPage", indexable=True):
    keywords = keywords or []
    extra_schema = extra_schema or []
    schema = {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": title.replace(" | NS Calculators", ""),
        "description": desc,
        "url": site_url(site, path),
        "isPartOf": {"@id": site_url(site, "/#website")},
    }
    if keywords:
        schema["keywords"] = keywords
    robots_meta = "" if indexable else '<meta name="robots" content="noindex,follow">'
    schema_html = "\n".join(json_ld(item) for item in [schema] + extra_schema)
    html = f"""<!doctype html><html lang="{h(site['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{h(title)}</title><meta name="description" content="{h(desc)}">{robots_meta}<meta name="theme-color" content="#2563eb">
<meta property="og:type" content="website"><meta property="og:site_name" content="NS Calculators"><meta property="og:locale" content="en_US"><meta property="og:title" content="{h(title)}"><meta property="og:description" content="{h(desc)}"><meta property="og:url" content="{h(site_url(site, path))}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="{h(title)}"><meta name="twitter:description" content="{h(desc)}">
<link rel="canonical" href="{h(site_url(site, path))}"><link rel="icon" href="/favicon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="/apple-touch-icon.svg"><link rel="stylesheet" href="/assets/site.css?v={ASSET_VERSION}">
{schema_html}<script>window.NORTHSTAR_BASE_PATH={json.dumps(PUBLIC_BASE_PATH)};</script></head><body>{nav()}{body}{footer(indexable)}</body></html>"""
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
    if slug == "sales-tax-calculator":
        base.update({"engine": "sales_tax_advanced", "desc": "Add sales tax to a purchase, reverse tax from a tax-inclusive total, or calculate the tax rate from before-tax and after-tax prices.", "formula": "Sales tax = taxable amount x tax rate; tax-inclusive total = before-tax total + sales tax.", "inputs": []})
    elif slug == "basic-calculator":
        base.update({"engine": "basic_advanced", "desc": "Use a free online basic calculator for arithmetic, percentages, square roots, memory, and calculation history.", "formula": "Expressions follow the standard order of operations: parentheses, exponents, multiplication and division, then addition and subtraction.", "inputs": []})
    elif slug == "debt-payoff-calculator":
        base.update({"engine": "debt_payoff_advanced", "desc": "Compare debt avalanche and debt snowball payoff plans for multiple balances, including extra payments, payoff dates, and total interest.", "formula": "Each month, interest is added to every open balance, minimum payments are made, and the remaining fixed budget is directed to the selected priority debt.", "inputs": []})
    elif slug == "percent-calculator":
        base.update({"engine": "percent_advanced", "desc": "Solve six common percentage problems: percent of a number, percent of total, reverse percentage, percent change, percentage difference, and increase or decrease by a percent.", "formula": "Percentage calculations compare a part with a whole, or a change with its original value.", "inputs": []})
    elif slug == "fraction-calculator":
        base.update({"engine": "fraction_advanced", "desc": "Add, subtract, multiply, and divide fractions or mixed numbers, simplify fractions, and convert decimals to fractions with step-by-step results.", "formula": "Fractions are normalized and reduced by their greatest common divisor.", "inputs": []})
    elif slug == "standard-deviation-calculator":
        base.update({"engine": "stats_advanced", "desc": "Calculate sample or population standard deviation, variance, mean, sum, range, standard error, and a normal-approximation margin of error with detailed steps.", "formula": "Population variance divides squared deviations by n; sample variance divides by n - 1.", "inputs": []})
    elif slug == "ratio-calculator":
        base.update({"engine": "ratio_advanced", "desc": "Simplify ratios, solve proportions, scale equivalent ratios, or split a total into proportional shares.", "formula": "Simplify by dividing every term by their greatest common divisor; solve a:b = c:d by equal cross products.", "inputs": []})
    elif slug == "bmi-calculator":
        base.update({"engine": "bmi_advanced", "desc": "Calculate adult BMI with US or metric units, CDC weight category, healthy weight range, BMI Prime, and Ponderal Index.", "formula": "BMI = weight in kilograms / height in meters squared, or 703 x pounds / inches squared.", "inputs": []})
    elif slug == "salary-calculator":
        base.update({"engine": "salary_converter", "desc": "Convert hourly, daily, weekly, biweekly, semimonthly, monthly, quarterly, or annual pay and compare unpaid time-off adjustments.", "formula": "Annual pay equals the entered amount multiplied by the number of pay periods per year.", "inputs": []})
    elif slug == "finance-calculator":
        base.update({"engine": "finance_tvm", "desc": "Solve any one of the five core time-value-of-money variables: future value, payment, annual interest rate, number of periods, or present value.", "formula": "PV(1 + r)^N + PMT(1 + r x type)((1 + r)^N - 1) / r + FV = 0.", "inputs": []})
    elif slug == "take-home-pay-calculator":
        base.update({"engine": "take_home_pay", "desc": "Estimate 2026 US take-home pay from federal income tax brackets, Social Security, Medicare, state or local tax, pay frequency, and payroll deductions.", "formula": "Take-home pay = gross pay - estimated federal income tax - FICA taxes - state or local tax - pre-tax and post-tax deductions.", "inputs": []})
    elif "mortgage" in text:
        base.update({"engine": "cn_mortgage", "desc": "Estimate a mortgage payment with principal, interest, taxes, insurance, PMI, HOA, extra payments, and total payoff costs.", "formula": "Monthly payment = principal and interest + optional annual taxes, insurance, PMI, HOA, and other costs divided by 12. Extra payments reduce payoff time and total interest.", "inputs": [["price", "Home price ($)", "number", 400000], ["down", "Down payment ($)", "number", 20], ["apr", "Interest rate (%)", "number", 6.81], ["years", "Loan term (years)", "number", 30], ["start", "Start month", "month", "2026-09"], ["tax", "Property tax", "number", 1.2], ["insurance", "Home insurance", "number", 1500], ["pmi", "PMI", "number", 0], ["hoa", "HOA", "number", 0], ["other", "Other costs", "number", 4000], ["increase", "Annual tax/insurance increase (%)", "number", 0], ["extra_monthly", "Extra monthly pay ($)", "number", 0], ["extra_yearly", "Extra yearly pay ($)", "number", 0], ["extra_once", "One-time extra pay ($)", "number", 0]]})
    elif slug == "loan-calculator":
        base.update({"engine": "loan_page", "desc": "Calculate amortized loan payments, deferred payment loan maturity value, and bond present value using the same three loan models shown on Calculator.net.", "formula": "Amortized payment uses an effective payback-period rate. Deferred payment compounds principal to maturity. Bond value discounts the predetermined due amount to the loan start.", "inputs": []})
    elif slug == "interest-calculator":
        base.update({"engine": "interest_advanced", "desc": "Compare simple and compound interest with recurring contributions, compounding frequency, estimated interest tax, and inflation-adjusted buying power.", "formula": "Simple interest uses principal x rate x time; compound interest applies growth to principal plus accumulated interest.", "inputs": []})
    elif slug == "payment-calculator":
        base.update({"engine": "payment_advanced", "desc": "Calculate a monthly loan payment from a fixed term or calculate payoff time from a fixed monthly payment, with total interest and a full amortization schedule.", "formula": "Payment = P x r x (1+r)^n / ((1+r)^n - 1); payoff periods = -ln(1 - P x r / payment) / ln(1+r).", "inputs": []})
    elif slug == "amortization-calculator":
        base.update({"engine": "amortization_advanced", "desc": "Build a monthly and annual loan amortization schedule, then test how recurring or one-time extra principal payments change interest and payoff time.", "formula": "Payment = P x r x (1+r)^n / ((1+r)^n - 1); each month, principal paid = payment - interest + extra principal.", "inputs": []})
    elif slug == "retirement-calculator":
        base.update({"engine": "retirement_advanced", "desc": "Estimate how much you need to retire, the monthly savings required, sustainable retirement withdrawals, or how long an existing nest egg may last.", "formula": "Retirement projections combine compound growth, recurring contributions, inflation-adjusted income needs, and an assumed fixed investment return.", "inputs": []})
    elif slug == "401k-calculator":
        base.update({"engine": "401k_advanced", "desc": "Project a 401(k) balance and retirement income, estimate early-withdrawal taxes and penalties, or calculate employer matching contributions.", "formula": "The projection compounds employee and employer contributions monthly; withdrawal estimates apply entered tax rates and any modeled 10% additional tax.", "inputs": []})
    elif slug == "social-security-calculator":
        base.update({"engine": "social_security_advanced", "desc": "Compare Social Security retirement claiming ages, estimate lifetime benefits and break-even age, or apply the 2026 retirement earnings test.", "formula": "Worker retirement benefits are adjusted by claiming months before or after full retirement age; cumulative values include entered COLA and investment-return assumptions.", "inputs": []})
    elif slug == "rmd-calculator":
        base.update({"engine": "rmd_advanced", "desc": "Calculate a required minimum distribution using the current IRS Uniform Lifetime or Joint and Last Survivor table, then project future annual RMDs.", "formula": "RMD = prior December 31 retirement account balance / IRS distribution period for the account owner's age and applicable life-expectancy table.", "inputs": []})
    elif "auto loan" in text or ("car" in text and "loan" in text):
        base.update({"engine": "car_loan", "desc": "Estimate an auto loan payment including price, tax, fees, cash incentives, down payment, trade-in, amount owed on trade-in, and whether taxes and fees are financed.", "formula": "Loan amount = auto price - cash incentives - down payment - trade-in value + amount owed on trade-in, plus taxes and fees when included in the loan. Payment uses monthly amortization.", "inputs": [["price", "Auto Price ($)", "number", 50000], ["months", "Loan Term (months)", "number", 60], ["apr", "Interest Rate (%)", "number", 5], ["incentives", "Cash Incentives ($)", "number", 0], ["down", "Down Payment ($)", "number", 10000], ["trade", "Trade-in Value ($)", "number", 0], ["owed", "Amount Owed on Trade-in ($)", "number", 0], ["tax", "Sales Tax (%)", "number", 3], ["fees", "Title, Registration and Other Fees ($)", "number", 2800], ["include_fees", "Include taxes and fees in loan", "select", [["0", "No"], ["1", "Yes"]]]]})
    elif "loan" in text or "payment calculator" in text:
        base.update({"engine": "loan", "desc": "Calculate an installment loan payment, total paid, and interest cost from loan amount, term, and APR.", "formula": "Payment = P x r x (1+r)^n / ((1+r)^n - 1).", "inputs": [["amount", "Loan amount ($)", "number", 10000], ["apr", "Interest rate (%)", "number", 10], ["years", "Loan term (years)", "number", 5], ["months_extra", "Extra months", "number", 0]]})
    elif slug == "compound-interest-calculator":
        base.update({"engine": "compound", "desc": "Calculate compound interest with monthly and annual contributions, years and months, tax, inflation, and nine compounding options.", "formula": "Ending balance = initial investment growth + recurring contribution growth - estimated tax on interest.", "inputs": []})
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
        if not match:
            expanded_slug = re.sub(r"(^|-)sq-", r"\1square-", calc["slug"])
            expanded_slug = re.sub(r"(^|-)cu-", r"\1cubic-", expanded_slug)
            match = metrics.get(expanded_slug)
        if not match and not calc.get("generated"):
            match = metrics.get(slugify_text(calc["title"]))
        if match:
            calc["keyword_data"] = dict(match)
            calc["seo_keyword"] = match["keyword"]
            calc["title"] = smart_title(calc["title"])
        else:
            calc["keyword_data"] = {}
        if calc["slug"] == "concrete-volume-calculator":
            calc["title"] = "Concrete Calculator"
            calc["seo_keyword"] = "concrete calculator"
            calc["desc"] = "Calculate cubic yards, cubic feet, concrete bags, and material cost for slabs, footings, columns, and post holes."
    title_counts = Counter(slugify_text(calc["title"]) for calc in calculators)
    for calc in calculators:
        if title_counts[slugify_text(calc["title"])] > 1 and not calc.get("seo_keyword"):
            calc["seo_context_label"] = f"{display_group(calculator_group(calc))} {calc['cat']}"
    return calculators


def primary_keyword(calc):
    return calc.get("seo_keyword") or str(calc["title"]).lower()


def is_indexable_calculator(calc):
    searches = int((calc.get("keyword_data") or {}).get("monthly_searches") or 0)
    return searches > 0 or not calc.get("generated") or calc.get("source") == "calculator.net keyword model"


def seo_keywords(calc):
    if calc.get("slug") == "loan-calculator":
        return [
            "loan calculator",
            "loan payment calculator",
            "monthly loan payment calculator",
            "loan interest calculator",
            "loan amortization calculator",
            "fixed payment loan calculator",
            "financial calculators",
        ]
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
    if calc.get("slug") == "basic-calculator":
        return "Basic Calculator with Memory & History"
    if calc.get("slug") == "debt-payoff-calculator":
        return "Debt Payoff Calculator: Snowball vs Avalanche"
    if calc.get("slug") == "ratio-calculator":
        return "Ratio Calculator: Simplify, Solve & Split Ratios"
    if calc.get("slug") == "bottleneck-calculator":
        return "PC Bottleneck Calculator: CPU vs GPU Checker"
    if calc.get("slug") == "feet-to-meters-calculator":
        return "Feet to Meters Calculator (ft to m)"
    if calc.get("slug") == "loan-calculator":
        return "Loan Calculator: Payment & Interest | NS Calculators"
    if calc.get("slug") == "percent-calculator":
        return "Percentage Calculator: Change, Difference & More"
    if calc.get("slug") == "fraction-calculator":
        return "Fraction Calculator: Add, Subtract, Multiply & Divide"
    if calc.get("slug") == "standard-deviation-calculator":
        return "Standard Deviation Calculator: Sample & Population"
    if calc.get("slug") == "bmi-calculator":
        return "BMI Calculator for Adults: US & Metric Units"
    if calc.get("slug") == "salary-calculator":
        return "Salary Calculator: Hourly, Monthly & Annual Pay"
    if calc.get("slug") == "finance-calculator":
        return "Finance Calculator: PV, FV, PMT, Rate & Periods"
    if calc.get("slug") == "interest-calculator":
        return "Interest Calculator: Simple vs Compound Interest"
    if calc.get("slug") == "amortization-calculator":
        return "Amortization Calculator with Extra Payments & Schedule"
    if calc.get("slug") == "retirement-calculator":
        return "Retirement Calculator: Savings, Income & Withdrawal Plan"
    if calc.get("slug") == "401k-calculator":
        return "401(k) Calculator: Balance, Match & Withdrawal"
    if calc.get("slug") == "social-security-calculator":
        return "Social Security Calculator: Claim Age & Benefits"
    if calc.get("slug") == "rmd-calculator":
        return "RMD Calculator: 2026 Required Minimum Distribution"
    if calc.get("slug") == "payment-calculator":
        return "Payment Calculator: Monthly Payment or Loan Term"
    if calc.get("slug") == "compound-interest-calculator":
        return "Compound Interest Calculator | NS Calculators"
    if calc.get("slug") == "take-home-pay-calculator":
        return "Take Home Pay Calculator 2026 | NS Calculators"
    if calc.get("slug") == "sales-tax-calculator":
        return "Sales Tax Calculator: Add or Reverse Tax | NS Calculators"
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
    context = f" for {display_group(calculator_group(calc)).lower()}" if calc.get("seo_context_label") else ""
    if calc.get("slug") == "basic-calculator":
        return "Use a free basic calculator with arithmetic, percent, square root, memory keys, keyboard input, backspace, and a reusable calculation history."
    if calc.get("slug") == "debt-payoff-calculator":
        return "Compare debt snowball and avalanche payoff plans. Add balances, APRs, minimums, and extra payments to estimate payoff dates and total interest."
    if calc.get("slug") == "ratio-calculator":
        return "Simplify two- or three-part ratios, solve a missing proportion value, scale an equivalent ratio, or divide a total into proportional shares."
    if calc.get("slug") in PRIORITY_LENGTH_CONVERSIONS:
        source, target, _ = conversion_parts(calc)
        return f"Convert {source} to {target} or reverse the calculation. See exact factors, metric and US unit results, common values, formulas, and examples."
    if calc.get("slug") == "feet-to-meters-calculator":
        return "Convert feet or feet and inches to meters using the exact 0.3048 factor. Reverse meters to feet, compare common values, and see the formula."
    if calc.get("slug") == "percent-calculator":
        return "Calculate a percentage of a number, percent of total, reverse percentage, percent change, percentage difference, or a percentage increase or decrease."
    if calc.get("slug") == "fraction-calculator":
        return "Calculate fractions and mixed numbers with step-by-step addition, subtraction, multiplication, division, simplification, decimal, and percent results."
    if calc.get("slug") == "standard-deviation-calculator":
        return "Calculate sample or population standard deviation, variance, mean, sum, range, standard error, and margin of error with step-by-step results."
    if calc.get("slug") == "bmi-calculator":
        return "Calculate adult BMI in US or metric units with CDC category, healthy weight range, BMI Prime, Ponderal Index, formulas, and limitations."
    if calc.get("slug") == "salary-calculator":
        return "Convert hourly, daily, weekly, biweekly, semimonthly, monthly, quarterly, or annual salary and compare pay adjusted for unpaid days off."
    if calc.get("slug") == "finance-calculator":
        return "Solve future value, present value, payment, annual interest rate, or number of periods with payment timing, compounding settings, and a schedule."
    if calc.get("slug") == "interest-calculator":
        return "Compare simple and compound interest with deposits, compounding frequency, tax, inflation, charts, and an annual growth schedule."
    if calc.get("slug") == "payment-calculator":
        return "Calculate a monthly loan payment or payoff term with fixed-payment and fixed-term modes, total interest, payoff time, and an amortization schedule."
    if calc.get("slug") == "amortization-calculator":
        return "Calculate monthly loan payments, total interest, payoff date, and full amortization schedules. Compare monthly, yearly, and one-time extra payments."
    if calc.get("slug") == "retirement-calculator":
        return "Estimate your retirement savings target, monthly savings gap, retirement income, and how long money may last with inflation-adjusted projections."
    if calc.get("slug") == "401k-calculator":
        return "Project your 401(k) balance, employer match, and retirement income. Estimate early-withdrawal taxes and penalties using current 2026 limits."
    if calc.get("slug") == "social-security-calculator":
        return "Compare Social Security claiming ages, lifetime retirement benefits, break-even timing, and 2026 earnings-test withholding using official SSA rules."
    if calc.get("slug") == "rmd-calculator":
        return "Calculate your 2026 required minimum distribution from an IRA or retirement account using current IRS life-expectancy tables, with a future RMD schedule."
    if calc.get("slug") == "compound-interest-calculator":
        return "Calculate compound interest with monthly and annual contributions, tax, inflation, years and months, detailed growth charts, and an annual schedule."
    if calc.get("slug") == "truck-payload-calculator":
        return "Calculate truck payload capacity and remaining payload from GVWR, curb weight, passengers, cargo, and trailer tongue weight."
    if calc.get("slug") == "towing-capacity-calculator":
        return "Estimate safe trailer weight from tow rating, GCWR, GVWR, payload, hitch rating, cargo, passengers, and tongue weight percentage."
    if calc.get("slug") == "mpg-calculator":
        return "Calculate gas mileage from distance and fuel used, with instant US MPG, Imperial MPG, L/100 km, and kilometers-per-liter results."
    if calc.get("slug") == "trip-fuel-cost-calculator":
        return "Estimate one-way or round-trip fuel cost, gallons or liters needed, cost per mile, and each traveler's share in US or metric units."
    if calc.get("slug") == "car-depreciation-calculator":
        return "Estimate car value loss with constant or two-stage depreciation, a yearly schedule, retained value, depreciation per year, and cost per mile."
    if calc.get("slug") == "car-resale-value-calculator":
        return "Project a car's future resale value, depreciation range, selling costs, loan payoff, net proceeds, and year-by-year value schedule."
    if calc.get("slug") == "horsepower-calculator":
        return "Calculate horsepower, torque, or RPM in either direction. Convert lb-ft to N-m and compare mechanical horsepower, kilowatts, and metric PS."
    if calc.get("slug") == "power-to-weight-ratio-calculator":
        return "Calculate vehicle power-to-weight ratio in hp/lb, lb/hp, hp per ton, and W/kg with power, weight, load, and target-ratio unit conversions."
    if calc.get("slug") == "bottleneck-calculator":
        return "Check whether a PC is CPU-bound, GPU-bound, frame-capped, or balanced using measured FPS, utilization, frame times, or benchmark FPS ceilings."
    if calc.get("slug") == "car-trade-in-value-calculator":
        return "Estimate a transparent car trade-in value, loan equity, possible sales-tax benefit, and effective trade value from a local comparable listing."
    if calc.get("slug") == "used-car-value-calculator":
        return "Estimate used-car retail, private-party, and trade-in ranges from a local comparable price, mileage, condition, options, and market adjustments."
    if calc.get("slug") == "tire-size-calculator":
        return "Compare two tire sizes for diameter, sidewall, circumference, revolutions per mile, speedometer error, and ground-clearance change."
    if calc.get("slug") == "wheel-offset-calculator":
        return "Compare current and new wheel width, offset, and spacer size to estimate inner clearance, outer poke, track change, and backspacing."
    if calc.get("slug") == "concrete-volume-calculator":
        return "Calculate concrete cubic yards, cubic feet, bag count, and estimated material cost for slabs, footings, round columns, and post holes."
    if calc.get("slug") == "roof-pitch-calculator":
        return "Calculate roof pitch, angle, percent slope, pitch multiplier, rafter length, sloped area, and roofing squares from pitch, rise and run, or angle."
    if calc.get("slug") == "rafter-length-calculator":
        return "Calculate common rafter length, roof rise, slope factor, angle, and horizontal-overhang adjustment from run and roof pitch."
    if calc.get("slug") == "square-footage-calculator":
        return "Calculate square footage for rectangles, circles, triangles, or room walls, including openings, overage, perimeter, and estimated material cost."
    if calc.get("slug") == "flooring-calculator":
        return "Calculate flooring square footage, waste, full boxes, purchased coverage, leftover material, underlayment, and estimated project cost."
    if calc.get("slug") == "tile-calculator":
        return "Calculate floor or wall tile quantity, waste, full boxes, purchased coverage, leftover tile, and estimated material cost."
    if calc.get("slug") == "deck-board-calculator":
        return "Calculate deck-board rows, full boards, linear feet, joists, fasteners, package quantities, waste, and estimated material cost."
    if calc.get("slug") == "board-foot-calculator":
        return "Calculate board feet per piece and total lumber volume, including quantity, waste allowance, cubic feet, linear feet, and estimated cost."
    if calc.get("slug") == "voltage-drop-calculator":
        return "Calculate voltage drop, voltage at the load, drop percentage, and maximum run length for copper or aluminum wire in DC, single-phase, or three-phase circuits."
    if calc.get("slug") == "wire-size-calculator":
        return "Estimate copper or aluminum wire size from load, continuous-use factor, reference ampacity, circuit length, voltage, phase, and maximum voltage drop."
    if calc.get("slug") == "breaker-size-calculator":
        return "Estimate a standard breaker size from continuous and noncontinuous load current, including the 125% continuous-load planning factor and circuit utilization."
    if calc.get("slug") == "electrical-load-calculator":
        return "Calculate amps, apparent power, continuous-load planning current, and a reference breaker size from watts, voltage, phase, and power factor."
    if calc.get("slug") == "watts-to-amps-calculator":
        return "Convert watts to amps for DC, single-phase AC, or balanced three-phase AC, with power factor, VA, kVA, reactive power, and continuous-load planning current."
    if calc.get("slug") == "amps-to-watts-calculator":
        return "Convert amps to watts and kilowatts for DC, single-phase AC, or balanced three-phase AC, including power factor, VA, kVA, and reactive power."
    if calc.get("slug") == "loan-calculator":
        return "Calculate loan payments, total interest, amortization, deferred loan maturity value, and bond present value with monthly or custom payment frequency."
    if calc.get("slug") == "salary-increase-calculator":
        return "Calculate a raise by percent or dollars and compare new annual, monthly, biweekly, weekly, hourly, and inflation-adjusted pay."
    if calc.get("slug") == "discount-calculator":
        return "Calculate one or two discounts, savings, quantity, sales tax, fees, effective discount, and the estimated final checkout total."
    if calc.get("slug") == "take-home-pay-calculator":
        return "Estimate 2026 US take-home pay by paycheck with federal brackets, Social Security, Medicare, state tax, and payroll deductions."
    if calc.get("slug") == "sales-tax-calculator":
        return "Add sales tax, reverse tax from a total, or find the tax rate with quantity, discount, shipping, and taxable-shipping options."
    if calc.get("engine") == "linear_convert":
        return f"Use this free {keyword} to convert units instantly with the formula, example, and related conversion calculators."
    if calc.get("engine") in ("cn_mortgage", "loan_page", "car_loan"):
        return f"Use this free {keyword}{context} for US planning with instant results, payment details, charts, formulas, and no signup."
    return f"Use this free {keyword}{context} for instant answers with clear inputs, formulas, examples, related tools, and no signup."


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


def conversion_parts(calc):
    source = target = ""
    factor = 0.0
    for field in calc.get("inputs", []):
        if field[0] == "value":
            source = str(field[1]).replace("Value in ", "")
        elif field[0] == "target":
            target = str(field[3])
        elif field[0] == "factor":
            factor = float(field[3])
    return source, target, factor


def priority_length_input_html(calc):
    source, target, factor = conversion_parts(calc)
    source_symbol = LENGTH_UNIT_SYMBOLS[source]
    target_symbol = LENGTH_UNIT_SYMBOLS[target]
    return f"""<div class="fields conversion-fields">
<div class="field field-wide"><label for="length_direction">Conversion direction</label><select id="length_direction"><option value="forward" selected>{h(source.title())} to {h(target.title())}</option><option value="reverse">{h(target.title())} to {h(source.title())}</option></select></div>
<div class="field field-wide"><label for="length_value">Value to convert</label><input id="length_value" type="number" step="any" value="1"></div>
<input id="conversion_factor" type="hidden" value="{factor:.15g}"><input id="source_name" type="hidden" value="{h(source)}"><input id="target_name" type="hidden" value="{h(target)}"><input id="source_symbol" type="hidden" value="{h(source_symbol)}"><input id="target_symbol" type="hidden" value="{h(target_symbol)}"><input id="source_meter_factor" type="hidden" value="{LENGTH_UNIT_METERS[source]:.15g}"><input id="target_meter_factor" type="hidden" value="{LENGTH_UNIT_METERS[target]:.15g}">
</div>"""


def compound_interest_input_html(include_scenarios=False):
    scenario_fields = """<div class="field"><label for="contribution_growth">Annual contribution increase</label><div class="input-unit"><input id="contribution_growth" type="number" step="any" min="-99" value="0"><span>%</span></div></div><div class="field"><label for="rate_variance">Interest rate range (+/-)</label><div class="input-unit"><input id="rate_variance" type="number" step="any" min="0" value="2"><span>%</span></div></div>""" if include_scenarios else ""
    options_label = "Contribution growth, tax, and scenarios" if include_scenarios else "Tax and inflation"
    return f"""<div class="fields compound-fields">
<div class="field"><label for="principal">Initial investment</label><div class="input-unit"><input id="principal" type="number" step="any" min="0" value="10000"><span>$</span></div></div>
<div class="field"><label for="rate">Annual interest rate</label><div class="input-unit"><input id="rate" type="number" step="any" value="6"><span>%</span></div></div>
<div class="field"><label for="years">Investment length</label><div class="input-unit"><input id="years" type="number" step="1" min="0" value="10"><span>years</span></div></div>
<div class="field"><label for="compound_months">Additional months</label><div class="input-unit"><input id="compound_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field"><label for="monthly">Monthly contribution</label><div class="input-unit"><input id="monthly" type="number" step="any" min="0" value="200"><span>$</span></div></div>
<div class="field"><label for="annual_contribution">Annual contribution</label><div class="input-unit"><input id="annual_contribution" type="number" step="any" min="0" value="0"><span>$</span></div></div>
<div class="field"><label for="compound_frequency">Compound frequency</label><select id="compound_frequency"><option value="365">Daily</option><option value="52">Weekly</option><option value="26">Biweekly</option><option value="24">Semimonthly</option><option value="12" selected>Monthly</option><option value="4">Quarterly</option><option value="2">Semi-annually</option><option value="1">Annually</option><option value="0">Continuously</option></select></div>
<div class="field"><label for="contribution_timing">Contribution timing</label><select id="contribution_timing"><option value="end" selected>End of period</option><option value="beginning">Beginning of period</option></select></div>
<details class="more-options field-wide"><summary>{options_label}</summary><div class="fields">{scenario_fields}<div class="field"><label for="interest_tax">Tax rate on interest</label><div class="input-unit"><input id="interest_tax" type="number" step="any" min="0" max="100" value="0"><span>%</span></div></div><div class="field"><label for="compound_inflation">Expected inflation rate</label><div class="input-unit"><input id="compound_inflation" type="number" step="any" min="-99" value="3"><span>%</span></div></div></div></details>
</div>"""


def salary_increase_input_html():
    return """<div class="fields salary-fields">
<div class="field"><label for="salary">Current annual salary</label><div class="input-unit"><input id="salary" type="number" step="any" min="0" value="60000"><span>$</span></div></div>
<div class="field"><label for="raise_unit">Raise entered as</label><select id="raise_unit"><option value="percent" selected>Percentage (%)</option><option value="dollar">Annual dollars ($)</option></select></div>
<div class="field"><label for="raise_amount">Raise amount</label><input id="raise_amount" type="number" step="any" value="5"></div>
<details class="more-options field-wide"><summary>Pay schedule and inflation</summary><div class="fields"><div class="field field-wide"><label for="pay_periods">Pay periods per year</label><select id="pay_periods"><option value="12">Monthly (12)</option><option value="24">Semimonthly (24)</option><option value="26" selected>Biweekly (26)</option><option value="52">Weekly (52)</option></select></div><div class="field"><label for="hours_week">Hours per week</label><input id="hours_week" type="number" step="any" min="0.1" value="40"></div><div class="field"><label for="weeks_year">Working weeks per year</label><input id="weeks_year" type="number" step="any" min="0.1" value="52"></div><div class="field field-wide"><label for="inflation_rate">Expected inflation rate</label><div class="input-unit"><input id="inflation_rate" type="number" step="any" min="-99" value="3"><span>%</span></div></div></div></details>
</div>"""


def discount_input_html():
    return """<div class="fields discount-fields">
<div class="field"><label for="price">Original unit price</label><div class="input-unit"><input id="price" type="number" step="any" min="0" value="100"><span>$</span></div></div>
<div class="field"><label for="discount">First discount</label><div class="input-unit"><input id="discount" type="number" step="any" min="0" max="100" value="20"><span>%</span></div></div>
<div class="field"><label for="discount_two">Second discount</label><div class="input-unit"><input id="discount_two" type="number" step="any" min="0" max="100" value="0"><span>%</span></div></div>
<details class="more-options field-wide"><summary>Quantity, tax, and fees</summary><div class="fields"><div class="field"><label for="quantity">Quantity</label><input id="quantity" type="number" step="1" min="1" value="1"></div><div class="field"><label for="sales_tax">Estimated sales tax</label><div class="input-unit"><input id="sales_tax" type="number" step="any" min="0" value="8.25"><span>%</span></div></div><div class="field field-wide"><label for="checkout_fees">Shipping and other fees</label><div class="input-unit"><input id="checkout_fees" type="number" step="any" min="0" value="0"><span>$</span></div></div></div></details>
</div>"""


def take_home_pay_input_html():
    return """<div class="fields take-home-fields">
<div class="field"><label for="pay_gross">Annual gross salary</label><div class="input-unit"><input id="pay_gross" type="number" step="any" min="0" value="75000"><span>$</span></div></div>
<div class="field"><label for="pay_status">Federal filing status</label><select id="pay_status"><option value="single" selected>Single</option><option value="joint">Married filing jointly</option><option value="head">Head of household</option></select></div>
<div class="field field-wide"><label for="pay_periods">Pay frequency</label><select id="pay_periods"><option value="12">Monthly (12 paychecks)</option><option value="24">Semimonthly (24 paychecks)</option><option value="26" selected>Biweekly (26 paychecks)</option><option value="52">Weekly (52 paychecks)</option></select></div>
<details class="more-options field-wide"><summary>Deductions, state tax, and withholding</summary><div class="fields">
<div class="field"><label for="pay_retirement">Pre-tax retirement contribution</label><div class="input-unit"><input id="pay_retirement" type="number" step="any" min="0" value="4500"><span>$/yr</span></div></div>
<div class="field"><label for="pay_pretax">Other pre-tax benefits</label><div class="input-unit"><input id="pay_pretax" type="number" step="any" min="0" value="2400"><span>$/yr</span></div></div>
<div class="field"><label for="pay_deduction_mode">Federal deduction</label><select id="pay_deduction_mode"><option value="standard" selected>2026 standard deduction</option><option value="custom">Custom deduction amount</option></select></div>
<div class="field is-hidden" data-pay-custom><label for="pay_custom_deduction">Custom federal deduction</label><div class="input-unit"><input id="pay_custom_deduction" type="number" step="any" min="0" value="0"><span>$</span></div></div>
<div class="field"><label for="pay_state_rate">State and local effective rate</label><div class="input-unit"><input id="pay_state_rate" type="number" step="any" min="0" value="5"><span>%</span></div></div>
<div class="field"><label for="pay_posttax">Post-tax deductions</label><div class="input-unit"><input id="pay_posttax" type="number" step="any" min="0" value="600"><span>$/yr</span></div></div>
<div class="field field-wide"><label for="pay_extra">Extra federal withholding</label><div class="input-unit"><input id="pay_extra" type="number" step="any" min="0" value="0"><span>$/paycheck</span></div></div>
</div></details>
</div>"""


def sales_tax_input_html():
    return """<div class="fields sales-tax-fields">
<div class="field field-wide"><label for="sales_mode">Calculate</label><select id="sales_mode"><option value="add" selected>Add tax to a purchase</option><option value="reverse">Reverse tax from a total</option><option value="rate">Find the sales tax rate</option></select></div>
<div class="field" data-sales-add data-sales-rate><label for="sales_price">Price before tax</label><div class="input-unit"><input id="sales_price" type="number" step="any" min="0" value="100"><span>$</span></div></div>
<div class="field is-hidden" data-sales-reverse><label for="sales_total">Tax-inclusive total</label><div class="input-unit"><input id="sales_total" type="number" step="any" min="0" value="108.25"><span>$</span></div></div>
<div class="field is-hidden" data-sales-rate><label for="sales_after">Price after tax</label><div class="input-unit"><input id="sales_after" type="number" step="any" min="0" value="108.25"><span>$</span></div></div>
<div class="field" data-sales-rate-input><label for="sales_rate">Combined sales tax rate</label><div class="input-unit"><input id="sales_rate" type="number" step="any" min="0" value="8.25"><span>%</span></div></div>
<details class="more-options field-wide" data-sales-add><summary>Quantity, discount, and shipping</summary><div class="fields">
<div class="field"><label for="sales_quantity">Quantity</label><input id="sales_quantity" type="number" step="1" min="1" value="1"></div>
<div class="field"><label for="sales_discount">Discount</label><div class="input-unit"><input id="sales_discount" type="number" step="any" min="0" max="100" value="0"><span>%</span></div></div>
<div class="field"><label for="sales_shipping">Shipping and handling</label><div class="input-unit"><input id="sales_shipping" type="number" step="any" min="0" value="0"><span>$</span></div></div>
<div class="field"><label for="sales_shipping_taxable">Tax shipping?</label><select id="sales_shipping_taxable"><option value="no" selected>No</option><option value="yes">Yes</option></select></div>
</div></details>
</div>"""


def percent_input_html():
    return """<div class="fields percent-fields">
<div class="field field-wide"><label for="percent_mode">Calculate</label><select id="percent_mode"><option value="percent_of" selected>What is X% of Y?</option><option value="what_percent">X is what percent of Y?</option><option value="find_whole">X is Y% of what?</option><option value="change">Percent change from X to Y</option><option value="difference">Percentage difference between X and Y</option><option value="adjust">Increase or decrease X by Y%</option></select></div>
<div class="field" data-percent-mode="percent_of"><label for="pct_percent">Percent</label><div class="input-unit"><input id="pct_percent" type="number" step="any" value="20"><span>%</span></div></div>
<div class="field" data-percent-mode="percent_of"><label for="pct_value">Value</label><input id="pct_value" type="number" step="any" value="150"></div>
<div class="field is-hidden" data-percent-mode="what_percent"><label for="pct_part">Part (X)</label><input id="pct_part" type="number" step="any" value="30"></div>
<div class="field is-hidden" data-percent-mode="what_percent"><label for="pct_whole">Whole (Y)</label><input id="pct_whole" type="number" step="any" value="150"></div>
<div class="field is-hidden" data-percent-mode="find_whole"><label for="pct_known_part">Part (X)</label><input id="pct_known_part" type="number" step="any" value="30"></div>
<div class="field is-hidden" data-percent-mode="find_whole"><label for="pct_known_percent">Percent (Y)</label><div class="input-unit"><input id="pct_known_percent" type="number" step="any" value="20"><span>%</span></div></div>
<div class="field is-hidden" data-percent-mode="change"><label for="pct_old">Original value</label><input id="pct_old" type="number" step="any" value="100"></div>
<div class="field is-hidden" data-percent-mode="change"><label for="pct_new">New value</label><input id="pct_new" type="number" step="any" value="125"></div>
<div class="field is-hidden" data-percent-mode="difference"><label for="pct_value_one">First value</label><input id="pct_value_one" type="number" step="any" value="80"></div>
<div class="field is-hidden" data-percent-mode="difference"><label for="pct_value_two">Second value</label><input id="pct_value_two" type="number" step="any" value="120"></div>
<div class="field is-hidden" data-percent-mode="adjust"><label for="pct_base">Starting value</label><input id="pct_base" type="number" step="any" value="200"></div>
<div class="field is-hidden" data-percent-mode="adjust"><label for="pct_adjust">Percent change</label><div class="input-unit"><input id="pct_adjust" type="number" step="any" min="0" value="15"><span>%</span></div></div>
<div class="field field-wide is-hidden" data-percent-mode="adjust"><label for="pct_direction">Operation</label><select id="pct_direction"><option value="increase" selected>Increase by the percentage</option><option value="decrease">Decrease by the percentage</option></select></div>
</div>"""


def fraction_input_html():
    return """<div class="fields fraction-fields">
<div class="field field-wide"><label for="fraction_mode">Calculate</label><select id="fraction_mode"><option value="arithmetic" selected>Fraction and mixed-number arithmetic</option><option value="simplify">Simplify a fraction</option><option value="decimal">Convert a decimal to a fraction</option></select></div>
<div class="field-group-label" data-fraction-mode="arithmetic">First number</div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_a_whole">Whole</label><input id="frac_a_whole" type="number" step="1" value="0"></div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_a_num">Numerator</label><input id="frac_a_num" type="number" step="1" value="1"></div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_a_den">Denominator</label><input id="frac_a_den" type="number" step="1" value="2"></div>
<div class="field field-wide" data-fraction-mode="arithmetic"><label for="fraction_operation">Operation</label><select id="fraction_operation"><option value="add" selected>Add (+)</option><option value="subtract">Subtract (-)</option><option value="multiply">Multiply (x)</option><option value="divide">Divide (divide)</option></select></div>
<div class="field-group-label" data-fraction-mode="arithmetic">Second number</div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_b_whole">Whole</label><input id="frac_b_whole" type="number" step="1" value="0"></div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_b_num">Numerator</label><input id="frac_b_num" type="number" step="1" value="1"></div>
<div class="field" data-fraction-mode="arithmetic"><label for="frac_b_den">Denominator</label><input id="frac_b_den" type="number" step="1" value="3"></div>
<div class="field is-hidden" data-fraction-mode="simplify"><label for="frac_simple_num">Numerator</label><input id="frac_simple_num" type="number" step="1" value="42"></div>
<div class="field is-hidden" data-fraction-mode="simplify"><label for="frac_simple_den">Denominator</label><input id="frac_simple_den" type="number" step="1" value="56"></div>
<div class="field field-wide is-hidden" data-fraction-mode="decimal"><label for="fraction_decimal">Decimal</label><input id="fraction_decimal" type="number" step="any" value="0.375"></div>
</div>"""


def standard_deviation_input_html():
    return """<div class="fields stats-fields">
<div class="field field-wide"><label for="stats_values">Data values</label><textarea id="stats_values" rows="4" spellcheck="false">10, 12, 23, 23, 16, 23, 21, 16</textarea><small>Separate numbers with commas, spaces, semicolons, or new lines.</small></div>
<div class="field"><label for="stats_type">Data represents</label><select id="stats_type"><option value="population" selected>Entire population</option><option value="sample">Sample of a population</option></select></div>
<div class="field"><label for="stats_confidence">Confidence level</label><select id="stats_confidence"><option value="1.645">90% normal approximation</option><option value="1.96" selected>95% normal approximation</option><option value="2.576">99% normal approximation</option></select></div>
</div>"""


def bmi_input_html():
    return """<div class="fields bmi-fields">
<div class="field field-wide"><label for="bmi_units">Units</label><select id="bmi_units"><option value="us" selected>US customary (lb, ft, in)</option><option value="metric">Metric (kg, cm)</option></select></div>
<div class="field" data-bmi-us><label for="bmi_weight_lb">Weight</label><div class="input-unit"><input id="bmi_weight_lb" type="number" step="any" min="1" value="160"><span>lb</span></div></div>
<div class="field" data-bmi-us><label for="bmi_height_ft">Height feet</label><div class="input-unit"><input id="bmi_height_ft" type="number" step="1" min="1" value="5"><span>ft</span></div></div>
<div class="field field-wide" data-bmi-us><label for="bmi_height_in">Additional inches</label><div class="input-unit"><input id="bmi_height_in" type="number" step="any" min="0" max="11.99" value="10"><span>in</span></div></div>
<div class="field is-hidden" data-bmi-metric><label for="bmi_weight_kg">Weight</label><div class="input-unit"><input id="bmi_weight_kg" type="number" step="any" min="1" value="72.57"><span>kg</span></div></div>
<div class="field is-hidden" data-bmi-metric><label for="bmi_height_cm">Height</label><div class="input-unit"><input id="bmi_height_cm" type="number" step="any" min="1" value="177.8"><span>cm</span></div></div>
<div class="field-note field-wide">For adults age 20 and older. Children and teens require BMI-for-age percentiles.</div>
</div>"""


def finance_tvm_input_html():
    return """<div class="fields finance-tvm-fields">
<div class="field field-wide"><label for="finance_solve">Calculate</label><select id="finance_solve"><option value="fv" selected>FV - Future Value</option><option value="pmt">PMT - Periodic Payment</option><option value="iy">I/Y - Annual Interest Rate</option><option value="n">N - Number of Periods</option><option value="pv">PV - Present Value</option></select></div>
<div class="field" data-finance-value="n"><label for="finance_n">N - number of periods</label><input id="finance_n" type="number" step="any" min="0" value="10"></div>
<div class="field" data-finance-value="iy"><label for="finance_iy">I/Y - interest per year</label><div class="input-unit"><input id="finance_iy" type="number" step="any" value="6"><span>%</span></div></div>
<div class="field" data-finance-value="pv"><label for="finance_pv">PV - present value</label><div class="input-unit"><input id="finance_pv" type="number" step="any" value="20000"><span>$</span></div></div>
<div class="field" data-finance-value="pmt"><label for="finance_pmt">PMT - periodic payment</label><div class="input-unit"><input id="finance_pmt" type="number" step="any" value="-2000"><span>$</span></div></div>
<div class="field field-wide" data-finance-value="fv"><label for="finance_fv">FV - future value</label><div class="input-unit"><input id="finance_fv" type="number" step="any" value="-9455.36"><span>$</span></div></div>
<details class="more-options field-wide"><summary>Payment and compounding settings</summary><div class="fields">
<div class="field"><label for="finance_py">Payments per year (P/Y)</label><input id="finance_py" type="number" step="1" min="1" value="1"></div>
<div class="field"><label for="finance_cy">Compounds per year (C/Y)</label><input id="finance_cy" type="number" step="1" min="1" value="1"></div>
<div class="field field-wide"><label for="finance_timing">Payments made at</label><select id="finance_timing"><option value="end" selected>End of each period</option><option value="beginning">Beginning of each period</option></select></div>
</div></details>
<div class="field-note field-wide">Use opposite signs for money received and money paid. For example, enter a loan received as positive PV and repayments as negative PMT.</div>
</div>"""


def salary_converter_input_html():
    return """<div class="fields salary-converter-fields">
<div class="field"><label for="salary_amount">Salary amount</label><div class="input-unit"><input id="salary_amount" type="number" step="any" min="0" value="50"><span>$</span></div></div>
<div class="field"><label for="salary_period">Paid per</label><select id="salary_period"><option value="hour" selected>Hour</option><option value="day">Day</option><option value="week">Week</option><option value="biweekly">Two weeks (biweekly)</option><option value="semimonthly">Half month (semimonthly)</option><option value="month">Month</option><option value="quarter">Quarter</option><option value="year">Year</option></select></div>
<div class="field"><label for="salary_hours_week">Hours per week</label><input id="salary_hours_week" type="number" step="any" min="0.1" value="40"></div>
<div class="field"><label for="salary_days_week">Days per week</label><input id="salary_days_week" type="number" step="any" min="0.1" max="7" value="5"></div>
<details class="more-options field-wide"><summary>Holidays and vacation</summary><div class="fields"><div class="field"><label for="salary_holidays">Holidays per year</label><input id="salary_holidays" type="number" step="1" min="0" value="10"></div><div class="field"><label for="salary_vacation">Vacation days per year</label><input id="salary_vacation" type="number" step="1" min="0" value="15"></div></div><p class="option-note">The adjusted column treats these as unpaid non-working days. Use the unadjusted column when salary or leave is paid.</p></details>
</div>"""


def feet_to_meters_input_html():
    return """<div class="fields feet-meter-fields">
<div class="field field-wide"><label for="conversion_direction">Conversion direction</label><select id="conversion_direction"><option value="feet_to_meters" selected>Feet and inches to meters</option><option value="meters_to_feet">Meters to feet and inches</option></select></div>
<div class="field" data-feet-input><label for="feet">Feet</label><div class="input-unit"><input id="feet" type="number" step="any" min="0" value="5"><span>ft</span></div></div>
<div class="field" data-feet-input><label for="inches">Additional inches</label><div class="input-unit"><input id="inches" type="number" step="any" min="0" value="10"><span>in</span></div></div>
<div class="field field-wide is-hidden" data-meter-input><label for="meters">Meters</label><div class="input-unit"><input id="meters" type="number" step="any" min="0" value="1.778"><span>m</span></div></div>
</div><p class="field-note">Results update as you type. Inches above 12 are automatically included in the total length.</p>"""


def truck_payload_input_html():
    return """<div class="fields vehicle-weight-fields">
<div class="field"><label for="gvwr">Vehicle GVWR</label><div class="input-unit"><input id="gvwr" type="number" step="any" min="0" value="7200"><span>lb</span></div></div>
<div class="field"><label for="curb">Curb weight</label><div class="input-unit"><input id="curb" type="number" step="any" min="0" value="5200"><span>lb</span></div></div>
<div class="field"><label for="people">Driver and passengers</label><div class="input-unit"><input id="people" type="number" step="any" min="0" value="400"><span>lb</span></div></div>
<div class="field"><label for="cargo">Cab and bed cargo</label><div class="input-unit"><input id="cargo" type="number" step="any" min="0" value="200"><span>lb</span></div></div>
<div class="field field-wide"><label for="tongue">Trailer tongue weight</label><div class="input-unit"><input id="tongue" type="number" step="any" min="0" value="750"><span>lb</span></div></div>
</div>"""


def towing_capacity_input_html():
    return """<div class="fields vehicle-weight-fields towing-fields">
<div class="field"><label for="rating">Maximum tow rating</label><div class="input-unit"><input id="rating" type="number" step="any" min="0" value="10000"><span>lb</span></div></div>
<div class="field"><label for="hitch_rating">Hitch trailer rating</label><div class="input-unit"><input id="hitch_rating" type="number" step="any" min="0" value="10000"><span>lb</span></div></div>
<div class="field"><label for="gcwr">Vehicle GCWR</label><div class="input-unit"><input id="gcwr" type="number" step="any" min="0" value="16000"><span>lb</span></div></div>
<div class="field"><label for="gvwr">Vehicle GVWR</label><div class="input-unit"><input id="gvwr" type="number" step="any" min="0" value="7200"><span>lb</span></div></div>
<div class="field"><label for="curb">Curb weight</label><div class="input-unit"><input id="curb" type="number" step="any" min="0" value="5200"><span>lb</span></div></div>
<div class="field"><label for="people">Driver and passengers</label><div class="input-unit"><input id="people" type="number" step="any" min="0" value="400"><span>lb</span></div></div>
<div class="field"><label for="cargo">Vehicle cargo</label><div class="input-unit"><input id="cargo" type="number" step="any" min="0" value="200"><span>lb</span></div></div>
<div class="field"><label for="tongue_pct">Estimated tongue weight</label><div class="input-unit"><input id="tongue_pct" type="number" step="any" min="1" value="12"><span>%</span></div></div>
</div>"""


def debt_payoff_input_html():
    debts = [
        (1, "Credit card", 6800, 22.99, 170),
        (2, "Personal loan", 4000, 12, 130),
        (3, "Auto loan", 14250, 6.49, 285),
        (4, "Other debt", 0, 0, 0),
    ]
    rows = "".join(f"""<fieldset class="debt-row"><legend>Debt {index}</legend>
<div class="field debt-name"><label for="debt_{index}_name">Name</label><input id="debt_{index}_name" type="text" maxlength="32" value="{h(name)}"></div>
<div class="field"><label for="debt_{index}_balance">Current balance</label><div class="input-unit"><input id="debt_{index}_balance" type="number" step="0.01" min="0" value="{balance}"><span>$</span></div></div>
<div class="field"><label for="debt_{index}_apr">APR</label><div class="input-unit"><input id="debt_{index}_apr" type="number" step="0.01" min="0" max="100" value="{apr}"><span>%</span></div></div>
<div class="field"><label for="debt_{index}_minimum">Minimum payment</label><div class="input-unit"><input id="debt_{index}_minimum" type="number" step="0.01" min="0" value="{minimum}"><span>$</span></div></div>
</fieldset>""" for index, name, balance, apr, minimum in debts)
    return f"""<div class="debt-payoff-fields">
<div class="fields debt-settings"><div class="field"><label for="debt_strategy">Detailed payoff plan</label><select id="debt_strategy"><option value="avalanche" selected>Debt avalanche: highest APR first</option><option value="snowball">Debt snowball: lowest balance first</option></select></div>
<div class="field"><label for="debt_extra">Extra monthly payment</label><div class="input-unit"><input id="debt_extra" type="number" step="0.01" min="0" value="100"><span>$</span></div></div>
<div class="field"><label for="debt_start">First payment month</label><input id="debt_start" type="month" value="2026-10"></div></div>
<div class="debt-list" aria-label="Debts to repay">{rows}</div></div>"""


def mpg_input_html():
    return """<div class="fields fuel-fields">
<div class="field"><label for="distance">Distance driven</label><input id="distance" type="number" step="any" min="0" value="300"></div>
<div class="field"><label for="distance_unit">Distance unit</label><select id="distance_unit"><option value="miles" selected>Miles</option><option value="kilometers">Kilometers</option></select></div>
<div class="field"><label for="fuel_used">Fuel used</label><input id="fuel_used" type="number" step="any" min="0.001" value="12"></div>
<div class="field"><label for="fuel_unit">Fuel unit</label><select id="fuel_unit"><option value="us_gallon" selected>US gallons</option><option value="imperial_gallon">Imperial gallons</option><option value="liter">Liters</option></select></div>
</div>"""


def trip_fuel_cost_input_html():
    return """<div class="fields fuel-fields trip-fuel-fields">
<div class="field"><label for="trip_units">Unit system</label><select id="trip_units"><option value="us" selected>US: miles, MPG, $/gal</option><option value="metric">Metric: km, L/100 km, price/L</option></select></div>
<div class="field"><label for="trip_type">Trip type</label><select id="trip_type"><option value="1" selected>One way</option><option value="2">Round trip</option></select></div>
<div class="field"><label for="distance">One-way distance</label><input id="distance" type="number" step="any" min="0" value="650"></div>
<div class="field"><label for="efficiency">Fuel economy</label><input id="efficiency" type="number" step="any" min="0.01" value="28"></div>
<div class="field"><label for="fuelprice">Fuel price</label><input id="fuelprice" type="number" step="any" min="0" value="3.60"></div>
<div class="field"><label for="trips">Number of trips</label><input id="trips" type="number" step="1" min="1" value="1"></div>
<div class="field"><label for="people">People sharing cost</label><input id="people" type="number" step="1" min="1" value="1"></div>
<div class="field"><label for="currency">Currency</label><select id="currency"><option value="USD" selected>USD ($)</option><option value="GBP">GBP (£)</option><option value="EUR">EUR (€)</option><option value="CAD">CAD ($)</option></select></div>
</div>"""


def trade_in_value_input_html():
    return """<div class="fields vehicle-value-fields">
<div class="field"><label for="comparable">Comparable dealer listing</label><div class="input-unit"><input id="comparable" type="number" step="any" min="0" value="22000"><span>$</span></div></div>
<div class="field"><label for="market_adjustment">Condition and mileage adjustment</label><div class="input-unit"><input id="market_adjustment" type="number" step="any" value="-500"><span>$</span></div></div>
<div class="field"><label for="dealer_margin">Dealer resale margin</label><div class="input-unit"><input id="dealer_margin" type="number" step="any" min="0" value="1800"><span>$</span></div></div>
<div class="field"><label for="reconditioning">Repair and cleanup cost</label><div class="input-unit"><input id="reconditioning" type="number" step="any" min="0" value="600"><span>$</span></div></div>
<div class="field"><label for="payoff">Current loan payoff</label><div class="input-unit"><input id="payoff" type="number" step="any" min="0" value="12000"><span>$</span></div></div>
<div class="field"><label for="replacement_price">Replacement vehicle price</label><div class="input-unit"><input id="replacement_price" type="number" step="any" min="0" value="35000"><span>$</span></div></div>
<div class="field field-wide"><label for="tax_rate">Entered trade-in sales-tax credit rate</label><div class="input-unit"><input id="tax_rate" type="number" step="any" min="0" value="6"><span>%</span></div></div>
</div>"""


def used_car_value_input_html():
    return """<div class="fields vehicle-value-fields">
<div class="field"><label for="retail_benchmark">Local comparable retail price</label><div class="input-unit"><input id="retail_benchmark" type="number" step="any" min="0" value="22000"><span>$</span></div></div>
<div class="field"><label for="condition_adjustment">Vehicle condition</label><select id="condition_adjustment"><option value="-12">Fair (-12%)</option><option value="-5" selected>Good (-5%)</option><option value="0">Very good (0%)</option><option value="3">Excellent (+3%)</option></select></div>
<div class="field"><label for="mileage_adjustment">Mileage adjustment</label><div class="input-unit"><input id="mileage_adjustment" type="number" step="any" value="-500"><span>$</span></div></div>
<div class="field"><label for="options_adjustment">Options and history adjustment</label><div class="input-unit"><input id="options_adjustment" type="number" step="any" value="0"><span>$</span></div></div>
<div class="field"><label for="regional_adjustment">Local market adjustment</label><div class="input-unit"><input id="regional_adjustment" type="number" step="any" value="0"><span>%</span></div></div>
<div class="field"><label for="dealer_spread">Retail-to-trade spread</label><div class="input-unit"><input id="dealer_spread" type="number" step="any" min="0" value="12"><span>%</span></div></div>
</div>"""


def car_depreciation_input_html():
    return """<div class="fields vehicle-value-fields depreciation-fields">
<div class="field"><label for="dep_start_value">Starting vehicle value</label><div class="input-unit"><input id="dep_start_value" type="number" step="any" min="0" value="35000"><span>$</span></div></div>
<div class="field"><label for="dep_years">Projection period</label><div class="input-unit"><input id="dep_years" type="number" step="1" min="1" max="30" value="5"><span>years</span></div></div>
<div class="field field-wide"><label for="dep_method">Depreciation method</label><select id="dep_method"><option value="uniform" selected>Same annual rate every year</option><option value="two_stage">First-year rate plus later-year rate</option></select></div>
<div class="field" data-dep-uniform><label for="dep_rate">Annual depreciation rate</label><div class="input-unit"><input id="dep_rate" type="number" step="any" min="0" max="100" value="15"><span>%</span></div></div>
<div class="field is-hidden" data-dep-two-stage><label for="dep_first_rate">First-year depreciation</label><div class="input-unit"><input id="dep_first_rate" type="number" step="any" min="0" max="100" value="20"><span>%</span></div></div>
<div class="field is-hidden" data-dep-two-stage><label for="dep_later_rate">Later annual depreciation</label><div class="input-unit"><input id="dep_later_rate" type="number" step="any" min="0" max="100" value="15"><span>%</span></div></div>
<details class="more-options field-wide"><summary>Mileage and value floor</summary><div class="fields"><div class="field"><label for="dep_miles_year">Expected miles per year</label><div class="input-unit"><input id="dep_miles_year" type="number" step="any" min="0" value="12000"><span>mi</span></div></div><div class="field"><label for="dep_floor">Minimum projected value</label><div class="input-unit"><input id="dep_floor" type="number" step="any" min="0" value="3000"><span>$</span></div></div></div></details>
</div>"""


def car_resale_input_html():
    return """<div class="fields vehicle-value-fields resale-fields">
<div class="field"><label for="resale_start_value">Current private-party value</label><div class="input-unit"><input id="resale_start_value" type="number" step="any" min="0" value="28000"><span>$</span></div></div>
<div class="field"><label for="resale_years">Years until sale</label><div class="input-unit"><input id="resale_years" type="number" step="1" min="1" max="30" value="3"><span>years</span></div></div>
<div class="field"><label for="resale_rate">Expected annual depreciation</label><div class="input-unit"><input id="resale_rate" type="number" step="any" min="0" max="100" value="14"><span>%</span></div></div>
<div class="field"><label for="resale_miles_year">Expected miles per year</label><div class="input-unit"><input id="resale_miles_year" type="number" step="any" min="0" value="12000"><span>mi</span></div></div>
<details class="more-options field-wide"><summary>Sale proceeds and scenarios</summary><div class="fields"><div class="field"><label for="resale_payoff">Expected loan payoff at sale</label><div class="input-unit"><input id="resale_payoff" type="number" step="any" min="0" value="8000"><span>$</span></div></div><div class="field"><label for="resale_cost_rate">Selling costs</label><div class="input-unit"><input id="resale_cost_rate" type="number" step="any" min="0" max="100" value="2"><span>%</span></div></div><div class="field field-wide"><label for="resale_variance">Depreciation scenario range (+/-)</label><div class="input-unit"><input id="resale_variance" type="number" step="any" min="0" max="100" value="3"><span>points</span></div></div></div></details>
</div>"""


def horsepower_input_html():
    return """<div class="fields performance-fields horsepower-fields">
<div class="field field-wide"><label for="hp_solve">Calculate</label><select id="hp_solve"><option value="power" selected>Horsepower from torque and RPM</option><option value="torque">Torque from horsepower and RPM</option><option value="rpm">RPM from horsepower and torque</option></select></div>
<div class="field" data-hp-torque><label for="hp_torque">Torque</label><input id="hp_torque" type="number" step="any" min="0" value="300"></div>
<div class="field" data-hp-torque><label for="hp_torque_unit">Torque unit</label><select id="hp_torque_unit"><option value="lbft" selected>lb-ft</option><option value="nm">N-m</option></select></div>
<div class="field" data-hp-rpm><label for="hp_rpm">Engine speed</label><div class="input-unit"><input id="hp_rpm" type="number" step="any" min="0" value="4000"><span>RPM</span></div></div>
<div class="field is-hidden" data-hp-power><label for="hp_power">Power</label><input id="hp_power" type="number" step="any" min="0" value="228.48"></div>
<div class="field is-hidden" data-hp-power><label for="hp_power_unit">Power unit</label><select id="hp_power_unit"><option value="hp" selected>Mechanical hp</option><option value="kw">Kilowatts</option><option value="ps">Metric horsepower (PS)</option></select></div>
</div>"""


def power_weight_input_html():
    return """<div class="fields performance-fields power-weight-fields">
<div class="field"><label for="pw_power">Power</label><input id="pw_power" type="number" step="any" min="0" value="300"></div>
<div class="field"><label for="pw_power_unit">Power unit</label><select id="pw_power_unit"><option value="hp" selected>Mechanical hp</option><option value="kw">Kilowatts</option><option value="w">Watts</option><option value="ps">Metric horsepower (PS)</option></select></div>
<div class="field"><label for="pw_weight">Vehicle or system weight</label><input id="pw_weight" type="number" step="any" min="0" value="3600"></div>
<div class="field"><label for="pw_weight_unit">Weight unit</label><select id="pw_weight_unit"><option value="lb" selected>Pounds</option><option value="kg">Kilograms</option><option value="us_ton">US short tons</option><option value="tonne">Metric tonnes</option></select></div>
<details class="more-options field-wide"><summary>Loaded weight and target ratio</summary><div class="fields"><div class="field"><label for="pw_load">Driver, passenger, or cargo load</label><input id="pw_load" type="number" step="any" min="0" value="0"></div><div class="field"><label for="pw_load_unit">Load unit</label><select id="pw_load_unit"><option value="lb" selected>Pounds</option><option value="kg">Kilograms</option></select></div><div class="field field-wide"><label for="pw_target">Target power-to-weight ratio</label><div class="input-unit"><input id="pw_target" type="number" step="any" min="0" value="0.1"><span>hp/lb</span></div></div></div></details>
</div>"""


def ratio_input_html():
    return """<div class="fields ratio-fields">
<div class="field field-wide"><label for="ratio_mode">Calculation</label><select id="ratio_mode"><option value="simplify" selected>Simplify a ratio</option><option value="proportion">Solve a proportion</option><option value="split">Split a total by ratio</option><option value="scale">Scale an equivalent ratio</option></select></div>
<div class="field" data-ratio-base><label for="ratio_a">Part A</label><input id="ratio_a" type="text" inputmode="decimal" value="12" autocomplete="off"></div>
<div class="field" data-ratio-base><label for="ratio_b">Part B</label><input id="ratio_b" type="text" inputmode="decimal" value="18" autocomplete="off"></div>
<div class="field" data-ratio-base><label for="ratio_c">Part C (optional)</label><input id="ratio_c" type="text" inputmode="decimal" placeholder="Leave blank" autocomplete="off"></div>
<div class="field is-hidden" data-ratio-scale><label for="ratio_factor">Scale factor</label><input id="ratio_factor" type="text" inputmode="decimal" value="4" autocomplete="off"></div>
<div class="field is-hidden" data-ratio-split><label for="ratio_total">Total to divide</label><input id="ratio_total" type="number" step="any" min="0" value="100"></div>
<div class="field is-hidden" data-ratio-proportion><label for="ratio_pa">Proportion A</label><input id="ratio_pa" type="text" inputmode="decimal" value="2" autocomplete="off"></div>
<div class="field is-hidden" data-ratio-proportion><label for="ratio_pb">Proportion B</label><input id="ratio_pb" type="text" inputmode="decimal" value="3" autocomplete="off"></div>
<div class="field is-hidden" data-ratio-proportion><label for="ratio_pc">Proportion C</label><input id="ratio_pc" type="text" inputmode="decimal" value="14" autocomplete="off"></div>
<div class="field is-hidden" data-ratio-proportion><label for="ratio_pd">Proportion D</label><input id="ratio_pd" type="text" inputmode="decimal" placeholder="Solve this value" autocomplete="off"></div>
</div>"""


def bottleneck_input_html():
    return """<div class="fields bottleneck-fields">
<div class="field field-wide"><label for="bn_mode">Analysis mode</label><select id="bn_mode"><option value="measured" selected>Measured in-game data (recommended)</option><option value="planning">Benchmark planning comparison</option></select></div>
<div class="field" data-bn-measured><label for="bn_fps">Measured average FPS</label><div class="input-unit"><input id="bn_fps" type="number" step="any" min="0" value="110"><span>FPS</span></div></div>
<div class="field" data-bn-measured><label for="bn_target">Target or refresh rate</label><div class="input-unit"><input id="bn_target" type="number" step="any" min="1" value="144"><span>FPS</span></div></div>
<div class="field" data-bn-measured><label for="bn_gpu_usage">Average GPU utilization</label><div class="input-unit"><input id="bn_gpu_usage" type="number" step="any" min="0" max="100" value="78"><span>%</span></div></div>
<div class="field" data-bn-measured><label for="bn_cpu_usage">Busiest CPU thread utilization</label><div class="input-unit"><input id="bn_cpu_usage" type="number" step="any" min="0" max="100" value="96"><span>%</span></div></div>
<div class="field" data-bn-measured><label for="bn_cpu_ms">CPU frame time</label><div class="input-unit"><input id="bn_cpu_ms" type="number" step="any" min="0" value="9.1"><span>ms</span></div></div>
<div class="field" data-bn-measured><label for="bn_gpu_ms">GPU frame time</label><div class="input-unit"><input id="bn_gpu_ms" type="number" step="any" min="0" value="7"><span>ms</span></div></div>
<div class="field is-hidden" data-bn-planning><label for="bn_cpu_cap">CPU-limited benchmark ceiling</label><div class="input-unit"><input id="bn_cpu_cap" type="number" step="any" min="0" value="180"><span>FPS</span></div></div>
<div class="field is-hidden" data-bn-planning><label for="bn_gpu_cap">GPU-limited benchmark ceiling</label><div class="input-unit"><input id="bn_gpu_cap" type="number" step="any" min="0" value="120"><span>FPS</span></div></div>
<div class="field is-hidden" data-bn-planning><label for="bn_plan_target">Target frame rate</label><div class="input-unit"><input id="bn_plan_target" type="number" step="any" min="1" value="144"><span>FPS</span></div></div>
<div class="field is-hidden" data-bn-planning><label for="bn_uncertainty">Benchmark uncertainty</label><div class="input-unit"><input id="bn_uncertainty" type="number" step="any" min="0" max="50" value="10"><span>%</span></div></div>
</div>"""


def tire_size_input_html():
    return """<div class="fields fitment-fields tire-size-fields">
<div class="field-group-label">Original tire</div>
<div class="field"><label for="original_width">Section width</label><div class="input-unit"><input id="original_width" type="number" step="1" min="1" value="225"><span>mm</span></div></div>
<div class="field"><label for="original_aspect">Aspect ratio</label><div class="input-unit"><input id="original_aspect" type="number" step="1" min="1" value="65"><span>%</span></div></div>
<div class="field"><label for="original_rim">Wheel diameter</label><div class="input-unit"><input id="original_rim" type="number" step="0.5" min="1" value="17"><span>in</span></div></div>
<div class="field-group-label">New tire</div>
<div class="field"><label for="new_width">Section width</label><div class="input-unit"><input id="new_width" type="number" step="1" min="1" value="235"><span>mm</span></div></div>
<div class="field"><label for="new_aspect">Aspect ratio</label><div class="input-unit"><input id="new_aspect" type="number" step="1" min="1" value="60"><span>%</span></div></div>
<div class="field"><label for="new_rim">Wheel diameter</label><div class="input-unit"><input id="new_rim" type="number" step="0.5" min="1" value="18"><span>in</span></div></div>
<div class="field field-wide"><label for="indicated_speed">Indicated speed</label><div class="input-unit"><input id="indicated_speed" type="number" step="1" min="0" value="60"><span>mph</span></div></div>
</div>"""


def wheel_offset_input_html():
    return """<div class="fields fitment-fields wheel-offset-fields">
<div class="field-group-label">Current wheel</div>
<div class="field"><label for="current_width">Wheel width</label><div class="input-unit"><input id="current_width" type="number" step="0.5" min="1" value="8"><span>in</span></div></div>
<div class="field"><label for="current_offset">Offset</label><div class="input-unit"><input id="current_offset" type="number" step="1" value="45"><span>mm</span></div></div>
<div class="field-group-label">New wheel</div>
<div class="field"><label for="new_wheel_width">Wheel width</label><div class="input-unit"><input id="new_wheel_width" type="number" step="0.5" min="1" value="9"><span>in</span></div></div>
<div class="field"><label for="new_offset">Offset</label><div class="input-unit"><input id="new_offset" type="number" step="1" value="35"><span>mm</span></div></div>
<div class="field field-wide"><label for="spacer">Spacer thickness per wheel</label><div class="input-unit"><input id="spacer" type="number" step="1" min="0" value="0"><span>mm</span></div></div>
</div>"""


def concrete_volume_input_html():
    return """<div class="fields project-fields concrete-fields">
<div class="field field-wide"><label for="concrete_shape">Project shape</label><select id="concrete_shape"><option value="slab" selected>Slab, patio, or footing</option><option value="column">Round column</option><option value="post_hole">Round post holes</option></select></div>
<div class="field" data-concrete-rect><label for="concrete_length">Length</label><div class="input-unit"><input id="concrete_length" type="number" step="any" min="0" value="20"><span>ft</span></div></div>
<div class="field" data-concrete-rect><label for="concrete_width">Width</label><div class="input-unit"><input id="concrete_width" type="number" step="any" min="0" value="10"><span>ft</span></div></div>
<div class="field" data-concrete-rect><label for="concrete_thickness">Thickness</label><div class="input-unit"><input id="concrete_thickness" type="number" step="any" min="0" value="4"><span>in</span></div></div>
<div class="field is-hidden" data-concrete-round><label for="concrete_diameter">Diameter</label><div class="input-unit"><input id="concrete_diameter" type="number" step="any" min="0" value="12"><span>in</span></div></div>
<div class="field is-hidden" data-concrete-round><label for="concrete_height">Height or depth</label><div class="input-unit"><input id="concrete_height" type="number" step="any" min="0" value="4"><span>ft</span></div></div>
<div class="field is-hidden" data-concrete-round><label for="concrete_qty">Quantity</label><input id="concrete_qty" type="number" step="1" min="1" value="4"></div>
<div class="field"><label for="concrete_waste">Waste allowance</label><div class="input-unit"><input id="concrete_waste" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="concrete_bag_size">Bag size</label><select id="concrete_bag_size"><option value="0.30">40 lb (0.30 ft³)</option><option value="0.45">60 lb (0.45 ft³)</option><option value="0.60" selected>80 lb (0.60 ft³)</option></select></div>
<details class="more-options field-wide"><summary>Cost options</summary><div class="fields concrete-cost-fields"><div class="field"><label for="concrete_bag_price">Price per bag</label><div class="input-unit"><input id="concrete_bag_price" type="number" step="any" min="0" value="6.25"><span>$</span></div></div><div class="field"><label for="concrete_yard_price">Ready-mix price</label><div class="input-unit"><input id="concrete_yard_price" type="number" step="any" min="0" value="165"><span>$/yd³</span></div></div></div></details>
</div>"""


def roof_pitch_input_html():
    return """<div class="fields project-fields roof-pitch-fields">
<div class="field field-wide"><label for="roof_input_mode">Calculate pitch from</label><select id="roof_input_mode"><option value="pitch" selected>Rise per 12 inches</option><option value="rise_run">Rise and run</option><option value="angle">Angle in degrees</option></select></div>
<div class="field field-wide" data-roof-pitch><label for="roof_pitch">Pitch rise</label><div class="input-unit"><input id="roof_pitch" type="number" step="any" min="0" value="6"><span>/ 12</span></div></div>
<div class="field is-hidden" data-roof-rise-run><label for="roof_rise">Rise</label><div class="input-unit"><input id="roof_rise" type="number" step="any" min="0" value="6"><span>in</span></div></div>
<div class="field is-hidden" data-roof-rise-run><label for="roof_run">Run</label><div class="input-unit"><input id="roof_run" type="number" step="any" min="0.01" value="12"><span>in</span></div></div>
<div class="field field-wide is-hidden" data-roof-angle><label for="roof_angle">Angle from horizontal</label><div class="input-unit"><input id="roof_angle" type="number" step="any" min="0" max="89.9" value="26.565"><span>°</span></div></div>
<div class="field"><label for="roof_rafter_run">Horizontal rafter run</label><div class="input-unit"><input id="roof_rafter_run" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field"><label for="roof_overhang">Horizontal overhang</label><div class="input-unit"><input id="roof_overhang" type="number" step="any" min="0" value="12"><span>in</span></div></div>
<div class="field field-wide"><label for="roof_plan_area">Horizontal plan area (optional)</label><div class="input-unit"><input id="roof_plan_area" type="number" step="any" min="0" value="1200"><span>ft²</span></div></div>
</div>"""


def rafter_length_input_html():
    return """<div class="fields project-fields rafter-fields">
<div class="field"><label for="rafter_pitch">Roof pitch rise</label><div class="input-unit"><input id="rafter_pitch" type="number" step="any" min="0" value="6"><span>/ 12</span></div></div>
<div class="field"><label for="rafter_run">Horizontal run</label><div class="input-unit"><input id="rafter_run" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field"><label for="rafter_overhang">Horizontal overhang</label><div class="input-unit"><input id="rafter_overhang" type="number" step="any" min="0" value="12"><span>in</span></div></div>
<div class="field"><label for="rafter_qty">Number of rafters</label><input id="rafter_qty" type="number" step="1" min="1" value="20"></div>
</div>"""


def square_footage_input_html():
    return """<div class="fields project-fields square-footage-fields">
<div class="field field-wide"><label for="area_shape">Area type</label><select id="area_shape"><option value="rectangle" selected>Rectangle: floor, room, or wall</option><option value="circle">Circle</option><option value="triangle">Triangle</option><option value="room_walls">Four room walls</option></select></div>
<div class="field" data-area-rectangle data-area-walls><label for="area_length">Length</label><div class="input-unit"><input id="area_length" type="number" step="any" min="0" value="20"><span>ft</span></div></div>
<div class="field" data-area-rectangle data-area-walls><label for="area_width">Width</label><div class="input-unit"><input id="area_width" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field is-hidden" data-area-circle><label for="area_diameter">Diameter</label><div class="input-unit"><input id="area_diameter" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field is-hidden" data-area-triangle><label for="area_base">Triangle base</label><div class="input-unit"><input id="area_base" type="number" step="any" min="0" value="20"><span>ft</span></div></div>
<div class="field is-hidden" data-area-triangle><label for="area_height">Triangle height</label><div class="input-unit"><input id="area_height" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field is-hidden" data-area-walls><label for="wall_height">Wall height</label><div class="input-unit"><input id="wall_height" type="number" step="any" min="0" value="8"><span>ft</span></div></div>
<div class="field is-hidden" data-area-walls><label for="area_openings">Doors and windows</label><div class="input-unit"><input id="area_openings" type="number" step="any" min="0" value="40"><span>ft²</span></div></div>
<div class="field"><label for="area_overage">Overage</label><div class="input-unit"><input id="area_overage" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="area_price">Material price</label><div class="input-unit"><input id="area_price" type="number" step="any" min="0" value="3.50"><span>$/ft²</span></div></div>
</div>"""


def flooring_input_html():
    return """<div class="fields project-fields flooring-fields">
<div class="field"><label for="floor_length">Room length</label><div class="input-unit"><input id="floor_length" type="number" step="any" min="0" value="20"><span>ft</span></div></div>
<div class="field"><label for="floor_width">Room width</label><div class="input-unit"><input id="floor_width" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field"><label for="floor_extra">Closets or extra area</label><div class="input-unit"><input id="floor_extra" type="number" step="any" min="0" value="0"><span>ft²</span></div></div>
<div class="field"><label for="floor_waste">Waste allowance</label><div class="input-unit"><input id="floor_waste" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="floor_box_coverage">Coverage per box</label><div class="input-unit"><input id="floor_box_coverage" type="number" step="any" min="0.01" value="24"><span>ft²</span></div></div>
<div class="field"><label for="floor_box_price">Price per box</label><div class="input-unit"><input id="floor_box_price" type="number" step="any" min="0" value="48"><span>$</span></div></div>
<details class="more-options field-wide"><summary>Underlayment options</summary><div class="fields concrete-cost-fields"><div class="field"><label for="underlay_coverage">Coverage per roll</label><div class="input-unit"><input id="underlay_coverage" type="number" step="any" min="0.01" value="100"><span>ft²</span></div></div><div class="field"><label for="underlay_price">Price per roll</label><div class="input-unit"><input id="underlay_price" type="number" step="any" min="0" value="35"><span>$</span></div></div></div></details>
</div>"""


def tile_input_html():
    return """<div class="fields project-fields tile-fields">
<div class="field"><label for="tile_project_length">Project length</label><div class="input-unit"><input id="tile_project_length" type="number" step="any" min="0" value="15"><span>ft</span></div></div>
<div class="field"><label for="tile_project_width">Project width</label><div class="input-unit"><input id="tile_project_width" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field"><label for="tile_width">Tile width</label><div class="input-unit"><input id="tile_width" type="number" step="any" min="0.01" value="12"><span>in</span></div></div>
<div class="field"><label for="tile_height">Tile length</label><div class="input-unit"><input id="tile_height" type="number" step="any" min="0.01" value="12"><span>in</span></div></div>
<div class="field"><label for="tile_waste">Waste allowance</label><div class="input-unit"><input id="tile_waste" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="tile_per_box">Tiles per box</label><input id="tile_per_box" type="number" step="1" min="1" value="15"></div>
<div class="field field-wide"><label for="tile_box_price">Price per box</label><div class="input-unit"><input id="tile_box_price" type="number" step="any" min="0" value="32"><span>$</span></div></div>
</div>"""


def deck_board_input_html():
    return """<div class="fields project-fields deck-board-fields">
<div class="field"><label for="deck_length">Deck length</label><div class="input-unit"><input id="deck_length" type="number" step="any" min="0" value="16"><span>ft</span></div></div>
<div class="field"><label for="deck_width">Deck width</label><div class="input-unit"><input id="deck_width" type="number" step="any" min="0" value="12"><span>ft</span></div></div>
<div class="field"><label for="deck_board_width">Actual board width</label><div class="input-unit"><input id="deck_board_width" type="number" step="any" min="0.01" value="5.5"><span>in</span></div></div>
<div class="field"><label for="deck_gap">Gap between boards</label><div class="input-unit"><input id="deck_gap" type="number" step="any" min="0" value="0.125"><span>in</span></div></div>
<div class="field"><label for="deck_stock_length">Stock board length</label><div class="input-unit"><input id="deck_stock_length" type="number" step="any" min="0.01" value="16"><span>ft</span></div></div>
<div class="field"><label for="deck_waste">Waste allowance</label><div class="input-unit"><input id="deck_waste" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="deck_joist_spacing">Joist spacing</label><div class="input-unit"><input id="deck_joist_spacing" type="number" step="any" min="0.01" value="16"><span>in OC</span></div></div>
<div class="field"><label for="deck_board_price">Price per board</label><div class="input-unit"><input id="deck_board_price" type="number" step="any" min="0" value="35"><span>$</span></div></div>
<details class="more-options field-wide"><summary>Fastener options</summary><div class="fields concrete-cost-fields"><div class="field"><label for="deck_fasteners_crossing">Fasteners per crossing</label><input id="deck_fasteners_crossing" type="number" step="1" min="1" value="2"></div><div class="field"><label for="deck_fastener_pack">Fasteners per box</label><input id="deck_fastener_pack" type="number" step="1" min="1" value="350"></div><div class="field field-wide"><label for="deck_fastener_price">Price per box</label><div class="input-unit"><input id="deck_fastener_price" type="number" step="any" min="0" value="30"><span>$</span></div></div></div></details>
</div>"""


def board_foot_input_html():
    return """<div class="fields project-fields board-foot-fields">
<div class="field"><label for="bf_thickness">Board thickness</label><div class="input-unit"><input id="bf_thickness" type="number" step="any" min="0" value="1"><span>in</span></div></div>
<div class="field"><label for="bf_width">Board width</label><div class="input-unit"><input id="bf_width" type="number" step="any" min="0" value="8"><span>in</span></div></div>
<div class="field"><label for="bf_length">Board length</label><div class="input-unit"><input id="bf_length" type="number" step="any" min="0" value="10"><span>ft</span></div></div>
<div class="field"><label for="bf_quantity">Quantity</label><input id="bf_quantity" type="number" step="1" min="1" value="10"></div>
<div class="field"><label for="bf_waste">Waste allowance</label><div class="input-unit"><input id="bf_waste" type="number" step="any" min="0" value="10"><span>%</span></div></div>
<div class="field"><label for="bf_price">Price per board foot</label><div class="input-unit"><input id="bf_price" type="number" step="any" min="0" value="4.25"><span>$/BF</span></div></div>
</div>"""


def voltage_drop_input_html():
    gauges = [("14", "14 AWG"), ("12", "12 AWG"), ("10", "10 AWG"), ("8", "8 AWG"), ("6", "6 AWG"), ("4", "4 AWG"), ("3", "3 AWG"), ("2", "2 AWG"), ("1", "1 AWG"), ("1/0", "1/0 AWG"), ("2/0", "2/0 AWG"), ("3/0", "3/0 AWG"), ("4/0", "4/0 AWG")]
    options = "".join(f'<option value="{h(value)}"{" selected" if value == "12" else ""}>{h(label)}</option>' for value, label in gauges)
    return f"""<div class="fields project-fields electrical-fields">
<div class="field"><label for="vd_phase">Circuit type</label><select id="vd_phase"><option value="dc">DC</option><option value="single" selected>Single-phase AC</option><option value="three">Three-phase AC</option></select></div>
<div class="field"><label for="vd_material">Conductor</label><select id="vd_material"><option value="copper" selected>Copper</option><option value="aluminum">Aluminum</option></select></div>
<div class="field"><label for="vd_gauge">Wire size</label><select id="vd_gauge">{options}</select></div>
<div class="field"><label for="vd_length">One-way run length</label><div class="input-unit"><input id="vd_length" type="number" step="any" min="0" value="100"><span>ft</span></div></div>
<div class="field"><label for="vd_amps">Load current</label><div class="input-unit"><input id="vd_amps" type="number" step="any" min="0" value="15"><span>A</span></div></div>
<div class="field"><label for="vd_voltage">System voltage</label><div class="input-unit"><input id="vd_voltage" type="number" step="any" min="0.01" value="120"><span>V</span></div></div>
<div class="field field-wide"><label for="vd_limit">Maximum voltage drop</label><div class="input-unit"><input id="vd_limit" type="number" step="any" min="0.1" value="3"><span>%</span></div></div>
</div>"""


def wire_size_input_html():
    return """<div class="fields project-fields electrical-fields">
<div class="field"><label for="ws_amps">Load current</label><div class="input-unit"><input id="ws_amps" type="number" step="any" min="0" value="24"><span>A</span></div></div>
<div class="field"><label for="ws_continuous">Continuous portion</label><div class="input-unit"><input id="ws_continuous" type="number" step="any" min="0" value="24"><span>A</span></div></div>
<div class="field"><label for="ws_material">Conductor</label><select id="ws_material"><option value="copper" selected>Copper</option><option value="aluminum">Aluminum</option></select></div>
<div class="field"><label for="ws_temp">Reference ampacity</label><select id="ws_temp"><option value="60" selected>60°C column</option><option value="75">75°C column</option></select></div>
<div class="field"><label for="ws_phase">Circuit type</label><select id="ws_phase"><option value="dc">DC</option><option value="single" selected>Single-phase AC</option><option value="three">Three-phase AC</option></select></div>
<div class="field"><label for="ws_voltage">System voltage</label><div class="input-unit"><input id="ws_voltage" type="number" step="any" min="0.01" value="240"><span>V</span></div></div>
<div class="field"><label for="ws_length">One-way run length</label><div class="input-unit"><input id="ws_length" type="number" step="any" min="0" value="100"><span>ft</span></div></div>
<div class="field"><label for="ws_drop_limit">Maximum voltage drop</label><div class="input-unit"><input id="ws_drop_limit" type="number" step="any" min="0.1" value="3"><span>%</span></div></div>
</div>"""


def breaker_size_input_html():
    return """<div class="fields project-fields electrical-fields">
<div class="field"><label for="br_continuous">Continuous load</label><div class="input-unit"><input id="br_continuous" type="number" step="any" min="0" value="16"><span>A</span></div></div>
<div class="field"><label for="br_noncontinuous">Noncontinuous load</label><div class="input-unit"><input id="br_noncontinuous" type="number" step="any" min="0" value="0"><span>A</span></div></div>
<div class="field"><label for="br_voltage">Circuit voltage</label><div class="input-unit"><input id="br_voltage" type="number" step="any" min="0.01" value="120"><span>V</span></div></div>
<div class="field"><label for="br_poles">Circuit poles</label><select id="br_poles"><option value="1" selected>Single pole</option><option value="2">Double pole</option><option value="3">Three pole</option></select></div>
</div>"""


def electrical_load_input_html():
    return """<div class="fields project-fields electrical-fields">
<div class="field"><label for="el_continuous">Continuous load</label><div class="input-unit"><input id="el_continuous" type="number" step="any" min="0" value="1800"><span>W</span></div></div>
<div class="field"><label for="el_noncontinuous">Noncontinuous load</label><div class="input-unit"><input id="el_noncontinuous" type="number" step="any" min="0" value="600"><span>W</span></div></div>
<div class="field"><label for="el_voltage">Line voltage</label><div class="input-unit"><input id="el_voltage" type="number" step="any" min="0.01" value="120"><span>V</span></div></div>
<div class="field"><label for="el_phase">Circuit type</label><select id="el_phase"><option value="dc">DC</option><option value="single" selected>Single-phase AC</option><option value="three">Three-phase AC</option></select></div>
<div class="field field-wide"><label for="el_pf">Power factor</label><input id="el_pf" type="number" step="0.01" min="0.01" max="1" value="1"></div>
</div>"""


def watts_to_amps_input_html():
    return """<div class="fields project-fields electrical-fields">
<div class="field"><label for="wa_watts">Real power</label><div class="input-unit"><input id="wa_watts" type="number" step="any" min="0" value="1200"><span>W</span></div></div>
<div class="field"><label for="wa_voltage">Voltage</label><div class="input-unit"><input id="wa_voltage" type="number" step="any" min="0.01" value="120"><span>V</span></div></div>
<div class="field"><label for="wa_phase">Power system</label><select id="wa_phase"><option value="dc">DC</option><option value="single" selected>Single-phase AC</option><option value="three">Three-phase AC</option></select></div>
<div class="field"><label for="wa_pf">Power factor</label><input id="wa_pf" type="number" step="0.01" min="0.01" max="1" value="1"></div>
<div class="field field-wide"><label for="wa_continuous">Load duration</label><select id="wa_continuous"><option value="no" selected>Noncontinuous / conversion only</option><option value="yes">Continuous load planning</option></select></div>
</div>"""


def amps_to_watts_input_html():
    return """<div class="fields project-fields electrical-fields">
<div class="field"><label for="aw_amps">Current</label><div class="input-unit"><input id="aw_amps" type="number" step="any" min="0" value="10"><span>A</span></div></div>
<div class="field"><label for="aw_voltage">Voltage</label><div class="input-unit"><input id="aw_voltage" type="number" step="any" min="0.01" value="120"><span>V</span></div></div>
<div class="field"><label for="aw_phase">Power system</label><select id="aw_phase"><option value="dc">DC</option><option value="single" selected>Single-phase AC</option><option value="three">Three-phase AC</option></select></div>
<div class="field"><label for="aw_pf">Power factor</label><input id="aw_pf" type="number" step="0.01" min="0.01" max="1" value="1"></div>
</div>"""


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


def payment_input_html():
    return """<div class="loan-mode-tabs payment-mode-tabs" role="tablist" aria-label="Payment calculation mode">
<button class="is-active" type="button" role="tab" aria-selected="true" data-payment-mode="term">Fixed Term</button>
<button type="button" role="tab" aria-selected="false" data-payment-mode="payment">Fixed Payments</button>
</div><div class="fields payment-fields">
<div class="field"><label for="payment_amount">Loan amount</label><div class="input-unit"><input id="payment_amount" type="number" step="any" min="0" value="200000"><span>$</span></div></div>
<div class="field"><label for="payment_rate">Interest rate</label><div class="input-unit"><input id="payment_rate" type="number" step="any" min="0" value="6"><span>%</span></div></div>
<div class="field" data-payment-term><label for="payment_years">Loan term</label><div class="input-unit"><input id="payment_years" type="number" step="1" min="0" value="15"><span>years</span></div></div>
<div class="field" data-payment-term><label for="payment_months">Additional months</label><div class="input-unit"><input id="payment_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field field-wide is-hidden" data-payment-fixed><label for="payment_monthly">Monthly payment</label><div class="input-unit"><input id="payment_monthly" type="number" step="any" min="0" value="1687.71"><span>$/mo</span></div></div>
<div class="field-note field-wide" data-payment-term>Enter a repayment period to calculate the required monthly payment.</div>
<div class="field-note field-wide is-hidden" data-payment-fixed>Enter the amount you can pay each month to estimate the payoff time.</div>
</div>"""


def amortization_input_html():
    return """<div class="fields amortization-fields">
<div class="field"><label for="amort_amount">Loan amount</label><div class="input-unit"><input id="amort_amount" type="number" step="any" min="0" value="200000"><span>$</span></div></div>
<div class="field"><label for="amort_rate">Interest rate</label><div class="input-unit"><input id="amort_rate" type="number" step="any" min="0" value="6"><span>%</span></div></div>
<div class="field"><label for="amort_years">Loan term</label><div class="input-unit"><input id="amort_years" type="number" step="1" min="0" value="15"><span>years</span></div></div>
<div class="field"><label for="amort_months">Additional months</label><div class="input-unit"><input id="amort_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field field-wide"><label for="amort_start">Loan start month</label><input id="amort_start" type="month" value="2026-09"></div>
<details class="more-options field-wide"><summary>Optional extra payments</summary><div class="fields">
<div class="field"><label for="amort_extra_monthly">Extra monthly principal</label><div class="input-unit"><input id="amort_extra_monthly" type="number" step="any" min="0" value="0"><span>$/mo</span></div></div>
<div class="field"><label for="amort_extra_yearly">Extra yearly principal</label><div class="input-unit"><input id="amort_extra_yearly" type="number" step="any" min="0" value="0"><span>$/yr</span></div></div>
<div class="field"><label for="amort_extra_once">One-time extra principal</label><div class="input-unit"><input id="amort_extra_once" type="number" step="any" min="0" value="0"><span>$</span></div></div>
<div class="field"><label for="amort_extra_date">One-time payment month</label><input id="amort_extra_date" type="month" value="2027-09"></div>
</div><p class="option-note">Extra amounts are applied directly to principal. Confirm that your lender accepts extra principal payments and whether a prepayment penalty applies.</p></details>
</div>"""


def retirement_input_html():
    return """<div class="loan-mode-tabs retirement-mode-tabs" role="tablist" aria-label="Retirement calculation mode" style="grid-template-columns:repeat(2,minmax(0,1fr))">
<button class="is-active" type="button" role="tab" aria-selected="true" data-retirement-mode="need">How much do I need?</button>
<button type="button" role="tab" aria-selected="false" data-retirement-mode="save">How much should I save?</button>
<button type="button" role="tab" aria-selected="false" data-retirement-mode="withdraw">How much can I withdraw?</button>
<button type="button" role="tab" aria-selected="false" data-retirement-mode="last">How long will it last?</button>
</div><div class="retirement-mode-stack">
<section class="retirement-mode-panel" data-retirement-panel="need"><div class="fields">
<div class="field"><label for="ret_current_age">Current age</label><input id="ret_current_age" type="number" step="1" min="18" max="100" value="35"></div>
<div class="field"><label for="ret_retirement_age">Planned retirement age</label><input id="ret_retirement_age" type="number" step="1" min="19" max="100" value="67"></div>
<div class="field"><label for="ret_life_age">Life expectancy</label><input id="ret_life_age" type="number" step="1" min="20" max="120" value="90"></div>
<div class="field"><label for="ret_income">Current pre-tax income</label><div class="input-unit"><input id="ret_income" type="number" step="any" min="0" value="75000"><span>$/yr</span></div></div>
<div class="field"><label for="ret_income_growth">Annual income increase</label><div class="input-unit"><input id="ret_income_growth" type="number" step="any" min="-99" value="2"><span>%</span></div></div>
<div class="field"><label for="ret_replacement">Income needed in retirement</label><div class="input-unit"><input id="ret_replacement" type="number" step="any" min="0" value="75"><span>%</span></div></div>
<div class="field"><label for="ret_return">Average investment return</label><div class="input-unit"><input id="ret_return" type="number" step="any" min="-99" value="6"><span>%/yr</span></div></div>
<div class="field"><label for="ret_inflation">Inflation rate</label><div class="input-unit"><input id="ret_inflation" type="number" step="any" min="-99" value="3"><span>%/yr</span></div></div>
<div class="field"><label for="ret_other_income">Social Security, pension, other income</label><div class="input-unit"><input id="ret_other_income" type="number" step="any" min="0" value="2000"><span>$/mo</span></div></div>
<div class="field"><label for="ret_savings">Current retirement savings</label><div class="input-unit"><input id="ret_savings" type="number" step="any" min="0" value="100000"><span>$</span></div></div>
<div class="field field-wide"><label for="ret_save_rate">Future retirement savings</label><div class="input-unit"><input id="ret_save_rate" type="number" step="any" min="0" value="12"><span>% of income</span></div></div>
</div></section>
<section class="retirement-mode-panel is-hidden" data-retirement-panel="save"><div class="fields">
<div class="field"><label for="save_current_age">Current age</label><input id="save_current_age" type="number" step="1" min="18" max="100" value="35"></div>
<div class="field"><label for="save_retirement_age">Planned retirement age</label><input id="save_retirement_age" type="number" step="1" min="19" max="100" value="67"></div>
<div class="field"><label for="save_target">Amount needed at retirement</label><div class="input-unit"><input id="save_target" type="number" step="any" min="0" value="1500000"><span>$</span></div></div>
<div class="field"><label for="save_now">Retirement savings now</label><div class="input-unit"><input id="save_now" type="number" step="any" min="0" value="100000"><span>$</span></div></div>
<div class="field"><label for="save_return">Average investment return</label><div class="input-unit"><input id="save_return" type="number" step="any" min="-99" value="6"><span>%/yr</span></div></div>
<div class="field"><label for="save_monthly_now">Current monthly contribution</label><div class="input-unit"><input id="save_monthly_now" type="number" step="any" min="0" value="750"><span>$/mo</span></div></div>
</div></section>
<section class="retirement-mode-panel is-hidden" data-retirement-panel="withdraw"><div class="fields">
<div class="field"><label for="withdraw_current_age">Current age</label><input id="withdraw_current_age" type="number" step="1" min="18" max="100" value="35"></div>
<div class="field"><label for="withdraw_retirement_age">Planned retirement age</label><input id="withdraw_retirement_age" type="number" step="1" min="19" max="100" value="67"></div>
<div class="field"><label for="withdraw_life_age">Life expectancy</label><input id="withdraw_life_age" type="number" step="1" min="20" max="120" value="90"></div>
<div class="field"><label for="withdraw_savings">Retirement savings today</label><div class="input-unit"><input id="withdraw_savings" type="number" step="any" min="0" value="100000"><span>$</span></div></div>
<div class="field"><label for="withdraw_annual_add">Annual contribution</label><div class="input-unit"><input id="withdraw_annual_add" type="number" step="any" min="0" value="3000"><span>$/yr</span></div></div>
<div class="field"><label for="withdraw_monthly_add">Monthly contribution</label><div class="input-unit"><input id="withdraw_monthly_add" type="number" step="any" min="0" value="750"><span>$/mo</span></div></div>
<div class="field"><label for="withdraw_return">Average investment return</label><div class="input-unit"><input id="withdraw_return" type="number" step="any" min="-99" value="6"><span>%/yr</span></div></div>
<div class="field"><label for="withdraw_inflation">Inflation rate</label><div class="input-unit"><input id="withdraw_inflation" type="number" step="any" min="-99" value="3"><span>%/yr</span></div></div>
</div></section>
<section class="retirement-mode-panel is-hidden" data-retirement-panel="last"><div class="fields">
<div class="field"><label for="last_amount">Amount available</label><div class="input-unit"><input id="last_amount" type="number" step="any" min="0" value="750000"><span>$</span></div></div>
<div class="field"><label for="last_withdrawal">Starting monthly withdrawal</label><div class="input-unit"><input id="last_withdrawal" type="number" step="any" min="0" value="4000"><span>$/mo</span></div></div>
<div class="field"><label for="last_return">Average investment return</label><div class="input-unit"><input id="last_return" type="number" step="any" min="-99" value="5"><span>%/yr</span></div></div>
<div class="field"><label for="last_inflation">Annual withdrawal increase</label><div class="input-unit"><input id="last_inflation" type="number" step="any" min="-99" value="3"><span>%/yr</span></div></div>
</div></section>
</div>"""


def k401_input_html():
    return """<div class="loan-mode-tabs k401-mode-tabs" role="tablist" aria-label="401(k) calculation mode" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<button class="is-active" type="button" role="tab" aria-selected="true" data-k401-mode="projection">401(k) projection</button>
<button type="button" role="tab" aria-selected="false" data-k401-mode="withdrawal">Early withdrawal</button>
<button type="button" role="tab" aria-selected="false" data-k401-mode="match">Employer match</button>
</div><div class="k401-mode-stack">
<section class="k401-mode-panel" data-k401-panel="projection"><div class="fields">
<div class="field"><label for="k401_age">Current age</label><input id="k401_age" type="number" step="1" min="18" max="100" value="35"></div>
<div class="field"><label for="k401_retirement_age">Retirement age</label><input id="k401_retirement_age" type="number" step="1" min="19" max="100" value="67"></div>
<div class="field"><label for="k401_life_age">Life expectancy</label><input id="k401_life_age" type="number" step="1" min="20" max="120" value="90"></div>
<div class="field"><label for="k401_salary">Current annual salary</label><div class="input-unit"><input id="k401_salary" type="number" step="any" min="0" value="75000"><span>$/yr</span></div></div>
<div class="field"><label for="k401_balance">Current 401(k) balance</label><div class="input-unit"><input id="k401_balance" type="number" step="any" min="0" value="50000"><span>$</span></div></div>
<div class="field"><label for="k401_contribution">Employee contribution</label><div class="input-unit"><input id="k401_contribution" type="number" step="any" min="0" value="6"><span>% of pay</span></div></div>
<div class="field"><label for="k401_match">Employer match</label><div class="input-unit"><input id="k401_match" type="number" step="any" min="0" value="50"><span>%</span></div></div>
<div class="field"><label for="k401_match_limit">Employer match limit</label><div class="input-unit"><input id="k401_match_limit" type="number" step="any" min="0" value="6"><span>% of pay</span></div></div>
<div class="field"><label for="k401_salary_growth">Annual salary increase</label><div class="input-unit"><input id="k401_salary_growth" type="number" step="any" min="-99" value="3"><span>%/yr</span></div></div>
<div class="field"><label for="k401_return">Annual investment return</label><div class="input-unit"><input id="k401_return" type="number" step="any" min="-99" value="7"><span>%/yr</span></div></div>
<div class="field"><label for="k401_inflation">Inflation rate</label><div class="input-unit"><input id="k401_inflation" type="number" step="any" min="-99" value="3"><span>%/yr</span></div></div>
<div class="field"><label for="k401_retirement_return">Return during retirement</label><div class="input-unit"><input id="k401_retirement_return" type="number" step="any" min="-99" value="5"><span>%/yr</span></div></div>
</div><p class="field-note">Contribution percentages are projected from salary. The results flag the current 2026 employee deferral limit but do not predict future IRS limit changes.</p></section>
<section class="k401-mode-panel is-hidden" data-k401-panel="withdrawal"><div class="fields">
<div class="field"><label for="k401_withdraw_age">Age at withdrawal</label><input id="k401_withdraw_age" type="number" step="any" min="18" max="120" value="45"></div>
<div class="field"><label for="k401_withdraw_amount">Early withdrawal amount</label><div class="input-unit"><input id="k401_withdraw_amount" type="number" step="any" min="0" value="50000"><span>$</span></div></div>
<div class="field"><label for="k401_federal_tax">Federal income tax rate</label><div class="input-unit"><input id="k401_federal_tax" type="number" step="any" min="0" value="22"><span>%</span></div></div>
<div class="field"><label for="k401_state_tax">State income tax rate</label><div class="input-unit"><input id="k401_state_tax" type="number" step="any" min="0" value="5"><span>%</span></div></div>
<div class="field"><label for="k401_local_tax">Local income tax rate</label><div class="input-unit"><input id="k401_local_tax" type="number" step="any" min="0" value="0"><span>%</span></div></div>
<div class="field"><label for="k401_employed">Still employed by plan sponsor?</label><select id="k401_employed"><option value="yes">Yes</option><option value="no">No</option></select></div>
<div class="field"><label for="k401_left_55">Separated in or after year age 55?</label><select id="k401_left_55"><option value="no">No</option><option value="yes">Yes</option></select></div>
<div class="field"><label for="k401_disability">Qualifying disability?</label><select id="k401_disability"><option value="no">No</option><option value="yes">Yes</option></select></div>
<div class="field field-wide"><label for="k401_other_exception">Another verified penalty exception?</label><select id="k401_other_exception"><option value="no">No</option><option value="yes">Yes</option></select></div>
</div><p class="field-note">This is a gross estimate. Tax withholding is not necessarily your final tax, and exception eligibility depends on IRS rules and plan facts.</p></section>
<section class="k401-mode-panel is-hidden" data-k401-panel="match"><div class="fields">
<div class="field"><label for="k401_match_salary">Current annual salary</label><div class="input-unit"><input id="k401_match_salary" type="number" step="any" min="0" value="75000"><span>$/yr</span></div></div>
<div class="field"><label for="k401_match_age">Age at year end</label><input id="k401_match_age" type="number" step="1" min="18" max="100" value="35"></div>
<div class="field"><label for="k401_match_contribution">Your contribution</label><div class="input-unit"><input id="k401_match_contribution" type="number" step="any" min="0" value="6"><span>% of pay</span></div></div>
<div class="field"><label for="k401_match_rate1">Employer match: first tier</label><div class="input-unit"><input id="k401_match_rate1" type="number" step="any" min="0" value="100"><span>% match</span></div></div>
<div class="field"><label for="k401_match_limit1">First-tier contribution band</label><div class="input-unit"><input id="k401_match_limit1" type="number" step="any" min="0" value="3"><span>% of pay</span></div></div>
<div class="field"><label for="k401_match_rate2">Employer match: second tier</label><div class="input-unit"><input id="k401_match_rate2" type="number" step="any" min="0" value="50"><span>% match</span></div></div>
<div class="field"><label for="k401_match_limit2">Second-tier contribution band</label><div class="input-unit"><input id="k401_match_limit2" type="number" step="any" min="0" value="2"><span>% of pay</span></div></div>
<div class="field"><label for="k401_pay_periods">Pay periods per year</label><select id="k401_pay_periods"><option value="12">12 monthly</option><option value="24">24 semimonthly</option><option value="26" selected>26 biweekly</option><option value="52">52 weekly</option></select></div>
</div><p class="field-note">The match formula assumes the second tier begins after the first contribution band. Confirm your plan formula, true-up policy, and vesting rules.</p></section>
</div>"""


def rmd_input_html():
    return """<div class="fields rmd-fields">
<div class="field"><label for="rmd_birth_year">Account owner's birth year</label><input id="rmd_birth_year" type="number" step="1" min="1906" max="2008" value="1951"></div>
<div class="field"><label for="rmd_year">Distribution year</label><input id="rmd_year" type="number" step="1" min="2022" max="2100" value="2026"></div>
<div class="field field-wide"><label for="rmd_balance">Prior December 31 account balance</label><div class="input-unit"><input id="rmd_balance" type="number" step="any" min="0" value="300000"><span>$</span></div></div>
<div class="field"><label for="rmd_spouse_solo">Is your spouse the sole beneficiary?</label><select id="rmd_spouse_solo"><option value="no" selected>No</option><option value="yes">Yes</option></select></div>
<div class="field"><label for="rmd_spouse_birth_year">Spouse's birth year</label><input id="rmd_spouse_birth_year" type="number" step="1" min="1906" max="2080" value="1965"></div>
<div class="field"><label for="rmd_return">Expected annual account return</label><div class="input-unit"><input id="rmd_return" type="number" step="any" min="-99" value="5"><span>%/yr</span></div></div>
<div class="field"><label for="rmd_projection_years">Projection length</label><div class="input-unit"><input id="rmd_projection_years" type="number" step="1" min="1" max="40" value="20"><span>years</span></div></div>
</div><p class="field-note">The return assumption only affects the future schedule. The selected year's RMD uses the prior December 31 balance you enter. The spouse table applies only when the spouse is the sole beneficiary and is more than 10 years younger.</p>"""


def social_security_input_html():
    return """<div class="loan-mode-tabs social-security-mode-tabs" role="tablist" aria-label="Social Security calculation mode" style="grid-template-columns:repeat(3,minmax(0,1fr))">
<button class="is-active" type="button" role="tab" aria-selected="true" data-ss-mode="planner">Claim age planner</button>
<button type="button" role="tab" aria-selected="false" data-ss-mode="compare">Compare two ages</button>
<button type="button" role="tab" aria-selected="false" data-ss-mode="earnings">2026 earnings test</button>
</div><div class="social-security-mode-stack">
<section class="social-security-mode-panel" data-ss-panel="planner"><div class="fields">
<div class="field"><label for="ss_birth_year">Birth year</label><input id="ss_birth_year" type="number" step="1" min="1930" max="2000" value="1960"></div>
<div class="field"><label for="ss_fra_benefit">Monthly benefit at full retirement age</label><div class="input-unit"><input id="ss_fra_benefit" type="number" step="any" min="0" value="2000"><span>$/mo</span></div></div>
<div class="field"><label for="ss_claim_years">Planned claim age</label><div class="input-unit"><input id="ss_claim_years" type="number" step="1" min="62" max="70" value="67"><span>years</span></div></div>
<div class="field"><label for="ss_claim_months">Additional claim-age months</label><div class="input-unit"><input id="ss_claim_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field"><label for="ss_life_age">Life expectancy</label><input id="ss_life_age" type="number" step="1" min="62" max="120" value="90"></div>
<div class="field"><label for="ss_cola">Annual cost-of-living adjustment</label><div class="input-unit"><input id="ss_cola" type="number" step="any" min="-99" value="2.5"><span>%/yr</span></div></div>
<div class="field field-wide"><label for="ss_return">Annual investment return on received benefits</label><div class="input-unit"><input id="ss_return" type="number" step="any" min="-99" value="4"><span>%/yr</span></div></div>
</div><p class="field-note">Use the monthly full-retirement-age estimate from your Social Security account. This tool adjusts that entered estimate; it does not calculate your earnings-record benefit.</p></section>
<section class="social-security-mode-panel is-hidden" data-ss-panel="compare"><div class="fields">
<div class="field"><label for="ss_compare_age1_years">Option 1 claim age</label><div class="input-unit"><input id="ss_compare_age1_years" type="number" step="1" min="62" max="70" value="62"><span>years</span></div></div>
<div class="field"><label for="ss_compare_age1_months">Option 1 additional months</label><div class="input-unit"><input id="ss_compare_age1_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field"><label for="ss_compare_payment1">Option 1 monthly benefit</label><div class="input-unit"><input id="ss_compare_payment1" type="number" step="any" min="0" value="1400"><span>$/mo</span></div></div>
<div class="field"><label for="ss_compare_age2_years">Option 2 claim age</label><div class="input-unit"><input id="ss_compare_age2_years" type="number" step="1" min="62" max="70" value="67"><span>years</span></div></div>
<div class="field"><label for="ss_compare_age2_months">Option 2 additional months</label><div class="input-unit"><input id="ss_compare_age2_months" type="number" step="1" min="0" max="11" value="0"><span>months</span></div></div>
<div class="field"><label for="ss_compare_payment2">Option 2 monthly benefit</label><div class="input-unit"><input id="ss_compare_payment2" type="number" step="any" min="0" value="2000"><span>$/mo</span></div></div>
<div class="field"><label for="ss_compare_life">Life expectancy</label><input id="ss_compare_life" type="number" step="1" min="62" max="120" value="90"></div>
<div class="field"><label for="ss_compare_cola">Annual cost-of-living adjustment</label><div class="input-unit"><input id="ss_compare_cola" type="number" step="any" min="-99" value="2.5"><span>%/yr</span></div></div>
<div class="field field-wide"><label for="ss_compare_return">Annual investment return</label><div class="input-unit"><input id="ss_compare_return" type="number" step="any" min="-99" value="4"><span>%/yr</span></div></div>
</div><p class="field-note">Enter the claim-age payment estimates shown in your official SSA record. The comparison compounds any benefits received before the later option begins.</p></section>
<section class="social-security-mode-panel is-hidden" data-ss-panel="earnings"><div class="fields">
<div class="field"><label for="ss_earnings_status">2026 age status</label><select id="ss_earnings_status"><option value="under">Under full retirement age all year</option><option value="reaches">Reach full retirement age in 2026</option><option value="fra">At or above full retirement age</option></select></div>
<div class="field"><label for="ss_earnings_income">Countable work earnings</label><div class="input-unit"><input id="ss_earnings_income" type="number" step="any" min="0" value="40000"><span>$</span></div></div>
<div class="field"><label for="ss_earnings_benefit">Monthly retirement benefit</label><div class="input-unit"><input id="ss_earnings_benefit" type="number" step="any" min="0" value="2000"><span>$/mo</span></div></div>
<div class="field"><label for="ss_earnings_months">Benefit months in 2026</label><input id="ss_earnings_months" type="number" step="1" min="1" max="12" value="12"></div>
</div><p class="field-note">For the year you reach full retirement age, enter only countable earnings before the FRA month. The special monthly rule and later benefit recomputation are not modeled.</p></section>
</div>"""


def loan_input_html():
    return f"""<div class="loan-mode-tabs" role="tablist" aria-label="Loan model"><button class="is-active" type="button" role="tab" aria-selected="true" data-loan-mode="monthlyfixed">Amortized</button><button type="button" role="tab" aria-selected="false" data-loan-mode="intheend">Deferred</button><button type="button" role="tab" aria-selected="false" data-loan-mode="fixedend">Bond</button></div><div class="loan-mode-stack">
<section class="loan-mode-input is-active" id="monthlyfixed"><h3>Amortized Loan</h3><p>Fixed payments paid periodically until the loan is paid off.</p><div class="fields loan-fields">
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
<div class="hero-copy"><h1>Free Online Calculators</h1><p>Calculate mortgage payments, loans, compound interest, BMI, auto costs, and unit conversions with clear formulas, examples, and no signup.</p></div>
<div class="search-panel wide-search" aria-label="Calculator search"><label for="siteSearch">Search calculators</label><div class="search-wrap"><input id="siteSearch" class="search" placeholder="Search calculators..." aria-label="Search calculators"><div id="searchResults" class="search-results"></div></div></div>
</div></section>
<section class="home-block"><div class="wrap"><h2>Calculator Categories</h2><div class="category-filter"><input id="categoryFilter" type="search" placeholder="Filter categories..." aria-label="Filter categories"></div><div class="home-category-grid">{category_cards}</div></div></section>
<section class="home-block browse-all"><div class="wrap browse-panel"><div><h2>Browse All Calculators</h2><p>Start with a main category, then choose the calculator that matches your task from its grouped directory.</p></div><a class="btn primary" href="/conversion-calculators/">Browse all calculators</a></div></section>
<section class="home-block"><div class="wrap scientific-panel"><div><h2>Scientific Calculator</h2><p>Use quick math functions directly from the homepage.</p></div><div class="scientific-widget"><input id="sciExpression" value="" placeholder="0" aria-label="Scientific expression"><button class="btn primary sci-run" id="sciRun" type="button">Calculate</button><div id="sciResult" class="mini-result">Ready</div><div class="sci-keypad">{sci_buttons}</div></div></div></section>
<section class="home-block popular-block"><div class="wrap"><h2>Most Popular Calculators</h2><div class="popular-list">{popular_links}</div></div></section>
<section class="home-block faq-section"><div class="wrap"><h2>Common Questions</h2><div class="faq-list">{faq_list}</div></div></section>
<section class="ad-band"><div class="wrap"><div class="ad-slot">Advertisement</div></div></section>
</main><script src="/assets/search.js?v={ASSET_VERSION}"></script><script src="/assets/scientific.js?v={ASSET_VERSION}"></script><script src="/assets/home.js?v={ASSET_VERSION}"></script>"""
    return page(site, "Free Online Calculators | Mortgage, Loan & Unit Converters", "Free US-focused calculators for mortgage, loan, auto loan, compound interest, BMI, and unit conversions with instant answers, charts, and formulas.", "/", body, ["free online calculators", "mortgage calculator", "loan calculator", "auto loan calculator", "compound interest calculator", "unit converter"], [website_schema(site), organization_schema(site)])


def category_page(site, cat, items, indexable=True):
    title = f"Free {cat} Calculators | NS Calculators"
    desc = f"Free {cat.lower()} calculators for US users with instant answers, formulas, examples, and related tools."
    groups = defaultdict(list)
    for item in items:
        groups[calculator_group(item)].append(item)
    configured_groups = GROUP_LABELS.get(cat) or []
    group_names = {group.casefold(): group for group in groups}
    ordered_groups = [group_names.pop(label.casefold()) for label in configured_groups if label.casefold() in group_names]
    ordered_groups.extend(sorted(group_names.values()))
    jump_links = "".join(
        f"""<a href="#{h(group_slug(group))}">{h(display_group(group))}</a>"""
        for group in ordered_groups
        if groups.get(group)
    )
    sections = "".join(
        f"""<section class="category-section" id="{h(group_slug(group))}"><div class="category-section-head"><h2>{h(display_group(group))}</h2><span class="category-count">{len(groups[group]):,} tools</span></div><div class="calculator-link-grid">{''.join(f'<a href="/{h(calc["slug"])}/" aria-label="{h(calc["title"])}">{h(re.sub(r" Calculator$", "", calc["title"]))}</a>' for calc in sorted(groups[group], key=lambda c: c["title"]))}</div></section>"""
        for group in ordered_groups
        if groups.get(group)
    )
    body = f"""<main class="main category-main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / {h(cat)} Calculators</div>
<section class="article wide category-directory"><div class="page-title-icon">{category_icon(cat, "title-icon")}<h1>{h(cat)} Calculators</h1></div><p class="lead">{h(category_desc(cat))}</p><nav class="category-jump-nav" aria-label="{h(cat)} calculator groups">{jump_links}</nav><div class="category-tools">{sections}</div></section></div></main>"""
    keywords = [f"{cat.lower()} calculators", f"free {cat.lower()} calculators", "online calculator", "calculator tools"]
    crumbs = [("Home", "/"), (f"{cat} Calculators", f"/{slugify_cat(cat)}/")]
    return page(site, title, desc, f"/{slugify_cat(cat)}/", body, keywords, [breadcrumb_schema(site, crumbs)], "CollectionPage", indexable=indexable)


def subgroup_desc(cat, group, items):
    sample = ", ".join(item["title"].replace(" Calculator", "") for item in items[:3])
    return f"{len(items):,} {cat.lower()} tools including {sample}."


def priority_length_copy(calc):
    if calc.get("slug") not in PRIORITY_LENGTH_CONVERSIONS:
        return None
    source, target, factor = conversion_parts(calc)
    source_symbol = LENGTH_UNIT_SYMBOLS[source]
    target_symbol = LENGTH_UNIT_SYMBOLS[target]
    reverse_factor = 1 / factor
    reverse_slug = f"{unit_slug(target)}-to-{unit_slug(source)}-calculator"
    rows = "".join(
        f"<tr><td>{value:g} {h(source_symbol)}</td><td>{value * factor:.10g} {h(target_symbol)}</td><td>{value * factor * LENGTH_UNIT_METERS[target]:.10g} m</td></tr>"
        for value in (1, 3, 5, 10, 25, 50, 100)
    )
    return f"""
<h2>How to convert {h(source)} to {h(target)}</h2><p>Multiply the number of {h(source)} by {factor:.12g}. The calculator keeps the full conversion factor during the calculation, then formats the displayed answer for readability. Use the direction menu to reverse the conversion without opening another page.</p>
<p class="formula">{h(target)} = {h(source)} x {factor:.12g}</p>
<h2>Worked conversion example</h2><p>For 10 {h(source_symbol)}, multiply 10 by {factor:.12g}. The result is {10 * factor:.10g} {h(target_symbol)}. In reverse, divide a {h(target)} value by {factor:.12g}, or multiply it by {reverse_factor:.12g}.</p>
<h2>Common {h(source)} to {h(target)} conversions</h2><div class="table-scroll"><table class="data-table"><thead><tr><th>{h(source.title())}</th><th>{h(target.title())}</th><th>Meters</th></tr></thead><tbody>{rows}</tbody></table></div>
<h2>Exact length standards</h2><p>These units share defined relationships: one inch is exactly 0.0254 meter, one international foot is exactly 0.3048 meter, one centimeter is exactly 0.01 meter, and one millimeter is exactly 0.001 meter. The <a href="https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors" rel="external noopener">NIST Guide to SI conversion factors</a> documents the inch, foot, and meter relationships used here. Because the factors are defined, rounding comes from the displayed decimal precision rather than an uncertain measurement factor.</p>
<h2>When this conversion is useful</h2><p>{h(source.title())} and {h(target)} commonly appear in product dimensions, construction plans, room measurements, manufacturing specifications, science work, and international forms. Convert every linear dimension before comparing values. For area or volume, do not apply a linear factor only once; square or cube the factor, or use a dedicated area or volume calculator.</p>
<h2>Reverse {h(target)} to {h(source)}</h2><p>The reverse factor is {reverse_factor:.12g}. You can select the reverse direction above or use the dedicated <a href="/{h(reverse_slug)}/">{h(target)} to {h(source)} calculator</a>. Both directions use the same underlying definitions, so equivalent entries produce reciprocal results apart from display rounding.</p>
<h2>Precision and rounding</h2><p>Keep extra decimal places during intermediate work and round only the final answer. A building estimate may need fewer decimals than machining or laboratory work. The calculator also reports meters, centimeters, millimeters, decimal feet, and inches so you can check the result against a familiar unit.</p>
<h2>Frequently asked questions</h2><h3>Is the conversion factor exact?</h3><p>Yes. The result is derived from defined metric prefixes and the exact international inch and foot definitions.</p><h3>Can I enter negative or decimal values?</h3><p>Yes. Decimal and negative values are accepted, which is useful for coordinates, offsets, and differences. Physical lengths are normally nonnegative.</p><h3>Why can the last decimal differ from another calculator?</h3><p>Calculators may display different numbers of decimal places. Compare the unrounded factor and the precision requested by your source measurement.</p>"""


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
    try:
        numeric_factor = float(factor)
        common_rows = "".join(
            f"<tr><td>{value:g} {h(source)}</td><td>{value * numeric_factor:.8g} {h(target)}</td></tr>"
            for value in (1, 5, 10, 25, 100)
        )
        common_values = f"""<h2>Common {h(source)} to {h(target)} conversions</h2><div class="table-scroll"><table class="data-table"><thead><tr><th>{h(source)}</th><th>{h(target)}</th></tr></thead><tbody>{common_rows}</tbody></table></div>"""
    except (TypeError, ValueError):
        common_values = ""
    return f"""
<h2>What this calculator does</h2><p>This tool converts a value entered in {h(source)} into {h(target)}. It is useful for quick checks, comparison tables, shopping, building estimates, recipes, science homework, and everyday unit changes.</p>
<h2>How to use it</h2><p>Enter the number of {h(source)} you want to convert. The calculator multiplies that value by the stored conversion factor and returns the answer in {h(target)}.</p>
<h2>Formula</h2><p class="formula">{h(calc['formula'])}</p>
<h2>Worked example</h2><p>{h(calc['example'])} For example, entering 10 gives 10 × {h(factor)}, expressed in {h(target)}.</p>
{common_values}
<h2>When to verify</h2><p>For scientific reporting, regulated work, medical dosing, engineering, construction, or commercial transactions, confirm rounding rules and source units with an authoritative reference.</p>
<h2>Frequently asked questions</h2><h3>Can I enter decimals?</h3><p>Yes. Decimal values are supported, which helps with small measurements and precise conversions.</p><h3>Why is the result rounded?</h3><p>The result is rounded for readability in the browser. Use the formula if you need more precision for a specialist workflow.</p>"""


def high_value_calculator_copy(calc):
    if calc.get("slug") == "debt-payoff-calculator":
        return """
<h2>Debt payoff calculator for multiple balances</h2><p>Enter each current balance, annual percentage rate, and required minimum payment, then add any amount you can pay above those minimums. The calculator keeps the starting monthly debt budget fixed and rolls freed minimum payments toward the next priority balance. It calculates both the debt avalanche and debt snowball methods from the same inputs so the interest cost and payoff date are directly comparable.</p>
<h2>Debt avalanche versus debt snowball</h2><p>The avalanche method directs extra money to the open debt with the highest APR after every required minimum is paid. This usually reduces interest because the most expensive balance is attacked first. The snowball method targets the smallest open balance, which can produce an earlier first payoff and a visible sense of progress. The Consumer Financial Protection Bureau describes both the <a href="https://www.consumerfinance.gov/archive/blog/how-reduce-your-debt/" rel="external noopener">highest-interest-rate and snowball strategies</a> and recommends choosing a method you can put into action consistently.</p>
<p class="formula">monthly interest = opening balance x APR / 12</p><p class="formula">fixed monthly debt budget = entered minimum payments + extra monthly payment</p>
<h2>How the monthly simulation works</h2><p>At the start of each modeled month, every unpaid balance receives one month of interest using its entered fixed APR. The plan then makes the entered minimum payment on each open debt. Any money left in the fixed budget goes to the strategy's priority debt. When that debt reaches zero, unused money in the same month moves to the next priority debt. In later months, its former minimum payment remains inside the fixed budget, creating the rollover effect.</p>
<h2>Worked debt payoff example</h2><p>The default example includes a $6,800 credit card at 22.99% APR with a $170 minimum, a $4,000 personal loan at 12% with a $130 minimum, and a $14,250 auto loan at 6.49% with a $285 minimum. Adding $100 creates a fixed $685 monthly budget. The comparison shows whether paying the small personal-loan balance first provides a quick win or whether attacking the high-rate card first saves more interest.</p>
<h2>What counts as an extra payment?</h2><p>Enter only the amount you expect to pay every month in addition to all listed minimums. A tax refund, bonus, or other one-time payment is not the same as a recurring extra payment and is not modeled by this version. Do not commit money needed for rent, utilities, food, insurance, taxes, or a basic emergency reserve. Confirm with each creditor how additional payments are applied and whether a loan has a prepayment penalty.</p>
<h2>Why actual results may differ</h2><p>This is a fixed-rate planning model. Credit-card APRs, minimum-payment formulas, fees, promotional periods, daily interest, statement dates, new charges, payment timing, and creditor allocation rules can change actual payoff results. The calculator assumes no new borrowing and one payment cycle per month. It also assumes every payment arrives on time and that the listed minimums remain part of the same total monthly budget after a debt is paid off.</p>
<h2>How to use the payoff comparison</h2><p>First, verify balances and APRs from current statements rather than memory. Next, enter minimum payments that are at least enough to satisfy the creditor's current requirement. Compare the two strategy rows for total interest and the debt-free month, then inspect the payoff order for the selected detailed plan. A mathematically cheaper plan is useful only if the monthly budget is realistic enough to maintain.</p>
<h2>When to seek additional help</h2><p>If required minimums are already unaffordable, a projection does not solve the cash-flow problem. Contact creditors promptly and consider a reputable nonprofit credit counselor. Be cautious with companies that promise to erase debt, demand large upfront fees, or tell you to stop communicating with creditors. This calculator is educational and is not financial, legal, tax, or credit counseling advice.</p>
<h2>Frequently asked questions</h2><h3>Which method saves the most interest?</h3><p>With the same fixed budget and no special rate changes, directing extra money to the highest APR generally minimizes interest. The results quantify the difference for the exact balances entered.</p><h3>Why can the two methods have the same payoff month?</h3><p>A fixed total budget can make the overall duration similar even when the order and interest differ. Rounding and the final partial payment also affect the displayed month.</p><h3>What if a minimum payment is too small?</h3><p>The calculator flags plans that fail to reach zero within 100 years. A payment that does not cover accruing interest can allow a balance to grow until it becomes the priority debt.</p><h3>Should a mortgage be included?</h3><p>This tool can model a fixed-rate balance, but mortgage escrow, amortization rules, tax considerations, and much longer terms make a dedicated <a href="/mortgage-payoff-calculator/">mortgage payoff calculator</a> more appropriate.</p>"""
    if calc.get("slug") == "ratio-calculator":
        return """
<h2>Ratio calculator for four common problems</h2><p>Use this calculator to simplify a two- or three-part ratio, solve one missing value in a proportion, multiply every term by the same scale factor, or divide a total into proportional shares. Enter whole numbers, decimals, or simple fractions such as 3/4. The result panel shows the answer first and then the arithmetic used to check it.</p>
<h2>How to simplify a ratio</h2><p>A ratio stays equivalent when every term is divided by the same nonzero factor. For whole-number terms, the calculator finds their greatest common divisor and divides every term by it. Decimal and fraction inputs are first written with a common denominator, then reduced to the smallest whole-number terms.</p>
<p class="formula">simplified ratio = each whole-number term / greatest common divisor</p>
<h2>Simplifying ratio example</h2><p>For 12:18, the greatest common divisor is 6. Dividing both terms by 6 gives 2:3. The relationship has not changed: 12/18 and 2/3 are both approximately 0.6667. For 1.5:2.5, clearing the decimal places gives 15:25, which reduces to 3:5.</p>
<h2>How to solve a proportion</h2><p>A proportion states that two ratios are equal: a/b = c/d. Leave exactly one of the four boxes empty. The calculator uses equal cross products, a x d = b x c, and isolates the missing term. For example, 2:3 = 14:x gives x = 3 x 14 / 2 = 21.</p>
<p class="formula">a / b = c / d, so a x d = b x c</p>
<h2>How to split a total by ratio</h2><p>Add the ratio terms to find the total number of parts. Divide the total by that sum to find one part, then multiply by each ratio term. Splitting 100 in a 3:2 ratio gives five total parts. One part is 20, so the shares are 60 and 40. The displayed shares are calculated from the unrounded values so they add back to the entered total apart from display rounding.</p>
<p class="formula">share = total x ratio term / sum of all ratio terms</p>
<h2>Scaling an equivalent ratio</h2><p>Multiply every term by the same positive scale factor. A 2:3:5 ratio scaled by 4 becomes 8:12:20. Scaling changes the quantities but preserves their relative relationship. Multiplying only one term creates a different ratio.</p>
<h2>Part-to-part and part-to-whole percentages</h2><p>In a ratio A:B, A divided by B is the unit comparison, while A divided by A+B is A's share of the combined whole. For 2:3, A/B is 66.67%, but A represents 40% of the total five parts. The calculator labels these separately because they answer different questions.</p>
<h2>Use matching units</h2><p>Ratio terms should describe comparable quantities. Convert measurements to the same unit before simplifying. A ratio of 1 foot to 6 inches is not 1:6; after converting 1 foot to 12 inches, the ratio is 12:6, or 2:1. OpenStax's <a href="https://openstax.org/books/prealgebra-2e/pages/5-6-ratios-and-rate" rel="external noopener">ratios and rates guide</a> likewise explains that measurements should use the same unit before their ratio is simplified.</p>
<h2>Equivalent ratios and cross products</h2><p>Equivalent ratios represent the same quotient. You can multiply or divide every term by one common factor to generate another equivalent form. For a proportion, equality can be checked by comparing the cross products. OpenStax defines a <a href="https://openstax.org/books/prealgebra-2e/pages/6-5-solve-proportions-and-their-applications" rel="external noopener">proportion</a> as an equation between two ratios and shows why their cross products are equal.</p>
<h2>Input and rounding limits</h2><p>The calculator accepts positive integers, decimals with up to six decimal places, and simple fractions. Very large values or highly precise repeating decimals may need separate exact arithmetic. Results are rounded for display, but calculations use the parsed numeric values before formatting.</p>
<h2>Frequently asked questions</h2><h3>What is the simplest form of a ratio?</h3><p>For whole-number terms, it is the equivalent ratio whose terms have no common divisor greater than 1.</p><h3>Can a ratio have three parts?</h3><p>Yes. Simplify, scale, and split modes accept an optional third term and apply the same common factor to all terms.</p><h3>Is 2:3 the same as 3:2?</h3><p>No. Order carries meaning. Reversing the terms reverses which quantity is being compared with the other.</p><h3>Why must one proportion box be blank?</h3><p>The other three values define the missing fourth value. More than one blank leaves too little information, while no blank leaves nothing to solve.</p>"""
    if calc.get("slug") == "car-depreciation-calculator":
        return """
<h2>How car depreciation is calculated</h2><p>This calculator applies an entered percentage to the vehicle value remaining at the start of each year. That is declining-balance depreciation: the dollar loss usually becomes smaller as the modeled value falls. Choose one constant rate for every year or separate the first year from later years.</p>
<p class="formula">ending value = opening value x (1 - annual depreciation rate)</p>
<h2>Constant rate versus two-stage depreciation</h2><p>The constant-rate method is useful when you start from a vehicle's current market value and want a simple forward projection. The two-stage method can model a new vehicle with a larger first-year loss and a different rate afterward. Both are planning assumptions, not model-specific market forecasts.</p>
<h2>Car depreciation example</h2><p>A $35,000 starting value depreciating 15% annually for five years falls to $15,529.69. The modeled loss is $19,470.31, or 55.6% of the starting value. At 12,000 miles per year, that equals about $0.32 of depreciation per mile across 60,000 projected miles.</p>
<h2>Value floor and mileage result</h2><p>The optional floor prevents the projection from dropping below an entered residual amount. The per-mile figure divides total modeled depreciation by projected miles; mileage does not independently change the value in this calculator. Use it to compare ownership horizons under the same assumptions.</p>
<h2>Market depreciation is not tax depreciation</h2><p>This page estimates a possible change in market value. It does not calculate a business deduction, MACRS, Section 179, bonus depreciation, basis, recapture, or passenger-automobile tax limits. The <a href="https://www.irs.gov/publications/p946" rel="external noopener">IRS Publication 946</a> covers federal tax depreciation rules for qualifying property.</p>
<h2>Verify the starting value and rate</h2><p>Actual resale value depends on make, model, trim, age, mileage, condition, accident history, options, location, season, supply, and demand. <a href="https://www.edmunds.com/appraisal/" rel="external noopener">Edmunds vehicle appraisal guidance</a> explains that market valuation considers many of these factors. Use a current vehicle-specific appraisal before making a sale, insurance, lending, or purchase decision.</p>
<h2>Related vehicle-value tools</h2><p>Use the <a href="/car-resale-value-calculator/">car resale value calculator</a> when you need expected sale proceeds after selling costs and a future loan payoff. For a current estimate based on a local comparable, use the <a href="/used-car-value-calculator/">used car value calculator</a>. For dealer trade equity, use the <a href="/car-trade-in-value-calculator/">trade-in value calculator</a>.</p>
<h2>Frequently asked questions</h2><h3>Does a 15% rate subtract 15% of the original value each year?</h3><p>No. This model applies 15% to the remaining value each year, so the annual dollar loss declines over time.</p><h3>Does mileage change the projected value?</h3><p>No. Mileage is used only to show depreciation per mile. Adjust the entered rate or starting value when you expect mileage to affect market value.</p><h3>Can a car appreciate?</h3><p>This calculator models depreciation rates from 0% to 100%. Collectible or unusually scarce vehicles can behave differently and require market data.</p>"""
    if calc.get("slug") == "car-resale-value-calculator":
        return """
<h2>How to estimate future car resale value</h2><p>Start with a current private-party value supported by comparable vehicles or a recognized valuation service. Enter how long you plan to keep the car and an annual depreciation assumption. The calculator projects market value, estimated selling costs, loan payoff at sale, and net proceeds.</p>
<p class="formula">projected resale value = current value x (1 - annual depreciation rate)^years</p>
<p class="formula">estimated net proceeds = resale value - selling costs - future loan payoff</p>
<h2>Car resale example</h2><p>A car worth $28,000 today, depreciating 14% annually for three years, has a projected resale value of $17,809.57. With 2% selling costs and an $8,000 payoff at sale, estimated net proceeds are $9,453.38.</p>
<h2>Slower and faster depreciation scenarios</h2><p>The scenario range changes only the annual depreciation rate. With a 14% entered rate and a 3-point range, the table compares 11%, 14%, and 17%. It holds the starting value, holding period, payoff, selling-cost percentage, and mileage constant so you can see how sensitive the result is to the rate assumption.</p>
<h2>Current value is the critical input</h2><p>Use a local value for the same year, make, model, trim, drivetrain, mileage, and condition. <a href="https://www.consumerreports.org/cars/car-value-estimator/" rel="external noopener">Consumer Reports vehicle-value guidance</a> notes that condition, high mileage, damage, and reconditioning needs affect value. <a href="https://www.edmunds.com/appraisal/" rel="external noopener">Edmunds appraisal guidance</a> also describes local market and vehicle-specific factors. This calculator does not have live VIN, auction, or listing data.</p>
<h2>Loan payoff and selling costs</h2><p>Enter the expected lender payoff at the future sale date, not today's payoff and not the sum of scheduled payments. Selling costs are modeled as a percentage of projected value and can represent listing, inspection, detailing, transaction, or consignment costs. Set the percentage to zero when those costs do not apply.</p>
<h2>Resale value versus depreciation</h2><p>This page focuses on future cash proceeds. Use the <a href="/car-depreciation-calculator/">car depreciation calculator</a> to compare constant and two-stage value loss with a residual floor and cost per mile. Use the <a href="/used-car-value-calculator/">used car value calculator</a> for current retail, private-party, and trade-in ranges from local comparable data.</p>
<h2>Frequently asked questions</h2><h3>Is the projected resale value guaranteed?</h3><p>No. It is a scenario based on your current value and entered rate. Obtain current appraisals when you are ready to sell.</p><h3>What if net proceeds are negative?</h3><p>A negative result means the modeled payoff and selling costs exceed the projected sale value. That indicates possible negative equity under the assumptions.</p><h3>Does annual mileage reduce the resale value automatically?</h3><p>No. It reports projected total mileage and depreciation per mile. Reflect an expected mileage penalty in the current value or annual depreciation assumption.</p>"""
    if calc.get("slug") == "horsepower-calculator":
        return """
<h2>Calculate horsepower, torque, or RPM</h2><p>Select the value you want to find, then enter the other two values measured at the same operating point. The calculator solves the rotational power relationship in either direction and reports mechanical horsepower, kilowatts, metric horsepower, pound-feet, newton-meters, and revolutions per minute.</p>
<p class="formula">horsepower = torque (lb-ft) x RPM / 5252.113</p>
<p class="formula">torque (lb-ft) = horsepower x 5252.113 / RPM</p>
<p class="formula">RPM = horsepower x 5252.113 / torque (lb-ft)</p>
<h2>Horsepower calculation example</h2><p>An engine producing 300 lb-ft at 4,000 RPM makes about 228.48 mechanical horsepower. That is approximately 170.38 kW or 231.65 metric horsepower (PS). The same entered torque equals about 406.75 N-m. These values describe one point on the engine's torque curve, not necessarily its peak output.</p>
<h2>Why the formula uses 5252</h2><p>One mechanical horsepower is 33,000 foot-pounds of work per minute. A rotating shaft travels 2 pi radians per revolution, so dividing 33,000 by 2 pi produces approximately 5252.113. At about 5,252 RPM, horsepower and torque in lb-ft have the same numerical value. The relationship still applies above and below that speed; only the numerical comparison changes.</p>
<h2>Mechanical hp, kW, and metric PS</h2><p>This calculator treats hp as mechanical horsepower, the unit commonly used for US vehicle specifications. One mechanical horsepower is approximately 745.7 watts. Metric horsepower, often written PS, is slightly smaller at approximately 735.5 watts. The <a href="https://www.nist.gov/pml/special-publication-811" rel="external noopener">NIST Guide to the SI</a> provides unit definitions and conversion references, while the watt is the SI unit of power.</p>
<h2>Crank horsepower versus wheel horsepower</h2><p>The formula does not estimate drivetrain loss. Use torque measured at the crankshaft to calculate crank horsepower, or wheel torque from a chassis dynamometer to calculate wheel horsepower. Do not mix crank torque with wheel RPM or compare results from different test conditions as if they were the same measurement.</p>
<h2>Rated power and dynamometer results</h2><p>Vehicle power claims depend on the test method, correction conditions, installed accessories, and reporting standard. <a href="https://saemobilus.sae.org/standards/j1349_202511-engine-power-test-code-spark-ignition-compression-ignition-installed-net-power-torque-rating" rel="external noopener">SAE J1349</a> describes a repeatable method for installed net engine power and torque ratings. This browser calculator performs the mathematical conversion only; it does not certify an engine or correct a dyno run for atmospheric conditions.</p>
<h2>Use values from the same RPM</h2><p>Torque and horsepower vary across the operating range. To verify a dyno point, pair the torque reading with the RPM shown at that exact point. Peak torque and peak horsepower usually occur at different RPM, so combining two separate peak specifications produces a result that does not represent a real operating point.</p>
<h2>Related performance calculators</h2><p>After calculating power, use the <a href="/power-to-weight-ratio-calculator/">power-to-weight ratio calculator</a> to account for vehicle mass. The <a href="/tire-size-calculator/">tire size calculator</a> compares diameter and speedometer effects, while the <a href="/towing-capacity-calculator/">towing capacity calculator</a> checks vehicle and trailer limits.</p>
<h2>Frequently asked questions</h2><h3>Why do horsepower and torque cross at 5,252 RPM?</h3><p>When RPM equals the 5252.113 conversion constant, multiplying torque by RPM and dividing by that same number leaves the torque value unchanged.</p><h3>Can I use newton-meters?</h3><p>Yes. Select N-m and the calculator converts the entered torque to lb-ft before solving, then reports both units.</p><h3>Is horsepower constant at every RPM?</h3><p>No. Horsepower changes with both torque and shaft speed. A single calculation represents one operating point.</p>"""
    if calc.get("slug") == "power-to-weight-ratio-calculator":
        return """
<h2>How to calculate power-to-weight ratio</h2><p>Enter engine or motor power and the weight it must move. Choose the units independently, and optionally add a driver, passengers, cargo, fuel, or equipment. The calculator converts everything to mechanical horsepower and pounds, then reports the equivalent ratio in common US and metric formats.</p>
<p class="formula">power-to-weight ratio = power / loaded weight</p>
<p class="formula">weight per horsepower = loaded weight / power</p>
<h2>Power-to-weight example</h2><p>A 300 hp vehicle weighing 3,600 lb has 0.08333 hp/lb, or 12.00 lb/hp. The same ratio is about 166.67 hp per US short ton, 183.72 hp per metric tonne, and 137.00 W/kg. Adding a 180 lb driver changes the loaded weight to 3,780 lb and lowers the ratio to about 0.07937 hp/lb.</p>
<h2>Which weight should you enter?</h2><p>Use the weight that matches the comparison. Curb weight typically includes standard equipment and operating fluids but not occupants or cargo. For a real acceleration or hill-climbing comparison, add the driver and any expected load. Do not compare one vehicle's dry weight with another vehicle's loaded weight.</p>
<h2>Crank power versus wheel power</h2><p>Use the same basis for every vehicle in a comparison. Manufacturer specifications generally report engine or crank power, while a chassis dynamometer reports power delivered at the wheels. Wheel power is normally lower because the drivetrain consumes some power. This calculator does not estimate or add drivetrain loss.</p>
<h2>Understanding hp/lb and lb/hp</h2><p>Higher hp/lb means more power is available for each pound. Lower lb/hp means each horsepower moves less weight. They express the same relationship in opposite directions. A value of 0.10 hp/lb is equivalent to 10 lb/hp and 200 hp per US short ton.</p>
<h2>Metric power-to-mass units</h2><p>Watts per kilogram and kilowatts per metric tonne are numerically identical because one kilowatt is 1,000 watts and one metric tonne is 1,000 kilograms. The calculator uses mechanical horsepower, watts, pounds, and kilograms as defined conversion units. See the <a href="https://www.nist.gov/pml/special-publication-811" rel="external noopener">NIST Guide to the SI</a> for SI usage and conversion references.</p>
<h2>What the ratio can and cannot predict</h2><p>Power-to-weight ratio is useful for broad comparisons, but it does not directly predict a zero-to-60 time, quarter-mile result, towing performance, or top speed. Traction, gearing, torque curve, aerodynamics, tires, launch control, road grade, temperature, and drivetrain efficiency also matter. Treat the result as one performance input rather than a complete vehicle model.</p>
<h2>Target-ratio calculation</h2><p>The optional target shows how much power the entered loaded weight would need to reach a chosen hp/lb ratio. It also reports the difference from current power. This isolates the power change while holding weight constant; reducing weight can reach the same target by a different path.</p>
<h2>Related performance calculators</h2><p>Use the <a href="/horsepower-calculator/">horsepower calculator</a> to derive power from torque and RPM before comparing ratios. The <a href="/tire-size-calculator/">tire size calculator</a> compares diameter and speedometer effects, and the <a href="/towing-capacity-calculator/">towing capacity calculator</a> checks vehicle and trailer limits rather than performance ratio.</p>
<h2>Frequently asked questions</h2><h3>Should a driver be included?</h3><p>Include the driver when comparing real operating performance. Leave the optional load at zero when comparing published curb-weight specifications.</p><h3>Is W/kg the same as kW per tonne?</h3><p>Yes, the numerical values are the same because both numerator and denominator differ by a factor of 1,000.</p><h3>Does a higher ratio guarantee faster acceleration?</h3><p>No. It generally indicates more power relative to mass, but traction, gearing, aerodynamics, and power delivery can change actual performance.</p>"""
    if calc.get("slug") == "bottleneck-calculator":
        return """
<h2>PC bottleneck calculator based on measured evidence</h2><p>A PC bottleneck is the component or limit that determines performance in one specific workload, scene, resolution, settings preset, and frame-rate target. It is not a permanent property of a CPU and GPU pair. This calculator therefore avoids a universal bottleneck percentage and instead evaluates measurements from the game or application you actually use.</p>
<h2>How to use measured mode</h2><p>Run the workload long enough to capture a representative average, then enter average FPS, the target FPS, average GPU utilization, utilization of the busiest CPU thread, and CPU and GPU frame times. Use an uncapped run when possible. The result weighs frame-time evidence most heavily, uses utilization as supporting evidence, and identifies when the system is already close to its target.</p>
<p class="formula">target frame-time budget (ms) = 1000 / target FPS</p>
<p class="formula">approximate FPS ceiling = 1000 / the slower CPU or GPU frame time</p>
<h2>Measured example</h2><p>At 110 average FPS with a 144 FPS target, 78% GPU utilization, 96% utilization on the busiest CPU thread, 9.1 ms CPU frame time, and 7.0 ms GPU frame time, the CPU side takes longer to prepare a frame. The calculator reports likely CPU-bound behavior for that measured scene. It does not claim the CPU is always the limit in every game or graphics setting.</p>
<h2>How to confirm a CPU bottleneck</h2><p>Lower the resolution or graphics settings while keeping the same scene and test path. If FPS changes very little and GPU utilization remains below full load while one or more CPU threads are heavily used, the workload is probably CPU-limited. Background software, thermal throttling, memory configuration, simulation load, and an FPS cap can produce similar symptoms, so check those before buying hardware.</p>
<h2>How to confirm a GPU bottleneck</h2><p>Reduce resolution, ray tracing, anti-aliasing, or another GPU-heavy setting. A substantial FPS increase with GPU utilization near full load and GPU frame time above CPU frame time indicates a likely GPU limit. A GPU bottleneck is not automatically a fault; it often means the graphics card is being fully used to deliver the selected image quality.</p>
<h2>Planning mode uses benchmark ceilings</h2><p>For a future build, enter a CPU-limited FPS result measured with a sufficiently fast GPU and a GPU-limited FPS result measured at the intended resolution and settings. Use the same game version, test scene, quality preset, upscaling mode, and frame-generation setting. The lower ceiling is the likely limit, and the uncertainty input creates a range around that estimate. Mixing unrelated benchmark suites makes the comparison unreliable.</p>
<h2>Why total CPU utilization can mislead</h2><p>A game can saturate one important thread while total CPU utilization appears moderate across many cores. Use the busiest relevant thread or per-core view instead of total package utilization. Intel's guide to <a href="https://www.intel.com/content/www/us/en/gaming/resources/what-is-bottlenecking-my-pc.html" rel="external noopener">identifying PC bottlenecks</a> also emphasizes that the limiting component depends on how the computer is being used and that multiple components can contribute.</p>
<h2>Frame time is more useful than a generic score</h2><p>Frame time describes how long each side of the rendering pipeline needs for a frame. The side with the longer recurring frame time usually sets the throughput ceiling. Intel's <a href="https://cdrdv2-public.intel.com/785322/gpa_user-guide_2023.3-767266-785322.pdf" rel="external noopener">Graphics Performance Analyzers guide</a> uses frame analysis to isolate CPU- or GPU-bound behavior. NVIDIA's <a href="https://download.nvidia.com/developer/GPU_Gems/Sample_Chapters/Graphics_Pipeline_Performance.pdf" rel="external noopener">graphics pipeline performance guidance</a> similarly recommends changing rendering workload to locate the limiting pipeline stage.</p>
<h2>Limits of this calculator</h2><p>The tool does not contain a hardware model database, predict exact game FPS from component names, or convert synthetic CPU and GPU scores into a universal loss percentage. It cannot detect shader compilation stutter, storage stalls, insufficient RAM or VRAM, driver problems, thermal or power limits, network latency, game-engine caps, or poor frame pacing. Validate an upgrade decision with repeatable benchmarks from the exact software you care about.</p>
<h2>Related PC calculators</h2><p>Use the <a href="/gpu-calculator/">GPU calculator</a> for theoretical compute, memory bandwidth, and efficiency. The <a href="/power-supply-calculator/">power supply calculator</a> estimates component load and headroom, while the <a href="/ai-compute-calculator/">AI compute calculator</a> models training throughput rather than gaming performance.</p>
<h2>Frequently asked questions</h2><h3>Is a bottleneck percentage accurate?</h3><p>No single percentage applies to every game, scene, resolution, and setting. This page reports the likely limiting side from the evidence entered and shows the underlying values.</p><h3>What GPU utilization indicates a GPU bottleneck?</h3><p>Utilization near full load is supporting evidence, especially when GPU frame time is longer than CPU frame time. Utilization alone is not conclusive because caps, telemetry sampling, and engine behavior can affect it.</p><h3>Does changing resolution change the bottleneck?</h3><p>Often. Higher resolution usually increases GPU work, while lower resolution can expose a CPU frame-delivery limit. The result can still vary by game and scene.</p><h3>Should I upgrade the component named by the result?</h3><p>Not automatically. First repeat the test, check temperatures and clock speeds, remove caps, close background tasks, and compare the measured shortfall with the performance target.</p>"""
    if calc.get("slug") == "rmd-calculator":
        return """
<h2>2026 required minimum distribution calculator</h2><p>Use this calculator for an owner of a traditional IRA, SEP IRA, SIMPLE IRA, or an employer retirement account that is subject to required minimum distributions. Enter the account owner's birth year, the distribution year, and the account's value on December 31 of the previous year. The result identifies the IRS table and distribution period used, calculates the annual RMD, and builds a future schedule.</p>
<p class="formula">required minimum distribution = prior December 31 balance / applicable IRS distribution period</p>
<h2>Which IRS life-expectancy table applies?</h2><p>Most account owners use the Uniform Lifetime Table, Table III in <a href="https://www.irs.gov/publications/p590b" rel="external noopener">IRS Publication 590-B</a>. Use the Joint and Last Survivor Table, Table II, only when the owner's spouse is the sole beneficiary for the entire distribution year and is more than 10 years younger than the owner. The calculator checks both conditions from the entries before selecting Table II.</p>
<h2>Worked RMD example</h2><p>An owner who is age 75 in 2026 and has a $300,000 prior-year-end balance uses the Uniform Lifetime distribution period of 24.6. Dividing $300,000 by 24.6 produces a 2026 RMD of $12,195.12. The projected schedule assumes each RMD is withdrawn at year end, after applying the entered annual return to the opening balance.</p>
<h2>When RMDs begin</h2><p>Under current federal rules, the applicable starting age is generally 73 for people born from 1951 through 1959 and 75 for people born in 1960 or later. The <a href="https://www.irs.gov/retirement-plans/retirement-plan-and-ira-required-minimum-distributions-faqs" rel="external noopener">IRS RMD frequently asked questions</a> explain that the first distribution can generally be delayed until April 1 of the following year. Delaying it does not move the second RMD, which is still due by December 31 of that same following year, so two taxable distributions may occur in one calendar year.</p>
<h2>Accounts and exceptions</h2><p>Roth IRA owners do not take lifetime RMDs from their own Roth IRAs. Beginning in 2024, designated Roth accounts in employer plans are also excluded from lifetime RMD requirements while the participant is alive. Some current employees can delay RMDs from their present employer's plan, but the exception generally does not apply to a person who owns more than 5% of the employer. It also does not postpone RMDs from traditional IRAs or former-employer plans.</p>
<h2>Projection assumptions</h2><p>The first row uses the balance entered. Each later row applies the fixed annual return, subtracts the modeled year-end RMD, and carries the remaining amount into the next year. Actual balances, investment returns, beneficiary status, rollovers, and tax rules can change. The schedule is a planning scenario, not a prediction.</p>
<h2>Important limitations</h2><p>This tool is for an account owner calculating a lifetime RMD. It does not calculate inherited IRA beneficiary distributions, the 10-year rule, annuity contract rules, qualified charitable distribution adjustments, multiple-account aggregation, or corrective excise taxes. Employer plans can have plan-specific rules. Confirm the final amount with the account custodian or a qualified tax professional; the account owner remains responsible for taking the correct amount.</p>
<h2>Frequently asked questions</h2><h3>What balance should I enter?</h3><p>Enter the fair market value of the applicable retirement account as of December 31 immediately before the distribution year, after any adjustments your custodian or tax adviser says are required.</p><h3>Can I withdraw more than the RMD?</h3><p>Yes, but an amount above the RMD generally cannot be applied to a future year's RMD. A distribution may be taxable and may affect other tax calculations.</p><h3>Can I combine IRA RMDs?</h3><p>You generally calculate an RMD separately for each traditional IRA, then may take the combined IRA amount from one or more of those IRAs. Different aggregation rules apply to employer plans, and 403(b) accounts have separate rules.</p><h3>Does the projected return change this year's RMD?</h3><p>No. This year's RMD is based on the prior December 31 balance entered. The return assumption is used only to estimate later balances and distributions.</p>"""
    if calc.get("slug") == "finance-calculator":
        return """
<h2>Five-key finance calculator</h2><p>This calculator solves the five core time-value-of-money variables used by common financial calculators: number of periods (N), annual interest rate (I/Y), present value (PV), periodic payment (PMT), and future value (FV). Select the value to calculate, enter the other four, and choose the payment and compounding settings.</p>
<h2>Cash-flow sign convention</h2><p>Money moving in opposite directions must use opposite signs. If you receive $20,000 today, enter PV as positive. If you then pay $2,000 each period, enter PMT as negative. The calculated FV uses the opposite sign of the ending account or loan balance. A sign error is the most common reason a finance calculator cannot find a meaningful result.</p>
<h2>Time value of money formula</h2><p>The calculator converts the nominal annual rate to an effective rate for each payment period, then solves the standard annuity equation. For end-of-period payments, type is 0. For beginning-of-period payments, type is 1.</p>
<p class="formula">PV(1 + r)^N + PMT(1 + r x type)((1 + r)^N - 1) / r + FV = 0</p>
<h2>Payment frequency and compounding frequency</h2><p>P/Y is the number of payments per year and C/Y is the number of times interest compounds per year. When they differ, the periodic rate is converted so each payment period receives the equivalent compounded return. For a typical monthly loan, use 12 for both P/Y and C/Y.</p>
<h2>Beginning versus end payments</h2><p>Ordinary annuities make payments at the end of each period. Annuities due make payments at the beginning, giving every payment one additional period of growth or one period less of loan interest. Rent and lease payments are often due at the beginning; many loan payments are modeled at the end.</p>
<h2>Worked example</h2><p>With N = 10, I/Y = 6%, PV = $20,000, PMT = -$2,000, one payment and one compounding period per year, the calculated FV is about -$9,455.36. The sign means the ending value is opposite the original inflow under the selected cash-flow convention.</p>
<h2>APR, APY, and assumptions</h2><p>This tool treats I/Y as a nominal annual interest rate and converts it using the selected C/Y and P/Y values. It does not add lender fees or independently calculate a disclosed APR. The <a href="https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that APR can include the interest rate plus certain loan charges. For savings growth, the <a href="https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator" rel="external noopener">SEC Investor.gov compound interest calculator</a> illustrates how principal, contributions, time, rate, and compounding affect future value.</p>
<h2>Frequently asked questions</h2><h3>What do PV and FV mean?</h3><p>PV is the value at the start of the calculation. FV is the value after N payment periods, expressed using the opposite-side cash-flow sign convention.</p><h3>Why can there be no interest-rate solution?</h3><p>The entered cash flows may never balance at a real rate, or they may permit more than one mathematical rate. This calculator reports the first practical real solution it finds and asks you to review signs when no solution is found.</p><h3>Can N include a partial period?</h3><p>Yes. The equation can return a decimal number of periods, but the schedule displays complete periods plus a final partial-period estimate.</p>"""
    if calc.get("slug") == "salary-calculator":
        return """
<h2>Salary calculator and pay converter</h2><p>Enter an amount paid by the hour, day, week, two weeks, half month, month, quarter, or year. The calculator converts it to the other common pay periods using your work schedule. Results are gross pay before taxes, payroll deductions, bonuses, commissions, and overtime.</p>
<h2>Hourly to annual salary</h2><p>Multiply the hourly rate by hours worked each week and by 52 weeks. At $50 per hour and 40 hours per week, the unadjusted annual equivalent is $104,000.</p><p class="formula">annual salary = hourly rate x hours per week x 52</p>
<h2>Annual salary to hourly pay</h2><p>Divide annual salary by 52 and then by weekly hours. A $62,400 annual salary at 40 hours per week is equivalent to $30 per hour before accounting for unpaid time off.</p><p class="formula">hourly equivalent = annual salary / (52 x hours per week)</p>
<h2>Biweekly versus semimonthly pay</h2><p>Biweekly means every two weeks, normally 26 pay periods per year. Semimonthly means twice per month, normally 24 pay periods per year. The <a href="https://webapps.dol.gov/elaws/whd/flsa/otcalc/glossaryall.asp" rel="external noopener">US Department of Labor pay glossary</a> describes semimonthly pay as two periods per month. A biweekly paycheck is therefore usually smaller than a semimonthly paycheck for the same annual salary.</p>
<h2>Unadjusted and adjusted results</h2><p>The unadjusted column assumes 52 full working weeks. The adjusted column subtracts the entered holidays and vacation days from scheduled workdays and treats them as unpaid. If your salary, holidays, or vacation days are paid, use the unadjusted amount for gross-pay comparisons.</p>
<p>The <a href="https://www.dol.gov/general/topic/workhours/vacation_leave" rel="external noopener">US Department of Labor vacation guidance</a> explains that federal law generally does not require payment for time not worked, such as vacations or holidays; paid leave is usually determined by the employment agreement and applicable law.</p>
<h2>Pay-period conversion factors</h2><p>This calculator uses 52 weekly periods, 26 biweekly periods, 24 semimonthly periods, 12 monthly periods, and 4 quarterly periods per year. Daily pay uses the entered days per week. Hourly pay uses both hours and days entered.</p>
<h2>Gross pay versus take-home pay</h2><p>This page converts gross salary frequencies only. It does not estimate taxes or deductions. Use the <a href="/take-home-pay-calculator/">take-home pay calculator</a> for a separate US federal, FICA, state, and payroll-deduction estimate, or the <a href="/salary-increase-calculator/">salary increase calculator</a> to evaluate a raise.</p>
<h2>Frequently asked questions</h2><h3>How many biweekly pay periods are in a year?</h3><p>The standard conversion uses 26 because 52 weeks divided by two equals 26. Some calendar years or employer schedules can produce a 27th paycheck.</p><h3>Is semimonthly the same as biweekly?</h3><p>No. Semimonthly usually means 24 paychecks per year; biweekly usually means 26.</p><h3>Does this calculator include overtime?</h3><p>No. Overtime eligibility and the regular rate can depend on job classification and compensation details. This tool converts straight-time gross pay only.</p>"""
    if calc.get("slug") == "bmi-calculator":
        return """
<h2>Adult BMI calculator</h2><p>Use US customary units or metric units to calculate body mass index for adults age 20 and older. The result includes the adult BMI category, the weight range corresponding to BMI 18.5 through 24.9 at the entered height, BMI Prime, and the Ponderal Index.</p>
<h2>Adult BMI categories</h2><p>The <a href="https://www.cdc.gov/bmi/adult-calculator/bmi-categories.html" rel="external noopener">CDC adult BMI categories</a> classify BMI below 18.5 as underweight, 18.5 to less than 25 as healthy weight, 25 to less than 30 as overweight, and 30 or greater as obesity. Obesity is further described as Class 1 from 30 to less than 35, Class 2 from 35 to less than 40, and Class 3 at 40 or greater.</p>
<h2>BMI formulas</h2><p>With metric units, divide weight in kilograms by height in meters squared. With US customary units, divide weight in pounds by height in inches squared and multiply by 703. The CDC lists both formulas in its <a href="https://www.cdc.gov/bmi/faq/" rel="external noopener">BMI frequently asked questions</a>.</p>
<p class="formula">BMI = weight (kg) / height (m)^2</p><p class="formula">BMI = 703 x weight (lb) / height (in)^2</p>
<h2>Worked example</h2><p>An adult who is 5 feet 10 inches tall and weighs 160 pounds has a BMI of about 23.0. That value is within the CDC healthy-weight screening category for adults. At 70 inches tall, BMI 18.5 through 24.9 corresponds to approximately 129 to 174 pounds.</p>
<h2>BMI Prime and Ponderal Index</h2><p>BMI Prime divides BMI by 25, the upper boundary of the CDC healthy-weight category. A BMI Prime of 0.92 corresponds to a BMI of 23. The Ponderal Index divides weight in kilograms by height in meters cubed; it is another height-and-weight ratio, not a diagnosis.</p>
<h2>BMI limitations</h2><p>BMI is a screening measure, not a direct measurement of body fat and not a diagnosis. The <a href="https://www.cdc.gov/bmi/adult-calculator/index.html" rel="external noopener">CDC adult BMI calculator guidance</a> says BMI should be considered with medical history, health behaviors, physical findings, and laboratory findings. Muscle mass, body composition, pregnancy, and other factors can affect interpretation. Discuss health concerns with a qualified healthcare professional.</p>
<h2>Children and teens</h2><p>Do not interpret this adult result for anyone younger than 20. CDC guidance uses sex- and age-specific BMI percentiles for children and teens ages 2 through 19.</p>
<h2>Frequently asked questions</h2><h3>What is a healthy adult BMI?</h3><p>The CDC healthy-weight screening category for adults is BMI 18.5 to less than 25. Individual health cannot be determined from BMI alone.</p><h3>Does sex change the adult BMI formula?</h3><p>No. CDC adult BMI categories apply regardless of age, sex, or race for adults age 20 and older, although those factors may affect how BMI relates to body composition and health.</p><h3>Is this medical advice?</h3><p>No. This calculator provides a mathematical screening result and cannot diagnose a condition or recommend treatment.</p>"""
    if calc.get("slug") == "standard-deviation-calculator":
        return """
<h2>Standard deviation calculator</h2><p>Enter a list of numbers and choose whether the data is an entire population or a sample drawn from a larger population. The calculator reports the selected standard deviation and variance, plus both population and sample values so you can compare the denominators.</p>
<h2>Population standard deviation</h2><p>Use the population formula when the values include every member of the group you want to describe. First find the mean, subtract the mean from each value, square those deviations, add them, and divide by the population size <em>n</em>. Standard deviation is the square root of that variance.</p>
<p class="formula">population variance = sum of (x - mean)^2 / n</p><p class="formula">population standard deviation = square root of population variance</p>
<h2>Sample standard deviation</h2><p>Use the sample formula when the entered observations are used to estimate variability in a larger population. The corrected sample variance divides by <em>n - 1</em>, often called Bessel's correction. The <a href="https://www.itl.nist.gov/div898/strd/univ/certmethdef/lew.html" rel="external noopener">NIST Statistical Reference Datasets</a> define sample standard deviation using this denominator.</p>
<p class="formula">sample variance = sum of (x - sample mean)^2 / (n - 1)</p><p class="formula">sample standard deviation = square root of sample variance</p>
<h2>Worked example</h2><p>For 1, 3, 4, 7, and 8, the mean is 4.6 and the sum of squared deviations is 33.2. Dividing by 5 gives a population variance of 6.64 and population standard deviation of about 2.5768. Dividing by 4 gives a sample variance of 8.3 and sample standard deviation of about 2.8810.</p>
<h2>Variance, standard error, and margin of error</h2><p>Variance is measured in squared units, while standard deviation returns to the original data units. NIST's <a href="https://www.itl.nist.gov/div898/handbook/eda/section3/eda356.htm" rel="external noopener">Engineering Statistics Handbook</a> describes standard deviation as the square root of variance and notes that squaring gives more weight to values farther from the mean.</p>
<p>Standard error estimates the spread of sample means and is calculated as the sample standard deviation divided by the square root of <em>n</em>. The displayed margin of error multiplies that standard error by the selected normal critical value. It is a normal approximation, not a substitute for a t interval or a study-specific sampling design.</p>
<h2>How to interpret standard deviation</h2><p>A smaller standard deviation means values are generally closer to the mean; a larger standard deviation means they are more dispersed. The number is not automatically good or bad. Its meaning depends on the measurement scale, context, distribution, and how the data were collected.</p>
<h2>Frequently asked questions</h2><h3>Should I choose sample or population?</h3><p>Choose population when the list contains the complete group of interest. Choose sample when the observations represent only part of a larger group.</p><h3>Why does sample standard deviation use n - 1?</h3><p>Estimating the mean from the same sample uses one degree of freedom. Dividing by n - 1 corrects the sample variance as an estimator of population variance.</p><h3>Can I enter negative numbers and decimals?</h3><p>Yes. Separate integers, negative values, or decimals with commas, spaces, semicolons, or line breaks.</p>"""
    if calc.get("slug") == "fraction-calculator":
        return """
<h2>Fraction calculator with mixed numbers</h2><p>Use the arithmetic mode to add, subtract, multiply, or divide proper fractions, improper fractions, whole numbers, and mixed numbers. Enter a negative sign on the whole-number field to make the entire mixed number negative. If the whole number is zero, put the negative sign on the numerator.</p>
<h2>Adding and subtracting fractions</h2><p>Fractions need a common denominator before their numerators can be combined. This calculator shows the least common denominator and the equivalent fractions used in the operation, then reduces the answer to lowest terms.</p>
<p class="formula">a/b + c/d = (a x d + c x b) / (b x d)</p>
<p class="formula">a/b - c/d = (a x d - c x b) / (b x d)</p>
<h2>Multiplying and dividing fractions</h2><p>To multiply fractions, multiply the numerators and denominators. To divide, multiply the first fraction by the reciprocal of the second. Division is undefined when the second fraction equals zero.</p>
<p class="formula">a/b x c/d = (a x c) / (b x d)</p>
<p class="formula">a/b divide c/d = (a x d) / (b x c)</p>
<h2>Mixed numbers and improper fractions</h2><p>A mixed number combines a whole number and a proper fraction. Before calculating, the tool converts each mixed number to an improper fraction. For example, 1 1/2 becomes 3/2 because 1 x 2 + 1 = 3.</p>
<h2>Simplify a fraction</h2><p>Select Simplify a fraction to divide the numerator and denominator by their greatest common divisor. For example, the greatest common divisor of 42 and 56 is 14, so 42/56 reduces to 3/4.</p>
<h2>Convert a decimal to a fraction</h2><p>Select Convert a decimal to a fraction to express a terminating decimal as an exact fraction based on the entered decimal places. For example, 0.375 becomes 375/1000 and reduces to 3/8.</p>
<h2>Decimal and percentage equivalents</h2><p>Every valid result includes a decimal and percentage equivalent. The decimal is the numerator divided by the denominator; the percentage is that decimal multiplied by 100.</p>
<h2>Frequently asked questions</h2><h3>Can the denominator be zero?</h3><p>No. A fraction with a denominator of zero is undefined, so the calculator displays an error instead of a numerical result.</p><h3>How do I enter a whole number?</h3><p>Enter the number in the Whole field and use 0 as the numerator. You can also enter the whole number as a numerator over 1.</p><h3>Does the calculator reduce answers automatically?</h3><p>Yes. It divides the numerator and denominator by their greatest common divisor and keeps the denominator positive.</p>"""
    if calc.get("slug") == "sales-tax-calculator":
        return """
<h2>Sales tax calculator</h2><p>Choose Add tax to calculate sales tax and the checkout total from a before-tax price. Choose Reverse tax when you know the tax-inclusive total and rate. Choose Find the sales tax rate when both the before-tax and after-tax prices are known.</p>
<p class="formula">sales tax = taxable amount x sales tax rate / 100</p>
<p class="formula">after-tax total = before-tax total + sales tax</p>
<h2>Add sales tax example</h2><p>A $100 taxable purchase at an 8.25% combined rate produces $8.25 of sales tax and a $108.25 total. If a discount applies, this calculator reduces the merchandise price before calculating tax.</p>
<h2>Reverse sales tax</h2><p>To remove sales tax from a tax-inclusive total, divide the total by one plus the rate as a decimal. For example, $108.25 divided by 1.0825 gives a $100 before-tax price and $8.25 tax.</p>
<p class="formula">before-tax price = tax-inclusive total / (1 + tax rate / 100)</p>
<h2>Find the sales tax rate</h2><p>Subtract the before-tax price from the after-tax price to find the tax amount, then divide by the before-tax price. A price that rises from $100 to $108.25 has an 8.25% implied sales tax rate.</p>
<p class="formula">tax rate = (after-tax price - before-tax price) / before-tax price x 100</p>
<h2>Discounts, quantity, and shipping</h2><p>In Add tax mode, the discount is applied to each item's price before multiplying by quantity. Shipping is added separately. Turn on Tax shipping only when shipping or handling is taxable for the actual transaction. For a broader promotion comparison, use the <a href="/discount-calculator/">discount calculator</a>.</p>
<h2>Use the correct combined rate</h2><p>Sales tax rules and rates can differ by state, county, city, product, and transaction. <a href="https://www.usa.gov/state-taxes" rel="external noopener">USAGov</a> notes that states and municipalities can charge different percentages on different goods or no tax on some items. Use the combined rate from the relevant state or local tax authority rather than a statewide rate alone.</p>
<p>The <a href="https://www.irs.gov/credits-deductions/individuals/use-the-sales-tax-deduction-calculator" rel="external noopener">IRS sales-tax deduction guidance</a> also explains that local tax bases and rates can vary within a state. This calculator estimates transaction tax; it does not determine whether an item, buyer, seller, or shipping charge is taxable.</p>
<h2>Total purchase cost</h2><p>The <a href="https://consumer.ftc.gov/articles/online-shopping" rel="external noopener">FTC online-shopping guide</a> recommends comparing the total cost, including shipping, handling, taxes, and other fees. Review the seller's checkout total before paying.</p>
<h2>Frequently asked questions</h2><h3>How do I add 7% sales tax?</h3><p>Multiply the taxable price by 0.07, then add that tax to the original price. A $50 purchase has $3.50 tax and a $53.50 total.</p><h3>How do I remove tax from a total?</h3><p>Divide the tax-inclusive total by one plus the rate as a decimal. Do not simply subtract the rate from the total.</p><h3>Does sales tax apply before or after a discount?</h3><p>This calculator applies tax after the entered discount. Actual treatment can vary with the jurisdiction and promotion.</p>"""
    if calc.get("slug") == "percent-calculator":
        return """
<h2>Percentage calculator for six common problems</h2><p>Select the wording that matches your question. The calculator can find a percentage of a number, express one value as a percentage of another, recover the whole from a known part and percentage, calculate percent change, calculate percentage difference, or increase and decrease a number by a percentage.</p>
<h2>What is X% of Y?</h2><p>Convert the percentage to a decimal and multiply it by the value. For example, 20% of 150 is 0.20 x 150 = 30.</p><p class="formula">part = percentage / 100 x whole</p>
<h2>X is what percent of Y?</h2><p>Divide the part by the whole and multiply by 100. For example, 30 is 20% of 150.</p><p class="formula">percentage = part / whole x 100</p>
<h2>X is Y% of what?</h2><p>Divide the known part by the percentage written as a decimal. If 30 is 20% of a number, the whole is 30 / 0.20 = 150.</p><p class="formula">whole = part / (percentage / 100)</p>
<h2>Percent change</h2><p>Percent change compares a new value with its original value. A positive result is an increase and a negative result is a decrease. Moving from 100 to 125 is a 25% increase.</p><p class="formula">percent change = (new - original) / |original| x 100</p>
<h2>Percentage difference</h2><p>Percentage difference compares two values without treating either one as the original baseline. It divides the absolute difference by the average magnitude. The values 80 and 120 have a 40% percentage difference.</p><p class="formula">percentage difference = |value 1 - value 2| / ((|value 1| + |value 2|) / 2) x 100</p>
<h2>Percentage points are different</h2><p>If a rate rises from 20% to 25%, it increases by 5 percentage points but by 25% relative to its original level. Use percentage points when subtracting two percentages directly; use percent change when comparing the relative movement.</p>
<h2>Frequently asked questions</h2><h3>How do I calculate a 15% increase?</h3><p>Multiply the starting value by 1.15. A 15% increase on 200 gives 230.</p><h3>How do I calculate a 15% decrease?</h3><p>Multiply the starting value by 0.85. A 15% decrease on 200 gives 170.</p><h3>Why can percent change be undefined?</h3><p>The formula divides by the original value, so a change from zero has no finite percentage. Use the absolute change instead.</p>"""
    if calc.get("slug") == "take-home-pay-calculator":
        return """
<h2>2026 US take-home pay estimate</h2><p>This calculator starts with annual gross wages, applies the selected 2026 federal filing-status brackets and deduction, estimates employee Social Security and Medicare taxes, then subtracts the state or local rate and payroll deductions you enter. Results include annual, monthly, and selected-paycheck take-home pay.</p>
<p class="formula">take-home pay = gross wages - pre-tax deductions - federal income tax - Social Security - Medicare - state or local tax - post-tax deductions - extra withholding</p>
<h2>Federal income tax calculation</h2><p>Federal taxable income is gross wages minus the entered pre-tax amounts and either the 2026 standard deduction or your custom deduction. The calculator applies progressive tax brackets, meaning each rate applies only to the income inside that bracket. It does not multiply all income by your highest marginal rate.</p>
<p>For 2026, the standard deduction is $16,100 for single filers, $32,200 for married couples filing jointly, and $24,150 for heads of household. See the <a href="https://www.irs.gov/newsroom/irs-releases-tax-inflation-adjustments-for-tax-year-2026-including-amendments-from-the-one-big-beautiful-bill" rel="external noopener">IRS 2026 inflation adjustments</a> and <a href="https://www.irs.gov/irb/2025-45_IRB" rel="external noopener">Revenue Procedure 2025-32</a>.</p>
<h2>Social Security and Medicare in 2026</h2><p>The employee Social Security rate is 6.2% on covered wages up to the 2026 wage base of $184,500. Medicare is 1.45% on covered wages with no ordinary wage cap. The calculator also estimates the 0.9% Additional Medicare Tax above the filing-status threshold. These parameters come from <a href="https://www.irs.gov/publications/p15" rel="external noopener">IRS Publication 15 (2026)</a> and the <a href="https://www.ssa.gov/oact/COLA/cbb.html" rel="external noopener">Social Security Administration contribution and benefit base</a>.</p>
<h2>How payroll deductions are treated</h2><p>The pre-tax retirement field reduces the federal income-tax estimate but not Social Security or Medicare wages, which is the common treatment for elective 401(k) deferrals. The other pre-tax benefits field is assumed to reduce both federal taxable income and FICA wages. Actual treatment depends on the plan and deduction type. Post-tax deductions reduce take-home pay but not taxable wages.</p>
<h2>Worked example</h2><p>Using the default $75,000 salary, single filing status, $4,500 retirement contribution, $2,400 other pre-tax benefits, 5% state or local rate, and $600 post-tax deductions, the model estimates about $52,389 in annual take-home pay, or about $2,015 across 26 biweekly paychecks.</p>
<h2>Estimate versus an actual paycheck</h2><p>This is an annual planning estimate, not payroll software or tax advice. It does not model W-4 dependents and credits, multiple jobs, bonus withholding, local tax rules, unemployment or disability insurance, HSA limits, age-based deductions, itemized-deduction limits, refundable credits, no-tax-on-tips or overtime deductions, or employer-specific benefit timing. Compare the result with your pay stub and use the <a href="https://www.irs.gov/individuals/tax-withholding-estimator" rel="external noopener">IRS Tax Withholding Estimator</a> when you need W-4 guidance.</p>
<h2>Frequently asked questions</h2><h3>Is take-home pay the same as net pay?</h3><p>They generally refer to the amount left after taxes and payroll deductions. A pay stub may use net pay for the exact employer calculation.</p><h3>Does a 401(k) contribution reduce Social Security tax?</h3><p>Traditional elective 401(k) deferrals generally reduce federal taxable income but remain subject to Social Security and Medicare taxes, which is how this calculator treats the retirement field.</p><h3>Why can my paycheck differ?</h3><p>Payroll withholding uses W-4 elections, payroll-period tables, benefit timing, rounding, and state rules. This tool annualizes those items for comparison.</p>"""
    if calc.get("slug") == "salary-increase-calculator":
        return """
<h2>How to calculate a salary increase</h2><p>Enter your current gross annual salary and a raise as either a percentage or a fixed annual dollar amount. The calculator converts the raise into both formats and then shows the new annual salary across common pay periods.</p>
<p class="formula">raise dollars = current salary x raise percentage / 100</p>
<p class="formula">new annual salary = current salary + raise dollars</p>
<h2>Salary raise example</h2><p>A 5% raise on $60,000 adds $3,000 and produces a new annual salary of $63,000. That equals $5,250 per month, about $2,423.08 across 26 biweekly pay periods, $1,211.54 per week, or $30.29 per hour when divided by 40 hours for 52 weeks.</p>
<h2>Percentage raise versus dollar raise</h2><p>A percentage makes offers at different salaries easier to compare. A dollar amount shows the direct annual change. Switching the input type does not change the underlying math: the calculator always reports both the annual dollar increase and its percentage of current salary.</p>
<h2>Inflation-adjusted raise</h2><p>The real raise estimates how much purchasing power changes after the inflation rate you enter. It uses the ratio of the new pay level to the changed price level, so simply subtracting inflation from the raise is only an approximation.</p>
<p class="formula">real raise = ((1 + nominal raise rate) / (1 + inflation rate) - 1) x 100</p>
<p>The <a href="https://www.bls.gov/cpi/" rel="external noopener">US Bureau of Labor Statistics</a> describes CPI as a measure of average price change over time, and its <a href="https://www.bls.gov/cpi/factsheets/purchasing-power-constant-dollars.htm" rel="external noopener">purchasing-power guide</a> explains how price indexes can compare the value of money across periods. Your personal cost changes can differ from the national average.</p>
<h2>Gross pay and take-home pay</h2><p>Every pay-period result is gross pay before federal, state, and local taxes, benefits, retirement contributions, overtime, bonuses, unpaid time, or payroll rounding. Use the <a href="/take-home-pay-calculator/">take-home pay calculator</a> for a separate net-pay estimate.</p>
<h2>Frequently asked questions</h2><h3>How do I calculate a 3% raise?</h3><p>Multiply current salary by 0.03, then add the result to current salary. On $50,000, the increase is $1,500 and the new salary is $51,500.</p><h3>Is biweekly pay the same as twice monthly?</h3><p>No. Biweekly normally means 26 pay periods per year, while semimonthly means 24. Select the schedule your employer uses.</p><h3>Does the hourly result include overtime?</h3><p>No. It is an annual-salary equivalent based only on the hours and working weeks entered.</p>"""
    if calc.get("slug") == "discount-calculator":
        return """
<h2>How to calculate a discount</h2><p>Enter the original unit price and the first discount. Add a second discount when a promotion applies another percentage to the already-discounted price. Quantity, estimated sales tax, shipping, and other fees then produce an estimated checkout total.</p>
<p class="formula">discounted unit price = original price x (1 - first discount) x (1 - second discount)</p>
<p class="formula">checkout total = discounted unit price x quantity + estimated tax + fees</p>
<h2>Discount example with sales tax</h2><p>Twenty percent off a $100 item saves $20 and leaves an $80 sale price. With 8.25% sales tax and no other fees, the estimated checkout total is $86.60.</p>
<h2>How stacked discounts work</h2><p>Successive discounts are multiplied, not added. A 20% discount followed by another 10% discount leaves 80% x 90% = 72% of the original price, so the effective discount is 28%, not 30%.</p>
<h2>Quantity, tax, and fees</h2><p>Savings and merchandise subtotal are multiplied by quantity. Estimated tax is applied to the discounted merchandise subtotal, then the entered shipping or fees are added. Actual taxability, rates, shipping treatment, exemptions, and marketplace fees depend on the location and transaction. Use the dedicated <a href="/sales-tax-calculator/">sales tax calculator</a> to add tax, reverse tax from a total, or infer a rate. The <a href="https://www.irs.gov/credits-deductions/individuals/use-the-sales-tax-deduction-calculator" rel="external noopener">IRS sales-tax calculator guidance</a> notes that local rates can vary within a state, so use the rate shown for the actual purchase.</p>
<h2>Compare the full offer</h2><p>Check model, size, shipping, return policy, and conditions attached to a low advertised price. The <a href="https://consumer.ftc.gov/articles/online-shopping" rel="external noopener">FTC online-shopping guide</a> recommends comparing item details and shipping fees, not only the headline price.</p>
<h2>Frequently asked questions</h2><h3>How much is 25% off $80?</h3><p>The savings are $20 and the discounted price is $60 before tax and fees.</p><h3>Do I add two discounts together?</h3><p>No. Apply the second percentage to the price remaining after the first discount.</p><h3>Is sales tax charged before or after a discount?</h3><p>This calculator applies the entered rate after discounts. Actual taxable amounts can differ by jurisdiction and promotion type.</p>"""
    if calc.get("slug") == "payment-calculator":
        return """
<h2>Monthly payment or payoff term</h2><p>This payment calculator answers either side of a common fixed-rate loan decision. Fixed Term calculates the monthly payment needed to repay a balance within a chosen number of years and months. Fixed Payments calculates how long repayment takes when the monthly amount is already known.</p>
<h2>Fixed-term payment formula</h2><p>For a fully amortizing loan, each payment covers that month's interest and reduces principal. P is the starting principal, r is the monthly interest rate, and n is the number of monthly payments.</p>
<p class="formula">monthly payment = P x r x (1 + r)^n / ((1 + r)^n - 1)</p>
<p>At a zero interest rate, the payment is simply principal divided by the number of months. A $200,000 loan at 6% for 15 years produces a monthly payment of about $1,687.71 before fees, taxes, or insurance.</p>
<h2>Fixed monthly payment formula</h2><p>When payment is known, the calculator rearranges the amortization equation to solve for the number of months. The monthly payment must be greater than the first month's interest. Otherwise the balance cannot decline under the entered assumptions.</p>
<p class="formula">months = -ln(1 - principal x monthly rate / payment) / ln(1 + monthly rate)</p>
<h2>How the amortization schedule works</h2><p>Interest is calculated from the balance at the beginning of each month. The rest of the payment reduces principal. Because the balance generally falls over time, the interest portion declines while the principal portion rises. The final payment can be smaller than the regular payment so the schedule does not overpay the balance.</p>
<h2>Interest rate versus APR</h2><p>This calculator applies the entered percentage as a fixed nominal annual rate divided by 12. It does not independently add origination fees, points, closing costs, insurance, or other charges. The <a href="https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that APR is a broader borrowing-cost measure that can include the interest rate and certain fees. Use the disclosed APR when comparing offers if you want those eligible costs reflected in the rate.</p>
<h2>Choosing a term or payment</h2><p>A longer term usually lowers the required monthly payment but raises total interest. A larger fixed payment shortens the payoff period and normally lowers interest. Compare both modes using the same principal and rate. For mortgages with taxes and insurance, use the <a href="/mortgage-calculator/">mortgage calculator</a>; for multiple compounding and payment frequencies, use the <a href="/loan-calculator/">loan calculator</a>.</p>
<h2>Important assumptions</h2><p>The calculation assumes a fixed rate, one payment each month, no missed or late payments, and no fees or prepayment penalties. Actual lenders can use daily interest, different rounding, payment dates, variable rates, or other contractual rules. Review the promissory note and lender disclosures before making a borrowing decision.</p>
<h2>Frequently asked questions</h2><h3>Why is my fixed payment too low?</h3><p>If the payment does not exceed monthly interest, it cannot reduce principal. Increase the payment, lower the balance, or use a lower rate.</p><h3>Does an extra monthly payment reduce interest?</h3><p>Usually yes. In Fixed Payments mode, enter the total amount you plan to pay each month; the schedule shows the shorter estimated term and reduced interest.</p><h3>Does this calculate a payoff date?</h3><p>It calculates the number of monthly payments and expresses that duration in years and months. It does not account for a lender's exact billing date or daily-interest convention.</p>"""
    if calc.get("slug") == "amortization-calculator":
        return """
<h2>Loan amortization schedule</h2><p>An amortization schedule separates every payment into interest and principal. Interest is calculated from the opening balance, so early payments generally contain more interest. As principal falls, less interest accrues and more of the same scheduled payment reduces the balance.</p>
<p class="formula">monthly payment = P x r x (1 + r)^n / ((1 + r)^n - 1)</p>
<p>Here, P is the loan amount, r is the monthly interest rate, and n is the number of monthly payments. At a zero rate, payment equals principal divided by the number of months.</p>
<h2>Amortization example</h2><p>A $200,000 fixed-rate loan at 6% for 15 years has a scheduled monthly payment of about $1,687.71. Without fees or extra payments, 180 payments total about $303,788 and include about $103,788 of interest.</p>
<h2>How extra payments change the loan</h2><p>Extra principal reduces the balance before later interest is calculated. The calculator supports an extra amount every month, an annual extra payment, and one dated one-time payment. Results compare the accelerated schedule with the original contractual schedule so you can see estimated interest and time saved.</p>
<h2>Interest rate versus APR</h2><p>This model treats the entered percentage as a fixed nominal annual rate divided by 12. It does not separately add origination fees, points, closing costs, insurance, or taxes. The <a href="https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that APR can include the interest rate plus certain lender fees. Use the rate that matches the schedule you want to model.</p>
<h2>Assumptions and limits</h2><p>The schedule assumes monthly payments, a fixed rate, no missed or late payments, and extra amounts applied directly to principal. Some lenders use daily interest, different rounding, payment-date conventions, prepayment penalties, or special instructions for principal-only payments. Compare this estimate with the lender's own payoff statement.</p>
<h2>Related loan tools</h2><p>Use the <a href="/mortgage-calculator/">mortgage calculator</a> when property tax and insurance matter, the <a href="/payment-calculator/">payment calculator</a> to solve for either payment or payoff term, and the <a href="/loan-calculator/">loan calculator</a> for custom compounding or repayment frequencies.</p>
<h2>Frequently asked questions</h2><h3>What is the difference between principal and interest?</h3><p>Principal is the amount borrowed or still owed. Interest is the borrowing charge calculated from the outstanding balance.</p><h3>Do extra payments always save interest?</h3><p>They generally save interest on a fixed-rate amortizing loan when the lender applies them promptly to principal and no offsetting fee applies.</p><h3>Why can my lender's schedule differ?</h3><p>Lenders may use exact payment dates, daily interest, contractual rounding, escrow, fees, or principal-payment processing rules that this monthly planning model does not include.</p>"""
    if calc.get("slug") == "retirement-calculator":
        return """
<h2>Four retirement planning questions</h2><p>This calculator separates retirement planning into four useful questions: the nest egg needed to support an income goal, the monthly savings required to reach a target, the inflation-adjusted withdrawal supported by projected savings, and how long an existing balance may last. Use the mode that matches the decision you are making.</p>
<h2>How much money do you need to retire?</h2><p>The first mode projects current income to retirement, applies the replacement percentage you enter, subtracts Social Security, pension, or other monthly income, and estimates the savings needed to fund the remaining gap through life expectancy. It then compares that target with the future value of current savings and contributions.</p>
<p class="formula">retirement income gap = desired annual income - annual Social Security, pension, and other income</p>
<p class="formula">savings gap = required nest egg - projected savings at retirement</p>
<h2>Monthly retirement savings goal</h2><p>The savings mode solves for the level monthly contribution that could grow current savings to a chosen retirement target. It also compares the required amount with what you already contribute. Returns are compounded monthly and held constant for the projection.</p>
<h2>Retirement withdrawals and longevity</h2><p>The withdrawal mode first projects contributions until retirement, then calculates a starting monthly withdrawal that increases with the inflation assumption and draws the balance toward zero at life expectancy. The longevity mode runs the reverse test: it applies an entered withdrawal, raises it annually, and estimates when the balance is depleted.</p>
<h2>Social Security estimates</h2><p>Enter Social Security as an outside monthly estimate rather than asking this calculator to infer it from one salary. The <a href="https://www.ssa.gov/prepare/get-benefits-estimate" rel="external noopener">Social Security Administration</a> provides personalized estimates based on your earnings record and lets you compare claiming ages. The SSA also notes that benefit estimates can change with earnings and the age you claim.</p>
<h2>Inflation and investment return</h2><p>Inflation increases the future dollar amount needed to maintain purchasing power. Investment return grows savings but is not guaranteed. The <a href="https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator" rel="external noopener">Investor.gov compound interest calculator</a> likewise treats contribution, time, return, and compounding assumptions as inputs rather than predictions. Test conservative and optimistic scenarios instead of relying on one result.</p>
<h2>Important limitations</h2><p>Results are educational estimates, not financial, tax, or investment advice. The model does not include taxes, investment fees, market volatility, required minimum distributions, contribution limits, health-care or long-term-care shocks, changes in benefits, or account-specific withdrawal rules. A constant return is especially unrealistic year to year; poor returns early in retirement can reduce sustainability even when the long-run average is unchanged.</p>
<h2>Frequently asked questions</h2><h3>Should I enter Social Security in today's dollars?</h3><p>Yes. In the first mode, other retirement income is entered in today's dollars and grows with the same inflation assumption as the retirement spending target.</p><h3>Does the 4% rule guarantee that money will last?</h3><p>No. It is a planning guideline, not a guarantee. This calculator instead uses your return, inflation, and time horizon to create a deterministic projection.</p><h3>Why does a small return change have a large effect?</h3><p>Long time horizons compound differences in assumed returns. Compare several scenarios and pay attention to fees and inflation.</p><h3>Where can I estimate Social Security?</h3><p>Use your official SSA earnings record and benefit estimator for a personalized amount, then enter that monthly estimate here.</p>"""
    if calc.get("slug") == "401k-calculator":
        return """
<h2>401(k) balance and retirement income projection</h2><p>The projection mode grows your current balance with employee contributions and employer matching contributions through the retirement age you enter. Salary and contributions are updated once per year, while account growth and deposits are modeled monthly. The result separates your starting balance, employee deposits, employer match, and estimated investment growth.</p>
<p class="formula">monthly employee contribution = annual salary x contribution rate / 12</p>
<p class="formula">monthly employer match = annual salary x min(contribution rate, match limit) x match rate / 12</p>
<h2>2026 401(k) contribution limits</h2><p>The <a href="https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-401k-and-profit-sharing-plan-contribution-limits" rel="external noopener">IRS 401(k) contribution limits</a> set the 2026 employee elective-deferral limit at $24,500. A plan may allow an additional $8,000 catch-up contribution for participants age 50 or older, while people who attain ages 60 through 63 in 2026 may have an $11,250 catch-up limit. The general combined employee-and-employer annual-additions limit is $72,000, excluding permitted catch-up contributions.</p>
<p>Future limits are unknown and may change with cost-of-living adjustments. The projection therefore does not force today's dollar limit across every future year. Instead, it shows whether the first-year contribution exceeds the current 2026 limit. Your plan may impose a lower limit, and contributions across multiple plans may need to be aggregated.</p>
<h2>How employer matching works</h2><p>An employer match is usually based on how much of your salary you contribute, up to one or more plan thresholds. For example, a plan might match 100% of the first 3% of pay and 50% of the next 2%. The employer-match mode handles that two-tier structure and estimates the contribution rate needed to capture the full stated match.</p>
<p>Some plans calculate matching every pay period and do not provide a year-end true-up. Contributing too much early in the year can then reduce later matches after you reach the employee deferral limit. The calculator shows a full-year contribution ceiling, but only your plan administrator can confirm whether a true-up applies.</p>
<h2>Early 401(k) withdrawal estimate</h2><p>Early distributions are generally included in taxable income and may also face a 10% additional tax. The withdrawal mode applies the federal, state, and local rates you enter, then adds the modeled 10% amount unless age or the selected exception inputs indicate otherwise. It is an estimate of net proceeds, not a tax return calculation.</p>
<p>The IRS lists exceptions that are more detailed than this form can capture. The separation-from-service exception generally concerns distributions after leaving the employer in or after the year you reach age 55 and usually applies to that employer's plan, not automatically to an IRA. Review the <a href="https://www.irs.gov/retirement-plans/plan-participant-employee/retirement-topics-exceptions-to-tax-on-early-distributions" rel="external noopener">IRS guidance on early distributions</a> before relying on an exception.</p>
<h2>Assumptions and limitations</h2><p>The projection assumes a constant return, steady contributions, annual salary growth, no fees, and fully vested employer contributions. Actual returns vary, plan expenses reduce growth, matching and vesting formulas differ, and a loan or rollover can change the account path. The retirement-income estimate is a deterministic inflation-adjusted withdrawal through life expectancy; it is not a guarantee and does not model market sequence risk, taxes in retirement, or required minimum distributions.</p>
<h2>Frequently asked questions</h2><h3>Does the calculator distinguish traditional and Roth 401(k) contributions?</h3><p>No. Both can share the same investment-growth projection, but their current and future tax treatment differs. The balance result is pre-tax or after-tax only to the extent your actual account is.</p><h3>Is employer match part of my employee limit?</h3><p>Employer match does not count toward the employee elective-deferral limit, but it generally counts toward the separate overall annual-additions limit.</p><h3>What return should I use?</h3><p>Use several scenarios rather than one optimistic number. Returns are not guaranteed, and fees, asset allocation, and the timing of gains and losses can materially change the outcome.</p><h3>Can I use this for a 403(b) or TSP?</h3><p>The growth math may be useful, but plan rules, matching formulas, contribution limits, and withdrawal exceptions can differ. Verify the rules for the specific plan.</p>"""
    if calc.get("slug") == "social-security-calculator":
        return """
<h2>Social Security claiming age calculator</h2><p>This calculator compares U.S. retired-worker benefits from age 62 through age 70. Start with the monthly benefit shown for your full retirement age in your <a href="https://www.ssa.gov/prepare/get-benefits-estimate" rel="external noopener">official Social Security estimate</a>. The tool applies the SSA claiming-age adjustment to that amount and compares the cumulative value of each start age through the life expectancy you enter.</p>
<p class="formula">early reduction = 5/9 of 1% for each of the first 36 months before FRA, plus 5/12 of 1% for each additional month</p>
<p class="formula">delayed retirement credit for people born in 1943 or later = 2/3 of 1% for each month after FRA, stopping at age 70</p>
<h2>Full retirement age by birth year</h2><p>Full retirement age is 66 for people born from 1943 through 1954, then rises by two months for each birth year from 1955 through 1959. It is 67 for people born in 1960 or later. The <a href="https://www.ssa.gov/benefits/retirement/planner/ageincrease.html" rel="external noopener">SSA retirement age calculator</a> notes a special convention for January 1 birthdays: use the previous birth year when determining FRA.</p>
<h2>How the claim-age comparison works</h2><p>The planner calculates an estimated monthly benefit at each possible claiming month, applies the cost-of-living adjustment you enter, and optionally compounds benefits already received at the entered investment return. It selects the claim age with the highest modeled value at life expectancy. That is a financial comparison only, not a recommendation.</p>
<p>The two-age mode is useful when your SSA account already provides distinct payment estimates. It compares cumulative benefits, investment-adjusted values, and the simple break-even age when the larger later payment catches up with benefits collected earlier. Taxes are not included.</p>
<h2>2026 retirement earnings test</h2><p>If you receive retirement benefits while working before full retirement age, SSA may withhold part of the benefit. In 2026, the lower annual exempt amount is $24,480, with $1 withheld for every $2 earned above that amount. In the year you reach FRA, the higher amount is $65,160 and $1 is withheld for every $3 above the limit, counting only earnings before the FRA month. Beginning with the FRA month, earnings no longer reduce benefits. See the <a href="https://www.ssa.gov/benefits/retirement/planner/whileworking.html" rel="external noopener">SSA working while receiving benefits guidance</a>.</p>
<p>SSA later recalculates the monthly benefit to credit months in which benefits were reduced or withheld. The earnings-test mode estimates current-year withholding only; it does not model that later adjustment, the special first-year monthly rule, or work outside the United States.</p>
<h2>What this calculator does not estimate</h2><p>It does not recreate your primary insurance amount from a 35-year earnings record, estimate disability or survivor benefits, model spousal coordination, determine eligibility, calculate Medicare premiums, or calculate federal and state tax on benefits. Actual payments also reflect SSA rounding and individual record details. Use the result for scenario comparison and verify decisions with SSA.</p>
<h2>Frequently asked questions</h2><h3>Is age 70 always the best time to claim?</h3><p>No. Delaying increases the monthly amount, but the financially preferable age depends on longevity, investment return, cash needs, health, work, taxes, and household or survivor considerations.</p><h3>Why should I enter my SSA estimate instead of salary?</h3><p>Retirement benefits depend on indexed earnings across up to 35 years, not one current salary. Your SSA record is a stronger starting point than a shortcut based only on today's pay.</p><h3>Does the earnings test permanently lose withheld benefits?</h3><p>SSA states that benefits are recalculated at full retirement age to credit months when benefits were withheld. This calculator does not estimate that later increase.</p><h3>Does delaying after age 70 increase benefits?</h3><p>No. Delayed retirement credits stop at age 70.</p>"""
    if calc.get("slug") == "loan-calculator":
        return """
<h2>Loan payment calculator</h2><p>Use the amortized-loan section for a conventional fixed-payment installment loan. Enter principal, annual interest rate, term, compounding frequency, and payment frequency to calculate each payment, total payments, total interest, and the full amortization schedule.</p>
<p class="formula">payment = P x r x (1 + r)^n / ((1 + r)^n - 1)</p>
<p>In the formula, P is principal, r is the effective rate for each payment period, and n is the number of payments. When the rate is zero, payment equals principal divided by the number of payments.</p>
<h2>Fixed-payment loan example</h2><p>A $100,000 loan at a 6% annual interest rate, compounded monthly and repaid monthly over 10 years, has a payment of about $1,110.21. Across 120 payments, total paid is about $133,224.60 and total interest is about $33,224.60.</p>
<h2>Amortization schedule</h2><p>Each fixed payment first covers interest on the remaining balance; the rest reduces principal. Early payments contain more interest because the balance is larger. Later payments shift toward principal. The schedule shows payment, principal, interest, and ending balance for every period.</p>
<h2>Deferred payment loan</h2><p>Use the second model when principal and interest accumulate until one amount is due at maturity. It compounds the entered principal for the selected term and frequency without periodic payments.</p>
<p class="formula">amount due = principal x (1 + annual rate / compounds per year)^(compounds per year x years)</p>
<h2>Bond or predetermined due amount</h2><p>Use the third model when the future amount due is known and you need its present value. The result discounts the future value back over the selected term using the entered rate and compounding frequency.</p>
<p class="formula">present value = future amount / (1 + annual rate / compounds per year)^(compounds per year x years)</p>
<h2>Interest rate versus APR</h2><p>The calculator treats the entered percentage as the nominal rate used in the selected compounding model. A disclosed APR can include certain fees and may not equal the note interest rate. The <a href="https://www.consumerfinance.gov/ask-cfpb/what-is-the-difference-between-a-loan-interest-rate-and-the-apr-en-733/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that APR is intended to reflect the interest rate plus additional loan charges.</p>
<h2>Compare total cost, not only payment</h2><p>A longer term can reduce each payment while increasing total interest. CFPB guidance recommends comparing amount financed, APR or rate, term, monthly payment, and total cost. Origination, documentation, insurance, late, and other fees are not included unless they are already part of the principal you enter.</p>
<h2>Frequently asked questions</h2><h3>Is this also a loan payment calculator?</h3><p>Yes. The amortized-loan model calculates periodic payment, total interest, total paid, and an amortization schedule.</p><h3>Can payment frequency differ from compounding frequency?</h3><p>Yes. The calculator converts the entered annual rate into an effective rate for the selected payment interval.</p><h3>Does the result include fees?</h3><p>No. Add financed fees to principal if appropriate and compare the result with the lender's legally required disclosures.</p><h3>Can I use it for mortgages or auto loans?</h3><p>The basic amortization math applies, but dedicated <a href="/mortgage-calculator/">mortgage</a> and <a href="/auto-loan-calculator/">auto loan</a> tools include costs specific to those products.</p>"""
    if calc.get("slug") == "feet-to-meters-calculator":
        return """
<h2>How to convert feet to meters</h2><p>Multiply a length in feet by 0.3048 to convert it to meters. The factor is exact, so any rounding happens only when the result is displayed. When a measurement includes inches, divide the inches by 12, add that decimal to the feet, and then multiply the combined value by 0.3048.</p>
<p class="formula">meters = (feet + inches / 12) x 0.3048</p>
<h2>Feet and inches example</h2><p>For 5 feet 10 inches, first convert 10 inches to 0.833333 feet. The total is 5.833333 feet, and 5.833333 x 0.3048 equals 1.778 meters. The calculator keeps the unrounded value during the calculation and also reports centimeters, decimal feet, and total inches.</p>
<h2>Common feet to meters conversions</h2><div class="table-scroll"><table class="data-table"><thead><tr><th>Feet</th><th>Meters</th><th>Feet</th><th>Meters</th></tr></thead><tbody><tr><td>1 ft</td><td>0.3048 m</td><td>10 ft</td><td>3.048 m</td></tr><tr><td>3 ft</td><td>0.9144 m</td><td>25 ft</td><td>7.62 m</td></tr><tr><td>5 ft</td><td>1.524 m</td><td>50 ft</td><td>15.24 m</td></tr><tr><td>6 ft</td><td>1.8288 m</td><td>100 ft</td><td>30.48 m</td></tr><tr><td>10 ft</td><td>3.048 m</td><td>500 ft</td><td>152.4 m</td></tr><tr><td>20 ft</td><td>6.096 m</td><td>5,280 ft</td><td>1,609.344 m</td></tr></tbody></table></div>
<h2>Common height conversions</h2><p>US height is often written with separate feet and inches, while many international forms request meters or centimeters. Use the second input for the inches portion rather than treating a value such as 5 ft 10 in as 5.10 decimal feet.</p><div class="table-scroll"><table class="data-table"><thead><tr><th>Height</th><th>Meters</th><th>Centimeters</th></tr></thead><tbody><tr><td>5 ft 0 in</td><td>1.524 m</td><td>152.4 cm</td></tr><tr><td>5 ft 4 in</td><td>1.6256 m</td><td>162.56 cm</td></tr><tr><td>5 ft 8 in</td><td>1.7272 m</td><td>172.72 cm</td></tr><tr><td>5 ft 10 in</td><td>1.778 m</td><td>177.8 cm</td></tr><tr><td>6 ft 0 in</td><td>1.8288 m</td><td>182.88 cm</td></tr><tr><td>6 ft 4 in</td><td>1.9304 m</td><td>193.04 cm</td></tr></tbody></table></div>
<h2>Why 0.3048 is exact</h2><p>The modern international foot is defined as exactly 0.3048 meter. The <a href="https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors" rel="external noopener">NIST Guide to the SI conversion tables</a> documents this relationship. Because the factor is defined rather than measured, values such as 1 foot = 0.3048 meter and 100 feet = 30.48 meters are exact before display rounding.</p>
<h2>International foot versus US survey foot</h2><p>The former US survey foot was slightly longer, at approximately 0.3048006096 meter. NIST states that it became obsolete for most uses on January 1, 2023, with exceptions for historical and legacy applications. This calculator uses the international foot. If you are converting coordinates or archived survey records, confirm which foot definition the source data uses before calculating. See the <a href="https://www.nist.gov/pml/us-surveyfoot" rel="external noopener">NIST US survey foot reference</a> for the distinction.</p>
<h2>Where feet-to-meter conversion is used</h2><p>Feet commonly appear in US room dimensions, building plans, property descriptions, human height, aviation altitude, and product specifications. Meters are standard in scientific work and widely used for construction and everyday measurement outside the United States. For a rectangular room, convert each dimension separately before multiplying; converting square feet to square meters requires an area factor, not the linear 0.3048 factor.</p>
<h2>Rounding feet and meters</h2><p>Choose the number of decimal places according to the measurement itself. Two decimal places in meters are often enough for a rough room dimension, while product drawings or engineering work may require millimeters and documented tolerances. Do not report more precision than the original measurement supports. The calculator displays up to six decimal places in the headline and up to eight in the calculation details.</p>
<h2>Frequently asked questions</h2><h3>How many meters are in one foot?</h3><p>One foot equals exactly 0.3048 meter. Multiply any number of feet by 0.3048.</p><h3>How do I convert meters back to feet?</h3><p>Divide meters by 0.3048. The reverse mode also separates the decimal result into whole feet and remaining inches.</p><h3>Is 5 feet 10 inches the same as 5.10 feet?</h3><p>No. Ten inches is 10/12, or about 0.833333 foot, so 5 ft 10 in is about 5.833333 decimal feet and exactly 1.778 meters.</p><h3>How many meters are in 100 feet?</h3><p>One hundred feet equals exactly 30.48 meters because 100 x 0.3048 = 30.48.</p><h3>Can I enter more than 12 inches?</h3><p>Yes. The calculator adds all entered inches to the total length. For example, 5 feet plus 14 inches is treated as 6 feet 2 inches.</p>"""
    if calc.get("slug") == "interest-calculator":
        return """
<h2>Simple interest versus compound interest</h2><p>Simple interest is calculated only on the money contributed. Compound interest is calculated on contributions plus interest already credited. This calculator runs both methods with the same rate, deposits, timing, tax estimate, and duration so the difference is visible rather than theoretical.</p>
<p class="formula">simple balance = contributions + (contributed principal x annual rate x time invested)</p>
<p class="formula">compound growth = balance x effective monthly rate, repeated each month</p>
<h2>Worked example</h2><p>Start with $10,000, add $200 at the end of each month, and earn a 6% nominal annual rate compounded monthly for 10 years. The calculator compares the ending balances, total interest, and the extra amount created by earning interest on prior interest. Change the contribution timing to see why earlier deposits usually finish with more.</p>
<h2>How recurring deposits are treated</h2><p>Monthly contributions are added every month and annual contributions once per complete year. In the simple-interest comparison, each deposit earns simple interest only for the time it remains invested. In the compound comparison, each deposit can earn interest on both principal and previously credited interest. The <a href="https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator" rel="external noopener">SEC Investor.gov calculator</a> also models starting principal, recurring deposits, time, rate, and compounding frequency.</p>
<h2>Compounding frequency and effective yield</h2><p>The nominal annual rate is converted to an effective monthly rate from the selected daily, weekly, monthly, quarterly, annual, or continuous frequency. More frequent compounding usually produces a higher effective annual yield when the nominal rate is unchanged. The <a href="https://www.consumerfinance.gov/ask-cfpb/how-does-compound-interest-work-en-1683/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that compound interest adds interest to principal, allowing future interest to be earned on a larger balance.</p>
<h2>Tax and inflation assumptions</h2><p>The optional tax rate is an illustration applied to positive interest as it accrues. It does not model tax brackets, account type, deductions, losses, or the timing rules on a tax return. Inflation converts each ending balance to estimated purchasing power in today's dollars. Rates, returns, and inflation are held constant and are not forecasts.</p>
<h2>When to use each result</h2><p>Simple interest is useful for understanding principal-only growth and some short-term arrangements. Compound interest is the better model when credited interest remains in an account. For a dedicated compound-only schedule, use the <a href="/compound-interest-calculator/">compound interest calculator</a>. The <a href="https://www.fdic.gov/consumer-resource-center/chapter-5-compound-interest" rel="external noopener">FDIC compound-interest guide</a> provides additional consumer examples.</p>
<h2>Frequently asked questions</h2><h3>Do monthly deposits earn a full year of interest?</h3><p>No. Each deposit begins earning from its selected beginning- or end-of-month timing, so later deposits have less time to grow.</p><h3>Is the entered rate APY?</h3><p>No. It is treated as a nominal annual rate. The results table shows the effective annual yield generated by the selected compounding frequency.</p><h3>Can simple interest ever be higher?</h3><p>With a positive rate and otherwise identical inputs, compounding is normally equal to or higher than simple interest. Negative rates, taxes, or unusual cash-flow timing can change that relationship.</p>"""
    if calc.get("slug") == "compound-interest-calculator":
        return """
<h2>How compound interest is calculated</h2><p>Compound interest earns a return on the original principal and on interest already added to the balance. This calculator supports daily, weekly, biweekly, semimonthly, monthly, quarterly, semi-annual, annual, and continuous compounding, plus monthly and annual contributions.</p>
<p class="formula">A = P(1 + r / n)^(nt)</p>
<p>In the formula, P is the starting principal, r is the nominal annual rate as a decimal, n is the number of compounding periods per year, and t is time in years. Continuous compounding uses A = Pe^(rt). Recurring contributions are added separately at the selected beginning or end timing.</p>
<h2>Worked example</h2><p>A $10,000 initial investment earning 6% annually, compounded monthly for 10 years with $200 deposited at the end of every month, grows to about $50,970 before taxes and fees. Total contributions are $34,000 and estimated interest is about $16,970.</p>
<h2>Contributions and annual increases</h2><p>Monthly additions are made every month. Annual additions are made once for each complete year. The optional annual contribution increase raises both amounts at the start of each new 12-month period, which can model a planned savings increase after a raise. The <a href="https://www.investor.gov/financial-tools-calculators/calculators/compound-interest-calculator" rel="external noopener">SEC Investor.gov compound interest tool</a> likewise models an initial investment, recurring monthly contributions, time, rate, and compounding frequency.</p>
<h2>Compounding frequency and APY</h2><p>At the same nominal annual rate, more frequent compounding produces a higher effective annual yield. The <a href="https://www.consumerfinance.gov/ask-cfpb/how-does-compound-interest-work-en-1683/" rel="external noopener">Consumer Financial Protection Bureau</a> explains that increasing compounding frequency, earning a higher rate, and adding principal can accelerate savings growth. Contribution size and time often have a larger effect than small frequency differences.</p>
<h2>Tax and inflation estimates</h2><p>The optional tax rate is applied to positive interest as it accrues, not to contributed principal. Actual tax timing, tax rates, account rules, losses, and deductions can differ. The inflation result discounts the ending balance into today's estimated purchasing power. The <a href="https://www.bls.gov/cpi/factsheets/purchasing-power-constant-dollars.htm" rel="external noopener">U.S. Bureau of Labor Statistics</a> explains that purchasing power falls as prices rise and that price-index ratios can convert nominal amounts to constant dollars.</p>
<h2>How to use the rate scenarios</h2><p>The lower, entered, and higher results change only the annual interest rate by the range selected in More Options. They keep the time, deposits, contribution growth, tax, inflation, and compounding assumptions the same. Use the range as a sensitivity check, not a best-case or worst-case forecast. Actual returns can vary and this calculator does not include account fees or market volatility.</p>
<h2>Frequently asked questions</h2><h3>What is the difference between APR and APY?</h3><p>APR or a nominal annual rate does not itself include intra-year compounding. APY is the effective annual yield after the selected compounding frequency.</p><h3>Does contribution timing change the answer?</h3><p>Yes. A beginning-of-period contribution has more time to earn interest than an otherwise identical end-of-period contribution.</p><h3>What is the Rule of 72?</h3><p>Dividing 72 by an annual percentage rate gives a rough estimate of the years needed to double money. It is a shortcut, not an exact projection.</p>"""
    if calc.get("slug") == "truck-payload-calculator":
        return """
<h2>How to calculate truck payload</h2><p>Payload capacity is the truck's GVWR minus its curb weight. Remaining payload subtracts everyone and everything carried by the truck, including passengers, cargo, accessories, and trailer tongue weight.</p>
<p class="formula">remaining payload = GVWR - curb weight - passengers - cargo - tongue weight</p>
<h2>Truck payload example</h2><p>A truck with a 7,200 lb GVWR and 5,200 lb curb weight has 2,000 lb of total payload capacity. After 400 lb of occupants, 200 lb of cargo, and 750 lb of trailer tongue weight, 650 lb remains.</p>
<h2>Where to find the numbers</h2><p>Use the certification and tire-loading labels on the driver-side door jamb for the specific vehicle. Trim, options, accessories, and modifications can change curb weight and available payload. A loaded scale weight is better than a brochure estimate.</p>
<h2>Payload is not towing capacity</h2><p>Payload is weight carried by the truck. Towing capacity is trailer weight pulled behind it. Trailer tongue weight presses on the truck and therefore consumes payload even though most trailer weight is carried by the trailer axles.</p>
<h2>Authoritative guidance</h2><p>Ford's US towing guidance explains that payload includes cargo and passengers and recommends using the vehicle label or a public scale. See <a href="https://www.ford.com/towing/" rel="external noopener">Ford Towing</a>. Always follow the ratings for the exact vehicle, tires, axles, and hitch.</p>
<h2>Frequently asked questions</h2><h3>Does the driver count as payload?</h3><p>Yes. Occupants, cargo, aftermarket equipment, and tongue weight all use available payload.</p><h3>Can remaining payload be negative?</h3><p>Yes. A negative result means the entered load exceeds GVWR and should be reduced.</p><h3>Is the advertised maximum payload right for every trim?</h3><p>No. Advertised maximums usually describe a favorable configuration. Use the label and ratings on the specific truck.</p>"""
    if calc.get("slug") == "towing-capacity-calculator":
        return """
<h2>How this towing capacity calculator works</h2><p>The safe planning estimate is the lowest limit produced by the vehicle's published tow rating, GCWR headroom, hitch trailer rating, and payload available for tongue weight. A trailer must stay under every applicable limit, not only the largest advertised number.</p>
<p class="formula">planning trailer limit = minimum of tow rating, GCWR limit, hitch limit, and payload-based limit</p>
<h2>Why payload often limits towing</h2><p>Passengers and cargo increase the loaded tow-vehicle weight and reduce both GCWR headroom and payload available for trailer tongue weight. For example, 650 lb of remaining payload at a 12% tongue-weight assumption supports about 5,417 lb of trailer weight before payload is exhausted.</p>
<h2>Terms used in the calculator</h2><p><strong>GVWR</strong> is the maximum loaded weight of the tow vehicle. <strong>GCWR</strong> is the maximum combined loaded weight of the vehicle and trailer. <strong>Tongue weight</strong> is the downward trailer load carried by the hitch and tow vehicle.</p>
<h2>Use vehicle-specific ratings</h2><p>Ratings vary with model, trim, drivetrain, axle ratio, factory options, tires, and hitch equipment. Verify the certification label, tire-loading label, owner's manual, towing guide, hitch label, and loaded scale weights before towing.</p>
<h2>Safety references</h2><p><a href="https://www.ford.com/towing/" rel="external noopener">Ford's towing guidance</a> describes GVWR, GCWR, curb weight, payload, and conventional trailer tongue weight. SAE J2807 establishes performance criteria used to determine tow-vehicle GCWR and trailer weight ratings for applicable light vehicles.</p>
<h2>Frequently asked questions</h2><h3>What tongue-weight percentage should I enter?</h3><p>Use the trailer and vehicle manufacturer's guidance. Conventional trailers are often planned around 10% to 15%, but the correct range depends on the trailer and hitch system.</p><h3>Does this replace a scale?</h3><p>No. Weigh the fully loaded tow vehicle and trailer when possible, and check individual axle ratings as well as total ratings.</p><h3>What if one limit is much lower than the others?</h3><p>The lowest limit controls. The results identify that limiting factor so you can review the relevant load or equipment rating.</p>"""
    if calc.get("slug") == "mpg-calculator":
        return """
<h2>How to calculate MPG</h2><p>Fill the tank, reset the trip odometer, drive normally, then refill the tank. Divide the distance driven by the fuel needed to refill. Using multiple tanks reduces the effect of small fill-level differences.</p>
<p class="formula">US MPG = miles driven / US gallons used</p>
<h2>MPG example</h2><p>Driving 300 miles and using 12 US gallons gives 25 US MPG. The same physical fuel economy is about 30.02 Imperial MPG, 9.41 L/100 km, or 10.63 km/L.</p>
<h2>US MPG versus Imperial MPG</h2><p>A UK Imperial gallon is larger than a US gallon, so Imperial MPG is numerically higher for the same vehicle and journey. Always identify which gallon a published MPG figure uses before comparing vehicles.</p>
<h2>Understanding L/100 km</h2><p>Liters per 100 kilometers measures consumption rather than distance per unit of fuel. Lower L/100 km is better, while higher MPG and km/L are better. The calculator normalizes the entered distance and fuel volume before showing every format.</p>
<h2>Getting a realistic result</h2><p>Use actual pump volume and odometer distance over several fill-ups. Traffic, speed, temperature, tire pressure, payload, idling, terrain, and driving style can all move real-world economy away from a window-sticker estimate. For official US estimates by model, use the <a href="https://www.fueleconomy.gov/feg/Find.do?action=sbsSelect" rel="external noopener">fueleconomy.gov vehicle comparison</a>.</p>
<h2>Frequently asked questions</h2><h3>Why does my dashboard MPG differ?</h3><p>Trip computers estimate fuel flow and may use different averaging periods. A careful fill-to-fill calculation provides an independent check.</p><h3>Can I enter kilometers and liters?</h3><p>Yes. Select kilometers and liters; the result still includes US MPG, Imperial MPG, L/100 km, and km/L.</p><h3>Is MPGe the same as MPG?</h3><p>No. MPGe is an energy-equivalent comparison used for alternative-fuel and electric vehicles; this calculator measures liquid-fuel volume.</p>"""
    if calc.get("slug") == "trip-fuel-cost-calculator":
        return """
<h2>How to estimate trip fuel cost</h2><p>Choose US or metric units, enter one-way distance, select one way or round trip, then add your vehicle's real-world fuel economy and expected pump price. Multiple trips and cost sharing are included.</p>
<p class="formula">US fuel cost = total miles / MPG x price per gallon</p>
<p class="formula">Metric fuel cost = total kilometers x L/100 km / 100 x price per liter</p>
<h2>Road-trip example</h2><p>A 650-mile one-way trip in a 28 MPG vehicle uses about 23.21 US gallons. At $3.60 per gallon, estimated fuel cost is $83.57. A round trip doubles distance, fuel, and cost before any extra detours.</p>
<h2>Plan a more realistic fuel budget</h2><p>Use your recent highway or mixed-driving average rather than the best published rating. Add expected detour mileage to the distance field and use an average fuel price for the route. When you need an official model estimate, check <a href="https://www.fueleconomy.gov/feg/Find.do?action=sbsSelect" rel="external noopener">fueleconomy.gov</a>. The result excludes tolls, parking, maintenance, depreciation, lodging, and food.</p>
<h2>Splitting gas money</h2><p>The per-person result divides fuel cost evenly by the number of travelers. It does not assign different shares for the driver, vehicle owner, or passengers, so adjust the entered count or agree on a different split when needed.</p>
<h2>US and metric modes</h2><p>US mode uses miles, MPG, and price per US gallon. Metric mode uses kilometers, L/100 km, and price per liter. Currency selection changes display only; it does not perform an exchange-rate conversion.</p>
<h2>Frequently asked questions</h2><h3>Should distance be one way?</h3><p>Yes. Enter one-way distance and choose Round trip when you plan to return over roughly the same distance.</p><h3>Where can I find my vehicle's MPG?</h3><p>Use a recent fill-to-fill calculation for the most relevant estimate, or start with the combined rating for the exact vehicle configuration.</p><h3>Does the result include idling?</h3><p>Only indirectly if your entered real-world MPG already reflects idling. Add a margin for heavy traffic, cold weather, towing, or long stationary periods.</p>"""
    if calc.get("slug") == "car-trade-in-value-calculator":
        return """
<h2>How to estimate car trade-in value</h2><p>Start with the asking price of a similar dealer-listed vehicle in your area: same year, make, model, trim, drivetrain, mileage, and condition. Adjust that benchmark for meaningful differences, then subtract expected dealer margin and reconditioning costs.</p>
<p class="formula">estimated trade-in = comparable retail price + adjustments - dealer margin - reconditioning</p>
<h2>Trade-in example</h2><p>A $22,000 comparable listing with a -$500 mileage or condition adjustment, $1,800 dealer margin, and $600 of expected work produces an estimated $19,100 trade-in value. With a $12,000 payoff, estimated positive equity is $7,100.</p>
<h2>Trade-in value versus private sale</h2><p>A dealer trade-in is usually lower than a private-party sale because a reseller may need to inspect, repair, detail, market, finance, and warranty the vehicle. In exchange, a trade-in can be faster and may reduce transaction complexity.</p>
<h2>Loan equity and negative equity</h2><p>Equity equals estimated trade-in value minus the lender's current payoff quote. A negative result means the payoff exceeds the estimated trade value. Ask the lender for a current payoff amount rather than adding remaining scheduled payments.</p>
<h2>Possible sales-tax benefit</h2><p>Some jurisdictions reduce the taxable amount of a replacement vehicle by an eligible trade-in value, while others do not. Enter only a rate and benefit that applies to your transaction. The calculator caps the assumed credit at the replacement vehicle price and is not tax advice.</p>
<h2>Check a data-backed valuation</h2><p>This tool does not have live auction, VIN, or dealer transaction data. Compare its planning estimate with multiple current offers and a recognized valuation provider. The <a href="https://www.kbb.com/faq/values/" rel="external noopener">Kelley Blue Book value FAQ</a> explains why trade-in value is generally below private-party value.</p>
<h2>Frequently asked questions</h2><h3>Should I use the original MSRP?</h3><p>No. Use a current local retail listing for a genuinely comparable vehicle; original MSRP does not capture present market demand.</p><h3>Can I enter a positive adjustment?</h3><p>Yes. Use a positive amount when your vehicle has lower mileage, better condition, or valuable equipment compared with the benchmark.</p><h3>Is this a dealer offer?</h3><p>No. It is a transparent planning estimate. Only an appraisal or written buyer offer establishes an actionable trade value.</p>"""
    if calc.get("slug") == "used-car-value-calculator":
        return """
<h2>How to estimate a used car's value</h2><p>Use a current local retail asking price for a closely comparable vehicle, then adjust for condition, mileage, options, history, and local demand. The calculator derives separate planning ranges for dealer retail, private-party sale, and dealer trade-in.</p>
<p class="formula">adjusted retail = local benchmark x condition factor x regional factor + mileage adjustment + options adjustment</p>
<h2>Used-car value example</h2><p>A $22,000 local retail benchmark in good condition, adjusted down $500 for mileage, produces an adjusted retail estimate of $20,400 before any options or regional adjustment. The private-party and trade-in estimates are lower to reflect different selling channels.</p>
<h2>Choose the right benchmark</h2><p>Match year, make, model, trim, engine, drivetrain, major options, title history, mileage, and ZIP-area market as closely as possible. Asking prices are not completed sale prices, so review several listings rather than relying on one unusually high or low example.</p>
<h2>Retail, private-party, and trade-in values</h2><p>Dealer retail reflects a vehicle offered by a business. Private-party value estimates an as-is transaction between individuals. Trade-in value is typically lower because the dealer must leave room for inspection, reconditioning, inventory, and operating costs.</p>
<h2>Vehicle condition</h2><p>Most vehicles should not be rated excellent. Consider mechanical condition, warning lights, tires, glass, paint, interior wear, accident and title history, maintenance records, odors, and required repairs. Be consistent with the condition of your benchmark vehicle.</p>
<h2>Independent comparison</h2><p>This calculator has no live VIN or transaction feed. Use it to reconcile listings and offers, then compare with a professional valuation. The <a href="https://www.kbb.com/faq/values/" rel="external noopener">Kelley Blue Book value FAQ</a> notes that age, mileage, equipment, condition, and location affect value.</p>
<h2>Frequently asked questions</h2><h3>Why is the value shown as a range?</h3><p>Real transactions vary with negotiation, local supply, buyer demand, inspection results, and timing. A range is more honest than false single-dollar precision.</p><h3>Does the calculator know my VIN?</h3><p>No. You supply the comparable market price and adjustments. Use a VIN-based valuation provider for vehicle-specific market data.</p><h3>Can an accident change the estimate?</h3><p>Yes. Enter a negative options and history adjustment based on comparable vehicles or documented appraisal evidence.</p>"""
    if calc.get("slug") == "tire-size-calculator":
        return """
<h2>How to compare tire sizes</h2><p>A metric tire code such as 225/65R17 describes a 225 mm nominal section width, a sidewall height equal to 65% of that width, radial construction, and a 17-inch wheel. Enter the original and proposed sizes to compare their calculated geometry.</p>
<p class="formula">overall diameter = wheel diameter + 2 x (section width x aspect ratio / 100) / 25.4</p>
<h2>Speedometer and ride-height changes</h2><p>A larger tire travels farther per revolution. The calculator multiplies the indicated speed by the new-to-original diameter ratio. Half of the diameter change is the approximate change in static ground clearance. Odometer distance changes by the same ratio.</p>
<h2>Tire-size example</h2><p>Changing from 225/65R17 to 235/60R18 increases calculated diameter from about 28.52 to 29.10 inches, a difference of about 2.06%. At an indicated 60 mph, calculated road speed is about 61.23 mph, and static ground clearance rises about 0.29 inch.</p>
<h2>Is a 3% diameter difference safe?</h2><p>Three percent is a common comparison guideline, not a universal fitment or safety approval. Vehicle systems, gearing, wheel width, load capacity, clearances, tire construction, and manufacturer requirements all matter. Actual mounted dimensions also vary by tire model, measuring rim, pressure, load, and tread wear.</p>
<h2>Verify the replacement size</h2><p><a href="https://www.nhtsa.gov/vehicle-safety/tires" rel="external noopener">NHTSA TireWise</a> advises checking the owner's manual or Tire and Loading Information Label and using the original size or another size recommended by the vehicle manufacturer. Also verify load index, speed rating, inflation pressure, wheel-width range, and full steering and suspension clearance with a qualified tire professional.</p>
<h2>Frequently asked questions</h2><h3>Why can the listed diameter differ from this result?</h3><p>The formula uses nominal size-code dimensions. Consult the tire manufacturer's specification sheet for measured overall diameter and revolutions per mile.</p><h3>Does this calculator confirm wheel fitment?</h3><p>No. It compares tire geometry only. Bolt pattern, wheel offset, hub bore, brake clearance, fender clearance, suspension clearance, and load ratings require separate verification.</p>"""
    if calc.get("slug") == "wheel-offset-calculator":
        return """
<h2>How wheel offset changes fitment</h2><p>Wheel offset is the distance from the wheel centerline to its hub-mounting face. Positive offset moves the wheel inward; lower or negative offset usually moves the outer face farther toward the fender. Width and offset must be compared together.</p>
<p class="formula">inner position = half wheel width + effective offset; outer position = half wheel width - effective offset</p>
<h2>Wheel-offset example</h2><p>Compared with an 8-inch ET45 wheel, a 9-inch ET35 wheel sits about 22.7 mm farther outward and has about 2.7 mm less inner clearance. Across both sides of an axle, the estimated track increases about 45.4 mm.</p>
<h2>How spacers affect offset</h2><p>A spacer moves the wheel outward. The calculator treats effective offset as the new wheel offset minus spacer thickness. A 5 mm spacer on an ET35 wheel therefore behaves like approximately ET30 for these position calculations.</p>
<h2>Backspacing estimate</h2><p>Backspacing is measured from the hub-mounting face to the inner wheel edge. The calculator adds one inch to nominal wheel width as a common approximation for both rim lips, then adds offset. Published wheel specifications should be used when exact overall width is available.</p>
<h2>Fitment limitations</h2><p>This geometry comparison does not verify bolt pattern, center bore, lug-seat type, stud engagement, brake-caliper clearance, tire bulge, suspension travel, steering lock, fender clearance, alignment, or wheel and tire load ratings. Measure the vehicle and confirm the setup with the wheel manufacturer or a qualified installer.</p>
<h2>Frequently asked questions</h2><h3>Does a lower offset add more poke?</h3><p>Usually yes when width is unchanged. A wider wheel can add both inner and outer extension, so compare width and offset together.</p><h3>Is more inner clearance always better?</h3><p>No. Moving outward can create fender interference, change scrub radius, alter steering feel, and increase load on components. The result is a dimensional estimate, not an approval.</p>"""
    if calc.get("slug") == "concrete-volume-calculator":
        return """
<h2>How much concrete do I need?</h2><p>Select a rectangular slab or footing, round column, or set of post holes. The calculator converts every measurement to feet, calculates volume, adds the entered waste allowance, and reports cubic feet, cubic yards, bags, and estimated material cost.</p>
<p class="formula">rectangular volume = length x width x thickness; round volume = π x radius² x height x quantity</p>
<h2>Concrete slab example</h2><p>A 20 ft by 10 ft slab at 4 inches thick contains 66.67 cubic feet before waste. Adding 10% gives 73.33 cubic feet, or about 2.72 cubic yards. At an approximate 0.60 cubic foot yield, that is 123 80 lb bags after rounding up.</p>
<h2>Concrete bag yields</h2><p>The calculator uses approximate yields of 0.30 cubic foot for a 40 lb bag, 0.45 cubic foot for a 60 lb bag, and 0.60 cubic foot for an 80 lb bag. These figures match the published <a href="https://www.quikrete.com/pdfs/data_sheet-concrete%20mix%201101.pdf" rel="external noopener">QUIKRETE Concrete Mix data sheet</a>. Product yield varies, so use the label for the exact mix you buy.</p>
<h2>Bagged mix versus ready-mix</h2><p>The two cost estimates use only the prices you enter. Bag cost excludes sales tax, tools, water, labor, and delivery. Ready-mix cost excludes short-load, delivery, waiting-time, pumping, and minimum-order charges. Call local suppliers before treating either result as a quote.</p>
<h2>Waste allowance</h2><p>Uneven excavation, subgrade variation, forms, spillage, and leftover material can increase the required volume. Ten percent is a common planning allowance, but the appropriate margin depends on site conditions and measurement confidence.</p>
<h2>Frequently asked questions</h2><h3>How many cubic feet are in a cubic yard?</h3><p>One cubic yard equals 27 cubic feet.</p><h3>Do I round concrete bags up?</h3><p>Yes. Partial bags are not normally purchased, so the calculator rounds the final bag count up after waste is included.</p><h3>Does this calculate structural requirements?</h3><p>No. It estimates material volume only. Slab thickness, reinforcement, mix strength, joints, drainage, frost protection, and foundation design must follow the project plans and local requirements.</p>"""
    if calc.get("slug") == "roof-pitch-calculator":
        return """
<h2>How to calculate roof pitch</h2><p>Choose the measurement you already know: rise per 12 inches, measured rise and horizontal run, or angle from horizontal. The calculator normalizes each method into an X:12 pitch, degree angle, percent slope, and pitch multiplier.</p>
<p class="formula">pitch rise per 12 = rise / run x 12; angle = arctan(rise / run); multiplier = √(1 + slope²)</p>
<h2>6:12 roof-pitch example</h2><p>A 6:12 roof rises 6 inches for every 12 inches of horizontal run. Its slope is 50%, its angle is about 26.57°, and its pitch multiplier is about 1.118. A 12 ft horizontal rafter run with a 12 in horizontal overhang has an estimated sloped length of 14.53 ft.</p>
<h2>Roof area and roofing squares</h2><p>When a horizontal plan area is entered, the calculator multiplies it by the pitch factor to estimate sloped surface area. One roofing square equals 100 square feet. The estimate does not include waste, starter strips, ridge caps, valleys, hips, dormers, or multiple roof pitches.</p>
<h2>Roof slope terminology</h2><p>In common US field usage, X:12 describes inches of rise per 12 inches of horizontal run. The <a href="https://www.gaf.com/en-us/document-library/documents/installation-instructions-%26-guides/guide__steepslope_profield_guide_version_20__english.pdf" rel="external noopener">GAF steep-slope field guide</a> explains rise, run, span, slope, and pitch conventions.</p>
<h2>Frequently asked questions</h2><h3>Is run the same as span?</h3><p>No. Run is horizontal distance from support to ridge. For a centered symmetrical gable, run is commonly half the full building span.</p><h3>Does pitch determine the required rafter size?</h3><p>No. Member size also depends on species, grade, spacing, loads, span, bearing, and code requirements. Use approved plans or a span resource such as the <a href="https://awc.org/resources/span-options-calculator-for-wood-joists-and-rafters/" rel="external noopener">American Wood Council span calculator</a>.</p>"""
    if calc.get("slug") == "rafter-length-calculator":
        return """
<h2>How to calculate common rafter length</h2><p>Enter the roof pitch as rise per 12 inches, the horizontal run from wall support to ridge, and the horizontal eave overhang. The calculator applies the same slope factor to the run and overhang.</p>
<p class="formula">slope factor = √(pitch² + 12²) / 12; rafter length = (run + horizontal overhang) x slope factor</p>
<h2>Rafter-length example</h2><p>For a 6:12 roof with a 12 ft horizontal run and 12 in horizontal overhang, the base rafter length is about 13.42 ft and the total sloped length is about 14.53 ft. The roof rise over the 12 ft run is 6 ft.</p>
<h2>Horizontal versus sloped overhang</h2><p>This calculator expects the overhang's horizontal projection. A 12 in horizontal overhang is longer than 12 in when measured along a sloped rafter. If your drawing already gives the tail length along the slope, do not enter that value as horizontal overhang.</p>
<h2>Geometry is not structural sizing</h2><p>The result is theoretical line length before ridge, birdsmouth, plumb-cut, seat-cut, fascia, and field-fitting adjustments. It does not select lumber size or verify loads. The <a href="https://awc.org/resources/calculator-help/" rel="external noopener">American Wood Council span-calculator guidance</a> explains that allowable spans depend on strength, stiffness, shear, bearing, species, grade, spacing, and loads.</p>
<h2>Frequently asked questions</h2><h3>Do I subtract half the ridge-board thickness?</h3><p>Often the theoretical run is adjusted for the ridge detail, but the exact layout depends on the plans and framing method. This calculator leaves that job-specific adjustment to the user.</p><h3>Does the total linear footage include waste?</h3><p>No. It multiplies the calculated length by the entered rafter count. Add an appropriate cutting and procurement allowance separately.</p>"""
    if calc.get("slug") == "square-footage-calculator":
        return """
<h2>How to calculate square footage</h2><p>Select a rectangle, circle, triangle, or four-wall room. Enter dimensions in feet, subtract door and window openings when using wall mode, and add an optional overage for the material being ordered.</p>
<p class="formula">rectangle = length x width; circle = π x (diameter / 2)²; triangle = base x height / 2</p>
<h2>Room and wall example</h2><p>A 20 ft by 12 ft rectangular floor contains 240 square feet and has a 64 ft perimeter. At 10% overage, the material-order area is 264 square feet. Four 8 ft walls around that room contain 512 square feet before subtracting doors and windows.</p>
<h2>Gross wall area versus net wall area</h2><p>Gross wall area is room perimeter multiplied by wall height. Net wall area subtracts the combined square footage of openings. Whether to subtract small openings depends on the product, labor method, and estimator, so enter only the deductions appropriate to your project.</p>
<h2>Material cost estimate</h2><p>The cost result multiplies the overage-adjusted area by the entered price per square foot. It does not include whole-package rounding, tax, delivery, accessories, labor, surface preparation, or minimum charges. Use a product-specific calculator when flooring, tile, paint, drywall, or roofing must be purchased in packages.</p>
<h2>Frequently asked questions</h2><h3>How many square feet are in a square yard?</h3><p>One square yard equals 9 square feet.</p><h3>Can this calculate an L-shaped room?</h3><p>Split the room into non-overlapping rectangles, calculate each section, and add the areas. Do not include the same section twice.</p><h3>Is this the same as official home living area?</h3><p>No. Real-estate and appraisal standards define which spaces count and how they are measured. This tool calculates geometric project area only.</p>"""
    if calc.get("slug") == "flooring-calculator":
        return """
<h2>How much flooring do I need?</h2><p>Measure the room and any closets or connected sections, add a waste allowance, then divide by the exact coverage printed on one box. Flooring is purchased in whole boxes, so the calculator always rounds the box count up.</p>
<p class="formula">boxes = round up((room area + extra area) x (1 + waste %) / box coverage)</p>
<h2>Flooring example</h2><p>A 20 ft by 12 ft room contains 240 square feet. With 10% waste, the target is 264 square feet. If each box covers 24 square feet, the order is exactly 11 boxes. At $48 per box, estimated flooring cost is $528 before tax and delivery.</p>
<h2>Coverage ordered and leftover material</h2><p>Because boxes are rounded up, purchased coverage can exceed the waste-adjusted target. The leftover result is purchased coverage minus the original measured floor area; it includes the planned cutting allowance and any additional package-rounding remainder.</p>
<h2>Underlayment</h2><p>Underlayment is calculated separately from its entered roll coverage and price. Some flooring includes an attached pad, some systems require a specific moisture or sound-control product, and some installations use no separate underlayment. Follow the flooring manufacturer's instructions.</p>
<h2>Waste allowance</h2><p>Room shape, installation direction, plank length, pattern matching, defects, and future repair stock affect waste. Use the allowance specified by your installer or product guidance instead of treating a default percentage as universal.</p>
<h2>Frequently asked questions</h2><h3>Should I use price per box or price per square foot?</h3><p>This calculator uses price per box so the cost matches the rounded number of packages purchased.</p><h3>Can I combine multiple rooms?</h3><p>Yes. Add the measured areas of rooms and closets and enter that total as extra area, or run each room separately when layouts and waste rates differ.</p>"""
    if calc.get("slug") == "tile-calculator":
        return """
<h2>How many tiles do I need?</h2><p>Enter the project dimensions, tile face dimensions, waste allowance, pieces per box, and price per box. The calculator estimates individual pieces, rounds to full boxes, and reports purchased coverage and material cost.</p>
<p class="formula">tiles = round up(project area / tile face area x (1 + waste %)); boxes = round up(tiles / pieces per box)</p>
<h2>Tile example</h2><p>A 15 ft by 12 ft area contains 180 square feet. Twelve-inch square tiles cover one square foot each, so 10% waste produces a 198-tile target. With 15 tiles per box, 14 boxes provide 210 tiles and 210 square feet of face coverage.</p>
<h2>Waste and spare tile</h2><p>Cuts, breakage, pattern alignment, room shape, tile variation, and future repairs affect the order. <a href="https://www.lowes.com/n/calculators/tile-floor-calculator" rel="external noopener">Lowe's tile calculator guidance</a> suggests purchasing an extra 10% for trim and waste, but the right allowance depends on the project.</p>
<h2>Mortar and grout are product-specific</h2><p>This page estimates tile pieces and boxes, not mortar or grout. Coverage depends on the product, trowel, tile dimensions, joint width and depth, substrate, and application. Use the exact product data sheet or a manufacturer tool such as the <a href="https://www.mapei.com/us/en-us/tools-and-downloads/product-calculators" rel="external noopener">MAPEI product calculators</a>.</p>
<h2>Frequently asked questions</h2><h3>Does grout-joint width reduce the tile count?</h3><p>Joint spacing affects layout, but cuts and edge conditions make a simple deduction unreliable. This estimator uses tile face area and a user-controlled waste allowance for purchasing.</p><h3>Why is box count rounded up?</h3><p>Retailers normally sell sealed tile in full boxes. The calculator rounds up after converting the required pieces to boxes.</p><h3>Should wall tile and floor tile be combined?</h3><p>Run separate estimates when tile sizes, patterns, waste, products, or dye lots differ.</p>"""
    if calc.get("slug") == "deck-board-calculator":
        return """
<h2>How many deck boards do I need?</h2><p>Enter the deck dimensions, actual board width, spacing gap, and stock-board length. The calculator determines the number of board rows, rounds each row to whole stock lengths, applies waste, and estimates joists, fasteners, packages, and material cost.</p>
<p class="formula">rows = round up(deck width / (board width + gap)); boards per row = round up(deck length / stock length)</p>
<h2>Deck-board example</h2><p>A 16 ft by 12 ft deck using 5.5 in boards with a 1/8 in gap needs 26 rows. With 16 ft stock, each row uses one board. Adding 10% waste produces an order of 29 full boards. At $35 each, the board estimate is $1,015.</p>
<h2>Joists and fasteners</h2><p>For a 16 ft joist run at 16 in on center, this planning model counts 13 joist lines, including both edges. Two fasteners at each of 26 board-row and 13 joist intersections produce about 676 fasteners, or two 350-count boxes. Picture framing, blocking, stairs, railings, hidden-fastener clips, and manufacturer-specific edge details are not included.</p>
<h2>Stock length and cut planning</h2><p>Boards are rounded up for each row, so the estimate is intentionally conservative when stock is shorter than the deck. Butt joints must land on approved framing, and reusable offcuts depend on the actual layout. Create a cut plan before ordering when staggered seams or multiple stock lengths could reduce waste.</p>
<h2>Spacing and structural limits</h2><p>Use the actual installed face width and the gap required by the decking manufacturer. Composite, PVC, diagonal, and specialty patterns can require different joist spacing and fasteners. This calculator estimates materials; it does not design a safe deck. Use approved plans and resources such as the <a href="https://awc.org/resources/span-options-calculator-for-wood-joists-and-rafters/" rel="external noopener">American Wood Council span calculator</a>.</p>
<h2>Frequently asked questions</h2><h3>Does the board count include waste?</h3><p>Yes. The final order rounds the base whole-board count up after applying the entered waste percentage.</p><h3>Are picture-frame border boards included?</h3><p>No. Estimate border, fascia, stair, and breaker boards separately because their stock lengths and framing requirements vary.</p><h3>How do I estimate lumber volume?</h3><p>Use the <a href="/board-foot-calculator/">board foot calculator</a> when lumber is sold or compared by board-foot volume.</p>"""
    if calc.get("slug") == "board-foot-calculator":
        return """
<h2>How to calculate board feet</h2><p>A board foot is a lumber-volume unit equal to a piece 1 inch thick, 12 inches wide, and 1 foot long. Enter thickness and width in inches, length in feet, and the number of pieces.</p>
<p class="formula">board feet = thickness (in) x width (in) x length (ft) / 12 x quantity</p>
<h2>Board-foot example</h2><p>One 1 in by 8 in by 10 ft board contains 6.67 board feet. Ten boards contain 66.67 board feet. With 10% waste, the purchasing estimate is 73.33 board feet; at $4.25 per board foot, estimated lumber cost is $311.67.</p>
<h2>Nominal versus actual dimensions</h2><p>Use the dimensions your supplier uses for pricing. Hardwood may be priced from stated rough thickness and measured width, while surfaced softwood commonly has smaller actual dimensions than its nominal name. Do not mix nominal dimensions with an actual-dimension price basis.</p>
<h2>Board feet, cubic feet, and linear feet</h2><p>Board feet measure volume, not surface area or length. Twelve board feet equal one cubic foot. Linear feet describe only total length and do not account for thickness or width. This calculator reports all three so you can check the order from different views.</p>
<h2>US lumber reference</h2><p>The USDA Forest Service defines one board foot as the volume of a board 1 foot long, 1 foot wide, and 1 inch thick. See its <a href="https://www.srs.fs.usda.gov/pubs/rb/rb_srs068.pdf" rel="external noopener">forest-products measurement reference</a>.</p>
<h2>Frequently asked questions</h2><h3>Should waste be added before cost?</h3><p>Yes. The cost result multiplies the waste-adjusted board feet by the entered price per board foot.</p><h3>Can I use this for decking?</h3><p>Use this page to compare lumber volume. For piece count, joists, fasteners, and whole-board purchasing, use the <a href="/deck-board-calculator/">deck board calculator</a>.</p><h3>Does this account for random widths?</h3><p>Run separate calculations for different dimensions or use an average only when your supplier's tally supports it.</p>"""
    if calc.get("slug") == "voltage-drop-calculator":
        return """
<h2>How to calculate voltage drop</h2><p>Select DC, single-phase AC, or three-phase AC, then enter conductor material and size, one-way run length, current, and system voltage. The calculator uses approximate conductor resistance to estimate voltage lost and voltage remaining at the load.</p>
<p class="formula">DC or single phase: Vdrop = 2 x length x current x resistance / 1,000; three phase: Vdrop = √3 x length x current x resistance / 1,000</p>
<h2>Voltage-drop example</h2><p>A 100 ft one-way, 120 V single-phase circuit carrying 15 A on 12 AWG copper at an approximate 1.93 ohms per 1,000 ft loses 5.79 V, or 4.83%. The calculator also estimates a larger conductor and the maximum run length for the selected drop target.</p>
<h2>Why conductor size matters</h2><p>Longer runs, higher current, and higher resistance increase drop. Larger conductors have lower resistance. Aluminum has higher resistance than copper at the same gauge, so equivalent installations may require different sizes and terminations.</p>
<h2>Planning limits</h2><p>A common design target is 3% for a branch circuit, but the correct limit depends on the complete system and applicable requirements. Southwire's <a href="https://www.southwire.com/calculator-vdrop" rel="external noopener">voltage drop calculator</a> also considers ampacity and installation details. This page uses a simplified resistive model and does not account for reactance, temperature, harmonics, parallel conductors, or every installation method.</p>
<h2>Frequently asked questions</h2><h3>Is one-way length or round-trip length entered?</h3><p>Enter one-way length. The DC and single-phase formula doubles it for the outgoing and returning path.</p><h3>Does the recommended gauge prove code compliance?</h3><p>No. It addresses the entered voltage-drop target only. Check ampacity, insulation, terminals, temperature, bundling, conduit fill, equipment instructions, and local code with a qualified electrician.</p><h3>Where can I check ampacity too?</h3><p>Use the <a href="/wire-size-calculator/">wire size calculator</a> for a combined reference ampacity and voltage-drop estimate.</p>"""
    if calc.get("slug") == "wire-size-calculator":
        return """
<h2>How this wire size calculator works</h2><p>The tool compares two constraints: reference ampacity after applying the continuous-load factor and conductor size needed to stay within the entered voltage-drop limit. It recommends the larger conductor produced by those two checks.</p>
<p class="formula">design current = noncontinuous amps + 125% x continuous amps</p>
<h2>Wire-size example</h2><p>A 24 A load that is entirely continuous produces 30 A of design current. For a 100 ft, 240 V single-phase copper circuit with a 3% drop target, 10 AWG satisfies the simplified 30 A reference ampacity and keeps estimated voltage drop below the target.</p>
<h2>Ampacity is installation-specific</h2><p>The 60°C and 75°C choices are reference columns, not permission to use a temperature rating. Terminal ratings, insulation, conductor material, ambient temperature, conductor count, cable type, wet locations, and special equipment rules can change the permitted ampacity. Small-conductor overcurrent limits are included conservatively in this planning table.</p>
<h2>Voltage-drop check</h2><p>The voltage-drop calculation uses approximate conductor resistance and actual entered load current. Southwire's professional <a href="https://www.southwire.com/calculators/re3%E2%84%A2-building-wire-selector-calculator" rel="external noopener">building wire selector</a> explains that final selection remains subject to current codes, the licensed electrician, and the local authority having jurisdiction.</p>
<h2>Frequently asked questions</h2><h3>Why can voltage drop require a larger wire?</h3><p>A conductor may carry the load safely at a short distance but lose too much voltage over a long run. The final recommendation uses whichever requirement produces the larger size.</p><h3>Can I size service conductors with this?</h3><p>No. Services, feeders, motors, HVAC, EV charging, and other equipment can have additional rules. Use project-specific engineering and code calculations.</p><h3>Should continuous load exceed total load?</h3><p>No. The calculator caps the continuous portion at the entered total load.</p>"""
    if calc.get("slug") == "breaker-size-calculator":
        return """
<h2>How to estimate breaker size</h2><p>Enter continuous load separately from noncontinuous load. The calculator applies 125% to the continuous portion, adds the noncontinuous portion, and selects the next standard breaker rating at or above that planning current.</p>
<p class="formula">minimum planning current = 125% x continuous load + noncontinuous load</p>
<h2>Breaker-size example</h2><p>A 16 A continuous load with no other load produces 20 A of planning current, so the reference result is a 20 A breaker. A 16 A continuous load plus 5 A noncontinuous load produces 25 A.</p>
<h2>Why continuous load is treated differently</h2><p>NFPA material for Article 215 describes feeder sizing for a combination of noncontinuous load plus 125% of continuous load, subject to listed 100%-rated assemblies and other exceptions. A continuous load is generally one expected to remain at maximum current for three hours or more.</p>
<h2>A breaker does not size the whole circuit</h2><p>The selected overcurrent device must protect conductors and match equipment, terminal, fault-current, panel, and local requirements. Some loads such as motors, HVAC, welders, and EV supply equipment use additional rules or nameplate values. Confirm the complete circuit with a licensed electrician and the AHJ.</p>
<h2>Frequently asked questions</h2><h3>Is the next standard size always allowed?</h3><p>No. This tool rounds to a familiar rating for planning, but conductor and equipment rules can prohibit that result.</p><h3>Can I add every appliance breaker to size a panel?</h3><p>No. The US Department of Energy notes that panel breakers cannot simply be added because not every load operates simultaneously. Residential service calculations use specific demand methods.</p><h3>What wire size goes with the result?</h3><p>Use the <a href="/wire-size-calculator/">wire size calculator</a> for a preliminary conductor check, then verify the installation professionally.</p>"""
    if calc.get("slug") == "electrical-load-calculator":
        return """
<h2>How to calculate electrical load</h2><p>Enter continuous and noncontinuous real power separately, then select DC, single-phase AC, or three-phase AC. For AC loads, enter power factor. The calculator reports actual current, apparent power, 125%-adjusted planning current, and a reference standard breaker.</p>
<p class="formula">single-phase amps = watts / (volts x power factor); three-phase amps = watts / (√3 x volts x power factor)</p>
<h2>Electrical-load example</h2><p>At 120 V single phase and power factor 1.0, 1,800 W continuous plus 600 W noncontinuous equals 2,400 W and 20 A actual current. Applying 125% only to the continuous portion produces 23.75 A of planning current and a 25 A reference breaker.</p>
<h2>Watts, VA, and power factor</h2><p>Watts measure real power. Volt-amperes measure apparent power. For AC loads below unity power factor, the same real power requires more current. DC calculations ignore the power-factor entry.</p>
<h2>Panel and service limitations</h2><p>This tool combines entered loads; it is not a residential service calculation. The US Department of Energy's <a href="https://bsesc.energy.gov/sites/default/files/2024-10/Home%20Electrification%20and%20Electric%20Panel%20Upgrades.pdf" rel="external noopener">panel-upgrade factsheet</a> explains that electricians use nameplate loads and NEC demand methods rather than simply adding breaker ratings.</p>
<h2>Frequently asked questions</h2><h3>What counts as continuous load?</h3><p>A load expected to operate at maximum current for three hours or more is generally treated as continuous; confirm the applicable definition and equipment rule.</p><h3>Does this include motor efficiency?</h3><p>No. Enter electrical input watts, not mechanical output watts. Motors and HVAC equipment should be sized from nameplate and applicable rules.</p><h3>Can I convert a single value?</h3><p>Use the <a href="/watts-to-amps-calculator/">watts to amps calculator</a> or <a href="/amps-to-watts-calculator/">amps to watts calculator</a> for a simpler conversion.</p>"""
    if calc.get("slug") == "watts-to-amps-calculator":
        return """
<h2>How to convert watts to amps</h2><p>Select DC, single-phase AC, or balanced three-phase AC. Enter real power in watts and voltage. AC calculations also use power factor because watts can be lower than apparent power when current and voltage are not perfectly in phase.</p>
<p class="formula">DC: A = W / V; single phase: A = W / (V x PF); three phase: A = W / (√3 x V line-to-line x PF)</p>
<h2>Watts-to-amps example</h2><p>A 1,200 W resistive load at 120 V and power factor 1.0 draws 10 A. At power factor 0.8, the same 1,200 W real load requires 12.5 A and 1,500 VA of apparent power.</p>
<h2>Single-phase and three-phase voltage</h2><p>For the three-phase formula, enter line-to-line RMS voltage and total three-phase real power. Do not enter per-phase power or line-to-neutral voltage into that formula. The US Department of Energy's <a href="https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/FINAL%20Industrial%20Electrification%20Assessment%20Framework_0.pdf" rel="external noopener">industrial electrification framework</a> gives the same √3 x power-factor relationship for a typical three-phase AC load.</p>
<h2>Watts, VA, and VAR</h2><p>Watts are real power doing useful work. Volt-amperes are apparent power carried by the source and conductors. Reactive volt-amperes represent the quadrature portion in this simplified sinusoidal model. DC uses power factor 1 and has no reactive-power result.</p>
<h2>Continuous-load planning</h2><p>Choose continuous-load planning to display 125% of calculated current. That is a planning reference, not a complete breaker or conductor selection. Use the <a href="/electrical-load-calculator/">electrical load calculator</a> when continuous and noncontinuous loads must be entered separately.</p>
<h2>Frequently asked questions</h2><h3>Is 1,500 watts always 12.5 amps?</h3><p>Only at 120 V with power factor 1. Current changes with voltage, phase, and power factor.</p><h3>Should I use equipment output watts?</h3><p>Use electrical input power. Mechanical motor output and cooling capacity are not interchangeable with electrical input watts.</p><h3>How do I reverse the conversion?</h3><p>Use the <a href="/amps-to-watts-calculator/">amps to watts calculator</a> with the same voltage, phase, and power factor.</p>"""
    if calc.get("slug") == "amps-to-watts-calculator":
        return """
<h2>How to convert amps to watts</h2><p>Current alone does not determine power. Enter voltage and select DC, single-phase AC, or balanced three-phase AC. For AC, use the equipment's measured or nameplate power factor.</p>
<p class="formula">DC: W = A x V; single phase: W = A x V x PF; three phase: W = √3 x A x V line-to-line x PF</p>
<h2>Amps-to-watts example</h2><p>Ten amps at 120 V DC or single-phase AC with power factor 1.0 equals 1,200 W. A balanced three-phase load drawing 10 A at 208 V line-to-line and 0.9 power factor uses about 3,242 W of real power and 3,603 VA.</p>
<h2>Real, apparent, and reactive power</h2><p>The calculator reports watts and kilowatts as real power, VA and kVA as apparent power, and VAR as a simplified reactive-power magnitude. At power factor 1.0, watts equal VA and reactive power is zero.</p>
<h2>Three-phase assumptions</h2><p>The result assumes a balanced three-phase load and line-to-line RMS voltage. Unequal phase currents, distorted waveforms, harmonics, and transient conditions require measurement or a more detailed power analysis. The US Department of Energy's <a href="https://betterbuildingssolutioncenter.energy.gov/sites/default/files/attachments/FINAL%20Industrial%20Electrification%20Assessment%20Framework_0.pdf" rel="external noopener">industrial electrification framework</a> uses P = √3 x PF x amps x voltage for typical three-phase AC loads.</p>
<h2>Breaker rating is not measured current</h2><p>A 20 A breaker does not mean the circuit is continuously drawing 20 A. Use actual load current or equipment data, and verify conductor and protection requirements separately with the <a href="/breaker-size-calculator/">breaker size calculator</a> and a qualified electrician.</p>
<h2>Frequently asked questions</h2><h3>Why does a lower power factor reduce calculated watts?</h3><p>For fixed RMS volts and amps, a lower power factor means less apparent power becomes real power.</p><h3>Can this calculate energy use?</h3><p>No. Watts measure power. Multiply kilowatts by operating hours to estimate kilowatt-hours of energy.</p><h3>How do I calculate current from watts?</h3><p>Use the <a href="/watts-to-amps-calculator/">watts to amps calculator</a> and enter the same electrical assumptions.</p>"""
    return None


def default_calculator_copy(calc):
    return f"""
<h2>How it works</h2><p>{h(calc['desc'])} Use the units shown in the calculator and review every assumption before using the result.</p>
<h2>Formula</h2><p class="formula">{h(calc['formula'])}</p>
<h2>Worked example</h2><p>{h(calc['example'])}</p>
<h2>Important assumptions</h2><p>This tool is designed for planning and comparison. Real-world prices, manufacturer ratings, building requirements, lender terms, electrical codes, tolerances, and product specifications can vary.</p>
<h2>Frequently asked questions</h2><h3>Is this calculator free?</h3><p>Yes. It runs in your browser and does not require an account.</p><h3>Are the results exact?</h3><p>The math is deterministic for the entered values, but the result depends on inputs and assumptions. Verify safety-critical, financial, code-related, towing, fitment, and manufacturer-specific decisions with authoritative information.</p>"""


def analysis_extra_html(calc):
    if calc.get("slug") == "debt-payoff-calculator":
        return """<section class="mortgage-dashboard generic-dashboard debt-dashboard" aria-label="Debt payoff results">
<div class="section-head stack"><h2>Debt Payoff Results</h2><p>Compare payoff time and interest, then review the selected strategy's payoff order.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Balance Over Time</h3><canvas id="genericChart" width="620" height="220" aria-label="Debt balance over time" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Strategy Comparison</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Plan</th><th>Debt-free estimate</th><th>Total interest</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3 id="debtOrderTitle">Selected Plan Payoff Order</h3><div class="table-scroll"><table class="data-table" id="debtOrderTable"><thead><tr><th>Priority</th><th>Debt</th><th>Estimated payoff</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "ratio-calculator":
        return """<section class="mortgage-dashboard generic-dashboard ratio-dashboard" aria-label="Ratio calculation results">
<div class="section-head stack"><h2>Ratio Results</h2><p>Review the answer, equivalent form, proportional shares, and calculation steps.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3 id="ratioChartTitle">Ratio Parts</h3><canvas id="genericChart" width="620" height="220" aria-label="Ratio part comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Steps</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Step</th><th>Value</th><th>Explanation</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") in PRIORITY_LENGTH_CONVERSIONS:
        source, target, _ = conversion_parts(calc)
        return f"""<section class="mortgage-dashboard generic-dashboard conversion-dashboard" aria-label="{h(source)} and {h(target)} conversion results">
<div class="section-head stack"><h2>Conversion Results</h2><p>Compare the selected result with metric and US customary length units.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="table-card"><h3>Equivalent Measurements</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Measurement</th><th>Value</th><th>Calculation note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "feet-to-meters-calculator":
        return """<section class="mortgage-dashboard generic-dashboard conversion-dashboard" aria-label="Feet to meters conversion results">
<div class="section-head stack"><h2>Conversion Results</h2><p>Compare meters, centimeters, decimal feet, and feet-and-inches notation.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Measurement</th><th>Value</th><th>How it is calculated</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "rmd-calculator":
        return """<section class="mortgage-dashboard generic-dashboard rmd-dashboard" aria-label="Required minimum distribution results">
<div class="section-head stack"><h2>RMD Analysis</h2><p>Review the required distribution, IRS table factor, account impact, and projected annual schedule.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>First-Year Account Impact</h3><canvas id="genericChart" width="420" height="190" aria-label="Required minimum distribution and projected account growth" data-chart-type="bar"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card" id="rmdScheduleCard"><h3>Projected RMD Schedule</h3><div class="table-scroll"><table class="data-table" id="rmdSchedule"><thead><tr><th>Year</th><th>Age</th><th>Starting balance</th><th>Table / period</th><th>RMD</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "social-security-calculator":
        return """<section class="mortgage-dashboard generic-dashboard social-security-dashboard" aria-label="Social Security calculation results">
<div class="section-head stack"><h2>Social Security Results</h2><p>Compare claiming ages, cumulative benefits, break-even timing, or 2026 earnings-test withholding.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Benefit Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Social Security benefit comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card" id="ssScheduleCard"><h3>Claim Age Comparison</h3><div class="table-scroll"><table class="data-table" id="ssSchedule"><thead><tr><th>Claim age</th><th>Benefit factor</th><th>Starting monthly</th><th>Lifetime paid</th><th>Value at life expectancy</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "401k-calculator":
        return """<section class="mortgage-dashboard generic-dashboard k401-dashboard" aria-label="401(k) calculation results">
<div class="section-head stack"><h2>401(k) Results</h2><p>Review the balance, contributions, taxes or matching details for the selected mode.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Result Breakdown</h3><canvas id="genericChart" width="620" height="230" aria-label="401(k) result breakdown" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card" id="k401ScheduleCard"><h3>Annual 401(k) Projection</h3><div class="table-scroll"><table class="data-table" id="k401Schedule"><thead><tr><th>Age</th><th>Salary</th><th>Employee</th><th>Employer</th><th>Growth</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "retirement-calculator":
        return """<section class="mortgage-dashboard generic-dashboard retirement-dashboard" aria-label="Retirement planning results">
<div class="section-head stack"><h2>Retirement Plan</h2><p>Review the target, projected balance, income estimate, and year-by-year outlook.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Retirement Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Retirement savings and income comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Annual Projection</h3><div class="table-scroll"><table class="data-table" id="retirementSchedule"><thead><tr><th>Age / year</th><th>Contributions or withdrawals</th><th>Growth</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "amortization-calculator":
        return """<section class="mortgage-dashboard generic-dashboard amortization-dashboard" aria-label="Loan amortization results">
<div class="section-head stack"><h2>Amortization Results</h2><p>Review payment, interest, payoff timing, savings, and the balance schedule.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Principal and Interest</h3><canvas id="genericChart" width="380" height="200" aria-label="Loan principal and interest breakdown" data-chart-type="pie" data-center-label="total paid"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Annual Amortization Schedule</h3><div class="table-scroll"><table class="data-table" id="amortAnnual"><thead><tr><th>Year</th><th>Payments</th><th>Principal</th><th>Interest</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
<details class="schedule-details"><summary>View monthly amortization schedule</summary><div class="table-card"><div class="table-scroll"><table class="data-table" id="amortMonthly"><thead><tr><th>Month</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Extra</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div></details>
</section>"""
    if calc.get("slug") == "finance-calculator":
        return """<section class="mortgage-dashboard generic-dashboard finance-tvm-dashboard" aria-label="Time value of money results">
<div class="section-head stack"><h2>Finance Calculator Results</h2><p>Review the solved TVM value, rates, cash flows, and period-by-period schedule.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Cash Flow Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Present value, total payments, future value, and interest comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Period Schedule</h3><div class="table-scroll"><table class="data-table" id="financeSchedule"><thead><tr><th>Period</th><th>Opening value</th><th>Payment</th><th>Interest</th><th>Ending value</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "salary-calculator":
        return """<section class="mortgage-dashboard generic-dashboard salary-converter-dashboard" aria-label="Salary conversion results">
<div class="section-head stack"><h2>Salary Conversion Results</h2><p>Compare gross pay periods before taxes and the effect of unpaid days off.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Annual and Monthly Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Unadjusted and unpaid-time adjusted salary comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Pay Frequency Table</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Pay period</th><th>Unadjusted gross pay</th><th>Adjusted for unpaid days</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "bmi-calculator":
        return """<section class="mortgage-dashboard generic-dashboard bmi-dashboard" aria-label="Adult BMI calculation results">
<div class="section-head stack"><h2>Adult BMI Results</h2><p>Review the BMI category, reference weight range, and supporting measures.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Adult BMI Thresholds</h3><canvas id="genericChart" width="620" height="230" aria-label="BMI value and adult category thresholds" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "standard-deviation-calculator":
        return """<section class="mortgage-dashboard generic-dashboard stats-dashboard" aria-label="Standard deviation calculation results">
<div class="section-head stack"><h2>Statistics Results</h2><p>Compare dispersion, center, range, and the calculation steps.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Data Position</h3><canvas id="genericChart" width="620" height="230" aria-label="Minimum, mean, median, and maximum comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric or step</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "fraction-calculator":
        return """<section class="mortgage-dashboard generic-dashboard fraction-dashboard" aria-label="Fraction calculation results">
<div class="section-head stack"><h2>Fraction Results</h2><p>Review the simplified answer, equivalent forms, and calculation steps.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Value Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Fraction operands and result comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Step-by-Step Calculation</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Step</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "percent-calculator":
        return """<section class="mortgage-dashboard generic-dashboard percent-dashboard" aria-label="Percentage calculation results">
<div class="section-head stack"><h2>Percentage Results</h2><p>Review the answer, formula, inputs, and related values.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Value Comparison</h3><canvas id="genericChart" width="620" height="230" aria-label="Percentage input and result comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "sales-tax-calculator":
        return """<section class="mortgage-dashboard generic-dashboard finance-dashboard" aria-label="Sales tax results">
<div class="section-head stack"><h2>Sales Tax Results</h2><p>Review the before-tax amount, sales tax, and final total.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Purchase Breakdown</h3><canvas id="genericChart" width="620" height="230" aria-label="Before-tax amount, sales tax, and final total" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "take-home-pay-calculator":
        return """<section class="mortgage-dashboard generic-dashboard finance-dashboard" aria-label="Take-home pay results">
<div class="section-head stack"><h2>Take-Home Pay Results</h2><p>Compare gross pay, taxes, deductions, and net pay for 2026.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Annual Pay Breakdown</h3><canvas id="genericChart" width="620" height="230" aria-label="Annual gross pay, taxes, deductions, and take-home pay" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Tax and Pay Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") in ("salary-increase-calculator", "discount-calculator"):
        labels = {
            "salary-increase-calculator": ("Raise and Pay Results", "Annual Pay Comparison"),
            "discount-calculator": ("Discount and Checkout Results", "Price, Savings, and Tax"),
        }
        title, chart_title = labels[calc.get("slug")]
        return f"""<section class="mortgage-dashboard generic-dashboard finance-dashboard" aria-label="{title}">
<div class="section-head stack"><h2>{title}</h2><p>Review the main answer, supporting amounts, and calculation details.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>{chart_title}</h3><canvas id="genericChart" width="620" height="230" aria-label="{chart_title}" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "car-depreciation-calculator":
        return """<section class="mortgage-dashboard generic-dashboard vehicle-value-dashboard" aria-label="Car depreciation results">
<div class="section-head stack"><h2>Vehicle Depreciation Results</h2><p>Review retained value, total loss, ownership-period cost, and the annual value schedule.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Starting Value and Depreciation</h3><canvas id="genericChart" width="620" height="220" aria-label="Starting value, ending value, and total depreciation" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Year-by-Year Depreciation</h3><div class="table-scroll"><table class="data-table" id="carDepSchedule"><thead><tr><th>Year</th><th>Opening value</th><th>Rate</th><th>Value lost</th><th>Ending value</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "car-resale-value-calculator":
        return """<section class="mortgage-dashboard generic-dashboard vehicle-value-dashboard" aria-label="Car resale value results">
<div class="section-head stack"><h2>Future Resale Results</h2><p>Compare projected value, depreciation, sale costs, payoff, and estimated net proceeds.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Value and Sale Proceeds</h3><canvas id="genericChart" width="620" height="220" aria-label="Current value, future value, depreciation, and net proceeds" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Depreciation Scenarios</h3><div class="table-scroll"><table class="data-table" id="resaleScenarios"><thead><tr><th>Scenario</th><th>Annual rate</th><th>Resale value</th><th>Net proceeds</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Annual Resale Projection</h3><div class="table-scroll"><table class="data-table" id="resaleSchedule"><thead><tr><th>Year</th><th>Opening value</th><th>Value lost</th><th>Ending value</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "bottleneck-calculator":
        return """<section class="mortgage-dashboard generic-dashboard bottleneck-dashboard" aria-label="PC bottleneck analysis results">
<div class="section-head stack"><h2>CPU and GPU Bottleneck Analysis</h2><p>Review the likely limiting side, target gap, frame-time or benchmark evidence, and verification notes.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3 id="bottleneckChartTitle">Frame-Time Comparison</h3><canvas id="genericChart" width="620" height="220" aria-label="CPU, GPU, and target frame-time comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Diagnostic Evidence</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>What it means</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") in ("horsepower-calculator", "power-to-weight-ratio-calculator"):
        horsepower = calc.get("slug") == "horsepower-calculator"
        title = "Horsepower, Torque, and RPM Results" if horsepower else "Power-to-Weight Results"
        chart_title = "Power Unit Comparison" if horsepower else "Current and Target Power"
        description = "Review the solved operating point and equivalent power and torque units." if horsepower else "Compare loaded weight, ratio formats, and power needed for the target ratio."
        return f"""<section class="mortgage-dashboard generic-dashboard performance-dashboard" aria-label="{title}">
<div class="section-head stack"><h2>{title}</h2><p>{description}</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>{chart_title}</h3><canvas id="genericChart" width="620" height="220" aria-label="{chart_title}" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") in ("concrete-volume-calculator", "roof-pitch-calculator", "rafter-length-calculator", "square-footage-calculator", "flooring-calculator", "tile-calculator", "deck-board-calculator", "board-foot-calculator", "voltage-drop-calculator", "wire-size-calculator", "breaker-size-calculator", "electrical-load-calculator", "watts-to-amps-calculator", "amps-to-watts-calculator"):
        labels = {
            "concrete-volume-calculator": ("Concrete Material Estimate", "Volume and Cost Comparison"),
            "roof-pitch-calculator": ("Roof Geometry", "Pitch and Area Results"),
            "rafter-length-calculator": ("Rafter Geometry", "Length Breakdown"),
            "square-footage-calculator": ("Area Estimate", "Area and Cost Results"),
            "flooring-calculator": ("Flooring Order", "Coverage and Cost Results"),
            "tile-calculator": ("Tile Order", "Pieces, Boxes, and Cost"),
            "deck-board-calculator": ("Deck Material Estimate", "Boards, Framing, and Cost"),
            "board-foot-calculator": ("Lumber Volume Estimate", "Board Feet and Cost"),
            "voltage-drop-calculator": ("Voltage Drop Results", "Voltage and Run-Length Analysis"),
            "wire-size-calculator": ("Wire Size Estimate", "Ampacity and Voltage-Drop Checks"),
            "breaker-size-calculator": ("Breaker Planning Result", "Load and Capacity Analysis"),
            "electrical-load-calculator": ("Electrical Load Results", "Power and Current Analysis"),
            "watts-to-amps-calculator": ("Watts to Amps Results", "Current and Power Components"),
            "amps-to-watts-calculator": ("Amps to Watts Results", "Real and Apparent Power"),
        }
        title, chart_title = labels[calc.get("slug")]
        return f"""<section class="mortgage-dashboard generic-dashboard project-dashboard" aria-label="{title} results">
<div class="section-head stack"><h2>{title}</h2><p>Review the main result, supporting measurements, and calculation details.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>{chart_title}</h3><canvas id="genericChart" width="620" height="230" aria-label="{chart_title}" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") in ("tire-size-calculator", "wheel-offset-calculator"):
        tire = calc.get("slug") == "tire-size-calculator"
        title = "Tire Size Comparison" if tire else "Wheel Position Comparison"
        chart_title = "Calculated Dimensions" if tire else "Position Changes"
        aria = "Tire size comparison results" if tire else "Wheel offset comparison results"
        return f"""<section class="mortgage-dashboard generic-dashboard fitment-dashboard" aria-label="{aria}">
<div class="section-head stack"><h2>{title}</h2><p>Review the main fitment changes, supporting dimensions, and calculation details.</p></div>
<div class="summary-grid" id="genericSummary"></div>
	<div class="chart-grid"><div class="chart-card compact-chart"><h3>{chart_title}</h3><canvas id="genericChart" width="620" height="230" aria-label="{chart_title}" data-chart-type="bars"></canvas></div></div>
	<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
	</section>"""
    if calc.get("slug") == "payment-calculator":
        return """<section class="mortgage-dashboard generic-dashboard payment-dashboard" aria-label="Loan payment results">
<div class="section-head stack"><h2>Payment Results</h2><p>Review the payment, payoff time, borrowing cost, and month-by-month balance.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Principal and Interest</h3><canvas id="genericChart" width="620" height="190" aria-label="Principal, total interest, and monthly payment comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Monthly Amortization Schedule</h3><div class="table-scroll"><table class="data-table" id="paymentSchedule"><thead><tr><th>Month</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "interest-calculator":
        return """<section class="mortgage-dashboard generic-dashboard interest-compare-dashboard" aria-label="Simple and compound interest comparison">
<div class="section-head stack"><h2>Interest Comparison</h2><p>Compare ending balances, interest earned, and inflation-adjusted buying power.</p></div>
<div class="summary-grid" id="genericSummary"></div>
<div class="chart-grid"><div class="chart-card compact-chart"><h3>Balance Components</h3><canvas id="genericChart" width="620" height="230" aria-label="Simple and compound interest balance comparison" data-chart-type="bars"></canvas></div></div>
<div class="table-card"><h3>Calculation Details</h3><div class="table-scroll"><table class="data-table" id="genericTable"><thead><tr><th>Metric</th><th>Value</th><th>Note</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Annual Comparison</h3><div class="table-scroll"><table class="data-table" id="interestSchedule"><thead><tr><th>Period</th><th>Total contributed</th><th>Simple balance</th><th>Compound balance</th><th>Compound advantage</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
    if calc.get("slug") == "compound-interest-calculator":
        return """<section class="mortgage-dashboard compound-dashboard" aria-label="Compound interest result details">
<div class="section-head stack"><h2>Growth Summary</h2><p>Compare contributions, interest, taxes, and inflation-adjusted buying power.</p></div>
<div class="summary-grid" id="compoundSummary"></div>
<div class="chart-grid">
<div class="chart-card compact-chart"><h3>Balance Composition</h3><canvas id="compoundPie" width="360" height="190" aria-label="Principal, contributions, and net interest chart"></canvas></div>
<div class="chart-card compact-chart"><h3>Balance by Year</h3><canvas id="compoundLine" width="420" height="190" aria-label="Compound interest balance by year chart"></canvas></div>
</div>
<div class="table-card"><h3>Interest Rate Scenarios</h3><p class="table-note">A sensitivity range for planning, not a prediction of future returns.</p><div class="table-scroll"><table class="data-table" id="compoundScenarios"><thead><tr><th>Scenario</th><th>Annual rate</th><th>Ending balance</th><th>Net interest</th><th>Today's buying power</th></tr></thead><tbody></tbody></table></div></div>
<div class="table-card"><h3>Growth Schedule</h3><div class="table-scroll"><table class="data-table" id="compoundSchedule"><thead><tr><th>Period</th><th>Contributions</th><th>Gross interest</th><th>Est. tax</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
</section>"""
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
<div class="loan-result-panel is-active" id="monthlyfixedr"><div class="section-head stack"><h2>Amortized Loan Results</h2><p>Fixed payment, total payments, total interest, and amortization table.</p></div><div class="summary-grid" id="loanSummary"></div><div class="loan-chart-row"><div class="chart-card compact-chart"><h3>Principal vs Interest</h3><canvas id="loanPie" width="360" height="180" aria-label="Amortized loan principal and interest pie chart" data-center-label="total"></canvas></div><div class="table-card loan-result-table"><h3>Results</h3><div class="table-scroll"><table class="data-table" id="loanResultTable"><tbody></tbody></table></div><button class="text-link table-toggle" type="button" data-toggle-table="loanAmortTable">View Amortization Table</button></div></div><div class="table-card is-collapsed" id="loanAmortTable"><h3>Amortization Table</h3><div class="table-scroll"><table class="data-table"><thead><tr><th>Period</th><th>Payment</th><th>Principal</th><th>Interest</th><th>Balance</th></tr></thead><tbody id="loanAmortRows"></tbody></table></div></div></div>
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
    title = f"{shown_group} Calculators | NS Calculators"
    desc = f"Browse {len(items):,} {shown_group.lower()} calculators in the {cat.lower()} category."
    cards = "".join(card(c, c["cat"]) for c in items)
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/{slugify_cat(cat)}/">{h(cat)}</a> / {h(group)}</div>
<section class="article wide"><h1>{h(shown_group)} Calculators</h1><p class="lead">{h(desc)}</p><div class="tool-grid category-list">{cards}</div></section></div></main>"""
    return page(site, title, desc, subgroup_path(cat, group), body)


def calculator_page(site, calc, related):
    title = seo_title(calc)
    desc = seo_description(calc)
    group = calculator_group(calc)
    page_engine = calc.get("engine")
    if calc.get("slug") == "ratio-calculator":
        fields = ratio_input_html()
        page_engine = "ratio_advanced"
    elif calc.get("slug") == "debt-payoff-calculator":
        fields = debt_payoff_input_html()
        page_engine = "debt_payoff_advanced"
    elif calc.get("slug") in PRIORITY_LENGTH_CONVERSIONS:
        fields = priority_length_input_html(calc)
        page_engine = "length_convert"
    elif calc.get("slug") == "finance-calculator":
        fields = finance_tvm_input_html()
        page_engine = "finance_tvm"
    elif calc.get("slug") == "feet-to-meters-calculator":
        fields = feet_to_meters_input_html()
        page_engine = "feet_meters"
    elif calc.get("slug") == "payment-calculator":
        fields = payment_input_html()
        page_engine = "payment_advanced"
    elif calc.get("slug") == "amortization-calculator":
        fields = amortization_input_html()
        page_engine = "amortization_advanced"
    elif calc.get("slug") == "retirement-calculator":
        fields = retirement_input_html()
        page_engine = "retirement_advanced"
    elif calc.get("slug") == "401k-calculator":
        fields = k401_input_html()
        page_engine = "401k_advanced"
    elif calc.get("slug") == "social-security-calculator":
        fields = social_security_input_html()
        page_engine = "social_security_advanced"
    elif calc.get("slug") == "rmd-calculator":
        fields = rmd_input_html()
        page_engine = "rmd_advanced"
    elif calc.get("slug") == "interest-calculator":
        fields = compound_interest_input_html()
        page_engine = "interest_advanced"
    elif calc.get("slug") == "compound-interest-calculator":
        fields = compound_interest_input_html(include_scenarios=True)
    elif calc.get("slug") == "salary-increase-calculator":
        fields = salary_increase_input_html()
        page_engine = "salary_advanced"
    elif calc.get("slug") == "discount-calculator":
        fields = discount_input_html()
        page_engine = "discount_advanced"
    elif calc.get("slug") == "take-home-pay-calculator":
        fields = take_home_pay_input_html()
        page_engine = "take_home_pay"
    elif calc.get("slug") == "sales-tax-calculator":
        fields = sales_tax_input_html()
        page_engine = "sales_tax_advanced"
    elif calc.get("slug") == "percent-calculator":
        fields = percent_input_html()
        page_engine = "percent_advanced"
    elif calc.get("slug") == "fraction-calculator":
        fields = fraction_input_html()
        page_engine = "fraction_advanced"
    elif calc.get("slug") == "standard-deviation-calculator":
        fields = standard_deviation_input_html()
        page_engine = "stats_advanced"
    elif calc.get("slug") == "bmi-calculator":
        fields = bmi_input_html()
        page_engine = "bmi_advanced"
    elif calc.get("slug") == "salary-calculator":
        fields = salary_converter_input_html()
        page_engine = "salary_converter"
    elif calc.get("slug") == "truck-payload-calculator":
        fields = truck_payload_input_html()
    elif calc.get("slug") == "towing-capacity-calculator":
        fields = towing_capacity_input_html()
    elif calc.get("slug") == "mpg-calculator":
        fields = mpg_input_html()
        page_engine = "mpg_advanced"
    elif calc.get("slug") == "trip-fuel-cost-calculator":
        fields = trip_fuel_cost_input_html()
        page_engine = "fuel_cost_advanced"
    elif calc.get("slug") == "car-depreciation-calculator":
        fields = car_depreciation_input_html()
        page_engine = "car_depreciation_advanced"
    elif calc.get("slug") == "car-resale-value-calculator":
        fields = car_resale_input_html()
        page_engine = "car_resale_advanced"
    elif calc.get("slug") == "horsepower-calculator":
        fields = horsepower_input_html()
        page_engine = "horsepower_advanced"
    elif calc.get("slug") == "power-to-weight-ratio-calculator":
        fields = power_weight_input_html()
        page_engine = "power_weight_advanced"
    elif calc.get("slug") == "bottleneck-calculator":
        fields = bottleneck_input_html()
        page_engine = "bottleneck_advanced"
    elif calc.get("slug") == "car-trade-in-value-calculator":
        fields = trade_in_value_input_html()
        page_engine = "trade_in_estimate"
    elif calc.get("slug") == "used-car-value-calculator":
        fields = used_car_value_input_html()
        page_engine = "used_car_estimate"
    elif calc.get("slug") == "tire-size-calculator":
        fields = tire_size_input_html()
        page_engine = "tire_compare"
    elif calc.get("slug") == "wheel-offset-calculator":
        fields = wheel_offset_input_html()
        page_engine = "wheel_offset_compare"
    elif calc.get("slug") == "concrete-volume-calculator":
        fields = concrete_volume_input_html()
        page_engine = "concrete_advanced"
    elif calc.get("slug") == "roof-pitch-calculator":
        fields = roof_pitch_input_html()
        page_engine = "roof_pitch_advanced"
    elif calc.get("slug") == "rafter-length-calculator":
        fields = rafter_length_input_html()
        page_engine = "rafter_advanced"
    elif calc.get("slug") == "square-footage-calculator":
        fields = square_footage_input_html()
        page_engine = "square_footage_advanced"
    elif calc.get("slug") == "flooring-calculator":
        fields = flooring_input_html()
        page_engine = "flooring_advanced"
    elif calc.get("slug") == "tile-calculator":
        fields = tile_input_html()
        page_engine = "tile_advanced"
    elif calc.get("slug") == "deck-board-calculator":
        fields = deck_board_input_html()
        page_engine = "deck_advanced"
    elif calc.get("slug") == "board-foot-calculator":
        fields = board_foot_input_html()
        page_engine = "board_foot_advanced"
    elif calc.get("slug") == "voltage-drop-calculator":
        fields = voltage_drop_input_html()
        page_engine = "voltage_drop_advanced"
    elif calc.get("slug") == "wire-size-calculator":
        fields = wire_size_input_html()
        page_engine = "wire_size_advanced"
    elif calc.get("slug") == "breaker-size-calculator":
        fields = breaker_size_input_html()
        page_engine = "breaker_advanced"
    elif calc.get("slug") == "electrical-load-calculator":
        fields = electrical_load_input_html()
        page_engine = "electrical_load_advanced"
    elif calc.get("slug") == "watts-to-amps-calculator":
        fields = watts_to_amps_input_html()
        page_engine = "watts_amps_advanced"
    elif calc.get("slug") == "amps-to-watts-calculator":
        fields = amps_to_watts_input_html()
        page_engine = "amps_watts_advanced"
    elif calc.get("engine") == "cn_mortgage":
        fields = mortgage_input_html()
    elif calc.get("engine") == "loan_page":
        fields = loan_input_html()
    else:
        fields = f"""<div class="fields">{''.join(input_html(f) for f in calc["inputs"])}</div>"""
    rel = "".join(card(c, compact=True) for c in related)
    content = priority_length_copy(calc) or high_value_calculator_copy(calc) or conversion_copy(calc) or default_calculator_copy(calc)
    extra = analysis_extra_html(calc)
    calculator_asset_versions = {"amortization-calculator": "20260919b", "retirement-calculator": "20260919c", "401k-calculator": "20260920a", "social-security-calculator": "20260920b", "rmd-calculator": "20260920c", "feet-to-meters-calculator": "20260925a", "compound-interest-calculator": "20260925b"}
    calculator_asset_version = "20260925c" if calc.get("slug") in PRIORITY_LENGTH_CONVERSIONS else "20260925d" if calc.get("slug") in ("car-depreciation-calculator", "car-resale-value-calculator") else "20260925e" if calc.get("slug") in ("horsepower-calculator", "power-to-weight-ratio-calculator") else "20260925f" if calc.get("slug") == "bottleneck-calculator" else "20260925g" if calc.get("slug") == "ratio-calculator" else "20260925i" if calc.get("slug") == "debt-payoff-calculator" else calculator_asset_versions.get(calc.get("slug"), ASSET_VERSION)
    if calc.get("engine") == "loan_page":
        calc_html = f"""<section class="calc loan-page-calc"><h2>Calculator</h2>{fields}<div class="result" id="result">Enter your values and select Calculate.</div></section>"""
    else:
        calc_html = f"""<section class="calc"><h2>Calculator</h2>{fields}<div class="calc-actions"><button class="btn primary calc-btn" data-engine="{h(page_engine)}">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div><div class="result" id="result" aria-live="polite">Enter your values and select Calculate.</div></section>"""
    primary_tool = f"""<div class="calculator-layout split-analysis"><div class="calculator-pane">{calc_html}</div><div class="analysis-pane">{extra}</div></div>""" if extra else calc_html
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/{slugify_cat(calc['cat'])}/">{h(calc['cat'])}</a> / {h(display_group(group))} / {h(calc['title'])}</div>
<article class="article calculator-article"><span class="pill icon-pill">{category_icon(calc["cat"], "pill-icon")}{h(calc['cat'])} calculator</span><div class="page-title-icon">{category_icon(calc["cat"], "title-icon")}<h1>{h(calc['title'])}</h1></div><p class="lead">{h(calc['desc'])}</p>{opportunity_notice(calc)}{keyword_section(calc)}
{primary_tool}
<div class="prose">{content}</div>
<h2>Related calculators</h2><div class="related">{rel}</div></article></div></main><script src="/assets/calculator.js?v={calculator_asset_version}"></script>"""
    crumbs = [
        ("Home", "/"),
        (f"{calc['cat']} Calculators", f"/{slugify_cat(calc['cat'])}/"),
        (display_group(group), f"/{slugify_cat(calc['cat'])}/#{group_slug(group)}"),
        (calc["title"], f"/{calc['slug']}/"),
    ]
    return page(site, title, desc, f"/{calc['slug']}/", body, seo_keywords(calc), [breadcrumb_schema(site, crumbs), calculator_schema(site, calc)], indexable=is_indexable_calculator(calc))


def simple_page(site, path, title, desc, content):
    body = f"""<main class="main"><div class="wrap"><article class="article"><h1>{h(title)}</h1><p class="lead">{h(desc)}</p><div class="prose">{content}</div></article></div></main>"""
    return page(site, f"{title} | NS Calculators", desc, path, body)


def basic_calculator_page(site, calc, related):
    buttons = [
        ("MC", "memory-clear", "Clear memory", "memory"), ("MR", "memory-recall", "Recall memory", "memory"),
        ("M+", "memory-add", "Add result to memory", "memory"), ("M-", "memory-subtract", "Subtract result from memory", "memory"),
        ("AC", "clear", "Clear calculation", "utility"), ("Back", "backspace", "Delete the last character", "utility"),
        ("(", "insert", "Open parenthesis", "operator", "("), (")", "insert", "Close parenthesis", "operator", ")"),
        ("sqrt", "root", "Square root", "function"), ("x2", "square", "Square the current expression", "function"),
        ("1/x", "reciprocal", "Reciprocal", "function"), ("%", "percent", "Percent", "function"),
        ("7", "insert", "7", "number", "7"), ("8", "insert", "8", "number", "8"),
        ("9", "insert", "9", "number", "9"), ("divide", "insert", "Divide", "operator", "/"),
        ("4", "insert", "4", "number", "4"), ("5", "insert", "5", "number", "5"),
        ("6", "insert", "6", "number", "6"), ("multiply", "insert", "Multiply", "operator", "*"),
        ("1", "insert", "1", "number", "1"), ("2", "insert", "2", "number", "2"),
        ("3", "insert", "3", "number", "3"), ("minus", "insert", "Subtract", "operator", "-"),
        ("0", "insert", "0", "number", "0"), (".", "insert", "Decimal point", "number", "."),
        ("Ans", "answer", "Insert previous answer", "function"), ("plus", "insert", "Add", "operator", "+"),
        ("+/-", "negate", "Change sign", "utility"), ("=", "calculate", "Calculate result", "equals"),
    ]
    labels = {"sqrt": "&radic;", "x2": "x<sup>2</sup>", "divide": "&divide;", "multiply": "&times;", "minus": "&minus;", "plus": "+"}
    keypad = "".join(
        f'<button type="button" class="basic-key basic-key-{item[3]}" data-basic-action="{item[1]}"'
        f'{f" data-basic-value=\"{h(item[4])}\"" if len(item) > 4 else ""} aria-label="{h(item[2])}" title="{h(item[2])}">{labels.get(item[0], item[0])}</button>'
        for item in buttons
    )
    rel = "".join(card(c, compact=True) for c in related)
    content = """
<h2>How to use this basic calculator</h2><p>Type an expression with the on-screen keypad or your computer keyboard, then select the equals key or press Enter. The calculator handles addition, subtraction, multiplication, division, decimals, parentheses, percentages, square roots, squares, reciprocals, and negative numbers. Use Backspace to correct one character or AC to start over. Your previous answer remains available through the Ans key.</p>
<h2>Order of operations</h2><p>Calculations follow the standard order of operations. Parentheses are evaluated first, followed by exponents, multiplication and division, then addition and subtraction. Operations at the same level are worked from left to right. This means <code>2 + 3 * 4</code> equals 14, while <code>(2 + 3) * 4</code> equals 20.</p>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Key</th><th>Operation</th><th>Example</th><th>Result</th></tr></thead><tbody><tr><td>+</td><td>Addition</td><td>18 + 7</td><td>25</td></tr><tr><td>&minus;</td><td>Subtraction</td><td>18 &minus; 7</td><td>11</td></tr><tr><td>&times;</td><td>Multiplication</td><td>18 &times; 7</td><td>126</td></tr><tr><td>&divide;</td><td>Division</td><td>18 &divide; 6</td><td>3</td></tr><tr><td>&radic;</td><td>Square root</td><td>&radic;81</td><td>9</td></tr><tr><td>x<sup>2</sup></td><td>Square</td><td>12<sup>2</sup></td><td>144</td></tr><tr><td>1/x</td><td>Reciprocal</td><td>1/8</td><td>0.125</td></tr></tbody></table></div>
<h2>How the percent key works</h2><p>The percent key uses familiar everyday calculator behavior. A percentage entered after addition or subtraction is based on the value before the operator: <code>200 + 10%</code> returns 220, and <code>200 - 10%</code> returns 180. After multiplication or division, the percentage is converted to a decimal: <code>200 * 10%</code> returns 20. A percentage entered by itself is divided by 100, so 15% becomes 0.15.</p>
<h2>Memory keys</h2><p>Memory is useful when several calculations share the same subtotal. M+ adds the displayed result to memory, while M- subtracts it. MR inserts the stored number into the expression, and MC resets memory to zero. The memory indicator above the display shows whether a value is stored. Clearing the current expression does not clear memory.</p>
<h2>Keyboard shortcuts</h2><p>Number keys, parentheses, the decimal point, and the operators <code>+</code>, <code>-</code>, <code>*</code>, and <code>/</code> work directly. Press Enter to calculate, Backspace to remove the last character, and Escape to clear the current calculation. Keyboard support makes the tool practical for repeated totals and quick checks without moving between the keyboard and pointer.</p>
<h2>Calculation history and privacy</h2><p>The history panel keeps the latest ten calculations during the current page session. Select a previous row to reuse its expression, or clear the list when it is no longer needed. Inputs and calculations run locally in your browser; this calculator does not require an account or send the arithmetic expression to a calculation server.</p>
<h2>Accuracy and limitations</h2><p>Results are displayed with up to 14 significant digits. Repeating decimals and very large or very small values can be rounded for display because browser calculations use finite numeric precision. Division by zero, a square root of a negative real number, or an incomplete expression produces a clear error instead of a misleading numeric answer. For accounting, tax, engineering, or other regulated work, confirm rounding rules and requirements that apply to your use case.</p>
<h2>Frequently asked questions</h2><h3>Can I use parentheses?</h3><p>Yes. Parentheses change the order of operations and can be nested in ordinary arithmetic expressions.</p><h3>Does AC erase calculator memory?</h3><p>No. AC clears the expression and displayed answer, while Ans still recalls the last completed calculation. Use MC when you want to erase the separate memory value.</p><h3>Why does 0.1 + 0.2 sometimes show rounding effects?</h3><p>Computers store many decimal fractions as binary approximations. The display rounds ordinary results to a practical number of significant digits, but extremely precise decimal work may require a dedicated arbitrary-precision tool.</p><h3>Is this a scientific calculator?</h3><p>No. This page is designed for everyday arithmetic. Use the <a href="/scientific-calculator/">scientific calculator</a> for trigonometry, logarithms, factorials, constants, and degree or radian modes.</p>
"""
    crumbs = [
        ("Home", "/"), ("Math Calculators", "/math-calculators/"),
        (display_group(calculator_group(calc)), f"/math-calculators/#{group_slug(calculator_group(calc))}"),
        (calc["title"], f"/{calc['slug']}/"),
    ]
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/math-calculators/">Math</a> / {h(calc['title'])}</div>
<article class="article calculator-article basic-article"><span class="pill icon-pill">{category_icon(calc["cat"], "pill-icon")}Math calculator</span><div class="page-title-icon">{category_icon(calc["cat"], "title-icon")}<h1>{h(calc['title'])}</h1></div><p class="lead">{h(calc['desc'])}</p>
<div class="basic-layout"><section class="calc basic-calculator" aria-labelledby="basic-tool-title"><div class="basic-toolbar"><h2 id="basic-tool-title">Calculator</h2><span id="basicMemory" class="basic-memory" aria-live="polite">Memory: empty</span></div><label class="basic-expression-label" for="basicExpression">Expression</label><input class="basic-expression" id="basicExpression" value="" inputmode="decimal" autocomplete="off" spellcheck="false" placeholder="0" aria-describedby="basicStatus"><div class="basic-output" aria-live="polite"><span>Answer</span><strong id="basicResult">0</strong><small id="basicStatus">Ready</small></div><div class="basic-keypad" aria-label="Basic calculator keypad">{keypad}</div></section>
<aside class="basic-history" aria-labelledby="basic-history-title"><div class="basic-history-head"><div><h2 id="basic-history-title">History</h2><p>Latest 10 calculations</p></div><button type="button" data-basic-action="history-clear">Clear</button></div><ol id="basicHistory"><li class="basic-history-empty">Your calculations will appear here.</li></ol></aside></div>
<div class="prose">{content}</div><h2>Related calculators</h2><div class="related">{rel}</div></article></div></main><script src="/assets/mathjs.min.js?v=20260925h" defer></script><script src="/assets/basic-calculator.js?v=20260925h" defer></script>"""
    return page(site, seo_title(calc), seo_description(calc), f"/{calc['slug']}/", body, seo_keywords(calc), [breadcrumb_schema(site, crumbs), calculator_schema(site, calc)], indexable=is_indexable_calculator(calc))


def scientific_page(site):
    description = "Use a free scientific calculator with DEG and RAD modes, trigonometry, logarithms, powers, roots, factorials, memory, Ans, and calculation history."
    buttons = [
        ("MC", "memory-clear", "Clear memory", "memory"), ("MR", "memory-recall", "Recall memory", "memory"),
        ("M+", "memory-add", "Add result to memory", "memory"), ("M-", "memory-subtract", "Subtract result from memory", "memory"),
        ("AC", "clear", "Clear expression", "utility"), ("⌫", "backspace", "Delete the last character", "utility"),
        ("sin", "insert", "Insert sine", "function", "sin("), ("cos", "insert", "Insert cosine", "function", "cos("),
        ("tan", "insert", "Insert tangent", "function", "tan("), ("sin⁻¹", "insert", "Insert inverse sine", "function", "asin("),
        ("cos⁻¹", "insert", "Insert inverse cosine", "function", "acos("), ("tan⁻¹", "insert", "Insert inverse tangent", "function", "atan("),
        ("log", "insert", "Insert base-10 logarithm", "function", "log("), ("ln", "insert", "Insert natural logarithm", "function", "ln("),
        ("√", "insert", "Insert square root", "function", "sqrt("), ("x²", "square", "Square the expression", "function"),
        ("xʸ", "insert", "Insert exponent operator", "function", "^"), ("1/x", "reciprocal", "Take the reciprocal", "function"),
        ("7", "insert", "7", "number", "7"), ("8", "insert", "8", "number", "8"), ("9", "insert", "9", "number", "9"),
        ("÷", "insert", "Divide", "operator", "/"), ("(", "insert", "Open parenthesis", "operator", "("), (")", "insert", "Close parenthesis", "operator", ")"),
        ("4", "insert", "4", "number", "4"), ("5", "insert", "5", "number", "5"), ("6", "insert", "6", "number", "6"),
        ("×", "insert", "Multiply", "operator", "*"), ("π", "insert", "Pi", "function", "pi"), ("e", "insert", "Euler's number", "function", "e"),
        ("1", "insert", "1", "number", "1"), ("2", "insert", "2", "number", "2"), ("3", "insert", "3", "number", "3"),
        ("−", "insert", "Subtract", "operator", "-"), ("x!", "insert", "Factorial", "function", "!"), ("%", "percent", "Convert to percent", "function"),
        ("0", "insert", "0", "number", "0"), (".", "insert", "Decimal point", "number", "."), ("Ans", "insert", "Previous answer", "function", "ans"),
        ("+", "insert", "Add", "operator", "+"), ("±", "negate", "Change sign", "utility"), ("=", "calculate", "Calculate result", "equals"),
    ]
    keypad = "".join(
        f'<button type="button" class="sci-key sci-key-{item[3]}" data-sci-action="{item[1]}"'
        f'{f" data-sci-value=\"{h(item[4])}\"" if len(item) > 4 else ""} aria-label="{h(item[2])}" title="{h(item[2])}">{item[0]}</button>'
        for item in buttons
    )
    software = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Scientific Calculator",
        "applicationCategory": "CalculatorApplication",
        "operatingSystem": "Any",
        "url": site_url(site, "/scientific-calculator/"),
        "description": description,
        "creator": {"@id": site_url(site, "/#organization")},
        "isAccessibleForFree": True,
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "featureList": ["Degree and radian modes", "Trigonometric functions", "Logarithms and roots", "Memory and previous answer", "Calculation history"],
    }
    crumbs = breadcrumb_schema(site, [("Home", "/"), ("Math Calculators", "/math-calculators/"), ("Scientific Calculator", "/scientific-calculator/")])
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/math-calculators/">Math</a> / Scientific Calculator</div>
<article class="article calculator-article scientific-article"><span class="pill icon-pill">{category_icon("Math", "pill-icon")}Math calculator</span><div class="page-title-icon">{category_icon("Math", "title-icon")}<h1>Scientific Calculator</h1></div><p class="lead">Evaluate arithmetic, trigonometry, logarithms, powers, roots, factorials, and percentages with degree or radian angle modes.</p>
<section class="calc scientific-page" aria-labelledby="scientific-tool-title"><div class="sci-toolbar"><h2 id="scientific-tool-title">Calculator</h2><div class="sci-angle-toggle" role="group" aria-label="Angle mode"><button type="button" class="is-active" data-angle-mode="deg" aria-pressed="true">DEG</button><button type="button" data-angle-mode="rad" aria-pressed="false">RAD</button></div></div>
<label class="sci-expression-label" for="sciExpression">Expression</label><input class="sci-expression" id="sciExpression" value="sqrt(144) + 25 / 100" inputmode="text" autocomplete="off" spellcheck="false" aria-describedby="sciStatus">
<div class="sci-output" aria-live="polite"><span>Result</span><strong id="sciResult">12.25</strong><small id="sciStatus">Ready in degree mode</small></div>
<div class="sci-keypad" aria-label="Scientific calculator keypad">{keypad}</div>
<div class="sci-history"><div class="sci-history-head"><h3>Calculation history</h3><button type="button" class="sci-history-clear" data-sci-action="history-clear">Clear history</button></div><ol id="sciHistory"><li class="sci-history-empty">Your calculations will appear here.</li></ol></div></section>
<div class="prose">
<h2>How to use this scientific calculator</h2><p>Enter an expression with the keypad or your keyboard, then select equals or press Enter. Parentheses control the order of operations. The caret symbol raises a value to a power, so <code>2^8</code> equals 256. Use <code>sqrt()</code> for square roots, <code>log()</code> for base-10 logarithms, and <code>ln()</code> for natural logarithms. The previous result is stored as <code>Ans</code> until the page is refreshed.</p>
<h2>Degrees and radians</h2><p>DEG mode interprets trigonometric inputs as degrees and returns inverse-trigonometric results in degrees. For example, <code>sin(30)</code> equals 0.5 in DEG mode. RAD mode uses radians, so <code>sin(pi/6)</code> equals 0.5. The selected mode affects sin, cos, tan, asin, acos, and atan; it does not change ordinary arithmetic.</p>
<h2>Supported functions and operators</h2><div class="table-scroll"><table class="data-table"><thead><tr><th>Type</th><th>Syntax</th><th>Example</th></tr></thead><tbody><tr><td>Arithmetic</td><td>+ − × ÷ and parentheses</td><td><code>(18 + 6) / 4 = 6</code></td></tr><tr><td>Powers and roots</td><td>^, sqrt(), x², 1/x</td><td><code>sqrt(81) + 3^2 = 18</code></td></tr><tr><td>Trigonometry</td><td>sin, cos, tan, asin, acos, atan</td><td><code>cos(60) = 0.5</code> in DEG mode</td></tr><tr><td>Logarithms</td><td>log, ln, exp</td><td><code>log(1000) = 3</code></td></tr><tr><td>Other</td><td>!, abs, floor, ceil, round, min, max, mod</td><td><code>5! = 120</code></td></tr><tr><td>Constants</td><td>pi, e, Ans</td><td><code>2 * pi ≈ 6.28319</code></td></tr></tbody></table></div>
<h2>Percent calculations</h2><p>The percent key wraps the current expression and divides it by 100. To find 15% of 240, enter <code>240 * 15%</code>, which returns 36. To increase 80 by 25%, enter <code>80 * (1 + 25%)</code>, which returns 100. This explicit notation avoids ambiguity about whether a percentage should be added, subtracted, or multiplied.</p>
<h2>Memory and history</h2><p>M+ adds the current numeric result to memory, M− subtracts it, MR inserts the stored value, and MC clears memory. The history list keeps the latest eight calculations for the current page session. Select a previous calculation to place its expression back in the input. Nothing is sent to a server for calculation.</p>
<h2>Precision and limitations</h2><p>Results use JavaScript number precision and are displayed with up to 14 significant digits. Very large factorials, values near trigonometric discontinuities, and repeated operations can show rounding effects. The calculator limits expression length and accepts a defined set of numeric functions. It is intended for everyday, classroom, and planning calculations, not for proofs or safety-critical engineering work.</p>
<h2>Frequently asked questions</h2><h3>Why does sin(30) change between DEG and RAD?</h3><p>The number 30 represents 30 degrees in DEG mode but 30 radians in RAD mode. Choose the unit used by the problem before evaluating a trigonometric expression.</p><h3>What is the difference between log and ln?</h3><p>Log uses base 10, while ln uses base e. Therefore <code>log(100)</code> is 2, and <code>ln(e)</code> is 1.</p><h3>Can this calculator use scientific notation?</h3><p>Yes. Enter values such as <code>6.02e23</code> or <code>1.5e-6</code>. The constant e is also available by itself as Euler's number.</p><h3>How do I calculate a factorial?</h3><p>Place an exclamation mark after a nonnegative integer, such as <code>7!</code>. Large factorials can exceed the range of ordinary JavaScript numbers.</p>
<h2>Related calculators</h2><p>Use the <a href="/fraction-calculator/">fraction calculator</a> for exact fraction arithmetic, the <a href="/percent-calculator/">percent calculator</a> for common percentage questions, or the <a href="/standard-deviation-calculator/">standard deviation calculator</a> for a data set.</p>
</div></article></div></main><script src="/assets/mathjs.min.js?v={ASSET_VERSION}" defer></script><script src="/assets/scientific.js?v={ASSET_VERSION}" defer></script>"""
    return page(site, "Scientific Calculator: DEG, RAD, Trig & Logs", description, "/scientific-calculator/", body, ["scientific calculator", "online scientific calculator", "degree mode calculator", "radian calculator", "trigonometry calculator"], [crumbs, software])


def redirect_page(site, from_path, to_path, title):
    return f"""<!doctype html><html lang="{h(site['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta http-equiv="refresh" content="0; url={h(to_path)}"><link rel="canonical" href="{h(site_url(site, to_path))}"></head><body><p><a href="{h(to_path)}">Continue to {h(title)}</a></p></body></html>"""


def info_pages(site):
    about = simple_page(site, "/about/", "About NS Calculators", "NS Calculators publishes practical, browser-based calculators and unit converters for everyday questions.", """
<h2>What we publish</h2><p>NS Calculators is a free calculator library for users who need quick estimates, unit conversions, formulas, and examples. The site includes automotive, construction, conversion, cooking, electrical, financial, health, math, pets, science, time and date, and video tools.</p>
<h2>Our editorial approach</h2><p>Pages are built around a clear user task. Each calculator includes a visible formula or conversion factor, a worked example, and related tools so users can continue researching a topic without guessing what to open next.</p>
<h2>Important limitations</h2><p>Calculator results are planning aids. They are not financial, legal, medical, engineering, electrical, construction, automotive, or safety advice. Always verify important decisions with qualified professionals, manufacturers, official standards, or other authoritative sources.</p>
""")
    privacy = simple_page(site, "/privacy-policy/", "Privacy Policy", "This Privacy Policy explains how NS Calculators handles information when you use the website.", """
<h2>Information you enter</h2><p>Calculator inputs are processed in your browser for the purpose of showing a result. The static calculator pages do not require account registration.</p>
<h2>Usage data</h2><p>Like many websites, hosting providers, analytics tools, or advertising partners may process basic technical information such as page URL, browser type, device type, approximate location, referring page, and interaction data.</p>
<h2>Cookies and advertising</h2><p>NS Calculators may use cookies or similar technologies for analytics, site performance, advertising measurement, and ad personalization where allowed by law. Third-party advertising partners, including Google, may use cookies to serve ads based on a user's visits to this and other websites.</p>
<h2>Your choices</h2><p>You can control cookies through your browser settings. You can also review Google's advertising settings and choices through Google's own privacy and ads controls.</p>
<h2>Children's privacy</h2><p>This website is intended for a general audience and is not designed to collect personal information from children.</p>
<h2>Contact</h2><p>Questions about this policy can be sent through the contact page.</p>
""")
    terms = simple_page(site, "/terms/", "Terms of Use", "These Terms of Use describe the rules for using NS Calculators.", """
<h2>Use of the site</h2><p>You may use the calculators and converters for personal, educational, and general planning purposes. You agree not to misuse the site, interfere with its operation, or attempt to access systems without permission.</p>
<h2>No professional advice</h2><p>Results are estimates based on the values entered and the assumptions shown. The site does not provide professional advice. Verify financial, health, construction, electrical, vehicle, legal, and safety-related decisions with appropriate professionals or official sources.</p>
<h2>Accuracy</h2><p>We aim to provide useful formulas, conversion factors, and examples, but errors or omissions may occur. We do not guarantee that every result is complete, current, or suitable for your specific situation.</p>
<h2>Advertising and third-party links</h2><p>The site may display advertisements or link to third-party resources. We are not responsible for third-party websites, services, claims, or policies.</p>
<h2>Changes</h2><p>We may update these terms as the site changes. Continued use of the site means you accept the current terms.</p>
""")
    contact = simple_page(site, "/contact/", "Contact", "Contact NS Calculators about calculator issues, corrections, privacy questions, or general feedback.", """
<h2>How to reach us</h2><p>For corrections, feedback, privacy questions, or general inquiries, open an issue in the public project repository: <a href="https://github.com/lg-list/NSCalculators/issues">NS Calculators issues</a>.</p>
<h2>What to include</h2><p>Please include the calculator URL, the values you entered, the result you expected, and any authoritative source that supports the correction. This helps us review issues faster.</p>
<h2>Advertising and partnerships</h2><p>For advertising, partnership, or business inquiries, use the same project issue tracker and include a clear subject line.</p>
""")
    return {"/about/": about, "/privacy-policy/": privacy, "/terms/": terms, "/contact/": contact}


CSS = r'''
:root{--ink:#152033;--muted:#667085;--subtle:#8b96a8;--line:#dfe5ee;--bg:#f6f8fb;--card:#fff;--card-2:#f1f5fb;--brand:#173f73;--brand-dark:#0f2d55;--accent:#c0333a;--accent-muted:#8a3f47;--accent-soft:#fff3f4;--accent-line:#f0c8cd;--soft:#edf3fb;--shadow:0 18px 50px rgba(21,32,51,.10)}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;font-family:Arial,"Helvetica Neue",ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}a{color:inherit;text-decoration:none}.wrap{width:min(1180px,calc(100% - 32px));margin:auto}
.site-header{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.96);border-bottom:1px solid var(--line);backdrop-filter:blur(16px)}.nav{min-height:68px;height:auto;padding:9px 0;display:flex;align-items:center;justify-content:space-between;gap:18px}.brand{display:inline-flex;align-items:center;gap:9px;font-size:18px;font-weight:850;letter-spacing:-.03em;white-space:nowrap}.brand-name{display:grid;gap:0;line-height:1.02}.brand-name strong{font-size:22px;color:var(--brand);letter-spacing:-.045em}.brand-name b{font-size:12px;color:var(--accent);letter-spacing:.025em}.brand b{color:var(--accent)}.brand-mark{display:inline-grid;place-items:center;width:38px;height:40px;border-radius:0;background:transparent;box-shadow:none;color:var(--brand)}.brand-mark svg{width:36px;height:36px;fill:none;stroke:currentColor;filter:drop-shadow(0 5px 8px rgba(23,63,115,.22))}.brand-mark circle{fill:var(--accent)}.navlinks{display:flex;align-items:center;justify-content:flex-end;gap:6px;color:var(--muted);font-size:13px;white-space:nowrap;flex-wrap:wrap}.category-nav-link{display:inline-flex;align-items:center;gap:6px;min-height:34px;padding:6px 8px;border:1px solid transparent;border-radius:9px;color:#344054;font-weight:800;line-height:1}.category-nav-link:hover{background:var(--accent-soft);border-color:var(--accent-line);color:var(--accent)}.category-nav-link .nav-icon{width:18px;height:18px}.menu-group{position:relative}.menu-top{display:inline-flex;align-items:center;height:38px;padding:0 9px;border-radius:9px}.menu-top:after{content:"";width:0;height:0;margin-left:6px;border-left:4px solid transparent;border-right:4px solid transparent;border-top:5px solid #8b96a8}.menu-group:hover .menu-top,.menu-top:focus{background:var(--soft);color:var(--brand)}.submenu{position:absolute;top:100%;left:0;min-width:210px;padding:8px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:var(--shadow);display:none}.menu-group:hover .submenu,.menu-group:focus-within .submenu{display:grid;gap:2px}.submenu a{display:block;padding:9px 10px;border-radius:8px;color:#344054}.submenu a:hover{background:var(--soft);color:var(--brand)}.navlinks a:hover,.text-link:hover{color:var(--accent)}
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
.brand-mark svg{width:36px;height:36px;fill:none;stroke:var(--brand);stroke-width:2.8;stroke-linecap:round;stroke-linejoin:round}.brand-mark rect{fill:rgba(232,240,251,.75);stroke:var(--brand)}.brand-mark .logo-screen{stroke:#0f2d55;stroke-width:3.1}.brand-mark .logo-accent{stroke:var(--accent);stroke-width:4}.navlinks{display:flex!important}.category-nav-link span{font-size:13px}.all-calculators-menu .menu-top{font-size:15px;font-weight:850;color:var(--ink);padding:0 13px}.all-calculators-menu .submenu{left:auto;right:0;width:min(480px,calc(100vw - 32px));grid-template-columns:repeat(3,1fr);gap:6px;padding:12px}.all-calculators-menu:hover .submenu,.all-calculators-menu:focus-within .submenu{display:grid}.mega-menu a.category-nav-link{display:flex;align-items:center;min-height:40px;padding:9px 10px}.mega-menu a.category-nav-link span{font-size:14px;font-weight:800;color:#27364b;line-height:1.2}.mega-menu a.category-nav-link:hover span{color:var(--accent)}
.category-directory .lead{margin-bottom:18px}.category-jump-nav{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 22px}.category-jump-nav a{display:inline-flex;align-items:center;gap:7px;min-height:34px;padding:6px 10px;background:#fff;border:1px solid var(--line);border-radius:9px;color:#344054;font-size:13px;font-weight:760}.category-jump-nav a:hover{border-color:#b8c7d8;color:var(--brand);background:var(--soft)}.jump-icon{width:18px;height:18px;border-radius:5px;background:transparent}.jump-icon svg{width:14px;height:14px;stroke-width:2.35}.category-tools{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:18px}.category-section{padding:16px;border-radius:12px}.category-section-head{grid-template-columns:34px minmax(0,1fr);gap:10px;margin-bottom:12px}.section-icon{width:34px;height:34px;border-radius:9px}.section-icon svg{width:19px;height:19px}.category-section h2{font-size:21px;margin-bottom:3px}.category-section p{font-size:14px;line-height:1.45}.calculator-link-grid{grid-template-columns:1fr;gap:8px}.calculator-link-grid a{min-height:42px;padding:8px 10px;border-radius:8px;font-size:13px;font-weight:720}.link-icon{width:18px;height:18px}.link-icon svg{width:13px;height:13px}
.lead,.home-hero p,.section-head p,.home-block p,.browse-panel p,.scientific-panel p,.category-section p,.faq-item p,.tool-card p,.method-card p{color:#5f6d80}.home-category small,.popular-list small,.search-results small,.mega-menu a small{color:#778295}.cat-icon,.category-icon{background:linear-gradient(135deg,#f3f7fc,#fff);color:var(--brand);box-shadow:inset 0 0 0 1px rgba(23,63,115,.09)}.cat-icon svg>*:last-child{stroke:var(--accent)}.nav-icon,.pill-icon,.jump-icon,.link-icon{background:transparent;box-shadow:none}.link-icon,.jump-icon{color:var(--brand)}.category-card span:not(.cat-icon){color:var(--brand)}.brand-name b{color:var(--accent)}.menu-group:hover .menu-top,.submenu a:hover,.sci-keypad button:hover{background:var(--accent-soft);color:var(--accent)}.category-jump-nav a:hover,.calculator-link-grid a:hover,.home-category:hover,.popular-list a:hover{border-color:var(--accent-line)}.result,.mini-result{background:#fff7f8;border-color:var(--accent-line)}.formula{border-left-color:var(--accent)}
.category-directory .calculator-link-grid a{display:block;min-height:auto;padding:9px 10px;line-height:1.32;overflow-wrap:anywhere}
.mortgage-dashboard{margin:10px 0 42px}.summary-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:16px 0 18px}.summary-card{background:#fff;border:1px solid var(--line);border-radius:12px;padding:14px}.summary-card span{display:block;color:#667085;font-size:12px;font-weight:760}.summary-card strong{display:block;margin-top:5px;color:var(--ink);font-size:22px;line-height:1.15}.summary-card small{display:block;margin-top:5px;color:#778295;line-height:1.35}.chart-grid{display:grid;grid-template-columns:minmax(260px,1fr) minmax(320px,1.3fr);gap:14px}.chart-card,.table-card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:16px;box-shadow:0 10px 28px rgba(21,32,51,.05)}.chart-card h3,.table-card h3{margin:0 0 12px;font-size:18px}.chart-card canvas{display:block;max-width:100%;height:auto;margin:0 auto}.table-card{margin-top:14px}.table-scroll{overflow:auto}.data-table{width:100%;border-collapse:collapse;font-size:13px}.data-table th,.data-table td{padding:10px 11px;border-bottom:1px solid var(--line);text-align:right;white-space:nowrap}.data-table th:first-child,.data-table td:first-child{text-align:left}.data-table th{color:#344054;background:#f8fafc;font-weight:850}.data-table td{color:#344054}
.calculator-article{max-width:960px}.calculator-article .pill{font-size:12px;padding:5px 9px;margin-bottom:10px}.calculator-article .pill-icon{width:16px;height:16px}.calculator-article .page-title-icon{gap:10px;margin-bottom:6px}.calculator-article .title-icon{width:42px;height:42px;border-radius:11px}.calculator-article .title-icon svg{width:23px;height:23px}.calculator-article h1{font-size:clamp(30px,4vw,44px);margin:0}.calculator-article .lead{font-size:16px;line-height:1.5;max-width:760px;margin:0 0 14px}.calculator-article .notice{margin:10px 0;padding:10px 12px}.calculator-article .calc{margin:14px 0 24px;padding:18px;border-radius:14px}.calculator-article .calc h2{font-size:22px;margin:0 0 12px;letter-spacing:-.02em}.calculator-article .fields{gap:10px}.calculator-article .field label{margin-bottom:5px}.calculator-article .field input,.calculator-article .field select{height:42px;border-radius:9px}.calculator-article .calc-btn{margin-top:12px}.calculator-article .result{margin-top:12px;padding:14px}.calculator-article .result strong{font-size:22px}.calculator-article .mortgage-dashboard{margin-top:6px}
.calculator-article:has(.split-analysis){max-width:none}.calculator-layout.split-analysis{display:grid;grid-template-columns:minmax(300px,380px) minmax(0,1fr);gap:18px;align-items:start;margin:14px 0 28px}.calculator-pane{position:sticky;top:88px}.calculator-pane .calc{margin:0}.analysis-pane .mortgage-dashboard{margin:0}.analysis-pane .section-head.stack{margin-bottom:12px}.analysis-pane .section-head h2{font-size:24px;margin-bottom:6px}.analysis-pane .summary-grid{grid-template-columns:repeat(2,1fr);margin:12px 0 14px}.analysis-pane .chart-grid{grid-template-columns:1fr;gap:12px}.analysis-pane .chart-card,.analysis-pane .table-card{padding:14px}.analysis-pane .chart-card canvas{max-height:none}.analysis-pane .data-table th,.analysis-pane .data-table td{padding:8px 9px}
.calculator-article:has(#mortgageSummary) .calculator-layout.split-analysis{grid-template-columns:minmax(400px,470px) minmax(0,1fr);gap:16px}.calculator-article:has(#mortgageSummary) .calc{padding:14px}.calculator-article:has(#mortgageSummary) .calc h2{font-size:20px;margin-bottom:10px}.calculator-article:has(#mortgageSummary) .fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.calculator-article:has(#mortgageSummary) .field label{font-size:12px;margin-bottom:3px}.calculator-article:has(#mortgageSummary) .field input,.calculator-article:has(#mortgageSummary) .field select{height:36px;padding:0 10px;font-size:14px}.calculator-article:has(#mortgageSummary) .calc-btn{min-height:38px;margin-top:10px;padding:9px 14px}.calculator-article:has(#mortgageSummary) .result{padding:10px 12px;margin-top:10px;font-size:13px}.calculator-article:has(#mortgageSummary) .result strong{font-size:20px}.calculator-article:has(#mortgageSummary) .analysis-pane .section-head h2{font-size:21px}.calculator-article:has(#mortgageSummary) .analysis-pane .section-head p{font-size:13px;line-height:1.35}.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:8px 0 10px}.calculator-article:has(#mortgageSummary) .summary-card{padding:10px;border-radius:10px}.calculator-article:has(#mortgageSummary) .summary-card strong{font-size:17px}.calculator-article:has(#mortgageSummary) .summary-card small{font-size:11px;line-height:1.25}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-card,.calculator-article:has(#mortgageSummary) .analysis-pane .table-card{padding:10px;border-radius:10px}.calculator-article:has(#mortgageSummary) .chart-card h3,.calculator-article:has(#mortgageSummary) .table-card h3{font-size:15px;margin-bottom:8px}.calculator-article:has(#mortgageSummary) .compact-chart canvas{max-height:230px}.calculator-article:has(#mortgageSummary) .table-card{margin-top:10px}.calculator-article:has(#mortgageSummary) .data-table{font-size:12px}.calculator-article:has(#mortgageSummary) .data-table th,.calculator-article:has(#mortgageSummary) .data-table td{padding:6px 7px}
.calculator-article .result{background:linear-gradient(135deg,#0f2d55,#173f73);border-color:#0f2d55;color:#e8f1ff;box-shadow:0 14px 32px rgba(15,45,85,.22)}.calculator-article .result strong{display:block;color:#fff;font-size:clamp(28px,3.2vw,36px);line-height:1.05;letter-spacing:-.035em;margin-bottom:5px}.calculator-article:has(#mortgageSummary) .result{padding:14px 16px;margin-top:10px;border-radius:12px;font-size:14px;line-height:1.45}.calculator-article:has(#mortgageSummary) .result strong{font-size:30px;line-height:1}
.calculator-article .field label,.calculator-article .field input,.calculator-article .field select{font-size:16px}
.input-unit{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;border:1px solid #cfd7e4;border-radius:9px;background:#fff;overflow:hidden}.input-unit input,.input-unit select{border:0!important;border-radius:0!important;height:42px!important}.input-unit input{min-width:0}.input-unit select,.input-unit span{height:42px;display:grid;place-items:center;border-left:1px solid #dfe5ee;background:#f8fafc;color:#344054;padding:0 10px;font-weight:760}.input-unit select{min-width:72px}.field-wide{grid-column:1/-1}.is-hidden{display:none!important}.checkline{display:flex!important;align-items:center;gap:10px;min-height:42px;margin:0!important;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#f8fafc;color:var(--ink);font-size:16px!important}.checkline input{width:18px;height:18px;accent-color:var(--brand)}.mortgage-cost-fields[hidden],.mortgage-cost-fields.is-hidden{display:none!important}.calculator-article:has(#mortgageSummary) .field label{font-size:16px;margin-bottom:4px}.calculator-article:has(#mortgageSummary) .field input,.calculator-article:has(#mortgageSummary) .field select{font-size:16px}.calculator-article:has(#mortgageSummary) .field>input,.calculator-article:has(#mortgageSummary) .field>select{height:42px;padding:0 10px}.calculator-article:has(#mortgageSummary) .mortgage-fields{gap:9px;margin-top:9px}.calculator-article:has(#mortgageSummary) .mortgage-fields:first-child{margin-top:0}
.calc-actions{display:flex;gap:10px;align-items:center;margin-top:14px}.calc-actions .calc-btn{margin-top:0;flex:1}.clear-btn{min-width:92px}.more-options{margin-top:10px;border:1px solid var(--line);border-radius:10px;background:#fff}.more-options summary{min-height:42px;display:flex;align-items:center;padding:0 12px;cursor:pointer;color:var(--brand);font-size:16px;font-weight:850}.more-options summary::marker{color:var(--accent)}.more-options .mortgage-fields{padding:0 12px 12px}.calculator-article:has(#mortgageSummary) .calc-actions{margin-top:10px}.calculator-article:has(#mortgageSummary) .calc-actions .calc-btn,.calculator-article:has(#mortgageSummary) .clear-btn{min-height:42px;font-size:16px;padding:9px 14px}
.loan-mode-tabs{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:6px;margin-bottom:10px;padding:4px;border:1px solid var(--line);border-radius:10px;background:#edf2f7}.loan-mode-tabs button{min-height:38px;border:0;border-radius:7px;background:transparent;color:#475467;font:800 14px/1 system-ui,sans-serif;cursor:pointer}.loan-mode-tabs button.is-active{background:#fff;color:var(--brand);box-shadow:0 2px 8px rgba(21,32,51,.12)}.loan-mode-stack{display:grid;gap:12px}.loan-mode-input{display:none;padding:12px;border:1px solid var(--line);border-radius:12px;background:#f8fafc}.loan-mode-input.is-active{display:block}.loan-mode-input h3{margin:0 0 4px;font-size:18px;letter-spacing:-.015em}.loan-mode-input p{margin:0 0 10px;color:var(--muted);font-size:13px;line-height:1.35}.loan-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.loan-results{display:grid;gap:14px}.loan-result-panel{display:none;background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:0 10px 28px rgba(21,32,51,.05)}.loan-result-panel.is-active{display:block}.loan-result-panel .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 12px}.loan-chart-row{display:grid;grid-template-columns:minmax(260px,.9fr) minmax(260px,1fr);gap:12px;align-items:start}.loan-result-table{margin-top:0}.table-toggle{margin-top:10px;border:0;background:transparent;padding:0;cursor:pointer}.is-collapsed{display:none}.calculator-article:has(.loan-results) .calculator-layout.split-analysis{grid-template-columns:minmax(430px,500px) minmax(0,1fr)}.calculator-article:has(.loan-results) .result strong{font-size:30px}.calculator-article:has(.loan-results) .calc{padding:14px}.calculator-article:has(.loan-results) .chart-card canvas{max-height:none}
.payment-mode-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}.payment-fields .field-wide{grid-column:1/-1}.payment-dashboard .chart-grid{grid-template-columns:1fr}.payment-dashboard .chart-card canvas{max-height:190px}.calculator-article:has(.payment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(360px,420px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.payment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.payment-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.payment-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.payment-fields .field input{height:36px!important;padding:0 7px}.payment-fields .input-unit input,.payment-fields .input-unit span{height:36px!important}.payment-fields .input-unit span{padding:0 7px;font-size:12px}.payment-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-article:has(.payment-fields) .calc{padding:10px}.calculator-article:has(.payment-fields) .result strong{font-size:23px}}
@media(max-width:1180px){.nav{align-items:center}.navlinks{flex:0 0 auto;overflow:visible;flex-wrap:nowrap;justify-content:flex-end;padding-bottom:0}.category-nav-link{flex:initial}}
@media(max-width:1100px){.category-tools{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.hero-grid,.feature-layout,.proof-grid,.scientific-home,.browse-panel,.scientific-panel,.chart-grid,.calculator-layout.split-analysis,.seo-keywords{grid-template-columns:1fr}.calculator-pane{position:static}.keyword-chip-list{justify-content:flex-start}.category-grid,.tool-grid,.home-category-grid,.popular-list,.summary-grid{grid-template-columns:repeat(2,1fr)}.category-tools{grid-template-columns:repeat(2,1fr)}.directory-links{grid-template-columns:repeat(2,1fr)}.proof-points,.faq-grid,.faq-list,.related{grid-template-columns:1fr 1fr}.search-panel{box-shadow:none}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.nav{min-height:64px;gap:10px}.brand{font-size:16px}.brand-mark{width:34px;height:34px}.category-nav-link{padding:6px 7px}.category-nav-link .nav-icon{display:none}.all-calculators-menu .submenu{grid-template-columns:1fr;right:-4px;max-height:72vh;overflow:auto}.hero{padding:32px 0 26px}.hero h1{font-size:36px}.home-hero{padding:30px 0 24px}.home-hero h1{font-size:38px}.hero-actions,.footer-grid,.mini-calc,.mini-calc.full{display:grid;grid-template-columns:1fr}.category-grid,.tool-grid,.home-category-grid,.fields,.directory-links,.proof-points,.faq-grid,.faq-list,.popular-list,.related,.calculator-link-grid,.summary-grid{grid-template-columns:1fr}.section{padding:42px 0}.section.tight,.home-block{padding:28px 0}.section-row{align-items:start}.article h1{font-size:36px}.calculator-article h1{font-size:30px}.calculator-article .lead{font-size:15px;margin-bottom:10px}.calculator-article .calc{padding:14px;margin:10px 0 20px}.calculator-article .calc h2{font-size:20px}.calculator-article .field input,.calculator-article .field select{height:40px}.page-title-icon{align-items:flex-start}.title-icon{width:48px;height:48px}.category-section{padding:18px}.category-section-head{grid-template-columns:1fr}.stats{gap:12px}.carousel{grid-auto-columns:82vw}.sci-keypad{grid-template-columns:repeat(4,1fr)}.ad-slot{min-height:76px}}
@media(max-width:900px){.calculator-article:has(#mortgageSummary) .calculator-layout.split-analysis,.calculator-article:has(.loan-results) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-grid,.loan-chart-row{grid-template-columns:minmax(0,1fr)}.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-pane,.analysis-pane,.chart-card,.table-card,.mortgage-dashboard,.loan-results{min-width:0}}
@media(max-width:560px){.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid,.loan-result-panel .summary-grid{grid-template-columns:minmax(0,1fr)}.calculator-article:has(.loan-results) .loan-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:7px}.calculator-article:has(.loan-results) .loan-mode-input{padding:10px}.calculator-article:has(.loan-results) .loan-mode-input h3{font-size:16px}.calculator-article:has(.loan-results) .loan-mode-input p{font-size:12px;margin-bottom:7px}.calculator-article:has(.loan-results) .field label{font-size:12px;margin-bottom:3px}.calculator-article:has(.loan-results) .field input,.calculator-article:has(.loan-results) .field select{height:36px;font-size:14px;padding:0 8px}.calculator-article:has(.loan-results) .calc-actions{margin-top:8px}.calculator-article:has(.loan-results) .result{padding:9px 12px;margin-top:7px}.calculator-article:has(.loan-results) .result strong{font-size:23px}}
@media(max-width:560px){
.wrap{width:calc(100% - 28px)}
.nav{min-height:56px;height:56px;padding:6px 0;gap:8px}.brand{font-size:15px;line-height:.95}.brand-mark{width:30px;height:30px}.menu-top{min-height:36px;padding:7px 8px;font-size:14px}
.main{padding:18px 0 44px}.crumb{margin-bottom:12px;font-size:12px;line-height:1.35;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.article h1,.calculator-article h1,.category-directory h1{font-size:26px;line-height:1.08;letter-spacing:0;overflow-wrap:anywhere}.page-title-icon,.calculator-article .page-title-icon{gap:8px;margin-bottom:5px;align-items:center}.title-icon,.calculator-article .title-icon{width:36px;height:36px;border-radius:9px}.title-icon svg,.calculator-article .title-icon svg{width:20px;height:20px}
.article .lead,.calculator-article .lead,.category-directory .lead{margin:0 0 10px;font-size:14px;line-height:1.42}.calculator-article .pill{margin-bottom:6px;padding:4px 8px;font-size:11px}.calculator-article .pill-icon{width:14px;height:14px}
.calculator-article .calc{margin:8px 0 18px;padding:12px;border-radius:12px}.calculator-article .calc h2{margin-bottom:9px;font-size:18px;letter-spacing:0}.calculator-article .fields{gap:8px}.calculator-article .field label,.calculator-article:has(#mortgageSummary) .field label{margin-bottom:3px;font-size:14px}.calculator-article .field input,.calculator-article .field select,.calculator-article:has(#mortgageSummary) .field>input,.calculator-article:has(#mortgageSummary) .field>select{height:40px;font-size:16px}.input-unit input,.input-unit select,.input-unit span{height:40px!important}.checkline{min-height:40px;padding:8px 10px;font-size:14px!important;line-height:1.35}.calc-actions,.calculator-article:has(#mortgageSummary) .calc-actions{gap:8px;margin-top:10px}.calc-actions .calc-btn,.calculator-article:has(#mortgageSummary) .calc-actions .calc-btn,.calculator-article:has(#mortgageSummary) .clear-btn{min-height:40px;padding:8px 12px;font-size:14px}.clear-btn{min-width:82px}.calculator-article .result,.calculator-article:has(#mortgageSummary) .result{margin-top:9px;padding:11px 12px;border-radius:10px}.calculator-article .result strong,.calculator-article:has(#mortgageSummary) .result strong{font-size:26px;letter-spacing:0}.more-options{margin-top:8px}.more-options summary{min-height:38px;font-size:14px}
.home-hero{padding:18px 0 16px}.hero-stack{gap:14px}.home-hero h1{margin-bottom:8px;font-size:30px;line-height:1.05;letter-spacing:0}.home-hero p{font-size:14px;line-height:1.45}.wide-search{padding:12px;border-radius:12px}.search-panel label{margin-bottom:7px;font-size:14px}.search{height:44px;padding:0 12px;font-size:16px}
.home-block{padding:22px 0}.home-block h2{margin-bottom:12px;font-size:24px;letter-spacing:0}.category-filter{margin-bottom:12px}.category-filter input{height:40px;font-size:16px}.home-category-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.home-category{grid-template-columns:30px minmax(0,1fr);gap:8px;align-items:center;min-height:66px;padding:10px;border-radius:10px}.home-category-icon{grid-row:auto;width:30px;height:30px}.home-category strong{font-size:14px;line-height:1.2;overflow-wrap:anywhere}.home-category small{display:none}
.category-directory .lead{margin-bottom:12px}.category-jump-nav{gap:6px;margin:10px 0 14px}.category-jump-nav a{min-height:32px;padding:5px 8px;font-size:12px}.category-jump-nav .jump-icon{display:none}.category-tools{gap:10px;margin-top:14px}.category-section{padding:12px;border-radius:10px}.category-section-head{display:block;margin-bottom:9px}.category-section-head .section-icon{display:none}.category-section-head h2{margin-bottom:3px;font-size:18px;letter-spacing:0}.category-section-head p{font-size:12px;line-height:1.4}.calculator-link-grid{gap:6px}.category-directory .calculator-link-grid a{padding:7px 8px;font-size:13px;line-height:1.25}
.prose h2,.calculator-article>h2{font-size:21px;letter-spacing:0}.prose h3{font-size:17px}.prose p,.prose li{font-size:14px;line-height:1.55}.related{gap:8px}.related a{padding:11px}
}
.category-main{padding-top:22px}.category-main .crumb{margin-bottom:16px}.category-directory .page-title-icon{gap:10px;margin-bottom:7px}.category-directory h1{font-size:38px;line-height:1.08;letter-spacing:0}.category-directory .title-icon{width:40px;height:40px;border-radius:9px}.category-directory .title-icon svg{width:22px;height:22px}.category-directory .lead{max-width:780px;margin-bottom:12px;font-size:15px;line-height:1.45}.category-jump-nav{gap:6px;margin:10px 0 16px}.category-jump-nav a{min-height:32px;padding:5px 9px;font-size:13px}.category-tools{align-items:start;gap:12px;margin-top:16px}.category-section{align-self:start;padding:14px;border-radius:10px}.category-section-head{display:flex;grid-template-columns:none;align-items:baseline;justify-content:space-between;gap:8px;margin-bottom:10px}.category-section-head h2{margin:0;font-size:18px;line-height:1.2;letter-spacing:0}.category-section-head .category-count{display:inline;width:auto;height:auto;border-radius:0;background:transparent;place-items:normal;flex:0 0 auto;color:var(--muted);font-size:12px;font-weight:750}.category-directory .calculator-link-grid{gap:6px}.category-directory .calculator-link-grid a{min-height:0;padding:8px 9px;font-size:13px;line-height:1.22}
@media(max-width:560px){.category-main{padding-top:14px}.category-main .crumb{margin-bottom:10px}.category-directory h1{font-size:24px}.category-directory .title-icon{width:30px;height:30px}.category-directory .title-icon svg{width:17px;height:17px}.category-directory .page-title-icon{gap:7px;margin-bottom:4px}.category-directory .lead{margin-bottom:8px;font-size:13px}.category-jump-nav{margin:8px 0 10px}.category-tools{gap:8px;margin-top:10px}.category-section{padding:10px}.category-section-head{margin-bottom:7px}.category-section-head h2{font-size:16px}.category-count{font-size:11px}.category-directory .calculator-link-grid a{padding:7px;font-size:12px}}
.article h1,.calculator-article h1,.category-directory h1{font-size:32px;line-height:1.12;letter-spacing:0}
@media(max-width:560px){.article h1,.calculator-article h1,.category-directory h1{font-size:22px;line-height:1.15}}
:root{--ink:#14213a;--muted:#52647b;--subtle:#7a8ba3;--line:#d8e4f1;--bg:#f8fbff;--card:#fff;--card-2:#eef5ff;--brand:#2563eb;--brand-dark:#1746a2;--accent:#d92d42;--accent-muted:#b42335;--accent-soft:#fff1f3;--accent-line:#ffc8d0;--soft:#eaf3ff;--shadow:0 18px 46px rgba(37,99,235,.10)}
body{background:var(--bg)}.site-header{border-bottom-color:#dbe7f4}.primary{background:var(--brand)}.primary:hover{background:var(--brand-dark);box-shadow:0 10px 24px rgba(37,99,235,.24)}.secondary:hover{border-color:#9eb7d5;background:#f8fbff}.search:focus,.field input:focus,.field select:focus{border-color:var(--brand);box-shadow:0 0 0 4px rgba(37,99,235,.12)}.calculator-article .result{background:#1d4ed8;border-color:#1d4ed8;box-shadow:0 12px 26px rgba(37,99,235,.20)}.home-hero{background:#fff}.category-section,.home-category,.chart-card,.table-card,.summary-card,.loan-result-panel{box-shadow:0 8px 24px rgba(37,99,235,.055)}
[data-feet-input].is-hidden,[data-meter-input].is-hidden{display:none}
.summary-card small{color:#52647b}.crumb a,.prose a{text-decoration:underline;text-underline-offset:2px;text-decoration-thickness:1px}
@media(max-width:560px){.compound-fields{grid-template-columns:repeat(2,minmax(0,1fr))}.compound-fields .field label{min-height:34px;display:flex;align-items:end}.compound-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.vehicle-weight-fields{grid-template-columns:repeat(2,minmax(0,1fr))}.vehicle-weight-fields .field label{min-height:34px;display:flex;align-items:end}.vehicle-weight-fields .field-wide{grid-column:1/-1}}
@media(max-width:560px){.fuel-fields{grid-template-columns:repeat(2,minmax(0,1fr))}.fuel-fields .field label{min-height:34px;display:flex;align-items:end}}
@media(max-width:560px){.vehicle-value-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.vehicle-value-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.vehicle-value-fields .field-wide{grid-column:1/-1}.vehicle-value-fields .field input,.vehicle-value-fields .field select{height:36px!important}.calculator-article:has(.vehicle-value-fields) .calc{padding:10px}.calculator-article:has(.vehicle-value-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.vehicle-value-fields) .calc-actions{margin-top:8px}.calculator-article:has(.vehicle-value-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.vehicle-value-fields) .result{padding:9px 10px}}
@media(max-width:560px){.ratio-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.ratio-fields .field-wide{grid-column:1/-1}.ratio-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.ratio-fields .field input,.ratio-fields .field select{height:36px!important;padding:0 7px}.calculator-article:has(.ratio-fields) .calc{padding:10px}.calculator-article:has(.ratio-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.ratio-fields) .calc-actions{margin-top:8px}.calculator-article:has(.ratio-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.ratio-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.ratio-fields) .result strong{font-size:23px}.ratio-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:560px){.bottleneck-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.bottleneck-fields .field-wide{grid-column:1/-1}.bottleneck-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.bottleneck-fields .field input,.bottleneck-fields .field select{height:36px!important;padding:0 6px}.bottleneck-fields .input-unit input,.bottleneck-fields .input-unit span{height:36px!important}.bottleneck-fields .input-unit span{padding:0 6px;font-size:12px}.calculator-article:has(.bottleneck-fields) .calc{padding:10px}.calculator-article:has(.bottleneck-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.bottleneck-fields) .calc-actions{margin-top:8px}.calculator-article:has(.bottleneck-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.bottleneck-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.bottleneck-fields) .result strong{font-size:23px}.bottleneck-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.fraction-fields{grid-template-columns:repeat(3,minmax(0,1fr));gap:8px!important}.fraction-fields .field-wide{grid-column:1/-1}.fraction-dashboard .chart-grid{grid-template-columns:1fr}.fraction-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.fraction-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(400px,460px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.fraction-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.fraction-fields{grid-template-columns:repeat(3,minmax(0,1fr));gap:6px!important}.fraction-fields .field label{font-size:12px!important}.fraction-fields .field input{padding:0 7px}.calculator-article:has(.fraction-fields) .calc{padding:10px}.fraction-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.stats-fields .field-wide{grid-column:1/-1}.stats-fields textarea{width:100%;min-height:98px;resize:vertical;border:1px solid #cfd7e4;border-radius:10px;background:#fff;padding:10px 12px;color:var(--ink);font:16px/1.45 system-ui,sans-serif}.stats-fields small{display:block;margin-top:5px;color:var(--muted);font-size:12px;line-height:1.35}.stats-dashboard .chart-grid{grid-template-columns:1fr}.stats-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.stats-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(390px,450px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.stats-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.stats-fields textarea{min-height:82px}.stats-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-article:has(.stats-fields) .calc{padding:10px}}
.bmi-fields .field-wide{grid-column:1/-1}.bmi-fields .is-hidden{display:none!important}.field-note{padding:9px 10px;border:1px solid #dbe7f4;border-radius:9px;background:#f5f9fd;color:var(--muted);font-size:12px;line-height:1.4}.bmi-dashboard .chart-grid{grid-template-columns:1fr}.bmi-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.bmi-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(360px,420px) minmax(0,1fr)}
.finance-tvm-fields .field-wide{grid-column:1/-1}.finance-tvm-fields .more-options .fields{padding:0 12px 12px}.finance-solve-target{padding:8px;border:1px solid #9bbce4;border-radius:9px;background:#eef5ff}.finance-solve-target input:disabled{color:#173f73;background:#fff;font-weight:800;opacity:1}.finance-tvm-dashboard .chart-grid{grid-template-columns:1fr}.finance-tvm-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.finance-tvm-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(380px,440px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.finance-tvm-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.finance-tvm-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.finance-tvm-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.finance-tvm-fields .field input,.finance-tvm-fields .field select{height:36px!important;padding:0 7px}.finance-tvm-fields .input-unit input,.finance-tvm-fields .input-unit span{height:36px!important}.finance-tvm-fields .input-unit span{padding:0 7px;font-size:12px}.finance-solve-target{padding:5px}.finance-tvm-fields .field-note{padding:7px 8px;font-size:11px}.finance-tvm-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-article:has(.finance-tvm-fields) .calc{padding:10px}.calculator-article:has(.finance-tvm-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.finance-tvm-fields) .calc-actions{margin-top:8px}.calculator-article:has(.finance-tvm-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.finance-tvm-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.finance-tvm-fields) .result strong{font-size:23px}}
@media(max-width:900px){.calculator-article:has(.bmi-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.bmi-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-article:has(.bmi-fields) .calc{padding:10px}}
.salary-converter-fields .field-wide{grid-column:1/-1}.salary-converter-fields .more-options .fields{padding:0 12px}.option-note{margin:8px 12px 12px;color:var(--muted);font-size:12px;line-height:1.4}.salary-converter-dashboard .chart-grid{grid-template-columns:1fr}.salary-converter-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.salary-converter-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(380px,440px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.salary-converter-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.salary-converter-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-article:has(.salary-converter-fields) .calc{padding:10px}}
.fitment-fields{gap:8px!important}.tire-size-fields{grid-template-columns:repeat(3,minmax(0,1fr))}.wheel-offset-fields{grid-template-columns:repeat(2,minmax(0,1fr))}.field-group-label{grid-column:1/-1;margin-top:2px;padding-bottom:3px;border-bottom:1px solid var(--line);color:var(--brand);font-size:13px;font-weight:850}.fitment-dashboard .chart-grid{grid-template-columns:1fr}.fitment-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.fitment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(390px,460px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.fitment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.fitment-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.tire-size-fields{grid-template-columns:repeat(3,minmax(0,1fr))}.fitment-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.fitment-fields .field-wide{grid-column:1/-1}.fitment-fields .field input{height:36px!important;padding:0 6px}.fitment-fields .input-unit input,.fitment-fields .input-unit span{height:36px!important}.fitment-fields .input-unit span{padding:0 6px;font-size:12px}.field-group-label{margin-top:0;font-size:12px}.calculator-article:has(.fitment-fields) .calc{padding:10px}.calculator-article:has(.fitment-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.fitment-fields) .calc-actions{margin-top:8px}.calculator-article:has(.fitment-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.fitment-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.fitment-fields) .result strong{font-size:23px}.fitment-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.project-fields{gap:8px!important}.project-fields .is-hidden{display:none!important}.project-dashboard .chart-grid{grid-template-columns:1fr}.project-dashboard .chart-card canvas{max-height:230px}.concrete-cost-fields{padding:0 12px 12px}.calculator-article:has(.project-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(390px,460px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.project-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.project-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.project-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.project-fields .field-wide{grid-column:1/-1}.project-fields .field input,.project-fields .field select{height:36px!important;padding:0 6px}.project-fields .input-unit input,.project-fields .input-unit span{height:36px!important}.project-fields .input-unit span{padding:0 6px;font-size:12px}.calculator-article:has(.project-fields) .calc{padding:10px}.calculator-article:has(.project-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.project-fields) .calc-actions{margin-top:8px}.calculator-article:has(.project-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.project-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.project-fields) .result strong{font-size:23px}.project-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.concrete-cost-fields{grid-template-columns:repeat(2,minmax(0,1fr))}}
.debt-payoff-fields{display:grid;gap:10px}.debt-settings{grid-template-columns:1fr 1fr;gap:8px!important}.debt-settings .field:first-child{grid-column:1/-1}.debt-list{display:grid;gap:7px}.debt-row{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:7px;margin:0;border:1px solid var(--line);border-radius:10px;padding:8px;background:#f8fafc}.debt-row legend{padding:0 5px;color:var(--brand);font-size:12px;font-weight:850}.debt-row .field label{font-size:12px!important;margin-bottom:3px}.debt-row .field input{height:36px!important;padding:0 8px;font-size:14px!important}.debt-row .input-unit input,.debt-row .input-unit span{height:36px!important}.debt-row .input-unit span{padding:0 7px;font-size:12px}.debt-dashboard .chart-grid{grid-template-columns:1fr}.debt-dashboard .compact-chart canvas{max-height:230px}.calculator-article:has(.debt-payoff-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(430px,500px) minmax(0,1fr)}.calculator-article:has(.debt-payoff-fields) .calc{padding:14px}.calculator-article:has(.debt-payoff-fields) .calc h2{font-size:20px;margin-bottom:8px}.calculator-article:has(.debt-payoff-fields) .calc-actions{margin-top:9px}.calculator-article:has(.debt-payoff-fields) .result{padding:11px 13px;margin-top:8px;font-size:13px}.calculator-article:has(.debt-payoff-fields) .result strong{font-size:25px}.debt-dashboard .table-card{margin-top:10px}
@media(max-width:900px){.calculator-article:has(.debt-payoff-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.calculator-article:has(.debt-payoff-fields) .calc{padding:10px}.debt-settings{grid-template-columns:1fr 1fr}.debt-row{gap:5px;padding:6px}.debt-row .field input,.debt-row .input-unit input,.debt-row .input-unit span{height:33px!important}.debt-row .field input{font-size:13px!important}.calculator-article:has(.debt-payoff-fields) .result strong{font-size:21px}.debt-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.basic-article{max-width:980px}.basic-layout{display:grid;grid-template-columns:minmax(320px,480px) minmax(260px,1fr);gap:14px;align-items:start;margin:12px 0 26px}.basic-calculator{margin:0!important;padding:14px!important}.basic-toolbar,.basic-history-head{display:flex;align-items:center;justify-content:space-between;gap:12px}.basic-calculator .basic-toolbar h2,.basic-history h2{margin:0;font-size:19px}.basic-memory{color:var(--brand);font-size:12px;font-weight:800}.basic-expression-label{display:block;margin:10px 0 4px;color:var(--ink);font-size:13px;font-weight:800}.basic-expression{width:100%;height:43px;border:1px solid #cfd7e4;border-radius:8px;background:#fff;padding:0 10px;color:var(--ink);font:650 17px/1.2 ui-monospace,SFMono-Regular,Consolas,monospace}.basic-expression:focus{outline:0;border-color:var(--brand);box-shadow:0 0 0 3px rgba(37,99,235,.12)}.basic-output{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 10px;align-items:center;margin:7px 0 8px;padding:9px 11px;border-radius:8px;background:linear-gradient(135deg,#0f2d55,#1d4ed8);color:#eaf2ff}.basic-output span{grid-row:1/3;font-size:11px;font-weight:850;text-transform:uppercase}.basic-output strong{min-width:0;color:#fff;font:850 24px/1.08 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.basic-output small{font-size:11px;line-height:1.2}.basic-keypad{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:5px}.basic-key{min-width:0;height:40px;border:1px solid #ccd7e5;border-radius:7px;background:#fff;color:var(--ink);font:780 14px/1 system-ui,sans-serif;cursor:pointer}.basic-key:hover{border-color:#91acd0;background:#f4f8fd}.basic-key:focus-visible{outline:3px solid rgba(37,99,235,.22);outline-offset:1px}.basic-key-memory,.basic-key-function{background:#eef5ff;color:#1746a2}.basic-key-operator,.basic-key-utility{background:#f1f4f8}.basic-key-equals{grid-column:span 3;border-color:var(--brand);background:var(--brand);color:#fff}.basic-key-equals:hover{background:var(--brand-dark);color:#fff}.basic-history{min-height:240px;border:1px solid var(--line);border-radius:12px;background:#fff;padding:14px}.basic-history-head p{margin:3px 0 0;color:var(--muted);font-size:12px}.basic-history-head button{border:0;background:transparent;color:var(--brand);font-size:12px;font-weight:800;cursor:pointer}.basic-history ol{display:grid;gap:6px;margin:12px 0 0;padding:0;list-style:none}.basic-history li button{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;width:100%;border:0;border-radius:7px;background:#f6f9fc;padding:8px 9px;text-align:left;cursor:pointer}.basic-history li span{overflow:hidden;color:var(--muted);font:12px/1.3 ui-monospace,SFMono-Regular,Consolas,monospace;text-overflow:ellipsis;white-space:nowrap}.basic-history li strong{color:var(--ink);font:800 12px/1.3 ui-monospace,SFMono-Regular,Consolas,monospace}.basic-history-empty{padding:10px 2px;color:var(--muted);font-size:13px}.basic-article code{border-radius:4px;background:#eef3f8;padding:1px 4px;color:#173f73;font-size:.92em}.basic-article .table-scroll{margin:10px 0 18px}
.scientific-article{max-width:980px}.scientific-page{max-width:760px;margin:12px 0 24px;padding:16px}.sci-toolbar{display:flex;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px}.scientific-page .sci-toolbar h2{margin:0}.sci-angle-toggle{display:grid;grid-template-columns:repeat(2,1fr);padding:3px;border:1px solid var(--line);border-radius:8px;background:#edf2f7}.sci-angle-toggle button{min-width:58px;min-height:32px;border:0;border-radius:6px;background:transparent;color:var(--muted);font:800 12px/1 system-ui,sans-serif;cursor:pointer}.sci-angle-toggle button.is-active{background:#fff;color:var(--brand);box-shadow:0 2px 7px rgba(21,32,51,.12)}.sci-expression-label{display:block;margin-bottom:5px;color:var(--ink);font-size:13px;font-weight:800}.sci-expression{width:100%;height:48px;border:1px solid #cfd7e4;border-radius:9px;background:#fff;padding:0 12px;color:var(--ink);font:600 18px/1.2 ui-monospace,SFMono-Regular,Consolas,monospace}.sci-expression:focus{outline:0;border-color:var(--brand);box-shadow:0 0 0 4px rgba(37,99,235,.12)}.sci-output{display:grid;grid-template-columns:auto minmax(0,1fr);gap:2px 12px;align-items:center;margin:9px 0 10px;padding:10px 12px;border-radius:9px;background:#1d4ed8;color:#eaf2ff}.sci-output span{grid-row:1/3;font-size:12px;font-weight:800;text-transform:uppercase}.sci-output strong{min-width:0;color:#fff;font:800 25px/1.1 ui-monospace,SFMono-Regular,Consolas,monospace;overflow-wrap:anywhere}.sci-output small{font-size:11px;line-height:1.25}.sci-keypad{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px}.sci-key{min-width:0;height:42px;border:1px solid #cfd9e6;border-radius:7px;background:#fff;color:var(--ink);font:750 14px/1 system-ui,sans-serif;cursor:pointer}.sci-key:hover{border-color:#91acd0;background:#f4f8fd}.sci-key:focus-visible{outline:3px solid rgba(37,99,235,.24);outline-offset:1px}.sci-key-function,.sci-key-memory{background:#eef5ff;color:#1746a2}.sci-key-operator,.sci-key-utility{background:#f2f5f8}.sci-key-equals{border-color:var(--brand);background:var(--brand);color:#fff}.sci-key-equals:hover{background:var(--brand-dark);color:#fff}.sci-history{margin-top:14px;padding-top:12px;border-top:1px solid var(--line)}.sci-history-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.sci-history h3{margin:0;font-size:15px}.sci-history-clear{border:0;background:transparent;color:var(--brand);font:750 12px/1 system-ui,sans-serif;cursor:pointer}.sci-history ol{display:grid;gap:5px;margin:9px 0 0;padding:0;list-style:none}.sci-history li button{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:10px;width:100%;border:0;border-radius:7px;background:#f6f9fc;padding:7px 9px;text-align:left;cursor:pointer}.sci-history li span{overflow:hidden;color:var(--muted);font:12px/1.25 ui-monospace,SFMono-Regular,Consolas,monospace;text-overflow:ellipsis;white-space:nowrap}.sci-history li strong{color:var(--ink);font:750 12px/1.25 ui-monospace,SFMono-Regular,Consolas,monospace}.sci-history-empty{padding:8px 9px;color:var(--muted);font-size:12px}.scientific-article code{border-radius:4px;background:#eef3f8;padding:1px 4px;color:#173f73;font-size:.92em}.scientific-article .table-scroll{margin:10px 0 18px}
@media(max-width:760px){.basic-layout{grid-template-columns:minmax(0,1fr)}.basic-history{min-height:0}.basic-history ol{max-height:190px;overflow:auto}}
@media(max-width:560px){.basic-layout{gap:9px;margin-top:8px}.basic-calculator,.basic-history{padding:10px!important}.basic-expression{height:40px;font-size:16px}.basic-output{margin:6px 0 7px;padding:8px 9px}.basic-output strong{font-size:21px}.basic-keypad{gap:4px}.basic-key{height:37px;border-radius:6px;font-size:12px}.scientific-page{margin-top:8px;padding:10px}.sci-toolbar{margin-bottom:8px}.sci-angle-toggle button{min-width:50px;min-height:29px}.sci-expression{height:42px;padding:0 9px;font-size:16px}.sci-output{margin:7px 0 8px;padding:8px 9px}.sci-output strong{font-size:21px}.sci-keypad{gap:4px}.sci-key{height:38px;border-radius:6px;font-size:12px}.sci-history{margin-top:10px;padding-top:9px}.sci-history ol{max-height:170px;overflow:auto}}
'''

SEARCH_JS = r'''
(function(){
  let items = window.NORTHSTAR_ITEMS || [];
  let loading = null;
  const basePath = window.NORTHSTAR_BASE_PATH || "";
  const q = document.getElementById("siteSearch");
  const box = document.getElementById("searchResults");
  if (!q || !box) return;
  function loadItems() {
    if (items.length) return Promise.resolve(items);
    if (!loading) {
      loading = fetch(basePath + "/assets/search-index.json")
        .then(response => response.ok ? response.json() : [])
        .then(data => { items = Array.isArray(data) ? data : []; return items; })
        .catch(() => []);
    }
    return loading;
  }
  q.addEventListener("input", async () => {
    const s = q.value.toLowerCase().trim();
    if (!s) {
      box.style.display = "none";
      box.innerHTML = "";
      return;
    }
    await loadItems();
    if (q.value.toLowerCase().trim() !== s) return;
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
const MONEY=(n,currency='USD')=>new Intl.NumberFormat('en-US',{style:'currency',currency,maximumFractionDigits:2}).format(Number.isFinite(n)?n:0);
const H=value=>String(value).replace(/[&<>"']/g,char=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[char]);
const RMD_JOINT_TABLE=__RMD_JOINT_TABLE__;
function show(html){const r=$('#result');if(r)r.innerHTML=html}
function unitValue(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function annualCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function monthlyCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100/12:V(id)/12}
function monthDate(id){const raw=document.getElementById(id)?.value||'';return /^\d{4}-\d{2}$/.test(raw)?new Date(`${raw}-01T00:00:00`):new Date(raw||Date.now())}
function syncMortgageCosts(){const box=document.getElementById('include_costs'),panel=document.getElementById('mortgageCostFields');if(!box||!panel)return true;const on=box.checked;panel.hidden=!on;panel.classList.toggle('is-hidden',!on);panel.style.display=on?'':'none';return on}
function priorityLengthProjection(){
  const reverse=document.getElementById('length_direction')?.value==='reverse',value=V('length_value'),factor=V('conversion_factor'),source=document.getElementById('source_name')?.value||'source units',target=document.getElementById('target_name')?.value||'target units',sourceSymbol=document.getElementById('source_symbol')?.value||source,targetSymbol=document.getElementById('target_symbol')?.value||target,sourceMeters=V('source_meter_factor'),targetMeters=V('target_meter_factor');
  const from=reverse?target:source,to=reverse?source:target,fromSymbol=reverse?targetSymbol:sourceSymbol,toSymbol=reverse?sourceSymbol:targetSymbol,activeFactor=reverse?1/factor:factor,result=value*activeFactor,meters=value*(reverse?targetMeters:sourceMeters),feet=meters/0.3048,inches=meters/0.0254;
  return{reverse,value,factor,activeFactor,result,source,target,sourceSymbol,targetSymbol,from,to,fromSymbol,toSymbol,meters,feet,inches,centimeters:meters*100,millimeters:meters*1000};
}
function compoundProjection(options={}){
  const principal=Math.max(0,V('principal')),enteredAnnual=Math.max(-.99,V('rate')/100),annual=Number.isFinite(options.annualOverride)?Math.max(-.99,options.annualOverride):enteredAnnual,years=Math.max(0,Math.floor(V('years'))),extraMonths=Math.max(0,Math.min(11,Math.floor(V('compound_months')))),frequency=Number(document.getElementById('compound_frequency')?.value??12),monthly=Math.max(0,V('monthly')),annualContribution=Math.max(0,V('annual_contribution')),contributionGrowth=Math.max(-.99,V('contribution_growth')/100),rateVariance=Math.max(0,V('rate_variance')/100),taxRate=Math.max(0,Math.min(1,V('interest_tax')/100)),inflation=Math.max(-.99,V('compound_inflation')/100);
  const timing=document.getElementById('contribution_timing')?.value||'end',totalMonths=years*12+extraMonths,monthlyRate=frequency===0?Math.exp(annual/12)-1:Math.pow(1+annual/frequency,frequency/12)-1,effectiveAnnual=frequency===0?Math.exp(annual)-1:Math.pow(1+annual/frequency,frequency)-1;
  let balance=principal,totalGrossInterest=0,totalTax=0,totalDeposits=0,periodInterest=0,periodTax=0,periodDeposits=0;const schedule=[];
  for(let month=1;month<=totalMonths;month++){
    const contributionYear=Math.floor((month-1)/12),growthFactor=Math.pow(1+contributionGrowth,contributionYear),monthlyDeposit=monthly*growthFactor,annualDeposit=annualContribution*growthFactor;
    if(timing==='beginning'){
      balance+=monthlyDeposit;totalDeposits+=monthlyDeposit;periodDeposits+=monthlyDeposit;
      if((month-1)%12===0){balance+=annualDeposit;totalDeposits+=annualDeposit;periodDeposits+=annualDeposit}
    }
    const grossInterest=balance*monthlyRate,interestTax=Math.max(0,grossInterest)*taxRate,netInterest=grossInterest-interestTax;
    balance+=netInterest;totalGrossInterest+=grossInterest;totalTax+=interestTax;periodInterest+=grossInterest;periodTax+=interestTax;
    if(timing!=='beginning'){
      balance+=monthlyDeposit;totalDeposits+=monthlyDeposit;periodDeposits+=monthlyDeposit;
      if(month%12===0){balance+=annualDeposit;totalDeposits+=annualDeposit;periodDeposits+=annualDeposit}
    }
    if(month%12===0||month===totalMonths){const wholeYears=Math.floor(month/12),remaining=month%12,period=remaining?(wholeYears?`${wholeYears} yr ${remaining} mo`:`${remaining} mo`):`${wholeYears} yr`;schedule.push({period,deposits:periodDeposits,grossInterest:periodInterest,tax:periodTax,balance});periodInterest=0;periodTax=0;periodDeposits=0}
  }
  if(!schedule.length)schedule.push({period:'Start',deposits:0,grossInterest:0,tax:0,balance});
  const totalInterest=totalGrossInterest-totalTax,contributed=principal+totalDeposits,buyingPower=balance/Math.pow(1+inflation,totalMonths/12),durationLabel=extraMonths?`${years} yr ${extraMonths} mo`:`${years} yr`;
  return {principal,annual,years,extraMonths,totalMonths,frequency,monthly,annualContribution,contributionGrowth,rateVariance,taxRate,inflation,timing,balance,totalGrossInterest,totalTax,totalInterest,totalDeposits,contributed,buyingPower,schedule,effectiveAnnual,durationLabel};
}
function interestComparisonProjection(){
  const compound=compoundProjection();
  let simplePrincipal=compound.principal,simpleGrossInterest=0,simpleTax=0,totalDeposits=0;const schedule=[];
  for(let month=1;month<=compound.totalMonths;month++){
    if(compound.timing==='beginning'){
      simplePrincipal+=compound.monthly;totalDeposits+=compound.monthly;
      if((month-1)%12===0){simplePrincipal+=compound.annualContribution;totalDeposits+=compound.annualContribution}
    }
    const gross=simplePrincipal*compound.annual/12,tax=Math.max(0,gross)*compound.taxRate;
    simpleGrossInterest+=gross;simpleTax+=tax;
    if(compound.timing!=='beginning'){
      simplePrincipal+=compound.monthly;totalDeposits+=compound.monthly;
      if(month%12===0){simplePrincipal+=compound.annualContribution;totalDeposits+=compound.annualContribution}
    }
    if(month%12===0||month===compound.totalMonths){
      const wholeYears=Math.floor(month/12),remaining=month%12,period=remaining?(wholeYears?`${wholeYears} yr ${remaining} mo`:`${remaining} mo`):`${wholeYears} yr`,compoundRow=compound.schedule[schedule.length],simpleBalance=simplePrincipal+simpleGrossInterest-simpleTax,compoundBalance=compoundRow?.balance??compound.balance;
      schedule.push({period,contributed:compound.principal+totalDeposits,simpleBalance,compoundBalance,advantage:compoundBalance-simpleBalance});
    }
  }
  if(!schedule.length)schedule.push({period:'Start',contributed:compound.principal,simpleBalance:compound.principal,compoundBalance:compound.principal,advantage:0});
  const simpleInterest=simpleGrossInterest-simpleTax,simpleBalance=simplePrincipal+simpleInterest,simpleBuyingPower=simpleBalance/Math.pow(1+compound.inflation,compound.totalMonths/12),advantage=compound.balance-simpleBalance;
  return {compound,simplePrincipal,simpleGrossInterest,simpleTax,simpleInterest,simpleBalance,simpleBuyingPower,advantage,schedule};
}
function syncPaymentMode(nextMode){
  const mode=nextMode||document.querySelector('[data-payment-mode].is-active')?.dataset.paymentMode||'term';
  document.querySelectorAll('[data-payment-mode]').forEach(button=>{const active=button.dataset.paymentMode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-selected',active?'true':'false')});
  document.querySelectorAll('[data-payment-term]').forEach(el=>el.classList.toggle('is-hidden',mode!=='term'));
  document.querySelectorAll('[data-payment-fixed]').forEach(el=>el.classList.toggle('is-hidden',mode!=='payment'));
  return mode;
}
function paymentProjection(){
  const mode=syncPaymentMode(),principal=Math.max(0,V('payment_amount')),annual=Math.max(0,V('payment_rate'))/100,rate=annual/12;
  let regularPayment=0,monthsExact=0,months=0,valid=true,message='';
  if(!(principal>0)){valid=false;message='Enter a loan amount greater than zero.'}
  if(mode==='term'){
    months=Math.max(0,Math.floor(V('payment_years'))*12+Math.floor(V('payment_months')));monthsExact=months;
    if(months<1){valid=false;message='Enter a loan term of at least one month.'}
    else regularPayment=rate?principal*rate*Math.pow(1+rate,months)/(Math.pow(1+rate,months)-1):principal/months;
  }else{
    regularPayment=Math.max(0,V('payment_monthly'));
    if(!(regularPayment>0)){valid=false;message='Enter a monthly payment greater than zero.'}
    else if(rate&&regularPayment<=principal*rate){valid=false;message='The payment must be greater than the first month of interest to reduce the balance.'}
    else{monthsExact=rate?-Math.log(1-principal*rate/regularPayment)/Math.log(1+rate):principal/regularPayment;months=Math.ceil(monthsExact-1e-10)}
  }
  if(valid&&(!Number.isFinite(regularPayment)||!Number.isFinite(monthsExact)||months>1200)){valid=false;message='The payoff period exceeds 100 years. Increase the payment or review the inputs.'}
  if(!valid)return{valid:false,mode,principal,annual,rate,regularPayment,monthsExact,months,message,schedule:[]};
  let balance=principal,totalPaid=0,totalInterest=0;const schedule=[];
  for(let month=1;month<=months&&balance>.005;month++){
    const interest=balance*rate,due=balance+interest,payment=Math.min(regularPayment,due),principalPaid=Math.max(0,payment-interest);balance=Math.max(0,due-payment);totalPaid+=payment;totalInterest+=interest;
    schedule.push({month,payment,principal:principalPaid,interest,balance});
  }
  const payoffMonths=schedule.length,years=Math.floor(payoffMonths/12),remainingMonths=payoffMonths%12,termLabel=[years?`${years} year${years===1?'':'s'}`:'',remainingMonths?`${remainingMonths} month${remainingMonths===1?'':'s'}`:''].filter(Boolean).join(' ')||'0 months';
  return{valid:true,mode,principal,annual,rate,regularPayment,monthsExact,payoffMonths,termLabel,totalPaid,totalInterest,schedule};
}
function amortizationProjection(){
  const principal=Math.max(0,V('amort_amount')),annual=Math.max(0,V('amort_rate'))/100,rate=annual/12,termMonths=Math.max(0,Math.floor(V('amort_years'))*12+Math.floor(V('amort_months'))),extraMonthly=Math.max(0,V('amort_extra_monthly')),extraYearly=Math.max(0,V('amort_extra_yearly')),extraOnce=Math.max(0,V('amort_extra_once')),startValue=document.getElementById('amort_start')?.value||'',oneTimeValue=document.getElementById('amort_extra_date')?.value||'';
  let valid=principal>0&&termMonths>0&&termMonths<=1200,message='';
  if(!(principal>0))message='Enter a loan amount greater than zero.';else if(!(termMonths>0))message='Enter a loan term of at least one month.';else if(termMonths>1200)message='The loan term cannot exceed 100 years.';
  const regularPayment=valid?(rate?principal*rate*Math.pow(1+rate,termMonths)/(Math.pow(1+rate,termMonths)-1):principal/termMonths):0;
  const monthIndex=value=>{if(!/^\d{4}-\d{2}$/.test(value))return null;const[y,m]=value.split('-').map(Number);return y*12+m-1},startIndex=monthIndex(startValue),oneTimeIndex=monthIndex(oneTimeValue),oneTimeMonth=startIndex!==null&&oneTimeIndex!==null?oneTimeIndex-startIndex+1:null;
  const build=(withExtras)=>{let balance=principal,totalPaid=0,totalInterest=0,totalExtra=0;const schedule=[];for(let month=1;month<=1200&&balance>.005;month++){const interest=balance*rate,scheduledPrincipal=Math.max(0,regularPayment-interest),requested=withExtras?(extraMonthly+(month%12===0?extraYearly:0)+(month===oneTimeMonth?extraOnce:0)):0,principalPaid=Math.min(balance,scheduledPrincipal+requested),extraPaid=Math.max(0,principalPaid-Math.min(balance,scheduledPrincipal)),payment=interest+principalPaid;balance=Math.max(0,balance-principalPaid);totalPaid+=payment;totalInterest+=interest;totalExtra+=extraPaid;schedule.push({month,payment,principal:principalPaid,interest,extra:extraPaid,balance});if(month>=termMonths&&!withExtras&&balance>.005){valid=false;message='The schedule did not amortize within the entered term.';break}}return{schedule,totalPaid,totalInterest,totalExtra,payoffMonths:schedule.length,balance}};
  if(!valid)return{valid:false,message,principal,annual,rate,termMonths,regularPayment,schedule:[],annualRows:[]};
  const baseline=build(false),accelerated=build(true),active=extraMonthly>0||extraYearly>0||(extraOnce>0&&oneTimeMonth!==null&&oneTimeMonth>0),selected=active?accelerated:baseline;
  if(selected.balance>.005)return{valid:false,message:'The loan did not pay off within the supported 100-year schedule.',principal,annual,rate,termMonths,regularPayment,schedule:[],annualRows:[]};
  const annualRows=[];for(let i=0;i<selected.schedule.length;i+=12){const chunk=selected.schedule.slice(i,i+12);annualRows.push({year:Math.floor(i/12)+1,payments:chunk.reduce((s,x)=>s+x.payment,0),principal:chunk.reduce((s,x)=>s+x.principal,0),interest:chunk.reduce((s,x)=>s+x.interest,0),balance:chunk.at(-1).balance})}
  const payoffDate=startIndex===null?'Not set':new Date(Date.UTC(Math.floor((startIndex+selected.payoffMonths-1)/12),(startIndex+selected.payoffMonths-1)%12,1)).toLocaleDateString('en-US',{month:'long',year:'numeric',timeZone:'UTC'}),years=Math.floor(selected.payoffMonths/12),months=selected.payoffMonths%12,termLabel=[years?`${years} year${years===1?'':'s'}`:'',months?`${months} month${months===1?'':'s'}`:''].filter(Boolean).join(' ')||'0 months';
  return{valid:true,principal,annual,rate,termMonths,regularPayment,active,extraMonthly,extraYearly,extraOnce,oneTimeMonth,schedule:selected.schedule,annualRows,totalPaid:selected.totalPaid,totalInterest:selected.totalInterest,totalExtra:selected.totalExtra,payoffMonths:selected.payoffMonths,payoffDate,termLabel,interestSaved:Math.max(0,baseline.totalInterest-selected.totalInterest),monthsSaved:Math.max(0,baseline.payoffMonths-selected.payoffMonths),baseline};
}
function syncRetirementMode(nextMode){
  const mode=nextMode||document.querySelector('[data-retirement-mode].is-active')?.dataset.retirementMode||'need';
  document.querySelectorAll('[data-retirement-mode]').forEach(button=>{const active=button.dataset.retirementMode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-selected',active?'true':'false')});
  document.querySelectorAll('[data-retirement-panel]').forEach(panel=>panel.classList.toggle('is-hidden',panel.dataset.retirementPanel!==mode));
  return mode;
}
function retirementGrowingWithdrawalPV(firstPayment,rate,growth,months){if(!(months>0)||!(firstPayment>0))return 0;if(Math.abs(rate-growth)<1e-10)return firstPayment*months/(1+rate);return firstPayment*(1-Math.pow((1+growth)/(1+rate),months))/(rate-growth)}
function retirementGrowingWithdrawal(balance,rate,growth,months){if(!(months>0)||!(balance>0))return 0;if(Math.abs(rate-growth)<1e-10)return balance*(1+rate)/months;return balance*(rate-growth)/(1-Math.pow((1+growth)/(1+rate),months))}
function retirementAnnuityFactor(rate,months){return rate?(Math.pow(1+rate,months)-1)/rate:months}
function retirementProjection(){
  const mode=syncRetirementMode(),schedule=[];let valid=true,message='',cards=[],bars=[],rows=[],result='';
  const finish=(payload={})=>({valid,message,mode,cards,bars,rows,schedule,result,...payload});
  if(mode==='need'){
    const currentAge=Math.floor(V('ret_current_age')),retirementAge=Math.floor(V('ret_retirement_age')),lifeAge=Math.floor(V('ret_life_age')),income=Math.max(0,V('ret_income')),incomeGrowth=Math.max(-.99,V('ret_income_growth')/100),replacement=Math.max(0,V('ret_replacement')/100),annualReturn=Math.max(-.99,V('ret_return')/100),inflation=Math.max(-.99,V('ret_inflation')/100),otherToday=Math.max(0,V('ret_other_income')),savings=Math.max(0,V('ret_savings')),saveRate=Math.max(0,V('ret_save_rate')/100),workYears=retirementAge-currentAge,retirementYears=lifeAge-retirementAge;
    if(!(workYears>0)){valid=false;message='Retirement age must be greater than current age.'}else if(!(retirementYears>0)){valid=false;message='Life expectancy must be greater than retirement age.'}
    if(!valid)return finish();
    const workMonths=workYears*12,retirementMonths=retirementYears*12,monthlyReturn=Math.pow(1+annualReturn,1/12)-1,monthlyInflation=Math.pow(1+inflation,1/12)-1,futureIncome=income*Math.pow(1+incomeGrowth,workYears),desiredMonthly=futureIncome*replacement/12,otherMonthly=otherToday*Math.pow(1+inflation,workYears),incomeGap=Math.max(0,desiredMonthly-otherMonthly),target=retirementGrowingWithdrawalPV(incomeGap,monthlyReturn,monthlyInflation,retirementMonths);
    let balance=savings,totalContributions=savings;for(let month=1;month<=workMonths;month++){const opening=balance,contribution=income*Math.pow(1+incomeGrowth,(month-1)/12)*saveRate/12,growth=opening*monthlyReturn;balance=opening+growth+contribution;totalContributions+=contribution;if(month%12===0){const prior=schedule.length?schedule.at(-1).balance:savings,yearContribution=totalContributions-(schedule.length?schedule.reduce((s,x)=>s+x.cashflow,0)+savings:savings);schedule.push({label:`Age ${currentAge+month/12}`,cashflow:yearContribution,growth:balance-prior-yearContribution,balance})}}
    const projected=balance,gap=Math.max(0,target-projected),surplus=Math.max(0,projected-target),factor=retirementAnnuityFactor(monthlyReturn,workMonths),extraMonthly=gap>0?gap/factor:0,todayTarget=target/Math.pow(1+inflation,workYears);
    cards=[["Required at retirement",USD(target),`${USD(todayTarget)} in today's purchasing power.`],["Projected savings",USD(projected),`${USD(totalContributions)} total contributed.`],[gap>0?"Savings gap":"Projected surplus",USD(gap||surplus),gap>0?`${USD(extraMonthly)} additional monthly savings.`:"Projection exceeds the modeled target."],["Starting retirement income",USD(desiredMonthly),`${USD(incomeGap)} from savings after other income.`]];
    bars=[{label:"Required nest egg",value:target,display:USD(target)},{label:"Projected savings",value:projected,display:USD(projected)},{label:"Current savings",value:savings,display:USD(savings)}];
    rows=[["Years until retirement",`${workYears} years`,`Age ${currentAge} to ${retirementAge}.`],["Years modeled in retirement",`${retirementYears} years`,`Through age ${lifeAge}.`],["Projected income at retirement",USD(futureIncome),`${F(incomeGrowth*100,2)}% annual income growth.`],["Desired first-year retirement income",USD(desiredMonthly*12),`${F(replacement*100,1)}% replacement target.`],["Other income at retirement",USD(otherMonthly*12),"Inflation-adjusted from today's entered amount."],["First-year portfolio income gap",USD(incomeGap*12),"Desired income minus other income."],["Required savings at retirement",USD(target),"Funds the inflation-adjusted gap through life expectancy."],["Projected retirement savings",USD(projected),`${F(saveRate*100,1)}% of projected income saved.`],[gap>0?"Additional monthly savings needed":"Projected surplus",USD(gap>0?extraMonthly:surplus),gap>0?"Level additional monthly contribution at the same return.":"Projected balance minus required savings."]];
    result=gap>0?`<strong>${USD(target)} estimated retirement target</strong><br>Projected savings: ${USD(projected)}; gap: ${USD(gap)}; about ${USD(extraMonthly)} additional monthly savings may close it.`:`<strong>${USD(target)} estimated retirement target</strong><br>Projected savings: ${USD(projected)}; modeled surplus: ${USD(surplus)}.`;return finish({target,projected,gap,extraMonthly});
  }
  if(mode==='save'){
    const currentAge=Math.floor(V('save_current_age')),retirementAge=Math.floor(V('save_retirement_age')),target=Math.max(0,V('save_target')),now=Math.max(0,V('save_now')),annualReturn=Math.max(-.99,V('save_return')/100),currentMonthly=Math.max(0,V('save_monthly_now')),years=retirementAge-currentAge,months=years*12;
    if(!(years>0)){valid=false;message='Retirement age must be greater than current age.';return finish()}if(!(target>0)){valid=false;message='Enter a retirement savings target greater than zero.';return finish()}
    const rate=Math.pow(1+annualReturn,1/12)-1,growth=Math.pow(1+rate,months),factor=retirementAnnuityFactor(rate,months),futureCurrent=now*growth,requiredMonthly=Math.max(0,(target-futureCurrent)/factor),projected= futureCurrent+currentMonthly*factor,monthlyGap=Math.max(0,requiredMonthly-currentMonthly);let balance=now;
    for(let month=1;month<=months;month++){const opening=balance,earned=opening*rate;balance=opening+earned+requiredMonthly;if(month%12===0)schedule.push({label:`Age ${currentAge+month/12}`,cashflow:requiredMonthly*12,growth:balance-(schedule.length?schedule.at(-1).balance:now)-requiredMonthly*12,balance})}
    cards=[["Required monthly savings",USD(requiredMonthly),`${years} years to the target.`],["Current monthly savings",USD(currentMonthly),monthlyGap?`${USD(monthlyGap)} below the modeled requirement.`:"Meets or exceeds the modeled requirement."],["Projected at current pace",USD(projected),projected>=target?"At or above target.":`${USD(target-projected)} below target.`],["Retirement target",USD(target),`At age ${retirementAge}.`]];bars=[{label:"Retirement target",value:target,display:USD(target)},{label:"Current pace",value:projected,display:USD(projected)},{label:"Current savings growth",value:futureCurrent,display:USD(futureCurrent)}];rows=[["Years to save",`${years} years`,`Age ${currentAge} to ${retirementAge}.`],["Savings today",USD(now),"Starting balance."],["Average annual return",`${F(annualReturn*100,2)}%`,"Compounded monthly."],["Future value of savings today",USD(futureCurrent),"Before new contributions."],["Required monthly contribution",USD(requiredMonthly),"Level end-of-month deposits."],["Current monthly contribution",USD(currentMonthly),"Entered current pace."],["Additional monthly amount",USD(monthlyGap),"Required minus current contribution, floored at zero."],["Projected balance at current pace",USD(projected),"Current savings plus current monthly deposits."]];result=`<strong>${USD(requiredMonthly)} per month to reach ${USD(target)}</strong><br>Your entered ${USD(currentMonthly)} monthly contribution projects to ${USD(projected)} at age ${retirementAge}.`;return finish({requiredMonthly,projected,target});
  }
  if(mode==='withdraw'){
    const currentAge=Math.floor(V('withdraw_current_age')),retirementAge=Math.floor(V('withdraw_retirement_age')),lifeAge=Math.floor(V('withdraw_life_age')),start=Math.max(0,V('withdraw_savings')),annualAdd=Math.max(0,V('withdraw_annual_add')),monthlyAdd=Math.max(0,V('withdraw_monthly_add')),annualReturn=Math.max(-.99,V('withdraw_return')/100),inflation=Math.max(-.99,V('withdraw_inflation')/100),workYears=retirementAge-currentAge,retirementYears=lifeAge-retirementAge;
    if(!(workYears>0)){valid=false;message='Retirement age must be greater than current age.';return finish()}if(!(retirementYears>0)){valid=false;message='Life expectancy must be greater than retirement age.';return finish()}
    const rate=Math.pow(1+annualReturn,1/12)-1,growthRate=Math.pow(1+inflation,1/12)-1;let balance=start,totalContributions=start;
    for(let month=1;month<=workYears*12;month++){const opening=balance,growth=opening*rate,contribution=monthlyAdd+(month%12===0?annualAdd:0);balance=opening+growth+contribution;totalContributions+=contribution;if(month%12===0)schedule.push({label:`Age ${currentAge+month/12}`,cashflow:contribution+(monthlyAdd*11),growth:balance-(schedule.length?schedule.at(-1).balance:start)-(annualAdd+monthlyAdd*12),balance})}
    const nestEgg=balance,firstMonthly=retirementGrowingWithdrawal(nestEgg,rate,growthRate,retirementYears*12),todayMonthly=firstMonthly/Math.pow(1+inflation,workYears),firstAnnual=firstMonthly*12;let retirementBalance=nestEgg,currentWithdrawal=firstMonthly;
    for(let year=1;year<=retirementYears;year++){const starting=retirementBalance;let withdrawn=0;for(let m=1;m<=12&&retirementBalance>.005;m++){const available=retirementBalance*(1+rate),paid=Math.min(available,currentWithdrawal);retirementBalance=available-paid;withdrawn+=paid;currentWithdrawal*=1+growthRate}schedule.push({label:`Age ${retirementAge+year}`,cashflow:-withdrawn,growth:retirementBalance-starting+withdrawn,balance:retirementBalance})}
    cards=[["Savings at retirement",USD(nestEgg),`${USD(totalContributions)} total contributed.`],["Starting monthly withdrawal",USD(firstMonthly),`${USD(todayMonthly)} in today's purchasing power.`],["Starting annual income",USD(firstAnnual),`Modeled through age ${lifeAge}.`],["Retirement duration",`${retirementYears} years`,`Inflation-adjusted withdrawals.`]];bars=[{label:"Savings at retirement",value:nestEgg,display:USD(nestEgg)},{label:"Total contributions",value:totalContributions,display:USD(totalContributions)},{label:"First-year withdrawal",value:firstAnnual,display:USD(firstAnnual)}];rows=[["Years until retirement",`${workYears} years`,`Age ${currentAge} to ${retirementAge}.`],["Savings today",USD(start),"Starting balance."],["Monthly contribution",USD(monthlyAdd),"Added during working years."],["Annual contribution",USD(annualAdd),"Added at each year end."],["Savings at retirement",USD(nestEgg),"Projected before withdrawals."],["Starting monthly withdrawal",USD(firstMonthly),"In future dollars at retirement."],["Today's purchasing power",USD(todayMonthly),`${F(inflation*100,2)}% inflation assumption.`],["Modeled retirement period",`${retirementYears} years`,`Through age ${lifeAge}.`]];result=`<strong>${USD(firstMonthly)} starting monthly withdrawal</strong><br>Projected savings at retirement: ${USD(nestEgg)}; today's purchasing-power equivalent: ${USD(todayMonthly)} per month.`;return finish({nestEgg,firstMonthly,todayMonthly});
  }
  const amount=Math.max(0,V('last_amount')),startingWithdrawal=Math.max(0,V('last_withdrawal')),annualReturn=Math.max(-.99,V('last_return')/100),inflation=Math.max(-.99,V('last_inflation')/100),rate=Math.pow(1+annualReturn,1/12)-1,growthRate=Math.pow(1+inflation,1/12)-1;
  if(!(amount>0)){valid=false;message='Enter an amount greater than zero.';return finish()}if(!(startingWithdrawal>0)){valid=false;message='Enter a monthly withdrawal greater than zero.';return finish()}
  let balance=amount,withdrawal=startingWithdrawal,totalWithdrawn=0,months=0;for(let month=1;month<=1200&&balance>.005;month++){const opening=balance,paid=Math.min(balance,withdrawal);balance=(balance-paid)*(1+rate);totalWithdrawn+=paid;months=month;withdrawal*=1+growthRate;if(month%12===0||balance<=.005)schedule.push({label:`Year ${Math.ceil(month/12)}`,cashflow:-Math.min(totalWithdrawn-(schedule.length?schedule.reduce((s,x)=>s-x.cashflow,0):0),totalWithdrawn),growth:balance-(schedule.length?schedule.at(-1).balance:amount)+(totalWithdrawn-(schedule.length?schedule.reduce((s,x)=>s-x.cashflow,0):0)),balance})}
  const perpetual=balance>.005,years=Math.floor(months/12),remaining=months%12,duration=perpetual?'More than 100 years':[years?`${years} year${years===1?'':'s'}`:'',remaining?`${remaining} month${remaining===1?'':'s'}`:''].filter(Boolean).join(' '),endingMonthly=withdrawal;
  cards=[["Estimated duration",duration,perpetual?"Balance remains after 100 modeled years.":"Until the modeled balance is depleted."],["Starting monthly withdrawal",USD(startingWithdrawal),`${F(inflation*100,2)}% annual increase.`],["Total withdrawn",USD(totalWithdrawn),"Across the modeled period."],["Final monthly withdrawal",USD(endingMonthly),"Inflation-adjusted amount near the end."]];bars=[{label:"Starting amount",value:amount,display:USD(amount)},{label:"Total withdrawn",value:totalWithdrawn,display:USD(totalWithdrawn)},{label:"Final balance",value:balance,display:USD(balance)}];rows=[["Starting amount",USD(amount),"Available retirement savings."],["Starting monthly withdrawal",USD(startingWithdrawal),"First modeled withdrawal."],["Average annual return",`${F(annualReturn*100,2)}%`,"Constant assumed return."],["Annual withdrawal increase",`${F(inflation*100,2)}%`,"Applied monthly at an equivalent rate."],["Estimated duration",duration,perpetual?"Projection capped at 100 years.":`${months} monthly withdrawals.`],["Total withdrawn",USD(totalWithdrawn),"Nominal dollars over time."],["Remaining balance",USD(balance),"Balance at the end of the modeled period."]];result=`<strong>${duration}</strong><br>${USD(amount)} with a starting ${USD(startingWithdrawal)} monthly withdrawal and ${F(inflation*100,2)}% annual increases.`;return finish({months,duration,totalWithdrawn,balance});
}
function syncK401Mode(nextMode){
  const mode=nextMode||document.querySelector('[data-k401-mode].is-active')?.dataset.k401Mode||'projection';
  document.querySelectorAll('[data-k401-mode]').forEach(button=>{const active=button.dataset.k401Mode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-selected',active?'true':'false')});
  document.querySelectorAll('[data-k401-panel]').forEach(panel=>panel.classList.toggle('is-hidden',panel.dataset.k401Panel!==mode));
  document.getElementById('k401ScheduleCard')?.classList.toggle('is-hidden',mode!=='projection');
  return mode;
}
function k401DeferralLimit(age){return 24500+(age>=60&&age<=63?11250:age>=50?8000:0)}
function k401Projection(){
  const mode=syncK401Mode();let valid=true,message='',cards=[],bars=[],rows=[],schedule=[],result='';
  const finish=(payload={})=>({valid,message,mode,cards,bars,rows,schedule,result,...payload});
  if(mode==='projection'){
    const age=Math.floor(V('k401_age')),retirementAge=Math.floor(V('k401_retirement_age')),lifeAge=Math.floor(V('k401_life_age')),salary=Math.max(0,V('k401_salary')),startingBalance=Math.max(0,V('k401_balance')),employeeRate=Math.max(0,V('k401_contribution')/100),matchRate=Math.max(0,V('k401_match')/100),matchLimit=Math.max(0,V('k401_match_limit')/100),salaryGrowth=Math.max(-.99,V('k401_salary_growth')/100),annualReturn=Math.max(-.99,V('k401_return')/100),inflation=Math.max(-.99,V('k401_inflation')/100),retirementReturn=Math.max(-.99,V('k401_retirement_return')/100),workYears=retirementAge-age,retirementYears=lifeAge-retirementAge;
    if(!(workYears>0)){valid=false;message='Retirement age must be greater than current age.';return finish()}if(!(retirementYears>0)){valid=false;message='Life expectancy must be greater than retirement age.';return finish()}
    const monthlyReturn=Math.pow(1+annualReturn,1/12)-1,retirementMonthly=Math.pow(1+retirementReturn,1/12)-1,inflationMonthly=Math.pow(1+inflation,1/12)-1;let balance=startingBalance,totalEmployee=0,totalEmployer=0,totalGrowth=0,yearEmployee=0,yearEmployer=0,yearGrowth=0,currentSalary=salary;
    for(let month=1;month<=workYears*12;month++){
      const employee=currentSalary*employeeRate/12,employer=currentSalary*Math.min(employeeRate,matchLimit)*matchRate/12,growth=balance*monthlyReturn;balance+=employee+employer+growth;totalEmployee+=employee;totalEmployer+=employer;totalGrowth+=growth;yearEmployee+=employee;yearEmployer+=employer;yearGrowth+=growth;
      if(month%12===0){schedule.push({age:age+month/12,salary:currentSalary,employee:yearEmployee,employer:yearEmployer,growth:yearGrowth,balance});currentSalary*=1+salaryGrowth;yearEmployee=0;yearEmployer=0;yearGrowth=0}
    }
    const todayBalance=balance/Math.pow(1+inflation,workYears),firstMonthly=retirementGrowingWithdrawal(balance,retirementMonthly,inflationMonthly,retirementYears*12),todayMonthly=firstMonthly/Math.pow(1+inflation,workYears),firstYearEmployee=salary*employeeRate,limit=k401DeferralLimit(age),limitNote=firstYearEmployee>limit?`${USD(firstYearEmployee-limit)} above the modeled 2026 age-based employee limit.`:`${USD(limit-firstYearEmployee)} below the modeled 2026 age-based employee limit.`;
    cards=[["401(k) at retirement",USD(balance),`${USD(todayBalance)} in today's purchasing power.`],["Starting monthly income",USD(firstMonthly),`${USD(todayMonthly)} in today's purchasing power.`],["Employee contributions",USD(totalEmployee),`${F(employeeRate*100,2)}% of projected salary.`],["Employer contributions",USD(totalEmployer),`${F(matchRate*100,1)}% match up to ${F(matchLimit*100,1)}% of pay.`]];
    bars=[{label:"Starting balance",value:startingBalance,display:USD(startingBalance)},{label:"Employee deposits",value:totalEmployee,display:USD(totalEmployee)},{label:"Employer match",value:totalEmployer,display:USD(totalEmployer)},{label:"Investment growth",value:Math.max(0,totalGrowth),display:USD(totalGrowth)}];
    rows=[["Years until retirement",`${workYears} years`,`Age ${age} to ${retirementAge}.`],["Years modeled in retirement",`${retirementYears} years`,`Through age ${lifeAge}.`],["Starting balance",USD(startingBalance),"Current 401(k) value."],["First-year employee contribution",USD(firstYearEmployee),limitNote],["2026 age-based employee limit",USD(limit),age>=60&&age<=63?"Includes the higher age 60-63 catch-up amount.":age>=50?"Includes the general age 50+ catch-up amount.":"Base elective-deferral limit."],["Total employee contributions",USD(totalEmployee),"Projected salary-based deposits."],["Total employer contributions",USD(totalEmployer),"Assumes the entered match continues."],["Estimated investment growth",USD(totalGrowth),`${F(annualReturn*100,2)}% constant annual return.`],["Balance at retirement",USD(balance),"Before retirement withdrawals and taxes."],["Starting monthly retirement income",USD(firstMonthly),`${F(retirementReturn*100,2)}% return and ${F(inflation*100,2)}% inflation during retirement.`]];
    result=`<strong>${USD(balance)} projected 401(k) balance</strong><br>${USD(firstMonthly)} estimated starting monthly retirement income; ${USD(totalEmployer)} projected employer match.`;return finish({balance,totalEmployee,totalEmployer,totalGrowth,firstMonthly});
  }
  if(mode==='withdrawal'){
    const age=V('k401_withdraw_age'),amount=Math.max(0,V('k401_withdraw_amount')),federal=Math.min(1,Math.max(0,V('k401_federal_tax')/100)),state=Math.min(1,Math.max(0,V('k401_state_tax')/100)),local=Math.min(1,Math.max(0,V('k401_local_tax')/100)),employed=document.getElementById('k401_employed')?.value==='yes',left55=document.getElementById('k401_left_55')?.value==='yes',disability=document.getElementById('k401_disability')?.value==='yes',other=document.getElementById('k401_other_exception')?.value==='yes';
    if(!(amount>0)){valid=false;message='Enter a withdrawal amount greater than zero.';return finish()}
    const ageExempt=age>=59.5,separationExempt=!employed&&left55&&age>=55,penaltyExempt=ageExempt||separationExempt||disability||other,federalTax=amount*federal,stateTax=amount*state,localTax=amount*local,penalty=penaltyExempt?0:amount*.10,totalCost=federalTax+stateTax+localTax+penalty,net=Math.max(0,amount-totalCost),reason=ageExempt?'Age 59.5 or older selected.':separationExempt?'Modeled age-55 separation exception selected.':disability?'Qualifying disability selected.':other?'Other verified exception selected.':'No modeled exception selected.';
    cards=[["Estimated cash received",USD(net),`${F(amount?net/amount*100:0,1)}% of the requested withdrawal.`],["Estimated income taxes",USD(federalTax+stateTax+localTax),"Using the entered marginal rates."],["Additional tax",USD(penalty),penaltyExempt?"No 10% amount modeled.":"10% amount modeled."],["Total estimated cost",USD(totalCost),"Income taxes plus additional tax."]];
    bars=[{label:"Cash received",value:net,display:USD(net)},{label:"Federal tax",value:federalTax,display:USD(federalTax)},{label:"State and local",value:stateTax+localTax,display:USD(stateTax+localTax)},{label:"Additional tax",value:penalty,display:USD(penalty)}];
    rows=[["Requested withdrawal",USD(amount),"Gross distribution."],["Federal income tax estimate",USD(federalTax),`${F(federal*100,2)}% entered rate.`],["State income tax estimate",USD(stateTax),`${F(state*100,2)}% entered rate.`],["Local income tax estimate",USD(localTax),`${F(local*100,2)}% entered rate.`],["Modeled 10% additional tax",USD(penalty),reason],["Total estimated taxes and penalty",USD(totalCost),"Does not model withholding or tax brackets."],["Estimated cash received",USD(net),"Gross distribution minus modeled costs."]];
    result=`<strong>${USD(net)} estimated cash received</strong><br>${USD(totalCost)} in modeled income taxes and additional tax from a ${USD(amount)} withdrawal.`;return finish({amount,net,totalCost,penalty});
  }
  const salary=Math.max(0,V('k401_match_salary')),age=Math.floor(V('k401_match_age')),enteredRate=Math.max(0,V('k401_match_contribution')/100),rate1=Math.max(0,V('k401_match_rate1')/100),limit1=Math.max(0,V('k401_match_limit1')/100),rate2=Math.max(0,V('k401_match_rate2')/100),limit2=Math.max(0,V('k401_match_limit2')/100),periods=Math.max(1,Math.round(V('k401_pay_periods'))),deferralLimit=k401DeferralLimit(age),rawEmployee=salary*enteredRate,employee=Math.min(rawEmployee,deferralLimit),actualRate=salary?employee/salary:0,firstBand=Math.min(actualRate,limit1),secondBand=Math.min(Math.max(0,actualRate-limit1),limit2),employer=salary*(firstBand*rate1+secondBand*rate2),fullEmployer=salary*(limit1*rate1+limit2*rate2),fullRate=(limit1+limit2)*100,ceilingRate=salary?deferralLimit/salary*100:0,captured=fullEmployer?employer/fullEmployer*100:100,combined=employee+employer;
  if(!(salary>0)){valid=false;message='Enter an annual salary greater than zero.';return finish()}
  cards=[["Annual employer match",USD(employer),`${F(captured,1)}% of the stated maximum match.`],["Your annual contribution",USD(employee),rawEmployee>deferralLimit?`Capped at the modeled ${USD(deferralLimit)} 2026 limit.`:`${F(actualRate*100,2)}% of pay.`],["Combined annual contribution",USD(combined),"Employee plus employer amount."],["Contribution rate for full match",`${F(fullRate,2)}%`,`${USD(fullEmployer)} maximum stated match.`]];
  bars=[{label:"Employee contribution",value:employee,display:USD(employee)},{label:"Employer match",value:employer,display:USD(employer)},{label:"Uncaptured match",value:Math.max(0,fullEmployer-employer),display:USD(Math.max(0,fullEmployer-employer))}];
  rows=[["Annual salary",USD(salary),"Entered eligible compensation."],["Age-based 2026 deferral limit",USD(deferralLimit),age>=60&&age<=63?"Includes age 60-63 catch-up.":age>=50?"Includes age 50+ catch-up.":"Base limit."],["Entered contribution rate",`${F(enteredRate*100,2)}%`,`${USD(rawEmployee)} before the modeled limit.`],["Actual employee contribution",USD(employee),`${USD(employee/periods)} per pay period.`],["Employer match",USD(employer),`${USD(employer/periods)} per pay period.`],["Maximum stated employer match",USD(fullEmployer),`Requires at least ${F(fullRate,2)}% of pay, subject to plan terms.`],["Maximum full-year rate before limit",`${F(ceilingRate,2)}%`,`Modeled 2026 limit divided by salary.`],["Combined contribution",USD(combined),"Before investment gains or losses."]];
  result=`<strong>${USD(employer)} estimated annual employer match</strong><br>Contribute at least ${F(fullRate,2)}% of pay to capture the full stated match; modeled combined contribution: ${USD(combined)}.`;return finish({employee,employer,combined,fullEmployer,fullRate});
}
const RMD_UNIFORM_FACTORS=[27.4,26.5,25.5,24.6,23.7,22.9,22.0,21.1,20.2,19.4,18.5,17.7,16.8,16.0,15.2,14.4,13.7,12.9,12.2,11.5,10.8,10.1,9.5,8.9,8.4,7.8,7.3,6.8,6.4,6.0,5.6,5.2,4.9,4.6,4.3,4.1,3.9,3.7,3.5,3.4,3.3,3.1,3.0,2.9,2.8,2.7,2.5,2.3,2.0];
function rmdRequiredAge(birthYear){if(birthYear<=1950)return 72;if(birthYear<=1959)return 73;return 75}
function rmdUniformFactor(age){const whole=Math.floor(age);if(whole<72)return null;if(whole>=120)return 2.0;return RMD_UNIFORM_FACTORS[whole-72]??null}
function rmdJointFactor(ownerAge,spouseAge){const owner=Math.min(120,Math.floor(ownerAge)),spouse=Math.floor(spouseAge),row=RMD_JOINT_TABLE[String(owner)];if(!row||spouse<20)return null;return row[spouse-20]??null}
function rmdProjection(){
  const birthYear=Math.floor(V('rmd_birth_year')),year=Math.floor(V('rmd_year')),balanceInput=Math.max(0,V('rmd_balance')),spouseSolo=document.getElementById('rmd_spouse_solo')?.value==='yes',spouseBirthYear=Math.floor(V('rmd_spouse_birth_year')),annualReturn=Math.max(-.99,V('rmd_return')/100),requestedYears=Math.max(1,Math.min(40,Math.floor(V('rmd_projection_years')))),ownerAge=year-birthYear,spouseAge=year-spouseBirthYear,requiredAge=rmdRequiredAge(birthYear),firstRmdYear=birthYear+requiredAge;
  let valid=true,message='',schedule=[],cards=[],bars=[],rows=[],result='';const finish=(payload={})=>({valid,message,cards,bars,rows,schedule,result,...payload});
  if(!(birthYear>=1900&&birthYear<=year)){valid=false;message='Enter a valid owner birth year that is not after the distribution year.';return finish()}
  if(!(ownerAge>=0&&ownerAge<=120)){valid=false;message='This owner calculator supports ages through 120. Review the birth and distribution years.';return finish()}
  if(!(balanceInput>0)){valid=false;message='Enter a prior December 31 account balance greater than zero.';return finish()}
  if(spouseSolo&&!(spouseBirthYear>=1900&&spouseBirthYear<=year)){valid=false;message='Enter a valid spouse birth year.';return finish()}
  const jointEligible=spouseSolo&&ownerAge-spouseAge>10&&spouseAge>=20,years=Math.min(requestedYears,121-ownerAge);let balance=balanceInput,totalRmd=0;
  for(let offset=0;offset<years;offset++){
    const itemYear=year+offset,age=ownerAge+offset,itemSpouseAge=spouseAge+offset,required=age>=requiredAge,table=jointEligible?'Joint Life Table II':'Uniform Lifetime Table III',period=required?(jointEligible?rmdJointFactor(age,itemSpouseAge):rmdUniformFactor(age)):null;
    if(required&&!period){valid=false;message='The IRS distribution period is unavailable for the entered age combination.';return finish()}
    const rmd=required?balance/period:0,growth=balance*annualReturn,ending=Math.max(0,balance+growth-rmd);
    schedule.push({year:itemYear,age,balance,table,period,rmd,growth,ending,required});totalRmd+=rmd;balance=ending;
  }
  const first=schedule[0],tableNote=jointEligible?'Spouse is sole beneficiary and more than 10 years younger.':spouseSolo?'The age gap is 10 years or less, so Table III applies.':'Default table for most account owners.',deadline=year<firstRmdYear?'No owner RMD is due for this year.':year===firstRmdYear?`April 1, ${year+1} is the latest first-year deadline; the next RMD is still due December 31, ${year+1}.`:`December 31, ${year}.`,rmdRate=first.rmd/balanceInput*100;
  cards=[["Required minimum distribution",USD(first.rmd),first.required?`${F(rmdRate,3)}% of the entered balance.`:"No owner RMD due for this year."],["IRS distribution period",first.period?F(first.period,1):"Not yet applicable",first.table],["Projected year-end balance",USD(first.ending),`${F(annualReturn*100,2)}% return, then year-end RMD.`],["First RMD year",String(firstRmdYear),`Applicable starting age ${requiredAge}.`]];
  bars=[{label:"Required distribution",value:first.rmd,display:USD(first.rmd)},{label:"Projected growth",value:Math.max(0,first.growth),display:USD(first.growth)},{label:"Projected ending balance",value:first.ending,display:USD(first.ending)}];
  rows=[["Owner age in distribution year",String(ownerAge),`Birth year ${birthYear}.`],["Prior December 31 balance",USD(balanceInput),"Balance used for the selected year's calculation."],["RMD starting age",String(requiredAge),`Current law for a person born in ${birthYear}.`],["First RMD year",String(firstRmdYear),deadline],["IRS table",first.table,tableNote],["Distribution period",first.period?F(first.period,1):"Not applicable",first.required?"Balance is divided by this factor.":"The owner has not reached the applicable RMD age."],["Required minimum distribution",USD(first.rmd),first.required?`${F(rmdRate,4)}% of the entered balance.`:"No owner RMD is modeled for the selected year."],["Assumed annual return",`${F(annualReturn*100,2)}%`,"Used only for the future schedule."],["Projected total RMDs",USD(totalRmd),`${schedule.length} displayed year${schedule.length===1?'':'s'} through age ${schedule.at(-1).age}.`]];
  result=first.required?`<strong>${USD(first.rmd)} required minimum distribution for ${year}</strong><br>${first.table}, ${F(first.period,1)} distribution period; ${deadline}`:`<strong>No owner RMD is due for ${year}</strong><br>Based on birth year ${birthYear}, the modeled first RMD year is ${firstRmdYear} at age ${requiredAge}.`;
  return finish({year,ownerAge,spouseAge,requiredAge,firstRmdYear,jointEligible,balanceInput,totalRmd,first});
}
function syncSocialSecurityMode(nextMode){
  const mode=nextMode||document.querySelector('[data-ss-mode].is-active')?.dataset.ssMode||'planner';
  document.querySelectorAll('[data-ss-mode]').forEach(button=>{const active=button.dataset.ssMode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-selected',active?'true':'false')});
  document.querySelectorAll('[data-ss-panel]').forEach(panel=>panel.classList.toggle('is-hidden',panel.dataset.ssPanel!==mode));
  document.getElementById('ssScheduleCard')?.classList.toggle('is-hidden',mode!=='planner');
  return mode;
}
function socialSecurityFraMonths(year){if(year<=1937)return 65*12;if(year<=1942)return 65*12+(year-1937)*2;if(year<=1954)return 66*12;if(year<=1959)return 66*12+(year-1954)*2;return 67*12}
function socialSecurityCreditRate(year){if(year>=1943)return .08;if(year>=1941)return .075;if(year>=1939)return .07;if(year>=1937)return .065;if(year>=1935)return .06;if(year>=1933)return .055;if(year>=1931)return .05;if(year>=1929)return .045;if(year>=1927)return .04;if(year>=1925)return .035;return .03}
function socialSecurityFactor(year,claimMonths){const fra=socialSecurityFraMonths(year),claim=Math.max(62*12,Math.min(70*12,claimMonths));if(claim<fra){const early=fra-claim;return 1-Math.min(36,early)/180-Math.max(0,early-36)/240}return 1+(Math.min(70*12,claim)-fra)*socialSecurityCreditRate(year)/12}
function socialSecurityAgeLabel(months){const years=Math.floor(months/12),extra=Math.round(months-years*12);return extra?`${years} years ${extra} months`:`${years}`}
function socialSecurityPath(claimMonths,monthlyBenefit,lifeMonths,colaAnnual,returnAnnual){const cola=Math.pow(1+colaAnnual,1/12)-1,rate=Math.pow(1+returnAnnual,1/12)-1;let payment=monthlyBenefit,total=0,value=0,monthsPaid=0;for(let month=claimMonths;month<lifeMonths;month++){value=value*(1+rate)+payment;total+=payment;monthsPaid++;payment*=1+cola}return{total,value,monthsPaid,endingPayment:payment}}
function socialSecurityProjection(){
  const mode=syncSocialSecurityMode();let valid=true,message='',cards=[],bars=[],rows=[],schedule=[],result='';const finish=(payload={})=>({valid,message,mode,cards,bars,rows,schedule,result,...payload});
  if(mode==='planner'){
    const birthYear=Math.floor(V('ss_birth_year')),fraBenefit=Math.max(0,V('ss_fra_benefit')),claimMonths=Math.floor(V('ss_claim_years'))*12+Math.floor(V('ss_claim_months')),lifeMonths=Math.floor(V('ss_life_age'))*12,cola=Math.max(-.99,V('ss_cola')/100),annualReturn=Math.max(-.99,V('ss_return')/100),fraMonths=socialSecurityFraMonths(birthYear);
    if(!(fraBenefit>0)){valid=false;message='Enter a full-retirement-age monthly benefit greater than zero.';return finish()}if(claimMonths<62*12||claimMonths>70*12){valid=false;message='Claim age must be between 62 and 70.';return finish()}if(lifeMonths<=claimMonths){valid=false;message='Life expectancy must be greater than the planned claim age.';return finish()}
    const factor=socialSecurityFactor(birthYear,claimMonths),monthly=fraBenefit*factor,path=socialSecurityPath(claimMonths,monthly,lifeMonths,cola,annualReturn);let best=null;
    for(let candidate=62*12;candidate<=70*12;candidate++){if(candidate>=lifeMonths)break;const candidateFactor=socialSecurityFactor(birthYear,candidate),candidateMonthly=fraBenefit*candidateFactor,candidatePath=socialSecurityPath(candidate,candidateMonthly,lifeMonths,cola,annualReturn),item={claimMonths:candidate,factor:candidateFactor,monthly:candidateMonthly,...candidatePath};if(!best||item.value>best.value)best=item;if(candidate%12===0)schedule.push(item)}
    if(!schedule.some(x=>x.claimMonths===claimMonths))schedule.push({claimMonths,factor,monthly,...path});schedule.sort((a,b)=>a.claimMonths-b.claimMonths);
    const fraLabel=socialSecurityAgeLabel(fraMonths),plannedLabel=socialSecurityAgeLabel(claimMonths),adjustment=(factor-1)*100;
    cards=[["Estimated monthly benefit",USD(monthly),`${adjustment>=0?'+':''}${F(adjustment,2)}% versus the entered FRA amount.`],["Modeled value at life expectancy",USD(path.value),`${F(annualReturn*100,2)}% assumed investment return.`],["Total benefits paid",USD(path.total),`${path.monthsPaid} modeled monthly payments.`],["Highest modeled claim age",best?socialSecurityAgeLabel(best.claimMonths):"Unavailable",best?`${USD(best.value)} at life expectancy.`:"Review the inputs."]];
    bars=[{label:"Age 62 monthly",value:fraBenefit*socialSecurityFactor(birthYear,62*12),display:USD(fraBenefit*socialSecurityFactor(birthYear,62*12))},{label:"Planned monthly",value:monthly,display:USD(monthly)},{label:"FRA monthly",value:fraBenefit,display:USD(fraBenefit)},{label:"Age 70 monthly",value:fraBenefit*socialSecurityFactor(birthYear,70*12),display:USD(fraBenefit*socialSecurityFactor(birthYear,70*12))}];
    rows=[["Birth year",String(birthYear),"January 1 birthdays may use the previous year under SSA rules."],["Full retirement age",fraLabel,"Age for the entered unreduced benefit."],["Entered FRA monthly benefit",USD(fraBenefit),"Use an estimate from your SSA record."],["Planned claim age",plannedLabel,claimMonths<fraMonths?"Before full retirement age.":claimMonths>fraMonths?"After full retirement age.":"At full retirement age."],["Claim-age benefit factor",`${F(factor*100,3)}%`,"Applied to the entered FRA benefit."],["Estimated starting monthly benefit",USD(monthly),"Before taxes, Medicare premiums, or earnings-test withholding."],["Total benefits through life expectancy",USD(path.total),`${F(cola*100,2)}% annual COLA assumption.`],["Investment-adjusted value",USD(path.value),`Value at age ${Math.floor(lifeMonths/12)} using ${F(annualReturn*100,2)}% annual return.`],["Highest modeled claim age",best?socialSecurityAgeLabel(best.claimMonths):"Unavailable","Financial model only; not a personal recommendation."]];
    result=`<strong>${USD(monthly)} estimated monthly benefit at age ${plannedLabel}</strong><br>Full retirement age: ${fraLabel}; highest modeled value through age ${Math.floor(lifeMonths/12)} starts at ${best?socialSecurityAgeLabel(best.claimMonths):'an unavailable age'}.`;return finish({monthly,factor,path,best});
  }
  if(mode==='compare'){
    const age1=Math.floor(V('ss_compare_age1_years'))*12+Math.floor(V('ss_compare_age1_months')),age2=Math.floor(V('ss_compare_age2_years'))*12+Math.floor(V('ss_compare_age2_months')),payment1=Math.max(0,V('ss_compare_payment1')),payment2=Math.max(0,V('ss_compare_payment2')),lifeMonths=Math.floor(V('ss_compare_life'))*12,cola=Math.max(-.99,V('ss_compare_cola')/100),annualReturn=Math.max(-.99,V('ss_compare_return')/100);
    if(age1<62*12||age1>70*12||age2<62*12||age2>70*12){valid=false;message='Both claim ages must be between 62 and 70.';return finish()}if(!(payment1>0&&payment2>0)){valid=false;message='Enter both monthly benefit amounts.';return finish()}if(lifeMonths<=Math.max(age1,age2)){valid=false;message='Life expectancy must be greater than both claim ages.';return finish()}
    const path1=socialSecurityPath(age1,payment1,lifeMonths,cola,annualReturn),path2=socialSecurityPath(age2,payment2,lifeMonths,cola,annualReturn);let cumulative1=0,cumulative2=0,p1=payment1,p2=payment2,breakEven=null,colaMonthly=Math.pow(1+cola,1/12)-1,minAge=Math.min(age1,age2);
    for(let month=minAge;month<=120*12;month++){if(month>=age1){cumulative1+=p1;p1*=1+colaMonthly}if(month>=age2){cumulative2+=p2;p2*=1+colaMonthly}if(month>=Math.max(age1,age2)&&((age1<age2&&cumulative2>=cumulative1)||(age2<age1&&cumulative1>=cumulative2))){breakEven=month+1;break}}
    const winner=path1.value>=path2.value?'Option 1':'Option 2',difference=Math.abs(path1.value-path2.value),breakLabel=breakEven?socialSecurityAgeLabel(breakEven):'Not reached by age 120';
    cards=[["Higher modeled value",winner,`${USD(difference)} difference at life expectancy.`],["Option 1 value",USD(path1.value),`Claim at ${socialSecurityAgeLabel(age1)}.`],["Option 2 value",USD(path2.value),`Claim at ${socialSecurityAgeLabel(age2)}.`],["Cumulative break-even age",breakLabel,"Based on benefit payments with entered COLA."]];
    bars=[{label:"Option 1 paid",value:path1.total,display:USD(path1.total)},{label:"Option 2 paid",value:path2.total,display:USD(path2.total)},{label:"Option 1 ending value",value:path1.value,display:USD(path1.value)},{label:"Option 2 ending value",value:path2.value,display:USD(path2.value)}];
    rows=[["Option 1 claim age",socialSecurityAgeLabel(age1),`${USD(payment1)} starting monthly benefit.`],["Option 2 claim age",socialSecurityAgeLabel(age2),`${USD(payment2)} starting monthly benefit.`],["Life expectancy",`${Math.floor(lifeMonths/12)} years`,`Comparison endpoint.`],["Option 1 total paid",USD(path1.total),`${path1.monthsPaid} monthly payments.`],["Option 2 total paid",USD(path2.total),`${path2.monthsPaid} monthly payments.`],["Option 1 investment-adjusted value",USD(path1.value),`${F(annualReturn*100,2)}% assumed return.`],["Option 2 investment-adjusted value",USD(path2.value),`${F(annualReturn*100,2)}% assumed return.`],["Cumulative break-even age",breakLabel,"Ignores taxes and household or survivor benefits."],["Higher value at life expectancy",winner,`${USD(difference)} modeled difference.`]];
    result=`<strong>${winner} has ${USD(difference)} more modeled value</strong><br>Cumulative benefits break even at ${breakLabel}; comparison runs through age ${Math.floor(lifeMonths/12)}.`;return finish({path1,path2,breakEven,winner,difference});
  }
  const status=document.getElementById('ss_earnings_status')?.value||'under',earnings=Math.max(0,V('ss_earnings_income')),monthly=Math.max(0,V('ss_earnings_benefit')),months=Math.max(1,Math.min(12,Math.floor(V('ss_earnings_months')))),annualBenefit=monthly*months,limit=status==='under'?24480:status==='reaches'?65160:Infinity,divisor=status==='under'?2:status==='reaches'?3:Infinity,excess=Number.isFinite(limit)?Math.max(0,earnings-limit):0,withheld=Number.isFinite(divisor)?Math.min(annualBenefit,excess/divisor):0,payable=Math.max(0,annualBenefit-withheld),statusLabel=status==='under'?'Under FRA all year':status==='reaches'?'Reach FRA during 2026':'At or above FRA';
  if(!(monthly>0)){valid=false;message='Enter a monthly retirement benefit greater than zero.';return finish()}
  cards=[["Estimated 2026 benefits payable",USD(payable),`${months} entered benefit months.`],["Estimated benefits withheld",USD(withheld),withheld?`Based on ${USD(excess)} earnings above the limit.`:"No withholding under the selected status."],["Applicable earnings limit",Number.isFinite(limit)?USD(limit):"No limit",statusLabel],["Gross scheduled benefits",USD(annualBenefit),`${USD(monthly)} per month.`]];
  bars=[{label:"Benefits payable",value:payable,display:USD(payable)},{label:"Benefits withheld",value:withheld,display:USD(withheld)}];
  rows=[["2026 age status",statusLabel,"Determines the annual earnings-test rule."],["Countable work earnings",USD(earnings),status==='reaches'?"Enter only earnings before the FRA month.":"Wages and net self-employment income."],["Applicable exempt amount",Number.isFinite(limit)?USD(limit):"No limit",status==='under'?"2026 lower exempt amount.":status==='reaches'?"2026 higher exempt amount.":"No earnings test beginning with the FRA month."],["Earnings above exempt amount",USD(excess),"Countable earnings minus the applicable limit."],["Gross scheduled benefits",USD(annualBenefit),`${months} months at ${USD(monthly)}.`],["Estimated withheld benefits",USD(withheld),status==='under'?"$1 withheld per $2 above the limit.":status==='reaches'?"$1 withheld per $3 above the limit.":"No withholding modeled."],["Estimated benefits payable",USD(payable),"Before taxes, Medicare premiums, or other deductions."]];
  result=`<strong>${USD(payable)} estimated 2026 benefits payable</strong><br>${USD(withheld)} withheld under the selected earnings-test status from ${USD(annualBenefit)} scheduled benefits.`;return finish({payable,withheld,annualBenefit,limit});
}
function syncFinanceTarget(){const target=document.getElementById('finance_solve')?.value||'fv';document.querySelectorAll('[data-finance-value]').forEach(field=>{const active=field.dataset.financeValue===target;field.classList.toggle('finance-solve-target',active);const input=field.querySelector('input');if(input){input.disabled=active;input.setAttribute('aria-disabled',active?'true':'false')}});return target}
function financePeriodicRate(annual,py,cy){return Math.pow(1+annual/100/cy,cy/py)-1}
function financeNominalRate(periodic,py,cy){return cy*(Math.pow(1+periodic,py/cy)-1)*100}
function financeEquation(rate,n,pv,pmt,fv,due){if(rate<=-1)return NaN;const growth=Math.pow(1+rate,n),annuity=Math.abs(rate)<1e-12?n:(growth-1)/rate;return pv*growth+pmt*(due?1+rate:1)*annuity+fv}
function solveFinanceRate(n,pv,pmt,fv,due){const fn=r=>financeEquation(r,n,pv,pmt,fv,due),points=[];for(let i=0;i<=800;i++){const x=i/800;points.push(-.9999+x*.9999);points.push(Math.pow(10,x*3)-1)}points.sort((a,b)=>a-b);let previous=points[0],fp=fn(previous);for(let i=1;i<points.length;i++){const current=points[i],fc=fn(current);if(Number.isFinite(fc)&&Math.abs(fc)<1e-9)return current;if(Number.isFinite(fp)&&Number.isFinite(fc)&&fp*fc<0){let lo=previous,hi=current,flo=fp;for(let j=0;j<120;j++){const mid=(lo+hi)/2,fm=fn(mid);if(Math.abs(fm)<1e-11)return mid;if(flo*fm<=0)hi=mid;else{lo=mid;flo=fm}}return(lo+hi)/2}previous=current;fp=fc}return NaN}
function financeProjection(){const target=syncFinanceTarget(),py=Math.max(1,Math.round(V('finance_py'))),cy=Math.max(1,Math.round(V('finance_cy'))),due=document.getElementById('finance_timing')?.value==='beginning';let n=V('finance_n'),iy=V('finance_iy'),pv=V('finance_pv'),pmt=V('finance_pmt'),fv=V('finance_fv'),rate=financePeriodicRate(iy,py,cy),valid=true,message='';if(!Number.isFinite(n)||!Number.isFinite(iy)||!Number.isFinite(pv)||!Number.isFinite(pmt)||!Number.isFinite(fv)||n<0){valid=false;message='Enter finite values and a nonnegative number of periods.'}if(valid&&target!=='iy'&&(!Number.isFinite(rate)||rate<=-1)){valid=false;message='The entered annual rate is not valid for these compounding settings.'}if(valid&&target==='fv'){const growth=Math.pow(1+rate,n),annuity=Math.abs(rate)<1e-12?n:(growth-1)/rate;fv=-(pv*growth+pmt*(due?1+rate:1)*annuity)}else if(valid&&target==='pv'){const growth=Math.pow(1+rate,n),annuity=Math.abs(rate)<1e-12?n:(growth-1)/rate;pv=-(fv+pmt*(due?1+rate:1)*annuity)/growth}else if(valid&&target==='pmt'){const growth=Math.pow(1+rate,n),annuity=(Math.abs(rate)<1e-12?n:(growth-1)/rate)*(due?1+rate:1);if(Math.abs(annuity)<1e-12){valid=false;message='Payment cannot be solved when the annuity factor is zero.'}else pmt=-(fv+pv*growth)/annuity}else if(valid&&target==='iy'){rate=solveFinanceRate(n,pv,pmt,fv,due);if(!Number.isFinite(rate)){valid=false;message='No practical real interest-rate solution was found. Check the cash-flow signs.'}else iy=financeNominalRate(rate,py,cy)}else if(valid&&target==='n'){if(Math.abs(rate)<1e-12){if(Math.abs(pmt)<1e-12){valid=false;message='N cannot be solved when both the rate and payment are zero.'}else n=-(pv+fv)/pmt}else{const adjusted=pmt*(due?1+rate:1),ratio=(adjusted/rate-fv)/(pv+adjusted/rate);if(!(ratio>0)){valid=false;message='No positive real period solution was found. Check the cash-flow signs.'}else n=Math.log(ratio)/Math.log(1+rate)}if(!(n>=0)&&valid){valid=false;message='The entered cash flows imply a negative number of periods.'}}if(valid&&(![n,iy,pv,pmt,fv,rate].every(Number.isFinite)||n>1000000)){valid=false;message='The calculation exceeds the supported numeric range. Reduce the rate or number of periods.'}
  if(!valid)return{valid:false,target,message,py,cy,due,n,iy,pv,pmt,fv,rate,schedule:[]};
  const solved={n,iy,pv,pmt,fv},input=document.getElementById(`finance_${target}`);if(input)input.value=Number(solved[target].toPrecision(12));const whole=Math.floor(n+1e-10),fraction=Math.max(0,n-whole),displayPeriods=Math.min(whole,600),schedule=[];let running=pv;for(let period=1;period<=displayPeriods;period++){const opening=running,payment=pmt,interest=due?(running+payment)*rate:running*rate;running=due?(running+payment)*(1+rate):running*(1+rate)+payment;schedule.push({period:String(period),opening,payment,interest,ending:running})}if(whole<=600&&fraction>1e-8){const opening=running,payment=pmt*fraction,partialRate=Math.pow(1+rate,fraction)-1,interest=due?(running+payment)*partialRate:running*partialRate;running=due?(running+payment)*(1+partialRate):running*(1+partialRate)+payment;schedule.push({period:`${whole+1} (${F(fraction,3)} partial)`,opening,payment,interest,ending:running})}const effectiveAnnual=(Math.pow(1+rate,py)-1)*100,totalPayments=pmt*n,balance=-fv,totalInterest=balance-pv-totalPayments,residual=financeEquation(rate,n,pv,pmt,fv,due),scheduleCapped=whole>600;return{valid:true,target,py,cy,due,n,iy,pv,pmt,fv,rate,effectiveAnnual,totalPayments,totalInterest,residual,balance,schedule,scheduleCapped};}
function debtMonthLabel(start,month){const date=new Date(start.getFullYear(),start.getMonth()+Math.max(0,month-1),1);return date.toLocaleDateString('en-US',{month:'long',year:'numeric'})}
function simulateDebtPayoff(source,strategy,extra,start){
  const debts=source.map(item=>({...item,balance:item.balance,paidMonth:0})),monthlyBudget=debts.reduce((sum,item)=>sum+item.minimum,0)+extra,initial=debts.reduce((sum,item)=>sum+item.balance,0),schedule=[{month:0,balance:initial}],order=[];let interest=0,totalPaid=0,month=0;
  while(month<1200&&debts.some(item=>item.balance>.005)){
    month++;let available=monthlyBudget;
    for(const debt of debts){if(debt.balance<=.005)continue;const charge=debt.balance*debt.apr/1200;debt.balance+=charge;interest+=charge}
    for(const debt of debts){if(debt.balance<=.005)continue;const payment=Math.min(debt.balance,debt.minimum,available);debt.balance-=payment;available-=payment;totalPaid+=payment;if(debt.balance<=.005&&!debt.paidMonth){debt.balance=0;debt.paidMonth=month;order.push({name:debt.name,month,index:debt.index})}}
    let guard=0;
    while(available>.005&&debts.some(item=>item.balance>.005)&&guard++<debts.length+1){const open=debts.filter(item=>item.balance>.005).sort((a,b)=>strategy==='snowball'?(a.balance-b.balance||b.apr-a.apr||a.index-b.index):(b.apr-a.apr||a.balance-b.balance||a.index-b.index)),target=open[0],payment=Math.min(target.balance,available);target.balance-=payment;available-=payment;totalPaid+=payment;if(target.balance<=.005&&!target.paidMonth){target.balance=0;target.paidMonth=month;order.push({name:target.name,month,index:target.index})}}
    const remaining=debts.reduce((sum,item)=>sum+Math.max(0,item.balance),0);if(month%12===0||remaining<=.005)schedule.push({month,balance:remaining});
  }
  const valid=!debts.some(item=>item.balance>.005);return{valid,strategy,months:month,interest,totalPaid,monthlyBudget,initial,schedule,order,payoffLabel:valid?debtMonthLabel(start,month):'Not paid off within 100 years'};
}
function debtPayoffProjection(){
  const debts=[];for(let index=1;index<=4;index++){const balance=V(`debt_${index}_balance`),apr=V(`debt_${index}_apr`),minimum=V(`debt_${index}_minimum`),name=(document.getElementById(`debt_${index}_name`)?.value||`Debt ${index}`).trim()||`Debt ${index}`;if(balance>0)debts.push({index,name,balance,apr,minimum})}
  const extra=Math.max(0,V('debt_extra')),strategy=document.getElementById('debt_strategy')?.value||'avalanche',start=monthDate('debt_start');let message='';if(!debts.length)message='Enter at least one debt with a positive balance.';else if(debts.some(item=>!Number.isFinite(item.apr)||item.apr<0||item.apr>100))message='Enter an APR from 0% to 100% for every active debt.';else if(debts.some(item=>!(item.minimum>0)))message='Enter a minimum payment greater than zero for every active debt.';
  if(message)return{valid:false,message,debts,extra,strategy,start};const avalanche=simulateDebtPayoff(debts,'avalanche',extra,start),snowball=simulateDebtPayoff(debts,'snowball',extra,start),baseline=simulateDebtPayoff(debts,'avalanche',0,start),selected=strategy==='snowball'?snowball:avalanche;if(!selected.valid)message='The entered budget does not pay every balance within 100 years. Increase payments or review the APRs.';return{valid:selected.valid,message,debts,extra,strategy,start,avalanche,snowball,baseline,selected,totalBalance:debts.reduce((sum,item)=>sum+item.balance,0),minimums:debts.reduce((sum,item)=>sum+item.minimum,0)};
}
function salaryProjection(){const current=Math.max(0,V('salary')),unit=document.getElementById('raise_unit')?.value||'percent',entered=V('raise_amount'),raiseDollars=unit==='dollar'?entered:current*entered/100,raisePercent=current?raiseDollars/current*100:0,annual=Math.max(0,current+raiseDollars),periods=Math.max(1,Math.floor(V('pay_periods'))),hours=Math.max(.1,V('hours_week')),weeks=Math.max(.1,V('weeks_year')),inflation=Math.max(-99,V('inflation_rate')),realRaise=((1+raisePercent/100)/(1+inflation/100)-1)*100;return{current,unit,entered,raiseDollars,raisePercent,annual,periods,hours,weeks,inflation,realRaise,monthly:annual/12,perPeriod:annual/periods,weekly:annual/weeks,hourly:annual/(hours*weeks),oldMonthly:current/12,oldPerPeriod:current/periods,oldWeekly:current/weeks,oldHourly:current/(hours*weeks)}}
function discountProjection(){const price=Math.max(0,V('price')),first=Math.max(0,Math.min(100,V('discount'))),second=Math.max(0,Math.min(100,V('discount_two'))),quantity=Math.max(1,Math.floor(V('quantity'))),taxRate=Math.max(0,V('sales_tax')),fees=Math.max(0,V('checkout_fees')),multiplier=(1-first/100)*(1-second/100),unitPrice=price*multiplier,effective=(1-multiplier)*100,subtotal=unitPrice*quantity,savings=(price-unitPrice)*quantity,tax=subtotal*taxRate/100,total=subtotal+tax+fees;return{price,first,second,quantity,taxRate,fees,multiplier,unitPrice,effective,subtotal,savings,tax,total}}
const FEDERAL_2026={single:[[12400,.10],[50400,.12],[105700,.22],[201775,.24],[256225,.32],[640600,.35],[Infinity,.37]],joint:[[24800,.10],[100800,.12],[211400,.22],[403550,.24],[512450,.32],[768700,.35],[Infinity,.37]],head:[[17700,.10],[67450,.12],[105700,.22],[201750,.24],[256200,.32],[640600,.35],[Infinity,.37]]};
const STANDARD_DEDUCTION_2026={single:16100,joint:32200,head:24150};
function progressiveTax(income,brackets){let tax=0,lower=0;for(const[upper,rate]of brackets){const amount=Math.max(0,Math.min(income,upper)-lower);tax+=amount*rate;if(income<=upper)break;lower=upper}return tax}
function marginalRate(income,brackets){return(brackets.find(([upper])=>income<=upper)||brackets.at(-1))[1]}
function syncPayDeductionFields(){const custom=document.getElementById('pay_deduction_mode')?.value==='custom';document.querySelectorAll('[data-pay-custom]').forEach(el=>el.classList.toggle('is-hidden',!custom));return custom}
function takeHomeProjection(){const gross=Math.max(0,V('pay_gross')),status=document.getElementById('pay_status')?.value||'single',periods=Math.max(1,Math.floor(V('pay_periods'))),retirement=Math.max(0,V('pay_retirement')),pretax=Math.max(0,V('pay_pretax')),posttax=Math.max(0,V('pay_posttax')),stateRate=Math.max(0,V('pay_state_rate')),extraPerPay=Math.max(0,V('pay_extra')),custom=syncPayDeductionFields(),deduction=custom?Math.max(0,V('pay_custom_deduction')):STANDARD_DEDUCTION_2026[status],federalTaxable=Math.max(0,gross-retirement-pretax-deduction),brackets=FEDERAL_2026[status],federal=progressiveTax(federalTaxable,brackets),marginal=marginalRate(federalTaxable,brackets),ficaWages=Math.max(0,gross-pretax),social=Math.min(ficaWages,184500)*.062,medicareThreshold=status==='joint'?250000:200000,medicare=ficaWages*.0145+Math.max(0,ficaWages-medicareThreshold)*.009,stateTaxable=Math.max(0,gross-retirement-pretax),state=stateTaxable*stateRate/100,extra=extraPerPay*periods,totalTax=federal+social+medicare+state+extra,totalDeductions=retirement+pretax+posttax,net=Math.max(0,gross-totalTax-totalDeductions),effective=gross?totalTax/gross*100:0;return{gross,status,periods,retirement,pretax,posttax,stateRate,extraPerPay,extra,deduction,custom,federalTaxable,federal,marginal,ficaWages,social,medicareThreshold,medicare,stateTaxable,state,totalTax,totalDeductions,net,effective,perPay:net/periods,grossPerPay:gross/periods,monthly:net/12}}
function syncSalesTaxFields(){const mode=document.getElementById('sales_mode')?.value||'add';document.querySelectorAll('[data-sales-add],[data-sales-reverse],[data-sales-rate]').forEach(el=>{const show=(mode==='add'&&el.hasAttribute('data-sales-add'))||(mode==='reverse'&&el.hasAttribute('data-sales-reverse'))||(mode==='rate'&&el.hasAttribute('data-sales-rate'));el.classList.toggle('is-hidden',!show)});document.querySelectorAll('[data-sales-rate-input]').forEach(el=>el.classList.toggle('is-hidden',mode==='rate'));return mode}
function salesTaxProjection(){const mode=syncSalesTaxFields();let rate=Math.max(0,V('sales_rate')),before=0,tax=0,after=0,price=Math.max(0,V('sales_price')),quantity=1,discount=0,discountedUnit=price,merchandise=0,shipping=0,taxableBase=0,savings=0,shippingTaxable=false;if(mode==='reverse'){after=Math.max(0,V('sales_total'));before=after/(1+rate/100);tax=after-before;taxableBase=before;merchandise=before}else if(mode==='rate'){before=price;after=Math.max(0,V('sales_after'));tax=Math.max(0,after-before);rate=before?tax/before*100:0;taxableBase=before;merchandise=before}else{quantity=Math.max(1,Math.floor(V('sales_quantity')));discount=Math.max(0,Math.min(100,V('sales_discount')));discountedUnit=price*(1-discount/100);merchandise=discountedUnit*quantity;shipping=Math.max(0,V('sales_shipping'));shippingTaxable=document.getElementById('sales_shipping_taxable')?.value==='yes';taxableBase=merchandise+(shippingTaxable?shipping:0);tax=taxableBase*rate/100;before=merchandise+shipping;after=before+tax;savings=(price-discountedUnit)*quantity}return{mode,rate,before,tax,after,price,quantity,discount,discountedUnit,merchandise,shipping,taxableBase,savings,shippingTaxable}}
function syncPercentFields(){const mode=document.getElementById('percent_mode')?.value||'percent_of';document.querySelectorAll('[data-percent-mode]').forEach(el=>el.classList.toggle('is-hidden',el.dataset.percentMode!==mode));return mode}
function percentageProjection(){const mode=syncPercentFields();let result=0,answer='',detail='',formula='',valid=true,a=0,b=0,change=0,average=0,direction='';if(mode==='what_percent'){a=V('pct_part');b=V('pct_whole');valid=b!==0;result=valid?a/b*100:0;answer=valid?`${F(result,4)}%`:'Undefined';detail=valid?`${F(a,4)} is ${F(result,4)}% of ${F(b,4)}.`:'The whole cannot be zero.';formula='part / whole x 100'}else if(mode==='find_whole'){a=V('pct_known_part');b=V('pct_known_percent');valid=b!==0;result=valid?a/(b/100):0;answer=valid?F(result,4):'Undefined';detail=valid?`${F(a,4)} is ${F(b,4)}% of ${F(result,4)}.`:'The percentage cannot be zero.';formula='part / (percentage / 100)'}else if(mode==='change'){a=V('pct_old');b=V('pct_new');change=b-a;valid=a!==0;result=valid?change/Math.abs(a)*100:0;direction=result>0?'increase':result<0?'decrease':'no change';answer=valid?`${result>0?'+':''}${F(result,4)}%`:'Undefined';detail=valid?`${F(a,4)} to ${F(b,4)} is a ${F(Math.abs(result),4)}% ${direction}.`:'Percent change from an original value of zero is undefined.';formula='(new - original) / |original| x 100'}else if(mode==='difference'){a=V('pct_value_one');b=V('pct_value_two');change=Math.abs(a-b);average=(Math.abs(a)+Math.abs(b))/2;valid=average!==0;result=valid?change/average*100:0;answer=valid?`${F(result,4)}%`:'Undefined';detail=valid?`${F(a,4)} and ${F(b,4)} differ by ${F(result,4)}%.`:'Percentage difference is undefined when both values are zero.';formula='|value 1 - value 2| / average magnitude x 100'}else if(mode==='adjust'){a=V('pct_base');b=Math.max(0,V('pct_adjust'));direction=document.getElementById('pct_direction')?.value||'increase';change=a*b/100*(direction==='decrease'?-1:1);result=a+change;answer=F(result,4);detail=`${F(a,4)} ${direction}d by ${F(b,4)}% is ${F(result,4)}.`;formula=`starting value x (1 ${direction==='decrease'?'-':'+'} percentage / 100)`}else{a=V('pct_percent');b=V('pct_value');result=a/100*b;answer=F(result,4);detail=`${F(a,4)}% of ${F(b,4)} is ${F(result,4)}.`;formula='percentage / 100 x whole'}return{mode,result,answer,detail,formula,valid,a,b,change,average,direction}}
function fractionGcd(a,b){a=Math.abs(Math.trunc(a));b=Math.abs(Math.trunc(b));while(b){const t=b;b=a%b;a=t}return a||1}
function fractionNormalize(n,d){n=Math.trunc(n);d=Math.trunc(d);if(!Number.isFinite(n)||!Number.isFinite(d)||d===0)return null;if(d<0){n=-n;d=-d}const divisor=fractionGcd(n,d);return{n:n/divisor,d:d/divisor,gcd:divisor}}
function fractionMixed(whole,num,den){whole=Math.trunc(whole);num=Math.trunc(num);den=Math.trunc(den);if(den===0)return null;const sign=(whole<0||num<0?-1:1)*(den<0?-1:1);return fractionNormalize(sign*(Math.abs(whole)*Math.abs(den)+Math.abs(num)),Math.abs(den))}
function fractionText(value){if(!value)return'Undefined';return value.d===1?String(value.n):`${value.n}/${value.d}`}
function mixedText(value){if(!value)return'Undefined';if(value.n===0)return'0';const sign=value.n<0?'-':'',absolute=Math.abs(value.n),whole=Math.floor(absolute/value.d),remainder=absolute%value.d;if(!remainder)return`${sign}${whole}`;return whole?`${sign}${whole} ${remainder}/${value.d}`:`${sign}${remainder}/${value.d}`}
function decimalFraction(){const input=document.getElementById('fraction_decimal'),raw=(input?.value||'0').trim(),value=Number(raw);if(!Number.isFinite(value))return null;let normalized=raw.toLowerCase();if(normalized.includes('e'))normalized=value.toFixed(12).replace(/0+$/,'').replace(/\.$/,'');const decimals=(normalized.split('.')[1]||'').length,scale=Math.pow(10,Math.min(12,decimals)),numerator=Math.round(value*scale);return fractionNormalize(numerator,scale)}
function syncFractionFields(){const mode=document.getElementById('fraction_mode')?.value||'arithmetic';document.querySelectorAll('[data-fraction-mode]').forEach(el=>el.classList.toggle('is-hidden',el.dataset.fractionMode!==mode));return mode}
function fractionProjection(){const mode=syncFractionFields();let a=null,b=null,result=null,rawN=0,rawD=1,operator='',operation='',step='',lcd=0;if(mode==='decimal'){result=decimalFraction();const decimal=Number(document.getElementById('fraction_decimal')?.value||0);return{mode,valid:!!result,a:null,b:null,result,rawN:result?.n||0,rawD:result?.d||1,operator:'=',operation:'Decimal conversion',step:`${F(decimal,12)} expressed over a power of 10 and reduced.`,lcd:0}}if(mode==='simplify'){rawN=Math.trunc(V('frac_simple_num'));rawD=Math.trunc(V('frac_simple_den'));result=fractionNormalize(rawN,rawD);return{mode,valid:!!result,a:null,b:null,result,rawN,rawD,operator:'=',operation:'Simplification',step:result?`Divide numerator and denominator by ${fractionGcd(rawN,rawD)}.`:'A denominator of zero is undefined.',lcd:0}}a=fractionMixed(V('frac_a_whole'),V('frac_a_num'),V('frac_a_den'));b=fractionMixed(V('frac_b_whole'),V('frac_b_num'),V('frac_b_den'));operation=document.getElementById('fraction_operation')?.value||'add';operator={add:'+',subtract:'-',multiply:'x',divide:'/'}[operation];if(!a||!b)return{mode,valid:false,a,b,result:null,rawN:0,rawD:0,operator,operation,step:'Each denominator must be nonzero.',lcd:0};if(operation==='add'||operation==='subtract'){rawD=a.d*b.d;rawN=operation==='add'?a.n*b.d+b.n*a.d:a.n*b.d-b.n*a.d;lcd=Math.abs(a.d*b.d)/fractionGcd(a.d,b.d);step=`Use common denominator ${lcd}, combine the numerators, then reduce.`}else if(operation==='multiply'){rawN=a.n*b.n;rawD=a.d*b.d;step='Multiply the numerators and denominators, then reduce.'}else{if(b.n===0)return{mode,valid:false,a,b,result:null,rawN:0,rawD:0,operator,operation,step:'Division by a zero fraction is undefined.',lcd:0};rawN=a.n*b.d;rawD=a.d*b.n;step='Multiply the first fraction by the reciprocal of the second, then reduce.'}result=fractionNormalize(rawN,rawD);return{mode,valid:!!result,a,b,result,rawN,rawD,operator,operation,step,lcd}}
function ratioParseDecimal(raw){raw=String(raw??'').trim();if(!/^\+?(?:\d+(?:\.\d{0,6})?|\.\d{1,6})$/.test(raw))return null;raw=raw.replace(/^\+/,'');const parts=raw.split('.'),decimals=(parts[1]||'').length,den=Math.pow(10,decimals),num=Math.round(Number(raw)*den);return Number.isSafeInteger(num)&&Number.isSafeInteger(den)?fractionNormalize(num,den):null}
function ratioParse(raw){raw=String(raw??'').trim();if(!raw)return null;const slash=raw.split('/');if(slash.length===1)return ratioParseDecimal(raw);if(slash.length!==2)return null;const left=ratioParseDecimal(slash[0]),right=ratioParseDecimal(slash[1]);if(!left||!right||right.n===0)return null;const n=left.n*right.d,d=left.d*right.n;return Number.isSafeInteger(n)&&Number.isSafeInteger(d)?fractionNormalize(n,d):null}
function ratioLcm(a,b){const value=Math.abs(a/fractionGcd(a,b)*b);return Number.isSafeInteger(value)?value:NaN}
function ratioText(values){return values.map(value=>F(value,8)).join(' : ')}
function syncRatioFields(){const mode=document.getElementById('ratio_mode')?.value||'simplify';document.querySelectorAll('[data-ratio-base]').forEach(el=>el.classList.toggle('is-hidden',mode==='proportion'));document.querySelectorAll('[data-ratio-scale]').forEach(el=>el.classList.toggle('is-hidden',mode!=='scale'));document.querySelectorAll('[data-ratio-split]').forEach(el=>el.classList.toggle('is-hidden',mode!=='split'));document.querySelectorAll('[data-ratio-proportion]').forEach(el=>el.classList.toggle('is-hidden',mode!=='proportion'));const title=document.getElementById('ratioChartTitle');if(title)title.textContent=mode==='proportion'?'Proportion Terms':mode==='split'?'Allocated Shares':mode==='scale'?'Scaled Ratio Parts':'Ratio Parts';return mode}
function ratioBaseParts(){const ids=['ratio_a','ratio_b','ratio_c'],raw=ids.map(id=>(document.getElementById(id)?.value||'').trim()),used=raw[2]?[0,1,2]:[0,1],rationals=used.map(index=>ratioParse(raw[index]));if(rationals.some(value=>!value||value.n<=0))return{valid:false,message:'Enter positive whole numbers, decimals, or simple fractions for Parts A and B. Part C is optional.'};let common=1;for(const value of rationals){common=ratioLcm(common,value.d);if(!Number.isFinite(common))return{valid:false,message:'The entered values are too large or precise to simplify safely.'}}const integers=rationals.map(value=>value.n*(common/value.d));if(integers.some(value=>!Number.isSafeInteger(value)))return{valid:false,message:'The entered values are too large or precise to simplify safely.'};const divisor=integers.reduce((g,value)=>fractionGcd(g,value)),terms=integers.map(value=>value/divisor),values=rationals.map(value=>value.n/value.d),sum=values.reduce((a,b)=>a+b,0),termSum=terms.reduce((a,b)=>a+b,0);return{valid:true,raw:used.map(index=>raw[index]),rationals,integers,common,divisor,terms,values,sum,termSum}}
function ratioProjection(){const mode=syncRatioFields();if(mode==='proportion'){const ids=['ratio_pa','ratio_pb','ratio_pc','ratio_pd'],labels=['A','B','C','D'],raw=ids.map(id=>(document.getElementById(id)?.value||'').trim()),missing=raw.map((value,index)=>value?null:index).filter(value=>value!==null);if(missing.length!==1)return{valid:false,mode,message:'Leave exactly one proportion value blank.'};const parsed=raw.map(value=>value?ratioParse(value):null);if(parsed.some((value,index)=>index!==missing[0]&&(!value||value.n<=0)))return{valid:false,mode,message:'Enter three positive whole numbers, decimals, or simple fractions.'};const values=parsed.map(value=>value?value.n/value.d:null),index=missing[0];let solved=0;if(index===0)solved=values[1]*values[2]/values[3];else if(index===1)solved=values[0]*values[3]/values[2];else if(index===2)solved=values[0]*values[3]/values[1];else solved=values[1]*values[2]/values[0];if(!Number.isFinite(solved)||solved<=0)return{valid:false,mode,message:'The proportion cannot be solved from those values.'};values[index]=solved;const equation=`${F(values[0],8)} : ${F(values[1],8)} = ${F(values[2],8)} : ${F(values[3],8)}`,leftProduct=values[0]*values[3],rightProduct=values[1]*values[2];return{valid:true,mode,values,index,label:labels[index],solved,equation,leftProduct,rightProduct}}const base=ratioBaseParts();if(!base.valid)return{...base,mode};if(mode==='scale'){const factorValue=ratioParse(document.getElementById('ratio_factor')?.value||'');if(!factorValue||factorValue.n<=0)return{valid:false,mode,message:'Enter a positive scale factor.'};const factor=factorValue.n/factorValue.d,scaled=base.values.map(value=>value*factor);return{...base,valid:true,mode,factor,scaled}}if(mode==='split'){const total=V('ratio_total');if(!(total>0))return{valid:false,mode,message:'Enter a total greater than zero.'};const shares=base.values.map(value=>total*value/base.sum),check=shares.reduce((a,b)=>a+b,0);return{...base,valid:true,mode,total,shares,check}}return{...base,valid:true,mode}}
function statsProjection(){const raw=document.getElementById('stats_values')?.value||'',tokens=raw.trim()?raw.trim().split(/[,;\s]+/).filter(Boolean):[],values=tokens.map(Number),invalid=tokens.filter((_,i)=>!Number.isFinite(values[i])),type=document.getElementById('stats_type')?.value||'population',z=Number(document.getElementById('stats_confidence')?.value||1.96),confidence=document.getElementById('stats_confidence')?.selectedOptions[0]?.textContent.split(' ')[0]||'95%',nums=values.filter(Number.isFinite),n=nums.length;if(!n||invalid.length||type==='sample'&&n<2)return{valid:false,message:invalid.length?`Invalid value: ${invalid[0]}`:type==='sample'?'A sample needs at least two values.':'Enter at least one number.',type,values:nums,n};const sum=nums.reduce((a,b)=>a+b,0),mean=sum/n,sorted=[...nums].sort((a,b)=>a-b),mid=Math.floor(n/2),median=n%2?sorted[mid]:(sorted[mid-1]+sorted[mid])/2,min=sorted[0],max=sorted[n-1],range=max-min,squared=nums.map(value=>({value,deviation:value-mean,square:(value-mean)**2})),sumSquares=squared.reduce((total,item)=>total+item.square,0),populationVariance=Math.max(0,sumSquares/n),sampleVariance=n>1?Math.max(0,sumSquares/(n-1)):null,populationSd=Math.sqrt(populationVariance),sampleSd=sampleVariance===null?null:Math.sqrt(sampleVariance),variance=type==='sample'?sampleVariance:populationVariance,sd=type==='sample'?sampleSd:populationSd,standardError=sd/Math.sqrt(n),margin=z*standardError,coefficient=mean!==0?sd/Math.abs(mean)*100:null;return{valid:true,type,z,confidence,values:nums,n,sum,mean,sorted,median,min,max,range,squared,sumSquares,populationVariance,sampleVariance,populationSd,sampleSd,variance,sd,standardError,margin,coefficient}}
function syncBmiFields(){const metric=document.getElementById('bmi_units')?.value==='metric';document.querySelectorAll('[data-bmi-us]').forEach(el=>el.classList.toggle('is-hidden',metric));document.querySelectorAll('[data-bmi-metric]').forEach(el=>el.classList.toggle('is-hidden',!metric));return metric}
function bmiProjection(){const metric=syncBmiFields(),feet=V('bmi_height_ft'),inches=V('bmi_height_in'),weightLb=metric?V('bmi_weight_kg')/0.45359237:V('bmi_weight_lb'),heightIn=metric?V('bmi_height_cm')/2.54:feet*12+inches,kg=weightLb*0.45359237,meters=heightIn*0.0254,valid=weightLb>0&&heightIn>0&&(metric||feet>0&&inches>=0&&inches<12);if(!valid)return{valid:false,message:metric?'Enter a positive weight and height.':'Enter positive weight and feet, with additional inches from 0 to less than 12.',metric};const bmi=kg/(meters*meters),category=bmi<18.5?'Underweight':bmi<25?'Healthy Weight':bmi<30?'Overweight':bmi<35?'Obesity, Class 1':bmi<40?'Obesity, Class 2':'Obesity, Class 3',lowKg=18.5*meters*meters,highKg=24.9*meters*meters,lowLb=lowKg/0.45359237,highLb=highKg/0.45359237,bmiPrime=bmi/25,ponderal=kg/(meters*meters*meters),difference=bmi<18.5?lowKg-kg:bmi>=25?kg-highKg:0,direction=bmi<18.5?'below':bmi>=25?'above':'within';return{valid:true,metric,feet,inches,weightLb,heightIn,kg,meters,bmi,category,lowKg,highKg,lowLb,highLb,bmiPrime,ponderal,difference,direction}}
function salaryConverterProjection(){const amount=Math.max(0,V('salary_amount')),period=document.getElementById('salary_period')?.value||'hour',hours=V('salary_hours_week'),days=V('salary_days_week'),holidays=Math.max(0,V('salary_holidays')),vacation=Math.max(0,V('salary_vacation')),valid=Number.isFinite(amount)&&hours>0&&days>0&&days<=7;if(!valid)return{valid:false};const multipliers={hour:hours*52,day:days*52,week:52,biweekly:26,semimonthly:24,month:12,quarter:4,year:1},annual=amount*multipliers[period],workdays=days*52,daysOff=Math.min(workdays,holidays+vacation),factor=workdays?(workdays-daysOff)/workdays:0,adjustedAnnual=annual*factor,hoursDay=hours/days,workedHours=(workdays-daysOff)*hoursDay,effectiveHourly=workedHours?annual/workedHours:0;const convert=value=>({hour:value/(hours*52),day:value/(days*52),week:value/52,biweekly:value/26,semimonthly:value/24,month:value/12,quarter:value/4,year:value});return{valid:true,amount,period,hours,days,holidays,vacation,annual,workdays,daysOff,factor,adjustedAnnual,hoursDay,workedHours,effectiveHourly,unadjusted:convert(annual),adjusted:convert(adjustedAnnual)}}
function tradeInProjection(){const comparable=Math.max(0,V('comparable')),adjustment=V('market_adjustment'),margin=Math.max(0,V('dealer_margin')),reconditioning=Math.max(0,V('reconditioning')),payoff=Math.max(0,V('payoff')),replacement=Math.max(0,V('replacement_price')),taxRate=Math.max(0,V('tax_rate'))/100,trade=Math.max(0,comparable+adjustment-margin-reconditioning),equity=trade-payoff,taxSavings=Math.min(trade,replacement)*taxRate;return{comparable,adjustment,margin,reconditioning,payoff,replacement,taxRate,trade,equity,taxSavings,effective:trade+taxSavings}}
function usedCarProjection(){const benchmark=Math.max(0,V('retail_benchmark')),condition=V('condition_adjustment'),mileage=V('mileage_adjustment'),options=V('options_adjustment'),regional=V('regional_adjustment'),spread=Math.max(0,Math.min(50,V('dealer_spread'))),retail=Math.max(0,benchmark*(1+condition/100)*(1+regional/100)+mileage+options),privateValue=retail*(1-spread/200),trade=retail*(1-spread/100);return{benchmark,condition,mileage,options,regional,spread,retail,privateValue,trade}}
function syncCarDepreciationMethod(){const method=document.getElementById('dep_method')?.value||'uniform';document.querySelectorAll('[data-dep-uniform]').forEach(el=>el.classList.toggle('is-hidden',method!=='uniform'));document.querySelectorAll('[data-dep-two-stage]').forEach(el=>el.classList.toggle('is-hidden',method!=='two_stage'));return method}
function carDepreciationProjection(){const method=syncCarDepreciationMethod(),start=Math.max(0,V('dep_start_value')),years=Math.max(1,Math.min(30,Math.floor(V('dep_years')))),uniformRate=Math.max(0,Math.min(1,V('dep_rate')/100)),firstRate=Math.max(0,Math.min(1,V('dep_first_rate')/100)),laterRate=Math.max(0,Math.min(1,V('dep_later_rate')/100)),floor=Math.min(start,Math.max(0,V('dep_floor'))),milesYear=Math.max(0,V('dep_miles_year'));let value=start;const schedule=[];for(let year=1;year<=years;year++){const opening=value,rate=method==='two_stage'?(year===1?firstRate:laterRate):uniformRate,ending=Math.max(floor,opening*(1-rate)),loss=Math.max(0,opening-ending);value=ending;schedule.push({year,opening,rate,loss,ending})}const totalLoss=Math.max(0,start-value),retained=start?value/start*100:0,totalMiles=milesYear*years,costPerMile=totalMiles?totalLoss/totalMiles:0,averageAnnual=totalLoss/years;return{method,start,years,uniformRate,firstRate,laterRate,floor,milesYear,value,totalLoss,retained,totalMiles,costPerMile,averageAnnual,schedule}}
function carResaleAtRate(start,years,rate,costRate,payoff){const value=start*Math.pow(1-rate,years),sellingCosts=value*costRate,net=value-sellingCosts-payoff;return{rate,value,sellingCosts,net,totalLoss:start-value}}
function carResaleProjection(){const start=Math.max(0,V('resale_start_value')),years=Math.max(1,Math.min(30,Math.floor(V('resale_years')))),rate=Math.max(0,Math.min(1,V('resale_rate')/100)),variance=Math.max(0,Math.min(1,V('resale_variance')/100)),milesYear=Math.max(0,V('resale_miles_year')),payoff=Math.max(0,V('resale_payoff')),costRate=Math.max(0,Math.min(1,V('resale_cost_rate')/100)),base=carResaleAtRate(start,years,rate,costRate,payoff),slower=carResaleAtRate(start,years,Math.max(0,rate-variance),costRate,payoff),faster=carResaleAtRate(start,years,Math.min(1,rate+variance),costRate,payoff);let value=start;const schedule=[];for(let year=1;year<=years;year++){const opening=value;value=opening*(1-rate);schedule.push({year,opening,loss:opening-value,ending:value})}const totalMiles=milesYear*years,costPerMile=totalMiles?base.totalLoss/totalMiles:0;return{start,years,rate,variance,milesYear,payoff,costRate,base,slower,faster,totalMiles,costPerMile,schedule}}
function syncHorsepowerFields(){const mode=document.getElementById('hp_solve')?.value||'power';document.querySelectorAll('[data-hp-torque]').forEach(el=>el.classList.toggle('is-hidden',mode==='torque'));document.querySelectorAll('[data-hp-rpm]').forEach(el=>el.classList.toggle('is-hidden',mode==='rpm'));document.querySelectorAll('[data-hp-power]').forEach(el=>el.classList.toggle('is-hidden',mode==='power'));return mode}
function horsepowerProjection(){const mode=syncHorsepowerFields(),torqueUnit=document.getElementById('hp_torque_unit')?.value||'lbft',powerUnit=document.getElementById('hp_power_unit')?.value||'hp',rawTorque=Math.max(0,V('hp_torque')),rawPower=Math.max(0,V('hp_power'));let torqueLb=torqueUnit==='nm'?rawTorque/1.3558179483314004:rawTorque,rpm=Math.max(0,V('hp_rpm')),hp=powerUnit==='kw'?rawPower/0.7456998715822702:powerUnit==='ps'?rawPower*0.73549875/0.7456998715822702:rawPower;const constant=5252.113122032546;if(mode==='power'){if(!(torqueLb>0&&rpm>0))return{valid:false,message:'Enter positive torque and RPM values.',mode};hp=torqueLb*rpm/constant}else if(mode==='torque'){if(!(hp>0&&rpm>0))return{valid:false,message:'Enter positive power and RPM values.',mode};torqueLb=hp*constant/rpm}else{if(!(hp>0&&torqueLb>0))return{valid:false,message:'Enter positive power and torque values.',mode};rpm=hp*constant/torqueLb}const kw=hp*0.7456998715822702,ps=kw/0.73549875,torqueNm=torqueLb*1.3558179483314004;return{valid:true,mode,torqueUnit,powerUnit,hp,kw,ps,torqueLb,torqueNm,rpm,constant}}
function powerWeightProjection(){const powerUnit=document.getElementById('pw_power_unit')?.value||'hp',weightUnit=document.getElementById('pw_weight_unit')?.value||'lb',loadUnit=document.getElementById('pw_load_unit')?.value||'lb',rawPower=Math.max(0,V('pw_power')),rawWeight=Math.max(0,V('pw_weight')),rawLoad=Math.max(0,V('pw_load')),target=Math.max(0,V('pw_target')),hp=powerUnit==='kw'?rawPower/0.7456998715822702:powerUnit==='w'?rawPower/745.6998715822702:powerUnit==='ps'?rawPower*0.73549875/0.7456998715822702:rawPower,weightLb=weightUnit==='kg'?rawWeight/0.45359237:weightUnit==='us_ton'?rawWeight*2000:weightUnit==='tonne'?rawWeight*2204.6226218488:rawWeight,loadLb=loadUnit==='kg'?rawLoad/0.45359237:rawLoad,totalLb=weightLb+loadLb,totalKg=totalLb*0.45359237;if(!(hp>0&&totalLb>0))return{valid:false,message:'Enter positive power and weight values.'};const hpPerLb=hp/totalLb,lbPerHp=totalLb/hp,hpPerUsTon=hpPerLb*2000,hpPerTonne=hp/(totalKg/1000),wPerKg=hp*745.6998715822702/totalKg,targetHp=target*totalLb,powerGap=targetHp-hp;return{valid:true,powerUnit,weightUnit,loadUnit,rawPower,rawWeight,rawLoad,hp,kw:hp*0.7456998715822702,weightLb,loadLb,totalLb,totalKg,target,hpPerLb,lbPerHp,hpPerUsTon,hpPerTonne,wPerKg,targetHp,powerGap}}
function syncBottleneckFields(){const mode=document.getElementById('bn_mode')?.value||'measured';document.querySelectorAll('[data-bn-measured]').forEach(el=>el.classList.toggle('is-hidden',mode!=='measured'));document.querySelectorAll('[data-bn-planning]').forEach(el=>el.classList.toggle('is-hidden',mode!=='planning'));const title=document.getElementById('bottleneckChartTitle');if(title)title.textContent=mode==='measured'?'Frame-Time Comparison':'Benchmark FPS Ceilings';return mode}
function bottleneckProjection(){const mode=syncBottleneckFields();if(mode==='planning'){const cpuCap=Math.max(0,V('bn_cpu_cap')),gpuCap=Math.max(0,V('bn_gpu_cap')),target=Math.max(0,V('bn_plan_target')),uncertainty=Math.max(0,Math.min(.5,V('bn_uncertainty')/100));if(!(cpuCap>0&&gpuCap>0&&target>0))return{valid:false,mode,message:'Enter positive CPU, GPU, and target FPS values.'};const estimate=Math.min(cpuCap,gpuCap),low=estimate*(1-uncertainty),high=estimate*(1+uncertainty),verdict=cpuCap<gpuCap*.9?'Likely CPU-bound':gpuCap<cpuCap*.9?'Likely GPU-bound':'Closely balanced',targetGap=target-estimate,limiting=cpuCap<=gpuCap?'CPU benchmark ceiling':'GPU benchmark ceiling';return{valid:true,mode,cpuCap,gpuCap,target,uncertainty,estimate,low,high,verdict,targetGap,limiting}}const fps=Math.max(0,V('bn_fps')),target=Math.max(0,V('bn_target')),gpuUsage=V('bn_gpu_usage'),cpuUsage=V('bn_cpu_usage'),cpuMs=Math.max(0,V('bn_cpu_ms')),gpuMs=Math.max(0,V('bn_gpu_ms'));if(!(fps>0&&target>0&&cpuMs>0&&gpuMs>0&&gpuUsage>=0&&gpuUsage<=100&&cpuUsage>=0&&cpuUsage<=100))return{valid:false,mode,message:'Enter positive FPS and frame times, with utilization values from 0% to 100%.'};const targetBudget=1000/target,frameCeiling=1000/Math.max(cpuMs,gpuMs),targetReached=fps>=target*.95;let verdict='Mixed or inconclusive',reason='CPU and GPU evidence is close or does not point to one limiting side.';if(targetReached){verdict='Target reached or frame-capped';reason='Measured FPS is within 5% of the entered target.'}else if(cpuMs>gpuMs*1.08){verdict='Likely CPU-bound';reason='CPU frame time is materially longer than GPU frame time.'}else if(gpuMs>cpuMs*1.08){verdict='Likely GPU-bound';reason='GPU frame time is materially longer than CPU frame time.'}else if(cpuUsage>=90&&gpuUsage<90){verdict='Likely CPU-bound';reason='The busiest CPU thread is highly utilized while the GPU has headroom.'}else if(gpuUsage>=95&&cpuUsage<90){verdict='Likely GPU-bound';reason='GPU utilization is near full load without a similarly busy CPU thread.'}const targetGap=target-fps;return{valid:true,mode,fps,target,gpuUsage,cpuUsage,cpuMs,gpuMs,targetBudget,frameCeiling,targetReached,verdict,reason,targetGap}}
function tireSpec(width,aspect,rim){const sidewall=width*aspect/100,diameter=rim+2*sidewall/25.4,circumference=Math.PI*diameter,revsPerMile=63360/circumference;return{width,aspect,rim,sidewall,diameter,circumference,revsPerMile}}
function tireComparison(){const original=tireSpec(Math.max(0,V('original_width')),Math.max(0,V('original_aspect')),Math.max(0,V('original_rim'))),next=tireSpec(Math.max(0,V('new_width')),Math.max(0,V('new_aspect')),Math.max(0,V('new_rim'))),ratio=original.diameter?next.diameter/original.diameter:0,differencePct=(ratio-1)*100,indicated=Math.max(0,V('indicated_speed')),actualSpeed=indicated*ratio,clearance=(next.diameter-original.diameter)/2;return{original,next,ratio,differencePct,indicated,actualSpeed,clearance}}
function wheelOffsetComparison(){const currentWidth=Math.max(0,V('current_width')),currentOffset=V('current_offset'),newWidth=Math.max(0,V('new_wheel_width')),newOffset=V('new_offset'),spacer=Math.max(0,V('spacer')),effectiveOffset=newOffset-spacer,currentHalf=currentWidth*25.4/2,newHalf=newWidth*25.4/2,currentInner=currentHalf+currentOffset,currentOuter=currentHalf-currentOffset,newInner=newHalf+effectiveOffset,newOuter=newHalf-effectiveOffset,innerClearance=currentInner-newInner,outerPoke=newOuter-currentOuter,trackChange=outerPoke*2,currentBackspacing=(currentWidth+1)/2+currentOffset/25.4,newBackspacing=(newWidth+1)/2+effectiveOffset/25.4;return{currentWidth,currentOffset,newWidth,newOffset,spacer,effectiveOffset,currentInner,currentOuter,newInner,newOuter,innerClearance,outerPoke,trackChange,currentBackspacing,newBackspacing}}
function syncConcreteFields(){const round=(document.getElementById('concrete_shape')?.value||'slab')!=='slab';document.querySelectorAll('[data-concrete-rect]').forEach(el=>el.classList.toggle('is-hidden',round));document.querySelectorAll('[data-concrete-round]').forEach(el=>el.classList.toggle('is-hidden',!round));return round}
function concreteProjection(){const shape=document.getElementById('concrete_shape')?.value||'slab',round=syncConcreteFields();let baseFt3=0,quantity=1;if(round){const radius=Math.max(0,V('concrete_diameter'))/24,height=Math.max(0,V('concrete_height'));quantity=Math.max(1,Math.floor(V('concrete_qty')));baseFt3=Math.PI*radius*radius*height*quantity}else baseFt3=Math.max(0,V('concrete_length'))*Math.max(0,V('concrete_width'))*Math.max(0,V('concrete_thickness'))/12;const waste=Math.max(0,V('concrete_waste')),withWaste=baseFt3*(1+waste/100),yards=withWaste/27,yieldPerBag=Math.max(.001,V('concrete_bag_size')),bags=Math.ceil(withWaste/yieldPerBag),bagCost=bags*Math.max(0,V('concrete_bag_price')),readyCost=yards*Math.max(0,V('concrete_yard_price'));return{shape,quantity,baseFt3,waste,withWaste,yards,yieldPerBag,bags,bagCost,readyCost}}
function syncRoofFields(){const mode=document.getElementById('roof_input_mode')?.value||'pitch';document.querySelectorAll('[data-roof-pitch]').forEach(el=>el.classList.toggle('is-hidden',mode!=='pitch'));document.querySelectorAll('[data-roof-rise-run]').forEach(el=>el.classList.toggle('is-hidden',mode!=='rise_run'));document.querySelectorAll('[data-roof-angle]').forEach(el=>el.classList.toggle('is-hidden',mode!=='angle'));return mode}
function roofPitchProjection(){const mode=syncRoofFields();let slope=0;if(mode==='rise_run')slope=Math.max(0,V('roof_rise'))/Math.max(.0001,V('roof_run'));else if(mode==='angle')slope=Math.tan(Math.max(0,Math.min(89.9,V('roof_angle')))*Math.PI/180);else slope=Math.max(0,V('roof_pitch'))/12;const pitch=slope*12,angle=Math.atan(slope)*180/Math.PI,percent=slope*100,factor=Math.sqrt(1+slope*slope),run=Math.max(0,V('roof_rafter_run')),overhang=Math.max(0,V('roof_overhang'))/12,rafter=(run+overhang)*factor,rise=run*slope,planArea=Math.max(0,V('roof_plan_area')),slopedArea=planArea*factor,squares=slopedArea/100;return{mode,slope,pitch,angle,percent,factor,run,overhang,rafter,rise,planArea,slopedArea,squares}}
function rafterProjection(){const pitch=Math.max(0,V('rafter_pitch')),slope=pitch/12,factor=Math.sqrt(1+slope*slope),run=Math.max(0,V('rafter_run')),overhang=Math.max(0,V('rafter_overhang'))/12,baseLength=run*factor,tailLength=overhang*factor,totalLength=baseLength+tailLength,rise=run*slope,angle=Math.atan(slope)*180/Math.PI,quantity=Math.max(1,Math.floor(V('rafter_qty'))),totalLinear=totalLength*quantity;return{pitch,slope,factor,run,overhang,baseLength,tailLength,totalLength,rise,angle,quantity,totalLinear}}
function syncAreaFields(){const shape=document.getElementById('area_shape')?.value||'rectangle';document.querySelectorAll('[data-area-rectangle],[data-area-circle],[data-area-triangle],[data-area-walls]').forEach(el=>{const show=(shape==='rectangle'&&el.hasAttribute('data-area-rectangle'))||(shape==='circle'&&el.hasAttribute('data-area-circle'))||(shape==='triangle'&&el.hasAttribute('data-area-triangle'))||(shape==='room_walls'&&el.hasAttribute('data-area-walls'));el.classList.toggle('is-hidden',!show)});return shape}
function squareFootageProjection(){const shape=syncAreaFields(),length=Math.max(0,V('area_length')),width=Math.max(0,V('area_width'));let area=0,perimeter=null,gross=0,openings=0;if(shape==='circle'){const diameter=Math.max(0,V('area_diameter'));area=Math.PI*(diameter/2)**2;perimeter=Math.PI*diameter}else if(shape==='triangle'){area=Math.max(0,V('area_base'))*Math.max(0,V('area_height'))/2}else if(shape==='room_walls'){perimeter=2*(length+width);gross=perimeter*Math.max(0,V('wall_height'));openings=Math.max(0,V('area_openings'));area=Math.max(0,gross-openings)}else{area=length*width;perimeter=2*(length+width)}const overage=Math.max(0,V('area_overage')),orderArea=area*(1+overage/100),price=Math.max(0,V('area_price')),cost=orderArea*price;return{shape,length,width,area,perimeter,gross,openings,overage,orderArea,price,cost}}
function flooringProjection(){const length=Math.max(0,V('floor_length')),width=Math.max(0,V('floor_width')),extra=Math.max(0,V('floor_extra')),area=length*width+extra,waste=Math.max(0,V('floor_waste')),target=area*(1+waste/100),boxCoverage=Math.max(.001,V('floor_box_coverage')),boxes=Math.ceil(target/boxCoverage-1e-9),purchased=boxes*boxCoverage,leftover=Math.max(0,purchased-area),boxCost=boxes*Math.max(0,V('floor_box_price')),underlayCoverage=Math.max(.001,V('underlay_coverage')),underlayRolls=Math.ceil(area/underlayCoverage-1e-9),underlayCost=underlayRolls*Math.max(0,V('underlay_price')),totalCost=boxCost+underlayCost;return{length,width,extra,area,waste,target,boxCoverage,boxes,purchased,leftover,boxCost,underlayCoverage,underlayRolls,underlayCost,totalCost}}
function tileProjection(){const length=Math.max(0,V('tile_project_length')),width=Math.max(0,V('tile_project_width')),area=length*width,tileWidth=Math.max(.001,V('tile_width')),tileHeight=Math.max(.001,V('tile_height')),tileArea=tileWidth*tileHeight/144,waste=Math.max(0,V('tile_waste')),targetArea=area*(1+waste/100),pieces=Math.ceil(targetArea/tileArea-1e-9),perBox=Math.max(1,Math.floor(V('tile_per_box'))),boxes=Math.ceil(pieces/perBox-1e-9),purchasedPieces=boxes*perBox,purchasedArea=purchasedPieces*tileArea,leftover=Math.max(0,purchasedArea-area),cost=boxes*Math.max(0,V('tile_box_price'));return{length,width,area,tileWidth,tileHeight,tileArea,waste,targetArea,pieces,perBox,boxes,purchasedPieces,purchasedArea,leftover,cost}}
function deckProjection(){const length=Math.max(0,V('deck_length')),width=Math.max(0,V('deck_width')),boardWidth=Math.max(.001,V('deck_board_width')),gap=Math.max(0,V('deck_gap')),stockLength=Math.max(.001,V('deck_stock_length')),waste=Math.max(0,V('deck_waste')),joistSpacing=Math.max(.001,V('deck_joist_spacing')),boardPrice=Math.max(0,V('deck_board_price')),fastenersPerCrossing=Math.max(1,Math.floor(V('deck_fasteners_crossing'))),fastenersPerPack=Math.max(1,Math.floor(V('deck_fastener_pack'))),fastenerPackPrice=Math.max(0,V('deck_fastener_price')),area=length*width,rows=Math.ceil(width*12/(boardWidth+gap)-1e-9),boardsPerRow=Math.ceil(length/stockLength-1e-9),baseBoards=rows*boardsPerRow,boards=Math.ceil(baseBoards*(1+waste/100)-1e-9),coverageLinear=rows*length,stockLinear=baseBoards*stockLength,orderedLinear=boards*stockLength,joists=Math.ceil(length*12/joistSpacing-1e-9)+1,fasteners=rows*joists*fastenersPerCrossing,fastenerPacks=Math.ceil(fasteners/fastenersPerPack-1e-9),boardCost=boards*boardPrice,fastenerCost=fastenerPacks*fastenerPackPrice,totalCost=boardCost+fastenerCost;return{length,width,area,boardWidth,gap,stockLength,waste,rows,boardsPerRow,baseBoards,boards,coverageLinear,stockLinear,orderedLinear,joistSpacing,joists,fastenersPerCrossing,fasteners,fastenersPerPack,fastenerPacks,boardCost,fastenerCost,totalCost}}
function boardFootProjection(){const thickness=Math.max(0,V('bf_thickness')),width=Math.max(0,V('bf_width')),length=Math.max(0,V('bf_length')),quantity=Math.max(1,Math.floor(V('bf_quantity'))),waste=Math.max(0,V('bf_waste')),price=Math.max(0,V('bf_price')),perBoard=thickness*width*length/12,total=perBoard*quantity,order=total*(1+waste/100),cubicFeet=order/12,linearFeet=length*quantity,cost=order*price;return{thickness,width,length,quantity,waste,price,perBoard,total,order,cubicFeet,linearFeet,cost}}
const ELECTRICAL_WIRE_TABLE=[
 {g:'14',cuR:3.07,alR:5.06,cu60:15,cu75:15,al60:0,al75:0},{g:'12',cuR:1.93,alR:3.20,cu60:20,cu75:20,al60:0,al75:0},{g:'10',cuR:1.21,alR:2.00,cu60:30,cu75:30,al60:0,al75:0},{g:'8',cuR:.764,alR:1.26,cu60:40,cu75:50,al60:30,al75:40},{g:'6',cuR:.491,alR:.808,cu60:55,cu75:65,al60:40,al75:50},{g:'4',cuR:.308,alR:.508,cu60:70,cu75:85,al60:55,al75:65},{g:'3',cuR:.245,alR:.404,cu60:85,cu75:100,al60:65,al75:75},{g:'2',cuR:.194,alR:.319,cu60:95,cu75:115,al60:75,al75:90},{g:'1',cuR:.154,alR:.253,cu60:110,cu75:130,al60:85,al75:100},{g:'1/0',cuR:.122,alR:.201,cu60:125,cu75:150,al60:100,al75:120},{g:'2/0',cuR:.0967,alR:.159,cu60:145,cu75:175,al60:115,al75:135},{g:'3/0',cuR:.0766,alR:.126,cu60:165,cu75:200,al60:130,al75:155},{g:'4/0',cuR:.0608,alR:.100,cu60:195,cu75:230,al60:150,al75:180}
];
const STANDARD_BREAKERS=[15,20,25,30,35,40,45,50,60,70,80,90,100,110,125,150,175,200,225,250,300,350,400];
function nextBreaker(amps){return STANDARD_BREAKERS.find(x=>x+1e-9>=amps)||Math.ceil(amps/50)*50}
function phaseFactor(phase){return phase==='three'?Math.sqrt(3):2}
function wireResistance(row,material){return material==='aluminum'?row.alR:row.cuR}
function voltageDropFor(row,material,phase,length,amps){return phaseFactor(phase)*length*amps*wireResistance(row,material)/1000}
function voltageDropProjection(){const phase=document.getElementById('vd_phase')?.value||'single',material=document.getElementById('vd_material')?.value||'copper',gauge=document.getElementById('vd_gauge')?.value||'12',length=Math.max(0,V('vd_length')),amps=Math.max(0,V('vd_amps')),voltage=Math.max(.001,V('vd_voltage')),limit=Math.max(.1,V('vd_limit')),row=ELECTRICAL_WIRE_TABLE.find(x=>x.g===gauge)||ELECTRICAL_WIRE_TABLE[1],drop=voltageDropFor(row,material,phase,length,amps),percent=drop/voltage*100,loadVoltage=Math.max(0,voltage-drop),targetVolts=voltage*limit/100,recommended=ELECTRICAL_WIRE_TABLE.find(x=>voltageDropFor(x,material,phase,length,amps)<=targetVolts+1e-9)||ELECTRICAL_WIRE_TABLE.at(-1),maxLength=amps>0?targetVolts*1000/(phaseFactor(phase)*amps*wireResistance(row,material)):0;return{phase,material,gauge,length,amps,voltage,limit,row,drop,percent,loadVoltage,recommended,maxLength}}
function wireSizeProjection(){const amps=Math.max(0,V('ws_amps')),continuous=Math.min(amps,Math.max(0,V('ws_continuous'))),designAmps=amps+continuous*.25,material=document.getElementById('ws_material')?.value||'copper',temp=document.getElementById('ws_temp')?.value||'60',phase=document.getElementById('ws_phase')?.value||'single',voltage=Math.max(.001,V('ws_voltage')),length=Math.max(0,V('ws_length')),limit=Math.max(.1,V('ws_drop_limit')),ampKey=(material==='aluminum'?'al':'cu')+temp,ampacityRow=ELECTRICAL_WIRE_TABLE.find(x=>x[ampKey]>=designAmps&&x[ampKey]>0)||ELECTRICAL_WIRE_TABLE.at(-1),targetVolts=voltage*limit/100,dropRow=ELECTRICAL_WIRE_TABLE.find(x=>voltageDropFor(x,material,phase,length,amps)<=targetVolts+1e-9)||ELECTRICAL_WIRE_TABLE.at(-1),ampIndex=ELECTRICAL_WIRE_TABLE.indexOf(ampacityRow),dropIndex=ELECTRICAL_WIRE_TABLE.indexOf(dropRow),recommended=ELECTRICAL_WIRE_TABLE[Math.max(ampIndex,dropIndex)],ampacity=recommended[ampKey],drop=voltageDropFor(recommended,material,phase,length,amps),dropPercent=drop/voltage*100,loadVoltage=Math.max(0,voltage-drop);return{amps,continuous,designAmps,material,temp,phase,voltage,length,limit,ampacityRow,dropRow,recommended,ampacity,drop,dropPercent,loadVoltage}}
function breakerProjection(){const continuous=Math.max(0,V('br_continuous')),noncontinuous=Math.max(0,V('br_noncontinuous')),actual=continuous+noncontinuous,planning=continuous*1.25+noncontinuous,breaker=nextBreaker(planning),voltage=Math.max(0,V('br_voltage')),poles=Math.max(1,V('br_poles')),utilization=breaker>0?actual/breaker*100:0,headroom=Math.max(0,breaker-planning),power=actual*voltage;return{continuous,noncontinuous,actual,planning,breaker,voltage,poles,utilization,headroom,power}}
function electricalLoadProjection(){const continuous=Math.max(0,V('el_continuous')),noncontinuous=Math.max(0,V('el_noncontinuous')),watts=continuous+noncontinuous,planningWatts=continuous*1.25+noncontinuous,voltage=Math.max(.001,V('el_voltage')),phase=document.getElementById('el_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('el_pf'))),divisor=voltage*pf*(phase==='three'?Math.sqrt(3):1),amps=watts/divisor,planningAmps=planningWatts/divisor,va=watts/pf,breaker=nextBreaker(planningAmps),utilization=breaker>0?amps/breaker*100:0;return{continuous,noncontinuous,watts,planningWatts,voltage,phase,pf,amps,planningAmps,va,breaker,utilization}}
function wattsAmpsProjection(){const watts=Math.max(0,V('wa_watts')),voltage=Math.max(.001,V('wa_voltage')),phase=document.getElementById('wa_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('wa_pf'))),multiplier=phase==='three'?Math.sqrt(3):1,amps=watts/(voltage*pf*multiplier),va=watts/pf,vars=Math.sqrt(Math.max(0,va*va-watts*watts)),continuous=document.getElementById('wa_continuous')?.value==='yes',planningAmps=amps*(continuous?1.25:1);return{watts,voltage,phase,pf,multiplier,amps,va,vars,continuous,planningAmps}}
function ampsWattsProjection(){const amps=Math.max(0,V('aw_amps')),voltage=Math.max(.001,V('aw_voltage')),phase=document.getElementById('aw_phase')?.value||'single',pf=phase==='dc'?1:Math.max(.01,Math.min(1,V('aw_pf'))),multiplier=phase==='three'?Math.sqrt(3):1,va=amps*voltage*multiplier,watts=va*pf,vars=Math.sqrt(Math.max(0,va*va-watts*watts));return{amps,voltage,phase,pf,multiplier,va,watts,vars}}
function syncFeetMeterInputs(){const reverse=document.getElementById('conversion_direction')?.value==='meters_to_feet';document.querySelectorAll('[data-feet-input]').forEach(el=>el.classList.toggle('is-hidden',reverse));document.querySelectorAll('[data-meter-input]').forEach(el=>el.classList.toggle('is-hidden',!reverse));return reverse}
function clearCalcForm(){const form=document.querySelector('.calc');if(!form)return;form.querySelectorAll('input').forEach(input=>{if(input.type==='checkbox')input.checked=false;else input.value=''});form.querySelectorAll('textarea').forEach(textarea=>{textarea.value=''});form.querySelectorAll('select').forEach(select=>{select.selectedIndex=0});form.querySelectorAll('details').forEach(item=>{item.open=false});syncMortgageCosts();syncConcreteFields();syncRoofFields();syncAreaFields();syncPayDeductionFields();syncSalesTaxFields();syncPercentFields();syncFractionFields();syncRatioFields();syncBmiFields();syncFinanceTarget();syncPaymentMode();syncRetirementMode();syncK401Mode();syncSocialSecurityMode();show('<strong>0</strong><br>Enter values to calculate a new result.');const engine=currentEngine();if(engine==='cn_mortgage')renderMortgage(0,0,1,0,0,0,0,0,0,0,0,0,0,new Date());if(engine==='loan_page')renderLoanPage();if(engine==='ratio_advanced')renderGenericFromEngine(engine)}
function calc(e){
 switch(e){
  case'trade_value':{let price=V('price'),age=V('age'),miles=V('miles'),cond=V('condition');let ageF=Math.pow(.84,age),expected=Math.max(1,age)*12000,mileageF=Math.max(.72,Math.min(1.12,1-(miles-expected)*0.000003));let r=price*ageF*mileageF*cond;show(`<strong>${USD(Math.max(0,r))}</strong><br>Illustrative estimate, not a dealer quote or appraisal.`);break}
  case'f150_bed':{let bed=String(document.getElementById('bed').value);let d={'5.5':['67.1 in','50.6 in','~52.8 cu ft'],'6.5':['78.9 in','50.6 in','~62.3 cu ft'],'8':['97.6 in','50.6 in','~77.4 cu ft']}[bed];show(`<strong>${bed} ft bed</strong><br>Approx. inside length: ${d[0]}; width between wheelhouses: ${d[1]}; cargo volume: ${d[2]}. Verify exact model year/configuration.`);break}
  case'depreciation':{let r=V('price')*Math.pow(1-V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Estimated future value.`);break}
  case'payload':{let capacity=V('gvwr')-V('curb'),used=V('people')+V('cargo')+V('tongue'),remaining=capacity-used,status=remaining>=0?'Within entered GVWR':'Over entered GVWR';show(`<strong>${F(remaining,0)} lb remaining</strong><br>${status}; ${F(capacity,0)} lb total payload capacity and ${F(used,0)} lb entered load.`);break}
  case'trailer_weight':{let r=V('empty')+V('cargo');show(`<strong>${F(r,0)} lb</strong><br>Estimated loaded trailer weight.`);break}
  case'tongue_weight':{let r=V('trailer')*V('percent')/100;show(`<strong>${F(r,0)} lb</strong><br>Estimated tongue weight.`);break}
  case'trailer_payload':{let r=V('gvwr')-V('empty');show(`<strong>${F(r,0)} lb</strong><br>Theoretical payload before other limits.`);break}
  case'tongue_pct':{let r=V('trailer')?V('tongue')/V('trailer')*100:0;show(`<strong>${F(r,2)}%</strong>`);break}
  case'towing':{let loaded=V('curb')+V('people')+V('cargo'),remainingPayload=Math.max(0,V('gvwr')-loaded),pct=Math.max(.01,V('tongue_pct')/100),limits=[['Vehicle tow rating',V('rating')],['GCWR headroom',Math.max(0,V('gcwr')-loaded)],['Hitch rating',V('hitch_rating')],['Payload for tongue weight',remainingPayload/pct]],hit=limits.reduce((a,b)=>b[1]<a[1]?b:a);show(`<strong>${F(hit[1],0)} lb trailer</strong><br>Planning limit: ${hit[0]}; ${F(remainingPayload,0)} lb vehicle payload remains before tongue weight.`);break}
  case'debt_payoff_advanced':{const p=debtPayoffProjection();if(!p.valid)show(`<strong>Unable to build a payoff plan</strong><br>${p.message}`);else{const label=p.strategy==='snowball'?'Debt snowball':'Debt avalanche',saved=p.baseline.valid?Math.max(0,p.baseline.interest-p.selected.interest):0;show(`<strong>${p.selected.payoffLabel} debt-free estimate</strong><br>${label}: ${F(p.selected.months,0)} months, ${USD(p.selected.interest)} interest, and ${USD(saved)} less interest than the no-extra-payment plan.`)}break}
  case'fuel_cost':{let r=V('distance')/Math.max(.01,V('mpg'))*V('fuelprice');show(`<strong>${USD(r)}</strong><br>Estimated fuel cost.`);break}
  case'mpg':{let r=V('gallons')?V('miles')/V('gallons'):0;show(`<strong>${F(r,2)} MPG</strong>`);break}
  case'mpg_advanced':{let distance=V('distance'),fuel=V('fuel_used'),miles=(document.getElementById('distance_unit')?.value==='kilometers'?distance*0.621371192237:distance),liters=fuel*(document.getElementById('fuel_unit')?.value==='us_gallon'?3.785411784:document.getElementById('fuel_unit')?.value==='imperial_gallon'?4.54609:1),usGallons=liters/3.785411784,mpg=usGallons>0?miles/usGallons:0,km=miles/0.621371192237,l100=km>0?liters/km*100:0;show(`<strong>${F(mpg,2)} US MPG</strong><br>${F(l100,2)} L/100 km; ${F(miles/(liters/4.54609),2)} Imperial MPG; ${F(liters?km/liters:0,2)} km/L.`);break}
  case'fuel_cost_advanced':{let metric=document.getElementById('trip_units')?.value==='metric',distance=V('distance')*Math.max(1,V('trip_type'))*Math.max(1,V('trips')),eff=Math.max(.01,V('efficiency')),fuel=metric?distance*eff/100:distance/eff,cost=fuel*V('fuelprice'),currency=document.getElementById('currency')?.value||'USD',people=Math.max(1,V('people'));show(`<strong>${MONEY(cost,currency)}</strong><br>${F(fuel,2)} ${metric?'liters':'US gallons'}; ${MONEY(cost/people,currency)} per person; ${F(distance,0)} ${metric?'km':'miles'} total.`);break}
  case'trade_in_estimate':{const p=tradeInProjection(),equityLabel=p.equity>=0?'positive equity':'negative equity';show(`<strong>${USD(p.trade)} trade-in estimate</strong><br>${USD(Math.abs(p.equity))} ${equityLabel}; ${USD(p.taxSavings)} entered tax benefit; ${USD(p.effective)} effective trade value.`);break}
  case'used_car_estimate':{const p=usedCarProjection();show(`<strong>${USD(p.privateValue)} private-party estimate</strong><br>Adjusted retail: ${USD(p.retail)}; trade-in estimate: ${USD(p.trade)}; review the planning ranges below.`);break}
  case'car_depreciation_advanced':{const p=carDepreciationProjection();show(`<strong>${USD(p.value)} projected vehicle value</strong><br>${USD(p.totalLoss)} total depreciation (${F(100-p.retained,1)}%); ${USD(p.averageAnnual)} average per year; ${USD(p.costPerMile)} per projected mile.`);break}
  case'car_resale_advanced':{const p=carResaleProjection(),equity=p.base.net>=0?'net proceeds':'negative equity';show(`<strong>${USD(p.base.value)} projected resale value</strong><br>${USD(Math.abs(p.base.net))} ${equity} after ${USD(p.base.sellingCosts)} selling costs and ${USD(p.payoff)} payoff.`);break}
  case'horsepower_advanced':{const p=horsepowerProjection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else{const answer=p.mode==='torque'?`${F(p.torqueLb,2)} lb-ft torque`:p.mode==='rpm'?`${F(p.rpm,0)} RPM`:`${F(p.hp,2)} horsepower`;show(`<strong>${answer}</strong><br>${F(p.kw,2)} kW; ${F(p.ps,2)} PS; ${F(p.torqueNm,2)} N-m at ${F(p.rpm,0)} RPM.`)}break}
  case'power_weight_advanced':{const p=powerWeightProjection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else show(`<strong>${F(p.hpPerLb,5)} hp/lb</strong><br>${F(p.lbPerHp,2)} lb/hp; ${F(p.hpPerUsTon,2)} hp per US ton; ${F(p.wPerKg,2)} W/kg.`);break}
  case'ratio_advanced':{const p=ratioProjection();if(!p.valid)show(`<strong>Check the ratio</strong><br>${p.message}`);else if(p.mode==='proportion')show(`<strong>${p.label} = ${F(p.solved,8)}</strong><br>${p.equation}; both cross products equal ${F(p.leftProduct,8)}.`);else if(p.mode==='split')show(`<strong>${ratioText(p.shares)}</strong><br>${F(p.total,8)} split in the simplified ratio ${ratioText(p.terms)}.`);else if(p.mode==='scale')show(`<strong>${ratioText(p.scaled)}</strong><br>${ratioText(p.values)} multiplied by ${F(p.factor,8)}; simplest form ${ratioText(p.terms)}.`);else show(`<strong>${ratioText(p.terms)}</strong><br>${ratioText(p.values)} reduced to lowest whole-number terms.`);break}
  case'bottleneck_advanced':{const p=bottleneckProjection();if(!p.valid)show(`<strong>Unable to analyze</strong><br>${p.message}`);else if(p.mode==='planning')show(`<strong>${p.verdict}</strong><br>${F(p.estimate,1)} FPS lower benchmark ceiling; ${F(p.low,1)}-${F(p.high,1)} FPS entered uncertainty range; ${p.targetGap>0?`${F(p.targetGap,1)} FPS below`:`${F(Math.abs(p.targetGap),1)} FPS above`} target.`);else show(`<strong>${p.verdict}</strong><br>${p.reason} Measured ${F(p.fps,1)} FPS; ${p.targetGap>0?`${F(p.targetGap,1)} FPS below`:`${F(Math.abs(p.targetGap),1)} FPS at or above`} target.`);break}
  case'tire_compare':{const p=tireComparison(),direction=p.differencePct>=0?'larger':'smaller';show(`<strong>${F(Math.abs(p.differencePct),2)}% ${direction} diameter</strong><br>Actual speed at ${F(p.indicated,0)} mph indicated: ${F(p.actualSpeed,2)} mph; ground-clearance change: ${p.clearance>=0?'+':''}${F(p.clearance,2)} in.`);break}
  case'wheel_offset_compare':{const p=wheelOffsetComparison(),clearance=p.innerClearance>=0?`${F(p.innerClearance,1)} mm more`:`${F(Math.abs(p.innerClearance),1)} mm less`;show(`<strong>${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm outer position</strong><br>${clearance} inner clearance; ${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm estimated track change.`);break}
  case'concrete_advanced':{const p=concreteProjection();show(`<strong>${F(p.yards,2)} cubic yards</strong><br>${F(p.withWaste,2)} cubic feet with waste; ${F(p.bags,0)} selected bags; estimated bag cost ${USD(p.bagCost)}.`);break}
  case'roof_pitch_advanced':{const p=roofPitchProjection();show(`<strong>${F(p.pitch,2)}:12 roof pitch</strong><br>${F(p.angle,2)}° angle; ${F(p.percent,1)}% slope; ${F(p.rafter,2)} ft estimated rafter length.`);break}
  case'rafter_advanced':{const p=rafterProjection();show(`<strong>${F(p.totalLength,2)} ft per rafter</strong><br>${F(p.baseLength,2)} ft to wall line plus ${F(p.tailLength,2)} ft sloped tail; ${F(p.totalLinear,1)} total linear feet.`);break}
  case'square_footage_advanced':{const p=squareFootageProjection();show(`<strong>${F(p.area,2)} square feet</strong><br>${F(p.orderArea,2)} sq ft with overage; estimated material cost ${USD(p.cost)}${p.perimeter!==null?`; ${F(p.perimeter,1)} ft perimeter`:''}.`);break}
	  case'flooring_advanced':{const p=flooringProjection();show(`<strong>${F(p.boxes,0)} boxes of flooring</strong><br>${F(p.target,1)} sq ft target; ${F(p.purchased,1)} sq ft purchased; estimated total with underlayment ${USD(p.totalCost)}.`);break}
	  case'tile_advanced':{const p=tileProjection();show(`<strong>${F(p.boxes,0)} boxes / ${F(p.pieces,0)} tiles</strong><br>${F(p.targetArea,1)} sq ft target; ${F(p.purchasedArea,1)} sq ft purchased; estimated tile cost ${USD(p.cost)}.`);break}
	  case'deck_advanced':{const p=deckProjection();show(`<strong>${F(p.boards,0)} full deck boards</strong><br>${F(p.rows,0)} rows; ${F(p.joists,0)} joist lines; ${F(p.fasteners,0)} fasteners; estimated materials ${USD(p.totalCost)}.`);break}
	  case'board_foot_advanced':{const p=boardFootProjection();show(`<strong>${F(p.order,2)} board feet to order</strong><br>${F(p.total,2)} board feet before waste; ${F(p.cubicFeet,2)} cubic feet; estimated lumber cost ${USD(p.cost)}.`);break}
	  case'voltage_drop_advanced':{const p=voltageDropProjection();show(`<strong>${F(p.drop,2)} V drop (${F(p.percent,2)}%)</strong><br>${F(p.loadVoltage,2)} V at load; ${p.recommended.g} AWG meets the entered ${F(p.limit,1)}% resistive-drop target.`);break}
	  case'wire_size_advanced':{const p=wireSizeProjection();show(`<strong>${p.recommended.g} AWG ${p.material}</strong><br>${F(p.ampacity,0)} A reference ampacity; ${F(p.dropPercent,2)}% estimated drop; ${F(p.designAmps,2)} A planning current.`);break}
	  case'breaker_advanced':{const p=breakerProjection();show(`<strong>${F(p.breaker,0)} A reference breaker</strong><br>${F(p.planning,2)} A minimum planning current; ${F(p.actual,2)} A connected load; verify conductor and equipment rules.`);break}
	  case'electrical_load_advanced':{const p=electricalLoadProjection();show(`<strong>${F(p.amps,2)} A actual load</strong><br>${F(p.planningAmps,2)} A continuous-load planning current; ${F(p.breaker,0)} A reference breaker; ${F(p.va,0)} VA.`);break}
	  case'watts_amps_advanced':{const p=wattsAmpsProjection();show(`<strong>${F(p.amps,3)} amps</strong><br>${F(p.watts/1000,3)} kW real power; ${F(p.va,1)} VA apparent power; ${F(p.planningAmps,3)} A ${p.continuous?'continuous-load planning':'conversion'} current.`);break}
	  case'amps_watts_advanced':{const p=ampsWattsProjection();show(`<strong>${F(p.watts,1)} watts</strong><br>${F(p.watts/1000,3)} kW real power; ${F(p.va,1)} VA apparent power; ${F(p.vars,1)} VAR reactive power.`);break}
  case'tire':{let width=V('width'),aspect=V('aspect'),wheel=V('wheel');let side=width*aspect/100,diam=wheel+2*side/25.4,circ=Math.PI*diam;show(`<strong>${F(diam,2)} in diameter</strong><br>Sidewall: ${F(side,1)} mm; circumference: ${F(circ,2)} in.`);break}
  case'offset':{let r=(V('backspacing')-V('width')/2)*25.4;show(`<strong>${F(r,1)} mm offset</strong><br>Approximation using nominal wheel width.`);break}
  case'backspacing':{let r=V('width')/2+V('offset')/25.4;show(`<strong>${F(r,2)} in backspacing</strong><br>Approximation using nominal wheel width.`);break}
  case'bolt_pattern':{let r=V('adjacent')/Math.sin(Math.PI/V('lugs'));show(`<strong>${F(r,3)} in bolt-circle diameter</strong>`);break}
  case'horsepower':{let r=V('torque')*V('rpm')/5252;show(`<strong>${F(r,1)} hp</strong>`);break}
  case'power_weight':{let a=V('hp')/V('weight'),b=V('weight')/V('hp');show(`<strong>${F(a,4)} hp/lb</strong><br>${F(b,2)} lb per hp.`);break}
  case'car_loan':{let price=V('price'),tax=price*V('tax')/100,fees=V('fees'),include=(document.getElementById('include_fees')?.value||'0')==='1';let base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')),P=Math.max(0,base+(include?tax+fees:0));let rr=V('apr')/1200,n=Math.max(1,V('months'));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,upfront=V('down')+(include?0:tax+fees);show(`<strong>${USD(pay)} / month</strong><br>Total loan amount: ${USD(P)}; upfront payment: ${USD(upfront)}; sale tax: ${USD(tax)}.`);break}
  case'loan':{let P=V('amount'),rr=V('apr')/1200,n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months')));let pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n,total=pay*n;show(`<strong>${USD(pay)} / month</strong><br>Total paid: ${USD(total)}; total interest: ${USD(total-P)}.`);break}
  case'loan_page':{renderLoanPage();break}
  case'finance_tvm':{const p=financeProjection();if(!p.valid)show(`<strong>Check the inputs</strong><br>${p.message}`);else{const labels={fv:'Future value',pmt:'Periodic payment',iy:'Annual interest rate',n:'Number of periods',pv:'Present value'},value=p.target==='iy'?`${F(p.iy,8)}%`:p.target==='n'?F(p.n,8):USD(p[p.target]);show(`<strong>${value} ${labels[p.target].toLowerCase()}</strong><br>${F(p.rate*100,6)}% effective rate per payment period; ${F(p.effectiveAnnual,6)}% effective annual rate.`)}break}
  case'payment_advanced':{const p=paymentProjection();if(!p.valid)show(`<strong>Payment cannot repay this loan</strong><br>${p.message}`);else show(`<strong>${USD(p.regularPayment)} monthly payment</strong><br>${p.termLabel} to payoff; ${USD(p.totalInterest)} total interest; ${USD(p.totalPaid)} total paid.`);break}
  case'amortization_advanced':{const p=amortizationProjection();if(!p.valid)show(`<strong>Unable to build the schedule</strong><br>${p.message}`);else show(`<strong>${USD(p.regularPayment)} scheduled monthly payment</strong><br>${p.termLabel} to payoff (${p.payoffDate}); ${USD(p.totalInterest)} total interest${p.active?`; ${USD(p.interestSaved)} interest saved`:''}.`);break}
  case'retirement_advanced':{const p=retirementProjection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else show(p.result);break}
  case'401k_advanced':{const p=k401Projection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else show(p.result);break}
  case'social_security_advanced':{const p=socialSecurityProjection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else show(p.result);break}
  case'rmd_advanced':{const p=rmdProjection();if(!p.valid)show(`<strong>Unable to calculate</strong><br>${p.message}`);else show(p.result);break}
  case'interest_advanced':{const p=interestComparisonProjection();show(`<strong>${USD(p.compound.balance)} compound balance</strong><br>${USD(p.simpleBalance)} with simple interest; ${USD(p.advantage)} compound advantage; ${USD(p.compound.buyingPower)} compound buying power in today's dollars.`);break}
  case'compound':{const p=compoundProjection();show(`<strong>${USD(p.balance)} ending balance</strong><br>${USD(p.contributed)} contributed; ${USD(p.totalInterest)} net interest; ${USD(p.buyingPower)} inflation-adjusted buying power.`);renderCompound(p);break}
  case'salary_advanced':{const p=salaryProjection();show(`<strong>${USD(p.annual)} new annual salary</strong><br>${USD(p.raiseDollars)} raise (${F(p.raisePercent,2)}%); ${USD(p.perPeriod)} per selected pay period; ${USD(p.hourly)} hourly equivalent.`);break}
  case'discount_advanced':{const p=discountProjection();show(`<strong>${USD(p.total)} estimated checkout total</strong><br>${USD(p.unitPrice)} discounted unit price; ${USD(p.savings)} total savings; ${F(p.effective,2)}% effective discount.`);break}
  case'take_home_pay':{const p=takeHomeProjection();show(`<strong>${USD(p.perPay)} take-home per paycheck</strong><br>${USD(p.net)} annual net pay; ${USD(p.monthly)} monthly average; ${F(p.effective,2)}% estimated total tax rate.`);break}
  case'sales_tax_advanced':{const p=salesTaxProjection();if(p.mode==='rate')show(`<strong>${F(p.rate,3)}% implied sales tax rate</strong><br>${USD(p.tax)} tax between ${USD(p.before)} before tax and ${USD(p.after)} after tax.`);else if(p.mode==='reverse')show(`<strong>${USD(p.before)} before tax</strong><br>${USD(p.tax)} tax removed from the ${USD(p.after)} tax-inclusive total at ${F(p.rate,3)}%.`);else show(`<strong>${USD(p.after)} after-tax total</strong><br>${USD(p.tax)} sales tax on ${USD(p.taxableBase)} taxable amount at ${F(p.rate,3)}%.`);break}
  case'percent_advanced':{const p=percentageProjection();show(`<strong>${p.answer}</strong><br>${p.detail}`);break}
  case'fraction_advanced':{const p=fractionProjection();if(!p.valid)show(`<strong>Undefined</strong><br>${p.step}`);else show(`<strong>${fractionText(p.result)}</strong><br>${mixedText(p.result)}; decimal ${F(p.result.n/p.result.d,10)}; ${F(p.result.n/p.result.d*100,6)}%.`);break}
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
  case'length_convert':{const p=priorityLengthProjection();show(`<strong>${F(p.result,10)} ${p.toSymbol}</strong><br>${F(p.value,10)} ${p.fromSymbol} x ${F(p.activeFactor,12)}; ${F(p.meters,10)} meters.`);break}
  case'feet_meters':{let reverse=syncFeetMeterInputs();if(reverse){let meters=Math.max(0,V('meters')),totalFeet=meters/0.3048,feet=Math.floor(totalFeet),inches=(totalFeet-feet)*12;show(`<strong>${F(totalFeet,6)} feet</strong><br>${feet} ft ${F(inches,3)} in; ${F(meters,6)} meters; ${F(meters*100,3)} centimeters.`)}else{let feet=Math.max(0,V('feet')),inches=Math.max(0,V('inches')),totalFeet=feet+inches/12,meters=totalFeet*0.3048;show(`<strong>${F(meters,6)} meters</strong><br>${F(meters*100,3)} centimeters; ${F(totalFeet,6)} decimal feet; ${F(totalFeet*12,3)} total inches.`)}break}
  case'cn_mortgage':{let price=V('price'),down=unitValue('down',price),P=Math.max(0,price-down),rr=V('apr')/1200,n=Math.max(1,V('years')*12);let pi=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n;let include=syncMortgageCosts(),tax=include?annualCost('tax',price)/12:0,ins=include?monthlyCost('insurance',price):0,pmi=include?monthlyCost('pmi',P):0,hoa=include?monthlyCost('hoa',price):0,other=include?monthlyCost('other',price):0,inc=include?V('increase'):0,extraM=V('extra_monthly'),extraY=V('extra_yearly'),extraO=V('extra_once'),extra=tax+ins+pmi+hoa+other;let start=monthDate('start');show(`<strong>${USD(pi)} / month</strong><br>Total monthly payment with selected taxes and costs: ${USD(pi+extra+extraM)}.`);renderMortgage(P,rr,n,pi,tax,ins,pmi,hoa,other,inc,extraM,extraY,extraO,start);break}
  case'cn_simple_interest':{let P=V('principal'),i=P*V('rate')/100*V('years');show(`<strong>${USD(P+i)}</strong><br>Simple interest: ${USD(i)}.`);break}
  case'cn_retirement':{let P=V('principal'),rr=V('rate')/1200,n=V('years')*12,pmt=V('monthly');let fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n);show(`<strong>${USD(fv)}</strong><br>Total contributions: ${USD(P+pmt*n)}; estimated growth: ${USD(fv-P-pmt*n)}.`);break}
  case'cn_inflation':{let r=V('amount')*Math.pow(1+V('rate')/100,V('years'));show(`<strong>${USD(r)}</strong><br>Inflation-adjusted estimate after ${F(V('years'),1)} years.`);break}
  case'salary_converter':{const p=salaryConverterProjection();if(!p.valid)show(`<strong>Check the inputs</strong><br>Enter a positive work schedule.`);else show(`<strong>${USD(p.annual)} annual gross equivalent</strong><br>${USD(p.unadjusted.month)} monthly; ${USD(p.unadjusted.biweekly)} biweekly; ${USD(p.adjustedAnnual)} after entered unpaid days.`);break}
  case'cn_tax_salary':{let taxable=Math.max(0,V('income')-V('deductions')),tax=taxable*V('taxrate')/100,net=V('income')-tax;show(`<strong>${USD(net)} take-home</strong><br>Estimated tax: ${USD(tax)}; monthly take-home: ${USD(net/12)}.`);break}
  case'bmi_advanced':{const p=bmiProjection();if(!p.valid)show(`<strong>Check the inputs</strong><br>${p.message}`);else show(`<strong>${F(p.bmi,1)} BMI</strong><br>${p.category}; adult healthy-weight reference ${p.metric?`${F(p.lowKg,1)}-${F(p.highKg,1)} kg`:`${F(p.lowLb,1)}-${F(p.highLb,1)} lb`}.`);break}
  case'cn_bmi':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0;let band=bmi<18.5?'underweight':bmi<25?'healthy range':bmi<30?'overweight range':'obesity range';show(`<strong>${F(bmi,1)} BMI</strong><br>This falls in the ${band} by adult BMI screening ranges.`);break}
  case'cn_calorie':{let h=(V('feet')*12+V('inches'))*2.54,kg=V('weight')*0.453592,age=V('age'),sex=document.getElementById('sex')?.value||'male';let bmr=10*kg+6.25*h-5*age+(sex==='male'?5:-161),tdee=bmr*V('activity');show(`<strong>${F(tdee,0)} calories/day</strong><br>BMR: ${F(bmr,0)}. Protein planning range: ${F(kg*1.6,0)}-${F(kg*2.2,0)} g/day.`);break}
  case'cn_body_metric':{let h=V('feet')*12+V('inches'),bmi=h?703*V('weight')/(h*h):0,low=18.5*h*h/703,high=24.9*h*h/703;show(`<strong>${F(bmi,1)} BMI</strong><br>Adult BMI reference weight range at this height: ${F(low,0)}-${F(high,0)} lb.`);break}
  case'cn_due_date':{let d=new Date(document.getElementById('date')?.value||''),days=V('days');if(isNaN(d)){show('Enter a valid date.');break}let out=new Date(d.getTime()+days*86400000);show(`<strong>${out.toLocaleDateString('en-US',{year:'numeric',month:'long',day:'numeric'})}</strong><br>Calculated by adding ${F(days,0)} days to the start date.`);break}
  case'cn_pace':{let sec=V('hours')*3600+V('minutes')*60+V('seconds'),dist=V('distance');let pace=dist?sec/dist:0;show(`<strong>${Math.floor(pace/60)}:${String(Math.round(pace%60)).padStart(2,'0')} per mile</strong><br>Average speed: ${F(dist/(sec/3600),2)} mph.`);break}
  case'cn_percent':{let pct=V('whole')?V('part')/V('whole')*100:0,change=V('old')?(V('new')-V('old'))/V('old')*100:0;show(`<strong>${F(pct,2)}%</strong><br>Percent change from old to new value: ${F(change,2)}%.`);break}
  case'cn_triangle':{let a=V('a'),b=V('b'),c=Math.sqrt(a*a+b*b),area=a*b/2;show(`<strong>${F(c,4)} hypotenuse</strong><br>Area: ${F(area,4)}; perimeter: ${F(a+b+c,4)}.`);break}
  case'stats_advanced':{const p=statsProjection();if(!p.valid)show(`<strong>Check the data</strong><br>${p.message}`);else show(`<strong>${F(p.sd,6)} ${p.type} standard deviation</strong><br>Variance: ${F(p.variance,6)}; mean: ${F(p.mean,6)}; count: ${p.n}.`);break}
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
  case'bottleneck':{let cpu=V('cpu_score'),gpu=V('gpu_score'),res=V('resolution'),refresh=Math.max(30,V('refresh')),work=document.getElementById('workload')?.value||'gaming';let resLoad=res>=2160?1.35:res>=1440?1.12:0.9,refreshLoad=Math.min(1.6,Math.max(.75,refresh/144)),workCpu=work==='streaming'?1.18:work==='productivity'?0.92:1,workGpu=work==='productivity'?0.9:1;let cpuCap=cpu/(refreshLoad*workCpu),gpuNeed=gpu*resLoad*workGpu,ratio=cpuCap/Math.max(1,gpuNeed),pct=Math.min(99,Math.abs(1-ratio)*100),type=ratio<0.92?'CPU bottleneck':ratio>1.12?'GPU bottleneck':'balanced';show(`<strong>${type}: ${F(pct,1)}%</strong><br>Estimated from CPU score, GPU score, resolution, refresh rate, and workload.`);break}
  case'gpu_compute':{let cores=V('cores'),clock=V('clock')/1000,ops=V('ops'),mem=V('memory_clock'),bus=V('bus'),power=Math.max(1,V('power'));let tflops=cores*clock*ops/1000,bandwidth=mem*bus/8,eff=tflops/power;show(`<strong>${F(tflops,2)} TFLOPS</strong><br>Memory bandwidth: ${F(bandwidth,0)} GB/s; efficiency: ${F(eff,3)} TFLOPS per watt.`);break}
  case'ai_compute':{let params=V('params_b')*1e9,tokens=V('tokens_b')*1e9,gpus=Math.max(1,V('gpu_count')),tflops=V('gpu_tflops'),util=Math.max(1,V('utilization'))/100,power=V('power_kw');let flops=6*params*tokens,effective=gpus*tflops*1e12*util,hours=flops/effective/3600,days=hours/24,pflopDays=flops/1e15/86400,energy=power*hours;show(`<strong>${F(pflopDays,2)} PFLOP-days</strong><br>Estimated training time: ${F(days,2)} days; GPU hours: ${F(hours*gpus,0)}.`);break}
  case'ai_cost':{let req=V('requests'),input=V('input_tokens'),output=V('output_tokens'),inPrice=V('input_price'),outPrice=V('output_price'),days=V('days');let daily=req*((input/1000000)*inPrice+(output/1000000)*outPrice),monthly=daily*days,perReq=daily/Math.max(1,req);show(`<strong>${USD(monthly)} / billing period</strong><br>Daily cost: ${USD(daily)}; cost per request: ${USD(perReq)}.`);break}
  case'mining_profit':{let rev=V('revenue'),power=V('power'),elec=V('electricity'),fee=V('pool_fee')/100,hardware=V('hardware'),uptime=V('uptime')/100;let gross=rev*uptime,energy=power/1000*24*elec*uptime,fees=gross*fee,profit=gross-energy-fees,payback=profit>0?hardware/profit:Infinity;show(`<strong>${USD(profit)} / day</strong><br>Electricity: ${USD(energy)} / day; payback: ${Number.isFinite(payback)?F(payback,0)+' days':'not profitable'} at entered values.`);break}
  case'power_supply':{let base=V('cpu_watts')+V('gpu_watts')+V('drives')+V('fans')+V('other'),recommended=base*(1+V('headroom')/100),standard=[450,500,550,600,650,700,750,850,1000,1200,1300,1500,1600],psu=standard.find(x=>x>=recommended)||Math.ceil(recommended/100)*100;show(`<strong>${F(psu,0)} W PSU</strong><br>Estimated load: ${F(base,0)} W; with headroom: ${F(recommended,0)} W.`);break}
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
    const pct = Math.abs(bar.value) / total * 100;
    const valueText = `${bar.display || F(bar.value, 2)} (${F(pct,1)}%)`;
    const valueWidth = ctx.measureText(valueText).width;
    const valueX = Math.max(250, canvas.width - valueWidth - 16);
    const trackWidth = Math.max(80, valueX - 170);
    const width = trackWidth * Math.abs(bar.value) / max;
    ctx.fillStyle = "#344054";
    ctx.fillText(label, 16, y + 16);
    ctx.fillStyle = "#eef3f8";
    ctx.fillRect(158, y, trackWidth, 24);
    ctx.fillStyle = colors[index % colors.length];
    ctx.fillRect(158, y, Math.max(4, width), 24);
    ctx.fillStyle = "#152033";
    ctx.fillText(valueText, valueX, y + 17);
  });
}

function drawCompoundLine(canvas, schedule, durationLabel) {
  if (!canvas || !schedule.length) return;
  const ctx=clearCanvas(canvas), pad={left:48,right:18,top:18,bottom:30}, width=canvas.width-pad.left-pad.right, height=canvas.height-pad.top-pad.bottom;
  const points=[Math.max(0,V('principal')),...schedule.map(row=>row.balance)], max=Math.max(...points,1);
  ctx.strokeStyle="#d8e4f1";ctx.lineWidth=1;
  for(let i=0;i<=4;i++){const y=pad.top+height*i/4;ctx.beginPath();ctx.moveTo(pad.left,y);ctx.lineTo(pad.left+width,y);ctx.stroke()}
  ctx.beginPath();points.forEach((value,index)=>{const x=pad.left+width*index/Math.max(1,points.length-1),y=pad.top+height*(1-value/max);if(index===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});ctx.strokeStyle="#2563eb";ctx.lineWidth=3;ctx.stroke();
  ctx.fillStyle="#52647b";ctx.font="600 11px system-ui, sans-serif";ctx.textAlign="left";ctx.fillText("$0",5,pad.top+height);ctx.fillText(USD(max).replace('.00',''),5,pad.top+9);ctx.fillText("Start",pad.left,canvas.height-8);ctx.textAlign="right";ctx.fillText(durationLabel,canvas.width-pad.right,canvas.height-8);
}

function renderCompound(projection) {
  const summary=document.getElementById('compoundSummary'), pie=document.getElementById('compoundPie'), line=document.getElementById('compoundLine'), scenarios=document.querySelector('#compoundScenarios tbody'), table=document.querySelector('#compoundSchedule tbody');
  if(!summary||!pie||!line||!scenarios||!table)return;
  summary.innerHTML=[["Ending balance",USD(projection.balance),"Projected account value."],["Total contributed",USD(projection.contributed),"Initial amount plus additions."],["Net interest",USD(projection.totalInterest),`${F(projection.effectiveAnnual*100,3)}% APY before estimated tax.`],["Today's buying power",USD(projection.buyingPower),`${F(projection.inflation*100,2)}% assumed inflation.`]].map(item=>`<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join('');
  drawPie(pie,[projection.principal,projection.totalDeposits,Math.max(0,projection.totalInterest)],["Initial investment","Contributions","Net interest"]);
  drawCompoundLine(line,projection.schedule,projection.durationLabel);
  const low=compoundProjection({annualOverride:projection.annual-projection.rateVariance}),high=compoundProjection({annualOverride:projection.annual+projection.rateVariance});
  scenarios.innerHTML=[["Lower",low],["Entered",projection],["Higher",high]].map(([label,item])=>`<tr><td>${label}</td><td>${F(item.annual*100,2)}%</td><td>${USD(item.balance)}</td><td>${USD(item.totalInterest)}</td><td>${USD(item.buyingPower)}</td></tr>`).join('');
  table.innerHTML=projection.schedule.map(row=>`<tr><td>${row.period}</td><td>${USD(row.deposits)}</td><td>${USD(row.grossInterest)}</td><td>${USD(row.tax)}</td><td>${USD(row.balance)}</td></tr>`).join('');
}

function renderGeneric(cards, bars, rows) {
  const summary = document.getElementById("genericSummary");
  const chart = document.getElementById("genericChart");
  const table = document.querySelector("#genericTable tbody");
  if (!summary || !table) return;
  summary.innerHTML = cards.slice(0, 4).map(item => `<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join("");
  if (chart) {
    if (chart.dataset.chartType === "pie") drawPie(chart, bars.map(x => Math.abs(x.value)), bars.map(x => x.label));
    else drawGenericBars(chart, bars);
  }
  table.innerHTML = rows.map(row => `<tr><td>${row[0]}</td><td>${row[1]}</td><td>${row[2]}</td></tr>`).join("");
}

function renderGenericFromEngine(engine) {
  if (!document.getElementById("genericSummary")) return;
  let cards=[], bars=[], rows=[];
  if (engine === "debt_payoff_advanced") {
    const p=debtPayoffProjection(),orderBody=document.querySelector('#debtOrderTable tbody'),orderTitle=document.getElementById('debtOrderTitle');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Active debts",F(p.debts.length,0),"Positive balances entered."],["Extra payment",USD(p.extra),"Amount above listed minimums."],["Payoff estimate","Unavailable","Correct the inputs to continue."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(orderBody)orderBody.innerHTML=''}
    else{const selected=p.selected,label=p.strategy==='snowball'?'Debt snowball':'Debt avalanche',saved=p.baseline.valid?Math.max(0,p.baseline.interest-selected.interest):0,points=selected.schedule,step=Math.max(1,Math.ceil(points.length/9)),sampled=points.filter((item,index)=>index===0||index===points.length-1||index%step===0);cards=[["Debt-free estimate",selected.payoffLabel,`${F(selected.months,0)} monthly payments.`],["Total starting debt",USD(p.totalBalance),`${F(p.debts.length,0)} active debts.`],["Fixed monthly budget",USD(selected.monthlyBudget),`${USD(p.extra)} above entered minimums.`],["Interest saved",USD(saved),"Compared with the modeled no-extra plan."]];bars=sampled.map(item=>({label:item.month===0?'Start':item.month%12===0?`Year ${item.month/12}`:`Month ${item.month}`,value:item.balance,display:USD(item.balance)}));rows=[["Debt avalanche",p.avalanche.valid?p.avalanche.payoffLabel:"Over 100 years",p.avalanche.valid?USD(p.avalanche.interest):"Not paid off"],["Debt snowball",p.snowball.valid?p.snowball.payoffLabel:"Over 100 years",p.snowball.valid?USD(p.snowball.interest):"Not paid off"],["No extra payment",p.baseline.valid?p.baseline.payoffLabel:"Over 100 years",p.baseline.valid?USD(p.baseline.interest):"Not paid off"]];if(orderTitle)orderTitle.textContent=`${label} Payoff Order`;if(orderBody)orderBody.innerHTML=selected.order.map((item,index)=>`<tr><td>${index+1}</td><td><strong>${H(item.name)}</strong></td><td>${debtMonthLabel(p.start,item.month)}</td></tr>`).join('')}
  } else if (engine === "rmd_advanced") {
    const p=rmdProjection(),schedule=document.querySelector('#rmdSchedule tbody');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["RMD estimate","Unavailable","Correct the entered values."],["IRS table","Unavailable","No calculation completed."],["Schedule","Unavailable","Correct the inputs first."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(schedule)schedule.innerHTML=''}
    else{cards=p.cards;bars=p.bars;rows=p.rows;if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${x.year}</td><td>${x.age}</td><td>${USD(x.balance)}</td><td>${x.required?`${x.table.replace(' Table','')} / ${F(x.period,1)}`:'Not yet required'}</td><td>${USD(x.rmd)}</td><td>${USD(x.ending)}</td></tr>`).join('')}
  } else if (engine === "social_security_advanced") {
    const p=socialSecurityProjection(),schedule=document.querySelector('#ssSchedule tbody');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Benefit estimate","Unavailable","Correct the entered values."],["Comparison","Unavailable","No calculation completed."],["Details","Unavailable","Correct the inputs first."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(schedule)schedule.innerHTML=''}
    else{cards=p.cards;bars=p.bars;rows=p.rows;if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${socialSecurityAgeLabel(x.claimMonths)}</td><td>${F(x.factor*100,2)}%</td><td>${USD(x.monthly)}</td><td>${USD(x.total)}</td><td>${USD(x.value)}</td></tr>`).join('')}
  } else if (engine === "401k_advanced") {
    const p=k401Projection(),schedule=document.querySelector('#k401Schedule tbody');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["401(k) estimate","Unavailable","Correct the entered values."],["Breakdown","Unavailable","No calculation completed."],["Details","Unavailable","Correct the inputs first."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(schedule)schedule.innerHTML=''}
    else{cards=p.cards;bars=p.bars;rows=p.rows;if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${F(x.age,0)}</td><td>${USD(x.salary)}</td><td>${USD(x.employee)}</td><td>${USD(x.employer)}</td><td>${USD(x.growth)}</td><td>${USD(x.balance)}</td></tr>`).join('')}
  } else if (engine === "retirement_advanced") {
    const p=retirementProjection(),schedule=document.querySelector('#retirementSchedule tbody');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Retirement target","Unavailable","Correct the ages or amounts."],["Projection","Unavailable","No projection calculated."],["Annual schedule","Unavailable","Correct the inputs first."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(schedule)schedule.innerHTML=''}
    else{cards=p.cards;bars=p.bars;rows=p.rows;if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${x.label}</td><td>${x.cashflow<0?'-':''}${USD(Math.abs(x.cashflow))}</td><td>${USD(x.growth)}</td><td>${USD(x.balance)}</td></tr>`).join('')}
  } else if (engine === "amortization_advanced") {
    const p=amortizationProjection(),annual=document.querySelector('#amortAnnual tbody'),monthly=document.querySelector('#amortMonthly tbody');
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Monthly payment","Unavailable","No schedule calculated."],["Payoff date","Unavailable","Review the entered values."],["Total interest","Unavailable","Review the entered values."]];bars=[{label:"Principal",value:p.principal||0,display:USD(p.principal||0)},{label:"Interest",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(annual)annual.innerHTML='';if(monthly)monthly.innerHTML=''}
    else{cards=[["Scheduled payment",USD(p.regularPayment),"Monthly principal and interest."],["Payoff date",p.payoffDate,p.termLabel],["Total interest",USD(p.totalInterest),p.active?`${USD(p.interestSaved)} saved with extras.`:"No extra principal entered."],["Time saved",`${F(p.monthsSaved,0)} months`,p.active?`${USD(p.totalExtra)} extra principal paid.`:"Add extra payments to compare."]];bars=[{label:"Principal",value:p.principal,display:USD(p.principal)},{label:"Interest",value:p.totalInterest,display:USD(p.totalInterest)}];rows=[["Loan amount",USD(p.principal),"Starting principal."],["Annual interest rate",`${F(p.annual*100,3)}%`,"Fixed nominal rate divided by 12."],["Scheduled monthly payment",USD(p.regularPayment),"Excludes optional extra principal."],["Original payoff term",`${F(p.baseline.payoffMonths,0)} months`,"Schedule without extra payments."],["Estimated payoff",p.payoffDate,`${F(p.payoffMonths,0)} monthly payments.`],["Total paid",USD(p.totalPaid),"Principal plus interest."],["Total interest",USD(p.totalInterest),"Sum of monthly interest."],["Extra principal paid",USD(p.totalExtra),"Recurring and one-time extras."],["Interest saved",USD(p.interestSaved),"Compared with the original schedule."],["Time saved",`${F(p.monthsSaved,0)} months`,"Compared with the original schedule."]];if(annual)annual.innerHTML=p.annualRows.map(x=>`<tr><td>${x.year}</td><td>${USD(x.payments)}</td><td>${USD(x.principal)}</td><td>${USD(x.interest)}</td><td>${USD(x.balance)}</td></tr>`).join('');if(monthly)monthly.innerHTML=p.schedule.map(x=>`<tr><td>${x.month}</td><td>${USD(x.payment)}</td><td>${USD(x.principal)}</td><td>${USD(x.interest)}</td><td>${USD(x.extra)}</td><td>${USD(x.balance)}</td></tr>`).join('')}
  } else if (engine === "finance_tvm") {
    const p=financeProjection(),schedule=document.querySelector('#financeSchedule tbody'),labels={fv:'Future value',pmt:'Periodic payment',iy:'Annual interest rate',n:'Number of periods',pv:'Present value'};
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Solved variable",labels[p.target],"Selected target."],["Periodic rate","Unavailable","No valid solution."],["Schedule","Unavailable","Correct the inputs first."]];bars=[{label:"Result",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]];if(schedule)schedule.innerHTML=''}
    else{const solved=p.target==='iy'?`${F(p.iy,8)}%`:p.target==='n'?F(p.n,8):USD(p[p.target]);cards=[[labels[p.target],solved,"Calculated TVM variable."],["Periodic rate",`${F(p.rate*100,6)}%`,`${F(p.py,0)} payment periods per year.`],["Effective annual rate",`${F(p.effectiveAnnual,6)}%`,`Derived from the payment-period rate.`],["Ending balance",USD(p.balance),`Should offset FV under the sign convention.`]];bars=[{label:"Present value",value:p.pv,display:USD(p.pv)},{label:"Total payments",value:p.totalPayments,display:USD(p.totalPayments)},{label:"Future value",value:p.fv,display:USD(p.fv)},{label:"Total interest",value:p.totalInterest,display:USD(p.totalInterest)}];rows=[["Solved variable",labels[p.target],solved],["Number of periods (N)",F(p.n,8),`${F(p.py,0)} payments per year.`],["Nominal annual rate (I/Y)",`${F(p.iy,8)}%`,`${F(p.cy,0)} compounding periods per year.`],["Present value (PV)",USD(p.pv),"Starting cash flow."],["Periodic payment (PMT)",USD(p.pmt),p.due?"Paid at the beginning of each period.":"Paid at the end of each period."],["Future value (FV)",USD(p.fv),"Opposite-side terminal cash flow."],["Effective periodic rate",`${F(p.rate*100,8)}%`,"Rate applied per payment period."],["Effective annual rate",`${F(p.effectiveAnnual,8)}%`,"Compounded payment-period rate."],["Sum of periodic payments",USD(p.totalPayments),"PMT multiplied by N."],["Total interest",USD(p.totalInterest),"Implied interest across all periods."],["Equation residual",USD(p.residual),"Rounding check; should be close to zero."]];if(p.scheduleCapped)rows.push(["Schedule display","First 600 periods","The result still uses the full entered period count."]);if(schedule)schedule.innerHTML=p.schedule.map(item=>`<tr><td>${item.period}</td><td>${USD(item.opening)}</td><td>${USD(item.payment)}</td><td>${USD(item.interest)}</td><td>${USD(item.ending)}</td></tr>`).join('')}
  } else if (engine === "length_convert") {
    const p=priorityLengthProjection();
    cards=[[`${p.to.charAt(0).toUpperCase()+p.to.slice(1)}`,`${F(p.result,10)} ${p.toSymbol}`,`${F(p.value,10)} ${p.fromSymbol} converted.`],["Meters",`${F(p.meters,10)} m`,"SI base unit for length."],["Decimal feet",`${F(p.feet,10)} ft`,"International feet."],["Inches",`${F(p.inches,10)} in`,"International inches."]];
    bars=[];
    rows=[["Entered measurement",`${F(p.value,12)} ${p.fromSymbol}`,p.from],["Converted result",`${F(p.result,12)} ${p.toSymbol}`,p.to],["Active conversion factor",F(p.activeFactor,12),`Multiply ${p.fromSymbol} by this factor.`],["Meters",`${F(p.meters,12)} m`,"Base SI length."],["Centimeters",`${F(p.centimeters,12)} cm`,"Meters x 100."],["Millimeters",`${F(p.millimeters,12)} mm`,"Meters x 1,000."],["Decimal feet",`${F(p.feet,12)} ft`,"Meters divided by 0.3048."],["Inches",`${F(p.inches,12)} in`,"Meters divided by 0.0254."]];
  } else if (engine === "feet_meters") {
    const reverse=document.getElementById('conversion_direction')?.value==='meters_to_feet';
    const meters=Math.max(0,reverse?V('meters'):(Math.max(0,V('feet'))+Math.max(0,V('inches'))/12)*0.3048), totalFeet=meters/0.3048, wholeFeet=Math.floor(totalFeet), inches=(totalFeet-wholeFeet)*12;
    cards=[["Meters",`${F(meters,6)} m`,"International System of Units."],["Centimeters",`${F(meters*100,3)} cm`,"Meters multiplied by 100."],["Decimal feet",`${F(totalFeet,6)} ft`,"Meters divided by 0.3048."],["Feet and inches",`${wholeFeet} ft ${F(inches,3)} in`,"US customary notation."]];
    bars=[];
    rows=[["Exact conversion factor","1 ft = 0.3048 m","International foot definition."],["Meters",`${F(meters,8)} m`,"Total feet multiplied by 0.3048."],["Centimeters",`${F(meters*100,6)} cm`,"Meters multiplied by 100."],["Decimal feet",`${F(totalFeet,8)} ft`,"Meters divided by 0.3048."],["Feet and inches",`${wholeFeet} ft ${F(inches,4)} in`,"Whole feet plus the remaining inches."],["Total inches",`${F(totalFeet*12,6)} in`,"Decimal feet multiplied by 12."],["Yards",`${F(totalFeet/3,8)} yd`,"Feet divided by 3."]];
  } else if (engine === "loan") {
    const P=V('amount'), rr=V('apr')/1200, n=Math.max(1,(V('years')*12)+(V('months_extra')||V('months'))), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, interest=total-P;
    cards=[["Monthly payment",USD(pay),"Estimated recurring payment."],["Total paid",USD(total),"Principal plus interest."],["Total interest",USD(interest),"Cost of borrowing."],["Loan term",`${F(n,0)} months`,"Entered repayment period."]];
    bars=[{label:"Principal",value:P,display:USD(P)},{label:"Interest",value:interest,display:USD(interest)},{label:"Monthly payment",value:pay,display:USD(pay)}];
    rows=[["Loan amount",USD(P),"Starting balance."],["APR",`${F(V('apr'),2)}%`,"Annual percentage rate."],["Term",`${F(n,0)} months`,"Number of payments."],["Total paid",USD(total),"Payment multiplied by term."]];
  } else if (engine === "car_loan") {
    const price=V('price'), tax=price*V('tax')/100, fees=V('fees'), include=(document.getElementById('include_fees')?.value||'0')==='1', base=Math.max(0,price-V('incentives')-V('down')-V('trade')+V('owed')), P=Math.max(0,base+(include?tax+fees:0)), rr=V('apr')/1200, n=Math.max(1,V('months')), pay=rr?P*rr*Math.pow(1+rr,n)/(Math.pow(1+rr,n)-1):P/n, total=pay*n, upfront=V('down')+(include?0:tax+fees);
    cards=[["Monthly Pay",USD(pay),"Estimated auto loan payment."],["Total Loan Amount",USD(P),"Amount financed."],["Sale Tax",USD(tax),"Estimated tax from entered rate."],["Upfront Payment",USD(upfront),"Down payment plus taxes and fees when not financed."]];
    bars=[{label:"Loan amount",value:P,display:USD(P)},{label:"Interest",value:total-P,display:USD(total-P)},{label:"Upfront",value:upfront,display:USD(upfront)}];
    rows=[["Monthly Pay",USD(pay),"Payment every month."],["Total Loan Amount",USD(P),"Balance used for amortization."],["Total of Payments",USD(total),"Monthly payment times term."],["Total Loan Interest",USD(total-P),"Total paid minus loan amount."],["Sale Tax",USD(tax),"Auto price times tax rate."],["Upfront Payment",USD(upfront),"Due at purchase if not financed."]];
  } else if (engine === "payment_advanced") {
    const p=paymentProjection(),schedule=document.querySelector('#paymentSchedule tbody'),modeLabel=p.mode==='term'?'Fixed Term':'Fixed Payments';
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Calculation mode",modeLabel,"Selected payment mode."],["Monthly payment","Unavailable","No amortizing payment calculated."],["Payoff time","Unavailable","Review the entered values."]];bars=[{label:"Loan amount",value:p.principal,display:USD(p.principal)},{label:"Interest",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message],["Calculation mode",modeLabel,"Selected payment mode."],["Loan amount",USD(p.principal),"Entered principal."],["Annual interest rate",`${F(p.annual*100,3)}%`,"Fixed nominal annual rate."]];if(schedule)schedule.innerHTML=''}
    else{cards=[["Monthly payment",USD(p.regularPayment),p.mode==='term'?"Required payment for the entered term.":"Entered fixed payment."],["Payoff time",p.termLabel,`${F(p.monthsExact,3)} calculated months.`],["Total interest",USD(p.totalInterest),"Total paid minus principal."],["Total paid",USD(p.totalPaid),`${F(p.payoffMonths,0)} scheduled payments.`]];bars=[{label:"Loan principal",value:p.principal,display:USD(p.principal)},{label:"Total interest",value:p.totalInterest,display:USD(p.totalInterest)},{label:"Monthly payment",value:p.regularPayment,display:USD(p.regularPayment)}];rows=[["Calculation mode",modeLabel,p.mode==='term'?"Solve for monthly payment.":"Solve for payoff time."],["Loan amount",USD(p.principal),"Starting principal."],["Annual interest rate",`${F(p.annual*100,3)}%`,"Nominal rate divided by 12 each month."],["Monthly rate",`${F(p.rate*100,6)}%`,"Rate applied to the opening balance."],["Regular monthly payment",USD(p.regularPayment),"The final payment can be smaller."],["Calculated payoff periods",F(p.monthsExact,6),"Unrounded mathematical result."],["Scheduled payoff time",p.termLabel,`${F(p.payoffMonths,0)} whole monthly payments.`],["Total interest",USD(p.totalInterest),"Sum of monthly interest charges."],["Total paid",USD(p.totalPaid),"Principal plus interest."]];if(schedule)schedule.innerHTML=p.schedule.map(item=>`<tr><td>${F(item.month,0)}</td><td>${USD(item.payment)}</td><td>${USD(item.principal)}</td><td>${USD(item.interest)}</td><td>${USD(item.balance)}</td></tr>`).join('')}
  } else if (engine === "interest_advanced") {
    const p=interestComparisonProjection(),c=p.compound,schedule=document.querySelector('#interestSchedule tbody'),frequency=c.frequency===0?'Continuous':`${F(c.frequency,0)} times/year`;
    cards=[["Compound ending balance",USD(c.balance),`${F(c.effectiveAnnual*100,3)}% effective annual yield.`],["Simple ending balance",USD(p.simpleBalance),"Interest does not earn additional interest."],["Compound advantage",USD(p.advantage),"Difference between the two methods."],["Today's buying power",USD(c.buyingPower),`${F(c.inflation*100,2)}% assumed inflation.`]];
    bars=[{label:"Initial investment",value:c.principal,display:USD(c.principal)},{label:"Additional deposits",value:c.totalDeposits,display:USD(c.totalDeposits)},{label:"Simple net interest",value:p.simpleInterest,display:USD(p.simpleInterest)},{label:"Compound net interest",value:c.totalInterest,display:USD(c.totalInterest)}];
    rows=[["Initial investment",USD(c.principal),"Starting principal."],["Additional deposits",USD(c.totalDeposits),`${USD(c.monthly)} monthly and ${USD(c.annualContribution)} annually.`],["Total contributed",USD(c.contributed),"Initial investment plus deposits."],["Nominal annual rate",`${F(c.annual*100,3)}%`,"Entered annual rate."],["Compounding frequency",frequency,"Used only for the compound projection."],["Effective annual yield",`${F(c.effectiveAnnual*100,4)}%`,"Yield before the illustrative tax estimate."],["Simple gross interest",USD(p.simpleGrossInterest),"Interest earned only on contributed principal."],["Compound gross interest",USD(c.totalGrossInterest),"Includes interest earned on prior interest."],["Estimated simple interest tax",USD(p.simpleTax),`${F(c.taxRate*100,2)}% entered tax rate.`],["Estimated compound interest tax",USD(c.totalTax),`${F(c.taxRate*100,2)}% entered tax rate.`],["Simple ending balance",USD(p.simpleBalance),"Contributions plus net simple interest."],["Compound ending balance",USD(c.balance),"Contributions plus net compound interest."],["Compound advantage",USD(p.advantage),"Compound balance minus simple balance."],["Simple buying power",USD(p.simpleBuyingPower),`${F(c.inflation*100,2)}% assumed inflation.`],["Compound buying power",USD(c.buyingPower),`${F(c.inflation*100,2)}% assumed inflation.`]];
    if(schedule)schedule.innerHTML=p.schedule.map(item=>`<tr><td>${item.period}</td><td>${USD(item.contributed)}</td><td>${USD(item.simpleBalance)}</td><td>${USD(item.compoundBalance)}</td><td>${USD(item.advantage)}</td></tr>`).join('');
  } else if (engine === "compound" || engine === "cn_retirement") {
    const P=V('principal'), rr=V('rate')/1200, n=V('years')*12, pmt=V('monthly'), fv=P*Math.pow(1+rr,n)+(rr?pmt*(Math.pow(1+rr,n)-1)/rr:pmt*n), contrib=P+pmt*n, growth=fv-contrib;
    cards=[["Future value",USD(fv),"Projected ending balance."],["Contributions",USD(contrib),"Starting amount plus deposits."],["Growth",USD(growth),"Estimated investment return."],["Time",`${F(V('years'),1)} years`,"Growth period."]];
    bars=[{label:"Starting amount",value:P,display:USD(P)},{label:"Deposits",value:pmt*n,display:USD(pmt*n)},{label:"Growth",value:growth,display:USD(growth)}];
    rows=[["Starting amount",USD(P),"Initial balance."],["Monthly contribution",USD(pmt),"Recurring addition."],["Annual return",`${F(V('rate'),2)}%`,"Assumed return."],["Projected balance",USD(fv),"Estimate before taxes and fees."]];
  } else if (engine === "bmi_advanced") {
    const p=bmiProjection();
    if(!p.valid){cards=[["Result","Check the inputs",p.message],["BMI","Unavailable","Positive height and weight are required."],["Category","Unavailable","No adult category calculated."],["Reference range","Unavailable","No range calculated."]];bars=[{label:"BMI",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate",p.message]]}
    else{
      const weightDisplay=p.metric?`${F(p.kg,2)} kg`:`${F(p.weightLb,2)} lb`,heightDisplay=p.metric?`${F(p.meters*100,2)} cm`:`${F(Math.floor(p.heightIn/12),0)} ft ${F(p.heightIn%12,2)} in`,rangeDisplay=p.metric?`${F(p.lowKg,1)}-${F(p.highKg,1)} kg`:`${F(p.lowLb,1)}-${F(p.highLb,1)} lb`,differenceDisplay=p.metric?`${F(p.difference,1)} kg`:`${F(p.difference/0.45359237,1)} lb`;
      cards=[["Adult BMI",F(p.bmi,1),p.category],["CDC category",p.category,"Adult screening category."],["Healthy-weight reference",rangeDisplay,"BMI 18.5 to less than 25."],["BMI Prime",F(p.bmiPrime,3),"BMI divided by 25."]];
      bars=[{label:"Your BMI",value:p.bmi,display:F(p.bmi,1)},{label:"Healthy starts",value:18.5,display:"18.5"},{label:"Overweight starts",value:25,display:"25.0"},{label:"Obesity starts",value:30,display:"30.0"},{label:"Class 3 starts",value:40,display:"40.0"}];
      rows=[["Units",p.metric?"Metric":"US customary","Selected input system."],["Height",heightDisplay,`${F(p.meters,4)} meters.`],["Weight",weightDisplay,`${F(p.kg,3)} kilograms.`],["BMI",F(p.bmi,4),p.metric?"kg / m^2.":"703 x lb / in^2."],["Adult BMI category",p.category,"CDC category for adults age 20 and older."],["Healthy-weight reference",rangeDisplay,"Weight at BMI 18.5 through 24.9 for this height."],["Position versus reference",p.direction==='within'?"Within reference range":`${differenceDisplay} ${p.direction} the reference range`,"Mathematical comparison, not a weight recommendation."],["BMI Prime",F(p.bmiPrime,5),"BMI divided by 25."],["Ponderal Index",`${F(p.ponderal,4)} kg/m^3`,"Weight divided by height cubed."],["Important limitation","Screening measure only","BMI does not diagnose disease or directly measure body fat."]];
    }
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
  } else if (engine === "sales_tax_advanced") {
    const p=salesTaxProjection(),modeLabel=p.mode==='reverse'?"Reverse tax":p.mode==='rate'?"Find tax rate":"Add tax";
    cards=[[p.mode==='rate'?"Implied tax rate":"After-tax total",p.mode==='rate'?`${F(p.rate,3)}%`:USD(p.after),p.mode==='rate'?"Derived from before-tax and after-tax prices.":"Before-tax total plus sales tax."],["Sales tax",USD(p.tax),`${F(p.rate,3)}% of the taxable amount.`],["Before-tax total",USD(p.before),p.mode==='reverse'?"Calculated from the tax-inclusive total.":"Merchandise and entered shipping before tax."],["Taxable amount",USD(p.taxableBase),"Amount used to calculate tax."]];
    bars=[{label:"Before-tax total",value:p.before,display:USD(p.before)},{label:"Sales tax",value:p.tax,display:USD(p.tax)},{label:"After-tax total",value:p.after,display:USD(p.after)}];
    rows=[["Calculation mode",modeLabel,"Selected sales-tax operation."],["Sales tax rate",`${F(p.rate,3)}%`,p.mode==='rate'?"Calculated from the two prices.":"Entered combined rate."],["Before-tax total",USD(p.before),p.mode==='add'?"Discounted merchandise plus shipping.":"Amount before sales tax."],["Taxable amount",USD(p.taxableBase),p.mode==='add'&&p.shippingTaxable?"Includes merchandise and shipping.":"Amount subject to the entered rate."],["Sales tax",USD(p.tax),"Taxable amount times the rate."],["After-tax total",USD(p.after),"Before-tax total plus sales tax."]];
    if(p.mode==='add')rows.splice(2,0,["Original unit price",USD(p.price),"Price before discount."],["Discounted unit price",USD(p.discountedUnit),`${F(p.discount,2)}% entered discount.`],["Quantity",F(p.quantity,0),"Number of items."],["Merchandise subtotal",USD(p.merchandise),"Discounted unit price times quantity."],["Shipping",USD(p.shipping),p.shippingTaxable?"Included in taxable amount.":"Not included in taxable amount."],["Discount savings",USD(p.savings),"Savings across all items."]);
  } else if (engine === "take_home_pay") {
    const p=takeHomeProjection(),statusLabel=p.status==='joint'?"Married filing jointly":p.status==='head'?"Head of household":"Single";
    cards=[["Take-home / paycheck",USD(p.perPay),`${F(p.periods,0)} paychecks per year.`],["Annual take-home",USD(p.net),"After estimated taxes and deductions."],["Monthly average",USD(p.monthly),"Annual net pay divided by 12."],["Effective tax rate",`${F(p.effective,2)}%`,"Estimated taxes divided by gross pay."]];
    bars=[{label:"Gross pay",value:p.gross,display:USD(p.gross)},{label:"Take-home pay",value:p.net,display:USD(p.net)},{label:"Estimated taxes",value:p.totalTax,display:USD(p.totalTax)},{label:"Payroll deductions",value:p.totalDeductions,display:USD(p.totalDeductions)}];
    rows=[["Gross annual salary",USD(p.gross),USD(p.grossPerPay)+" gross per paycheck."],["Filing status",statusLabel,"Used for 2026 federal brackets and deduction."],["Federal deduction",USD(p.deduction),p.custom?"Entered custom deduction.":"2026 standard deduction."],["Federal taxable income",USD(p.federalTaxable),"Gross less modeled pre-tax amounts and deduction."],["Federal income tax",USD(p.federal),`${F(p.marginal*100,0)}% estimated marginal bracket.`],["Social Security",USD(p.social),"6.2% up to the $184,500 wage base."],["Medicare",USD(p.medicare),"1.45% plus applicable Additional Medicare Tax."],["State and local tax",USD(p.state),`${F(p.stateRate,2)}% entered effective rate.`],["Extra federal withholding",USD(p.extra),USD(p.extraPerPay)+" per paycheck."],["Pre-tax retirement",USD(p.retirement),"Reduces modeled federal taxable income, not FICA wages."],["Other pre-tax benefits",USD(p.pretax),"Assumed to reduce income-tax and FICA wages."],["Post-tax deductions",USD(p.posttax),"Reduces take-home pay only."],["Total estimated taxes",USD(p.totalTax),"Federal, FICA, state or local, and extra withholding."],["Annual take-home pay",USD(p.net),"Gross pay less modeled taxes and deductions."]];
  } else if (engine === "salary_converter") {
    const p=salaryConverterProjection();
    if(!p.valid){cards=[["Result","Check the inputs","Enter a positive work schedule."],["Annual pay","Unavailable","Unable to annualize."],["Monthly pay","Unavailable","Unable to convert."],["Adjusted pay","Unavailable","Unable to calculate."]];bars=[{label:"Annual pay",value:0,display:"Unavailable"}];rows=[["Validation","Unable to calculate","Hours and days per week must be positive."]]}
    else{
      const labels={hour:"Hourly",day:"Daily",week:"Weekly",biweekly:"Biweekly",semimonthly:"Semimonthly",month:"Monthly",quarter:"Quarterly",year:"Annual"},keys=["hour","day","week","biweekly","semimonthly","month","quarter","year"];
      cards=[["Annual gross equivalent",USD(p.annual),"Before taxes and deductions."],["Monthly gross",USD(p.unadjusted.month),"Annual equivalent divided by 12."],["Biweekly gross",USD(p.unadjusted.biweekly),"Annual equivalent divided by 26."],["Adjusted annual",USD(p.adjustedAnnual),`${F(p.daysOff,0)} unpaid non-working days.`]];
      bars=[{label:"Annual unadjusted",value:p.annual,display:USD(p.annual)},{label:"Annual adjusted",value:p.adjustedAnnual,display:USD(p.adjustedAnnual)},{label:"Monthly unadjusted",value:p.unadjusted.month,display:USD(p.unadjusted.month)},{label:"Monthly adjusted",value:p.adjusted.month,display:USD(p.adjusted.month)}];
      rows=keys.map(key=>[labels[key],USD(p.unadjusted[key]),USD(p.adjusted[key])]);rows.push(["Scheduled workdays",F(p.workdays,1),`${F(p.days,2)} days/week x 52.`],["Entered non-working days",F(p.daysOff,1),`${F(p.holidays,0)} holidays + ${F(p.vacation,0)} vacation days.`],["Adjusted work-year factor",`${F(p.factor*100,2)}%`,"Share of scheduled workdays remaining."],["Effective hourly value with paid leave",USD(p.effectiveHourly),"Annual gross divided by hours actually worked; informational only."]);
    }
  } else if (engine === "cn_tax_salary") {
    const income=V('income'), taxable=Math.max(0,income-V('deductions')), tax=taxable*V('taxrate')/100, net=income-tax;
    cards=[["Take-home pay",USD(net),"Estimated annual net pay."],["Monthly net",USD(net/12),"Estimated monthly take-home."],["Estimated tax",USD(tax),"Taxable income times rate."],["Taxable income",USD(taxable),"Income minus deductions."]];
    bars=[{label:"Take-home",value:net,display:USD(net)},{label:"Tax",value:tax,display:USD(tax)},{label:"Deductions",value:V('deductions'),display:USD(V('deductions'))}];
    rows=[["Gross income",USD(income),"Entered annual income."],["Deductions",USD(V('deductions')),"Entered deductions."],["Effective rate",`${F(V('taxrate'),2)}%`,"Applied to taxable income."],["Net pay",USD(net),"Estimated take-home."]];
  } else if (engine === "fraction_advanced") {
    const p=fractionProjection();
    if(!p.valid){cards=[["Result","Undefined",p.step],["Status","Check inputs","Denominators and divisors must be nonzero."],["Decimal","Undefined","No finite result."],["Percentage","Undefined","No finite result."]];bars=[{label:"Result",value:0,display:"Undefined"}];rows=[["Validation","Undefined",p.step]]}
    else{
      const decimal=p.result.n/p.result.d,improper=fractionText(p.result),mixed=mixedText(p.result),percent=`${F(decimal*100,6)}%`;
      cards=[["Simplified fraction",improper,"Answer in lowest terms."],["Mixed number",mixed,"Whole-number and fractional form."],["Decimal",F(decimal,10),"Numerator divided by denominator."],["Percentage",percent,"Decimal multiplied by 100."]];
      if(p.mode==='arithmetic'){
        bars=[{label:"First number",value:p.a.n/p.a.d,display:fractionText(p.a)},{label:"Second number",value:p.b.n/p.b.d,display:fractionText(p.b)},{label:"Result",value:decimal,display:improper}];
        rows=[["Convert first number",fractionText(p.a),"Improper fraction in lowest terms."],["Convert second number",fractionText(p.b),"Improper fraction in lowest terms."],["Operation",`${fractionText(p.a)} ${p.operator} ${fractionText(p.b)}`,p.step],["Before reduction",`${p.rawN}/${p.rawD}`,"Numerator and denominator after the operation."],["Greatest common divisor",F(fractionGcd(p.rawN,p.rawD),0),"Divide both terms by this value."],["Simplified fraction",improper,"Final fraction in lowest terms."],["Mixed number",mixed,"Equivalent mixed-number form."],["Decimal",F(decimal,10),"Equivalent decimal value."],["Percentage",percent,"Equivalent percentage."]];
      }else if(p.mode==='simplify'){
        bars=[{label:"Original numerator",value:p.rawN,display:F(p.rawN,0)},{label:"Original denominator",value:p.rawD,display:F(p.rawD,0)},{label:"Result",value:decimal,display:improper}];
        rows=[["Original fraction",`${p.rawN}/${p.rawD}`,"Entered fraction."],["Greatest common divisor",F(fractionGcd(p.rawN,p.rawD),0),p.step],["Simplified fraction",improper,"Final fraction in lowest terms."],["Mixed number",mixed,"Equivalent mixed-number form."],["Decimal",F(decimal,10),"Equivalent decimal value."],["Percentage",percent,"Equivalent percentage."]];
      }else{
        const entered=document.getElementById('fraction_decimal')?.value||'0';bars=[{label:"Entered decimal",value:Number(entered),display:entered},{label:"Numerator",value:p.result.n,display:F(p.result.n,0)},{label:"Denominator",value:p.result.d,display:F(p.result.d,0)}];
        rows=[["Entered decimal",entered,"Original value."],["Power-of-ten fraction",p.step,"Built from the decimal places."],["Simplified fraction",improper,"Final fraction in lowest terms."],["Mixed number",mixed,"Equivalent mixed-number form."],["Percentage",percent,"Equivalent percentage."]];
      }
    }
  } else if (engine === "percent_advanced") {
    const p=percentageProjection();
    if(p.mode==='what_percent'){
      cards=[["Percentage",p.answer,"Part as a share of the whole."],["Part",F(p.a,4),"Entered numerator."],["Whole",F(p.b,4),"Entered denominator."],["Decimal ratio",p.valid?F(p.result/100,6):"Undefined","Part divided by whole."]];
      bars=[{label:"Part",value:p.a,display:F(p.a,4)},{label:"Whole",value:p.b,display:F(p.b,4)},{label:"Percent",value:p.result,display:p.answer}];
      rows=[["Question",`${F(p.a,4)} is what percent of ${F(p.b,4)}?`,"Selected calculation."],["Formula",p.formula,"Standard part-to-whole percentage."],["Answer",p.answer,p.detail]];
    }else if(p.mode==='find_whole'){
      cards=[["Whole",p.answer,"Recovered base value."],["Known part",F(p.a,4),"Entered part."],["Known percentage",`${F(p.b,4)}%`,"Entered share of the whole."],["Decimal rate",F(p.b/100,6),"Percentage divided by 100."]];
      bars=[{label:"Known part",value:p.a,display:F(p.a,4)},{label:"Calculated whole",value:p.result,display:p.answer},{label:"Percentage",value:p.b,display:`${F(p.b,4)}%`}];
      rows=[["Question",`${F(p.a,4)} is ${F(p.b,4)}% of what?`,"Selected calculation."],["Formula",p.formula,"Divide by the decimal percentage."],["Answer",p.answer,p.detail]];
    }else if(p.mode==='change'){
      cards=[["Percent change",p.answer,p.valid?p.detail:"Original value cannot be zero."],["Absolute change",F(p.change,4),"New minus original."],["Original value",F(p.a,4),"Baseline denominator."],["New value",F(p.b,4),"Comparison value."]];
      bars=[{label:"Original",value:p.a,display:F(p.a,4)},{label:"New",value:p.b,display:F(p.b,4)},{label:"Absolute change",value:Math.abs(p.change),display:F(p.change,4)}];
      rows=[["Original value",F(p.a,4),"Baseline."],["New value",F(p.b,4),"Comparison."],["Absolute change",F(p.change,4),"New minus original."],["Formula",p.formula,"Relative to the original magnitude."],["Percent change",p.answer,p.detail]];
    }else if(p.mode==='difference'){
      cards=[["Percentage difference",p.answer,"Symmetric comparison without a baseline."],["Absolute difference",F(Math.abs(p.a-p.b),4),"Distance between values."],["Average magnitude",F(p.average,4),"Denominator used by the formula."],["Values",`${F(p.a,4)} and ${F(p.b,4)}`,"Entered pair."]];
      bars=[{label:"First value",value:p.a,display:F(p.a,4)},{label:"Second value",value:p.b,display:F(p.b,4)},{label:"Absolute difference",value:Math.abs(p.a-p.b),display:F(Math.abs(p.a-p.b),4)}];
      rows=[["First value",F(p.a,4),"Entered value."],["Second value",F(p.b,4),"Entered value."],["Average magnitude",F(p.average,4),"Average of absolute values."],["Formula",p.formula,"Symmetric percentage difference."],["Answer",p.answer,p.detail]];
    }else if(p.mode==='adjust'){
      cards=[["Adjusted value",p.answer,`After the ${p.direction}.`],["Starting value",F(p.a,4),"Entered base."],["Percent",`${F(p.b,4)}%`,`${p.direction} rate.`],["Amount changed",F(p.change,4),"Signed difference from the start."]];
      bars=[{label:"Starting value",value:p.a,display:F(p.a,4)},{label:"Change amount",value:Math.abs(p.change),display:F(p.change,4)},{label:"Adjusted value",value:p.result,display:p.answer}];
      rows=[["Operation",p.direction==='decrease'?"Decrease":"Increase","Selected adjustment."],["Starting value",F(p.a,4),"Entered base."],["Percentage",`${F(p.b,4)}%`,"Entered rate."],["Formula",p.formula,"Multiplier method."],["Adjusted value",p.answer,p.detail]];
    }else{
      cards=[["Answer",p.answer,p.detail],["Percentage",`${F(p.a,4)}%`,"Entered rate."],["Whole",F(p.b,4),"Entered value."],["Remaining amount",F(p.b-p.result,4),"Whole minus the calculated part."]];
      bars=[{label:"Whole",value:p.b,display:F(p.b,4)},{label:"Calculated part",value:p.result,display:p.answer},{label:"Remaining",value:p.b-p.result,display:F(p.b-p.result,4)}];
      rows=[["Question",`What is ${F(p.a,4)}% of ${F(p.b,4)}?`,"Selected calculation."],["Decimal percentage",F(p.a/100,6),"Percentage divided by 100."],["Formula",p.formula,"Multiply decimal rate by whole."],["Answer",p.answer,p.detail]];
    }
  } else if (engine === "cn_percent") {
    const pct=V('whole')?V('part')/V('whole')*100:0, change=V('old')?(V('new')-V('old'))/V('old')*100:0;
    cards=[["Percentage",`${F(pct,2)}%`,"Part as a share of whole."],["Percent change",`${F(change,2)}%`,"New versus old value."],["Difference",F(V('new')-V('old'),2),"New value minus old value."],["Whole",F(V('whole'),2),"Entered denominator."]];
    bars=[{label:"Part",value:V('part'),display:F(V('part'),2)},{label:"Whole",value:V('whole'),display:F(V('whole'),2)},{label:"Old",value:V('old'),display:F(V('old'),2)},{label:"New",value:V('new'),display:F(V('new'),2)}];
    rows=[["Part / whole",`${F(V('part'),2)} / ${F(V('whole'),2)}`,"Percentage inputs."],["Percentage",`${F(pct,2)}%`,"Part divided by whole."],["Old to new",`${F(V('old'),2)} to ${F(V('new'),2)}`,"Change inputs."],["Percent change",`${F(change,2)}%`,"Relative change."]];
  } else if (engine === "salary_advanced") {
    const p=salaryProjection();
    cards=[["New annual salary",USD(p.annual),"Gross pay after the entered raise."],["Annual raise",USD(p.raiseDollars),`${F(p.raisePercent,2)}% of current salary.`],["Selected pay period",USD(p.perPeriod),`${F(p.periods,0)} pay periods per year.`],["Real raise",`${F(p.realRaise,2)}%`,"After the entered inflation rate."]];
    bars=[{label:"Current annual",value:p.current,display:USD(p.current)},{label:"Annual raise",value:Math.max(0,p.raiseDollars),display:USD(p.raiseDollars)},{label:"New annual",value:p.annual,display:USD(p.annual)}];
    rows=[["Current annual salary",USD(p.current),"Entered gross annual pay."],["Raise",`${USD(p.raiseDollars)} (${F(p.raisePercent,2)}%)`,p.unit==='dollar'?"Converted from annual dollars.":"Converted from the entered percentage."],["New annual salary",USD(p.annual),"Current salary plus raise."],["Monthly pay",USD(p.monthly),"New annual salary divided by 12."],["Selected pay period",USD(p.perPeriod),`New annual salary divided by ${F(p.periods,0)}.`],["Weekly pay",USD(p.weekly),`New annual salary divided by ${F(p.weeks,1)} working weeks.`],["Hourly equivalent",USD(p.hourly),`${F(p.hours,1)} hours/week across ${F(p.weeks,1)} weeks.`],["Inflation-adjusted raise",`${F(p.realRaise,2)}%`,`Nominal ${F(p.raisePercent,2)}% raise versus ${F(p.inflation,2)}% inflation.`]];
  } else if (engine === "discount_advanced" || engine === "discount") {
    const p=engine === "discount_advanced"?discountProjection():{price:V('price'),first:V('discount'),second:0,quantity:1,taxRate:0,fees:0,unitPrice:V('price')*(1-V('discount')/100),effective:V('discount'),subtotal:V('price')*(1-V('discount')/100),savings:V('price')*V('discount')/100,tax:0,total:V('price')*(1-V('discount')/100)};
    cards=[["Checkout total",USD(p.total),"Discounted merchandise, estimated tax, and fees."],["Discounted unit price",USD(p.unitPrice),"Price per item after both discounts."],["Total savings",USD(p.savings),`Savings across ${F(p.quantity,0)} item(s).`],["Effective discount",`${F(p.effective,2)}%`,"Combined discount rate."]];
    bars=[{label:"Merchandise",value:p.subtotal,display:USD(p.subtotal)},{label:"Savings",value:p.savings,display:USD(p.savings)},{label:"Estimated tax",value:p.tax,display:USD(p.tax)},{label:"Fees",value:p.fees,display:USD(p.fees)}];
    rows=[["Original unit price",USD(p.price),"Before discounts."],["First discount",`${F(p.first,2)}%`,"Applied to original price."],["Second discount",`${F(p.second,2)}%`,"Applied to the remaining price."],["Effective discount",`${F(p.effective,2)}%`,"Combined rate, not a simple sum."],["Discounted unit price",USD(p.unitPrice),"After both discounts."],["Quantity",F(p.quantity,0),"Number of items."],["Merchandise subtotal",USD(p.subtotal),"Discounted unit price times quantity."],["Estimated sales tax",USD(p.tax),`${F(p.taxRate,3)}% of discounted merchandise.`],["Shipping and fees",USD(p.fees),"Entered amount."],["Checkout total",USD(p.total),"Subtotal plus estimated tax and fees."]];
  } else if (engine === "cn_triangle") {
    const a=V('a'), b=V('b'), c=Math.sqrt(a*a+b*b), area=a*b/2, perimeter=a+b+c;
    cards=[["Hypotenuse",F(c,4),"Right-triangle side c."],["Area",F(area,4),"a x b / 2."],["Perimeter",F(perimeter,4),"a + b + c."],["Angle A",`${F(Math.atan2(a,b)*180/Math.PI,2)}°`,"Opposite side a."]];
    bars=[{label:"Side a",value:a,display:F(a,2)},{label:"Side b",value:b,display:F(b,2)},{label:"Side c",value:c,display:F(c,2)},{label:"Area",value:area,display:F(area,2)}];
    rows=[["Side a",F(a,4),"Entered leg."],["Side b",F(b,4),"Entered leg."],["Hypotenuse",F(c,4),"Pythagorean theorem."],["Perimeter",F(perimeter,4),"Sum of sides."]];
  } else if (engine === "stats_advanced") {
    const p=statsProjection();
    if(!p.valid){cards=[["Result","Check the data",p.message],["Count",F(p.n||0,0),"Valid numeric values found."],["Variance","Unavailable","Correct the input first."],["Standard deviation","Unavailable","Correct the input first."]];bars=[{label:"Valid values",value:p.n||0,display:F(p.n||0,0)}];rows=[["Validation","Unable to calculate",p.message]]}
    else{
      const typeLabel=p.type==='sample'?'Sample':'Population',intervalLow=p.mean-p.margin,intervalHigh=p.mean+p.margin;
      cards=[[`${typeLabel} standard deviation`,F(p.sd,6),p.type==='sample'?'Uses n - 1.':'Uses n.'],[`${typeLabel} variance`,F(p.variance,6),"Standard deviation squared."],["Mean",F(p.mean,6),`${F(p.sum,6)} divided by ${p.n}.`],["Standard error",F(p.standardError,6),"Selected SD divided by square root of n."]];
      bars=[{label:"Minimum",value:p.min,display:F(p.min,4)},{label:"Mean",value:p.mean,display:F(p.mean,4)},{label:"Median",value:p.median,display:F(p.median,4)},{label:"Maximum",value:p.max,display:F(p.max,4)}];
      rows=[["Data type",typeLabel,p.type==='sample'?"Variance denominator is n - 1.":"Variance denominator is n."],["Count (n)",F(p.n,0),"Number of observations."],["Sum",F(p.sum,8),"Total of all values."],["Mean",F(p.mean,8),"Sum divided by count."],["Median",F(p.median,8),"Middle value after sorting."],["Minimum",F(p.min,8),"Smallest value."],["Maximum",F(p.max,8),"Largest value."],["Range",F(p.range,8),"Maximum minus minimum."],["Sum of squared deviations",F(p.sumSquares,8),"Sum of (x - mean)^2."],["Population variance",F(p.populationVariance,8),"Squared deviations divided by n."],["Population standard deviation",F(p.populationSd,8),"Square root of population variance."],["Sample variance",p.sampleVariance===null?"Requires n > 1":F(p.sampleVariance,8),"Squared deviations divided by n - 1."],["Sample standard deviation",p.sampleSd===null?"Requires n > 1":F(p.sampleSd,8),"Square root of sample variance."],["Standard error",F(p.standardError,8),"Selected standard deviation divided by square root of n."],[`${p.confidence} normal margin of error`,F(p.margin,8),`${F(p.z,3)} x standard error.`],[`${p.confidence} normal interval`,`${F(intervalLow,6)} to ${F(intervalHigh,6)}`,"Mean plus or minus the normal-approximation margin."],["Coefficient of variation",p.coefficient===null?"Undefined when mean is zero":`${F(p.coefficient,6)}%`,"Selected standard deviation divided by absolute mean."]];
      if(p.n<=20)p.squared.forEach((item,index)=>rows.push([`Value ${index+1}: squared deviation`,F(item.square,8),`(${F(item.value,6)} - ${F(p.mean,6)})^2`]));
    }
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
  } else if (engine === "bottleneck") {
    const cpu=V('cpu_score'), gpu=V('gpu_score'), res=V('resolution'), refresh=Math.max(30,V('refresh')), work=document.getElementById('workload')?.value||'gaming', resLoad=res>=2160?1.35:res>=1440?1.12:0.9, refreshLoad=Math.min(1.6,Math.max(.75,refresh/144)), workCpu=work==='streaming'?1.18:work==='productivity'?0.92:1, workGpu=work==='productivity'?0.9:1, cpuCap=cpu/(refreshLoad*workCpu), gpuNeed=gpu*resLoad*workGpu, ratio=cpuCap/Math.max(1,gpuNeed), pct=Math.min(99,Math.abs(1-ratio)*100), type=ratio<0.92?'CPU bottleneck':ratio>1.12?'GPU bottleneck':'Balanced';
    cards=[["Likely result",type,"Estimated limiting side."],["Bottleneck index",`${F(pct,1)}%`,"Distance from balanced score."],["CPU headroom",F(cpuCap,0),"Adjusted CPU capacity."],["GPU demand",F(gpuNeed,0),"Adjusted GPU load."]];
    bars=[{label:"CPU headroom",value:cpuCap,display:F(cpuCap,0)},{label:"GPU demand",value:gpuNeed,display:F(gpuNeed,0)},{label:"Bottleneck",value:pct,display:`${F(pct,1)}%`}];
    rows=[["CPU score",F(cpu,0),"Entered benchmark score."],["GPU score",F(gpu,0),"Entered benchmark score."],["Resolution",`${F(res,0)}p`,"Higher resolution shifts load toward GPU."],["Refresh target",`${F(refresh,0)} Hz`,"Higher refresh increases CPU demand."],["Workload",work,"Selected usage model."]];
  } else if (engine === "gpu_compute") {
    const cores=V('cores'), clock=V('clock')/1000, ops=V('ops'), mem=V('memory_clock'), bus=V('bus'), power=Math.max(1,V('power')), tflops=cores*clock*ops/1000, bandwidth=mem*bus/8, eff=tflops/power;
    cards=[["FP32 compute",`${F(tflops,2)} TFLOPS`,"Theoretical peak estimate."],["Bandwidth",`${F(bandwidth,0)} GB/s`,"Memory throughput estimate."],["Efficiency",`${F(eff,3)} TFLOPS/W`,"Compute divided by board power."],["Boost clock",`${F(clock,2)} GHz`,"Entered boost frequency."]];
    bars=[{label:"TFLOPS",value:tflops,display:F(tflops,2)},{label:"Bandwidth",value:bandwidth,display:`${F(bandwidth,0)} GB/s`},{label:"Power",value:power,display:`${F(power,0)} W`}];
    rows=[["GPU cores",F(cores,0),"Shader/CUDA-style units."],["Boost clock",`${F(clock,3)} GHz`,"Clock in GHz."],["Operations/cycle",F(ops,0),"Selected math model."],["Memory bus",`${F(bus,0)} bit`,"Entered bus width."],["Board power",`${F(power,0)} W`,"Used for efficiency."]];
  } else if (engine === "ai_compute") {
    const params=V('params_b')*1e9, tokens=V('tokens_b')*1e9, gpus=Math.max(1,V('gpu_count')), tflops=V('gpu_tflops'), util=Math.max(1,V('utilization'))/100, power=V('power_kw'), flops=6*params*tokens, effective=gpus*tflops*1e12*util, hours=flops/effective/3600, days=hours/24, petaDays=flops/1e15/86400, gpuHours=hours*gpus, energy=power*hours;
    cards=[["Training compute",`${F(petaDays,2)} PFLOP-days`,"Approximate total training work."],["Training time",`${F(days,2)} days`,"Wall-clock time at entered throughput."],["GPU hours",F(gpuHours,0),"GPU count times wall-clock hours."],["Energy use",`${F(energy,0)} kWh`,"Cluster power times hours."]];
    bars=[{label:"PFLOP-days",value:petaDays,display:F(petaDays,2)},{label:"GPU hours",value:gpuHours,display:F(gpuHours,0)},{label:"Energy kWh",value:energy,display:F(energy,0)}];
    rows=[["Model size",`${F(params/1e9,2)}B parameters`,"Entered parameter count."],["Training tokens",`${F(tokens/1e9,2)}B tokens`,"Entered token count."],["Total FLOPs",`${F(flops/1e21,2)}e21`,"6 x parameters x tokens."],["Effective throughput",`${F(effective/1e15,2)} PFLOPS`,"GPU count x TFLOPS x utilization."],["GPU count",F(gpus,0),"Accelerators used."],["Utilization",`${F(util*100,1)}%`,"Effective hardware utilization."]];
  } else if (engine === "ai_cost") {
    const req=V('requests'), input=V('input_tokens'), output=V('output_tokens'), inPrice=V('input_price'), outPrice=V('output_price'), days=V('days'), inputCost=req*days*input/1000000*inPrice, outputCost=req*days*output/1000000*outPrice, total=inputCost+outputCost, daily=total/Math.max(1,days);
    cards=[["Billing-period cost",USD(total),"Input plus output token cost."],["Daily cost",USD(daily),"Average cost per day."],["Input token cost",USD(inputCost),"Prompt/context portion."],["Output token cost",USD(outputCost),"Generated response portion."]];
    bars=[{label:"Input cost",value:inputCost,display:USD(inputCost)},{label:"Output cost",value:outputCost,display:USD(outputCost)},{label:"Daily cost",value:daily,display:USD(daily)}];
    rows=[["Requests",`${F(req,0)} / day`,"Estimated daily API calls."],["Input tokens",F(input,0),"Average prompt/context tokens."],["Output tokens",F(output,0),"Average generated tokens."],["Input price",USD(inPrice),"Per 1M input tokens."],["Output price",USD(outPrice),"Per 1M output tokens."],["Billing days",F(days,0),"Days included."]];
  } else if (engine === "mining_profit") {
    const rev=V('revenue'), power=V('power'), elec=V('electricity'), fee=V('pool_fee')/100, hardware=V('hardware'), uptime=V('uptime')/100, gross=rev*uptime, energy=power/1000*24*elec*uptime, fees=gross*fee, profit=gross-energy-fees, monthly=profit*30, payback=profit>0?hardware/profit:Infinity;
    cards=[["Daily profit",USD(profit),"Revenue minus power and fees."],["Monthly profit",USD(monthly),"Daily profit times 30."],["Electricity/day",USD(energy),"Power draw times kWh rate."],["Payback",Number.isFinite(payback)?`${F(payback,0)} days`:"Not profitable","Hardware cost divided by profit."]];
    bars=[{label:"Gross revenue",value:gross,display:USD(gross)},{label:"Electricity",value:energy,display:USD(energy)},{label:"Pool fees",value:fees,display:USD(fees)},{label:"Profit",value:profit,display:USD(profit)}];
    rows=[["Revenue",USD(rev),"Estimated daily mining revenue before uptime."],["Power draw",`${F(power,0)} W`,"Miner load."],["Electricity rate",USD(elec),"Cost per kWh."],["Pool fee",`${F(fee*100,2)}%`,"Deducted from gross revenue."],["Uptime",`${F(uptime*100,1)}%`,"Operational time assumption."],["Hardware cost",USD(hardware),"Used for payback."]];
  } else if (engine === "power_supply") {
    const cpu=V('cpu_watts'), gpu=V('gpu_watts'), drives=V('drives'), fans=V('fans'), other=V('other'), base=cpu+gpu+drives+fans+other, recommended=base*(1+V('headroom')/100), standard=[450,500,550,600,650,700,750,850,1000,1200,1300,1500,1600], psu=standard.find(x=>x>=recommended)||Math.ceil(recommended/100)*100;
    cards=[["Recommended PSU",`${F(psu,0)} W`,"Next common PSU size."],["Estimated load",`${F(base,0)} W`,"Component wattage total."],["With headroom",`${F(recommended,0)} W`,"Load plus safety margin."],["Headroom",`${F(V('headroom'),0)}%`,"Entered planning margin."]];
    bars=[{label:"CPU",value:cpu,display:`${F(cpu,0)} W`},{label:"GPU",value:gpu,display:`${F(gpu,0)} W`},{label:"Storage",value:drives,display:`${F(drives,0)} W`},{label:"Cooling",value:fans,display:`${F(fans,0)} W`},{label:"Other",value:other,display:`${F(other,0)} W`}];
    rows=[["CPU",`${F(cpu,0)} W`,"Entered CPU power."],["GPU",`${F(gpu,0)} W`,"Entered GPU power."],["Drives/storage",`${F(drives,0)} W`,"Storage estimate."],["Fans/cooling/RGB",`${F(fans,0)} W`,"Cooling and lighting load."],["Other devices",`${F(other,0)} W`,"Additional system load."],["Recommended PSU",`${F(psu,0)} W`,"Rounded to a common size."]];
  } else if (engine === "ratio_advanced") {
    const p=ratioProjection(),names=['Part A','Part B','Part C'];
    if(!p.valid){cards=[["Ratio result","Check inputs",p.message],["Simplest form","Unavailable","Enter valid positive ratio terms."],["Parts","Unavailable","Parts A and B are required."],["Verification","Unavailable","Correct the highlighted calculation inputs."]];bars=[];rows=[["Validation","Unable to calculate",p.message]]}
    else if(p.mode==='proportion'){cards=[[`Missing ${p.label}`,F(p.solved,8),"Solved by equal cross products."],["Left ratio",`${F(p.values[0],8)} : ${F(p.values[1],8)}`,`Quotient ${F(p.values[0]/p.values[1],8)}.`],["Right ratio",`${F(p.values[2],8)} : ${F(p.values[3],8)}`,`Quotient ${F(p.values[2]/p.values[3],8)}.`],["Cross-product check",F(p.leftProduct,8),"Both cross products match."]];bars=p.values.map((value,index)=>({label:['A','B','C','D'][index],value,display:F(value,8)}));rows=[["Proportion",p.equation,"The two ratios are equal."],["Missing term",p.label,`Solved value ${F(p.solved,10)}.`],["Left quotient",F(p.values[0]/p.values[1],10),"A divided by B."],["Right quotient",F(p.values[2]/p.values[3],10),"C divided by D."],["A x D",F(p.leftProduct,10),"First cross product."],["B x C",F(p.rightProduct,10),"Second cross product."],["Check","Equal cross products","The solved proportion is internally consistent."]]}
    else if(p.mode==='split'){cards=p.shares.map((value,index)=>[names[index],F(value,8),`${F(p.values[index]/p.sum*100,4)}% of the total.`]);while(cards.length<3)cards.push([names[cards.length],"Not used","Enter an optional third ratio term."]);cards.push(["Allocated total",F(p.check,8),`Matches entered total ${F(p.total,8)}.`]);bars=p.shares.map((value,index)=>({label:names[index],value,display:F(value,8)}));rows=[["Entered ratio",ratioText(p.values),"Original positive terms."],["Simplest ratio",ratioText(p.terms),`Divide whole-number terms by ${F(p.divisor,0)}.`],["Total ratio weight",F(p.sum,8),"Sum of entered ratio values."],["One weighted unit",F(p.total/p.sum,10),"Total divided by ratio weight."],...p.shares.map((value,index)=>[names[index],F(value,10),`${F(p.total,8)} x ${F(p.values[index],8)} / ${F(p.sum,8)}.`]),["Allocation check",F(p.check,10),"Unrounded shares add to the entered total."]]}
    else if(p.mode==='scale'){cards=[["Scaled ratio",ratioText(p.scaled),"Every term uses the same factor."],["Scale factor",F(p.factor,8),"Multiplier applied to each term."],["Simplest form",ratioText(p.terms),"Equivalent lowest whole-number terms."],["Scaled total",F(p.scaled.reduce((a,b)=>a+b,0),8),"Sum of scaled terms."]];bars=p.scaled.map((value,index)=>({label:names[index],value,display:F(value,8)}));rows=[["Original ratio",ratioText(p.values),"Values before scaling."],["Scale factor",F(p.factor,10),"Applied equally to every term."],["Scaled ratio",ratioText(p.scaled),"Original terms multiplied by the factor."],["Simplest ratio",ratioText(p.terms),"Scaling preserves this relationship."],["Equivalence check",F(p.scaled[0]/p.scaled[1],10),`Matches original A/B, ${F(p.values[0]/p.values[1],10)}.`]]}
    else{const shares=p.values.map(value=>value/p.sum*100);cards=[["Simplified ratio",ratioText(p.terms),"Lowest whole-number terms."],["Original ratio",ratioText(p.values),"Parsed input values."],["Total parts",F(p.termSum,0),"Sum of simplified terms."],["Part A share",`${F(shares[0],4)}%`,"A divided by the combined total."]];bars=p.terms.map((value,index)=>({label:names[index],value,display:F(value,8)}));rows=[["Original ratio",ratioText(p.values),"Entered values after parsing."],["Common-denominator terms",ratioText(p.integers),p.common===1?"Inputs were already whole numbers.":`Fractions cleared with denominator ${F(p.common,0)}.`],["Greatest common divisor",F(p.divisor,0),"Divide every whole-number term by this value."],["Simplified ratio",ratioText(p.terms),"Lowest whole-number form."],["Total simplified parts",F(p.termSum,0),"Sum of the reduced terms."],["A per B",F(p.values[0]/p.values[1],10),"Part-to-part unit comparison."],["B per A",F(p.values[1]/p.values[0],10),"Reverse part-to-part comparison."],...shares.map((value,index)=>[`${names[index]} share`,`${F(value,6)}%`,`${names[index]} divided by all entered parts.`])]}
  } else if (engine === "bottleneck_advanced") {
    const p=bottleneckProjection();
    if(!p.valid){cards=[["Analysis","Check inputs",p.message],["CPU evidence","Unavailable","Enter valid source measurements."],["GPU evidence","Unavailable","Enter valid source measurements."],["Target comparison","Unavailable","Enter a positive target FPS."]];bars=[];rows=[["Validation","Unable to analyze",p.message]]}
    else if(p.mode==='planning'){const targetStatus=p.targetGap>0?`${F(p.targetGap,1)} FPS below target`:`${F(Math.abs(p.targetGap),1)} FPS at or above target`;cards=[["Likely limit",p.verdict,p.limiting],["Estimated ceiling",`${F(p.estimate,1)} FPS`,"Lower of the two benchmark ceilings."],["Uncertainty range",`${F(p.low,1)}-${F(p.high,1)} FPS`,`${F(p.uncertainty*100,1)}% entered range.`],["Target comparison",targetStatus,`${F(p.target,1)} FPS target.`]];bars=[{label:"CPU benchmark ceiling",value:p.cpuCap,display:`${F(p.cpuCap,1)} FPS`},{label:"GPU benchmark ceiling",value:p.gpuCap,display:`${F(p.gpuCap,1)} FPS`},{label:"Target",value:p.target,display:`${F(p.target,1)} FPS`}];rows=[["Analysis mode","Benchmark planning","Use matched game, scene, settings, and software versions."],["CPU-limited benchmark",`${F(p.cpuCap,2)} FPS`,"Measured with GPU limitation minimized."],["GPU-limited benchmark",`${F(p.gpuCap,2)} FPS`,"Measured at the intended resolution and settings."],["Likely limiting side",p.verdict,p.limiting],["Estimated FPS ceiling",`${F(p.estimate,2)} FPS`,"Minimum of CPU and GPU benchmark ceilings."],["Entered uncertainty",`${F(p.uncertainty*100,2)}%`,"Applied around the lower benchmark result."],["Estimated range",`${F(p.low,2)}-${F(p.high,2)} FPS`,"Planning range, not a guaranteed result."],["Target FPS",`${F(p.target,2)} FPS`,targetStatus],["Important limitation","Not a universal bottleneck percentage","Results apply only to the matched benchmark conditions."]]}
    else{const targetStatus=p.targetGap>0?`${F(p.targetGap,1)} FPS below target`:`${F(Math.abs(p.targetGap),1)} FPS at or above target`;cards=[["Likely limit",p.verdict,p.reason],["Measured performance",`${F(p.fps,1)} FPS`,targetStatus],["Frame-time ceiling",`${F(p.frameCeiling,1)} FPS`,"Derived from the slower entered frame time."],["Target frame budget",`${F(p.targetBudget,2)} ms`,`${F(p.target,1)} FPS target.`]];bars=[{label:"CPU frame time",value:p.cpuMs,display:`${F(p.cpuMs,2)} ms`},{label:"GPU frame time",value:p.gpuMs,display:`${F(p.gpuMs,2)} ms`},{label:"Target frame budget",value:p.targetBudget,display:`${F(p.targetBudget,2)} ms`}];rows=[["Analysis mode","Measured in-game data","Applies to the tested workload and scene."],["Likely limiting side",p.verdict,p.reason],["Measured average FPS",`${F(p.fps,2)} FPS`,targetStatus],["Target FPS",`${F(p.target,2)} FPS`,`${F(p.targetBudget,3)} ms frame-time budget.`],["Busiest CPU thread",`${F(p.cpuUsage,1)}%`,"Per-thread evidence is more useful than total CPU utilization."],["Average GPU utilization",`${F(p.gpuUsage,1)}%`,"Near-full use supports a GPU-bound diagnosis when uncapped."],["CPU frame time",`${F(p.cpuMs,3)} ms`,`${F(1000/p.cpuMs,1)} FPS mathematical ceiling.`],["GPU frame time",`${F(p.gpuMs,3)} ms`,`${F(1000/p.gpuMs,1)} FPS mathematical ceiling.`],["Slower-side ceiling",`${F(p.frameCeiling,2)} FPS`,"1000 divided by the longer entered frame time."],["Verification","Repeat the same scene","Remove FPS caps and check temperatures, clocks, RAM, VRAM, and background tasks."]]}
  } else if (engine === "car_depreciation_advanced") {
    const p=carDepreciationProjection(),schedule=document.querySelector('#carDepSchedule tbody'),method=p.method==='two_stage'?'First year plus later years':'Constant annual rate';
    cards=[["Projected value",USD(p.value),`${F(p.retained,1)}% of starting value retained.`],["Total depreciation",USD(p.totalLoss),`${F(100-p.retained,1)}% value lost.`],["Average per year",USD(p.averageAnnual),`${F(p.years,0)}-year projection.`],["Depreciation per mile",USD(p.costPerMile),`${F(p.totalMiles,0)} projected miles.`]];
    bars=[{label:"Starting value",value:p.start,display:USD(p.start)},{label:"Ending value",value:p.value,display:USD(p.value)},{label:"Total depreciation",value:p.totalLoss,display:USD(p.totalLoss)}];
    rows=[["Method",method,p.method==='two_stage'?`${F(p.firstRate*100,2)}% first year; ${F(p.laterRate*100,2)}% later.`:`${F(p.uniformRate*100,2)}% each year.`],["Starting vehicle value",USD(p.start),"Entered market-value baseline."],["Projection period",`${F(p.years,0)} years`,`${F(p.milesYear,0)} miles per year entered.`],["Minimum value floor",USD(p.floor),"Projection does not fall below this amount."],["Projected ending value",USD(p.value),`${F(p.retained,2)}% retained value.`],["Total depreciation",USD(p.totalLoss),`${F(100-p.retained,2)}% of starting value.`],["Average annual depreciation",USD(p.averageAnnual),"Total loss divided by years."],["Projected mileage",`${F(p.totalMiles,0)} miles`,"Mileage does not independently change value."],["Depreciation per mile",USD(p.costPerMile),"Total loss divided by projected miles."]];
    if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${x.year}</td><td>${USD(x.opening)}</td><td>${F(x.rate*100,2)}%</td><td>${USD(x.loss)}</td><td>${USD(x.ending)}</td></tr>`).join('');
  } else if (engine === "car_resale_advanced") {
    const p=carResaleProjection(),schedule=document.querySelector('#resaleSchedule tbody'),scenarios=document.querySelector('#resaleScenarios tbody'),equityLabel=p.base.net>=0?"Estimated net proceeds":"Estimated negative equity";
    cards=[["Projected resale value",USD(p.base.value),`${F(p.rate*100,2)}% annual depreciation.`],[equityLabel,USD(Math.abs(p.base.net)),"After selling costs and payoff."],["Total depreciation",USD(p.base.totalLoss),`${F(p.years,0)}-year value loss.`],["Depreciation per mile",USD(p.costPerMile),`${F(p.totalMiles,0)} projected miles.`]];
    bars=[{label:"Current value",value:p.start,display:USD(p.start)},{label:"Future resale value",value:p.base.value,display:USD(p.base.value)},{label:"Total depreciation",value:p.base.totalLoss,display:USD(p.base.totalLoss)},{label:"Net proceeds",value:Math.max(0,p.base.net),display:USD(p.base.net)}];
    rows=[["Current private-party value",USD(p.start),"Entered market-value baseline."],["Years until sale",F(p.years,0),`${F(p.milesYear,0)} miles per year entered.`],["Entered annual depreciation",`${F(p.rate*100,2)}%`,"Applied to remaining value each year."],["Projected resale value",USD(p.base.value),"Before selling costs and loan payoff."],["Modeled selling costs",USD(p.base.sellingCosts),`${F(p.costRate*100,2)}% of projected value.`],["Future loan payoff",USD(p.payoff),"Entered expected payoff at sale."],[equityLabel,USD(Math.abs(p.base.net)),"Resale value less costs and payoff."],["Projected mileage",`${F(p.totalMiles,0)} miles`,"Mileage does not independently change value."],["Depreciation per mile",USD(p.costPerMile),"Total value loss divided by projected miles."]];
    if(scenarios)scenarios.innerHTML=[["Slower depreciation",p.slower],["Entered rate",p.base],["Faster depreciation",p.faster]].map(([label,x])=>`<tr><td>${label}</td><td>${F(x.rate*100,2)}%</td><td>${USD(x.value)}</td><td>${USD(x.net)}</td></tr>`).join('');
    if(schedule)schedule.innerHTML=p.schedule.map(x=>`<tr><td>${x.year}</td><td>${USD(x.opening)}</td><td>${USD(x.loss)}</td><td>${USD(x.ending)}</td></tr>`).join('');
  } else if (engine === "horsepower_advanced") {
    const p=horsepowerProjection();
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Horsepower","Unavailable","Positive source values are required."],["Torque","Unavailable","Positive source values are required."],["RPM","Unavailable","Positive source values are required."]];bars=[];rows=[["Validation","Unable to calculate",p.message]]}
    else{const modeLabel=p.mode==='power'?"Solve horsepower":p.mode==='torque'?"Solve torque":"Solve RPM";cards=[["Mechanical horsepower",`${F(p.hp,2)} hp`,`${F(p.kw,2)} kW.`],["Torque",`${F(p.torqueLb,2)} lb-ft`,`${F(p.torqueNm,2)} N-m.`],["Engine speed",`${F(p.rpm,0)} RPM`,"Selected operating point."],["Metric horsepower",`${F(p.ps,2)} PS`,"Approximately 735.5 watts per PS."]];bars=[{label:"Mechanical hp",value:p.hp,display:`${F(p.hp,2)} hp`},{label:"Kilowatts",value:p.kw,display:`${F(p.kw,2)} kW`},{label:"Metric PS",value:p.ps,display:`${F(p.ps,2)} PS`}];rows=[["Calculation mode",modeLabel,"The selected value is solved from the other two."],["Mechanical horsepower",`${F(p.hp,6)} hp`,"Torque times RPM divided by 5252.113."],["Power in kilowatts",`${F(p.kw,6)} kW`,"Mechanical horsepower times 0.7456998716."],["Metric horsepower",`${F(p.ps,6)} PS`,"Kilowatts divided by 0.73549875."],["Torque",`${F(p.torqueLb,6)} lb-ft`,`${F(p.torqueNm,6)} N-m.`],["Engine speed",`${F(p.rpm,3)} RPM`,"Revolutions per minute."],["Conversion constant",F(p.constant,6),"33,000 divided by 2 pi."],["Operating-point note","Use matching values","Torque and RPM must refer to the same shaft operating point."]]}
  } else if (engine === "power_weight_advanced") {
    const p=powerWeightProjection();
    if(!p.valid){cards=[["Result","Check inputs",p.message],["Power","Unavailable","Enter positive power."],["Loaded weight","Unavailable","Enter positive weight."],["Target","Unavailable","No target comparison calculated."]];bars=[];rows=[["Validation","Unable to calculate",p.message]]}
    else{const gapLabel=p.powerGap>=0?"Additional power for target":"Power above target";cards=[["Power-to-weight",`${F(p.hpPerLb,5)} hp/lb`,`${F(p.hpPerUsTon,2)} hp per US ton.`],["Weight per horsepower",`${F(p.lbPerHp,2)} lb/hp`,"Lower means less mass per horsepower."],["Metric ratio",`${F(p.wPerKg,2)} W/kg`,`${F(p.hpPerTonne,2)} hp per metric tonne.`],["Target power",`${F(p.targetHp,2)} hp`,`${F(Math.abs(p.powerGap),2)} hp ${p.powerGap>=0?'needed':'above target'}.`]];bars=[{label:"Current power",value:p.hp,display:`${F(p.hp,2)} hp`},{label:"Target power",value:p.targetHp,display:`${F(p.targetHp,2)} hp`},{label:gapLabel,value:Math.abs(p.powerGap),display:`${F(Math.abs(p.powerGap),2)} hp`}];rows=[["Converted power",`${F(p.hp,6)} hp`,`${F(p.kw,6)} kW.`],["Base weight",`${F(p.weightLb,3)} lb`,"Converted from the selected weight unit."],["Added load",`${F(p.loadLb,3)} lb`,"Driver, passengers, cargo, or equipment."],["Loaded weight",`${F(p.totalLb,3)} lb`,`${F(p.totalKg,3)} kg.`],["Horsepower per pound",`${F(p.hpPerLb,8)} hp/lb`,"Power divided by loaded weight."],["Pounds per horsepower",`${F(p.lbPerHp,6)} lb/hp`,"Loaded weight divided by power."],["Horsepower per US ton",`${F(p.hpPerUsTon,4)} hp/ton`,"One US short ton equals 2,000 lb."],["Horsepower per metric tonne",`${F(p.hpPerTonne,4)} hp/tonne`,"One metric tonne equals 1,000 kg."],["Watts per kilogram",`${F(p.wPerKg,4)} W/kg`,"Numerically equal to kW per metric tonne."],["Target ratio",`${F(p.target,6)} hp/lb`,`${F(p.targetHp,3)} hp required at the loaded weight.`],[gapLabel,`${F(Math.abs(p.powerGap),3)} hp`,"Target power minus current power."]]}
  } else if (engine === "trade_in_estimate") {
    const p=tradeInProjection(), equityLabel=p.equity>=0?"Positive equity":"Negative equity";
    cards=[["Trade-in estimate",USD(p.trade),"Comparable less entered dealer costs."],[equityLabel,USD(Math.abs(p.equity)),"Trade estimate minus loan payoff."],["Entered tax benefit",USD(p.taxSavings),"Varies by jurisdiction and transaction."],["Effective trade value",USD(p.effective),"Trade estimate plus entered tax benefit."]];
    bars=[{label:"Trade-in value",value:p.trade,display:USD(p.trade)},{label:"Loan payoff",value:p.payoff,display:USD(p.payoff)},{label:"Tax benefit",value:p.taxSavings,display:USD(p.taxSavings)},{label:"Dealer costs",value:p.margin+p.reconditioning,display:USD(p.margin+p.reconditioning)}];
    rows=[["Comparable retail listing",USD(p.comparable),"Current local asking-price benchmark."],["Condition/mileage adjustment",USD(p.adjustment),"Positive or negative difference."],["Dealer resale margin",USD(p.margin),"Entered planning allowance."],["Repair and cleanup",USD(p.reconditioning),"Expected reconditioning."],["Estimated trade-in",USD(p.trade),"Planning estimate, not an offer."],["Loan payoff",USD(p.payoff),"Entered lender payoff."],["Loan equity",USD(p.equity),p.equity>=0?"Value above payoff.":"Payoff above value."],["Entered sales-tax benefit",USD(p.taxSavings),"Confirm local rules."]];
  } else if (engine === "used_car_estimate") {
    const p=usedCarProjection(), range=(value)=>`${USD(value*.96)} - ${USD(value*1.04)}`;
    cards=[["Private-party estimate",USD(p.privateValue),"Midpoint for an as-is private sale."],["Trade-in estimate",USD(p.trade),"Midpoint after entered dealer spread."],["Adjusted retail",USD(p.retail),"Comparable retail after adjustments."],["Pricing spread",`${F(p.spread,1)}%`,"Entered retail-to-trade difference."]];
    bars=[{label:"Dealer retail",value:p.retail,display:USD(p.retail)},{label:"Private party",value:p.privateValue,display:USD(p.privateValue)},{label:"Trade-in",value:p.trade,display:USD(p.trade)}];
    rows=[["Local retail benchmark",USD(p.benchmark),"Comparable asking price."],["Condition adjustment",`${F(p.condition,1)}%`,"Selected condition factor."],["Mileage adjustment",USD(p.mileage),"Entered dollar adjustment."],["Options/history adjustment",USD(p.options),"Entered dollar adjustment."],["Regional adjustment",`${F(p.regional,1)}%`,"Local demand assumption."],["Adjusted retail range",range(p.retail),"Midpoint plus or minus 4%."],["Private-party range",range(p.privateValue),"Planning range."],["Trade-in range",range(p.trade),"Planning range, not an offer."]];
  } else if (engine === "concrete_advanced") {
    const p=concreteProjection(), shapeLabel=p.shape==='slab'?"Slab or footing":p.shape==='column'?"Round column":"Round post holes", bagLabel=document.getElementById('concrete_bag_size')?.selectedOptions[0]?.textContent||"Selected bag";
    cards=[["Concrete needed",`${F(p.yards,2)} yd³`,"Includes entered waste."],["Volume",`${F(p.withWaste,2)} ft³`,"Final ordering volume."],["Bag count",F(p.bags,0),bagLabel],["Estimated bag cost",USD(p.bagCost),"Price per bag times count."]];
    bars=[{label:"Volume before waste",value:p.baseFt3,display:`${F(p.baseFt3,2)} ft³`},{label:"Volume with waste",value:p.withWaste,display:`${F(p.withWaste,2)} ft³`},{label:"Bag cost",value:p.bagCost,display:USD(p.bagCost)},{label:"Ready-mix material",value:p.readyCost,display:USD(p.readyCost)}];
    rows=[["Project shape",shapeLabel,"Selected geometry."],["Volume before waste",`${F(p.baseFt3,3)} ft³`,"Calculated dimensions."],["Waste allowance",`${F(p.waste,1)}%`,"Entered planning margin."],["Ordering volume",`${F(p.withWaste,3)} ft³`,`${F(p.yards,3)} cubic yards.`],["Selected bag yield",`${F(p.yieldPerBag,3)} ft³`,"Approximate yield per bag."],["Bags required",F(p.bags,0),"Rounded up to a whole bag."],["Estimated bag cost",USD(p.bagCost),"Excludes tax and labor."],["Estimated ready-mix material",USD(p.readyCost),"Excludes delivery and fees."]];
  } else if (engine === "roof_pitch_advanced") {
    const p=roofPitchProjection();
    cards=[["Roof pitch",`${F(p.pitch,2)}:12`,"Rise per 12 inches of run."],["Roof angle",`${F(p.angle,2)}°`,"Angle from horizontal."],["Pitch multiplier",F(p.factor,4),"Sloped length per horizontal foot."],["Rafter length",`${F(p.rafter,2)} ft`,"Run plus horizontal overhang."]];
    bars=[{label:"Horizontal run",value:p.run,display:`${F(p.run,2)} ft`},{label:"Roof rise",value:p.rise,display:`${F(p.rise,2)} ft`},{label:"Rafter length",value:p.rafter,display:`${F(p.rafter,2)} ft`},{label:"Roofing squares",value:p.squares,display:F(p.squares,2)}];
    rows=[["Pitch",`${F(p.pitch,3)}:12`,"Normalized rise per 12."],["Percent slope",`${F(p.percent,3)}%`,"Rise divided by run."],["Angle",`${F(p.angle,3)}°`,"Angle from horizontal."],["Pitch multiplier",F(p.factor,5),"Square root of 1 plus slope squared."],["Horizontal rafter run",`${F(p.run,3)} ft`,"Entered plan distance."],["Roof rise",`${F(p.rise,3)} ft`,"Run times slope."],["Rafter with overhang",`${F(p.rafter,3)} ft`,"Geometry estimate before cuts."],["Sloped roof area",`${F(p.slopedArea,1)} ft²`,"Horizontal plan area times multiplier."],["Roofing squares",F(p.squares,2),"One square equals 100 square feet."]];
  } else if (engine === "rafter_advanced") {
    const p=rafterProjection();
    cards=[["Rafter length",`${F(p.totalLength,2)} ft`,"Includes horizontal overhang."],["Roof rise",`${F(p.rise,2)} ft`,"Over entered horizontal run."],["Slope factor",F(p.factor,4),"Length per horizontal foot."],["Total linear feet",`${F(p.totalLinear,1)} ft`,`${F(p.quantity,0)} rafters before waste.`]];
    bars=[{label:"Wall-to-ridge length",value:p.baseLength,display:`${F(p.baseLength,2)} ft`},{label:"Sloped tail",value:p.tailLength,display:`${F(p.tailLength,2)} ft`},{label:"Roof rise",value:p.rise,display:`${F(p.rise,2)} ft`},{label:"Total per rafter",value:p.totalLength,display:`${F(p.totalLength,2)} ft`}];
    rows=[["Roof pitch",`${F(p.pitch,2)}:12`,"Entered rise per 12."],["Pitch angle",`${F(p.angle,3)}°`,"Angle from horizontal."],["Slope factor",F(p.factor,5),"Sloped length multiplier."],["Horizontal run",`${F(p.run,3)} ft`,"Wall support to ridge."],["Roof rise",`${F(p.rise,3)} ft`,"Run times pitch ratio."],["Base rafter length",`${F(p.baseLength,3)} ft`,"Before overhang."],["Sloped overhang length",`${F(p.tailLength,3)} ft`,"From horizontal overhang."],["Total rafter length",`${F(p.totalLength,3)} ft`,"Before cut adjustments."],["Total linear footage",`${F(p.totalLinear,2)} ft`,"Length times rafter count."]];
  } else if (engine === "square_footage_advanced") {
    const p=squareFootageProjection(), shape={rectangle:"Rectangle",circle:"Circle",triangle:"Triangle",room_walls:"Four room walls"}[p.shape]||p.shape;
    cards=[["Net area",`${F(p.area,2)} ft²`,shape],["Order area",`${F(p.orderArea,2)} ft²`,`${F(p.overage,1)}% overage included.`],["Perimeter",p.perimeter===null?"n/a":`${F(p.perimeter,2)} ft`,"Boundary length when determined."],["Material cost",USD(p.cost),`${USD(p.price)} per square foot.`]];
    bars=[{label:"Measured area",value:p.area,display:`${F(p.area,2)} ft²`},{label:"Overage amount",value:p.orderArea-p.area,display:`${F(p.orderArea-p.area,2)} ft²`},{label:"Order area",value:p.orderArea,display:`${F(p.orderArea,2)} ft²`},{label:"Estimated cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Area type",shape,"Selected geometry."],["Measured or net area",`${F(p.area,3)} ft²`,p.shape==='room_walls'?"Gross walls minus openings.":"Calculated geometry."],["Gross wall area",p.shape==='room_walls'?`${F(p.gross,3)} ft²`:"n/a","Available in wall mode."],["Openings deducted",p.shape==='room_walls'?`${F(p.openings,3)} ft²`:"n/a","Doors and windows."],["Perimeter",p.perimeter===null?"n/a":`${F(p.perimeter,3)} ft`,"Triangle sides are not inferred."],["Overage",`${F(p.overage,2)}%`,"Entered planning allowance."],["Order area",`${F(p.orderArea,3)} ft²`,"Area after overage."],["Estimated cost",USD(p.cost),"Area times entered unit price."]];
  } else if (engine === "flooring_advanced") {
    const p=flooringProjection();
    cards=[["Boxes to buy",F(p.boxes,0),"Rounded up to complete boxes."],["Order target",`${F(p.target,1)} ft²`,`${F(p.waste,1)}% waste included.`],["Purchased coverage",`${F(p.purchased,1)} ft²`,"Box count times coverage."],["Estimated total",USD(p.totalCost),"Flooring plus entered underlayment."]];
    bars=[{label:"Measured floor",value:p.area,display:`${F(p.area,1)} ft²`},{label:"Waste allowance",value:p.target-p.area,display:`${F(p.target-p.area,1)} ft²`},{label:"Purchased coverage",value:p.purchased,display:`${F(p.purchased,1)} ft²`},{label:"Flooring cost",value:p.boxCost,display:USD(p.boxCost)},{label:"Underlayment cost",value:p.underlayCost,display:USD(p.underlayCost)}];
    rows=[["Measured floor area",`${F(p.area,2)} ft²`,"Room plus extra area."],["Waste allowance",`${F(p.waste,2)}%`,"Cuts and planning margin."],["Order target",`${F(p.target,2)} ft²`,"Area after waste."],["Coverage per box",`${F(p.boxCoverage,2)} ft²`,"Entered package label."],["Boxes to buy",F(p.boxes,0),"Rounded up."],["Purchased coverage",`${F(p.purchased,2)} ft²`,"Whole-box coverage."],["Left after installation",`${F(p.leftover,2)} ft²`,"Includes waste and package remainder."],["Flooring cost",USD(p.boxCost),"Boxes times price."],["Underlayment rolls",F(p.underlayRolls,0),"Rounded up separately."],["Estimated total",USD(p.totalCost),"Entered materials only."]];
  } else if (engine === "tile_advanced") {
    const p=tileProjection();
    cards=[["Boxes to buy",F(p.boxes,0),`${F(p.perBox,0)} pieces per box.`],["Tiles needed",F(p.pieces,0),`${F(p.waste,1)}% waste included.`],["Purchased coverage",`${F(p.purchasedArea,1)} ft²`,"Full boxes converted to area."],["Estimated tile cost",USD(p.cost),"Boxes times entered price."]];
    bars=[{label:"Project area",value:p.area,display:`${F(p.area,1)} ft²`},{label:"Waste allowance",value:p.targetArea-p.area,display:`${F(p.targetArea-p.area,1)} ft²`},{label:"Purchased coverage",value:p.purchasedArea,display:`${F(p.purchasedArea,1)} ft²`},{label:"Tile cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Project area",`${F(p.area,2)} ft²`,"Length times width."],["Tile face size",`${F(p.tileWidth,2)} x ${F(p.tileHeight,2)} in`,`${F(p.tileArea,4)} square feet each.`],["Waste allowance",`${F(p.waste,2)}%`,"Entered cutting margin."],["Order target",`${F(p.targetArea,2)} ft²`,"Project area after waste."],["Tiles needed",F(p.pieces,0),"Rounded up by piece."],["Tiles per box",F(p.perBox,0),"Entered package quantity."],["Boxes to buy",F(p.boxes,0),"Rounded up to full boxes."],["Purchased tile",`${F(p.purchasedArea,2)} ft²`,`${F(p.purchasedPieces,0)} total pieces.`],["Left after installation",`${F(p.leftover,2)} ft²`,"Includes waste and box remainder."],["Estimated cost",USD(p.cost),"Tile boxes only."]];
  } else if (engine === "deck_advanced") {
    const p=deckProjection();
    cards=[["Full boards to buy",F(p.boards,0),`${F(p.waste,1)}% waste included.`],["Board rows",F(p.rows,0),`${F(p.boardWidth,3)} in boards plus ${F(p.gap,3)} in gaps.`],["Fastener boxes",F(p.fastenerPacks,0),`${F(p.fasteners,0)} fasteners estimated.`],["Estimated materials",USD(p.totalCost),"Boards plus entered fastener cost."]];
    bars=[{label:"Base whole boards",value:p.baseBoards,display:F(p.baseBoards,0)},{label:"Boards with waste",value:p.boards,display:F(p.boards,0)},{label:"Joist lines",value:p.joists,display:F(p.joists,0)},{label:"Fastener boxes",value:p.fastenerPacks,display:F(p.fastenerPacks,0)},{label:"Material cost",value:p.totalCost,display:USD(p.totalCost)}];
    rows=[["Deck area",`${F(p.area,2)} ft²`,"Length times width."],["Board rows",F(p.rows,0),"Rounded across deck width."],["Stock boards per row",F(p.boardsPerRow,0),"Rounded from deck length."],["Base whole-board count",F(p.baseBoards,0),"Rows times boards per row."],["Waste allowance",`${F(p.waste,2)}%`,"Applied to whole-board count."],["Full boards to buy",F(p.boards,0),"Final count rounded up."],["Coverage linear footage",`${F(p.coverageLinear,1)} ft`,"Rows times deck length."],["Ordered stock footage",`${F(p.orderedLinear,1)} ft`,"Full boards times stock length."],["Joist lines",F(p.joists,0),`${F(p.joistSpacing,2)} in on center, including edges.`],["Fasteners",F(p.fasteners,0),`${F(p.fastenersPerCrossing,0)} per row and joist crossing.`],["Fastener boxes",F(p.fastenerPacks,0),`${F(p.fastenersPerPack,0)} per box.`],["Board cost",USD(p.boardCost),"Full boards times entered price."],["Fastener cost",USD(p.fastenerCost),"Full boxes times entered price."],["Estimated total",USD(p.totalCost),"Entered decking and fasteners only."]];
  } else if (engine === "board_foot_advanced") {
    const p=boardFootProjection();
    cards=[["Board feet to order",F(p.order,2),`${F(p.waste,1)}% waste included.`],["Board feet per piece",F(p.perBoard,3),`${F(p.thickness,2)} x ${F(p.width,2)} in x ${F(p.length,2)} ft.`],["Cubic feet",F(p.cubicFeet,3),"Waste-adjusted lumber volume."],["Estimated lumber cost",USD(p.cost),`${USD(p.price)} per board foot.`]];
    bars=[{label:"Board feet before waste",value:p.total,display:F(p.total,2)},{label:"Waste allowance",value:p.order-p.total,display:F(p.order-p.total,2)},{label:"Board feet to order",value:p.order,display:F(p.order,2)},{label:"Estimated cost",value:p.cost,display:USD(p.cost)}];
    rows=[["Dimensions",`${F(p.thickness,2)} in x ${F(p.width,2)} in x ${F(p.length,2)} ft`,"Entered pricing dimensions."],["Quantity",F(p.quantity,0),"Whole pieces."],["Board feet per piece",F(p.perBoard,4),"Thickness x width x length / 12."],["Board feet before waste",F(p.total,4),"Per-piece volume times quantity."],["Waste allowance",`${F(p.waste,2)}%`,"Entered purchasing margin."],["Board feet to order",F(p.order,4),"Volume after waste."],["Cubic feet",F(p.cubicFeet,4),"Board feet divided by 12."],["Total linear feet",`${F(p.linearFeet,2)} ft`,"Length times quantity before waste."],["Price per board foot",USD(p.price),"Entered unit price."],["Estimated cost",USD(p.cost),"Order volume times unit price."]];
  } else if (engine === "voltage_drop_advanced") {
    const p=voltageDropProjection(), material=p.material==='copper'?"Copper":"Aluminum", phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Voltage drop",`${F(p.drop,2)} V`,`${F(p.percent,2)}% of source voltage.`],["Voltage at load",`${F(p.loadVoltage,2)} V`,`${F(p.voltage,1)} V source.`],["Drop-target wire",`${p.recommended.g} AWG`,`${material}; ${F(p.limit,1)}% target.`],["Maximum run",`${F(p.maxLength,1)} ft`,"For selected wire and target."]];
    bars=[{label:"Source voltage",value:p.voltage,display:`${F(p.voltage,1)} V`},{label:"Voltage at load",value:p.loadVoltage,display:`${F(p.loadVoltage,2)} V`},{label:"Voltage lost",value:p.drop,display:`${F(p.drop,2)} V`},{label:"Drop limit",value:p.voltage*p.limit/100,display:`${F(p.limit,1)}%`}];
    rows=[["Circuit type",phase,"Selected formula."],["Conductor",`${p.gauge} AWG ${material}`,`${F(wireResistance(p.row,p.material),4)} ohms/1,000 ft reference.`],["One-way run",`${F(p.length,2)} ft`,"Round trip is handled by formula."],["Load current",`${F(p.amps,2)} A`,"Entered current."],["Source voltage",`${F(p.voltage,2)} V`,"Entered system voltage."],["Voltage drop",`${F(p.drop,3)} V`,`${F(p.percent,3)}% of source.`],["Voltage at load",`${F(p.loadVoltage,3)} V`,"Source minus estimated drop."],["Target conductor",`${p.recommended.g} AWG`,"Drop-only recommendation."],["Maximum selected-wire run",`${F(p.maxLength,2)} ft`,`${F(p.limit,2)}% entered target.`]];
  } else if (engine === "wire_size_advanced") {
    const p=wireSizeProjection(), material=p.material==='copper'?"Copper":"Aluminum", phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Recommended wire",`${p.recommended.g} AWG`,`${material}; larger of both checks.`],["Planning current",`${F(p.designAmps,2)} A`,"Includes continuous-load factor."],["Reference ampacity",`${F(p.ampacity,0)} A`,`${p.temp}°C selected column.`],["Voltage drop",`${F(p.dropPercent,2)}%`,`${F(p.drop,2)} V over entered run.`]];
    bars=[{label:"Actual load",value:p.amps,display:`${F(p.amps,2)} A`},{label:"Planning current",value:p.designAmps,display:`${F(p.designAmps,2)} A`},{label:"Reference ampacity",value:p.ampacity,display:`${F(p.ampacity,0)} A`},{label:"Drop percentage",value:p.dropPercent,display:`${F(p.dropPercent,2)}%`}];
    rows=[["Circuit type",phase,"Selected voltage-drop formula."],["Conductor",material,`${p.temp}°C reference column.`],["Actual load",`${F(p.amps,2)} A`,"Entered total current."],["Continuous portion",`${F(p.continuous,2)} A`,"Receives 125% planning factor."],["Planning current",`${F(p.designAmps,2)} A`,"Ampacity sizing load."],["Ampacity-only size",`${p.ampacityRow.g} AWG`,"First size meeting reference ampacity."],["Drop-only size",`${p.dropRow.g} AWG`,`${F(p.limit,2)}% target.`],["Recommended size",`${p.recommended.g} AWG`,"Larger of ampacity and drop checks."],["Reference ampacity",`${F(p.ampacity,0)} A`,"Before correction or adjustment."],["Estimated voltage drop",`${F(p.drop,3)} V`,`${F(p.dropPercent,3)}%; ${F(p.loadVoltage,2)} V at load.`]];
  } else if (engine === "breaker_advanced") {
    const p=breakerProjection();
    cards=[["Reference breaker",`${F(p.breaker,0)} A`,`${F(p.poles,0)} pole selection.`],["Planning current",`${F(p.planning,2)} A`,"125% continuous plus noncontinuous."],["Connected load",`${F(p.actual,2)} A`,`${F(p.utilization,1)}% of reference breaker.`],["Connected power",`${F(p.power,0)} W`,`${F(p.voltage,0)} V x actual amps.`]];
    bars=[{label:"Continuous load",value:p.continuous,display:`${F(p.continuous,2)} A`},{label:"Noncontinuous load",value:p.noncontinuous,display:`${F(p.noncontinuous,2)} A`},{label:"Planning current",value:p.planning,display:`${F(p.planning,2)} A`},{label:"Reference breaker",value:p.breaker,display:`${F(p.breaker,0)} A`}];
    rows=[["Continuous load",`${F(p.continuous,3)} A`,"Multiplied by 125%."],["Noncontinuous load",`${F(p.noncontinuous,3)} A`,"Added at 100%."],["Connected load",`${F(p.actual,3)} A`,"Sum before planning factor."],["Minimum planning current",`${F(p.planning,3)} A`,"Continuous x 1.25 plus noncontinuous."],["Reference breaker",`${F(p.breaker,0)} A`,"Next familiar standard rating."],["Planning headroom",`${F(p.headroom,2)} A`,"Breaker minus planning current."],["Connected-load utilization",`${F(p.utilization,2)}%`,"Actual amps divided by reference breaker."],["Connected power",`${F(p.power,1)} W`,"Simple volts x amps display."]];
  } else if (engine === "electrical_load_advanced") {
    const p=electricalLoadProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Actual current",`${F(p.amps,2)} A`,`${F(p.watts,0)} W total load.`],["Planning current",`${F(p.planningAmps,2)} A`,"Continuous portion at 125%."],["Apparent power",`${F(p.va,0)} VA`,`${F(p.pf,2)} power factor.`],["Reference breaker",`${F(p.breaker,0)} A`,"Planning result only."]];
    bars=[{label:"Continuous power",value:p.continuous,display:`${F(p.continuous,0)} W`},{label:"Noncontinuous power",value:p.noncontinuous,display:`${F(p.noncontinuous,0)} W`},{label:"Actual current",value:p.amps,display:`${F(p.amps,2)} A`},{label:"Planning current",value:p.planningAmps,display:`${F(p.planningAmps,2)} A`}];
    rows=[["Circuit type",phase,"Selected current formula."],["Continuous load",`${F(p.continuous,2)} W`,"Receives 125% planning factor."],["Noncontinuous load",`${F(p.noncontinuous,2)} W`,"Included at 100%."],["Total real power",`${F(p.watts,2)} W`,"Entered loads combined."],["Power factor",F(p.pf,3),p.phase==='dc'?"Not applied to DC.":"Used for AC current."],["Apparent power",`${F(p.va,2)} VA`,"Watts divided by power factor."],["Actual current",`${F(p.amps,3)} A`,"Before continuous-load factor."],["Planning power",`${F(p.planningWatts,2)} W`,"Continuous x 1.25 plus other load."],["Planning current",`${F(p.planningAmps,3)} A`,"Used for reference breaker."],["Reference breaker",`${F(p.breaker,0)} A`,`${F(p.utilization,1)}% connected-load utilization.`]];
  } else if (engine === "watts_amps_advanced") {
    const p=wattsAmpsProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Calculated current",`${F(p.amps,3)} A`,`${F(p.watts,1)} W real power.`],["Real power",`${F(p.watts/1000,3)} kW`,"Entered wattage."],["Apparent power",`${F(p.va,1)} VA`,`${F(p.pf,2)} power factor.`],["Planning current",`${F(p.planningAmps,3)} A`,p.continuous?"Includes 125% continuous factor.":"No continuous factor selected."]];
    bars=[{label:"Real power",value:p.watts,display:`${F(p.watts,1)} W`},{label:"Apparent power",value:p.va,display:`${F(p.va,1)} VA`},{label:"Reactive power",value:p.vars,display:`${F(p.vars,1)} VAR`},{label:"Current",value:p.amps,display:`${F(p.amps,3)} A`}];
    rows=[["Power system",phase,p.phase==='three'?"Uses line-to-line voltage.":"Selected conversion mode."],["Real power",`${F(p.watts,3)} W`,`${F(p.watts/1000,4)} kW.`],["Voltage",`${F(p.voltage,3)} V`,p.phase==='three'?"Line-to-line RMS voltage.":"Entered voltage."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Real power divided by apparent power."],["Calculated current",`${F(p.amps,4)} A`,"Formula result."],["Apparent power",`${F(p.va,3)} VA`,`${F(p.va/1000,4)} kVA.`],["Reactive power",`${F(p.vars,3)} VAR`,"Simplified magnitude."],["Load duration",p.continuous?"Continuous planning":"Conversion only",p.continuous?"125% factor shown.":"No sizing factor applied."],["Planning current",`${F(p.planningAmps,4)} A`,p.continuous?"Calculated amps x 1.25.":"Same as calculated amps."]];
  } else if (engine === "amps_watts_advanced") {
    const p=ampsWattsProjection(), phase=p.phase==='three'?"Three-phase AC":p.phase==='dc'?"DC":"Single-phase AC";
    cards=[["Real power",`${F(p.watts,1)} W`,`${F(p.watts/1000,3)} kW.`],["Apparent power",`${F(p.va,1)} VA`,`${F(p.va/1000,3)} kVA.`],["Reactive power",`${F(p.vars,1)} VAR`,"Simplified magnitude."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Entered AC power factor."]];
    bars=[{label:"Real power",value:p.watts,display:`${F(p.watts,1)} W`},{label:"Apparent power",value:p.va,display:`${F(p.va,1)} VA`},{label:"Reactive power",value:p.vars,display:`${F(p.vars,1)} VAR`},{label:"Current",value:p.amps,display:`${F(p.amps,3)} A`}];
    rows=[["Power system",phase,p.phase==='three'?"Uses line-to-line voltage.":"Selected conversion mode."],["Current",`${F(p.amps,4)} A`,"Entered RMS current."],["Voltage",`${F(p.voltage,3)} V`,p.phase==='three'?"Line-to-line RMS voltage.":"Entered voltage."],["Power factor",F(p.pf,3),p.phase==='dc'?"Fixed at 1 for DC.":"Entered AC ratio."],["Real power",`${F(p.watts,3)} W`,`${F(p.watts/1000,4)} kW.`],["Apparent power",`${F(p.va,3)} VA`,`${F(p.va/1000,4)} kVA.`],["Reactive power",`${F(p.vars,3)} VAR`,"Square root of VA² minus W²."]];
  } else if (engine === "tire_compare") {
    const p=tireComparison(), speedError=p.actualSpeed-p.indicated;
    cards=[["Diameter difference",`${p.differencePct>=0?'+':''}${F(p.differencePct,2)}%`,"New tire versus original."],["Actual speed",`${F(p.actualSpeed,2)} mph`,`${F(p.indicated,0)} mph indicated.`],["Ground clearance",`${p.clearance>=0?'+':''}${F(p.clearance,2)} in`,"Half the diameter change."],["Revolutions per mile",F(p.next.revsPerMile,1),"Calculated new tire value."]];
    bars=[{label:"Original diameter",value:p.original.diameter,display:`${F(p.original.diameter,2)} in`},{label:"New diameter",value:p.next.diameter,display:`${F(p.next.diameter,2)} in`},{label:"Original sidewall",value:p.original.sidewall/25.4,display:`${F(p.original.sidewall,1)} mm`},{label:"New sidewall",value:p.next.sidewall/25.4,display:`${F(p.next.sidewall,1)} mm`}];
    rows=[["Original size",`${F(p.original.width,0)}/${F(p.original.aspect,0)}R${F(p.original.rim,1)}`,"Entered baseline tire."],["New size",`${F(p.next.width,0)}/${F(p.next.aspect,0)}R${F(p.next.rim,1)}`,"Entered comparison tire."],["Original diameter",`${F(p.original.diameter,3)} in`,"Nominal calculated diameter."],["New diameter",`${F(p.next.diameter,3)} in`,"Nominal calculated diameter."],["Diameter difference",`${p.differencePct>=0?'+':''}${F(p.differencePct,3)}%`,"Common 3% guidance is not fitment approval."],["Speedometer difference",`${speedError>=0?'+':''}${F(speedError,2)} mph`,`${F(p.indicated,0)} mph indicated.`],["Ground-clearance change",`${p.clearance>=0?'+':''}${F(p.clearance,3)} in`,"Static estimate."],["New revolutions per mile",F(p.next.revsPerMile,2),"Actual tire specs may vary."]];
  } else if (engine === "wheel_offset_compare") {
    const p=wheelOffsetComparison(), clearanceNote=p.innerClearance>=0?"More suspension-side clearance.":"Less suspension-side clearance.";
    cards=[["Outer position",`${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm`,p.outerPoke>=0?"Farther toward the fender.":"Farther inward."],["Inner clearance",`${p.innerClearance>=0?'+':''}${F(p.innerClearance,1)} mm`,clearanceNote],["Track change",`${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm`,"Estimated across both wheels."],["Effective new offset",`ET${F(p.effectiveOffset,1)}`,"New offset minus spacer."]];
    bars=[{label:"Outer position change",value:p.outerPoke,display:`${p.outerPoke>=0?'+':''}${F(p.outerPoke,1)} mm`},{label:"Inner clearance change",value:p.innerClearance,display:`${p.innerClearance>=0?'+':''}${F(p.innerClearance,1)} mm`},{label:"Track change",value:p.trackChange,display:`${p.trackChange>=0?'+':''}${F(p.trackChange,1)} mm`},{label:"Spacer",value:p.spacer,display:`${F(p.spacer,1)} mm`}];
    rows=[["Current wheel",`${F(p.currentWidth,1)} in ET${F(p.currentOffset,1)}`,"Entered baseline wheel."],["New wheel",`${F(p.newWidth,1)} in ET${F(p.newOffset,1)}`,"Before spacer adjustment."],["Effective new offset",`ET${F(p.effectiveOffset,1)}`,"Offset minus spacer thickness."],["Inner clearance change",`${p.innerClearance>=0?'+':''}${F(p.innerClearance,2)} mm`,clearanceNote],["Outer position change",`${p.outerPoke>=0?'+':''}${F(p.outerPoke,2)} mm`,p.outerPoke>=0?"Additional poke.":"Moves inward."],["Estimated track change",`${p.trackChange>=0?'+':''}${F(p.trackChange,2)} mm`,"Both sides combined."],["Current backspacing",`${F(p.currentBackspacing,3)} in`,"Includes estimated rim lips."],["New backspacing",`${F(p.newBackspacing,3)} in`,"Includes estimated rim lips and spacer."]];
  } else if (engine === "mpg_advanced") {
    const distance=V('distance'), fuel=V('fuel_used'), miles=document.getElementById('distance_unit')?.value==='kilometers'?distance*0.621371192237:distance, liters=fuel*(document.getElementById('fuel_unit')?.value==='us_gallon'?3.785411784:document.getElementById('fuel_unit')?.value==='imperial_gallon'?4.54609:1), km=miles/0.621371192237, usGallons=liters/3.785411784, imperialGallons=liters/4.54609, usMpg=usGallons>0?miles/usGallons:0, imperialMpg=imperialGallons>0?miles/imperialGallons:0, l100=km>0?liters/km*100:0, kmL=liters>0?km/liters:0;
    cards=[["US fuel economy",`${F(usMpg,2)} MPG`,"Miles per US gallon."],["Metric consumption",`${F(l100,2)} L/100 km`,"Lower is more efficient."],["Imperial fuel economy",`${F(imperialMpg,2)} MPG`,"Miles per UK gallon."],["Kilometers per liter",`${F(kmL,2)} km/L`,"Distance per liter."]];
    bars=[{label:"US MPG",value:usMpg,display:F(usMpg,2)},{label:"Imperial MPG",value:imperialMpg,display:F(imperialMpg,2)},{label:"km/L",value:kmL,display:F(kmL,2)},{label:"L/100 km",value:l100,display:F(l100,2)}];
    rows=[["Entered distance",`${F(distance,2)} ${document.getElementById('distance_unit')?.value||'miles'}`,"Normalized before conversion."],["Entered fuel",`${F(fuel,3)} ${(document.getElementById('fuel_unit')?.selectedOptions[0]?.textContent)||'fuel units'}`,"Normalized to liters."],["Distance in miles",F(miles,4),"Used for MPG."],["Fuel in US gallons",F(usGallons,4),"Used for US MPG."],["US MPG",F(usMpg,3),"Miles divided by US gallons."],["L/100 km",F(l100,3),"Liters used per 100 kilometers."]];
  } else if (engine === "fuel_cost_advanced") {
    const metric=document.getElementById('trip_units')?.value==='metric', oneWay=V('distance'), multiplier=Math.max(1,V('trip_type'))*Math.max(1,V('trips')), distance=oneWay*multiplier, efficiency=Math.max(.01,V('efficiency')), fuel=metric?distance*efficiency/100:distance/efficiency, price=V('fuelprice'), cost=fuel*price, currency=document.getElementById('currency')?.value||'USD', people=Math.max(1,V('people')), perPerson=cost/people, perDistance=distance>0?cost/distance:0;
    cards=[["Estimated fuel cost",MONEY(cost,currency),"For all selected trips."],["Fuel needed",`${F(fuel,2)} ${metric?'L':'gal'}`,"Estimated volume used."],["Cost per person",MONEY(perPerson,currency),`Split between ${F(people,0)} people.`],[`Cost per ${metric?'km':'mile'}`,MONEY(perDistance,currency),"Fuel cost only."]];
    bars=[{label:"Fuel cost",value:cost,display:MONEY(cost,currency)},{label:"Per person",value:perPerson,display:MONEY(perPerson,currency)},{label:`Fuel ${metric?'liters':'gallons'}`,value:fuel,display:F(fuel,2)}];
    rows=[["One-way distance",`${F(oneWay,1)} ${metric?'km':'mi'}`,"Entered route length."],["Total distance",`${F(distance,1)} ${metric?'km':'mi'}`,"Trip type multiplied by trip count."],["Fuel economy",`${F(efficiency,2)} ${metric?'L/100 km':'MPG'}`,"Entered real-world estimate."],["Fuel price",`${MONEY(price,currency)} / ${metric?'L':'gal'}`,"No currency conversion applied."],["Fuel needed",`${F(fuel,3)} ${metric?'L':'gal'}`,"Calculated trip volume."],["Total fuel cost",MONEY(cost,currency),"Fuel only."],["Cost per person",MONEY(perPerson,currency),"Even split."]];
  } else if (engine === "payload") {
    const capacity=V('gvwr')-V('curb'), occupants=V('people'), cargo=V('cargo'), tongue=V('tongue'), used=occupants+cargo+tongue, remaining=capacity-used, utilization=capacity>0?used/capacity*100:0;
    cards=[["Remaining payload",`${F(remaining,0)} lb`,remaining>=0?"Available before reaching GVWR.":"Entered load exceeds GVWR."],["Payload capacity",`${F(capacity,0)} lb`,"GVWR minus curb weight."],["Payload used",`${F(used,0)} lb`,"Occupants, cargo, and tongue weight."],["Utilization",`${F(utilization,1)}%`,"Share of payload capacity used."]];
    bars=[{label:"Occupants",value:occupants,display:`${F(occupants,0)} lb`},{label:"Cargo",value:cargo,display:`${F(cargo,0)} lb`},{label:"Tongue weight",value:tongue,display:`${F(tongue,0)} lb`},{label:"Remaining",value:Math.max(0,remaining),display:`${F(remaining,0)} lb`}];
    rows=[["GVWR",`${F(V('gvwr'),0)} lb`,"Maximum entered vehicle weight."],["Curb weight",`${F(V('curb'),0)} lb`,"Entered empty vehicle weight."],["Payload capacity",`${F(capacity,0)} lb`,"GVWR minus curb weight."],["Loaded vehicle weight",`${F(V('curb')+used,0)} lb`,"Curb weight plus entered payload."],["Remaining payload",`${F(remaining,0)} lb`,remaining>=0?"Within entered GVWR.":"Reduce load before travel."]];
  } else if (engine === "towing") {
    const loaded=V('curb')+V('people')+V('cargo'), remainingPayload=Math.max(0,V('gvwr')-loaded), pct=Math.max(.01,V('tongue_pct')/100), limits=[{label:"Vehicle tow rating",value:V('rating')},{label:"GCWR headroom",value:Math.max(0,V('gcwr')-loaded)},{label:"Hitch rating",value:V('hitch_rating')},{label:"Payload-based limit",value:remainingPayload/pct}], controlling=limits.reduce((a,b)=>b.value<a.value?b:a), tongue=controlling.value*pct;
    cards=[["Planning trailer limit",`${F(controlling.value,0)} lb`,"Lowest entered or calculated limit."],["Controlling factor",controlling.label,"The first rating reached."],["Estimated tongue weight",`${F(tongue,0)} lb`,`${F(V('tongue_pct'),1)}% of planning trailer limit.`],["Payload before hitch",`${F(remainingPayload,0)} lb`,"Available after passengers and cargo."]];
    bars=limits.map(item=>({label:item.label,value:item.value,display:`${F(item.value,0)} lb`}));
    rows=[["Loaded tow vehicle",`${F(loaded,0)} lb`,"Curb weight, occupants, and cargo."],["Tow rating",`${F(V('rating'),0)} lb`,"Vehicle manufacturer's entered rating."],["GCWR trailer headroom",`${F(Math.max(0,V('gcwr')-loaded),0)} lb`,"GCWR minus loaded vehicle."],["Hitch trailer rating",`${F(V('hitch_rating'),0)} lb`,"Entered equipment rating."],["Payload-based trailer limit",`${F(remainingPayload/pct,0)} lb`,"Remaining payload divided by tongue percentage."],["Planning limit",`${F(controlling.value,0)} lb`,controlling.label+" controls."]];
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
  const activeMode = document.querySelector("[data-loan-mode].is-active")?.dataset.loanMode || "monthlyfixed";
  const payback = document.getElementById("l_payback")?.value || "month";
  const compound = document.getElementById("l_compound")?.value || "monthly";
  const P = V("l_amount"), annual = V("l_rate") / 100, rate = effectiveRate(annual, compound, payback);
  const n = loanTermPeriods("l_years", "l_months", payback);
  const payment = rate ? P * rate * Math.pow(1 + rate, n) / (Math.pow(1 + rate, n) - 1) : P / n;
  const total = payment * n, interest = total - P, payLabel = paybackLabel(payback);
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
  if (activeMode === "intheend") show(`<strong>${USD(due)} due at maturity</strong><br>${USD(dP)} principal; ${USD(dInterest)} compounded interest over ${F(dYears,2)} years.`);
  else if (activeMode === "fixedend") show(`<strong>${USD(received)} present value</strong><br>${USD(bDue)} predetermined due amount; ${USD(bInterest)} total discount or interest.`);
  else show(`<strong>${USD(payment)} / ${payLabel.toLowerCase()}</strong><br>Total of ${F(n,0)} payments: ${USD(total)}; total interest: ${USD(interest)}.`);
}

function setLoanMode(mode) {
  document.querySelectorAll("[data-loan-mode]").forEach(button => {
    const active = button.dataset.loanMode === mode;
    button.classList.toggle("is-active", active);
    button.setAttribute("aria-selected", active ? "true" : "false");
  });
  document.querySelectorAll(".loan-mode-input").forEach(panel => panel.classList.toggle("is-active", panel.id === mode));
  document.querySelectorAll(".loan-result-panel").forEach(panel => panel.classList.toggle("is-active", panel.id === mode + "r"));
  renderLoanPage();
}

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-loan-mode]");
  if (tab) setLoanMode(tab.dataset.loanMode);
});

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-payment-mode]");
  if(tab){syncPaymentMode(tab.dataset.paymentMode);calc('payment_advanced')}
});

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-retirement-mode]");
  if(tab){syncRetirementMode(tab.dataset.retirementMode);calc('retirement_advanced')}
});

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-k401-mode]");
  if(tab){syncK401Mode(tab.dataset.k401Mode);calc('401k_advanced')}
});

document.addEventListener("click", event => {
  const tab = event.target.closest("[data-ss-mode]");
  if(tab){syncSocialSecurityMode(tab.dataset.ssMode);calc('social_security_advanced')}
});

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

BASIC_CALCULATOR_JS = r'''
(function(){
  const input=document.getElementById('basicExpression'),output=document.getElementById('basicResult'),status=document.getElementById('basicStatus'),memoryLabel=document.getElementById('basicMemory'),historyList=document.getElementById('basicHistory');
  if(!input||!output||!status||!memoryLabel||!historyList||!window.math)return;
  let answer=0,memory=0,history=[],afterResult=false;
  function format(value){
    if(typeof value!=='number'||!Number.isFinite(value))throw new Error('The result is outside the supported numeric range.');
    return math.format(value,{precision:14,lowerExp:-9,upperExp:15});
  }
  function normalize(raw){
    if(!raw.trim())throw new Error('Enter a calculation.');
    if(raw.length>180)throw new Error('Keep the expression under 180 characters.');
    if(!/^[0-9A-Za-z+\-*/^().,%\s]+$/.test(raw)||/[;=\[\]{}'"_:?]/.test(raw))throw new Error('Use numbers and the calculator keys only.');
    const identifiers=raw.match(/[A-Za-z]+/g)||[];
    const unsupported=identifiers.find(name=>!['sqrt','ans','e'].includes(name.toLowerCase()));
    if(unsupported)throw new Error(`${unsupported} is not supported by this basic calculator.`);
    let expression=raw.replace(/\bAns\b/gi,'ans');
    for(let pass=0;pass<4;pass++)expression=expression.replace(/(\d+(?:\.\d+)?(?:e[+\-]?\d+)?|\([^()]*\))%/gi,'($1/100)');
    return expression;
  }
  function renderHistory(){
    historyList.innerHTML=history.length?history.map((item,index)=>`<li><button type="button" data-basic-history="${index}"><span>${item.expression}</span><strong>${item.result}</strong></button></li>`).join(''):'<li class="basic-history-empty">Your calculations will appear here.</li>';
  }
  function updateMemory(message){
    memoryLabel.textContent=memory===0?'Memory: empty':`M = ${format(memory)}`;
    if(message)status.textContent=message;
  }
  function run(){
    try{
      const expression=input.value.trim(),value=math.evaluate(normalize(expression),new Map([['ans',answer]]));
      if(typeof value!=='number')throw new Error('This expression does not have a real-number result.');
      const result=format(value);output.textContent=result;status.textContent='Calculated';answer=value;afterResult=true;
      history=[{expression,result},...history.filter(item=>item.expression!==expression)].slice(0,10);renderHistory();
    }catch(error){output.textContent='Error';status.textContent=error&&error.message?error.message:'Check the expression.';afterResult=false}
  }
  function insert(value){
    const isNumber=/^(?:\d*\.?\d+(?:e[+\-]?\d+)?)$/i.test(value);
    if(afterResult&&isNumber){input.value='';afterResult=false}
    else if(afterResult&&/^[+\-*/]$/.test(value)){input.value=format(answer);afterResult=false}
    const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
    input.value=input.value.slice(0,start)+value+input.value.slice(end);const caret=start+value.length;input.focus();input.setSelectionRange(caret,caret);status.textContent='Ready';
  }
  function wrap(prefix,suffix=')'){
    const expression=input.value.trim()||(Number.isFinite(answer)?format(answer):'0');input.value=`${prefix}${expression}${suffix}`;afterResult=false;input.focus();input.setSelectionRange(input.value.length,input.value.length);
  }
  function applyPercent(){
    const raw=input.value.trim();if(!raw){input.value='0';return}
    const match=raw.match(/^(.*)([+\-*/])\s*(\d*\.?\d+(?:e[+\-]?\d+)?)$/i);
    if(match&&match[1].trim()){
      const base=match[1].trim(),operator=match[2],percent=match[3];
      input.value=(operator==='+'||operator==='-')?`${base}${operator}(${base})*(${percent}/100)`: `${base}${operator}(${percent}/100)`;
    }else input.value=`(${raw})/100`;
    afterResult=false;input.focus();input.setSelectionRange(input.value.length,input.value.length);status.textContent='Percent applied';
  }
  document.addEventListener('click',event=>{
    const historyButton=event.target.closest('[data-basic-history]');
    if(historyButton){const item=history[Number(historyButton.dataset.basicHistory)];if(item){input.value=item.expression;afterResult=false;input.focus()}return}
    const button=event.target.closest('[data-basic-action]');if(!button)return;
    const action=button.dataset.basicAction,value=button.dataset.basicValue||'';
    if(action==='insert')insert(value);else if(action==='calculate')run();else if(action==='clear'){input.value='';output.textContent='0';status.textContent='Ready';afterResult=false;input.focus()}
    else if(action==='backspace'){const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;if(start!==end)input.value=input.value.slice(0,start)+input.value.slice(end);else if(start>0)input.value=input.value.slice(0,start-1)+input.value.slice(end);const caret=Math.max(0,start-(start===end?1:0));afterResult=false;input.focus();input.setSelectionRange(caret,caret)}
    else if(action==='root')wrap('sqrt(',')');else if(action==='square')wrap('(',')^2');else if(action==='reciprocal')wrap('1/(',')');else if(action==='negate')wrap('-(',')');else if(action==='percent')applyPercent();else if(action==='answer')insert(format(answer));
    else if(action==='memory-clear'){memory=0;updateMemory('Memory cleared')}else if(action==='memory-recall')insert(format(memory));else if(action==='memory-add'){memory+=answer;updateMemory('Answer added to memory')}else if(action==='memory-subtract'){memory-=answer;updateMemory('Answer subtracted from memory')}else if(action==='history-clear'){history=[];renderHistory();status.textContent='History cleared'}
  });
  input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run()}else if(event.key==='Escape'){event.preventDefault();input.value='';output.textContent='0';status.textContent='Ready';afterResult=false}});
  updateMemory();
})();
'''


SCIENTIFIC_JS = r'''
(function(){
  const input=document.getElementById('sciExpression'),output=document.getElementById('sciResult'),status=document.getElementById('sciStatus'),historyList=document.getElementById('sciHistory');
  if(!input||!output||!status||!historyList||!window.math)return;
  let angleMode='deg',answer=0,memory=0,lastNumeric=12.25,history=[];
  const allowed=new Set(['sqrt','sin','cos','tan','asin','acos','atan','log','ln','abs','floor','ceil','round','exp','factorial','min','max','mod','pi','e','ans']);
  const toRadians=value=>angleMode==='deg'?value*Math.PI/180:value;
  const fromRadians=value=>angleMode==='deg'?value*180/Math.PI:value;
  const scope=()=>new Map([
    ['ans',answer],['nsSin',value=>Math.sin(toRadians(value))],['nsCos',value=>Math.cos(toRadians(value))],['nsTan',value=>Math.tan(toRadians(value))],
    ['nsAsin',value=>fromRadians(Math.asin(value))],['nsAcos',value=>fromRadians(Math.acos(value))],['nsAtan',value=>fromRadians(Math.atan(value))],
    ['log',value=>Math.log10(value)],['ln',value=>Math.log(value)]
  ]);
  function normalized(raw){
    if(!raw.trim())throw new Error('Enter an expression.');
    if(raw.length>240)throw new Error('Keep the expression under 240 characters.');
    if(!/^[0-9A-Za-z+\-*/^().,%!\s]+$/.test(raw)||/[;=\[\]{}'"_:?]/.test(raw))throw new Error('Use numbers, supported functions, and arithmetic operators only.');
    const identifiers=raw.match(/[A-Za-z]+/g)||[];
    const unsupported=identifiers.find(name=>!allowed.has(name.toLowerCase())&&!/^e\d+$/i.test(name));
    if(unsupported)throw new Error(`${unsupported} is not a supported function or constant.`);
    let expression=raw.replace(/\bAns\b/gi,'ans');
    for(let pass=0;pass<4;pass++)expression=expression.replace(/(\d+(?:\.\d+)?|\([^()]*\))%/g,'($1/100)');
    expression=expression.replace(/\basin\s*\(/gi,'nsAsin(').replace(/\bacos\s*\(/gi,'nsAcos(').replace(/\batan\s*\(/gi,'nsAtan(')
      .replace(/\bsin\s*\(/gi,'nsSin(').replace(/\bcos\s*\(/gi,'nsCos(').replace(/\btan\s*\(/gi,'nsTan(');
    return expression;
  }
  function displayValue(value){
    if(typeof value==='number'){
      if(!Number.isFinite(value))throw new Error('The result is outside the supported numeric range.');
      return math.format(value,{precision:14,lowerExp:-9,upperExp:15});
    }
    if(value&&typeof value.toString==='function')return math.format(value,{precision:14});
    throw new Error('The expression did not return a numeric result.');
  }
  function renderHistory(){
    historyList.innerHTML=history.length?history.map((item,index)=>`<li><button type="button" data-history-index="${index}"><span>${item.expression}</span><strong>${item.result}</strong></button></li>`).join(''):'<li class="sci-history-empty">Your calculations will appear here.</li>';
  }
  function run(){
    try{
      const expression=input.value.trim(),value=math.evaluate(normalized(expression),scope()),formatted=displayValue(value);
      output.textContent=formatted;status.textContent=`Calculated in ${angleMode==='deg'?'degree':'radian'} mode`;answer=value;lastNumeric=typeof value==='number'?value:lastNumeric;
      history=[{expression,result:formatted},...history.filter(item=>item.expression!==expression)].slice(0,8);renderHistory();
    }catch(error){output.textContent='Check expression';status.textContent=error&&error.message?error.message:'The expression could not be evaluated.'}
  }
  function insert(value){
    const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;
    input.value=input.value.slice(0,start)+value+input.value.slice(end);const caret=start+value.length;input.focus();input.setSelectionRange(caret,caret);
  }
  function wrap(prefix,suffix=')'){
    const expression=input.value.trim()||'0';input.value=`${prefix}${expression}${suffix}`;input.focus();input.setSelectionRange(input.value.length,input.value.length);
  }
  function setMode(mode){
    angleMode=mode;document.querySelectorAll('[data-angle-mode]').forEach(button=>{const active=button.dataset.angleMode===mode;button.classList.toggle('is-active',active);button.setAttribute('aria-pressed',active?'true':'false')});status.textContent=`Ready in ${mode==='deg'?'degree':'radian'} mode`;
  }
  document.addEventListener('click',event=>{
    const modeButton=event.target.closest('[data-angle-mode]');if(modeButton){setMode(modeButton.dataset.angleMode);return}
    const historyButton=event.target.closest('[data-history-index]');if(historyButton){const item=history[Number(historyButton.dataset.historyIndex)];if(item){input.value=item.expression;input.focus()}return}
    const button=event.target.closest('[data-sci-action]');if(!button)return;const action=button.dataset.sciAction,value=button.dataset.sciValue||'';
    if(action==='insert')insert(value);else if(action==='calculate')run();else if(action==='clear'){input.value='';output.textContent='0';status.textContent=`Ready in ${angleMode==='deg'?'degree':'radian'} mode`;input.focus()}
    else if(action==='backspace'){const start=input.selectionStart??input.value.length,end=input.selectionEnd??start;if(start!==end)input.value=input.value.slice(0,start)+input.value.slice(end);else if(start>0)input.value=input.value.slice(0,start-1)+input.value.slice(end);const caret=Math.max(0,start-(start===end?1:0));input.focus();input.setSelectionRange(caret,caret)}
    else if(action==='square')wrap('(',')^2');else if(action==='reciprocal')wrap('1/(',')');else if(action==='negate')wrap('-(',')');else if(action==='percent')wrap('(',')%');
    else if(action==='memory-clear'){memory=0;status.textContent='Memory cleared'}else if(action==='memory-recall')insert(math.format(memory,{precision:14}));else if(action==='memory-add'){memory+=Number(lastNumeric)||0;status.textContent=`Memory: ${math.format(memory,{precision:14})}`}else if(action==='memory-subtract'){memory-=Number(lastNumeric)||0;status.textContent=`Memory: ${math.format(memory,{precision:14})}`}else if(action==='history-clear'){history=[];renderHistory()}
  });
  input.addEventListener('keydown',event=>{if(event.key==='Enter'){event.preventDefault();run()}else if(event.key==='Escape'){event.preventDefault();input.value='';output.textContent='0';status.textContent=`Ready in ${angleMode==='deg'?'degree':'radian'} mode`}});
  setMode('deg');
})();
'''

LOGO_SVG = r'''
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="NS Calculators">
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
    rmd_joint_table = json.loads(RMD_JOINT_LIFE_TABLE.read_text(encoding="utf-8"))["rows"]
    site = dict(data["site"])
    if PUBLIC_SITE_DOMAIN:
        site["domain"] = PUBLIC_SITE_DOMAIN
    calculators = [c for c in base_and_supplemental(data) if c["slug"] not in CALCULATOR_REDIRECTS]
    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    write(DIST / "assets" / "site.css", CSS.strip() + "\n")
    write(DIST / "assets" / "search.js", SEARCH_JS.strip() + "\n")
    write(DIST / "assets" / "home.js", HOME_JS.strip() + "\n")
    write(DIST / "assets" / "basic-calculator.js", BASIC_CALCULATOR_JS.strip() + "\n")
    write(DIST / "assets" / "scientific.js", SCIENTIFIC_JS.strip() + "\n")
    shutil.copyfile(ROOT / "vendor" / "mathjs-15.2.0.min.js", DIST / "assets" / "mathjs.min.js")
    shutil.copyfile(ROOT / "vendor" / "mathjs-LICENSE.txt", DIST / "assets" / "mathjs-LICENSE.txt")
    shutil.copyfile(ROOT / "vendor" / "mathjs-NOTICE.txt", DIST / "assets" / "mathjs-NOTICE.txt")
    calculator_js = CALC_JS.replace("__RMD_JOINT_TABLE__", json.dumps(rmd_joint_table, separators=(",", ":")))
    write(DIST / "assets" / "calculator.js", calculator_js.strip() + "\n")
    search_index = [
        {"title": c["title"], "slug": c["slug"], "desc": c["desc"], "cat": c["cat"], "keyword": primary_keyword(c)}
        for c in calculators
    ]
    write(DIST / "assets" / "search-index.json", json.dumps(search_index, ensure_ascii=False, separators=(",", ":")) + "\n")
    write(DIST / "favicon.svg", LOGO_SVG.strip() + "\n")
    write(DIST / "apple-touch-icon.svg", LOGO_SVG.strip() + "\n")
    write(DIST / "index.html", home_new(site, calculators))

    by_cat = defaultdict(list)
    for calc in calculators:
        by_cat[calc["cat"]].append(calc)
    for cat in CATEGORY_ORDER:
        all_category_items = by_cat.get(cat, [])
        if not all_category_items:
            continue
        indexable_items = [c for c in all_category_items if is_indexable_calculator(c)]
        visible_items = indexable_items or all_category_items
        write(DIST / slugify_cat(cat) / "index.html", category_page(site, cat, visible_items, indexable=bool(indexable_items)))
    for calc in calculators:
        indexable_peers = [c for c in by_cat[calc["cat"]] if is_indexable_calculator(c)]
        if calc in indexable_peers and len(indexable_peers) > 1:
            current_index = indexable_peers.index(calc)
            ring = []
            for offset in range(1, len(indexable_peers)):
                candidate = indexable_peers[(current_index + offset) % len(indexable_peers)]
                if candidate not in ring:
                    ring.append(candidate)
            same_group = [c for c in ring if calculator_group(c) == calculator_group(calc)]
            rel = same_group[:4]
            for candidate in ring:
                if candidate not in rel:
                    rel.append(candidate)
                if len(rel) == 6:
                    break
        else:
            rel = [c for c in by_cat[calc["cat"]] if c["slug"] != calc["slug"] and calculator_group(c) == calculator_group(calc) and is_indexable_calculator(c)][:6]
        rendered = basic_calculator_page(site, calc, rel) if calc["slug"] == "basic-calculator" else calculator_page(site, calc, rel)
        write(DIST / calc["slug"] / "index.html", rendered)
    for source_slug, target_slug in CALCULATOR_REDIRECTS.items():
        target_calc = next((c for c in calculators if c["slug"] == target_slug), None)
        redirect_title = target_calc["title"] if target_calc else smart_title(target_slug.replace("-", " "))
        write(DIST / source_slug / "index.html", redirect_page(site, f"/{source_slug}/", f"/{target_slug}/", redirect_title))

    write(DIST / "scientific-calculator" / "index.html", scientific_page(site))
    for path, html in info_pages(site).items():
        write(DIST / path.strip("/") / "index.html", html)
    write(DIST / "methodology" / "index.html", simple_page(site, "/methodology/", "Methodology", "How NS Calculators chooses, builds, reviews, and links calculator pages.", "<h2>How calculators are selected</h2><p>We prioritize calculators with a distinct user task, measurable search demand, or a clear practical use. Low-demand variations remain available through site search but are not automatically submitted for indexing.</p><h2>Calculation standards</h2><p>Every indexable calculator should provide real inputs, a transparent formula or documented lookup, visible assumptions, a worked example, and relevant internal links. Unit converters use stated conversion factors, while financial tools expose the rates, periods, and recurring costs used in the result.</p><h2>Review and corrections</h2><p>We test representative inputs before publication and review reported errors against authoritative standards or product documentation. For safety-critical, financial, construction, fitment, towing, medical, and electrical decisions, users should verify results with a qualified professional or authoritative source.</p>"))
    write(DIST / "privacy" / "index.html", redirect_page(site, "/privacy/", "/privacy-policy/", "Privacy Policy"))
    write(DIST / "404.html", page(site, "Page Not Found | NS Calculators", "The requested calculator page could not be found.", "/404.html", '<main class="main"><div class="wrap"><article class="article"><h1>Page not found</h1><p class="lead">Try the homepage search to find the calculator you need.</p><a class="btn primary" href="/">Go to homepage</a></article></div></main>', indexable=False))
    write(DIST / "robots.txt", f"User-agent: *\nAllow: /\nSitemap: {site_url(site, '/sitemap.xml')}\n")
    write(DIST / "CNAME", "nscalculators.com\n")
    for verification_file in ROOT.glob("google*.html"):
        shutil.copy2(verification_file, DIST / verification_file.name)

    indexable_calculators = [c for c in calculators if is_indexable_calculator(c)]
    urls = ["/"] + [f"/{slugify_cat(cat)}/" for cat in CATEGORY_ORDER if any(is_indexable_calculator(c) for c in by_cat.get(cat, []))] + [f"/{c['slug']}/" for c in indexable_calculators] + ["/scientific-calculator/", "/about/", "/methodology/", "/privacy-policy/", "/terms/", "/contact/"]
    urls = list(dict.fromkeys(urls))
    sitemap = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    sitemap.extend(f"  <url><loc>{h(site_url(site, u))}</loc></url>" for u in urls)
    sitemap.append("</urlset>")
    write(DIST / "sitemap.xml", "\n".join(sitemap) + "\n")

    keyword_map = [
        {
            "keyword": c["keyword_data"]["keyword"],
            "monthly_searches": c["keyword_data"]["monthly_searches"],
            "competition_index": c["keyword_data"]["competition_index"],
            "category": c["cat"],
            "page": site_url(site, f"/{c['slug']}/"),
        }
        for c in sorted((item for item in calculators if item.get("keyword_data")), key=keyword_score, reverse=True)
    ]
    write(ROOT / "exports" / "keyword-page-map.json", json.dumps(keyword_map, ensure_ascii=False, indent=2) + "\n")

    print(f"Built {len(calculators)} calculator pages; {len(indexable_calculators)} are included in the sitemap.")


if __name__ == "__main__":
    build()

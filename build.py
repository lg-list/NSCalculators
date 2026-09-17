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
ASSET_VERSION = "20260917o"
CALCULATOR_REDIRECTS = {
    "concrete-calculator": "concrete-volume-calculator",
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


def footer():
    return """<footer class="footer"><div class="wrap footer-grid">
<div><a class="brand footer-brand" href="/"><span class="brand-mark">""" + LOGO_MARK + """</span><span class="brand-name"><strong>NS</strong><b>Calculators</b></span></a><p>Practical browser-based tools for US users. Verify critical results with authoritative sources.</p></div>
<div class="footer-links"><a href="/about/">About</a><a href="/privacy-policy/">Privacy Policy</a><a href="/terms/">Terms of Use</a><a href="/contact/">Contact</a></div>
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
    context = f" for {display_group(calculator_group(calc)).lower()}" if calc.get("seo_context_label") else ""
    if calc.get("slug") == "truck-payload-calculator":
        return "Calculate truck payload capacity and remaining payload from GVWR, curb weight, passengers, cargo, and trailer tongue weight."
    if calc.get("slug") == "towing-capacity-calculator":
        return "Estimate safe trailer weight from tow rating, GCWR, GVWR, payload, hitch rating, cargo, passengers, and tongue weight percentage."
    if calc.get("slug") == "mpg-calculator":
        return "Calculate gas mileage from distance and fuel used, with instant US MPG, Imperial MPG, L/100 km, and kilometers-per-liter results."
    if calc.get("slug") == "trip-fuel-cost-calculator":
        return "Estimate one-way or round-trip fuel cost, gallons or liters needed, cost per mile, and each traveler's share in US or metric units."
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


def compound_interest_input_html():
    return """<div class="fields compound-fields">
<div class="field"><label for="principal">Initial investment</label><div class="input-unit"><input id="principal" type="number" step="any" min="0" value="10000"><span>$</span></div></div>
<div class="field"><label for="rate">Annual interest rate</label><div class="input-unit"><input id="rate" type="number" step="any" value="6"><span>%</span></div></div>
<div class="field"><label for="years">Investment length</label><div class="input-unit"><input id="years" type="number" step="1" min="1" value="10"><span>years</span></div></div>
<div class="field"><label for="compound_frequency">Compound frequency</label><select id="compound_frequency"><option value="365">Daily</option><option value="12" selected>Monthly</option><option value="4">Quarterly</option><option value="2">Semi-annually</option><option value="1">Annually</option></select></div>
<div class="field"><label for="monthly">Monthly contribution</label><div class="input-unit"><input id="monthly" type="number" step="any" min="0" value="200"><span>$</span></div></div>
<div class="field"><label for="contribution_timing">Contribution timing</label><select id="contribution_timing"><option value="end" selected>End of month</option><option value="beginning">Beginning of month</option></select></div>
</div>"""


def feet_to_meters_input_html():
    return """<div class="fields feet-meter-fields">
<div class="field field-wide"><label for="conversion_direction">Conversion direction</label><select id="conversion_direction"><option value="feet_to_meters" selected>Feet and inches to meters</option><option value="meters_to_feet">Meters to feet and inches</option></select></div>
<div class="field" data-feet-input><label for="feet">Feet</label><input id="feet" type="number" step="any" value="5"></div>
<div class="field" data-feet-input><label for="inches">Inches</label><input id="inches" type="number" step="any" value="10"></div>
<div class="field field-wide is-hidden" data-meter-input><label for="meters">Meters</label><input id="meters" type="number" step="any" value="1.778"></div>
</div>"""


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
    if calc.get("slug") == "feet-to-meters-calculator":
        return """
<h2>How to convert feet to meters</h2><p>Multiply feet by the exact conversion factor 0.3048. When a measurement includes inches, divide the inches by 12, add that value to the feet, and then multiply the total feet by 0.3048.</p>
<p class="formula">meters = (feet + inches / 12) x 0.3048</p>
<h2>Feet and inches example</h2><p>For 5 feet 10 inches, the calculation is (5 + 10 / 12) x 0.3048 = 1.778 meters. The calculator also reverses meters into feet and remaining inches.</p>
<h2>Common feet to meters conversions</h2><div class="table-scroll"><table class="data-table"><thead><tr><th>Feet</th><th>Meters</th><th>Feet</th><th>Meters</th></tr></thead><tbody><tr><td>1 ft</td><td>0.3048 m</td><td>10 ft</td><td>3.048 m</td></tr><tr><td>3 ft</td><td>0.9144 m</td><td>25 ft</td><td>7.62 m</td></tr><tr><td>5 ft</td><td>1.524 m</td><td>50 ft</td><td>15.24 m</td></tr><tr><td>6 ft</td><td>1.8288 m</td><td>100 ft</td><td>30.48 m</td></tr></tbody></table></div>
<h2>Measurement reference</h2><p>The international foot is exactly 0.3048 meter. The meter is the SI base unit for length; see the <a href="https://www.nist.gov/pml/owm/si-units-length" rel="external noopener">NIST guide to SI length</a> for the official US measurement reference.</p>
<h2>Frequently asked questions</h2><h3>How many meters are in one foot?</h3><p>One foot equals exactly 0.3048 meter.</p><h3>How do I convert meters back to feet?</h3><p>Divide meters by 0.3048. This calculator also separates the decimal result into whole feet and remaining inches.</p>"""
    if calc.get("slug") == "compound-interest-calculator":
        return """
<h2>How compound interest is calculated</h2><p>Compound interest earns a return on the original principal and on interest already added to the balance. This calculator supports daily, monthly, quarterly, semi-annual, and annual compounding plus recurring monthly deposits.</p>
<p class="formula">A = P(1 + r / n)^(nt)</p>
<p>In the formula, P is the starting principal, r is the annual rate as a decimal, n is the number of compounding periods per year, and t is the number of years. Monthly deposits are applied separately at the beginning or end of each month.</p>
<h2>Worked example</h2><p>A $10,000 initial investment earning 6% annually, compounded monthly for 10 years with $200 deposited at the end of every month, grows to about $50,970 before taxes and fees. Of that total, $34,000 is contributed principal and about $16,970 is estimated interest.</p>
<h2>Compounding frequency matters</h2><p>At the same stated annual rate, more frequent compounding produces a slightly higher effective annual yield. The difference is often modest, while contribution size and time invested usually have a larger effect.</p>
<h2>How to use the results</h2><p>Use the annual schedule to see how contributions and interest build over time. The estimate assumes a constant rate and does not include taxes, investment fees, inflation, or market volatility, so it should be used for planning rather than as a guaranteed return.</p>
<h2>Frequently asked questions</h2><h3>What is the difference between APR and APY?</h3><p>APR is a stated annual rate that does not itself show intra-year compounding. APY includes the effect of compounding over a year.</p><h3>Does contribution timing change the answer?</h3><p>Yes. A beginning-of-month contribution has one additional month to earn a return compared with an end-of-month contribution.</p><h3>What is the Rule of 72?</h3><p>Dividing 72 by an annual percentage rate gives a rough estimate of the years needed to double money. It is a shortcut, not an exact projection.</p>"""
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
    if calc.get("slug") == "compound-interest-calculator":
        return """<section class="mortgage-dashboard compound-dashboard" aria-label="Compound interest result details">
<div class="section-head stack"><h2>Growth Summary</h2><p>Compare contributions with estimated interest and review the balance year by year.</p></div>
<div class="summary-grid" id="compoundSummary"></div>
<div class="chart-grid">
<div class="chart-card compact-chart"><h3>Balance Composition</h3><canvas id="compoundPie" width="360" height="190" aria-label="Principal, deposits, and interest chart"></canvas></div>
<div class="chart-card compact-chart"><h3>Balance by Year</h3><canvas id="compoundLine" width="420" height="190" aria-label="Compound interest balance by year chart"></canvas></div>
</div>
<div class="table-card"><h3>Annual Growth Schedule</h3><div class="table-scroll"><table class="data-table" id="compoundSchedule"><thead><tr><th>Year</th><th>Deposits</th><th>Interest</th><th>Ending balance</th></tr></thead><tbody></tbody></table></div></div>
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
    if calc.get("slug") == "feet-to-meters-calculator":
        fields = feet_to_meters_input_html()
        page_engine = "feet_meters"
    elif calc.get("slug") == "compound-interest-calculator":
        fields = compound_interest_input_html()
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
    content = high_value_calculator_copy(calc) or conversion_copy(calc) or default_calculator_copy(calc)
    extra = analysis_extra_html(calc)
    if calc.get("engine") == "loan_page":
        calc_html = f"""<section class="calc loan-page-calc"><h2>Calculator</h2>{fields}<div class="result" id="result">Enter your values and select Calculate.</div></section>"""
    else:
        calc_html = f"""<section class="calc"><h2>Calculator</h2>{fields}<div class="calc-actions"><button class="btn primary calc-btn" data-engine="{h(page_engine)}">Calculate</button><button class="btn secondary clear-btn" type="button" data-clear>Clear</button></div><div class="result" id="result" aria-live="polite">Enter your values and select Calculate.</div></section>"""
    primary_tool = f"""<div class="calculator-layout split-analysis"><div class="calculator-pane">{calc_html}</div><div class="analysis-pane">{extra}</div></div>""" if extra else calc_html
    body = f"""<main class="main"><div class="wrap"><div class="crumb"><a href="/">Home</a> / <a href="/{slugify_cat(calc['cat'])}/">{h(calc['cat'])}</a> / {h(display_group(group))} / {h(calc['title'])}</div>
<article class="article calculator-article"><span class="pill icon-pill">{category_icon(calc["cat"], "pill-icon")}{h(calc['cat'])} calculator</span><div class="page-title-icon">{category_icon(calc["cat"], "title-icon")}<h1>{h(calc['title'])}</h1></div><p class="lead">{h(calc['desc'])}</p>{opportunity_notice(calc)}{keyword_section(calc)}
{primary_tool}
<div class="prose">{content}</div>
<h2>Related calculators</h2><div class="related">{rel}</div></article></div></main><script src="/assets/calculator.js?v={ASSET_VERSION}"></script>"""
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


def scientific_page(site):
    body = f"""<main class="main"><div class="wrap"><article class="article"><div class="crumb"><a href="/">Home</a> / Scientific Calculator</div><span class="pill">Math calculator</span><h1>Scientific Calculator</h1><p class="lead">Run arithmetic, percentages, powers, square roots, trigonometry, and logarithms in your browser.</p><section class="calc scientific-page"><h2>Calculator</h2><div class="mini-calc full"><input id="sciExpression" value="sqrt(144)+25%" aria-label="Scientific expression"><button class="btn primary" id="sciRun" type="button">Calculate</button><div id="sciResult" class="mini-result">Ready</div></div></section><div class="prose"><h2>Supported syntax</h2><p>Use operators such as +, -, *, /, ^, parentheses, percentages, sqrt(), sin(), cos(), tan(), log(), ln(), pi, and e.</p><h2>Example</h2><p>Entering sqrt(144)+25% returns 12.25.</p></div></article></div></main><script src="/assets/scientific.js?v={ASSET_VERSION}"></script>"""
    return page(site, "Scientific Calculator | NS Calculators", "Free browser-based scientific calculator for arithmetic, percentages, powers, roots, trig, and logarithms.", "/scientific-calculator/", body)


def redirect_page(site, from_path, to_path, title):
    return f"""<!doctype html><html lang="{h(site['language'])}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{h(title)}</title><meta http-equiv="refresh" content="0; url={h(to_path)}"><link rel="canonical" href="{h(site_url(site, to_path))}"><meta name="robots" content="noindex"></head><body><p><a href="{h(to_path)}">Continue to {h(title)}</a></p></body></html>"""


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
.input-unit{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;border:1px solid #cfd7e4;border-radius:9px;background:#fff;overflow:hidden}.input-unit input,.input-unit select{border:0!important;border-radius:0!important;height:42px!important}.input-unit input{min-width:0}.input-unit select,.input-unit span{height:42px;display:grid;place-items:center;border-left:1px solid #dfe5ee;background:#f8fafc;color:#344054;padding:0 10px;font-weight:760}.input-unit select{min-width:72px}.field-wide{grid-column:1/-1}.checkline{display:flex!important;align-items:center;gap:10px;min-height:42px;margin:0!important;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:#f8fafc;color:var(--ink);font-size:16px!important}.checkline input{width:18px;height:18px;accent-color:var(--brand)}.mortgage-cost-fields[hidden],.mortgage-cost-fields.is-hidden{display:none!important}.calculator-article:has(#mortgageSummary) .field label{font-size:16px;margin-bottom:4px}.calculator-article:has(#mortgageSummary) .field input,.calculator-article:has(#mortgageSummary) .field select{font-size:16px}.calculator-article:has(#mortgageSummary) .field>input,.calculator-article:has(#mortgageSummary) .field>select{height:42px;padding:0 10px}.calculator-article:has(#mortgageSummary) .mortgage-fields{gap:9px;margin-top:9px}.calculator-article:has(#mortgageSummary) .mortgage-fields:first-child{margin-top:0}
.calc-actions{display:flex;gap:10px;align-items:center;margin-top:14px}.calc-actions .calc-btn{margin-top:0;flex:1}.clear-btn{min-width:92px}.more-options{margin-top:10px;border:1px solid var(--line);border-radius:10px;background:#fff}.more-options summary{min-height:42px;display:flex;align-items:center;padding:0 12px;cursor:pointer;color:var(--brand);font-size:16px;font-weight:850}.more-options summary::marker{color:var(--accent)}.more-options .mortgage-fields{padding:0 12px 12px}.calculator-article:has(#mortgageSummary) .calc-actions{margin-top:10px}.calculator-article:has(#mortgageSummary) .calc-actions .calc-btn,.calculator-article:has(#mortgageSummary) .clear-btn{min-height:42px;font-size:16px;padding:9px 14px}
.loan-mode-stack{display:grid;gap:12px}.loan-mode-input{padding:12px;border:1px solid var(--line);border-radius:12px;background:#f8fafc}.loan-mode-input h3{margin:0 0 4px;font-size:18px;letter-spacing:-.015em}.loan-mode-input p{margin:0 0 10px;color:var(--muted);font-size:13px;line-height:1.35}.loan-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.loan-results{display:grid;gap:14px}.loan-result-panel{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;box-shadow:0 10px 28px rgba(21,32,51,.05)}.loan-result-panel .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:10px 0 12px}.loan-chart-row{display:grid;grid-template-columns:minmax(260px,.9fr) minmax(260px,1fr);gap:12px;align-items:start}.loan-result-table{margin-top:0}.table-toggle{margin-top:10px;border:0;background:transparent;padding:0;cursor:pointer}.is-collapsed{display:none}.calculator-article:has(.loan-results) .calculator-layout.split-analysis{grid-template-columns:minmax(430px,500px) minmax(0,1fr)}.calculator-article:has(.loan-results) .result strong{font-size:30px}.calculator-article:has(.loan-results) .calc{padding:14px}.calculator-article:has(.loan-results) .chart-card canvas{max-height:none}
@media(max-width:1180px){.nav{align-items:center}.navlinks{flex:0 0 auto;overflow:visible;flex-wrap:nowrap;justify-content:flex-end;padding-bottom:0}.category-nav-link{flex:initial}}
@media(max-width:1100px){.category-tools{grid-template-columns:repeat(2,1fr)}}
@media(max-width:900px){.hero-grid,.feature-layout,.proof-grid,.scientific-home,.browse-panel,.scientific-panel,.chart-grid,.calculator-layout.split-analysis,.seo-keywords{grid-template-columns:1fr}.calculator-pane{position:static}.keyword-chip-list{justify-content:flex-start}.category-grid,.tool-grid,.home-category-grid,.popular-list,.summary-grid{grid-template-columns:repeat(2,1fr)}.category-tools{grid-template-columns:repeat(2,1fr)}.directory-links{grid-template-columns:repeat(2,1fr)}.proof-points,.faq-grid,.faq-list,.related{grid-template-columns:1fr 1fr}.search-panel{box-shadow:none}.stats{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){.nav{min-height:64px;gap:10px}.brand{font-size:16px}.brand-mark{width:34px;height:34px}.category-nav-link{padding:6px 7px}.category-nav-link .nav-icon{display:none}.all-calculators-menu .submenu{grid-template-columns:1fr;right:-4px;max-height:72vh;overflow:auto}.hero{padding:32px 0 26px}.hero h1{font-size:36px}.home-hero{padding:30px 0 24px}.home-hero h1{font-size:38px}.hero-actions,.footer-grid,.mini-calc,.mini-calc.full{display:grid;grid-template-columns:1fr}.category-grid,.tool-grid,.home-category-grid,.fields,.directory-links,.proof-points,.faq-grid,.faq-list,.popular-list,.related,.calculator-link-grid,.summary-grid{grid-template-columns:1fr}.section{padding:42px 0}.section.tight,.home-block{padding:28px 0}.section-row{align-items:start}.article h1{font-size:36px}.calculator-article h1{font-size:30px}.calculator-article .lead{font-size:15px;margin-bottom:10px}.calculator-article .calc{padding:14px;margin:10px 0 20px}.calculator-article .calc h2{font-size:20px}.calculator-article .field input,.calculator-article .field select{height:40px}.page-title-icon{align-items:flex-start}.title-icon{width:48px;height:48px}.category-section{padding:18px}.category-section-head{grid-template-columns:1fr}.stats{gap:12px}.carousel{grid-auto-columns:82vw}.sci-keypad{grid-template-columns:repeat(4,1fr)}.ad-slot{min-height:76px}}
@media(max-width:900px){.calculator-article:has(#mortgageSummary) .calculator-layout.split-analysis,.calculator-article:has(.loan-results) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}.calculator-article:has(#mortgageSummary) .analysis-pane .chart-grid,.loan-chart-row{grid-template-columns:minmax(0,1fr)}.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.calculator-pane,.analysis-pane,.chart-card,.table-card,.mortgage-dashboard,.loan-results{min-width:0}}
@media(max-width:560px){.calculator-article:has(#mortgageSummary) .analysis-pane .summary-grid,.loan-result-panel .summary-grid{grid-template-columns:minmax(0,1fr)}}
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
.fitment-fields{gap:8px!important}.tire-size-fields{grid-template-columns:repeat(3,minmax(0,1fr))}.wheel-offset-fields{grid-template-columns:repeat(2,minmax(0,1fr))}.field-group-label{grid-column:1/-1;margin-top:2px;padding-bottom:3px;border-bottom:1px solid var(--line);color:var(--brand);font-size:13px;font-weight:850}.fitment-dashboard .chart-grid{grid-template-columns:1fr}.fitment-dashboard .chart-card canvas{max-height:230px}.calculator-article:has(.fitment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(390px,460px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.fitment-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.fitment-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.tire-size-fields{grid-template-columns:repeat(3,minmax(0,1fr))}.fitment-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.fitment-fields .field-wide{grid-column:1/-1}.fitment-fields .field input{height:36px!important;padding:0 6px}.fitment-fields .input-unit input,.fitment-fields .input-unit span{height:36px!important}.fitment-fields .input-unit span{padding:0 6px;font-size:12px}.field-group-label{margin-top:0;font-size:12px}.calculator-article:has(.fitment-fields) .calc{padding:10px}.calculator-article:has(.fitment-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.fitment-fields) .calc-actions{margin-top:8px}.calculator-article:has(.fitment-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.fitment-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.fitment-fields) .result strong{font-size:23px}.fitment-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.project-fields{gap:8px!important}.project-fields .is-hidden{display:none!important}.project-dashboard .chart-grid{grid-template-columns:1fr}.project-dashboard .chart-card canvas{max-height:230px}.concrete-cost-fields{padding:0 12px 12px}.calculator-article:has(.project-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(390px,460px) minmax(0,1fr)}
@media(max-width:900px){.calculator-article:has(.project-fields) .calculator-layout.split-analysis{grid-template-columns:minmax(0,1fr)}}
@media(max-width:560px){.project-fields{grid-template-columns:repeat(2,minmax(0,1fr));gap:6px!important}.project-fields .field label{min-height:28px;display:flex;align-items:end;font-size:12px!important}.project-fields .field-wide{grid-column:1/-1}.project-fields .field input,.project-fields .field select{height:36px!important;padding:0 6px}.project-fields .input-unit input,.project-fields .input-unit span{height:36px!important}.project-fields .input-unit span{padding:0 6px;font-size:12px}.calculator-article:has(.project-fields) .calc{padding:10px}.calculator-article:has(.project-fields) .calc h2{margin-bottom:6px;font-size:17px}.calculator-article:has(.project-fields) .calc-actions{margin-top:8px}.calculator-article:has(.project-fields) .calc-actions .btn{min-height:36px;padding:7px 10px}.calculator-article:has(.project-fields) .result{padding:9px 10px;font-size:12px}.calculator-article:has(.project-fields) .result strong{font-size:23px}.project-dashboard .summary-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.concrete-cost-fields{grid-template-columns:repeat(2,minmax(0,1fr))}}
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
function show(html){const r=$('#result');if(r)r.innerHTML=html}
function unitValue(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function annualCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100:V(id)}
function monthlyCost(id, base){return document.getElementById(`${id}_unit`)?.value==='percent'?base*V(id)/100/12:V(id)/12}
function monthDate(id){const raw=document.getElementById(id)?.value||'';return /^\d{4}-\d{2}$/.test(raw)?new Date(`${raw}-01T00:00:00`):new Date(raw||Date.now())}
function syncMortgageCosts(){const box=document.getElementById('include_costs'),panel=document.getElementById('mortgageCostFields');if(!box||!panel)return true;const on=box.checked;panel.hidden=!on;panel.classList.toggle('is-hidden',!on);panel.style.display=on?'':'none';return on}
function compoundProjection(){
  const principal=Math.max(0,V('principal')), annual=V('rate')/100, years=Math.max(0,Math.floor(V('years'))), frequency=Math.max(1,V('compound_frequency')||12), monthly=Math.max(0,V('monthly'));
  const timing=document.getElementById('contribution_timing')?.value||'end', months=years*12;
  const monthlyRate=Math.pow(1+annual/frequency,frequency/12)-1;
  let balance=principal,totalInterest=0,totalDeposits=0,yearInterest=0,yearDeposits=0;const schedule=[];
  for(let month=1;month<=months;month++){
    if(timing==='beginning'){balance+=monthly;totalDeposits+=monthly;yearDeposits+=monthly}
    const interest=balance*monthlyRate;balance+=interest;totalInterest+=interest;yearInterest+=interest;
    if(timing!=='beginning'){balance+=monthly;totalDeposits+=monthly;yearDeposits+=monthly}
    if(month%12===0)schedule.push({year:month/12,deposits:yearDeposits,interest:yearInterest,balance});
    if(month%12===0){yearInterest=0;yearDeposits=0}
  }
  return {principal,annual,years,frequency,monthly,timing,balance,totalInterest,totalDeposits,schedule,effectiveAnnual:Math.pow(1+annual/frequency,frequency)-1};
}
function tradeInProjection(){const comparable=Math.max(0,V('comparable')),adjustment=V('market_adjustment'),margin=Math.max(0,V('dealer_margin')),reconditioning=Math.max(0,V('reconditioning')),payoff=Math.max(0,V('payoff')),replacement=Math.max(0,V('replacement_price')),taxRate=Math.max(0,V('tax_rate'))/100,trade=Math.max(0,comparable+adjustment-margin-reconditioning),equity=trade-payoff,taxSavings=Math.min(trade,replacement)*taxRate;return{comparable,adjustment,margin,reconditioning,payoff,replacement,taxRate,trade,equity,taxSavings,effective:trade+taxSavings}}
function usedCarProjection(){const benchmark=Math.max(0,V('retail_benchmark')),condition=V('condition_adjustment'),mileage=V('mileage_adjustment'),options=V('options_adjustment'),regional=V('regional_adjustment'),spread=Math.max(0,Math.min(50,V('dealer_spread'))),retail=Math.max(0,benchmark*(1+condition/100)*(1+regional/100)+mileage+options),privateValue=retail*(1-spread/200),trade=retail*(1-spread/100);return{benchmark,condition,mileage,options,regional,spread,retail,privateValue,trade}}
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
function clearCalcForm(){const form=document.querySelector('.calc');if(!form)return;form.querySelectorAll('input').forEach(input=>{if(input.type==='checkbox')input.checked=false;else input.value=''});form.querySelectorAll('select').forEach(select=>{select.selectedIndex=0});form.querySelectorAll('details').forEach(item=>{item.open=false});syncMortgageCosts();syncConcreteFields();syncRoofFields();syncAreaFields();show('<strong>0</strong><br>Enter values to calculate a new result.');const engine=currentEngine();if(engine==='cn_mortgage')renderMortgage(0,0,1,0,0,0,0,0,0,0,0,0,0,new Date());if(engine==='loan_page')renderLoanPage()}
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
  case'fuel_cost':{let r=V('distance')/Math.max(.01,V('mpg'))*V('fuelprice');show(`<strong>${USD(r)}</strong><br>Estimated fuel cost.`);break}
  case'mpg':{let r=V('gallons')?V('miles')/V('gallons'):0;show(`<strong>${F(r,2)} MPG</strong>`);break}
  case'mpg_advanced':{let distance=V('distance'),fuel=V('fuel_used'),miles=(document.getElementById('distance_unit')?.value==='kilometers'?distance*0.621371192237:distance),liters=fuel*(document.getElementById('fuel_unit')?.value==='us_gallon'?3.785411784:document.getElementById('fuel_unit')?.value==='imperial_gallon'?4.54609:1),usGallons=liters/3.785411784,mpg=usGallons>0?miles/usGallons:0,km=miles/0.621371192237,l100=km>0?liters/km*100:0;show(`<strong>${F(mpg,2)} US MPG</strong><br>${F(l100,2)} L/100 km; ${F(miles/(liters/4.54609),2)} Imperial MPG; ${F(liters?km/liters:0,2)} km/L.`);break}
  case'fuel_cost_advanced':{let metric=document.getElementById('trip_units')?.value==='metric',distance=V('distance')*Math.max(1,V('trip_type'))*Math.max(1,V('trips')),eff=Math.max(.01,V('efficiency')),fuel=metric?distance*eff/100:distance/eff,cost=fuel*V('fuelprice'),currency=document.getElementById('currency')?.value||'USD',people=Math.max(1,V('people'));show(`<strong>${MONEY(cost,currency)}</strong><br>${F(fuel,2)} ${metric?'liters':'US gallons'}; ${MONEY(cost/people,currency)} per person; ${F(distance,0)} ${metric?'km':'miles'} total.`);break}
  case'trade_in_estimate':{const p=tradeInProjection(),equityLabel=p.equity>=0?'positive equity':'negative equity';show(`<strong>${USD(p.trade)} trade-in estimate</strong><br>${USD(Math.abs(p.equity))} ${equityLabel}; ${USD(p.taxSavings)} entered tax benefit; ${USD(p.effective)} effective trade value.`);break}
  case'used_car_estimate':{const p=usedCarProjection();show(`<strong>${USD(p.privateValue)} private-party estimate</strong><br>Adjusted retail: ${USD(p.retail)}; trade-in estimate: ${USD(p.trade)}; review the planning ranges below.`);break}
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
  case'compound':{const p=compoundProjection();show(`<strong>${USD(p.balance)}</strong><br>Total contributions: ${USD(p.principal+p.totalDeposits)}; estimated interest: ${USD(p.totalInterest)}.`);renderCompound(p);break}
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
  case'feet_meters':{let reverse=syncFeetMeterInputs();if(reverse){let meters=V('meters'),totalFeet=meters/0.3048,feet=Math.floor(totalFeet),inches=(totalFeet-feet)*12;show(`<strong>${F(totalFeet,6)} feet</strong><br>${feet} ft ${F(inches,3)} in; ${F(meters,6)} meters.`)}else{let feet=V('feet'),inches=V('inches'),totalFeet=feet+inches/12,meters=totalFeet*0.3048;show(`<strong>${F(meters,6)} meters</strong><br>${F(totalFeet,6)} feet; ${F(totalFeet*12,3)} total inches.`)}break}
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

function drawCompoundLine(canvas, schedule) {
  if (!canvas || !schedule.length) return;
  const ctx=clearCanvas(canvas), pad={left:48,right:18,top:18,bottom:30}, width=canvas.width-pad.left-pad.right, height=canvas.height-pad.top-pad.bottom;
  const points=[Math.max(0,V('principal')),...schedule.map(row=>row.balance)], max=Math.max(...points,1);
  ctx.strokeStyle="#d8e4f1";ctx.lineWidth=1;
  for(let i=0;i<=4;i++){const y=pad.top+height*i/4;ctx.beginPath();ctx.moveTo(pad.left,y);ctx.lineTo(pad.left+width,y);ctx.stroke()}
  ctx.beginPath();points.forEach((value,index)=>{const x=pad.left+width*index/Math.max(1,points.length-1),y=pad.top+height*(1-value/max);if(index===0)ctx.moveTo(x,y);else ctx.lineTo(x,y)});ctx.strokeStyle="#2563eb";ctx.lineWidth=3;ctx.stroke();
  ctx.fillStyle="#52647b";ctx.font="600 11px system-ui, sans-serif";ctx.textAlign="left";ctx.fillText("$0",5,pad.top+height);ctx.fillText(USD(max).replace('.00',''),5,pad.top+9);ctx.fillText("Start",pad.left,canvas.height-8);ctx.textAlign="right";ctx.fillText(`Year ${schedule.length}`,canvas.width-pad.right,canvas.height-8);
}

function renderCompound(projection) {
  const summary=document.getElementById('compoundSummary'), pie=document.getElementById('compoundPie'), line=document.getElementById('compoundLine'), table=document.querySelector('#compoundSchedule tbody');
  if(!summary||!pie||!line||!table)return;
  const contributed=projection.principal+projection.totalDeposits;
  summary.innerHTML=[["Ending balance",USD(projection.balance),"Projected account value."],["Total contributed",USD(contributed),"Initial amount plus deposits."],["Interest earned",USD(projection.totalInterest),"Estimated compound growth."],["Effective annual yield",`${F(projection.effectiveAnnual*100,3)}%`,"Based on selected frequency."]].map(item=>`<div class="summary-card"><span>${item[0]}</span><strong>${item[1]}</strong><small>${item[2]}</small></div>`).join('');
  drawPie(pie,[projection.principal,projection.totalDeposits,projection.totalInterest],["Initial investment","Monthly deposits","Interest"]);
  drawCompoundLine(line,projection.schedule);
  table.innerHTML=projection.schedule.map(row=>`<tr><td>${row.year}</td><td>${USD(row.deposits)}</td><td>${USD(row.interest)}</td><td>${USD(row.balance)}</td></tr>`).join('');
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
  if (engine === "feet_meters") {
    const reverse=document.getElementById('conversion_direction')?.value==='meters_to_feet';
    const meters=reverse?V('meters'):(V('feet')+V('inches')/12)*0.3048, totalFeet=meters/0.3048, wholeFeet=Math.floor(totalFeet), inches=(totalFeet-wholeFeet)*12;
    cards=[["Meters",`${F(meters,6)} m`,"SI length."],["Decimal feet",`${F(totalFeet,6)} ft`,"Feet as a decimal."],["Feet and inches",`${wholeFeet} ft ${F(inches,3)} in`,"US customary format."],["Total inches",`${F(totalFeet*12,3)} in`,"Combined length in inches."]];
    bars=[{label:"Meters",value:meters,display:`${F(meters,4)} m`},{label:"Feet",value:totalFeet,display:`${F(totalFeet,4)} ft`},{label:"Yards",value:totalFeet/3,display:`${F(totalFeet/3,4)} yd`}];
    rows=[["Exact factor","1 ft = 0.3048 m","International foot."],["Meters",F(meters,8),"Calculated metric length."],["Decimal feet",F(totalFeet,8),"Meters divided by 0.3048."],["Feet and inches",`${wholeFeet} ft ${F(inches,4)} in`,"Separated customary units."]];
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
    site = dict(data["site"])
    if PUBLIC_SITE_DOMAIN:
        site["domain"] = PUBLIC_SITE_DOMAIN
    calculators = [c for c in base_and_supplemental(data) if c["slug"] not in CALCULATOR_REDIRECTS]
    if DIST.exists():
        shutil.rmtree(DIST, ignore_errors=True)
    write(DIST / "assets" / "site.css", CSS.strip() + "\n")
    write(DIST / "assets" / "search.js", SEARCH_JS.strip() + "\n")
    write(DIST / "assets" / "home.js", HOME_JS.strip() + "\n")
    write(DIST / "assets" / "scientific.js", SCIENTIFIC_JS.strip() + "\n")
    write(DIST / "assets" / "calculator.js", CALC_JS.strip() + "\n")
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
        rel = [c for c in by_cat[calc["cat"]] if c["slug"] != calc["slug"] and calculator_group(c) == calculator_group(calc) and is_indexable_calculator(c)][:6]
        write(DIST / calc["slug"] / "index.html", calculator_page(site, calc, rel))
    for source_slug, target_slug in CALCULATOR_REDIRECTS.items():
        write(DIST / source_slug / "index.html", redirect_page(site, f"/{source_slug}/", f"/{target_slug}/", "Concrete Calculator"))

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

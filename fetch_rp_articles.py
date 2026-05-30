#!/usr/bin/env python3
"""
Generate the unified Blog hub (content/blog/) from three sources:

  1. Real Python written tutorials  - discovered dynamically from Martin's team
     page (https://realpython.com/team/mbreuss/). Authorship is verified per
     article via the page's JSON-LD `author` field, so tutorials Martin only
     *edited/reviewed* are excluded. Title, publish date and description come
     from each article's JSON-LD / meta tags.

  2. Real Python video courses       - from courses_stats.csv (instructor=mbreuss).
     Descriptions are scraped from each course page; ratings/dates come from the CSV.

  3. Medium archive (2017-2019)       - curated, from medium_posts.json.

Scraped page metadata is cached in rp_meta_cache.json so reruns are fast and
reproducible: the daily GitHub Action only fetches pages it hasn't seen before.
Star ratings are merged in from the CSV snapshots (refresh the CSVs to update them).

Everything in content/blog/ is regenerated from these sources on each run.
"""
import csv
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

AUTHOR_NAME = "Martin Breuss"
TEAM_URL = "https://realpython.com/team/mbreuss/"
BLOG_DIR = Path("content/blog")
CACHE_FILE = Path("rp_meta_cache.json")
POSTS_CSV = Path("posts_stats.csv")
COURSES_CSV = Path("courses_stats.csv")
MEDIUM_JSON = Path("medium_posts.json")

UA = {"User-Agent": "Mozilla/5.0 (compatible; mb-homepage/1.0)"}
REQUEST_DELAY = 1.0  # be polite to realpython.com

# Single-segment slugs on the team page that are navigation, not tutorials.
NAV_SLUGS = {
    "about", "books", "jobs", "contact", "search", "newsletter", "community",
    "account", "quizzes", "courses", "tutorials", "learning-paths", "podcasts",
    "team", "start-here", "mentor", "office-hours", "products", "practice",
    "cheatsheets", "editorial-guidelines", "learner-stories", "ref", "join",
    "sign-in", "sign-up", "python-mentor", "logout", "settings", "bonus",
}

_cache = {}


# --------------------------------------------------------------------------- #
# HTTP + parsing helpers
# --------------------------------------------------------------------------- #
def get(url):
    """Fetch a URL, returning text or None on error."""
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.read().decode("utf-8", "replace")
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  ! fetch failed {url}: {e}")
        return None


def _iter_jsonld(html):
    for block in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S
    ):
        try:
            yield json.loads(block)
        except json.JSONDecodeError:
            continue


def _meta(html, name=None, prop=None):
    if name:
        m = re.search(rf'<meta name="{name}" content="([^"]*)"', html)
    else:
        m = re.search(rf'<meta property="{prop}" content="([^"]*)"', html)
    return m.group(1) if m else None


def scrape_page_meta(url):
    """Return {author, title, date, description} for an RP article/course page.

    Results (including 'author' = None for non-Martin pages) are cached.
    """
    if url in _cache:
        return _cache[url]

    html = get(url)
    time.sleep(REQUEST_DELAY)
    meta = {"author": None, "title": None, "date": None, "description": None}
    if html:
        for d in _iter_jsonld(html):
            if d.get("@type") not in ("Article", "Course"):
                continue
            meta["title"] = d.get("headline") or d.get("name") or meta["title"]
            meta["description"] = d.get("description") or meta["description"]
            dp = d.get("datePublished")
            if dp:
                meta["date"] = _normalize_date(dp)
            author = d.get("author")
            if isinstance(author, dict):
                meta["author"] = author.get("name")
            elif isinstance(author, str):
                meta["author"] = author
        # Fallbacks from <meta> tags
        meta["description"] = meta["description"] or _meta(html, name="description") \
            or _meta(html, prop="og:description")
        meta["title"] = meta["title"] or _meta(html, prop="og:title")

    _cache[url] = meta
    return meta


def _normalize_date(raw):
    """Normalize various ISO-ish date strings to YYYY-MM-DDTHH:MM:SSZ."""
    if not raw:
        return None
    m = re.match(r"(\d{4}-\d{2}-\d{2})[T ]?(\d{2}:\d{2}:\d{2})?", raw)
    if not m:
        return None
    day, t = m.group(1), m.group(2) or "00:00:00"
    return f"{day}T{t}Z"


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text.lower())
    return re.sub(r"[-\s]+", "-", text).strip("-")


# --------------------------------------------------------------------------- #
# Frontmatter writer
# --------------------------------------------------------------------------- #
def write_post(filename, fm, body_lines):
    lines = ["+++"]
    for key, value in fm.items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            lines.append(f"{key} = {str(value).lower()}")
        elif isinstance(value, (int, float)):
            lines.append(f"{key} = {value}")
        elif isinstance(value, list):
            items = ", ".join(f'"{v}"' for v in value)
            lines.append(f"{key} = [{items}]")
        else:
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key} = "{escaped}"')
    lines.append("+++")
    lines.append("")
    lines.extend(body_lines)
    (BLOG_DIR / filename).write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------- #
# CSV rating lookups
# --------------------------------------------------------------------------- #
def load_article_ratings():
    """slug -> (rating, total_count) from posts_stats.csv."""
    ratings = {}
    if not POSTS_CSV.exists():
        return ratings
    for row in csv.DictReader(POSTS_CSV.open(encoding="utf-8")):
        try:
            ratings[row["slug"]] = (
                round(float(row["rating_star_rating"]), 1),
                int(row.get("rating_total_count") or 0),
            )
        except (ValueError, KeyError):
            continue
    return ratings


def load_courses():
    """List of course dicts from courses_stats.csv (instructor=mbreuss)."""
    courses = []
    if not COURSES_CSV.exists():
        return courses
    for row in csv.DictReader(COURSES_CSV.open(encoding="utf-8")):
        if row.get("instructor") not in ("mbreuss", None, ""):
            continue
        try:
            rating = round(float(row["star_rating"]), 1)
        except (ValueError, KeyError):
            rating = None
        courses.append({
            "slug": row["slug"],
            "title": row["title"],
            "date": _normalize_date(row.get("pub_date")) or "2019-01-01T00:00:00Z",
            "rating": rating,
            "skill_level": (row.get("skill_level") or "").strip(),
        })
    return courses


# --------------------------------------------------------------------------- #
# Source builders
# --------------------------------------------------------------------------- #
def discover_article_slugs():
    """Single-segment tutorial slugs linked from the team page."""
    html = get(TEAM_URL)
    if not html:
        print("! Could not load team page; no articles discovered.")
        return []
    slugs = set()
    for href in re.findall(r'href="(/[^"]+)"', html):
        parts = href.strip("/").split("/")
        if len(parts) == 1 and parts[0] and parts[0] not in NAV_SLUGS:
            if re.fullmatch(r"[a-z0-9][a-z0-9-]+", parts[0]):
                slugs.add(parts[0])
    return sorted(slugs)


def build_articles(ratings):
    slugs = discover_article_slugs()
    print(f"Discovered {len(slugs)} candidate article slugs on team page.")
    count = 0
    for slug in slugs:
        url = f"https://realpython.com/{slug}/"
        meta = scrape_page_meta(url)
        if meta.get("author") != AUTHOR_NAME:
            continue  # edited/reviewed by Martin, not authored
        rating, total = ratings.get(slug, (None, None))
        fm = {
            "title": meta["title"] or slug.replace("-", " ").title(),
            "date": meta["date"] or "2024-01-01T00:00:00Z",
            "draft": False,
            "description": meta["description"] or "",
            "externalUrl": url,
            "author": AUTHOR_NAME,
            "source": "Real Python",
            "rating": rating,
            "ratingCount": total,
            "tags": ["python", "real-python"],
            "categories": ["Tutorial"],
        }
        body = [
            meta["description"] or "",
            "",
            f"Read the full tutorial on [Real Python]({url}).",
        ]
        write_post(f"{slug}.md", fm, body)
        count += 1
        print(f"  article: {fm['date'][:10]}  {fm['title'][:55]}"
              + (f"  ({rating}★)" if rating else ""))
    return count


def build_courses():
    courses = load_courses()
    print(f"Loaded {len(courses)} video courses from CSV.")
    count = 0
    for c in courses:
        url = f"https://realpython.com/courses/{c['slug']}/"
        meta = scrape_page_meta(url)
        desc = meta.get("description") or ""
        fm = {
            "title": c["title"],
            "date": meta.get("date") or c["date"],
            "draft": False,
            "description": desc,
            "externalUrl": url,
            "author": AUTHOR_NAME,
            "source": "Video Course",
            "rating": c["rating"],
            "skillLevel": c["skill_level"],
            "tags": ["python", "video-course", "real-python"],
            "categories": ["Video Course"],
        }
        body = [desc, "", f"Watch the full course on [Real Python]({url})."]
        write_post(f"course-{c['slug']}.md", fm, body)
        count += 1
        print(f"  course:  {fm['date'][:10]}  {c['title'][:55]}"
              + (f"  ({c['rating']}★)" if c["rating"] else ""))
    return count


def build_medium():
    if not MEDIUM_JSON.exists():
        return 0
    posts = json.loads(MEDIUM_JSON.read_text(encoding="utf-8"))
    count = 0
    for p in posts:
        slug = slugify(p["title"])[:60] or slugify(p["url"].split("/")[-1])
        desc = p.get("description", "")
        fm = {
            "title": p["title"],
            "date": p["date"],
            "draft": False,
            "description": desc,
            "externalUrl": p["url"],
            "author": AUTHOR_NAME,
            "source": "Medium",
            "tags": ["writing", "medium"],
            "categories": ["Earlier Writing"],
        }
        body = [desc, "", f"Read the full post on [Medium]({p['url']})."]
        write_post(f"medium-{slug}.md", fm, body)
        count += 1
        print(f"  medium:  {p['date'][:10]}  {p['title'][:55]}")
    return count


# --------------------------------------------------------------------------- #
def main():
    global _cache
    BLOG_DIR.mkdir(parents=True, exist_ok=True)
    if CACHE_FILE.exists():
        _cache = json.loads(CACHE_FILE.read_text(encoding="utf-8"))

    # Regenerate the whole blog hub from sources (keep the section index).
    for old in BLOG_DIR.glob("*.md"):
        if old.name != "_index.md":
            old.unlink()

    ratings = load_article_ratings()
    print("== Real Python tutorials ==")
    n_articles = build_articles(ratings)
    print("== Video courses ==")
    n_courses = build_courses()
    print("== Medium archive ==")
    n_medium = build_medium()

    CACHE_FILE.write_text(json.dumps(_cache, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    print(f"\nDone. {n_articles} tutorials + {n_courses} courses + {n_medium} Medium "
          f"= {n_articles + n_courses + n_medium} posts in content/blog/.")


if __name__ == "__main__":
    main()

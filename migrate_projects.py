#!/usr/bin/env python3
"""
Convert projects.json to Hugo markdown files for the projects section.

Project dates are derived from each project's GitHub repository creation date
(`created_at` from the GitHub API) instead of a hardcoded default. Fetched dates
are cached in `project_repo_dates.json` so repeated runs are reproducible and
don't repeatedly hit the API (the unauthenticated limit is 60 requests/hour).
"""
import json
import re
import time
import urllib.request
import urllib.error
from pathlib import Path

CACHE_FILE = Path("project_repo_dates.json")
# Fallback for projects without a real GitHub repo (e.g. xyayz). Kept in the
# ballpark of Martin's early web work so sorting stays sensible.
FALLBACK_DATE = "2017-01-01T00:00:00Z"


def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')


def parse_repo(code_link):
    """Return (owner, repo) parsed from a GitHub code link, or None."""
    m = re.search(r'github\.com/([^/]+)/([^/?#]+)', code_link or '')
    if not m:
        return None
    owner, repo = m.group(1), m.group(2)
    # `github.com/xyayz` parses owner=xyayz with no real repo -> guard known non-repos
    if owner == 'xyayz':
        return None
    return owner, repo


def fetch_created_at(owner, repo):
    """Fetch a repo's created_at from the GitHub API. Returns ISO string or None."""
    api = f"https://api.github.com/repos/{owner}/{repo}"
    req = urllib.request.Request(api, headers={'User-Agent': 'mb-homepage'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.load(resp)
        return data.get('created_at')  # e.g. "2016-12-17T13:27:41Z"
    except urllib.error.HTTPError as e:
        print(f"  ! GitHub API {e.code} for {owner}/{repo}")
    except Exception as e:
        print(f"  ! Error fetching {owner}/{repo}: {e}")
    return None


def get_project_date(project, cache):
    """Resolve a project's date, using and updating the on-disk cache."""
    parsed = parse_repo(project.get('code_link', ''))
    if not parsed:
        return FALLBACK_DATE
    key = f"{parsed[0]}/{parsed[1]}"
    if cache.get(key):
        return cache[key]
    created = fetch_created_at(*parsed)
    time.sleep(0.4)  # be polite to the API
    if created:
        cache[key] = created
        return created
    return FALLBACK_DATE


def migrate_projects():
    """Convert projects.json to Hugo markdown files."""
    projects_json = Path("content/projects/projects.json")
    projects_dir = Path("content/projects")
    projects_dir.mkdir(parents=True, exist_ok=True)

    with open(projects_json) as f:
        projects = json.load(f)

    cache = {}
    if CACHE_FILE.exists():
        cache = json.loads(CACHE_FILE.read_text())

    for project in projects:
        slug = slugify(project['name'])
        date = get_project_date(project, cache)

        frontmatter = {
            'title': project['name'],
            'date': date,
            'draft': False,
            'description': project['description'],
            'technologies': project['technologies'],
        }

        if project.get('image'):
            image_path = project['image'].replace('static/screenshots/', '/images/screenshots/')
            frontmatter['cover'] = image_path

        if project.get('live_link'):
            frontmatter['liveLink'] = project['live_link']
        if project.get('code_link'):
            frontmatter['codeLink'] = project['code_link']
        if project.get('info_link'):
            frontmatter['infoLink'] = project['info_link']

        frontmatter_lines = ['+++']
        for key, value in frontmatter.items():
            if isinstance(value, bool):
                frontmatter_lines.append(f'{key} = {str(value).lower()}')
            elif isinstance(value, str):
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                frontmatter_lines.append(f'{key} = "{escaped}"')
            else:
                frontmatter_lines.append(f'{key} = {value}')
        frontmatter_lines.append('+++')

        content_lines = [
            '\n'.join(frontmatter_lines),
            '',
            project['description'],
            '',
        ]
        if project.get('live_link'):
            content_lines.append(f"**Live:** [{project['live_link']}]({project['live_link']})")
        if project.get('code_link'):
            content_lines.append(f"**Code:** [{project['code_link']}]({project['code_link']})")
        if project.get('info_link'):
            content_lines.append(f"**Info:** [{project['info_link']}]({project['info_link']})")

        project_file = projects_dir / f"{slug}.md"
        project_file.write_text('\n'.join(content_lines) + '\n')
        print(f"Created: {project_file.name}  ({date[:10]})")

    CACHE_FILE.write_text(json.dumps(cache, indent=2, sort_keys=True) + '\n')
    print(f"\nCreated {len(projects)} project files. Cached {len(cache)} repo dates.")


if __name__ == "__main__":
    migrate_projects()

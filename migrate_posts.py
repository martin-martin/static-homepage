#!/usr/bin/env python3
"""
Migrate Pelican blog posts to Hugo format.
Converts Pelican frontmatter to Hugo TOML frontmatter.
"""
import re
from pathlib import Path
from datetime import datetime

def parse_pelican_date(date_str):
    """Convert Pelican date formats to ISO format."""
    # Try ISO format first (2010-12-03 10:20)
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d %H:%M")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    
    # Try "Aug 01, 2022" format
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    
    # Try "Aug 1, 2022" format (no leading zero)
    try:
        dt = datetime.strptime(date_str.strip(), "%b %d, %Y")
        return dt.strftime("%Y-%m-%dT%H:%M:%S")
    except ValueError:
        pass
    
    # Fallback: return as-is
    return date_str.strip()

def migrate_post(pelican_file, hugo_dir):
    """Convert a single Pelican post to Hugo format."""
    content = pelican_file.read_text()
    
    # Parse Pelican frontmatter
    frontmatter = {}
    body_lines = []
    in_frontmatter = True
    
    for line in content.split('\n'):
        if in_frontmatter:
            if line.strip() == '':
                in_frontmatter = False
                continue
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                frontmatter[key.lower()] = value
        else:
            body_lines.append(line)
    
    # Convert to Hugo frontmatter
    hugo_frontmatter = {}
    
    # Title
    if 'title' in frontmatter:
        hugo_frontmatter['title'] = frontmatter['title']
    
    # Date
    if 'date' in frontmatter:
        hugo_frontmatter['date'] = parse_pelican_date(frontmatter['date'])
    
    # Tags
    if 'tags' in frontmatter:
        tags = [t.strip() for t in frontmatter['tags'].split(',')]
        hugo_frontmatter['tags'] = tags
    
    # Categories
    if 'category' in frontmatter:
        hugo_frontmatter['categories'] = [frontmatter['category']]
    
    # Summary/Description
    if 'summary' in frontmatter:
        hugo_frontmatter['description'] = frontmatter['summary']
    
    # External URL (for Real Python articles)
    if 'url' in frontmatter:
        hugo_frontmatter['externalUrl'] = frontmatter['url']
    
    # Author
    if 'author' in frontmatter or 'authors' in frontmatter:
        author = frontmatter.get('author') or frontmatter.get('authors', '')
        hugo_frontmatter['author'] = author
    
    # Draft status (if needed)
    hugo_frontmatter['draft'] = False
    
    # Build Hugo frontmatter string
    frontmatter_lines = ['+++']
    for key, value in hugo_frontmatter.items():
        if isinstance(value, list):
            # Format list as TOML array
            items = ', '.join([f'"{item}"' for item in value])
            frontmatter_lines.append(f'{key} = [{items}]')
        elif isinstance(value, bool):
            frontmatter_lines.append(f'{key} = {str(value).lower()}')
        elif isinstance(value, str):
            # Escape backslashes and quotes properly for TOML
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            frontmatter_lines.append(f'{key} = "{escaped}"')
        else:
            frontmatter_lines.append(f'{key} = {value}')
    frontmatter_lines.append('+++')
    
    # Combine frontmatter and body
    hugo_content = '\n'.join(frontmatter_lines) + '\n\n' + '\n'.join(body_lines).strip() + '\n'
    
    # Write Hugo file
    slug = frontmatter.get('slug', pelican_file.stem)
    hugo_file = hugo_dir / f"{slug}.md"
    hugo_file.write_text(hugo_content)
    
    print(f"Migrated: {pelican_file.name} -> {hugo_file.name}")

def main():
    pelican_posts_dir = Path("content/posts")
    hugo_blog_dir = Path("content/blog")
    
    hugo_blog_dir.mkdir(parents=True, exist_ok=True)
    
    for pelican_file in pelican_posts_dir.glob("*.md"):
        migrate_post(pelican_file, hugo_blog_dir)
    
    print(f"\nMigration complete! Migrated {len(list(pelican_posts_dir.glob('*.md')))} posts.")

if __name__ == "__main__":
    main()


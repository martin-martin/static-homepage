#!/usr/bin/env python3
"""
Generate Hugo markdown files from Real Python articles.
Uses articles.json which contains authored articles from Real Python.
"""
import json
from pathlib import Path
from datetime import datetime
import re

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_slug_from_url(url):
    """Extract slug from Real Python URL."""
    # Remove leading/trailing slashes
    url = url.strip('/')
    # Remove /courses/ prefix if present
    if url.startswith('courses/'):
        url = url.replace('courses/', '')
    return url

def generate_articles():
    """Generate Hugo markdown files from articles.json."""
    articles_json = Path("articles.json")
    external_dir = Path("content/external")
    
    external_dir.mkdir(parents=True, exist_ok=True)
    
    if not articles_json.exists():
        print(f"Error: {articles_json} not found!")
        return
    
    with open(articles_json) as f:
        data = json.load(f)
    
    articles_created = 0
    
    # Process authored articles
    for url_path, title in data.get('authored', []):
        # Skip courses (they end with "(Course)" in the title)
        if title.endswith("(Course)"):
            continue
        
        # Create slug from URL path
        slug = extract_slug_from_url(url_path)
        if not slug:
            slug = slugify(title)
        
        # Build full URL
        full_url = f"https://realpython.com{url_path}"
        
        # Build Hugo frontmatter
        frontmatter = {
            'title': title,
            'date': '2024-01-01T00:00:00Z',  # Default date
            'draft': False,
            'description': f'Real Python article: {title}',
            'externalUrl': full_url,
            'author': 'Martin Breuss',
            'tags': ['python', 'real-python'],
            'categories': ['External'],
        }
        
        frontmatter_lines = ['+++']
        for key, value in frontmatter.items():
            if isinstance(value, list):
                # Format list as TOML array
                items = ', '.join([f'"{item}"' for item in value])
                frontmatter_lines.append(f'{key} = [{items}]')
            elif isinstance(value, bool):
                frontmatter_lines.append(f'{key} = {str(value).lower()}')
            elif isinstance(value, str) and ('"' in value or "'" in value):
                escaped = value.replace('"', '\\"')
                frontmatter_lines.append(f'{key} = "{escaped}"')
            elif isinstance(value, str):
                frontmatter_lines.append(f'{key} = "{value}"')
            else:
                frontmatter_lines.append(f'{key} = {value}')
        frontmatter_lines.append('+++')
        
        # Create content
        content_lines = [
            '\n'.join(frontmatter_lines),
            '',
            f'Read the full article on [Real Python]({full_url}).',
        ]
        
        # Write file
        article_file = external_dir / f"{slug}.md"
        article_file.write_text('\n'.join(content_lines) + '\n')
        
        articles_created += 1
        print(f"Created: {article_file.name}")
    
    print(f"\nCreated {articles_created} article files from articles.json.")

if __name__ == "__main__":
    generate_articles()

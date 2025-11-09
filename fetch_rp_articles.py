#!/usr/bin/env python3
"""
Generate Hugo markdown files from Real Python articles.
Fetches articles from Real Python RSS feed and creates markdown files for new articles.
"""
import feedparser
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import re
import requests
from bs4 import BeautifulSoup
import time

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

def extract_slug_from_url(url):
    """Extract slug from Real Python URL."""
    # Parse URL to get path
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    # Remove /courses/ prefix if present
    if path.startswith('courses/'):
        path = path.replace('courses/', '')
    return path

def format_date_for_hugo(date_tuple):
    """Convert feedparser date tuple to ISO format string."""
    if date_tuple:
        try:
            dt = datetime(*date_tuple[:6])
            return dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        except (ValueError, TypeError):
            pass
    return '2025-01-01T00:00:00Z'  # Default fallback

def fetch_author_from_article(url, author_name):
    """
    Fetch article page and check if the author matches.
    
    Args:
        url: The URL of the article page
        author_name: The name of the author to search for (e.g., "Martin Breuss")
    
    Returns:
        True if author matches, False otherwise
    """
    try:
        # Fetch the article page
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Search for "About {author_name}" text in the page
        # The author section typically contains "About [Author Name]"
        about_pattern = f"About {author_name}"
        
        # Search in all text content
        page_text = soup.get_text()
        if about_pattern.lower() in page_text.lower():
            return True
        
        # Also search in specific elements that might contain author info
        # Look for elements containing "About" and the author name
        for element in soup.find_all(string=lambda text: text and "about" in text.lower()):
            if author_name.lower() in element.lower():
                return True
        
        return False
    
    except requests.RequestException as e:
        print(f"Warning: Could not fetch article page {url}: {e}")
        return False
    except Exception as e:
        print(f"Warning: Error parsing article page {url}: {e}")
        return False

def generate_articles():
    """Generate Hugo markdown files from Real Python RSS feed."""
    rss_url = "https://realpython.com/atom.xml"
    external_dir = Path("content/external")
    author_name = "Martin Breuss"
    
    external_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch and parse RSS feed
    print(f"Fetching RSS feed from {rss_url}...")
    feed = feedparser.parse(rss_url)
    
    if feed.bozo:
        print(f"Warning: Feed parsing had issues: {feed.bozo_exception}")
    
    articles_created = 0
    articles_skipped = 0
    articles_not_authored = 0
    
    # Process feed entries
    for entry in feed.entries:
        title = entry.get('title', '').strip()
        if not title:
            continue
        
        # Get URL from entry
        full_url = entry.get('link', '').strip()
        if not full_url:
            continue
        
        # Check if article is authored by the target author by scraping the page
        print(f"Checking author for: {title}")
        is_author_match = fetch_author_from_article(full_url, author_name)
        
        # Add a small delay between requests to be respectful
        time.sleep(1)
        
        if not is_author_match:
            articles_not_authored += 1
            continue
        
        # Create slug from URL
        slug = extract_slug_from_url(full_url)
        if not slug:
            slug = slugify(title)
        
        # Check if file already exists
        article_file = external_dir / f"{slug}.md"
        if article_file.exists():
            articles_skipped += 1
            continue
        
        # Extract publication date
        published_date = format_date_for_hugo(entry.get('published_parsed'))
        if not published_date or published_date == '2024-01-01T00:00:00Z':
            # Try updated date if published is not available
            published_date = format_date_for_hugo(entry.get('updated_parsed'))
        
        # Build Hugo frontmatter
        frontmatter = {
            'title': title,
            'date': published_date,
            'draft': False,
            'description': f'Real Python article: {title}',
            'externalUrl': full_url,
            'author': author_name,
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
        
        # Create parent directories if they don't exist
        article_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        article_file.write_text('\n'.join(content_lines) + '\n')
        
        articles_created += 1
        print(f"Created: {article_file.name}")
    
    print(f"\nCreated {articles_created} new article files.")
    if articles_skipped > 0:
        print(f"Skipped {articles_skipped} existing articles.")
    if articles_not_authored > 0:
        print(f"Skipped {articles_not_authored} articles not authored by {author_name}.")

if __name__ == "__main__":
    generate_articles()

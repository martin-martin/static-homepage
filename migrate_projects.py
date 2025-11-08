#!/usr/bin/env python3
"""
Convert projects.json to Hugo markdown files for the projects section.
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

def migrate_projects():
    """Convert projects.json to Hugo markdown files."""
    projects_json = Path("content/projects/projects.json")
    projects_dir = Path("content/projects")
    
    # Create projects directory if it doesn't exist
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    with open(projects_json) as f:
        projects = json.load(f)
    
    for project in projects:
        # Create slug from name
        slug = slugify(project['name'])
        
        # Prepare frontmatter
        frontmatter = {
            'title': project['name'],
            'date': '2024-01-01T00:00:00Z',  # Default date, can be updated
            'draft': False,
            'description': project['description'],
            'technologies': project['technologies'],
        }
        
        # Add image path (adjust path for Hugo static directory)
        # Terminal theme uses 'cover' parameter, not 'image'
        if 'image' in project and project['image']:
            # Convert static/screenshots/ to /images/screenshots/
            # Hugo serves files from static/ at the root, so static/images/screenshots/file.png -> /images/screenshots/file.png
            image_path = project['image'].replace('static/screenshots/', '/images/screenshots/')
            frontmatter['cover'] = image_path
        
        # Add links
        if project.get('live_link'):
            frontmatter['liveLink'] = project['live_link']
        if project.get('code_link'):
            frontmatter['codeLink'] = project['code_link']
        if project.get('info_link'):
            frontmatter['infoLink'] = project['info_link']
        
        # Build Hugo frontmatter
        frontmatter_lines = ['+++']
        for key, value in frontmatter.items():
            if isinstance(value, bool):
                frontmatter_lines.append(f'{key} = {str(value).lower()}')
            elif isinstance(value, str):
                # Escape backslashes and quotes properly for TOML
                escaped = value.replace('\\', '\\\\').replace('"', '\\"')
                frontmatter_lines.append(f'{key} = "{escaped}"')
            else:
                frontmatter_lines.append(f'{key} = {value}')
        frontmatter_lines.append('+++')
        
        # Create content
        content_lines = [
            '\n'.join(frontmatter_lines),
            '',
            project['description'],
            ''
        ]
        
        if project.get('live_link'):
            content_lines.append(f"**Live:** [{project['live_link']}]({project['live_link']})")
        if project.get('code_link'):
            content_lines.append(f"**Code:** [{project['code_link']}]({project['code_link']})")
        if project.get('info_link'):
            content_lines.append(f"**Info:** [{project['info_link']}]({project['info_link']})")
        
        # Write file
        project_file = projects_dir / f"{slug}.md"
        project_file.write_text('\n'.join(content_lines) + '\n')
        
        print(f"Created: {project_file.name}")
    
    print(f"\nCreated {len(projects)} project files.")

if __name__ == "__main__":
    migrate_projects()


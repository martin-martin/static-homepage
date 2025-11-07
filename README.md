# Martin Breuss - Static Homepage

A static site built with Hugo and the Terminal theme, featuring a portfolio, blog, and external articles from Real Python.

## Features

- **Portfolio/Projects**: Showcase of 40+ projects with images, descriptions, and GitHub links
- **Blog**: Local markdown blog posts
- **External Articles**: Auto-generated from Real Python articles authored by Martin Breuss
- **Auto-deployment**: GitHub Actions automatically builds and deploys on push to main

## Setup

### Prerequisites

- Hugo (extended version)
- Python 3.11+

### Local Development

1. Clone the repository
2. Install Hugo theme (already included as submodule):
   ```bash
   git submodule update --init --recursive
   ```
3. Generate content:
   ```bash
   python3 fetch_rp_articles.py  # Generate Real Python articles
   ```
4. Run Hugo server:
   ```bash
   hugo server
   ```
5. Visit `http://localhost:1313`

### Building

```bash
hugo --minify
```

The built site will be in the `public/` directory.

## Content Structure

- `content/blog/` - Local blog posts
- `content/projects/` - Portfolio projects (generated from `content/projects/projects.json`)
- `content/external/` - Real Python articles (generated from `articles.json`)
- `content/about.md` - About page
- `content/contact.md` - Contact page
- `static/` - Static assets (images, CSS, etc.)

## Deployment

The site is automatically deployed to GitHub Pages via GitHub Actions when you push to the `main` branch.

### Custom Domain

The site is configured for `martinbreuss.com`. The CNAME file is in `static/CNAME`.

To set up the custom domain:
1. Go to your GitHub repository Settings > Pages
2. Enter `martinbreuss.com` in the Custom domain field
3. Configure DNS records as instructed by GitHub

## Updating Content

### Adding a New Blog Post

Create a new markdown file in `content/blog/` with Hugo frontmatter:

```toml
+++
title = "Your Post Title"
date = "2024-01-01T00:00:00Z"
draft = false
tags = ["python"]
+++

Your content here...
```

### Adding a New Project

Edit `content/projects/projects.json` and add your project, then regenerate:

```bash
python3 migrate_projects.py
```

### Updating Real Python Articles

Update `articles.json` with new articles, then regenerate:

```bash
python3 fetch_rp_articles.py
```

## Migration Scripts

- `migrate_posts.py` - Migrates Pelican blog posts to Hugo format
- `migrate_projects.py` - Converts projects.json to Hugo markdown files
- `fetch_rp_articles.py` - Generates Hugo markdown from Real Python articles

## Theme

Using the [Terminal](https://github.com/panr/hugo-theme-terminal) theme by Panr.

## License

martinmade 2018


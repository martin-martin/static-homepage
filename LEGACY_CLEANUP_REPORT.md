# Legacy Cleanup Report

## Core Hugo Assets (MUST KEEP)

These files and directories are essential for the current Hugo static site:

### Configuration Files
- `hugo.toml` - Main Hugo configuration
- `.gitignore` - Git ignore rules (includes Hugo-specific entries)

### Content Directories
- `content/` - All Hugo content (blog, external, projects, _index.md, contact.md)
- `static/` - Static assets (images, CNAME, favicon.ico)
  - Note: `static/css/` is empty but directory structure may be needed
- `themes/terminal/` - Hugo theme (submodule)

### Deployment
- `.github/workflows/deploy.yml` - Active GitHub Pages deployment workflow
- `articles.json` - Source data for Real Python articles
- `fetch_rp_articles.py` - Script to generate Real Python articles (used in deploy.yml)

### Documentation
- `README.md` - Project documentation (needs updates after cleanup)

## Legacy Artifacts (SAFE TO DELETE)

### Pelican-Specific Files
1. **`Makefile`** - Pelican build system
   - References: Only self-referencing, Pelican-specific commands
   - Status: Not used by Hugo or any current workflows
   - Safe to delete: ✅

2. **`migrate_posts.py`** - Pelican to Hugo migration script
   - References: Mentioned in README.md line 101
   - Status: One-time migration script, no longer needed
   - Safe to delete: ✅ (update README.md)

3. **`pyproject.toml`** - Python project config with Pelican dependency
   - References: None found
   - Status: Contains `pelican[markdown]>=4.11.0` dependency, not needed
   - Note: `fetch_rp_articles.py` uses only standard library
   - Safe to delete: ✅

4. **`uv.lock`** - Lock file for Pelican dependencies
   - References: None found
   - Status: Lock file for pyproject.toml dependencies
   - Safe to delete: ✅ (if pyproject.toml is deleted)

5. **`requirements.txt`** - Python dependencies (empty, mentions Pelican)
   - References: None found
   - Status: Empty file with Pelican comment
   - Safe to delete: ✅

### Firebase Deployment (Old)
6. **`.github/workflows/deploy-to-firebase.yml`** - Old Firebase deployment
   - References: None found
   - Status: Replaced by GitHub Pages deployment (deploy.yml)
   - Safe to delete: ✅

7. **`firebase.json`** - Firebase hosting configuration
   - References: Only referenced by deploy-to-firebase.yml (which is unused)
   - Status: Points to `output` directory (Pelican), not used
   - Safe to delete: ✅

### Unused Project Files
8. **`content/projects/projects-full.json`** - Alternative project format
   - References: None found
   - Status: Projects already migrated to markdown files
   - Safe to delete: ✅

9. **`content/projects/project_types.json`** - Project type definitions
   - References: None found
   - Status: Not referenced by any scripts or Hugo config
   - Safe to delete: ✅

10. **`content/projects/tech.json`** - Technology list
    - References: None found
    - Status: Not referenced by any scripts or Hugo config
    - Safe to delete: ✅

### Temporary/Planning Files
11. **`_plan.md`** - Planning document
    - References: None found
    - Status: Appears to be a temporary planning file
    - Safe to delete: ✅

### Empty Directories
12. **`static/css/`** - Empty CSS directory
    - Status: Empty directory, not needed
    - Safe to delete: ✅

## Files to Keep (But May Need Updates)

- **`migrate_projects.py`** - Still referenced in README.md (line 88)
  - Status: May still be useful for regenerating project markdown files
  - Action: Keep for now, but verify if still needed

## Documentation Updates Required

After deletion, update `README.md`:

1. **Line 101**: Remove mention of `migrate_posts.py`:
   ```markdown
   ## Migration Scripts
   
   - `migrate_posts.py` - Migrates Pelican blog posts to Hugo format  ← DELETE THIS LINE
   - `migrate_projects.py` - Converts projects.json to Hugo markdown files
   - `fetch_rp_articles.py` - Generates Hugo markdown from Real Python articles
   ```

2. **Line 17**: Update Python version requirement (currently says 3.11+, but pyproject.toml requires 3.13+):
   - However, since pyproject.toml will be deleted, this may not be necessary
   - `fetch_rp_articles.py` uses only standard library, so any Python 3.x should work

3. Consider removing or updating the "Migration Scripts" section entirely if `migrate_posts.py` is deleted

## Summary

**Total files/directories to delete: 12**
- 5 Pelican-related files
- 2 Firebase-related files  
- 3 unused project JSON files
- 1 planning file
- 1 empty directory

**Files to keep but verify:**
- `migrate_projects.py` (still referenced in README)

**No Django artifacts found** - The site appears to have been migrated from Pelican, not Django.


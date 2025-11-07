AUTHOR = "Martin Breuss"
SITENAME = "mb/home"
SITEURL = ""

PATH = "content"

TIMEZONE = "Europe/Vienna"
DEFAULT_LANG = "en"

# custom settings
STATIC_PATHS = ["images", "extras", "static"]
EXTRA_PATH_METADATA = {
    "extras/favicon.ico": {"path": "favicon.ico"},
    # 'extras/custom.css': {'path': 'custom.css'},
    "extras/robots.txt": {"path": "robots.txt"},
    "extras/CNAME": {"path": "CNAME"},
    "extras/LICENSE": {"path": "LICENSE"},
    "extras/README": {"path": "README"},
}
CSS_OVERRIDE = [
    # "https://cdn.simplecss.org/simple.min.css",
    # 'static/custom.css'
]

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (
    ("collections", "https://www.datamat.in"),
    ("spacerest", "https://sadieparker.net"),
)

# Social widget
SOCIAL = (
    ("GitHub", "https://github.com/martin-martin/"),
    ("StackOverflow", "https://stackoverflow.com/users/5717580/martin-martin"),
    ("Medium", "https://medium.com/@martin.breuss"),
    ("Real Python", "https://realpython.com/team/mbreuss/"),
    ("Twitter", "https://twitter.com/martinbreuss"),
    ("LinkedIN", "https://www.linkedin.com/in/martinbreuss/"),
)

DEFAULT_PAGINATION = False

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

# THEME = "/Users/martin/Documents/projects/static-homepage/themes/datamatin"
THEME = "Flex"

# Attila theme config
HOME_COVER = "/static/images/waterfall.png"
HOME_COLOR = "white"

AUTHORS_BIO = {
    "datamatin": {
        "name": "Martin Breuss",
        "cover": "https://arulrajnet.github.io/attila-demo/assets/images/avatar.png",
        "image": "https://files.realpython.com/media/martin_breuss_python_square.efb2b07faf9f.jpg?__no_cf_polish=1",
        "website": "https://www.martinbreuss.com",
        "location": "Graz, Austria",
        "bio": "This is the place for a small biography with max 200 characters. Well, now 100 are left. Cool, hugh?",
    }
}

# TODO: undo these dev settings
LOAD_CONTENT_CACHE = False
FILENAME_METADATA = "(?P<title>.*)"
DISPLAY_PAGES_ON_MENU = True

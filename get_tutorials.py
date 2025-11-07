import json
import re
import time
from pathlib import Path
from urllib import request

from loguru import logger
from bs4 import BeautifulSoup

URL = "https://realpython.com/team/mbreuss/"


def main():
    # Uncomment below to scrape posts anew
    info = extract_tutorial_list(scrape_url(URL))
    write_info(info)

    # Uncomment below to write new post files
    info = load_info()
    build_posts(info)


def scrape_url(query_url):
    """Gets HTML content from a web page."""
    req = request.Request(query_url)
    req.add_header(
        "User-Agent",
        (
            "Mozilla/5.0 (Macintosh; "
            "Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/14.1.2 Safari/605.1.15"
        ),
    )
    response = request.urlopen(req)
    raw_data = response.read()
    # encoding = response.info().get_content_charset("utf8")
    logger.info(f"Scraped web content: {raw_data[:10]}...")
    return raw_data


def extract_tutorial_list(profile_page_html):
    """Gets content titles and URLs from my RP profile page."""
    soup = BeautifulSoup(profile_page_html, "html.parser")
    sections = soup.find_all("ul", class_=False)
    all_ul = list()
    for s in sections:
        all_ul.append([(link.a.get("href"), link.text) for link in s.find_all("li")])
        logger.info(f"Extracted section {s}")
    # Filter the articles and courses from the site HTML
    return {"authored": all_ul[0], "contributed": all_ul[1]}


def extract_author_date_description(article_url):
    time.sleep(20)  # Avoid rate limiting
    article_html = scrape_url(article_url)
    soup = BeautifulSoup(article_html, "html.parser")
    meta_info_container = soup.find("span", {"class": "text-muted"}).text
    #breakpoint()
    author = re.search(r"by\s([\w ]+)", meta_info_container).group(1)
    logger.info(f"{author}")
    date = re.search(r"\w+\s\d{1,2},\s\d{4}", meta_info_container).group(0)
    description = soup.find("meta", {"name": "description"})["content"]
    return author, date, description


def build_posts(info):
    POST_PATH = Path().cwd() / "content" / "posts"
    for type, content_list in info.items():
        if type == "authored":
            for article in content_list:
                title = article[1]
                if title.endswith("(Course)"):
                    course = True
                    continue
                course = False
                url = "https://realpython.com" + article[0]
                author, date, description = extract_author_date_description(url)
                fn_string = article[0].strip("/") + ".md"
                file_name = Path(fn_string).name
                file_path = POST_PATH.joinpath(file_name)
                POST_CONTENT = f"""Title: {title}
Category: Python
Date: {date}
Slug: {Path(fn_string).stem}
Tags: python
Author: {author}
Summary: Real Python {'Video Course' if course else 'Article'}

{description}

{'Watch' if course else 'Read'} the full {'video course' if course else 'tutorial'} on Real Python:

[{title}]({url})
"""
                # try:
                file_path.write_text(POST_CONTENT)
                # except FileNotFoundError as e:
                #     print(e)


def write_info(info):
    article_db_path = Path().cwd() / "articles.json"
    jsonified_info = json.dumps(info)
    article_db_path.write_text(jsonified_info)
    return f"Articles written to {article_db_path}"


def load_info():
    article_db_path = Path().cwd() / "articles.json"
    with open(article_db_path) as in_file:
        info = json.load(in_file)
    return info


if __name__ == "__main__":
    main()

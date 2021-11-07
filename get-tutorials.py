from pathlib import Path
from urllib import request

from bs4 import BeautifulSoup


URL = "https://realpython.com/team/mbreuss/"


def get_tutorials(query_url):
    """Gets RP tutorials from my profile page."""
    req = request.Request(URL)
    req.add_header("User-Agent",
                   ("Mozilla/5.0 (Macintosh; "
                    "Intel Mac OS X 10_15_7) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) "
                    "Version/14.1.2 Safari/605.1.15")
                   )
    response = request.urlopen(req)
    raw_data = response.read()
    # encoding = response.info().get_content_charset("utf8")
    return raw_data


def extract_info(content):
    soup = BeautifulSoup(content, "html.parser")
    sections = soup.find_all("ul")
    all_ul = list()
    for s in sections:
        all_ul.append([(link.a.get("href"), link.text)
                        for link in s.find_all("li")])
    # Filter the articles and courses from the site HTML
    return {"authored": all_ul[-2], "contributed": all_ul[-1]}


def build_posts(info):
    POST_PATH = Path().cwd() / "content" / "posts"
    for type, content_list in info.items():
        if type == "authored":
            for article in content_list:
                url = "https://realpython.com/" + article[0]
                title = article[1]
                fn_string = article[0].strip("/") + ".md"
                file_name = Path(fn_string).name
                file_path = POST_PATH.joinpath(file_name)
                POST_CONTENT =f"""Title: {title}
Category: Python
Date: 2010-12-03 10:20
Modified: 2010-12-05 19:30
Slug: {Path(fn_string).stem}
Tags: python
Authors: Martin Breuss
Summary: Real Python Article
Url: {url}

Read or watch my tutorial over at _Real Python_."""
                # try:
                file_path.write_text(POST_CONTENT)
                # except FileNotFoundError as e:
                #     print(e)



if __name__ == "__main__":
    info = extract_info(get_tutorials(URL))
    build_posts(info)

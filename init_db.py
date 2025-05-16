import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import re
import random

client = MongoClient("mongodb://root:pwd1234@my-db:27018")
db = client.favoriteMovie


def init():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"
    }
    data = requests.get(
        "https://search.daum.net/search?w=tot&q=역대관객순위&DA=MOR&rtmaxcoll=MOR",
        headers=headers,
    )
    soup = BeautifulSoup(data.text, "html.parser")

    movies = soup.select("c-list-doc > c-doc")

    for movie in movies:

        posterElement = movie.select_one("c-thumb")
        if not posterElement:
            print("No poster element found")
            # continue

        posterUrl = posterElement["data-original-src"]

        titleElement = movie.select_one("c-title")
        if not titleElement:
            print("No movie element found")
            # continue

        title = titleElement.string.strip()

        infoUrlParam = titleElement["data-href"]

        infoUrl = f"https://search.daum.net/search{infoUrlParam}"

        viewerElement = movie.select_one("c-contents-desc")
        if not viewerElement:
            print("No viewer element found")
            # continue
        viewers = viewerElement.string.strip()
        viewers = parse_viewers_text_to_int(viewers)

        openDateElement = movie.select_one("c-contents-desc-sub")
        if not openDateElement:
            print("No open date element found")
            # continue
        openDate = openDateElement.string.strip()
        openDate = openDate.replace(".", " ").strip()
        openDate = openDate.replace(" ", ".")
        (openYear, openMonth, openDay) = openDate.split(".")

        likes = random.randrange(0, 1000)

        doc = {
            "title": title,
            "posterUrl": posterUrl,
            "infoUrl": infoUrl,
            "viewers": viewers,
            "openYear": openYear,
            "openMonth": openMonth,
            "openDay": openDay,
            "likes": likes,
            "trashed": False,
        }

        db.movies.insert_one(doc)
        print("Movie inserted:", doc)


def parse_viewers_text_to_int(viewers):
    viewers = viewers.replace("만명", "0,000")
    viewers = re.findall(r"[0-9]+", viewers)
    viewers = "".join(viewers)
    return int(viewers)


if __name__ == "__main__":
    db.movies.drop()

    init()

"""
Scrapbox doesn't have official write API. Use import API instead.
"""

import requests
import dotenv
import json
import os

dotenv.load_dotenv()
SID = os.getenv("SID")
PROJECT = os.getenv("PROJECT_NAME")


API_ME = "https://scrapbox.io/api/users/me"
import_api_url = f"https://scrapbox.io/api/page-data/import/{PROJECT}.json"


def write_pages(pages):
    if pages == []:
        print("no pages to write")
        return
    cookie = "connect.sid=" + SID
    r = requests.get(API_ME, headers={"Cookie": cookie})
    r.raise_for_status()
    csrfToken = r.json()["csrfToken"]

    data = json.dumps({"pages": pages})
    r = requests.post(
        import_api_url,
        files={"import-file": data},
        headers={
            "Cookie": cookie,
            "Accept": "application/json, text/plain, */*",
            "X-CSRF-TOKEN": csrfToken,
        },
    )
    r.raise_for_status()


def _test():
    pages = [{"title": "Scbot Home", "lines": ["Scbot Home", "Hello world!"]}]
    write_pages(pages)


if __name__ == "__main__":
    _test()

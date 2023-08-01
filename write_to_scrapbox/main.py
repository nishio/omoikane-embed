import requests
import dotenv
import json
import os
import generate_pages

dotenv.load_dotenv()
SID = os.getenv("SID")

project = "omoikane"


API_ME = "https://scrapbox.io/api/users/me"
API_IMPORT = "https://scrapbox.io/api/page-data/import/{project}.json"


def write_pages(pages):
    cookie = "connect.sid=" + SID
    r = requests.get(API_ME, headers={"Cookie": cookie})
    r.raise_for_status()
    csrfToken = r.json()["csrfToken"]

    url = API_IMPORT.format(project=project)
    data = json.dumps({"pages": pages})
    r = requests.post(
        url,
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


def main(dry=False):
    pages = generate_pages.main()
    write_pages(pages)
    print("write ok")


if __name__ == "__main__":
    main()

import requests
from dotenv import load_dotenv
import json
import os
import time

load_dotenv()

project = "omoikane"

API_ME = "https://scrapbox.io/api/users/me"
API_IMPORT = "https://scrapbox.io/api/page-data/import/{project}.json"


def write_pages(pages):
    sid = os.getenv("SID")

    cookie = "connect.sid=" + sid
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
    title = "🤖Omoikane Embed" + time.strftime("%Y-%m-%d_%H:%M:%S")
    lines = [title]
    lines.append("automatic report from omoikane-embed")
    lines.append("JSON size: {}".format(os.path.getsize("omoikane.json")))
    lines.append("pickle size: {}".format(os.path.getsize("omoikane.pickle")))

    if dry:
        print("\n".join(lines))
        return

    pages = [{"title": title, "lines": lines}]
    write_pages(pages)


if __name__ == "__main__":
    main()

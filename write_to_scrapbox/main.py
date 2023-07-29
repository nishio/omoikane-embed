import requests
from dotenv import load_dotenv
import json
import os
import time
import openai
import io

project = "omoikane"

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

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


PROMPT = """You are a member of this community. Read following information. Make human-friendly report in Japanese. Constraint: Explain basic infomation. Explain digest of some interesting updated pages. You can add why it is interesting. And then add your opinion or question.
### Basic information
Exported timestamp: {exported}
JSON size: {json_size}
Pickle size: {pickle_size}
Titles of updated pages: {titles}
### contents of updated pages
{digest_str}
"""

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))


def main(dry=False):
    output_page_title = "🤖Omoikane Embed" + time.strftime("%Y-%m-%d_%H:%M:%S")
    lines = [output_page_title]
    json_size = os.path.getsize("omoikane.json")
    pickle_size = os.path.getsize("omoikane.pickle")

    data = json.load(open("omoikane.json"))
    exported = data["exported"]
    # one day limit
    limit = exported - 60 * 60 * 24
    updated_pages = {}
    for page in data["pages"]:
        if page["updated"] < limit:
            continue
        if "🤖" in page["title"]:
            continue
        updated_pages[page["title"]] = page

    # take 2000 tokens digests
    digests = []
    num_updated_pages = len(updated_pages)
    block_size = 2000 / num_updated_pages
    for title, page in updated_pages.items():
        header = ""
        buf = []
        for line in page["lines"]:
            buf.append(line)
            body = "\n".join(buf)
            if get_size(body) > block_size:
                buf.pop(-1)
                header = "\n".join(buf)
                break

        footer = ""
        buf = []
        for line in reversed(page["lines"]):
            buf.append(line)
            body = "\n".join(buf)
            if get_size(body) > block_size:
                buf.pop(-1)
                footer = "\n".join(reversed(buf))
                break

        digest = f"# {title}\n{header}\n...\n{footer}\n"
        print(digest)
        digests.append(digest)

    titles = ", ".join(updated_pages.keys())
    digest_str = "\n".join(digests)

    prompt = PROMPT.format(**locals())
    print(prompt)
    messages = [{"role": "system", "content": prompt}]
    # model = "gpt-3.5-turbo"
    model = "gpt-4"
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0.0,
            # max_tokens=max_tokens,
            n=1,
            stop=None,
        )
        ret = response.choices[0].message.content.strip()
        lines.extend(ret.split("\n"))
    except Exception as e:
        lines.append("Failed to generate report.")
        lines.append(str(e))
        lines.append("Prompt:")
        lines.extend(prompt.split("\n"))

    pages = [{"title": output_page_title, "lines": lines}]
    print("\n".join(lines))
    if dry:
        print("dry run")
        return
    write_pages(pages)
    print("write ok")


if __name__ == "__main__":
    main()

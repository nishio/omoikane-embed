import dotenv
import openai
import time
import os
import json
import datetime
import random

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT = os.getenv("PROJECT_NAME")
assert OPENAI_API_KEY and PROJECT
openai.api_key = OPENAI_API_KEY

PROMPT = """You are a member of this community. Read following information. Make human-friendly report in Japanese as bullet lists. Constraint: Refer the title of some interesting pages in `[title]` style. You should explain why those are interesting. And then add your opinions and questions. You should ask at least one question.
### contents of updated pages
{digest_str}
"""

import tiktoken

enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))

def make_digest(title, page, block_size):
    header = ""
    buf = []
    lines = page["lines"][:]
    for line in lines:
        buf.append(lines.pop(0))
        body = "\n".join(buf)
        if get_size(body) > block_size:
            buf.pop(-1)
            header = "\n".join(buf)
            break
    else:
        header = "\n".join(buf)
        digest = f"# {title}\n{header}\n"
        return digest

    if "雑談ページ" in title:
        header = ""

    header_size = get_size(header)
    footer = ""
    buf = []
    for line in reversed(lines):
        buf.append(line)
        body = "\n".join(buf)
        if get_size(body) + header_size > block_size * 2:
            buf.pop(-1)
            footer = "\n".join(reversed(buf))
            break
    else:
        digest = f"# {title}\n{header}\n{footer}\n"
        return digest


    digest = f"# {title}\n{header}\n...\n{footer}\n"
    return digest


def get_updated_pages(data, span=60 * 60 * 24):
    exported = data["exported"]
    limit = exported - span
    updated_pages = {}
    for page in data["pages"]:
        if page["updated"] < limit:
            continue
        if any(x in page["title"] for x in ["🤖", "ネタバレ注意"]):
            continue
        updated_pages[page["title"]] = page
    return updated_pages


def get_random_pages(data, num=4):
    target_pages = {}
    for page in data["pages"]:
        if any(x in page["title"] for x in ["🤖", "ネタバレ注意"]):
            continue
        target_pages[page["title"]] = page
    keys = list(target_pages.keys())
    random.shuffle(keys)
    target_pages = {k: target_pages[k] for k in keys[:num]}
    return target_pages


def main():
    # make title
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d")
    output_page_title = "🤖" + date

    lines = [output_page_title]
    json_size = os.path.getsize(f"{PROJECT}.json")
    pickle_size = os.path.getsize(f"{PROJECT}.pickle")

    data = json.load(open(f"{PROJECT}.json"))
    target_pages = get_random_pages(data)

    # take 2000 tokens digests
    digests = []
    num_target_pages = len(target_pages)
    block_size = 2000 / num_target_pages
    for title, page in target_pages.items():
        digests.append(make_digest(title, page, block_size))

    titles = ", ".join(target_pages.keys())
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


    # extra info
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines.append("")
    lines.append("[* extra info]")
    lines.append("date: " + date)
    lines.append("json size: " + str(json_size))
    lines.append("pickle size: " + str(pickle_size))
    lines.append("titles: " + titles)
    lines.append("num_target_pages: " + str(num_target_pages))

    pages = [{"title": output_page_title, "lines": lines}]
    return pages


if __name__ == "__main__":
    pages = main()
    for page in pages:
        print(page["title"])
        print("\n".join(page["lines"]))
        print()

import dotenv
import openai
import time
import os
import json
import datetime

dotenv.load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
PROJECT = os.getenv("PROJECT_NAME")

PROMPT = """You are a member of this community. Read following information. Make human-friendly report in Japanese. Constraint: Explain digest of some interesting updated pages. You should explain why those are interesting. And then add your opinions and questions. You should ask at least one question.
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


def main():
    date = datetime.datetime.now() + datetime.timedelta(days=1)
    date = date.strftime("%Y-%m-%d")
    output_page_title = "🤖" + date
    lines = [output_page_title]
    json_size = os.path.getsize(f"{PROJECT}.json")
    pickle_size = os.path.getsize(f"{PROJECT}.pickle")

    data = json.load(open(f"{PROJECT}.json"))
    exported = data["exported"]
    # one day limit
    limit = exported - 60 * 60 * 24
    updated_pages = {}
    for page in data["pages"]:
        if page["updated"] < limit:
            continue
        if any(x in page["title"] for x in ["🤖", "ネタバレ注意"]):
            continue
        updated_pages[page["title"]] = page

    # take 2000 tokens digests
    digests = []
    num_updated_pages = len(updated_pages)
    block_size = 2000 / num_updated_pages
    for title, page in updated_pages.items():
        digests.append(make_digest(title, page, block_size))

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

    lines.append("")
    lines.append("[* extra info]")
    lines.append("json size: " + str(json_size))
    lines.append("pickle size: " + str(pickle_size))
    lines.append("titles: " + titles)
    lines.append("num_updated_pages: " + str(num_updated_pages))

    pages = [{"title": output_page_title, "lines": lines}]
    return pages


if __name__ == "__main__":
    pages = main()
    for page in pages:
        print(page["title"])
        print("\n".join(page["lines"]))
        print()

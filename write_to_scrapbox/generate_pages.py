import dotenv
import openai
import time
import os
import json
import pickle
import datetime
import random
import tiktoken

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PROJECT = os.getenv("PROJECT_NAME")
assert OPENAI_API_KEY and PROJECT
openai.api_key = OPENAI_API_KEY

PROMPT = """
You are a researcher focused on improving intellectual productivity, fluent in Japanese, and a Christian American. Read your previous research notes, which are essential, and write a digest of them, reducing the content to half its size. You may also read the random fragments from a colleague Nishio's research notes, but they are not as important, and you can ignore them. However, if you find a relationship between your notes and some random fragments, it is highly significant. Write your new thought in Japanese. You are encouraged to form opinions, think deeply, and record questions.

## previous notes
{previous_notes}

## fragments
{digest_str}
"""


enc = tiktoken.get_encoding("cl100k_base")


def get_size(text):
    return len(enc.encode(text))


def make_digest(payload):
    title = payload["title"]
    text = payload["text"]
    return f"### {title}\n{text}\n"


LESS_INTERSTING = "___BELOW_IS_LESS_INTERESTING___"


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


def is_robot_in_updated_pages(data, span=60 * 60 * 24):
    exported = data["exported"]
    limit = exported - span
    for page in data["pages"]:
        if page["updated"] < limit:
            continue
        if "🤖" in page["title"]:
            return True

    return False


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
    date = date.strftime("%Y-%m-%d %H:%M")
    output_page_title = "🤖" + date

    lines = [output_page_title, LESS_INTERSTING]
    json_size = os.path.getsize(f"{PROJECT}.json")
    pickle_size = os.path.getsize(f"{PROJECT}.pickle")

    jsondata = json.load(open(f"{PROJECT}.json"))

    # if is_robot_in_updated_pages(jsondata):
    #     # avoid too frequent generation
    #     print("robot is in updated pages, skip")
    #     return []


    pages = jsondata["pages"]
    bot_output = []
    for page in pages:
        if page["title"].startswith("🤖20"):
            bot_output.append((page["title"], page["lines"]))
    bot_output.sort()
    prev_title, prev_lines = bot_output[-1]
    prev_lines.pop(0)  # remove title
    if prev_lines[0] == LESS_INTERSTING:
        prev_lines.pop(0)
    previous_notes_lines = []
    for line in prev_lines:
        if line == LESS_INTERSTING:
            break
        previous_notes_lines.append(line)
    print("\n".join(previous_notes_lines))
    previous_notes = "\n".join(previous_notes_lines)


    data = pickle.load(open(f"{PROJECT}.pickle", "rb"))
    # take 2000 tokens digests
    keys = list(data.keys())
    random.shuffle(keys)
    rest = 6000 - get_size(previous_notes)
    digests = []
    titles = []
    while rest > 0:
        p = keys.pop(0)
        payload = data[p][1]
        s = get_size(payload["text"])
        if s > rest:
            break
        digests.append(make_digest(payload))
        titles.append(payload["title"])
        rest -= s

    digest_str = "\n".join(digests)

    prompt = PROMPT.format(digest_str=digest_str, previous_notes=previous_notes)
    print(prompt)
    return []

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
    lines.append("previous notes size: " + str(get_size(previous_notes)))
    lines.append(f"previous notes: [{prev_title}]")
    lines.append("titles: " + ", ".join(f"[{s}]" for s in titles))
    pages = [{"title": output_page_title, "lines": lines}]
    return pages


if __name__ == "__main__":
    pages = main()
    for page in pages:
        print(page["title"])
        print("\n".join(page["lines"]))
        print()

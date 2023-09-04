import re
import unittest

# old format marker to separate AI generated notes
LESS_INTERESTING = "___BELOW_IS_LESS_INTERESTING___"
# new format marker to separate AI generated notes (from iterarive commenter)
AI_GENERATED_MARKER = "__BELOW_IS_AI_GENERATED__"


EXTRA_INFO_HEADER = "[* extra info]"
MICROFORMAT_IGNORE = "`AI_IGNORE"
MICROFORMAT_TO_AI = "`TO_AI:"

TEST_for_markdown_to_scrapbox = "### A is level 3 header\n## B is level 2 header"


def markdown_to_scrapbox(text):
    """easy conversion from markdown to scrapbox
    >>> print(markdown_to_scrapbox(TEST_for_markdown_to_scrapbox))
    [* A is level 3 header]
    [** B is level 2 header]
    """
    # Replace '### ' with '[* ' and close with ']'
    text = re.sub(r"### (.+)", r"[* \1]", text)
    # Replace '## ' with '[** ' and close with ']'
    text = re.sub(r"## (.+)", r"[** \1]", text)
    return text


def extract_microformat_to_ai(input_str):
    """
    Extracts text enclosed between `TO_AI:` and backticks from the input string.

    Args:
        input_str (str): The input string containing the target text.

    Returns:
        str: The extracted text, or None if no match is found.

    Examples:
        >>> extract_microformat_to_ai("aaa`TO_AI: bbb`ccc")
        'bbb'

        >>> extract_microformat_to_ai("Some text without TO_AI")
        ...
    """
    pattern = r"`TO_AI: (.*?)`"
    match = re.search(pattern, input_str)
    if match:
        extracted_text = match.group(1)
        return extracted_text
    else:
        return None


def extract_previous_notes(prev_lines, version=1):
    """
    Extracts previous notes from a list of lines, filtering out less interesting and extra information headers.

    Args:
        prev_lines (list): List of lines containing previous notes and related information.

    Returns:
        str: A string containing the extracted previous notes.

    Raises:
        NotImplementedError: If a microformat TO_AI line is encountered.
    """
    if not prev_lines:
        return ""  # this does not happen, because even empty page has title line

    # Remove title line
    prev_lines.pop(0)

    if not prev_lines:
        # empty page
        return ""

    # Check if the first line is less interesting, and skip if needed
    if prev_lines[0] == LESS_INTERESTING:
        prev_lines.pop(0)

    previous_notes_lines = []
    to_ai = []

    # Extract previous notes lines until less interesting, extra info header, or microformat is encountered
    for line in prev_lines:
        if line == LESS_INTERESTING:
            # check if the previous notes is empty (if there are only empty lines, it is empty)
            body = "".join(previous_notes_lines).strip()
            if body:
                break
            # if the previous notes is empty, continue to pick less interesting lines
            previous_notes_lines = []
            continue
        if line == AI_GENERATED_MARKER:
            break
        if line == EXTRA_INFO_HEADER:
            break
        if MICROFORMAT_IGNORE in line:
            continue
        if "[*** 🤖" in line:  # section header of previous notes
            continue  # ignore
        if MICROFORMAT_TO_AI in line:
            prompt = extract_microformat_to_ai(line)
            to_ai.append(prompt)

        previous_notes_lines.append(line)

    # Combine extracted lines into a string
    previous_notes = "\n".join(previous_notes_lines)

    if version == 1:
        return previous_notes

    return previous_notes


class TestExtractPreviousNotes(unittest.TestCase):
    def test_extract_previous_notes(self):
        prev_lines = [
            "Title",
            LESS_INTERESTING,
            "Some notes...",
            EXTRA_INFO_HEADER,
            "More notes...",
        ]

        extracted_notes = extract_previous_notes(prev_lines)

        expected_notes = "Some notes..."
        self.assertEqual(extracted_notes, expected_notes)

    def test_extract_previous_notes_ignore(self):
        prev_lines = [
            "Title",
            LESS_INTERESTING,
            "Some notes...",
            "`AI_IGNORE: This line should be ignored`",
            EXTRA_INFO_HEADER,
            "More notes...",
        ]

        extracted_notes = extract_previous_notes(prev_lines)

        expected_notes = "Some notes..."
        self.assertEqual(extracted_notes, expected_notes)

    def test_extract_previous_notes_with_microformat(self):
        prev_lines = [
            "Title",
            "AAA",
            LESS_INTERESTING,
            "BBB",
            EXTRA_INFO_HEADER,
            "More notes...",
        ]

        extracted_notes = extract_previous_notes(prev_lines)

        expected_notes = "AAA"
        self.assertEqual(extracted_notes, expected_notes)

    def test_(self):
        prev_lines = [
            "Title",
            "   ",
            LESS_INTERESTING,
            "BBB",
            EXTRA_INFO_HEADER,
            "More notes...",
        ]

        extracted_notes = extract_previous_notes(prev_lines)

        expected_notes = "BBB"
        self.assertEqual(extracted_notes, expected_notes)


def parse_titles(line):
    """
    Extracts titles from a line.

    Args:
        line (str): The line containing the titles.

    Returns:
        list: A list of titles.


    New better format:
    >>> parse_titles('titles: `["aaa", "ううう", "1,2,3"]`')
    ['aaa', 'ううう', '1,2,3']
    >>> parse_titles('titles: `["X:Y"]`')
    ['X:Y']

    old format(it may ambiguous when title contains comma):
    >>> parse_titles("titles: A, B, C")
    ['A', ' B', ' C']

    """
    import json

    body = line.split(":", 1)[1].strip()
    try:
        if body.startswith("`"):
            titles = json.loads(body[1:-1])
            return titles
    except Exception as e:
        print(e)
        pass
    titles = body.split(",")
    return titles


def get_api_url(url):
    """
    >>> get_api_url("https://scrapbox.io/nishio/example")
    'https://scrapbox.io/api/pages/nishio/example'
    """
    api_url = re.sub(
        r"(https://scrapbox\.io)/([^/]+)/([^/]+)", r"\1/api/pages/\2/\3", url
    )
    return api_url


if __name__ == "__main__":
    import doctest

    doctest.testmod()

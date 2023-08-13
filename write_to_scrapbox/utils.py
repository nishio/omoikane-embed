import re

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


if __name__ == "__main__":
    import doctest

    doctest.testmod()

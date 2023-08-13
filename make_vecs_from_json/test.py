import pickle
import os
import dotenv

dotenv.load_dotenv()
PROJECT = os.environ.get("PROJECT_NAME")
assert PROJECT

def update_from_scrapbox_json(name, json_name, is_public=False):
    "mock"
    assert os.path.isfile(json_name)
    import main

    vs = main.VectorStore(name, create_if_not_exist=True)
    for k in vs.cache:
        vec_, payload = vs.cache[k]
        # format check
        assert isinstance(payload["project"], str)
        assert isinstance(payload["title"], str)
        assert isinstance(payload["text"], str)
        assert isinstance(payload["is_public"], bool)
    vs.cache = {}  # delete cache, because it is test with small data

    payload = {
        "title": "MOCK TEST",
        "project": PROJECT,
        "text": "MOCK TEST",
        "is_public": True,
    }

    api_tasks = [("MOCK TEST", payload)]
    vs.batch(api_tasks, {})
    vs.save()


if __name__ == "__main__":
    PAGE_LIMIT = 0
    update_from_scrapbox_json(
        f"{PROJECT}.pickle",
        f"{PROJECT}.json",
        is_public=True,
    )
    print(f"OK, wrote {PROJECT}.pickle")

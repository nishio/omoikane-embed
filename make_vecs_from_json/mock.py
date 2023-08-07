import pickle
import os


def update_from_scrapbox_json(name, json_name, is_public=False):
    "mock"
    assert os.path.isfile(json_name)
    import main

    vs = main.VectorStore(name, create_if_not_exist=True)
    payload = {
        "title": "MOCK TEST",
        "project": project,
        "text": "MOCK TEST",
        "is_public": True,
    }

    api_tasks = [("MOCK TEST", payload)]
    vs.batch(api_tasks, {})
    vs.save()


if __name__ == "__main__":
    PAGE_LIMIT = 0
    # `project` is global variable and used to make payload for scrapbox
    project = "omoikane"
    update_from_scrapbox_json(
        "omoikane.pickle",
        "omoikane.json",
        is_public=True,
    )

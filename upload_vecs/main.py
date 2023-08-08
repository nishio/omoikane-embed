from qdrant_client.http.models import PointStruct
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import Distance, VectorParams
from qdrant_client.http.models import Filter, FieldCondition, MatchValue
import pprint
import time
import hashlib
from tqdm import tqdm
import pickle
import dotenv
import os


dotenv.load_dotenv()
QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")
QDRANT_URL = os.environ.get("QDRANT_URL")
PROJECT_NAME = os.environ.get("PROJECT_NAME")
COLLECTION_NAME = os.environ.get("COLLECTION_NAME") or PROJECT_NAME
assert QDRANT_API_KEY and QDRANT_URL and PROJECT_NAME

def get_64bit_hash_from_tuple(input_tuple):
    input_string = "".join(map(str, input_tuple))
    sha256_hash = hashlib.sha256()
    sha256_hash.update(input_string.encode())
    return int(sha256_hash.hexdigest(), 16) & ((1 << 64) - 1)


def main(pickle_names, IS_LOCAL=False, TO_RESET=False):
    if IS_LOCAL:
        client = QdrantClient("localhost", port=6333)
    else:
        client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

    if TO_RESET:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=1536, distance=Distance.DOT),
        )

    # disable indexing for faster insertion
    client.update_collection(
        collection_name=COLLECTION_NAME,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=0),
    )

    for pickle_name in pickle_names:
        print("uploading", pickle_name)
        data = pickle.load(open(pickle_name, "rb"))
        keys = list(data.keys())
        batches = [keys[i : i + 100] for i in range(0, len(keys), 100)]
        for batch in tqdm(batches):
            points = []
            for k in batch:
                # print(k, data[k])
                vec, payload = data[k]
                try:
                    id = get_64bit_hash_from_tuple(
                        (payload["project"], payload["title"], payload["text"])
                    )
                except Exception as e:
                    print(e)
                    print("payload:", payload)
                    break


                points.append(
                    PointStruct(
                        id=id,
                        vector=vec,
                        payload=payload,
                    ),
                )
            while True:
                try:
                    operation_info = client.upsert(
                        collection_name=COLLECTION_NAME,
                        wait=True,  # block until operation is finished
                        points=points,
                    )
                    break
                except Exception as e:
                    print(e)
                    time.sleep(10)

    # enable indexing
    client.update_collection(
        collection_name=COLLECTION_NAME,
        optimizer_config=models.OptimizersConfigDiff(indexing_threshold=20000),
    )
    print("OK")

if __name__ == "__main__":
    main([f"{PROJECT_NAME}.pickle"], IS_LOCAL=False)

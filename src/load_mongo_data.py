"""Load the Nairobi air-quality parquet file into a MongoDB collection.

Usage (from the repo root):
    uv run python src/load_mongo_data.py            # load if the collection is empty
    uv run python src/load_mongo_data.py --replace  # drop and reload
"""

import argparse
import os
from pathlib import Path

import pandas as pd
from pymongo import ASCENDING, MongoClient

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARQUET = ROOT / "data" / "raw" / "nairobi.parquet"


def load_nairobi_to_mongodb(
    host=None,
    port=27017,
    parquet_path=DEFAULT_PARQUET,
    db_name="air-quality",
    collection_name="nairobi",
    replace=False,
):
    """Insert the Nairobi parquet data into MongoDB and index `timestamp`.

    The host defaults to the MONGO_HOST environment variable, then "localhost".
    An existing non-empty collection is left alone unless replace=True.
    """
    host = host or os.environ.get("MONGO_HOST", "localhost")
    parquet_path = Path(parquet_path)
    if not parquet_path.exists():
        raise FileNotFoundError(f"Parquet file not found: {parquet_path}")

    client = MongoClient(f"mongodb://{host}:{port}", serverSelectionTimeoutMS=3000)
    client.server_info()  # raises ServerSelectionTimeoutError if unreachable
    collection = client[db_name][collection_name]

    existing = collection.count_documents({})
    if existing and not replace:
        print(f"{db_name}.{collection_name} already has {existing:,} documents; "
              "nothing loaded (use --replace to reload).")
        client.close()
        return

    df = pd.read_parquet(parquet_path)  # read first, so a bad file never costs us the data
    records = df.to_dict("records")
    for record in records:
        record["timestamp"] = record["timestamp"].to_pydatetime()

    if replace:
        collection.drop()
    collection.insert_many(records)
    collection.create_index([("timestamp", ASCENDING)])
    print(f"Loaded {len(records):,} documents into {db_name}.{collection_name} at {host}:{port}")
    client.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--host", default=None)
    parser.add_argument("--port", type=int, default=27017)
    parser.add_argument("--parquet", default=str(DEFAULT_PARQUET))
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    load_nairobi_to_mongodb(args.host, args.port, args.parquet, replace=args.replace)

"""Wrangling helpers for the Nairobi air-quality data stored in MongoDB."""

import os

import pandas as pd
from pymongo import MongoClient


def wrangle_data(db="air-quality", collection="nairobi", host=None, port=27017, sensor_id=None):
    """Retrieve PM2.5 readings from MongoDB as a clean, time-indexed DataFrame.

    Parameters
    ----------
    db, collection : str
        MongoDB database and collection names.
    host : str, optional
        MongoDB host. Defaults to the MONGO_HOST environment variable, then "localhost".
    port : int
        MongoDB port (default 27017).
    sensor_id : str, optional
        If given, return only this sensor's readings; otherwise all sensors.

    Returns
    -------
    pd.DataFrame
        One column, ``pm25``, indexed by a timezone-aware (Africa/Nairobi)
        ``timestamp`` index sorted ascending, with no missing values.
        Stored timestamps are assumed to be UTC.
    """
    host = host or os.environ.get("MONGO_HOST", "localhost")
    query = {"value_type": "P2"}
    if sensor_id is not None:
        query["sensor_id"] = sensor_id

    client = MongoClient(f"mongodb://{host}:{port}", serverSelectionTimeoutMS=3000)
    try:
        records = list(
            client[db][collection]
            .find(query, projection={"timestamp": 1, "value": 1, "_id": 0})
            .sort("timestamp", 1)
        )
    finally:
        client.close()

    if not records:
        raise ValueError(f"No PM2.5 documents found in {db}.{collection} for query {query}")

    return (
        pd.DataFrame(records)
        .assign(
            timestamp=lambda x: pd.to_datetime(x["timestamp"])
            .dt.tz_localize("UTC")
            .dt.tz_convert("Africa/Nairobi")
        )
        .set_index("timestamp")
        .dropna()
        .sort_index()
        .rename(columns={"value": "pm25"})
    )

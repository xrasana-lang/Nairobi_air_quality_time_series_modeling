# Time Series Modeling of Air Quality in Nairobi

Hourly PM2.5 readings from a network of 10 sensors in Nairobi, stored in MongoDB and wrangled into a clean, time-indexed pandas series for time series modelling.

**Status:** Lesson 3.1 (data wrangling with MongoDB) complete. Modelling lessons to follow.

## What this project does so far

- Loads the sensor data into a local MongoDB 7 collection (`air-quality.nairobi`) with a timestamp index.
- Explores the collection with `pymongo`: document counts, a sample document, distinct sensors and measurement types, and aggregation pipelines.
- Packages the pipeline as `wrangle_data()`, which returns PM2.5 as a timezone-aware, sorted, hourly DataFrame, optionally for a single sensor.

![Hourly PM2.5, all sensors combined](reports/figures/pm25_hourly_series.png)

## Data

`nairobi.parquet`, provided as part of the course materials. It is not committed to this repository (`data/raw/` is git-ignored).

| Property | Value |
|---|---|
| Documents | 10,000 |
| Sensors | 10 (`nairobi_001` to `nairobi_010`) |
| Measurement type | `P2` (PM2.5) only |
| Fields | `timestamp`, `sensor_id`, `value_type`, `value`, nested `location` (`lat`, `lon`) |
| Period | 2024-01-01 to about 2025-02-20 |
| Readings per sensor | 938 to 1,051 (e.g. `nairobi_001`: 953) |

## Results (Lesson 3.1)

- All 10,000 timestamps are distinct, and every one of the 9,999 gaps between consecutive readings is exactly one hour. The combined series is a perfectly regular hourly series with no missing values.
- `nairobi_001` alone has 953 readings, with mean PM2.5 of 39.8 (median 39.9, standard deviation 9.8, range 8.0 to 67.4).
- Stored timestamps are timezone-naive. `wrangle_data()` treats them as UTC and converts them to Africa/Nairobi.

## Limitations

- Each hourly value comes from one of the 10 sensors, at a different location, so the combined series is a patchwork of sensors rather than one instrument's record. Differences between sensors appear as noise.
- The data does not state its timezone; assuming UTC is the course's convention.
- Only PM2.5 is available in this dataset.

## Reproduce

    uv sync
    docker run -d --name nairobi-mongo -p 27017:27017 -v nairobi-mongo-data:/data/db mongo:7
    # place nairobi.parquet (from the course materials) in data/raw/
    uv run python src/load_mongo_data.py
    # open notebooks/3.1_data_wrangling_mongodb.ipynb (kernel: nairobi-env)

The MongoDB host defaults to `localhost`; set the `MONGO_HOST` environment variable to use another server. Tested with Python 3.14.2, pandas 3.1.0, pymongo 4.19.0 and MongoDB 7.

## Notebooks

| Notebook | Topic |
|---|---|
| `notebooks/3.1_data_wrangling_mongodb.ipynb` | Connect, explore, import and wrangle PM2.5 data from MongoDB |

## Layout

    data/raw/            raw parquet file (git-ignored)
    data/processed/      processed data (git-ignored)
    notebooks/           one notebook per lesson
    src/load_mongo_data.py   loads the parquet file into MongoDB
    src/mongo_wrangle.py     wrangle_data(): MongoDB to clean DataFrame
    reports/figures/     saved charts
    pyproject.toml, uv.lock  environment (uv)

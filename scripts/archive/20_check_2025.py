import csv

import pandas as pd

FILES = [
    ("амброзія", "data/raw/ambrosia_ukraine_gbif.csv"),
    ("інші рослини", "data/raw/plants_ukraine_gbif.csv"),
]
WANT = ["year", "basisOfRecord", "decimalLatitude", "decimalLongitude",
        "coordinateUncertaintyInMeters"]

for name, path in FILES:
    header = pd.read_csv(path, sep="\t", nrows=0, quoting=csv.QUOTE_NONE).columns
    cols = [c for c in WANT if c in header]
    df = pd.read_csv(path, sep="\t", usecols=cols, quoting=csv.QUOTE_NONE,
                     on_bad_lines="skip", low_memory=False)
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    for c in ["decimalLatitude", "decimalLongitude"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["year", "decimalLatitude", "decimalLongitude"])

    print(f"\n=== {name} ({path}) ===")
    print("Усього записів із роком і координатами:", len(df))
    print("Роки від 2020 (усі типи записів):")
    print(df[df["year"] >= 2020]["year"].astype(int).value_counts().sort_index().to_string())
    if "basisOfRecord" in df.columns:
        h = df[df["basisOfRecord"] == "HUMAN_OBSERVATION"]
        print("Лише HUMAN_OBSERVATION від 2020:")
        print(h[h["year"] >= 2020]["year"].astype(int).value_counts().sort_index().to_string())

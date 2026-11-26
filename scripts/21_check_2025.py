import json

import joblib
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree
from sklearn.metrics import roc_auc_score

from common import CLIMATE, LAND, MAX_UNCERTAINTY_M, SEED, load_plants, to_km

TEST_YEAR = 2025
RAW_PATH = "data/raw/ambrosia_ukraine_gbif.csv"
PLANTS_PATH = "data/raw/plants_ukraine_gbif.csv"
CLIMATE_PATH = "data/processed/full_grid_climate_data_v3.csv"
MODEL_PATH = "data/processed/ambrosia_risk_model_v2.joblib"
META_PATH = "data/processed/model_v2_meta.json"
TRAIN_PATH = "data/processed/training_data_cell.csv"
MAX_CLIMATE_DIST_KM = 15.0
SEEDS = [SEED + i for i in range(10)]

with open(META_PATH, encoding="utf-8") as f:
    meta = json.load(f)
FEATURES = meta["features"]
T_HIGH = meta["threshold_high"]
model = joblib.load(MODEL_PATH)

# 1. записи амброзії за 2025 рік, ті самі фільтри, що в 02_clean_data.py
df = pd.read_csv(RAW_PATH, sep="\t", low_memory=False)
df = df[df[["year", "month", "day"]].notna().all(axis=1)]
df = df[df[["decimalLatitude", "decimalLongitude"]].notna().all(axis=1)]
df = df[df["basisOfRecord"] == "HUMAN_OBSERVATION"]
df = df[df["year"] == TEST_YEAR]
unc = df["coordinateUncertaintyInMeters"]
df = df[unc.isna() | (unc <= MAX_UNCERTAINTY_M)]
same = pd.DataFrame({
    "lat": df["decimalLatitude"].round(4), "lon": df["decimalLongitude"].round(4),
    "year": df["year"], "month": df["month"], "day": df["day"],
})
df = df[~same.duplicated()].copy()
print(f"Записів амброзії {TEST_YEAR} після фільтрів: {len(df)}")

df["lat10"] = np.rint(df["decimalLatitude"] * 10).astype(int)
df["lon10"] = np.rint(df["decimalLongitude"] * 10).astype(int)
cells_2025 = set(zip(df["lat10"], df["lon10"]))

# 2. комірки, де амброзію бачили в 2015-2024, і фон, який модель уже бачила
amb = pd.read_csv("data/processed/ambrosia_with_grid.csv")
train_keys = set(zip(np.rint(amb["lat_grid"] * 10).astype(int), np.rint(amb["lon_grid"] * 10).astype(int)))
td = pd.read_csv(TRAIN_PATH)
train_bg = set(zip(td.loc[td["presence"] == 0, "lat10"], td.loc[td["presence"] == 0, "lon10"]))

new_keys = cells_2025 - train_keys
print(f"Комірок 0.1° з амброзією {TEST_YEAR}: {len(cells_2025)}")
print(f"  з них уже були в 2015-2024: {len(cells_2025 & train_keys)}")
print(f"  нових: {len(new_keys)}")

# 3. ознаки: так само, як у 14_cell_level_background.py
land = pd.read_csv("data/processed/landcover_01deg.csv")[["lat10", "lon10"] + LAND]
reference = pd.read_csv(CLIMATE_PATH)
reference = reference.dropna(subset=CLIMATE).drop_duplicates(["lat_grid", "lon_grid"]).reset_index(drop=True)
tree = cKDTree(to_km(reference["lat_grid"].values, reference["lon_grid"].values))


def add_features(cells, label):
    n_before = len(cells)
    cells = cells.merge(land, on=["lat10", "lon10"], how="left")
    dist, idx = tree.query(to_km(cells["lat10"] / 10, cells["lon10"] / 10))
    climate = reference.iloc[idx][CLIMATE].reset_index(drop=True)
    cells = pd.concat([cells.reset_index(drop=True), climate], axis=1)
    cells["clim_dist_km"] = dist
    cells = cells[cells["clim_dist_km"] <= MAX_CLIMATE_DIST_KM]
    cells = cells.dropna(subset=LAND + ["temp_mean"]).drop(columns="clim_dist_km")
    print(f"{label}: {n_before} -> {len(cells)}")
    return cells


plants = load_plants(PLANTS_PATH)
plants["lat10"] = np.rint(plants["decimalLatitude"] * 10).astype(int)
plants["lon10"] = np.rint(plants["decimalLongitude"] * 10).astype(int)
visits = plants.groupby(["lat10", "lon10"]).size().rename("visits").reset_index()

pos = pd.DataFrame(sorted(new_keys), columns=["lat10", "lon10"])
pos = add_features(pos, "Нові presence-комірки з ознаками")
pos = pos.merge(visits, on=["lat10", "lon10"], how="left").fillna({"visits": 0})
pos["presence"] = 1

exclude = train_keys | cells_2025 | train_bg
pool = visits[[k not in exclude for k in zip(visits["lat10"], visits["lon10"])]].copy()
pool = add_features(pool, "Пул фону (без комірок, які модель уже бачила)")
print(f"Нових presence: {len(pos)}, пул фону: {len(pool)}")

# 4. оцінка збереженої моделі на нових комірках
rows = []
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    p = pool["visits"].values / pool["visits"].values.sum()
    chosen = rng.choice(len(pool), size=min(len(pos), len(pool)), replace=False, p=p)
    bg = pool.iloc[chosen].copy()
    bg["presence"] = 0
    data = pd.concat([pos, bg], ignore_index=True)
    risk = model.predict_proba(data[FEATURES])[:, 1]
    y = data["presence"]
    rows.append({
        "seed": seed,
        "AUC моделі": roc_auc_score(y, risk),
        "AUC лише візити": roc_auc_score(y, data["visits"]),
        "частка presence з індексом >= high": float((risk[y == 1] >= T_HIGH).mean()),
        "частка фону з індексом >= high": float((risk[y == 0] >= T_HIGH).mean()),
    })

res = pd.DataFrame(rows)
print(f"\nПеревірка на нових комірках {TEST_YEAR} ({len(SEEDS)} вибірок фону):")
print(res.drop(columns="seed").agg(["mean", "std"]).round(3).T.to_string())
print("\nПо вибірках:")
print(res.round(3).to_string(index=False))

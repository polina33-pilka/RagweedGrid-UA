import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold, cross_val_score

from common import LAND, SEED, load_plants, make_rf, spatial_blocks

PLANTS_PATH = "data/raw/plants_ukraine_gbif.csv"
SEEDS = [SEED, SEED + 1, SEED + 2]
LAND_FILES = {
    0.1: "data/processed/landcover_01deg.csv",
    0.2: "data/processed/landcover_02deg.csv",  # створює 12b
}


def snap(values, step):
    # центр комірки в десятих частках градуса: 0.1 -> будь-яке ціле, 0.2 -> парне
    values = np.asarray(values, dtype=float)
    if step == 0.1:
        return np.rint(values * 10).astype(int)
    return (np.rint(values * 5) * 2).astype(int)


ambrosia = pd.read_csv("data/processed/ambrosia_with_grid.csv")
plants = load_plants(PLANTS_PATH)

for step, land_path in LAND_FILES.items():
    land = pd.read_csv(land_path)[["lat10", "lon10"] + LAND].dropna()

    presence = pd.DataFrame({
        "lat10": snap(ambrosia["decimalLatitude"], step),
        "lon10": snap(ambrosia["decimalLongitude"], step),
    }).drop_duplicates()
    presence_keys = set(zip(presence["lat10"], presence["lon10"]))
    presence = presence.merge(land, on=["lat10", "lon10"], how="inner")
    presence["presence"] = 1

    # виключаємо комірки присутності ще до вибірки фону, щоб уникнути витоку міток
    plants["lat10"] = snap(plants["decimalLatitude"], step)
    plants["lon10"] = snap(plants["decimalLongitude"], step)
    visits = plants.groupby(["lat10", "lon10"]).size().rename("visits").reset_index()
    not_ambrosia = [k not in presence_keys for k in zip(visits["lat10"], visits["lon10"])]
    candidates = visits[not_ambrosia].merge(land, on=["lat10", "lon10"], how="inner")

    print(f"\n=== Комірка {step}° ===")
    print(f"Presence: {len(presence)}, кандидатів на фон: {len(candidates)}")

    scores = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        p = candidates["visits"].values / candidates["visits"].values.sum()
        chosen = rng.choice(len(candidates), size=min(len(presence), len(candidates)),
                            replace=False, p=p)
        background = candidates.iloc[chosen].copy()
        background["presence"] = 0

        data = pd.concat([presence, background], ignore_index=True)
        data["lat_grid"] = data["lat10"] / 10
        data["lon_grid"] = data["lon10"] / 10

        auc = cross_val_score(make_rf(seed), data[LAND], data["presence"],
                              cv=GroupKFold(n_splits=5), groups=spatial_blocks(data),
                              scoring="roc_auc").mean()
        scores.append(auc)

    print(f"Лише земля, AUC по регіонах: {np.mean(scores):.3f} +/- {np.std(scores, ddof=1):.3f} "
          f"(по {len(SEEDS)} вибірках фону)")
    print(f"Середня built: presence {presence['built'].mean():.3f}, "
          f"кандидати {candidates['built'].mean():.3f}")

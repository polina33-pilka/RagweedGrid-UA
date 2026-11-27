import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import GroupKFold

from common import CLIMATE, LAND, make_rf, spatial_blocks
from ukraine_border import in_ukraine

FEATURES = CLIMATE + LAND
OUT_DIR = "data/processed/"


def boyce_continuous(pred_all, pred_pres, n_windows=100, width=0.1):
    pred_all = np.asarray(pred_all, dtype=float)
    pred_pres = np.asarray(pred_pres, dtype=float)
    lo, hi = pred_all.min(), pred_all.max()
    w = (hi - lo) * width
    if w <= 0 or len(pred_pres) < 5:
        return np.nan
    centers, ratios = [], []
    # рухоме вікно по діапазону прогнозів: порівнюємо частку знахідок і частку всієї площі
    for s in np.linspace(lo, hi - w, n_windows):
        e = np.mean((pred_all >= s) & (pred_all <= s + w))
        if e == 0:
            continue
        p = np.mean((pred_pres >= s) & (pred_pres <= s + w))
        centers.append(s + w / 2)
        ratios.append(p / e)
    if len(ratios) < 10 or np.allclose(ratios, ratios[0]):
        return np.nan
    return float(spearmanr(centers, ratios).statistic)


d = pd.read_csv(OUT_DIR + "training_data_cell.csv")
X, y = d[FEATURES], d["presence"].to_numpy()
blocks_train = np.asarray(spatial_blocks(d))

# точки карти, як у 16_train_final_model_v2.py
grid = pd.read_csv(OUT_DIR + "full_grid_climate_data_v3.csv")
grid["lat10"] = np.rint(grid["lat_grid"] * 10).astype(int)
grid["lon10"] = np.rint(grid["lon_grid"] * 10).astype(int)
land = pd.read_csv(OUT_DIR + "landcover_01deg.csv")[["lat10", "lon10"] + LAND]
grid = grid.merge(land, on=["lat10", "lon10"], how="left").dropna(subset=FEATURES).reset_index(drop=True)
inside = [in_ukraine(lon, lat) for lat, lon in zip(grid["lat_grid"], grid["lon_grid"])]
grid = grid[inside].reset_index(drop=True)
print(f"Точок карти: {len(grid)}")

# блоки для точок карти (одним викликом, щоб нумерація збігалася)
both = pd.concat([d[["lat_grid", "lon_grid"]], grid[["lat_grid", "lon_grid"]]], ignore_index=True)
blocks_all = np.asarray(spatial_blocks(both))
b_train, b_grid = blocks_all[: len(d)], blocks_all[len(d):]

check = pd.DataFrame({"a": blocks_train, "b": b_train})
same = (check.groupby("a")["b"].nunique().max() == 1) and (check.groupby("b")["a"].nunique().max() == 1)
print("Блоки навчальних даних збігаються з блоками при спільному виклику:", same)

rows = []
for k, (tr, te) in enumerate(GroupKFold(n_splits=5).split(X, y, groups=blocks_train), start=1):
    model = make_rf(n_estimators=500).fit(X.iloc[tr], y[tr])
    p_te = model.predict_proba(X.iloc[te])[:, 1]
    pres = p_te[y[te] == 1]
    # беремо лише точки карти з тестових блоків поточного фолда, без витоку з тренувальних
    mask = np.isin(b_grid, list(set(b_train[te])))
    p_test_blocks = model.predict_proba(grid.loc[mask, FEATURES])[:, 1]
    p_all_map = model.predict_proba(grid[FEATURES])[:, 1]
    rows.append({
        "fold": k,
        "AUC": roc_auc_score(y[te], p_te),
        "знахідок": len(pres),
        "точок карти в тест. блоках": int(mask.sum()),
        "Boyce (тест. блоки)": boyce_continuous(p_test_blocks, pres),
        "Boyce (вся карта)": boyce_continuous(p_all_map, pres),
    })

res = pd.DataFrame(rows)
print("\nПо фолдах:")
print(res.round(3).to_string(index=False))
print("\nСереднє +/- std:")
for c in ["AUC", "Boyce (тест. блоки)", "Boyce (вся карта)"]:
    print(f"{c}: {res[c].mean():.3f} +/- {res[c].std(ddof=0):.3f}")

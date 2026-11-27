import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

from common import CLIMATE, to_km

GRID_PATH = "data/processed/full_grid_points_v3.csv"
RAW_PATH = "data/processed/full_grid_climate_data_v3.csv"
OUT_PATH = "data/processed/full_grid_climate_data_v3_filled.csv"

K = 4            # скільки найближчих завантажених точок використовувати
MAX_KM = 60.0    # далі за цю відстань точку не заповнюємо


def idw(tree, values, query_xy, k, skip_self=False):
    # зважене за 1/d^2 середнє k найближчих точок
    dist, idx = tree.query(query_xy, k=k + 1 if skip_self else k)
    # при leave-one-out першим сусідом завжди буде сама точка з нульовою відстанню
    if skip_self:
        dist, idx = dist[:, 1:], idx[:, 1:]
    # нижня межа 1.0 км, щоб не ділити на нуль при збігу координат
    w = np.where(dist <= MAX_KM, 1.0 / np.maximum(dist, 1.0) ** 2, 0.0)
    total = w.sum(axis=1)
    out = {}
    for col in CLIMATE:
        v = values[col].values[idx]
        out[col] = np.where(total > 0, (v * w).sum(axis=1) / np.where(total > 0, total, 1), np.nan)
    return out


grid = pd.read_csv(GRID_PATH).round(1)
got = pd.read_csv(RAW_PATH).round({"lat_grid": 1, "lon_grid": 1})
got = got.dropna(subset=CLIMATE).drop_duplicates(["lat_grid", "lon_grid"]).reset_index(drop=True)
print(f"Точок у сітці: {len(grid)}, завантажено: {len(got)}")

have = set(zip(got["lat_grid"], got["lon_grid"]))
missing = grid[[(la, lo) not in have for la, lo in zip(grid["lat_grid"], grid["lon_grid"])]].copy()
print(f"Відсутніх точок: {len(missing)}")

tree = cKDTree(to_km(got["lat_grid"].values, got["lon_grid"].values))

# оцінка похибки інтерполяції: приховуємо кожну завантажену точку по черзі
pred = idw(tree, got, to_km(got["lat_grid"].values, got["lon_grid"].values), K, skip_self=True)
print("\nПохибка інтерполяції (кожна завантажена точка передбачається з сусідніх):")
for col in CLIMATE:
    err = (pred[col] - got[col].values)
    err = err[np.isfinite(err)]
    print(f"  {col}: середня абсолютна похибка {np.abs(err).mean():.3f}, "
          f"95-й перцентиль {np.percentile(np.abs(err), 95):.3f}, "
          f"розкид значень (std) {got[col].std():.3f}")

if len(missing):
    fill = idw(tree, got, to_km(missing["lat_grid"].values, missing["lon_grid"].values), K)
    for col in CLIMATE:
        missing[col] = fill[col]
    # точки далі за MAX_KM залишаються з NaN, тому випадають після dropna
    missing = missing.dropna(subset=CLIMATE)
    missing["interpolated"] = True
    print(f"\nЗаповнено інтерполяцією: {len(missing)}")

out = got[["lat_grid", "lon_grid"] + CLIMATE].copy()
out["interpolated"] = False
out = pd.concat([out, missing], ignore_index=True) if len(missing) else out
out.to_csv(OUT_PATH, index=False)
print(f"Збережено: {OUT_PATH} ({len(out)} точок, з них інтерполяцією {int(out['interpolated'].sum())})")
print("Це чернетковий варіант. Остаточний прогін робіть на повністю завантаженому файлі.")

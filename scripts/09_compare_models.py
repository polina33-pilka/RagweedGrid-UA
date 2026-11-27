import os
import sys

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from common import CLIMATE, LAND, SEED, make_rf, spatial_blocks

# вибірку створює 14_cell_level_background.py (одна вибірка фону, seed 42)
path = sys.argv[1] if len(sys.argv) > 1 else "data/processed/training_data_cell.csv"
data = pd.read_csv(path)
y = data["presence"]
blocks = spatial_blocks(data)

print(f"Файл: {path}")
print(f"Рядків: {len(data)} (presence {int(y.sum())}, фон {int((y == 0).sum())})")
print(f"Просторових блоків: {blocks.nunique()}")
print("Увага: це одна вибірка фону (seed 42), тому числа трохи відрізняються від середнього "
      "по трьох вибірках у 14.\n")


def make_models():
    return {
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000)),
        "Random Forest": make_rf(),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.05, random_state=SEED),
    }


random_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
spatial_cv = GroupKFold(n_splits=5)


def auc(model, X, **cv_args):
    return cross_val_score(model, X, y, scoring="roc_auc", **cv_args)


feature_sets = {
    "клімат": CLIMATE,
    "клімат + земля": CLIMATE + LAND,
}

rows = []
for set_name, cols in feature_sets.items():
    for name, model in make_models().items():
        random_scores = auc(model, data[cols], cv=random_cv)
        spatial_scores = auc(model, data[cols], cv=spatial_cv, groups=blocks)
        rows.append({
            "model": name,
            "features": set_name,
            "AUC random CV": round(random_scores.mean(), 3),
            "AUC spatial CV": round(spatial_scores.mean(), 3),
            "spatial std": round(spatial_scores.std(), 3),
        })

# діагностика: якщо модель лише на координатах не гірша, вона вчить місця спостережень
coords = data[["lat_grid", "lon_grid"]]
rows.append({
    "model": "Random Forest (діагностика)",
    "features": "тільки lat/lon",
    "AUC random CV": round(auc(make_rf(), coords, cv=random_cv).mean(), 3),
    "AUC spatial CV": round(auc(make_rf(), coords, cv=spatial_cv, groups=blocks).mean(), 3),
    "spatial std": np.nan,
})

results = pd.DataFrame(rows)
print("Порівняння моделей (AUC-ROC, 5 фолдів):")
print(results.to_string(index=False))

out = "data/processed/model_comparison_" + os.path.splitext(os.path.basename(path))[0] + ".csv"
results.to_csv(out, index=False)
print(f"\nЗбережено: {out}")

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score

from common import CLIMATE, LAND, SEED, make_rf, spatial_blocks

# вибірку створює 14_cell_level_background.py (одна вибірка фону, seed 42)
TRAINING_PATH = "data/processed/training_data_cell.csv"
COMPARISON_PATH = "data/processed/feature_set_comparison_cell.csv"

data = pd.read_csv(TRAINING_PATH)
y = data["presence"]
blocks = spatial_blocks(data)

print(f"Рядків: {len(data)} (presence {int(y.sum())}, фон {int((y == 0).sum())})")
print("Увага: це одна вибірка фону (seed 42), тому числа трохи відрізняються від середнього "
      "по трьох вибірках у 14.")
print("Висота тут не перевірялась: для нових комірок немає таблиці висот "
      "(результат для висоти див. у попередньому прогоні).\n")

# lat/lon беремо як контроль, щоб побачити, чи не тягне модель просто координати замість факторів
feature_sets = {
    "клімат": CLIMATE,
    "лише земля": LAND,
    "клімат + земля": CLIMATE + LAND,
    "лише lat/lon (діагностика)": ["lat_grid", "lon_grid"],
}


def make_models():
    return {
        "Random Forest": make_rf(),
        "Gradient Boosting": GradientBoostingClassifier(
            n_estimators=200, max_depth=3, learning_rate=0.05, random_state=SEED),
    }


random_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
# групуємо за просторовими блоками, щоб оцінити узагальнення на нові регіони без сусіднього витоку
spatial_cv = GroupKFold(n_splits=5)

rows = []
for set_name, cols in feature_sets.items():
    for model_name, model in make_models().items():
        r = cross_val_score(model, data[cols], y, cv=random_cv, scoring="roc_auc")
        s = cross_val_score(model, data[cols], y, cv=spatial_cv, groups=blocks, scoring="roc_auc")
        rows.append({
            "ознаки": set_name,
            "модель": model_name,
            "AUC випадкова": round(r.mean(), 3),
            "AUC по регіонах": round(s.mean(), 3),
            "std по регіонах": round(s.std(), 3),
        })

results = pd.DataFrame(rows)
print("Порівняння наборів ознак (AUC-ROC, 5 фолдів):")
print(results.to_string(index=False))
results.to_csv(COMPARISON_PATH, index=False)

all_cols = CLIMATE + LAND
forest = make_rf().fit(data[all_cols], y)
importance = pd.Series(forest.feature_importances_, index=all_cols).sort_values(ascending=False)
print("\nВажливість ознак (Random Forest, клімат + земля):")
print(importance.round(3).to_string())
print(f"\nЗбережено: {COMPARISON_PATH}")

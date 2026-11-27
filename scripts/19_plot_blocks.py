import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from common import BLOCK_SIZE, spatial_blocks
from ukraine_border import UKRAINE_POLYGON

d = pd.read_csv("data/processed/training_data_cell.csv")
blocks = spatial_blocks(d)

# записуємо номер тестового фолда (1..5) для кожної точки
fold = np.zeros(len(d), dtype=int)
for i, (_, test_idx) in enumerate(GroupKFold(n_splits=5).split(d, d["presence"], blocks), start=1):
    fold[test_idx] = i
d["fold"] = fold

print("Рядків:", len(d), "| блоків 2°x2°:", blocks.nunique())
print("Блоків у фолді:", blocks.groupby(d["fold"]).nunique().to_dict())
print("Точок у фолді:", d["fold"].value_counts().sort_index().to_dict())

colors = ["#1b4d3e", "#d97706", "#3b82a6", "#9b5de5", "#c2410c"]
fig, ax = plt.subplots(figsize=(10, 6.5), dpi=200)

poly = np.array(UKRAINE_POLYGON)
ax.plot(poly[:, 0], poly[:, 1], color="#444444", linewidth=1.3, zorder=3)

# сітка просторових блоків за розміром з common
for v in np.arange(20, 42, BLOCK_SIZE):
    ax.axvline(v, color="#777777", linewidth=1.2, zorder=1)
for v in np.arange(44, 54, BLOCK_SIZE):
    ax.axhline(v, color="#777777", linewidth=1.2, zorder=1)

for k in range(1, 6):
    s = d[d["fold"] == k]
    ax.scatter(s["lon_grid"], s["lat_grid"], s=16, color=colors[k - 1],
               label=f"Фолд {k}", zorder=2, alpha=0.9)

ax.set_xlim(21.5, 40.5)
ax.set_ylim(44, 52.6)
# коригуємо співвідношення осей на широті ~48.5°, щоб карта не виглядала розтягнутою
ax.set_aspect(1 / np.cos(np.radians(48.5)))
ax.legend(title="Тестовий фолд", loc="lower right", fontsize=9, frameon=True)
ax.axis("off")
plt.tight_layout()
plt.savefig("outputs_after/spatial_cv_blocks.png", transparent=False)
print("Збережено outputs_after/spatial_cv_blocks.png")

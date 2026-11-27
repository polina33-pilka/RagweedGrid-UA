import pandas as pd

from ukraine_border import in_ukraine

OUT = "data/processed/"

land = pd.read_csv(OUT + "landcover_02deg.csv").dropna(subset=["cropland", "built"])

# беремо лише точки сітки 0.2°, які потрапляють у межі України
points = [
    (r.lat10 / 10, r.lon10 / 10)
    for r in land.itertuples()
    if in_ukraine(r.lon10 / 10, r.lat10 / 10)
]
grid = pd.DataFrame(points, columns=["lat_grid", "lon_grid"]).round(1)
grid.to_csv(OUT + "full_grid_points_v3.csv", index=False)
print(f"Точок сітки 0.2°: {len(grid)}")
# старий клімат не переносимо, бо він рахувався для іншого сезону
print("Клімат для них завантажує 04d (старий файл за інший сезон не переноситься).")

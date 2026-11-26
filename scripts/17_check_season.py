import pandas as pd

PATH = "data/processed/full_grid_climate_data_v3.csv"
DAYS = {4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31}
SEASONS = {"4-10": (4, 10), "5-9": (5, 9), "4-9": (4, 9), "7-10": (7, 10), "7-9": (7, 9)}
VARS = [("temp_mean", "t"), ("precip_sum", "p"), ("humidity_mean", "h")]
TOL = 0.01

df = pd.read_csv(PATH)
print("Рядків:", len(df))
print("Колонки:", list(df.columns))

needed = [v for v, _ in VARS] + [f"{pre}{m:02d}" for _, pre in VARS for m in range(4, 11)]
absent = [c for c in needed if c not in df.columns]
if absent:
    print("УВАГА: немає колонок:", absent)
    raise SystemExit(1)

print("\nНайбільше розходження між сезонною колонкою і середнім із місячних:")
ok = True
for var, pre in VARS:
    sub = df.dropna(subset=[var] + [f"{pre}{m:02d}" for m in range(4, 11)])
    print(f"\n{var} (рядків без пропусків: {len(sub)} з {len(df)})")
    for name, (a, b) in SEASONS.items():
        months = range(a, b + 1)
        w = sum(DAYS[m] for m in months)
        calc = sum(sub[f"{pre}{m:02d}"] * DAYS[m] for m in months) / w
        diff = (calc - sub[var]).abs().max()
        mark = ""
        if name == "4-10":
            mark = "  <- має бути ~0" 
            if diff > TOL:
                ok = False
        print(f"  сезон {name}: {diff:.4f}{mark}")

print()
print("Сезон 4-10 збігається в усіх рядках." if ok else "УВАГА: сезонні колонки не збігаються з 4-10, не продовжуйте.")

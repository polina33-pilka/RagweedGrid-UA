import pandas as pd

path = r"data\raw\plants_ukraine_gbif.csv"
df = pd.read_csv(path, sep="\t", low_memory=False, on_bad_lines="skip",
                 usecols=lambda c: c in ("genus", "species", "scientificName"))
print("Усього рядків:", len(df))
for col in ("genus", "species", "scientificName"):
    if col in df.columns:
        n = df[col].astype(str).str.contains("Ambrosia", case=False, na=False).sum()
        print(col, "-> рядків з Ambrosia:", n)

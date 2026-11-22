import os
import time

import pandas as pd
import requests

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"
START_DATE = "2015-01-01"
END_DATE = "2024-12-31"

# колонка у API -> префікс місячної колонки у нашому файлі
VARIABLES = {
    "temperature_2m_mean": "t",
    "precipitation_sum": "p",
    "relative_humidity_2m_mean": "h",
    "temperature_2m_min": "n",
}
DAILY_VARIABLES = ",".join(VARIABLES)

# сезон для ознак temp_mean, precip_sum, humidity_mean (біологія виду: вегетація квітень-жовтень)
SEASON_FIRST_MONTH, SEASON_LAST_MONTH = 4, 10

# стартовий розмір пачки; якщо API каже, що даних забагато, пачка зменшується автоматично
BATCH_SIZE = 30
MAX_RETRIES = 5
PAUSE_ON_ERROR = 30

SEASON_COLUMNS = ["temp_mean", "precip_sum", "humidity_mean"]
# середні по місяцях за 2015-2024: t01..t12 (температура), p01..p12 (опади, мм/добу),
# h01..h12 (вологість, %), n01..n12 (середній добовий мінімум температури)
MONTHLY_COLUMNS = [f"{prefix}{m:02d}" for prefix in VARIABLES.values() for m in range(1, 13)]
COLUMNS = ["lat_grid", "lon_grid"] + SEASON_COLUMNS + MONTHLY_COLUMNS


def round_pair(lat, lon):
    return round(lat, 1), round(lon, 1)


def priority(point):
    """0: решітка 0.4 x 0.4 градуса, 1: додається решітка 0.4 за широтою, 2: решта.
    Якщо час закінчиться раніше, вже завантажені точки покривають усю територію рівномірно."""
    la10, lo10 = int(round(point[0] * 10)), int(round(point[1] * 10))
    if la10 % 4 == 0 and lo10 % 4 == 0:
        return 0
    if la10 % 4 == 0:
        return 1
    return 2


def check_format(output_path):
    """Файл зі старим форматом (без місячних колонок) не можна доповнювати: сезон міг бути іншим."""
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        return
    header = pd.read_csv(output_path, nrows=0).columns.tolist()
    if header != COLUMNS:
        raise SystemExit(
            f"{output_path} має старий формат колонок. Перенесіть його в архів "
            "(наприклад, data/processed/climate_5_9/) і запустіть скрипт знову."
        )


def load_done_pairs(output_path):
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        print("Файлу прогресу ще немає, починаємо з нуля.")
        return set()
    try:
        done = pd.read_csv(output_path)
    except pd.errors.EmptyDataError:
        print("Файл прогресу порожній, починаємо з нуля.")
        open(output_path, "w").close()
        return set()
    pairs = set(zip(done["lat_grid"].round(1), done["lon_grid"].round(1)))
    print(f"Вже оброблено точок: {len(pairs)}, продовжуємо.")
    return pairs


def append_rows(output_path, rows):
    needs_header = not os.path.exists(output_path) or os.path.getsize(output_path) == 0
    pd.DataFrame(rows, columns=COLUMNS).to_csv(
        output_path, mode="a", header=needs_header, index=False
    )


def fetch_batch(label, lats, lons, delay, max_delay):
    """Повертає (дані, delay). Дані: список, None (збій), "too_large" або "daily_limit"."""
    params = {
        "latitude": ",".join(map(str, lats)),
        "longitude": ",".join(map(str, lons)),
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": DAILY_VARIABLES,
        "timezone": "auto",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(BASE_URL, params=params, timeout=90)
        except requests.exceptions.RequestException as e:
            print(f"Пачка {label}: помилка мережі ({e}), пауза {PAUSE_ON_ERROR} с")
            time.sleep(PAUSE_ON_ERROR)
            continue

        if response.status_code == 429:
            print(response.text[:200])
            if "Daily API request limit" in response.text:
                return "daily_limit", delay
            retry_after = response.headers.get("Retry-After")
            wait = int(retry_after) if retry_after else 60 * attempt
            print(f"Пачка {label}: ліміт запитів ({attempt}/{MAX_RETRIES}), пауза {wait} с")
            time.sleep(wait)
            delay = min(delay * 1.5, max_delay)
            continue

        if response.status_code != 200:
            print(response.text[:300])
            if response.status_code == 400 and "too much data" in response.text:
                return "too_large", delay
            print(f"Пачка {label}: відповідь {response.status_code}, пауза {PAUSE_ON_ERROR} с")
            time.sleep(PAUSE_ON_ERROR)
            continue

        try:
            data = response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"Пачка {label}: пошкоджена відповідь ({attempt}/{MAX_RETRIES}), пауза {PAUSE_ON_ERROR} с")
            time.sleep(PAUSE_ON_ERROR)
            continue

        # для однієї точки API повертає об'єкт, а не список
        return (data if isinstance(data, list) else [data]), delay

    return None, delay


def season_means(location_data):
    daily = pd.DataFrame(location_data["daily"])
    month = pd.to_datetime(daily["time"]).dt.month
    season = daily[(month >= SEASON_FIRST_MONTH) & (month <= SEASON_LAST_MONTH)]

    result = {
        "temp_mean": season["temperature_2m_mean"].mean(),
        "precip_sum": season["precipitation_sum"].mean(),
        "humidity_mean": season["relative_humidity_2m_mean"].mean(),
    }
    for column, prefix in VARIABLES.items():
        by_month = daily[column].groupby(month).mean()
        for m in range(1, 13):
            result[f"{prefix}{m:02d}"] = by_month.get(m, float("nan"))
    return result


def report_coverage(grid, output_path):
    needed = set(zip(grid["lat_grid"].round(1), grid["lon_grid"].round(1)))
    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        print(f"Потрібно {len(needed)}, не вистачає {len(needed)}")
        return
    done = pd.read_csv(output_path)
    have = set(zip(done["lat_grid"].round(1), done["lon_grid"].round(1)))
    print(f"Потрібно {len(needed)}, не вистачає {len(needed - have)}")
    empty = int(done[SEASON_COLUMNS].isna().any(axis=1).sum())
    if empty:
        print(f"УВАГА: у {empty} точок немає кліматичних значень (NaN).")


def fetch_grid_climate(grid_path, output_path, base_delay, max_delay):
    check_format(output_path)
    print(f"Сезон: місяці {SEASON_FIRST_MONTH}-{SEASON_LAST_MONTH}, період {START_DATE} - {END_DATE}")

    grid = pd.read_csv(grid_path)
    print(f"Комірок для обробки: {len(grid)}")

    done_pairs = load_done_pairs(output_path)
    todo = [
        (la, lo)
        for la, lo in zip(grid["lat_grid"].tolist(), grid["lon_grid"].tolist())
        if round_pair(la, lo) not in done_pairs
    ]
    todo.sort(key=priority)  # стабільне сортування: спочатку груба решітка, потім густіша
    levels = [sum(1 for p in todo if priority(p) == k) for k in (0, 1, 2)]
    print(f"Лишилось завантажити: {len(todo)} (груба решітка: {levels[0]}, середня: {levels[1]}, решта: {levels[2]})")

    size = BATCH_SIZE
    delay = base_delay
    i = 0
    while i < len(todo):
        chunk = todo[i:i + size]
        data, delay = fetch_batch(i, [p[0] for p in chunk], [p[1] for p in chunk], delay, max_delay)

        if isinstance(data, str) and data == "daily_limit":
            print("\nДобовий ліміт Open-Meteo вичерпано. Закрийте термінал і запустіть цей самий "
                  "скрипт завтра: усе збережене лишається.")
            break
        if isinstance(data, str) and data == "too_large":
            if size == 1:
                print("Навіть одна точка завелика для API. Зменште кількість змінних у VARIABLES.")
                break
            size = max(1, size // 2)
            print(f"Запит завеликий, зменшуємо пачку до {size} точок.")
            continue
        if data is None:
            print(f"Пачка {i}: не вдалося отримати дані після {MAX_RETRIES} спроб. "
                  "Зупиняємось, повторний запуск продовжить з цього місця.")
            break
        if len(data) != len(chunk):
            print(f"Пачка {i}: очікували {len(chunk)} точок, отримали {len(data)}. Зупиняємось.")
            break

        rows = [
            {"lat_grid": la, "lon_grid": lo, **season_means(location)}
            for (la, lo), location in zip(chunk, data)
        ]
        append_rows(output_path, rows)
        done_pairs.update(round_pair(la, lo) for la, lo in chunk)
        i += len(chunk)

        print(f"Збережено {len(done_pairs)} / {len(grid)} (пачка {size}, пауза {delay:.0f} с)")
        time.sleep(delay)
        delay = max(base_delay, delay * 0.9)

    print("\nГотово або зупинено для повторного запуску.")
    report_coverage(grid, output_path)

import pandas as pd

from .mephi_scraper import fetch as mephi_fetch
from .hse_scraper import fetch as hse_fetch
from .mipt_scraper import fetch as mipt_fetch


def fetch_all():
    frames = []
    scrapers = [
        ("MEPhI", mephi_fetch),
        ("HSE", hse_fetch),
        ("MIPT", mipt_fetch),
    ]
    for name, scraper in scrapers:
        try:
            print("Fetching", name)
            df = scraper()
            frames.append(df)
        except Exception as e:
            print("Failed", name, e)

    if not frames:
        raise RuntimeError("No data fetched")
    result = pd.concat(frames, ignore_index=True)
    return result

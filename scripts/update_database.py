import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ege_calculator.integrations.aggregator import fetch_all
from ege_calculator.settings import DATABASE_FILE


def main():
    df = fetch_all()
    DATABASE_FILE.parent.mkdir(exist_ok=True)
    df.to_csv(DATABASE_FILE, index=False)
    print("Saved rows:", len(df))


if __name__ == "__main__":
    main()

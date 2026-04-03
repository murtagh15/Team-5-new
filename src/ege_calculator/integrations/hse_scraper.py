import pandas as pd


def fetch():
    # временный fallback dataset

    data = [
        ("09.03.01", "Информатика и вычислительная техника", 294),
        ("01.03.02", "Прикладная математика", 298),
        ("38.03.01", "Экономика", 304),
        ("38.03.05", "Бизнес-информатика", 302),
    ]

    df = pd.DataFrame(data, columns=["code", "program", "score"])

    df["university"] = "HSE"

    return df
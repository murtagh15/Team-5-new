import pandas as pd


def fetch():

    data = [
        ("03.03.01", "Прикладная математика и физика", 300),
        ("03.03.02", "Физика", 298),
        ("09.03.01", "Информатика и вычислительная техника", 295),
    ]

    df = pd.DataFrame(data, columns=["code", "program", "score"])

    df["university"] = "MIPT"

    return df
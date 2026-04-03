import requests
import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO


URL = "https://admission.mephi.ru/admission/baccalaureate-and-specialty/exams/previous-years"


def fetch():

    r = requests.get(URL, timeout=20)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    table = soup.find("table")

    html = StringIO(str(table))

    df = pd.read_html(html)[0]

    df.columns = [
        "code",
        "program",
        "score_type",
        "score"
    ]

    df["university"] = "MEPhI"

    df["score"] = pd.to_numeric(df["score"], errors="coerce")

    df = df.dropna(subset=["score"])

    return df
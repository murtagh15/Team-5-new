import pandas as pd
from functools import lru_cache
from ege_calculator.settings import DATABASE_FILE


class CSVRepository:

    @lru_cache(maxsize=1)
    def get_dataframe(self):
        df = pd.read_csv(DATABASE_FILE)

        return df

    def get_universities(self):
        df = self.get_dataframe()

        return sorted(df["university"].unique())

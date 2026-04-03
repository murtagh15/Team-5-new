from abc import ABC, abstractmethod
import pandas as pd


class Repository(ABC):

    @abstractmethod
    def get_dataframe(self) -> pd.DataFrame:
        pass

    @abstractmethod
    def get_universities(self):
        pass
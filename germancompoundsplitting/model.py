from abc import ABC, abstractmethod
import pandas as pd

class Model(ABC):
    def __init__(self):
        self.df = pd.DataFrame()
        self.name = "Model"

    def set_data(self,df):
        self.df = df

    def model_type(self):
        return self.name

    @abstractmethod
    def run(self):
        ...

import german_compound_splitter
from german_compound_splitter import comp_split
import pandas as pd

class CompSplitWrapper:
    def __init__(self, *,data:pd.DataFrame):
        self.df = data
        self.input_file = 'Dictionaries/german.dic.txt'


    def run(self):
        ahocs = comp_split.read_dictionary_from_file(self.input_file)
        for column in self.df.columns:
            self.df['components'] = self.df[column].apply(lambda x: comp_split.dissect(x, ahocs, make_singular=True))
        return self.df


model_1 = CompSplitWrapper(data=pd.DataFrame({'compounds':['Donaudampfschifffahrtskapitänsmützenabzeichen','Datensatz','Ablauforganisation','Einsatzfähigkeit','Heimspiel']}))
print(model_1.run())


from germancompoundsplitting.german_compound_splitter import comp_split
import pandas as pd

class CompSplitWrapper:
    def __init__(self, data:pd.DataFrame=None):
        self.df = data
        self.input_file = '../Dictionaries/german.dic.txt'
        self.ahocs = comp_split.read_dictionary_from_file(self.input_file)


    def run(self):
        self.df['components'] = self.df['compounds'].apply(lambda x: comp_split.dissect(x, self.ahocs, make_singular=True))
        return self.df

    @staticmethod
    def model_type():
        return 'Compound_Splitter'


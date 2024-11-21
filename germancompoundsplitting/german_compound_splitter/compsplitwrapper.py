from germancompoundsplitting.german_compound_splitter import comp_split
import pandas as pd

class CompSplitWrapper:

    def __init__(self, data:pd.DataFrame=None):
        """
        Creates a wrapper object around comp_split.py. Used to make class usable for evaluator class.
        :param data: Dataframe with compound words to split in a column labeled 'compounds'.
        """
        self.df = data
        self.input_file = '../Dictionaries/german.dic.txt'
        self.ahocs = comp_split.read_dictionary_from_file(self.input_file)


    def run(self):
        """
        Runs the underlying model's splitting of compounds and places the created words in a
        'components' column of the dataframe.
        :return: Returns the dataframe with components added.
        """
        self.df['components'] = self.df['compounds'].apply(lambda x: comp_split.dissect(x, self.ahocs, make_singular=True))
        return self.df

    @staticmethod
    def model_type():
        """
        Method to return type of model. Used for easier dynamic identification.
        :return: THe name of this model as a string.
        """
        return 'Compound_Splitter'


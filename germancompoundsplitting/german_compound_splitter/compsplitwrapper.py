from germancompoundsplitting.german_compound_splitter import comp_split
import pandas as pd
import numpy as np
import os

class CompSplitWrapper:
    EXCEPTION = 'exception'
    def __init__(self):
        """
        Creates a wrapper object around comp_split.py. Used to make class usable for evaluator class.
        :param data: Dataframe with compound words to split in a column labeled 'compounds'.
        """
        self.df = pd.DataFrame()
        curdir = os.path.dirname(os.path.abspath(__file__))
        self.input_file = os.path.join(curdir, "Dictionaries", "german.dic.txt")
        self.ahocs = comp_split.read_dictionary_from_file(self.input_file)
        self.exception_list = []


    def run(self):
        """
        Runs the underlying model's splitting of compounds and places the created words in a
        'components' column of the dataframe.
        :return: Returns the dataframe with components added.
        """
        # self.df['components'] = self.df['compounds'].apply(lambda x: comp_split.dissect(x, self.ahocs, make_singular=True))
        self.df['components'] = self.df['compounds'].apply(lambda x: self.safe_dissect(x))
        return self.df

    def safe_dissect(self,word):
        try:
            result = comp_split.dissect(word, self.ahocs, only_nouns=False, make_singular=True)
        except IndexError:
            # self.exception_list.append(word)
            result = [CompSplitWrapper.EXCEPTION]
        return result


    @staticmethod
    def model_type():
        """
        Method to return type of model. Used for easier dynamic identification.
        :return: THe name of this model as a string.
        """
        return 'Compound_Splitter'

    def get_exception_list(self):
        return np.unique(self.exception_list)
#
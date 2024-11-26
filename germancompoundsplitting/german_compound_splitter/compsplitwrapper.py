import os
import numpy as np
import pandas as pd
from germancompoundsplitting.german_compound_splitter import comp_split
from typing_extensions import override
from germancompoundsplitting.model import Model


class CompSplitWrapper(Model):
    EXCEPTION = 'exception'

    def __init__(self):
        """
        Creates a wrapper object around comp_split.py. Used to make class usable for evaluator class.
        :param data: Dataframe with compound words to split in a column labeled 'compounds'.
        """
        super().__init__()
        self.name = 'Comp_Splitter'
        self.df = pd.DataFrame()
        curdir = os.path.dirname(os.path.abspath(__file__))
        self.input_file = os.path.join(curdir, "Dictionaries", "german.dic.txt")
        self.ahocs = comp_split.read_dictionary_from_file(self.input_file)
        self.exception_list = []
        self.only_nouns = False
        self.make_singular = False

    @override
    def run(self):
        """
        Runs the underlying model's splitting of compounds and places the created words in a
        'components' column of the dataframe.
        :return: Returns the dataframe with components added.
        """
        # self.df['components'] = self.df['compounds'].apply(lambda x: comp_split.dissect(x, self.ahocs, make_singular=True))
        print("Comp_split processing data")
        self.df['components'] = self.df['compounds'].apply(lambda x: self.safe_dissect(x))
        return self.df

    def set_mode(self, *, only_nouns = False, make_singular = False):
        """
        Method to set modes for comp_split.
        :param only_nouns: If components in the compounds are only nouns.
        :param make_singular: If found components should be made singular.
        """
        self.only_nouns = only_nouns
        self.make_singular = make_singular

    def safe_dissect(self, word):
        try:
            result = comp_split.dissect(word, self.ahocs, only_nouns= self.only_nouns, make_singular= self.make_singular)
        except IndexError:
            # self.exception_list.append(word)
            result = [CompSplitWrapper.EXCEPTION]
        return result

    def get_exception_list(self):
        return np.unique(self.exception_list)

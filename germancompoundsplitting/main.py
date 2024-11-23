import os

import pandas as pd

from germancompoundsplitting.Evaluator.Evaluator import Evaluator
from germancompoundsplitting.SMOR.smor import SMORWrapper
from germancompoundsplitting.data_preprocessing.data_preprocessing import GermanCompoundProcessor
from germancompoundsplitting.german_compound_splitter.compsplitwrapper import CompSplitWrapper
from germancompoundsplitting.mop_compound_splitter.mcswrapper import MCSWrapper


def main():
    sample_data_path = get_path_to_data('Sample_Data.pk1')
    sample_data = get_sample_data(sample_data_path, num_samples=1000)
    comp_splitter = CompSplitWrapper()
    smor = SMORWrapper()
    mcs = MCSWrapper()
    sample_evaluator = Evaluator(sample_data, [comp_splitter, smor, mcs])
    sample_metrics = sample_evaluator.evaluate(iterations=1)
    gold_standard_data = GermanCompoundProcessor.process_gold_standard((get_path_to_data('Ghost-NN_freq_prod_amb.txt')))
    comp_splitter.set_mode(only_nouns=True)
    gold_evaluator = Evaluator(gold_standard_data, [comp_splitter, smor, mcs])
    gold_metrics = gold_evaluator.evaluate(iterations=1)
    print('Sample dataset:')
    print(sample_metrics.to_string())
    print('GoldStandard dataset:')
    print(gold_metrics.to_string())


def get_path_to_data(file_name: str) -> os.path:
    """
    Creates OS-independent path to file. Must be located in datasets folder. Does not check if file exists.
    :param file_name: Filename to get filepath for.
    :return: OS-independent filepath.
    """
    curdir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(curdir, "Datasets", file_name)


def get_sample_data(file_path, num_samples=10):
    """
    Returns num_samples data from the pre-processed sample data if it exists. Pre-processed sample data is 1 million
    compounds out of a total of > 380 million compound words in gecodb_v01.tsv. Words only include alphabetical characters.
    If data has not been pre-processed, pre-processes data and saves via pickling to the file specified by filepath.
    :param file_path: File to get data from. Will process full-data and create this file if it does not exist.
    :param num_samples: The number of samples to return. Cannot be more than 1 million.
    :return: Dataframe containing num_samples of compound words, ignores original index.
    """
    if not os.path.exists(file_path):
        print("No processed data found. Processing data...")
        processor = GermanCompoundProcessor()
        curdir = os.path.dirname(os.path.abspath(__file__))
        dataset = os.path.join(curdir, "Datasets", "gecodb_v01.tsv")
        full_dataset = processor.process_file(dataset)
        sample_data = full_dataset.sample(n=1000000, random_state=42, ignore_index=True)
        sample_data.to_pickle(file_path)
    else:
        print("Processed data found. Loading data...")
        sample_data = pd.read_pickle(file_path)
    sample_data['targets'] = sample_data['targets'].apply(lambda x: [x] if type(x) == str else x)
    sample_data = sample_data.sample(n=num_samples, random_state=42, ignore_index=True)
    return sample_data


main()

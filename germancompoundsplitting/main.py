from germancompoundsplitting.Evaluator.Evaluator import Evaluator
from germancompoundsplitting.SMOR.smor import smor_wrapper
from germancompoundsplitting.german_compound_splitter.compsplitwrapper import CompSplitWrapper
from germancompoundsplitting.data_preprocessing.data_preprocessing import GermanCompoundProcessor
import pandas as pd
import os

def main():
    sample_data_path = get_path_to_data('Sample_Data.pk1')
    if not os.path.exists(sample_data_path):
        print("No processed data found. Processing data...")
        sample_data = process_data(sample_data_path)
    else:
        print("Processed data found. Loading data...")
        sample_data = pd.read_pickle(sample_data_path)
    sample_data['targets'] = sample_data['targets'].apply(lambda x: [x] if type(x) == str else x)
    sample_data = sample_data.sample(n=250, random_state=42,ignore_index = True)
    print(sample_data.head())
    print(sample_data.shape)
    comp_splitter = CompSplitWrapper()
    smor = smor_wrapper()
    myEvaluator = Evaluator(sample_data, [comp_splitter])
    metrics = myEvaluator.evaluate()
    print(comp_splitter.get_exception_list())
    print(metrics.to_string())


def get_path_to_data(file_name: str) -> os.path:
    curdir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(curdir, "Datasets", file_name)

def process_data(file_path):
    processor = GermanCompoundProcessor()
    curdir = os.path.dirname(os.path.abspath(__file__))
    dataset = os.path.join(curdir, "Datasets", "gecodb_v01.tsv")
    full_dataset = processor.process_file(dataset)
    sample_data = full_dataset.sample(n=1000000, random_state=42, ignore_index = True)
    sample_data.to_pickle(file_path)
    return sample_data

main()
from germancompoundsplitting.Evaluator.Evaluator import Evaluator
from germancompoundsplitting.data_preprocessing.data_preprocessing import GermanCompoundProcessor
import os

processor = GermanCompoundProcessor()
curdir = os.path.dirname(os.path.abspath(__file__))
dataset = os.path.join(curdir, "Datasets", "gecodb_v01.tsv")
output_df = processor.process_file(dataset)
print(output_df.head())


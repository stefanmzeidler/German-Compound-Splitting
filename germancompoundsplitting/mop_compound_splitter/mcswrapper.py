import os
import subprocess

import pandas as pd
from typing_extensions import override

from germancompoundsplitting.model import Model


class MCSWrapper(Model):
    def __init__(self):
        super().__init__()
        self.name = "MCS"

    @override
    def run(self):
        self.extract_components(self.process_compounds())
        return self.df

    def process_compounds(self):
        compounds_file = 'compounds.txt'
        output_label = 'components'
        output_file = compounds_file + '.' + output_label + '.SPLITS.tsv.trees'
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        compounds_file = os.path.join(cur_dir, 'compounds.txt')
        output_file = os.path.join(cur_dir, output_file)
        self.df['compounds'].to_csv(compounds_file, header=False, index=False)
        jar_file = os.path.join(cur_dir, 'MCS.jar')
        lemma_set = os.path.join(cur_dir, "Wikipedia.DE.LEMMASET.tsv")
        word_mops = os.path.join(cur_dir, "Wikipedia.DE.WORDMOPS.tsv")
        command = ["java", "-jar", jar_file, "--SPLIT", "--LEMMASET", lemma_set, "--modifierMOPs", word_mops,
                   "--headMOPs", word_mops, "--COLLECTION", compounds_file, "--OUTPUT", output_label]
        try:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                print("MCS is processing...")
                for line in process.stderr:  # Read error output line by line
                    print(line.strip())
        except FileNotFoundError as e:
            print(f"Error: {e}. File not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

        return output_file

    def extract_components(self, output_file):
        results = pd.read_csv(output_file, sep='\t', usecols=[4, 5], names=['compounds', 'components'])
        results.drop_duplicates(subset=['compounds'], keep='first', inplace=True)
        results['components'] = results['components'].apply(lambda x: x.split('|'))
        results.reset_index(drop=True, inplace=True)
        self.df['components'] = results['components']

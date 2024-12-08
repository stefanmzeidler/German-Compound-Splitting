import os
import subprocess
from typing_extensions import override
from germancompoundsplitting.model import Model
import pandas as pd


class SMORWrapper(Model):
    def __init__(self, df=None):
        super().__init__()
        self.df = df
        self.name = "SMOR"

    @override
    def run(self):
        return self.smor(self.df)

    @staticmethod
    def get_dir():
        file_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(file_directory, 'SMOR/')

    @staticmethod
    def smor(df):
        prevdir = os.getcwd()
        os.chdir(SMORWrapper.get_dir())
        df['compounds'].to_csv('compounds.txt', header=False, index=False)
        #e = subprocess.Popen(('echo', 'compounds.txt'), stdout=subprocess.PIPE)
        #e = subprocess.Popen(('echo', df['compounds'].str.cat(sep='\n')), stdout=subprocess.PIPE)
        #output = subprocess.check_output(os.path.abspath('smor-infl'), stdin=e.stdout).decode('utf-8')
        output = subprocess.check_output([os.path.abspath('smor-infl'), 'compounds.txt']).decode('utf-8')
        os.chdir(prevdir)

        subwords = []
        newword = False
        for line in output.splitlines():
            if newword:
                newword = False
                segment = ''
                wordSegments = []
                insegment = True
                for char in line:
                    if char == '<':
                        insegment = False
                        if len(segment) > 0:
                            wordSegments.append(segment)
                            segment = ''
                    elif insegment:
                        segment += char
                    elif char == '>':
                        insegment = True
                subwords.append(wordSegments)
            if line[:2] == '> ':
                newword = True

        df.insert(len(df.columns), 'components', subwords)
        return df


# testframe = pd.DataFrame({'compounds': ['Donaudampfschifffahrtskapitänsmützenabzeichen', 'Datensatz',
#                                         'Ablauforganisation', 'Einsatzfähigkeit', 'Heimspiel']})
# model_2 = smor_wrapper(testframe)
# print(model_2.run())
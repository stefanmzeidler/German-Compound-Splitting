import os
import subprocess
import pandas as pd


class smor_wrapper:
    def __init__(self, df):
        self.df = df

    def run(self):
        return self.smor(self.df)

    @staticmethod
    def get_dir():
        file_directory = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(file_directory, 'SMOR/')

    @staticmethod
    def smor(df):
        prevdir = os.getcwd()
        os.chdir(smor_wrapper.get_dir())
        # os.chdir(os.path.abspath('SMOR/'))
        e = subprocess.Popen(('echo', df['compounds'].str.cat(sep='\n')), stdout=subprocess.PIPE)
        output = subprocess.check_output(os.path.abspath('smor-infl'), stdin=e.stdout).decode('utf-8')
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


testframe = pd.DataFrame({'compounds': ['Donaudampfschifffahrtskapitänsmützenabzeichen', 'Datensatz',
                                        'Ablauforganisation', 'Einsatzfähigkeit', 'Heimspiel']})
model_2 = smor_wrapper(testframe)
print(model_2.run())
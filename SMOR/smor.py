import os
import subprocess
import pandas as pd

# testframe = pd.DataFrame({'compounds':['Donaudampfschifffahrtskapitänsmützenabzeichen','Abiturnote','Ablauforganisation','Einsatzfähigkeit','Heimspiel']})

def smor(df):
    prevdir = os.getcwd()
    os.chdir(os.path.abspath('SMOR/'))
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

testframe = pd.DataFrame({'compounds':['Donaudampfschifffahrtskapitänsmützenabzeichen','Abiturnote','Ablauforganisation','Einsatzfähigkeit','Heimspiel']})
print(smor(testframe))
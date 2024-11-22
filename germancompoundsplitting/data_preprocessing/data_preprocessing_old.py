import pandas as pd
import re

def is_invalid_noun(cell: str) -> bool:
    if pd.isna(cell):
        return True

    # Remove words starting with a hyphen (suffixes)
    if cell.startswith('-'):
        return True

    # Remove multi-word expressions (contains spaces)
    if ' ' in cell:
        return True

    # Remove single characters
    if len(cell) == 1:
        return True

    # Remove acronyms/all-caps words
    if cell.isupper():
        return True

    # Remove words containing numbers - causes file to be alphabetized
    if not cell.isalpha():
        return True

    # Remove mixed-case acronyms (e.g., BaFöG, AStA)
    mixed_case_acronym_pattern = r'^[A-ZÄÖÜ][a-zäöüß]*([A-ZÄÖÜ][a-zäöüß]*)+$'
    if re.match(mixed_case_acronym_pattern, cell):
        return True

    # Remove compound words (containing hyphens after cleaning numbers)
    cleaned = re.sub(r'^[^a-zA-ZäöüÄÖÜß]+', '', cell)
    if '-' in cleaned:
        return True

    return False

def clean_noun(cell: str) -> str:
    if not isinstance(cell, str):
        return cell
    return re.sub(r'^[^a-zA-ZäöüÄÖÜß]+', '', cell)

# Load each dataset
nouns_df = pd.read_csv('~/desktop/nouns.csv', encoding='utf-8-sig', low_memory=False)
ghost_df = pd.read_csv('~/desktop/Ghost-NN_freq_prod_amb.txt', sep='\t')

# Create separate dataframes for compound, modifier, and head
compounds = pd.DataFrame({'lemma': ghost_df['Compound']})
modifiers = pd.DataFrame({'lemma': ghost_df['Modifier']})
heads = pd.DataFrame({'lemma': ghost_df['Head']})

# Combine all dataframes
combined_df = pd.concat([nouns_df[['lemma']], compounds, modifiers, heads], ignore_index=True)

# Remove invalid nouns
df_cleaned = combined_df[~combined_df['lemma'].apply(is_invalid_noun)].copy()

# Clean remaining nouns by removing any non-alphabetic characters from the beginning of each word
df_cleaned['lemma'] = df_cleaned['lemma'].apply(clean_noun)

df_cleaned = df_cleaned.drop_duplicates()

df_cleaned.to_csv('~/desktop/cleaned_nouns.csv', index=False, encoding='utf-8-sig')
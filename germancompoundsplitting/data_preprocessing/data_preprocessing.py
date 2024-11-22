import pandas as pd
import time

class GermanCompoundProcessor:
    def __init__(self):
        self.umlaut_map = {
            'a': 'ä',
            'o': 'ö',
            'u': 'ü',
            'A': 'Ä',
            'O': 'Ö',
            'U': 'Ü'
        }

    def apply_umlaut(self, word):
        # Find a character that can be umlauted
        for i in range(len(word) - 1, -1, -1):
            if word[i] in self.umlaut_map:
                return word[:i] + self.umlaut_map[word[i]] + word[i + 1:]
        return word

    def apply_transformation_rules(self, parts):
        transformed_parts = []
        i = 0
        current_part = ""

        while i < len(parts):
            part = parts[i]

            # Process regular parts first (words that don't start with special modifiers)
            if not part.startswith('+') and not part.startswith('#') and not part.startswith(
                    '-') and not part.startswith('(') and not part.startswith('+='):
                if current_part:
                    transformed_parts.append(current_part)
                current_part = part

            # Handles deletions
            elif part.startswith('-'):
                if '+' in part:  # Replacement case
                    to_remove, to_add = part[1:].split('+')
                    if current_part.endswith(to_remove):
                        current_part = current_part[:-len(to_remove)] + to_add
                else:  # Simple deletion
                    to_remove = part[1:]
                    if current_part.endswith(to_remove):
                        current_part = current_part[:-len(to_remove)]

            # Handles umlaut triggers
            elif part.startswith('+='):
                current_part = self.apply_umlaut(current_part)
                if len(part) > 2:  # If there's additional content after +=
                    current_part += part[2:]

            # Handles parenthesis when linking nouns
            elif part.startswith('('):
                content = part[1:-1]  # Remove the parentheses
                current_part += content

            # Handles appending nouns
            elif part.startswith('+'):
                current_part += part[1:]

            # Handles omitted endings
            elif part.startswith('#'):
                ending = part[1:]
                if current_part.endswith(ending):
                    current_part = current_part[:-len(ending)]

            # If we've processed all special markers for this part
            if i + 1 == len(parts) or (not parts[i + 1].startswith('+') and
                                       not parts[i + 1].startswith('#') and
                                       not parts[i + 1].startswith('-') and
                                       not parts[i + 1].startswith('(') and
                                       not parts[i + 1].startswith('+=')):
                if current_part:
                    transformed_parts.append(current_part)
                    current_part = ""

            i += 1

        if current_part:
            transformed_parts.append(current_part)

        return transformed_parts

    def merge_compound(self, parts):
        transformed_parts = self.apply_transformation_rules(parts)

        # For the final merged word, capitalize only the first part
        # and lowercase the rest
        if len(transformed_parts) > 0:
            result = transformed_parts[0]
            for part in transformed_parts[1:]:
                result += part.lower()
            return result
        return ""

    def process_compound(self, noun):
        # Skip hyphenated compounds
        if '--' in noun:
            return []

        parts = noun.split('_')

        compound_results = []

        # Get constituents (excluding special markers)
        constituents = []
        for part in parts:
            if not (part.startswith('+') or part.startswith('#') or
                    part.startswith('-') or part.startswith('(') or
                    part.startswith('+=')):
                constituents.append(part)
                compound_results.append({
                    'compounds': part,
                    'targets': part
                })

        # Add the merged compound
        merged = self.merge_compound(parts)
        compound_results.append({
            'compounds': merged,
            'targets': constituents
        })

        return compound_results

    def process_file(self, input_file):
        # Read TSV file - first column only
        input_nouns = pd.read_csv(input_file, sep='\t', header=None, usecols=[0])

        # Process all compounds
        all_results = []
        for compound in input_nouns[0]:
            results = self.process_compound(compound)
            if results:  # Only add if not empty (i.e., not hyphenated)
                all_results.extend(results)

        results_df = pd.DataFrame(all_results)
        return results_df

# pd.set_option('display.max_rows', None)
# pd.reset_option('display.max_rows')
# processor = GermanCompoundProcessor()
#
# start_time = time.time()
# output_df = processor.process_file('~/desktop/gecodb_v01.tsv')
# print(f"Processing time: {time.time() - start_time:.2f} seconds")
#
# print(output_df.head())
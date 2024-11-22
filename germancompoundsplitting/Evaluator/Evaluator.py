from germancompoundsplitting.german_compound_splitter.comp_split import read_dictionary_from_file
from germancompoundsplitting.german_compound_splitter.compsplitwrapper import CompSplitWrapper
from germancompoundsplitting.SMOR.smor import smor_wrapper
from sklearn.utils import shuffle
from collections import defaultdict
import pandas as pd
import numpy as np
import time
import gc
import os


class Evaluator:
    nanoseconds_to_milliseconds = 1000000

    def __init__(self, df, models, splits=None):
        """
        Evaluator object to evaluate models on accuracy and efficiency for splitting German compound nouns. Data is
        shuffled to avoid any folds that are particularly hard or easy, but using a random seed for reproducibility.
        :param df: The data to use in the evaluation. Should have a column for 'compounds' and for 'targets',
        where targets is the list of components of the compound words.
        :param models: The models to compare. Must take a dataframe as their constructor parameter and have a run method
        adds the predicted splits to the dataframe and returns it.
        :param splits: The number of splits for the dataset. E.g., 10 splits would mean the first 10% of the data,
        then the first 20%, then the first 30%, etc.
        """
        if df is None or models is None:
            raise ValueError('Data or models cannot be none')
        if splits is None:
            splits = min(len(df), 10)
        self.sample_data = pd.DataFrame(shuffle(df, random_state=42))
        self.sample_data.reset_index(inplace=True, drop=True)
        self.indices = np.linspace(start=1, stop=len(self.sample_data) - 1, num=splits, dtype=int)
        self.models = models
        self.metrics = pd.DataFrame()
        self.incorrect_words = defaultdict(list)

    def evaluate(self, iterations=10):
        """
        Evaluates the models given to the instance for average time over each split for <iterations>.
        Also gives the accuracy, precision, recall, and F1 scores, as well as the individual values for
        each type of classification over the whole dataset.
        :param iterations:
        :return: A dataframe containing the results of the evaluation.
        """
        metrics_dict = defaultdict(list)
        results = pd.DataFrame()
        for model in self.models:
            metrics_dict['Model'].append(model.model_type())
            elapsed_time = 0
            for index in self.indices:
                for i in range(iterations):
                    gc.collect()
                    model.df = self.sample_data.copy().head(index)
                    start = time.process_time_ns()
                    results = model.run()
                    stop = time.process_time_ns()
                    elapsed_time += stop - start
                average_time = (elapsed_time / iterations) / Evaluator.nanoseconds_to_milliseconds
                metrics_dict[f'Time for {str(index + 1)} words'].append(average_time)
            scores = self.__score(results)
            for metric, score in scores.items():
                metrics_dict[metric].append(score)
        self.metrics = pd.DataFrame(metrics_dict)
        print(self.metrics.to_string())
        return self.metrics

    def __score(self, results):
        """
        Scores the results of model after splitting compound words.
        :param results: The dataframe containing the compound words, the target component words, and the predicted component words.
        :return: Returns a dictionary item with each of the measures, metrics, and scores.
        """
        labels = ['true_positives', 'false_positives', 'true_negatives', 'false_negatives', 'oversplit', 'undersplit',
                  'incorrect_components', 'exceptions']
        results[labels] = results.apply(
            lambda row: self.__score_helper(row['components'], row['targets']), axis=1)
        score_dict = defaultdict(list)
        for label in labels:
            score_dict[label].append(results[label].sum())
        true_positives = score_dict['true_positives'][0]
        false_positives = score_dict['false_positives'][0]
        true_negatives = score_dict['true_negatives'][0]
        false_negatives = score_dict['false_negatives'][0]
        accuracy = (true_positives + true_negatives) / (
                    true_positives + true_negatives + false_positives + false_negatives)
        score_dict['accuracy'].append(accuracy)
        precision = true_positives / (true_positives + false_positives)
        score_dict['precision'].append(precision)
        recall = true_positives / (true_positives + false_negatives)
        score_dict['recall'].append(recall)
        f1 = ((precision * recall) / (precision + recall)) * 2
        score_dict['F1'].append(f1)
        return score_dict

    def __score_helper(self, components, targets):
        """
        Helper method computes the number of true positive, true negative, false positive and false negative words.
        Also indicates whether there was oversplitting, undersplitting, or incorrect components.
        True positives are considered predicted words that match a target word.
        True negatives are words simple word that have not been split.
        False positives and false negatives are a bit trickier to define.  For the purposes of this
        evaluation, false positives are incorrectly predicted words when oversplitting occurs. I.e., when the model
        predicts more components than there should be. In the case of undersplitting, we first calculate the number
        of incorrect words. The amount of false negatives, words that should have been split but were not, is the
        total amount of target words minus the total predicted words minus any true positives. Then false positives
        are any remaining incorrect words minus false negatives. This is because some of the incorrect words could have
        been part of a correct split, but a false positive in the sense that the wrong component was selected.

        :param components: Predicted components
        :param targets: Actual components
        :return: The scores for this compound word.
        """
        exception = False
        true_positives = true_negatives = false_negatives = false_words = oversplit = undersplit = incorrect_components = exceptions = 0
        components = [word.lower() for word in components]
        targets = [word.lower() for word in targets]
        total_predictions = len(components)
        total_targets = len(targets)
        if total_predictions > total_targets:
            oversplit = 1
        elif total_targets > total_predictions:
            undersplit = 1
        for component in components:
            if component == CompSplitWrapper.EXCEPTION:
                exceptions += 1
                exception = True
                break
            elif component in targets:
                if total_targets == 1:
                    true_negatives += 1
                else:
                    true_positives += 1
            else:
                print(f"found: {component} Expected: {targets}")
                false_words += 1
        if exception:
            # In order for stat calculations to not divide by zero.
            false_positives = 1
            false_negatives = 1
        else:
            if undersplit > 0:
                false_negatives = total_targets - total_predictions - true_positives
                false_positives = false_words - false_negatives
                assert (false_words == false_positives + false_negatives)
            else:
                false_positives = false_words
            if true_positives != total_targets and oversplit == 0 and undersplit == 0:
                incorrect_components += 1
                self.incorrect_words['components'].append(components)
                self.incorrect_words['targets'].append(targets)
        return pd.Series([true_positives, false_positives, true_negatives, false_negatives, oversplit, undersplit,
                          incorrect_components, exceptions])


def main():
    testframe = pd.DataFrame(
        {'compounds': ['Fernsehen'],
         'targets': ['Fernsehen']})

    testframe2 = pd.DataFrame(
        {'compounds': ['Datensatz','Fernsehen'],
         'targets': [['Datum', 'Satz'], ['Fernsehen']]})
    # print(testframe)
    comp_splitter = CompSplitWrapper()
    smor = smor_wrapper()
    # myEvaluator = Evaluator(testframe, [comp_splitter])
    myEvaluator = Evaluator(testframe, [comp_split, smor])
    myEvaluator.evaluate()
    print(comp_splitter.get_exception_list())




# main()

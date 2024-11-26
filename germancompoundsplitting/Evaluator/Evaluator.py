import gc
import time
from collections import defaultdict
import numpy as np
import pandas as pd
import spacy
from sklearn.utils import shuffle

from germancompoundsplitting.german_compound_splitter.compsplitwrapper import CompSplitWrapper
from germancompoundsplitting.model import Model

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
        self.split_indices = np.linspace(start=1, stop=len(self.sample_data) - 1, num=splits, dtype=int)
        self.models = models
        self.metrics = pd.DataFrame()
        self.incorrect_words = defaultdict(list)
        self.nlp = spacy.load("de_core_news_md")

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
            temp_dict = defaultdict(list)
            try:
                temp_dict['Model'].append(model.model_type())
                for index in self.split_indices:
                    average_time, results = self.__get_average_time(model,index, iterations)
                    temp_dict[f'Time for {str(index)} words'].append(average_time)
                print(f"Scoring {model.model_type()}")
                scores = self.__score(results)
                for metric, score_vals in scores.items():
                    for score_val in score_vals:
                        temp_dict[metric].append(score_val)
            except Exception as e:
                print(f"{model.model_type()} encountered an error at {time.ctime()}. Data not processed.")
                print(type(e))
                print(e)
                continue
            for key,values in temp_dict.items():
                for value in values:
                    metrics_dict[key].append(value)
        self.metrics = pd.DataFrame(metrics_dict)
        return self.metrics


    def __get_average_time(self, model,index,iterations):
        elapsed_time = 0
        results = None
        for i in range(iterations):
            gc.collect()
            model.set_data(self.sample_data.copy().head(index))
            start = time.time_ns()
            results = model.run()
            stop = time.time_ns()
            elapsed_time += stop - start
        average_time = (elapsed_time / iterations) / Evaluator.nanoseconds_to_milliseconds
        return average_time,results

    def __score(self, results):
        """
        Scores the results of model after splitting compound words.
        :param results: The dataframe containing the compound words, the target component words, and the predicted component words.
        :return: Returns a dictionary item with each of the measures, metrics, and scores.
        """
        labels = ['true_positives', 'false_positives', 'true_negatives', 'false_negatives', 'oversplit', 'undersplit',
                  'incorrect_components', 'exceptions']
        results.dropna()
        self.__lemmatize(results)
        results[labels] = results.apply(lambda row: self.__score_helper(row['components'], row['targets']), axis=1)
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
                # print(f"found: {component} Expected: {targets}")
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

    def __lemmatize(self, results):
        """
        Lemmatizes the text in targets and components column of a dataframe. Must have already been run through a model.
        """
        for column in ['targets', 'components']:
            results[column] = results[column].apply(lambda x: self.lemmatize_helper(x))

    def lemmatize_helper(self, text):
        """
        Helper method to lemmatize text.
        :param text: Text to lemmatize
        :return: List containing lemmatized words.
        """
        if not isinstance(text, list):
            return [Model.EXCEPTION]
        lemma = []
        for word in text:
            doc = self.nlp(word)
            for doc_word in doc:
                lemma.append(doc_word.lemma_)
        return lemma


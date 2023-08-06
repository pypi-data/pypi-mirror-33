"""
coding=utf-8

"""


__author__ = 'Sekou Diao'

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import precision_recall_fscore_support
from sklearn.tree import DecisionTreeClassifier
from sklearn.tree import export_graphviz, _tree

import random
import numpy as np
# numpy removed for azure compatibility
from collections import defaultdict, OrderedDict
import six
import time



class EndingCountVectorizer(CountVectorizer):
    def _char_ngrams(self, text_document):
        """Tokenize text_document into a sequence of ending character n-grams"""
        # normalize white spaces
        text_document = self._white_spaces.sub(" ", text_document)

        text_len = len(text_document)
        ngrams = []
        min_n, max_n = self.ngram_range
        for n in range(min_n, min(max_n + 1, text_len + 1)):
            ngram = text_document[-n:]
            ngrams.append(ngram)
            # if ngram in self.vocabulary:
            # ngrams.append(ngram)
        return ngrams


class CustomCountVectorizer(CountVectorizer):
    def _char_ngrams(self, text_document):
        """Tokenize text_document into a sequence of character n-grams"""
        # normalize white spaces
        text_document = self._white_spaces.sub(" ", text_document)

        text_len = len(text_document)
        ngrams = []
        min_n, max_n = self.ngram_range
        for n in range(min_n, min(max_n + 1, text_len + 1)):
            for i in range(text_len - n + 1):
                ngram = text_document[i: i + n]
                if ngram in self.vocabulary:
                    ngrams.append(ngram)
        return ngrams

class DataSet:
    def __init__(self, VerbisteObj):
        """

        :param VerbisteObj:
        
        :return:
        """
        self.verbiste = VerbisteObj
        self.verbes = self.verbiste.verbes.keys()
        self.templates = sorted(self.verbiste.conjugaisons.keys())
        self.liste_verbes = []
        self.liste_templates = []
        self.dict_conjug = []
        self.train_input = []
        self.train_labels = []
        self.test_input = []
        self.test_labels = []
    
    def construct_dict_conjug(self):
        conjug = defaultdict(list)
        for verbe, info_verbe in self.verbiste.verbes.items():
            self.liste_verbes.append(verbe)
            self.liste_templates.append(self.templates.index(info_verbe["template"]))
            conjug[info_verbe["template"]].append(verbe)
        self.dict_conjug = conjug
        return
        
    
    def split_data(self, threshold=8, proportion=0.5):
        # Create train and test sets
        # TODO attraper exception quand proportion < 0 oo > 1
        self.min_threshold = threshold
        self.split_proportion = proportion
        train_set = []
        test_set = []
        for template, lverbes in self.dict_conjug.items():
            if len(lverbes) <= threshold:
                for verbe in lverbes:
                    train_set.append((verbe, template))
            else:
                index = round(len(lverbes) * proportion)
                for verbe in lverbes[:index]:
                    train_set.append((verbe, template))
                for verbe in lverbes[index:]:
                    test_set.append((verbe, template))        
        random.shuffle(train_set)
        random.shuffle(test_set)        
        self.train_input = [elmt[0] for elmt in train_set]
        self.train_labels = [self.templates.index(elmt[1]) for elmt in train_set]
        self.test_input = [elmt[0] for elmt in test_set]
        self.test_labels = [self.templates.index(elmt[1]) for elmt in test_set]
        return


def train_and_predict(classifier, dataset, train, test, ngrange):
    print("training {0} conjugator model:\n\n".format(type(classifier).__name__))
    print((ngrange, classifier.get_params()))
    start_time = time.clock()
    classifier = classifier.fit(train, dataset.train_labels)
    duration = round(time.clock() - start_time, 2)
    print("{0} conjugator model has been trained in {1} seconds.\n\n".format(type(classifier).__name__, duration))
    print("###########################################################\n\n")
    print("{0} conjugator model starting predictions:\n\n".format(type(classifier).__name__))
    predicted = classifier.predict(test)
    print("{0} conjugator model has finihed making predictions:\n\n".format(type(classifier).__name__))
    scores = {}
    scores['precision'], scores['recall'], scores['fbeta-score'], scores['support'] = precision_recall_fscore_support(dataset.test_labels, predicted)
    erreurs = [(verbe, dataset.templates[elmt], dataset.templates[cat]) for verbe, elmt, cat in
                zip(dataset.test_input, predicted, dataset.test_labels) if elmt != cat]
    correct_predictions = [(verbe, dataset.templates[elmt], dataset.templates[cat]) for verbe, elmt, cat in
                           zip(dataset.test_input, predicted, dataset.test_labels) if elmt == cat]
    mean_prediction = np.mean(predicted == dataset.test_labels)
    if isinstance(classifier, DecisionTreeClassifier):
        # les coeffs et les scores ne sont pas serializables sous json donc pour l'instant on les enleve
        # result_names = ('classifier', 'ngram_range', 'min_threshold', 'split_proportion', 'classifier_parameters', 'prediction_accuracy', 'correct_predictions', 'classification_errors', 'stat_infos', 'training_duration')
        # results = (str(type(classifier).__name__), ngrange, dataset.min_threshold, dataset.split_proportion, classifier.get_params(), mean_prediction, correct_predictions,
        #                                 erreurs, scores, duration)
        result_names = ('classifier', 'ngram_range', 'min_threshold', 'split_proportion', 'classifier_parameters',
                        'prediction_accuracy', 'correct_predictions', 'classification_errors', 'training_duration')
        results = (str(type(classifier).__name__), ngrange, dataset.min_threshold, dataset.split_proportion,
                   classifier.get_params(), mean_prediction, correct_predictions,
                   erreurs, duration)
    else:
        # les coeffs et les scores ne sont pas serializables sous json donc pour l'instant on les enleve
        # result_names = ('classifier', 'ngram range', 'min threshold', 'split proportion', 'classifier parameters', 'prediction accuracy', 'feature weights', 'correct_predictions', 'classification errors', 'stat infos', 'training duration')
        # results = (str(type(classifier).__name__), ngrange, dataset.min_threshold, dataset.split_proportion, classifier.get_params(), mean_prediction, classifier.coef_, correct_predictions,
        #                                 erreurs, scores, duration)
        result_names = ('classifier', 'ngram_range', 'min_threshold', 'split_proportion', 'classifier_parameters',
                        'prediction_accuracy', 'correct_predictions', 'classification_errors', 'training_duration')
        results = (str(type(classifier).__name__), ngrange, dataset.min_threshold, dataset.split_proportion,
                   classifier.get_params(), mean_prediction, correct_predictions,
                   erreurs, duration)
    dict_results = OrderedDict(zip(result_names, results))
    print((type(classifier).__name__, mean_prediction,
           "{0} errors out of {1} guesses".format(len(dict_results['classification_errors']),
                                                  len(dict_results['correct_predictions'])), classifier.get_params()))
    print("\n\n")
    print("###########################################################\n\n")
    return dict_results

def custom_export_graphviz(decision_tree, out_file="tree.dot", feature_names=None,
                    max_depth=None, label_names=None):
    """Export a decision tree in DOT format.

    Custom implementation to label nodes according to the verbe terminaisons
    """
    def node_to_str(tree, node_id, criterion):
        if not isinstance(criterion, six.string_types):
            criterion = "impurity"

        value = tree.value[node_id]
        if tree.n_outputs == 1:
            value = value[0, :]
            if label_names is not None:
                labels = [label_names[i] for i, elmt in enumerate(value) if elmt >0]
            else:
                labels = [i for i, elmt in enumerate(value)if elmt > 0]

        if tree.children_left[node_id] == _tree.TREE_LEAF:
            return "%s = %.4f\\nsamples = %s\\nlabel = %s" \
                   % (criterion,
                      tree.impurity[node_id],
                      tree.n_node_samples[node_id],
                      " / ".join(labels))
        else:
            if feature_names is not None:
                feature = feature_names[tree.feature[node_id]]
            else:
                feature = "X[%s]" % tree.feature[node_id]

            return "ends with %s ?\\n%s = %s\\nsamples = %s" \
                   % (feature,
                      criterion,
                      tree.impurity[node_id],
                      tree.n_node_samples[node_id])

    def recurse(tree, node_id, criterion, parent=None, depth=0):
        if node_id == _tree.TREE_LEAF:
            raise ValueError("Invalid node_id %s" % _tree.TREE_LEAF)

        left_child = tree.children_left[node_id]
        right_child = tree.children_right[node_id]

        # Add node with description
        if max_depth is None or depth <= max_depth:
            out_file.write('%d [label="%s", shape="box"] ;\n' %
                           (node_id, node_to_str(tree, node_id, criterion)))

            if parent is not None:
                # Add edge to parent
                out_file.write('%d -> %d ;\n' % (parent, node_id))

            if left_child != _tree.TREE_LEAF:
                recurse(tree, left_child, criterion=criterion, parent=node_id,
                        depth=depth + 1)
                recurse(tree, right_child, criterion=criterion, parent=node_id,
                        depth=depth + 1)

        else:
            out_file.write('%d [label="(...)", shape="box"] ;\n' % node_id)

            if parent is not None:
                # Add edge to parent
                out_file.write('%d -> %d ;\n' % (parent, node_id))

    own_file = False
    try:
        if isinstance(out_file, six.string_types):
            if six.PY3:
                out_file = open(out_file, "w", encoding="utf-8")
            else:
                out_file = open(out_file, "wb")
            own_file = True

        out_file.write("digraph Tree {\n")

        if isinstance(decision_tree, _tree.Tree):
            recurse(decision_tree, 0, criterion="impurity")
        else:
            recurse(decision_tree.tree_, 0, criterion=decision_tree.criterion)
        out_file.write("}")

    finally:
        if own_file:
            out_file.close()



export_graphviz = custom_export_graphviz
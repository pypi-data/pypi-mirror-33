# encoding: utf-8
"""
wordmatch.py
~~~~~~~~~~~~

Implements key-word based topic labelling classifier

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-07"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import types

# third party imports
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, ClassifierMixin

# local imports
from atnlp.core.logger import log, title_break

# globals


class WordMatchClassifier(BaseEstimator, ClassifierMixin):
    """Keyword based binary topic classifier

    The classifier works by assigning the positive class to
    any example that contains any of the given keywords.
    It is assumed the input data is in the bag-of-words format.

    The set of keywords is fit to the training data using the
    following algorithm. Initially, a single keyword that
    maximises $rp^4$ is selected, where $r$ is recall and $p$
    is precision. The choice $p^4$ is made to strongly penalise
    false positives. This process is repeated, adding keywords
    until the metric decreases.

    TODO: allow predefinition of keywords, that would then be built on?
    TODO: include max number of words as hyperparameter

    :param df_threshold: minimum document frequency for keywords
    """
    def __init__(self, df_threshold=0.1):
        self.df_threshold = df_threshold

        self._keywords = None

    def fit(self, X, y):
        """Fit model to data

        :param X: data (bag-of-words format)
        :param y: binary classification labels
        """
        def next_best_word(X_sig_, X_bkg_, words):
            # get decision from existing words
            mask_sig = self._word_based_predict(X_sig_, words)
            mask_bkg = self._word_based_predict(X_bkg_, words)

            # calculate tp and fp from existing mask
            tp_base = np.sum(mask_sig)
            fp_base = np.sum(mask_bkg)

            # calculate tp/fn/fp arrays for each word (accounting for mask contributions)
            tp = np.sum(X_sig_[~mask_sig] > 0, axis=0) + tp_base
            fn = np.sum(X_sig_[~mask_sig] == 0, axis=0)
            fp = np.sum(X_bkg_[~mask_bkg] > 0, axis=0) + fp_base
            recall = tp / (tp + fn)
            precision = tp / (tp + fp)
            score = recall * np.power(precision, 4)

            # select best scorer
            i = np.argsort(score)[::-1][0]
            return (i, score[i])


        # convert sparse-matrix from BOW into standard matrix
        # (probably inefficient, but the sparse matrix exhibits
        #  a lot of non-intuitive behavior that ultimately leads
        #  to bugs)
        if hasattr(X, 'toarray') and isinstance(X.toarray, types.MethodType):
            X = X.toarray()

        # signal/background datasets
        X_sig = X[y.astype(np.bool)]
        X_bkg = X[~y.astype(np.bool)]

        # select words with document frequency above threshold
        word_mask = np.sum(X_sig > 0, axis=0) > (self.df_threshold * np.sum(y))
        X_sig = X_sig[:, word_mask]
        X_bkg = X_bkg[:, word_mask]

        # iteratively add keywords until optimisation score decreases
        keyword_indices_in_mask = []
        score = None
        while True:
            (w, s) = next_best_word(X_sig, X_bkg, keyword_indices_in_mask)
            if score is None or s > score:
                keyword_indices_in_mask.append(w)
                score = s
            else:
                break

        self._keywords = list(np.arange(X.shape[1])[word_mask][keyword_indices_in_mask])

    def predict(self, X):
        """

        :param X:
        :return:
        """
        if hasattr(X, 'toarray') and isinstance(X.toarray, types.MethodType):
            X = X.toarray()

        return self._word_based_predict(X, self._keywords)

    def decision_function(self, X):
        return self.predict(X)

    def _word_based_predict(self, X, keyword_indices):
        """Return single-class membership prediction based on `keyword_indices`
        (if match to any keyword then return True, otherwise False)

        Will return all false if `keyword_indices` is empty

        :param X: BOW matrix
        :param keyword_indices: indices of keywords in X
        :return: np.array (size `n` where n is rows in X)
        """
        # stack predictions for each word in rows
        # (zeros row in case keyword_indices is empty)
        y_per_word = np.vstack(
            [np.zeros(X.shape[0])] + [X[:, i] > 0 for i in keyword_indices]
        )

        # build logical or from rows
        return np.any(y_per_word, axis=0)


def display_keywords(model, topic_names, vocab):
    """Print keywords for WordMatchClassifier instances in OneVsRestClassifier

    :param model: OneVsRestClassifier containing WordMatchClassifier instances
    :param topic_names: topic for each model instance in OneVsRest
    :param vocab: id-to-word dictionary for bag-of-words input data
    """
    title_break('Topic Keywords')
    for (i, t) in enumerate(topic_names):
        keywords = vocab[model.estimators_[i]._keywords]
        log().info("{:20s}: {}".format(t, keywords))


def get_keyword_dataframe(model, topic_names, vocab):
    """Return pandas DataFrame with keywords for WordMatchClassifier instances in OneVsRestClassifier

    :param model: OneVsRestClassifier containing WordMatchClassifier instances
    :param topic_names: topic for each model instance in OneVsRest
    :param vocab: id-to-word dictionary for bag-of-words input data
    :return: pandas DataFrame
    """
    return pd.DataFrame({
        'topic': topic_names,
        'keywords': [', '.join(vocab[eval._keywords]) for eval in model.estimators_]
    })[['topic', 'keywords']]


# EOF
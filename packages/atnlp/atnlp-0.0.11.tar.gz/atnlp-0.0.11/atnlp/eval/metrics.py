# encoding: utf-8
"""
metrics.py
~~~~~~~~~~

Functionality for computing performance metrics. Typically custom metrics not provided by sklearn.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-30"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 

# third party imports
import numpy as np

# local imports

# globals


def recall_all_score(Y_true, Y_pred):
    """Return the 'recall all' score

    'Recall all' is defined as::

        score := number of examples with all labels correct / number of examples

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :return: recall all score
    """
    Y_true = Y_true.as_matrix()
    matches = np.all(Y_true == Y_pred, axis=1)
    return np.sum(matches) / len(matches)


def flpd_score(Y_true, Y_pred):
    """Return 'false labels per document' score

    'False labels per document' is defined as::

        score := total number of false labels / number of examples

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :return: false labels per document score
    """
    Y_true = Y_true.as_matrix()
    return np.sum(Y_pred & ~Y_true) / Y_true.shape[0]


def mlpd_score(Y_true, Y_pred):
    """Missing labels per document score

    'Missing labels per document' is defined as::

        score := total number of missing labels / number of examples

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :return: missing labels per document score
    """
    Y_true = Y_true.as_matrix()
    return np.sum(~Y_pred & Y_true) / Y_true.shape[0]

# EOF
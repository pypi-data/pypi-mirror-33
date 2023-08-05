# encoding: utf-8
"""
io.py
~~~~~

Functionality for reading and writing datasets

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-07"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 

# third party imports
import pandas as pd
import numpy as np

# local imports

# globals


def write_raw(X, filename):
    """Write raw text data to file

    :param X: list of strings
    :param filename: name of output file
    """
    with open(filename, 'w') as f:
        for l in X:
            l = repr(l.encode('utf-8'))
            f.write(l)
            f.write('\n')


def read_raw(filename):
    """Read raw text data from file

    :param filename: name of input file
    :return: list of strings
    """
    with open(filename, 'r') as f:
        X = f.readlines()
    return X


def write_one_hot_labels(Y, filename):
    """Write topic labels to file in one-hot form

    :param Y: topic labels (one-hot DataFrame, M x N)
    :param filename: name of output file
    """
    if not isinstance(Y, pd.DataFrame):
        df = pd.DataFrame(Y)
        df.to_csv(filename, index=False, header=False)
    else:
        Y.to_csv(filename, index=False)


def read_one_hot_labels(filename):
    """Read topic labels from file in one-hot form

    :param filename: name of input file
    :return: topic labels (one-hot DataFrame, M x N)
    """
    return pd.read_csv(filename, dtype=np.bool)


# EOF
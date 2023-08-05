# encoding: utf-8
"""
reuters.py
~~~~~~~~~~

Functionality to read in Reuters corpus using the nltk module

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-05"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports

# third party imports
from nltk.corpus import reuters
import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

# local imports

# globals


def get_data(cats=None, tokenize=None):
    """Return raw text data from Reuters corpus in (train, test) tuple

    If *cats* is specified, data is filtered to only contain documents
    from the specified categories.

    If *tokenize* is specified, data is tokenized.

    :param cats: categories
    :param tokenize: tokenization function
    :return: tuple of (train, test) data (each is list of strings)
    """
    return (get_data_train(cats,tokenize=tokenize), get_data_test(cats,tokenize=tokenize))


def get_labels(cats=None):
    """Return topic labels (one-hot format) from Reuters corpus in (train, test) tuple

    :param cats: categories
    :return: tuple of (train, test) topic labels (one-hot format)
    """
    return (get_labels_train(cats), get_labels_test(cats))


def get_data_train(cats=None, tokenize=None):
    """Return raw text training data (cf *get_data*)

    :param cats: categories
    :param tokenize: tokenization function
    :return: train data (list of strings)
    """
    return ReutersIter(train_filenames(cats=cats), tokenize=tokenize)


def get_data_test(cats=None, tokenize=None):
    """Return raw text testing data (cf *get_data*)

    :param cats: categories
    :param tokenize: tokenization function
    :return: test data (list of strings)
    """
    return ReutersIter(test_filenames(cats=cats), tokenize=tokenize)


def get_labels_train(cats=None):
    """Return training set topic labels (one-hot format) from Reuters corpus (cf *get_labels*)

    :param cats: categories
    :return: train topic labels (one-hot format)
    """
    return labels(train_filenames(cats), cats=cats)


def get_labels_test(cats=None):
    """Return testing set topic labels (one-hot format) from Reuters corpus (cf *get_labels*)

    :param cats: categories
    :return: test topic labels (one-hot format)
    """
    return labels(test_filenames(cats), cats=cats)


def get_topics(min_samples=None):
    """Return set of topics from Reuters corpus

    If *min_samples* is specified, only topics with at
    least that many examples are included.

    :param min_samples: minimum number of example per topic
    :return: list of topics
    """
    cats = reuters.categories()
    if min_samples is not None:
        cats = [c for c in reuters.categories() if len(reuters.fileids(c)) >= min_samples]
    return cats


def train_filenames(cats=None):
    """Return filenames of training examples

    If *cats* is specified, filenames are filtered to only contain documents
    from the specified categories.

    :param cats: categories
    :return: list of filenames
    """
    return np.array([f for f in reuters.fileids(cats) if f.startswith('train')])


def test_filenames(cats=None):
    """Return filenames of testing examples

    If *cats* is specified, filenames are filtered to only contain documents
    from the specified categories.

    :param cats: categories
    :return: list of filenames
    """
    return np.array([f for f in reuters.fileids(cats) if f.startswith('test')])


def labels(filenames, cats=None):
    """Return topic labels (one-hot format) for given files

    :param filenames: selected files from Reuters dataset
    :param cats: categories to filter (optional)
    :return: topic labels (one-hot format)
    """
    if cats is None: cats = reuters.categories()
    data = [[c for c in reuters.categories(f) if c in cats] for f in filenames]
    mb = MultiLabelBinarizer(classes = cats)
    onehot = mb.fit_transform(data)
    df = pd.DataFrame(onehot, columns=cats)
    return df


class ReutersIter(object):
    """Reuters dataset iterator

    Implements generator instead of reading full dataset into memory.
    However, its not super necessary coz this dataset is small, and
    most of the time we actually create a list from this anyway.

    :param files: list of files to iterate over
    :param tokenize: tokenization function (optional)
    """
    def __init__(self, files, tokenize=None):
        self.files = files
        self.tokenize = tokenize

    def __iter__(self):
        for i in range(len(self.files)):
            yield self[i]

    def __getitem__(self, key):
        data = reuters.raw(self.files[key])
        if self.tokenize is None:
            return data
        return self.tokenize(data)


# EOF
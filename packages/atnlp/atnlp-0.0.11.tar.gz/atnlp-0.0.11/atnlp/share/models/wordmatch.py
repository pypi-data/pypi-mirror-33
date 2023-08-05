# encoding: utf-8
"""
wordmatch.py
~~~~~~~~~~~~

Pipeline converting raw text to sparse bag-of-words representation and feeding to
a custom key-word based topic labelling model.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-07"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# imports
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.multiclass import OneVsRestClassifier
from atnlp.model.wordmatch import WordMatchClassifier

model = Pipeline([
    ('bow', CountVectorizer()),
    ('wmc', OneVsRestClassifier(WordMatchClassifier())),
    ])

# EOF
# encoding: utf-8
"""
svm.py
~~~~~~

Pipeline converting raw text to sparse tfidf representation and feeding to
a support vector machine for topic labelling.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-07"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# imports
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import SVC

# model
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('svc', OneVsRestClassifier(SVC())),
    ])

# EOF
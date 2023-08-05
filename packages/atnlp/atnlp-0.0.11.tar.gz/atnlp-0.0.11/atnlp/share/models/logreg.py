# encoding: utf-8
"""
logreg.py
~~~~~~~~~

Pipeline converting raw text to sparse tfidf representation and feeding to
logistic regression for topic labelling.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-12"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# imports
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

# model
model = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('logreg', OneVsRestClassifier(LogisticRegression())),
    ])

# EOF
# encoding: utf-8
"""
keras.py
~~~~~~~~

Keras specific evaluation functions

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-08"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 

# third party imports
from keras.callbacks import Callback
import numpy as np
from sklearn.metrics import get_scorer

# local imports

# globals


class Metric(Callback):
    """Class for calculating sklearn metrics on validation data in keras

    :param scorer: sklearn scorer or name of scorer
    :param name: name of metric
    """
    def __init__(self, scorer=None, name=None):
        Callback.__init__(self)
        self.scorer = get_scorer(scorer)
        self.name = name

    def on_epoch_end(self, epoch, logs={}):
        y_true = self.validation_data[1]
        y_pred = (np.asarray(self.model.predict(self.validation_data[0]))).round()
        logs[self.name] = self.scorer._score_func(y_true, y_pred, **self.scorer._kwargs)


# global metrics
f1_metric = Metric(scorer='f1_micro', name='val_f1')

# EOF
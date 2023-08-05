# encoding: utf-8
"""
table.py
~~~~~~~~

Functionality for creating performance summary tables.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-05"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports

# third party imports
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support

# local imports
from atnlp.eval.metrics import recall_all_score, flpd_score, mlpd_score

# globals


def topic_labelling_summary_table(Y_true, Y_pred, sample_min=None, thresholds=None):
    """Return topic labelling summary table for single model predictions

    Contents of the table includes the following entries per topic:

    - samples: total number of examples
    - standard metrics: precision, recall, f1
    - fl: total number of false labels (for topic)
    - flps: false labels for topic / topic samples
    - flpd: false labels for topic / total documents
    - ml: total numebr of missing labels (for topic)
    - mlps: missing labels for topic / topic samples
    - mlpd: missing labels for topic / total documents

    If *sample_min* is specified, topics with fewer examples will be omitted.

    *thresholds* is a list of one threshold per category, which if specified,
    will be applied to *Y_pred* to generate class predictions. In this case
    *Y_pred* is assumed to be a matrix of class probability scores rather than
    predictions.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :param sample_min: minimum number of examples per topic
    :param thresholds: list of thresholds per category (optional)
    :return: summary table (pandas DataFrame)
    """
    # filter topics with too few samples    
    if sample_min is not None:
        samples = np.array([sum(Y_true[topic]) for topic in Y_true.columns])
        Y_true = Y_true[Y_true.columns[samples > sample_min]]
        Y_pred = Y_pred[:, samples > sample_min]
        if thresholds is not None:
            thresholds = thresholds[samples > sample_min]

    # define column order
    columns = ['topic', 'samples',
               'precision', 'recall', 'f1',
               'fl', 'flps', 'flpd',
               'ml', 'mlps', 'mlpd']

    # build table data
    scores = np.array([np.array(precision_recall_fscore_support(Y_true[c], Y_pred[:, i]))[:3,1]
                       for (i,c) in enumerate(Y_true.columns)])
    samples = np.sum(Y_true, axis=0)
    fl = np.sum(Y_pred & ~Y_true, axis=0)
    flps = fl / samples
    flpd = fl / len(Y_true)
    ml = np.sum(~Y_pred & Y_true, axis=0)
    mlps = ml / samples
    mlpd = ml / len(Y_true)

    data = {'topic' :Y_true.columns, 'samples': samples,
        'precision': scores[:,0], 'recall': scores[:,1], 'f1': scores[:,2],
        'fl': fl, 'flps':flps, 'flpd':flpd,
        'ml': ml, 'mlps':mlps, 'mlpd':mlpd}

    if thresholds is not None:
        data['threshold'] = thresholds
        columns += ['threshold']

    # return table sorted by number of samples
    return pd.DataFrame(data, columns=columns) \
        .sort_values(by='samples', ascending=False) \
        .round({k:3 for k in columns if k not in ['topic', 'samples', 'fl', 'ml', 'threshold']})


def multimodel_topic_labelling_summary_tables(Y_true, Y_preds, model_names, sample_min=None, thresholds=None):
    """Return dictionary of topic labelling summary tables for multiple model predictions

    The dictionary includes a single table for each of the metrics included in
    :func:`topic_labelling_summary_table`, where the key is the metric name.

    An overall summary table (with key *summary*) is also provided, including the following metrics:

    - pre_mic, rec_mic, f1_mic: precision, recall and f1 scores using 'micro' averaging over topics
    - recall_all: recall calculated requiring all labels in document correct (see :func:`atnlp.eval.metrics.recall_all_score`)
    - flpd, mlpd: false/missing labels per document (see :func:`atnlp.eval.metrics.flpd_score`, :func:`atnlp.eval.metrics.mlpd_score`)

    In each table, metrics are provided for each of the models provided.

    If *sample_min* is specified, topics with fewer examples will be omitted.

    *thresholds* is a list of one threshold per category per model, which if specified,
    will be applied to *Y_pred* to generate class predictions. In this case
    *Y_pred* is assumed to be a matrix of class probability scores rather than
    predictions.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_preds: list of topic predictions for each model (one-hot format)
    :param model_names: name of each model
    :param sample_min: minimum number of examples per topic
    :param thresholds: list of thresholds per category (optional)
    :return: dict of summary tables (pandas DataFrames)
    """
    assert len(model_names) == len(Y_preds), "model_names must be same length as Y_preds!"
    if thresholds: assert len(thresholds) == len(Y_preds)
    else:          thresholds = [None] * len(Y_preds)
    n = len(model_names)
    tables = dict()

    # get per-model tables
    model_tables = [topic_labelling_summary_table(Y_true, Y_preds[i],
                                                  sample_min=sample_min,
                                                  thresholds=thresholds[i])
                    for i in range(n)]

    # create per-topic summary tables for each metric
    topic = model_tables[0]['topic']
    samples = model_tables[0]['samples']
    columns = [c for c in model_tables[0].columns if c not in ['topic','samples','threshold']]
    for c in columns:
        df = pd.DataFrame({'topic':topic, 'samples':samples}, columns=['topic','samples']+model_names)
        for (i,n) in enumerate(model_names):
            df[n] = model_tables[i][c]
        tables[c] = df

    # create overall metric table
    scores = np.array([np.array(precision_recall_fscore_support(Y_true, Y_pred))[:3,1]
                       for Y_pred in Y_preds])

    columns = ['model', 'pre_mic', 'rec_mic', 'f1_mic', 'rec_all', 'flpd', 'mlpd']
    ave_table = pd.DataFrame({
            'model': model_names,
            'pre_mic': scores[:,0], 'rec_mic': scores[:,1], 'f1_mic': scores[:,2],
            'rec_all': [recall_all_score(Y_true, Y_pred) for Y_pred in Y_preds],
            'flpd': [flpd_score(Y_true, Y_pred) for Y_pred in Y_preds],
            'mlpd': [mlpd_score(Y_true, Y_pred) for Y_pred in Y_preds],
            },
            columns = columns) \
        .sort_values(by='f1_mic', ascending=False) \
        .round({k:3 for k in columns if k not in ['model']})

    tables['summary'] = ave_table
    return tables


# EOF

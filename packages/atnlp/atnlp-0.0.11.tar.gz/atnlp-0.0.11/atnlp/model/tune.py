# encoding: utf-8
"""
tune.py
~~~~~~~

Functionality for tuning models

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-08"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports

# third party imports
import numpy as np
from matplotlib import pyplot as plt
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, roc_auc_score

# local imports
from atnlp.core.logger import log, title_break

# globals


def grid_search(X_train, y_train, model, pname, pvals, scoring=None):
    """Perform 1D model hyper-parameter scan using 5-fold cross-validation

    The sklearn grid is returned and a plot of the performance is made.

    :param X_train: training data
    :param y_train: ground truth labels
    :param model: model
    :param pname: model hyperparameter name
    :param pvals: model hyperparameter values
    :param scoring: sklearn performance metric (optional)
    :return: sklearn GridSearchCV
    """
    # configure grid-search parameters
    params = {pname:pvals}

    # run grid-search
    grid = GridSearchCV(model, cv=5, param_grid=params,
                        return_train_score=True,
                        scoring=scoring)
    result = grid.fit(X_train, y_train)

    # plot results
    scan_x = params[pname]
    plt.errorbar(scan_x, grid.cv_results_['mean_test_score'],
                 yerr=grid.cv_results_['std_test_score'],
                 label='test')
    plt.errorbar(scan_x, grid.cv_results_['mean_train_score'],
                 yerr=grid.cv_results_['std_train_score'],
                 label = 'train')
    plt.legend()
    ax = plt.gca()
    ax.grid(True)
    for line in ax.get_xgridlines() + ax.get_ygridlines():
        line.set_linestyle('-.')

    return grid


def find_threshold(y_true, y_score, target_contamination=0.01, show=True):
    """Return binary classification probability threshold that yields contamination closest to target

    :param y_true: ground truth labels
    :param y_score: predicted class scores
    :param target_contamination: target level of contamination (1-precision)
    :param show: make plots
    :return: optimal threshold
    """
    thres_min = 0.0
    thres_max = 1.02
    thres = np.arange(thres_min, thres_max, 0.005)

    # first calculate denominator (total entries passing threshold)
    tots = np.array([np.sum(y_score > v) for v in thres])

    # filter entries where nothing passes
    thres = thres[tots > 0]
    tots = tots[tots > 0]

    # if no points return a valid number, return threshold
    if len(tots) == 0:
        return thres_min

    # calculate contamination
    conts = np.array([np.sum(y_score[y_true == False] > v) for v in thres]) / tots

    # get point closest to target contamination
    idx = (np.abs(conts - target_contamination)).argmin()

    # plot
    if show:
        recall = np.array([np.sum(y_score[y_true == True] > v) for v in thres]) / np.sum(y_true)
        ymin = max(min([target_contamination - 0.1, conts[idx]]), 0.0)
        ymax = min(max([target_contamination + 0.1, conts[idx]]), 1.0)

        plt.figure(figsize=(20, 5))

        # Plot 1: probability distributions
        plt.subplot(1, 3, 1)
        bins = np.arange(0., 1.001, 0.02)
        plt.hist(y_score[y_true == True], bins=bins, label='Signal', alpha=0.5)
        plt.hist(y_score[y_true == False], bins=bins, label='Background', alpha=0.5)
        ax = plt.gca()
        ax.set_yscale('log')
        plt.vlines(x=thres[idx], ymin=ax.get_ylim()[0], ymax=ax.get_ylim()[1], linestyles='--')
        plt.annotate('chosen threshold', xy=(thres[idx], ax.get_ylim()[1] / 10.0),
                     verticalalignment='top', horizontalalignment='right', rotation=90)

        plt.xlabel('threshold')
        plt.legend()

        # Plot 2: threshold tuning
        plt.subplot(1, 3, 2)
        plt.hlines(y=target_contamination, xmin=thres_min, xmax=thres_max, linestyles='--')
        plt.annotate('target', xy=(thres_min, target_contamination),
                     verticalalignment='bottom')
        plt.plot(thres, conts, label='contamination', color='b')
        plt.plot(thres, recall, label='recall', color='r')
        plt.plot(thres[idx], conts[idx], 'bo')
        plt.plot(thres[idx], recall[idx], 'ro')
        # plt.ylim(ymin,ymax)
        plt.legend()

        ax = plt.gca()
        ax.grid(True)
        gridlines = ax.get_xgridlines() + ax.get_ygridlines()
        for line in gridlines:
            line.set_linestyle('-.')
        # ax.set_yscale('log')

        plt.xlabel('threshold')
        plt.ylabel('cont. / recall')

        # Plot 3: ROC
        plt.subplot(1, 3, 3)
        plt.plot(conts, recall)
        plt.xlabel('contamination')
        plt.ylabel('recall')
        plt.plot(conts[idx], recall[idx], 'bo')

        ax = plt.gca()
        ax.grid(True)
        gridlines = ax.get_xgridlines() + ax.get_ygridlines()
        for line in gridlines:
            line.set_linestyle('-.')

        plt.xlim(-0.02, 1.02)
        plt.ylim(-0.02, 1.02)

    return thres[idx]


def fit_xgb_model(alg, X, y, X_test, y_test, useTrainCV=True, cv_folds=5, early_stopping_rounds=50):
    """Fit xgboost model

    :param alg: XGBClassifier (sklearn api class)
    :param X: training data
    :param y: training labels
    :param X_test: testing data
    :param y_test: testing labels
    :param useTrainCV: use cross validation
    :param cv_folds: number of folds for cross-validation
    :param early_stopping_rounds: minimum number of rounds before early stopping
    """
    if useTrainCV:
        import xgboost as xgb
        dtrain = xgb.DMatrix(X, label=y)
        cvresult = xgb.cv(alg.get_xgb_params(), dtrain,
                          num_boost_round=alg.get_params()['n_estimators'],
                          early_stopping_rounds=early_stopping_rounds,
                          nfold=cv_folds, metrics='auc')
        alg.set_params(n_estimators=cvresult.shape[0])

    # Fit the algorithm on the data
    eval_set = [(X, y), (X_test, y_test)]
    alg.fit(X, y, eval_metric='auc', eval_set=eval_set, verbose=False)

    # Predict training set:
    y_pred = alg.predict(X)
    y_prob = alg.predict_proba(X)[:, 1]

    # Print model report:
    title_break("Model Report")
    log().info("Accuracy : %.4g" % accuracy_score(y, y_pred))
    log().info("AUC Score (Train): %f" % roc_auc_score(y, y_prob))

    result = alg.evals_result()
    n = len(result['validation_0']['auc'])

    if useTrainCV:
        x = np.arange(len(cvresult))
        (ytr, eytr) = (cvresult['train-auc-mean'], cvresult['train-auc-std'])
        (yte, eyte) = (cvresult['test-auc-mean'], cvresult['test-auc-std'])

        plt.fill_between(x, ytr - eytr, ytr + eytr, facecolor='r', alpha=0.25, label='train(cv) err')
        plt.fill_between(x, yte - eyte, yte + eyte, facecolor='b', alpha=0.25, label='test(cv) err')
        plt.plot(x, ytr, color='r', linestyle='--', label='train(cv)')
        plt.plot(x, yte, color='b', linestyle='--', label='test(cv)')

    plt.plot(np.arange(n), result['validation_0']['auc'], color='r', label='train')
    plt.plot(np.arange(n), result['validation_1']['auc'], color='b', linewidth=2, label='test')

    plt.legend()


# EOF
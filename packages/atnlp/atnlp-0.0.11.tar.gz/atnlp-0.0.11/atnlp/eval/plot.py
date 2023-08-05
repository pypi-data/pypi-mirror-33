# encoding: utf-8
"""
plot.py
~~~~~~~

Functionality for creating performance summary plots.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-08"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports

# third party imports
import random
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.colors import CSS4_COLORS
from sklearn.metrics import accuracy_score
from sklearn.metrics.scorer import check_scoring, _PredictScorer, _ProbaScorer
from sklearn.base import clone as clone_model
from sklearn.model_selection import cross_val_score

# local imports
from atnlp.eval.table import topic_labelling_summary_table

# globals
COLORS = ['red', 'blue', 'green', 'orange', 'magenta', 'yellow', 'brown']
random.seed(42)
COLORS += random.sample(list(CSS4_COLORS), len(CSS4_COLORS))


def create_awesome_plot_grid(nminor, ncol=5, maj_h=2, maj_w=3,
                             min_xlabel=None, min_ylabel=None,
                             maj_xlabel=None, maj_ylabel=None,
                             grid=True):
    """Returns an awesome plot grid

     The grid includes a specified number (*nminor*) of minor
     plots (unit size in the grid) and a single major plot
     whose size can be specified in grid units (*maj_h* and *maj_w*).

     The major plot is located top-right. If either dimension
     is 0 the major plot is omitted.

     The minor plots are tiled from left-to-right, top-to-bottom
     on a grid of width *ncol* and will be spaced around the major
     plot.

    The grid will look something like this

    .. code-block:: text

        #----#----#----#---------#
        |    |    |    |         |
        |    |    |    |         |
        #----#----#----#         |
        |    |    |    |         |
        |    |    |    |         |
        #----#----#----#----#----#
        |    |    |    |    |    |
        |    |    |    |    |    |
        #----#----#----#----#----#
        |    |    |
        |    |    | -->
        #----#----#


    :param nminor: number of minor plots
    :param ncol: width of grid (in grid units)
    :param maj_h: height of major plot (in grid units)
    :param maj_w: width of major plot (in grid units)
    :param min_xlabel: x-axis label of minor plots
    :param min_ylabel: y-axis label of minor plots
    :param maj_xlabel: x-axis label of major plot
    :param maj_ylabel: y-axis label of major plot
    :param grid: draw grid lines (if True)
    :return: tuple (figure, major axis, minor axes (flat list), minor axes (2D list))
    """
    assert maj_w <= ncol, "Major fig cannot be wider than grid!"

    def pad_coord(ipad):
        """Return x-y coordinate for ith element"""
        i = int(np.floor(ipad / ncol))
        j = ipad % ncol
        return (i, j)

    def in_main(ipad):
        """Return True if ith element within major plot space"""
        (i, j) = pad_coord(ipad)
        if j >= ncol - maj_w and i < maj_h: return True
        return False

    # derived quantities
    n = maj_w * maj_h + nminor
    nrow = int(np.ceil(n / ncol))
    if maj_h and nminor <= ncol - maj_w:
        ncol = maj_w + nminor
    if maj_w:
        nrow = max(nrow, maj_h)

    # create figure
    f = plt.figure(figsize=(16 * ncol / 5, 16 * nrow / 5))

    # create major axis
    if maj_h and maj_w:
        ax_maj = plt.subplot2grid((nrow, ncol), (0, ncol - maj_w), colspan=maj_w, rowspan=maj_h)
        if maj_xlabel: ax_maj.set_xlabel(maj_xlabel)
        if maj_ylabel: ax_maj.set_ylabel(maj_ylabel)
        ax_maj.tick_params(top=True, right=True,
                           labeltop=True, labelright=True,
                           labelleft=False, labelbottom=False,
                           grid_linestyle='-.')
        ax_maj.grid(grid)
    else:
        ax_maj = None

    # create minor axes
    ax_min = []
    ax_min_ij = [[None] * ncol] * nrow
    ipad = 0
    imin = 0
    while imin < nminor:
        if not in_main(ipad):
            (i, j) = pad_coord(ipad)
            ax0 = ax_min[0] if ax_min else None
            ax = plt.subplot2grid((nrow, ncol), (i, j), sharex=ax0, sharey=ax0)
            ax.i = i
            ax.j = j
            ax.tick_params(top=True, right=True, grid_linestyle='-.')
            ax.grid(grid)
            # add top labels
            if i == 0:
                ax.tick_params(labeltop=True)

            # add right labels
            if j == ncol - 1: ax.tick_params(labelright=True)
            # remove inner left labels
            if j > 0:
                ax.tick_params(labelleft=False)
            # set y-titles
            elif min_ylabel:
                ax.set_ylabel(min_ylabel)
            # set x-titles
            if min_xlabel: ax.set_xlabel(min_xlabel)
            # remove inner bottom labels
            if i > 0 and ax_min_ij[i - 1][j]:
                ax_min_ij[i - 1][j].tick_params(labelbottom=False)
                ax_min_ij[i - 1][j].set_xlabel("")

            ax_min.append(ax)
            ax_min_ij[i][j] = ax
            imin += 1
        ipad += 1

    return (f, ax_maj, ax_min, ax_min_ij)


def binary_classification_accuracy_overlays(classifiers, X_train, y_train, X_test, y_test):
    """Create overlays of binary classification accuracy for multiple classifiers

    :param classifiers: list of tuples (name, classifier)
    :param X_train: training data
    :param y_train: binary training labels
    :param X_test: testing data
    :param y_test: binary testing labels
    :return: tuple (figure, axis)
    """
    acc_train = [accuracy_score(y_train, c.predict(X_train))
               for (_,c) in classifiers]
    acc_test = [accuracy_score(y_test, c.predict(X_test))
               for (_,c) in classifiers]

    acc_cv = [c.cv_results_['mean_test_score'][c.best_index_]
             for (_,c) in classifiers]
    acc_err_cv = [c.cv_results_['std_test_score'][c.best_index_]
             for (_,c) in classifiers]

    names = [n for (n,_) in classifiers]
    ypos = np.arange(len(classifiers))

    fig, ax = plt.subplots()
    ax.barh(ypos, acc_cv, xerr=acc_err_cv, align='center',
            color='g', label='cv', alpha=0.5)
    ax.set_yticks(ypos)
    ax.set_yticklabels(names)
    ax.set_xlabel('Accuracy')
    ax.scatter(acc_train, ypos, color='red', label='train')
    ax.scatter(acc_test, ypos,  color='b',   label='test')
    ax.invert_yaxis()
    ax.legend()
    xmin = 0.98 * min(acc_train+acc_test+acc_cv)
    xmax = 1.02 * max(acc_train+acc_test+acc_cv)
    ax.set_xlim(xmin,xmax)

    return (fig, ax)


def topic_labelling_scatter_plots(Y_true, Y_pred, sample_min=None, thresholds=None):
    """Create scatter plots comparing precision, recall and number of samples

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :param sample_min: minimum number of examples per topic
    :param thresholds: list of thresholds per category (optional)
    :return: tuple (figure, list of axes)
    """
    table = topic_labelling_summary_table(Y_true, Y_pred, sample_min, thresholds)

    # Make scatter plots
    f = plt.figure(figsize=(20,5))

    ax1 = plt.subplot(1,3,1)
    ax1.scatter(table['recall'], table['precision'])
    plt.xlabel('recall')
    plt.ylabel('contamination')

    ax2 = plt.subplot(1,3,2)
    ax2.scatter(table['samples'], table['recall'])
    ax2.set_xscale('log')
    plt.xlabel('samples')
    plt.ylabel('recall')

    ax3 = plt.subplot(1,3,3)
    ax3.scatter(table['samples'], table['precision'])
    ax3.set_xscale('log')
    plt.xlabel('samples')
    plt.ylabel('contamination')

    return (f, (ax1, ax2, ax3))


def topic_labelling_barchart(Y_true, Y_preds, model_names):
    """Create topic labelling barchart

    The figure includes a 1x4 grid of bar charts, illustrating
    the number of samples, precision, recall and f1 scores for
    each topic. The scores are overlayed for each model.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_preds: topic predictions for each model (list of one-hot formats)
    :param model_names: topic labelling model names
    :return: tuple (figure, list of axes)
    """
    n = len(model_names)
    tables = [topic_labelling_summary_table(Y_true, Y_preds[i]) for i in range(n)]
    topics = tables[0]['topic']
    samples = tables[0]['samples']

    # y-axis
    ypos = np.arange(len(samples))

    # figure
    plt.close('all')
    f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey=True, figsize=(16, 0.25 * len(samples)))

    # samples subfig
    ax1.set_xlabel('Samples')
    ax1.barh(ypos, samples, align='center',
             color='g', label='Samples', alpha=0.25)
    ax1.set_yticks(ypos)
    ax1.set_yticklabels(topics)
    ax1.invert_yaxis()

    # precision
    ax2.set_xlabel('Precision')
    ax2.set_xlim((-0.05, 1.05))
    for i in range(n):
        ax2.scatter(tables[i]['precision'], ypos, color=COLORS[i],
                    label=model_names[i], alpha=0.5)

    # recall
    ax3.set_xlabel('Recall')
    ax3.set_xlim((-0.05, 1.05))
    for i in range(n):
        ax3.scatter(tables[i]['recall'], ypos, color=COLORS[i],
                    label=model_names[i], alpha=0.5)

    # recall
    ax4.set_xlabel('F1')
    ax4.set_xlim((-0.05, 1.05))
    for i in range(n):
        ax4.scatter(tables[i]['f1'], ypos, color=COLORS[i],
                    label=model_names[i], alpha=0.5)


    ax4.legend(loc='center left', bbox_to_anchor=(1, 1))

    gridlines = []
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid()
        gridlines += ax.get_xgridlines() + ax.get_ygridlines()
    for line in gridlines:
        line.set_linestyle('-.')

    return (f, (ax1, ax2, ax3, ax4))


def topic_labelling_barchart_cv(models, model_names, model_inputs, Y, cv=10):
    """Create topic labelling barchart with k-fold cross-validation

    Figure layout is the same as in :func:`topic_labelling_barchart`.

    K-fold cross-validation is used to estimate uncertainties on the metrics.

    :param models: list of topic labelling models
    :param model_names: list of model names
    :param model_inputs: list of input data for models
    :param Y: ground truth topic labels (one-hot format)
    :param cv: number of folds for cross-validation
    :return: tuple (figure, list of axes)
    """
    n = len(models)
    samples = np.array([sum(Y[cat]) for cat in Y.columns])
    order = np.argsort(samples)[::-1]
    samples = samples[order]
    topics = Y.columns[order]

    def get_cv_scores(scoring, model, X):
        scores = np.array([cross_val_score(model.estimators_[i], X, Y[cat], scoring=scoring, cv=cv)
                           for (i, cat) in enumerate(Y.columns[order])])
        smed = np.median(scores, axis=1)
        smin = np.min(scores, axis=1)
        smax = np.max(scores, axis=1)
        err = np.column_stack([np.abs(smin - smed), np.abs(smax - smed)])
        return [smed, err]

    precision = [get_cv_scores('precision', m, X) for (m, X) in zip(models, model_inputs)]
    recall = [get_cv_scores('recall', m, X) for (m, X) in zip(models, model_inputs)]
    f1 = [get_cv_scores('f1', m, X) for (m, X) in zip(models, model_inputs)]

    # y-axis
    ypos = np.arange(len(samples))

    # figure
    plt.close('all')
    f, (ax1, ax2, ax3, ax4) = plt.subplots(1, 4, sharey=True, figsize=(16, 0.25 * len(samples)))

    # samples subfig
    ax1.set_xlabel('Samples')
    ax1.barh(ypos, samples, align='center',
             color='g', label='Samples', alpha=0.25)
    ax1.set_yticks(ypos)
    ax1.set_yticklabels(topics)
    ax1.invert_yaxis()

    # precision
    ax2.set_xlabel('Precision')
    ax2.set_xlim((-0.05, 1.05))
    for i in range(n):
        (med, err) = precision[i]
        ax2.errorbar(med, ypos, xerr=err.T, color=COLORS[i],
                     fmt='o', capsize=5, label=model_names[i], alpha=0.5)

    # recall
    ax3.set_xlabel('Recall')
    ax3.set_xlim((-0.05, 1.05))
    for i in range(n):
        (med, err) = recall[i]
        ax3.errorbar(med, ypos, xerr=err.T, color=COLORS[i],
                     fmt='o', capsize=5, label=model_names[i], alpha=0.5)

    # f1
    ax4.set_xlabel('F1')
    ax4.set_xlim((-0.05, 1.05))
    for i in range(n):
        (med, err) = f1[i]
        ax4.errorbar(med, ypos, xerr=err.T, color=COLORS[i],
                     fmt='o', capsize=5, label=model_names[i], alpha=0.5)

    ax4.legend(loc='center left', bbox_to_anchor=(1, 1))

    gridlines = []
    for ax in [ax1, ax2, ax3, ax4]:
        ax.grid()
        gridlines += ax.get_xgridlines() + ax.get_ygridlines()
    for line in gridlines:
        line.set_linestyle('-.')

    return (f, (ax1, ax2, ax3, ax4))


def background_composition_pie(Y_true, Y_score, topic, threshold, min_topic_frac=0.05):
    """Create a pie chart illustrating the major background contributions for given label

    Background topics contributing less than *min_topic_frac* will be merged into a
    single contribution called "Other".

    A bar chart is also included illustrating the overall topic composition.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_score: topic probability predictions (shape: samples x topics)
    :param topic: name of topic to investigate
    :param threshold: threshold above which to investigate background contributions
    :param min_topic_frac: minimum background sample fraction
    :return: tuple (figure, list of axes)
    """
    ix = Y_true.columns.get_loc(topic)
    y_score = Y_score[:, ix]
    topics = np.array([t for t in Y_true.columns if t != topic])
    composition = np.array([np.sum(Y_true[topic][y_score > threshold]) for topic in topics])

    # combine contributions less than 5%
    tot = np.sum(composition)
    mask = (composition < tot * min_topic_frac)
    other = np.sum(composition[mask])
    topics = np.array(topics[~mask].tolist() + ["Other"])
    composition = np.array(composition[~mask].tolist() + [other])

    # sort
    topics = topics[np.argsort(composition)]
    composition = np.sort(composition)

    # make fig
    fig = plt.figure(figsize=(15, 5))
    # Plot 1: bar
    ax1 = plt.subplot(1, 2, 1)
    ypos = np.arange(len(composition))
    ax1.barh(ypos, composition, align='center')
    ax1.set_yticks(ypos)
    ax1.set_yticklabels(topics)
    ax1.set_xlabel('Samples')

    # Plot 2: pie
    ax2 = plt.subplot(1, 2, 2)
    ax2.pie(composition, labels=topics, autopct='%1.1f%%', startangle=90)
    plt.axis('equal')

    return (fig, (ax1, ax2))


def get_multimodel_sample_size_dependence(models, datasets, labels, sample_fracs, scoring=None, cat_scoring=None):
    """Return performance metrics vs training sample size

    Fractions of data (*sample_fracs*) are randomly sampled from the training dataset
    and used to train the models, which are always evaluated on the full testing datasets.

    :param models: list of topic labelling models
    :param datasets: list of input data for models (each is (training, testing) tuple)
    :param labels: tuple (train, test) of ground truth topic labels (one-hot format)
    :param sample_fracs: list of sample fractions to scan
    :param scoring: sklearn scorer or scoring name for topic averaged metric
    :param cat_scoring: sklearn scorer or scoring name for individual topic metric
    :return: tuple (entries per step, averaged model scores for each step, model scores for each topic for each step)
    """
    # inputs
    (Y_train, Y_test) = labels
    train_size = len(Y_train)
    test_size = len(Y_test)
    train_indices = np.arange(train_size)
    categories = Y_train.columns

    # check input dataset size compatibility
    assert np.all(np.array([X.shape[0] for (X, _) in datasets]) == train_size), \
        "Model training sample sizes are incompatible!"
    assert np.all(np.array([X.shape[0] for (_, X) in datasets]) == test_size), \
        "Model testing sample sizes are incompatible!"

    # values to fill
    entries = []
    scores = [] if scoring is not None else None
    cat_scores = [] if cat_scoring is not None else None
    for frac in sample_fracs:
        # sub-sampling
        subsample_size = int(frac * train_size)
        np.random.seed(42)
        rand_indices = np.random.choice(train_indices, subsample_size, replace=False)
        Y_train_sub = Y_train.iloc[rand_indices]

        # account for active categories (ie have at least 1 True and 1 False label)
        active_cats = [cat for cat in categories if len(Y_train_sub[cat].unique()) == 2]
        if len(active_cats) == 0:
            print("no active categories, skipping frac: ", frac)
            continue
        print("frac: {}, samples: {}, active cats: {}".format(frac, subsample_size, len(active_cats)))
        Y_train_sub = Y_train_sub[active_cats]
        Y_test_sub = Y_test[active_cats]

        # evaluate model
        model_scores = []
        cat_model_scores = []
        for (model, (X_train, X_test)) in zip(models, datasets):
            # print ("evaluating model...")
            X_train_sub = X_train[rand_indices]

            # train
            model_tmp = clone_model(model)
            model_tmp.fit(X_train_sub, Y_train_sub)

            # predict/eval overall
            scorer = Y_test_pred = None
            if scoring is not None:
                scorer = check_scoring(model_tmp, scoring)
                if isinstance(scorer, _PredictScorer):
                    Y_test_pred = model_tmp.predict(X_test)
                elif isinstance(scorer, _ProbaScorer):
                    Y_test_pred = model_tmp.predict_proba(X_test)
                else:
                    assert False, "Scorer not supported"
                model_scores.append(scorer._score_func(Y_test_sub, Y_test_pred, **scorer._kwargs))

            # predict/eval per category
            if cat_scoring is not None:
                cat_scorer = check_scoring(model_tmp.estimators_[0], cat_scoring)
                if scoring is not None and type(scorer) == type(cat_scorer):
                    Y_test_pred_cat = Y_test_pred
                else:
                    if isinstance(cat_scorer, _PredictScorer):
                        Y_test_pred_cat = model_tmp.predict(X_test)
                    elif isinstance(cat_scorer, _ProbaScorer):
                        Y_test_pred_cat = model_tmp.predict_proba(X_test)
                    else:
                        assert False, "Category Scorer not supported"

                # eval
                cat_score = []
                for cat in categories:
                    if cat not in active_cats:
                        s = 0.0
                    else:
                        icat = np.where(Y_test_sub.columns == cat)[0][0]
                        s = cat_scorer._score_func(Y_test_sub[cat],
                                                   Y_test_pred_cat[:, icat],
                                                   **cat_scorer._kwargs)
                    cat_score.append(s)
                cat_model_scores.append(cat_score)

            # Note: this is typically how to call the scorer (but we hacked to avoid multiple prediction)
            # score = scorer(model_tmp, X_test, Y_test_sub)

        entries.append(subsample_size)
        if scoring is not None:
            scores.append(model_scores)
        if cat_scoring is not None:
            cat_scores.append(cat_model_scores)

    entries = np.array(entries)
    if scoring is not None:
        scores = np.array(scores).T
    if cat_scoring is not None:
        cat_scores = np.array(cat_scores).T
    return (entries, scores, cat_scores)


def multimodel_sample_size_dependence_graph(models, model_names, datasets, labels, sample_fracs, scoring=None,
                                            cat_scoring=None):
    """Create graph of performance metric vs training sample size

    Fractions of data (*sample_fracs*) are randomly sampled from the training dataset
    and used to train the models, which are always evaluated on the full testing datasets.

    :param models: list of topic labelling models
    :param model_names: list of model names
    :param datasets: list of input data for models (each is (training, testing) tuple)
    :param labels: tuple (train, test) of ground truth topic labels (one-hot format)
    :param sample_fracs: list of sample fractions to scan
    :param scoring: sklearn scorer or scoring name for topic averaged metric
    :param cat_scoring: sklearn scorer or scoring name for individual topic metric
    :return: tuple (figure, major axis, minor axes (flat list), minor axes (2D list))
    """
    (entries, scores, cat_scores) = get_multimodel_sample_size_dependence(
        models, datasets, labels, sample_fracs, scoring=scoring, cat_scoring=cat_scoring)

    # set figure configuration
    if scoring is None:
        maj_w = maj_h = None
    else:
        maj_w = 3
        maj_h = 2
    if cat_scoring is None:
        ncat = 0
    else:
        ncat = cat_scores.shape[0]

    plt.close('all')
    (f, ax_maj, ax_min, ax_min_ij) = create_awesome_plot_grid(
        ncat, maj_w=maj_w, maj_h=maj_h, min_xlabel="Train sample size", min_ylabel="Score")

    # plot main figure
    if scoring:
        ax = ax_maj
        for j in range(len(models)):
            ax.plot(entries, scores[j], color=COLORS[j], label=model_names[j])
        ax.set_title("Overall", pad=25)
        ax.legend()

    # plot grid with categories
    if cat_scoring:
        # get category sample fractions
        categories = labels[0].columns
        cfracs = np.array([np.sum(labels[0][cat]) / len(labels[0]) for cat in categories])

        # sort categories by size
        order = np.argsort(cfracs)[::-1]
        categories = categories[order]
        cfracs = cfracs[order]
        cat_scores = cat_scores[order]

        # plot subfigs
        for i in range(len(categories)):
            ax = ax_min[i]
            for j in range(len(models)):
                ax.plot(entries, cat_scores[i, j], color=COLORS[j], label=model_names[j])
            pad = 25 if ax.i == 0 else None
            ax.set_title("{} ({:.1f}% frac)".format(categories[i], 100. * cfracs[i]), pad=pad)
        if not scoring: ax_min[0].legend()

    return (f, ax_maj, ax_min, ax_min_ij)


def topic_correlation_matrix(Y):
    """Create MxM correlation matrix for M topics

    Each column represents a given ground truth topic label.
    Each row represents the relative frequency with which other
    ground truth labels co-occur.

    :param Y: ground truth topic labels (one-hot format)
    :return: tuple (figure, axis)
    """
    d = np.array([np.sum(Y[Y[t]], axis=0) / np.sum(Y[t]) for t in Y.columns]) * 100
    d = d.T
    df = pd.DataFrame(d, columns=Y.columns)
    df['topic'] = Y.columns
    df = df.set_index('topic')
    fig, ax = plt.subplots(figsize=(11, 11))
    graph = sns.heatmap(df, annot=True, fmt=".0f", cbar=False, cmap="Blues", linewidths=0.2)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('Chosen label')
    ax.set_ylabel('Coincidence of other labels with chosen label [%]')
    _ = plt.xticks(rotation=90)

    return (fig, ax)


def topic_migration_matrix(Y_true, Y_pred):
    """Create MxM migration matrix for M topics

    Each column represents a given ground truth topic label.
    Each row represents the relative frequency with which
    predicted labels are assigned.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :return: tuple (figure, axis)
    """
    d = np.array([np.sum(Y_pred[Y_true[t]], axis=0) / np.sum(Y_true[t]) for t in Y_true.columns]) * 100
    d = d.T
    df = pd.DataFrame(d, columns=Y_true.columns)
    df['topic'] = Y_true.columns
    df = df.set_index('topic')
    fig, ax = plt.subplots(figsize=(11, 11))
    graph = sns.heatmap(df, annot=True, fmt=".0f", cbar=False, cmap="Greens", linewidths=0.2)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('True label')
    ax.set_ylabel('Frequency of predicted label per true label [%]')
    _ = plt.xticks(rotation=90)

    return (fig, ax)


def false_labels_matrix(Y_true, Y_pred):
    """Create MxM false labels matrix for M topics

    Each column represents a given ground truth topic label.
    Each row represents the absolute number of false predicted
    labels.

    :param Y_true: ground truth topic labels (one-hot format)
    :param Y_pred: topic predictions (one-hot format)
    :return: tuple (figure, axis)
    """
    d = np.array([np.sum(Y_pred[Y_true[t]] & ~Y_true[Y_true[t]], axis=0) for t in Y_true.columns])
    d = d.T
    df = pd.DataFrame(d, columns=Y_true.columns)
    df['topic'] = Y_true.columns
    df = df.set_index('topic')
    fig, ax = plt.subplots(figsize=(11, 11))
    graph = sns.heatmap(df, annot=True, fmt=".0f", cbar=False, cmap="Reds", linewidths=0.2)
    ax.xaxis.tick_top()  # x axis on top
    ax.xaxis.set_label_position('top')
    ax.set_xlabel('True label')
    ax.set_ylabel('Number of false labels for given true label')
    _ = plt.xticks(rotation=90)
    return fig


def keras_train_history_graph(history, metrics):
    """Plot selected performance *metrics* as a function of training epoch.

    :param history: keras training history
    :param metrics: list of metric names to plot
    :return: tuple (figure, list of axes)
    """
    plt.close('all')
    f, axs = plt.subplots(len(metrics), 1, sharex=True, figsize=(8, 8))

    if not isinstance(axs, np.ndarray):
        axs = [axs]

    for (i, metric) in enumerate(metrics):
        ax = axs[i]
        if metric in history:
            x = np.arange(len(history[metric]))
            ax.plot(x, history[metric], c='r', label='train')
        if 'val_' + metric in history:
            x = np.arange(len(history['val_' + metric]))
            ax.plot(x, history['val_' + metric], c='b', label='validation')
        if i == 0: ax.legend()
        ax.grid()
        ax.set_xlabel("epoch")
        ax.set_ylabel(metric)

    return (f, axs)

# EOF
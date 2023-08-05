#!/usr/bin/env python
# encoding: utf-8
"""
evaluate.py
~~~~~~~~~~~

<Description goes here...>

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-06"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports
import logging
import os
from argparse import ArgumentParser

# third party imports
from sklearn.externals import joblib

# local imports
from atnlp.core.helpers import start_timer, stop_timer
from atnlp.core.logger import log, section_break
from atnlp.core.setup import setup
from atnlp.data.io import read_raw, read_one_hot_labels
from atnlp.eval.html import Report
from atnlp.eval.plot import topic_labelling_barchart, topic_correlation_matrix, \
    topic_migration_matrix, false_labels_matrix
from atnlp.eval.table import multimodel_topic_labelling_summary_tables

# globals


def build_parser():
    description = "Evaluate topic models"
    parser = ArgumentParser(description=description)
    parser.add_argument('data', help="Data (text file format)")
    parser.add_argument('labels', help="Labels (text file format)")
    parser.add_argument('models', nargs='+', help="Model configs (pickle format)")
    parser.add_argument('-o', '--output', default='summary.html',
                        help="Directory for evaluation outputs [default: summary]")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Set logging level to DEBUG")
    parser.add_argument('-q', '--quiet', action='store_true',
                        help="Quiet mode")

    return parser


def main():
    ti = start_timer()

    # parse command line args
    parser = build_parser()
    args = parser.parse_args()

    # setup atnlp framework
    log_level = logging.DEBUG if args.verbose else None
    if args.quiet:
        log_level = logging.WARN
    else:
        print("\nExecuting {}\n".format(os.path.basename(__file__)))
    setup(log_level=log_level)

    section_break("Config summary")
    for (k, v) in vars(args).items():
        log().info("{:20s}: {}".format(k, v))

    # ------------------
    # Prepare input data
    # ------------------
    section_break("Preparing input data")

    log().info("Reading training data from {}...".format(args.data))
    X = read_raw(args.data)

    log().info("Reading training labels from {}...".format(args.labels))
    Y = read_one_hot_labels(args.labels)

    # -----------
    # Load models
    # -----------
    section_break("Loading models")
    names = [os.path.splitext(os.path.basename(m))[0] for m in args.models]
    models = [joblib.load(m) for m in args.models]

    # -------
    # Predict
    # -------
    section_break("Predicting labels")
    preds = [m.predict(X) for m in models]

    # --------
    # Evaluate
    # --------
    tables = multimodel_topic_labelling_summary_tables(Y, preds, names)

    # --------
    # Finalize
    # --------
    section_break("Finalizing")

    html = Report()
    html.add_title("Topic modelling performance",
                   par="Here are some totally awesome results on topic modelling!")

    html.add_section("Topic-averaged performance")
    html.add_text("The precision, recall and f1 metrics use 'micro' averaging over topics")
    html.add_table(tables['summary'], cap='')

    html.add_section("Per-topic performance")

    topic_labelling_barchart(Y, preds, names)
    html.add_figure(cap="Comparison of per-topic metrics for each model")

    html.add_section("Per-topic performance (tables)")

    html.add_table(tables['precision'], cap='Precision scores per topic for each model')
    html.add_table(tables['recall'], cap='Recall scores per topic for each model')
    html.add_table(tables['f1'], cap='f1 scores per topic for each model')
    html.add_table(tables['fl'], cap='Number of false labels')
    html.add_table(tables['ml'], cap='Number of missed labels')

    # best model perf
    best_model = tables['summary']['model'].iloc[0]
    best_index = names.index(best_model)
    best_pred = preds[best_index]

    html.add_section("Correlations")
    topic_correlation_matrix(Y)
    html.add_figure(cap='True topic correlations')

    topic_migration_matrix(Y, best_pred)
    html.add_figure(cap='Topic migration matrix')

    false_labels_matrix(Y, best_pred)
    html.add_figure(cap="False labels matrix")

    html.write(args.output)

    # log().info("Writing labels to {}".format(args.output))

    # timer
    stop_timer(ti)


if __name__ == "__main__":
    main()
# EOF

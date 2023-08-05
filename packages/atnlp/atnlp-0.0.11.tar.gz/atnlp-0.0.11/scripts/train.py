#!/usr/bin/env python
# encoding: utf-8
"""
train.py
~~~~~~~~

Train topic labelling model on standardized text file input

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-06"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports
import os
from argparse import ArgumentParser
import logging

# third party imports
from sklearn.externals import joblib

# local imports
from atnlp.core.setup import setup
from atnlp.core.logger import log, section_break
from atnlp.core.helpers import start_timer, stop_timer
from atnlp.data.io import read_raw, read_one_hot_labels
from atnlp.model.io import load_configured_model

# globals


def build_parser():

    description = "Train topic labelling model"
    parser = ArgumentParser(description=description)
    parser.add_argument('data', help="Training data (text file format)")
    parser.add_argument('labels', help="Training labels (text file format)")
    parser.add_argument('-o', '--output',
                        help="Model output filename [default: {model}.pkl]")
    parser.add_argument('-m', '--model', default='svm',
                        help="Model name or yml config [default: svm]")
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
    if not args.output:
        model_name = os.path.splitext(os.path.basename(args.model))[0]
        if model_name:
            args.output = model_name + '.pkl'
        else:
            args.output = 'model.pkl'

    # setup atnlp framework
    log_level = logging.DEBUG if args.verbose else None
    if args.quiet: log_level = logging.WARN
    else:
        print("\nExecuting {}\n".format(os.path.basename(__file__)))
    setup(log_level=log_level)

    section_break("Config summary")
    for (k,v) in vars(args).items():
        log().info("{:20s}: {}".format(k,v))

    # ------------------
    # Prepare input data
    # ------------------
    section_break("Preparing input data")

    log().info("Reading training data from {}...".format(args.data))
    X = read_raw(args.data)

    log().info("Reading training labels from {}...".format(args.labels))
    Y = read_one_hot_labels(args.labels)

    # ------------
    # Create model
    # ------------
    section_break("Creating model")

    # dynamically load model using yml config
    model = load_configured_model(args.model)

    # attach topics to model so they are persistified
    model.topics = list(Y.columns)

    if not args.quiet:
        log().info("")
        for s in str(model).split('\n'):
            log().info(s)

    # ---------
    # Fit model
    # ---------
    section_break("Training model")
    model.fit(X, Y)

    # --------
    # Finalize
    # --------
    section_break("Finalizing")
    log().info("Saving model to {}".format(args.output))
    joblib.dump(model, args.output)

    # timer
    stop_timer(ti)


if __name__ == "__main__":
    main()

# EOF
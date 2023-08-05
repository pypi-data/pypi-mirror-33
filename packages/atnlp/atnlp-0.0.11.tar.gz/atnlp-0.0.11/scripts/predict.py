#!/usr/bin/env python
# encoding: utf-8
"""
predict.py
~~~~~~~~~~

Generate topic label predictions for input data from trained model

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
import pandas as pd
from sklearn.externals import joblib

# local imports
from atnlp.core.setup import setup
from atnlp.core.logger import log, section_break
from atnlp.core.helpers import start_timer, stop_timer
from atnlp.data.io import read_raw, write_one_hot_labels

# globals


# Your awesome code goes in here...

def build_parser():

    description = "Predict topic labels"
    parser = ArgumentParser(description=description)
    parser.add_argument('model', help="Model config (pickle format)")
    parser.add_argument('data', help="Training data (text file format)")
    parser.add_argument('-o', '--output', default='pred_labels.txt',
                        help="Predicted labels [default: pred_labels.txt]")
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

    log().info("Reading data from {}...".format(args.data))
    X = read_raw(args.data)

    # ----------
    # Load model
    # ----------
    section_break("Loading model")

    model = joblib.load(args.model)

    if not args.quiet: print(model)

    # -------
    # Predict
    # -------
    section_break("Predicting labels")
    Y_pred = model.predict(X)
    Y_pred = pd.DataFrame(Y_pred, columns=model.topics)

    # --------
    # Finalize
    # --------
    section_break("Finalizing")
    log().info("Writing labels to {}".format(args.output))
    write_one_hot_labels(Y_pred, args.output)

    # timer
    stop_timer(ti)


if __name__ == "__main__":
    main()
# EOF
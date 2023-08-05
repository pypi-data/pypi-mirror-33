#!/usr/bin/env python
# encoding: utf-8
"""
summary.py
~~~~~~~~~~~~~~~

Print performance from model pickle

NOTE: perhaps should be deprecated since it requires specific pickle format that we're not using anymore.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-01"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
from argparse import ArgumentParser
import pickle


def main():

    parser = ArgumentParser(description="Print training summary")
    parser.add_argument('file', help="Model training pickle")
    args = parser.parse_args()

    with open(args.file, 'rb') as f:
        scores = pickle.load(f)['scores']
    train, val, test = scores['train'], scores['val'], scores['test']

    print("{:<10s}{:>15s}{:>15s}{:>15s}".format("Sample", "Precision", "Recall", "F1"))
    print("-"*55)
    print("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Train", *train[:3]))
    print("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Val",   *val[:3]))
    print("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Test",  *test[:3]))
    print("")


if __name__ == "__main__":
    main()

# EOF
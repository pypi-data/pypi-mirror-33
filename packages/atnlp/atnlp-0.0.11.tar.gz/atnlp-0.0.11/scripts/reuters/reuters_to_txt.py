#!/usr/bin/env python
# encoding: utf-8
"""
reuters_to_txt.py
~~~~~~~~~~~~~~~~~

Convert installed reuters corpus into standardised text format

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-06"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
from argparse import ArgumentParser
import logging

# third party imports

# local imports
from atnlp.core.setup import setup
from atnlp.core.logger import log
from atnlp.data.io import write_raw, write_one_hot_labels
from atnlp.data.reuters import get_topics, get_labels, get_data

# globals


def main():
    # parse args
    description = "Convert Reuters dataset to standard text format"
    parser = ArgumentParser(description=description)
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Set logging level to DEBUG")
    parser.add_argument('--min-samples', type=int, default=100,
                        help="Minimum number of samples per category [default: 100]")
    parser.add_argument('--topics', help="comma separated list of topics")
    args = parser.parse_args()

    # setup atnlp framework
    log_level = logging.DEBUG if args.verbose else None
    setup(log_level=log_level)

    # select topics
    if args.topics:
        topics = args.topics.split(',')
    else:
        topics = get_topics(min_samples=args.min_samples)
    log().info("{} topics selected.".format(len(topics)))

    # get topic labels (MxN data frame of bools: M categories, N documents)
    log().info("getting topic labels...")
    (Y_train, Y_test) = get_labels(topics)
    log().info("Writing to labels_train.txt")
    write_one_hot_labels(Y_train, 'labels_train.txt')
    log().info("Writing to labels_test.txt")
    write_one_hot_labels(Y_test, 'labels_test.txt')

    # get data iterators
    # Note: we also use test data because model currently requires
    #       vocab from all samples to get be predictions
    log().info("getting topic data...")
    (X_train, X_test) = get_data(topics)
    log().info("Writing to data_train.txt")
    write_raw(X_train, "data_train.txt")
    log().info("Writing to data_test.txt")
    write_raw(X_test, "data_test.txt")


if __name__ == '__main__':
    main()

# EOF
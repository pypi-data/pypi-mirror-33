#!/usr/bin/env python
# encoding: utf-8
"""
train_reuters_rnn.py
~~~~~~~~~~~~~~~~~~~~

Train RNN for topic labelling on reuters dataset using keras

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-29"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
from argparse import ArgumentParser
import logging
import os
import pickle

# third party imports
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import LSTM, Embedding, Dense, Bidirectional
from keras.callbacks import EarlyStopping
from sklearn.model_selection import train_test_split
from sklearn.metrics import precision_recall_fscore_support

# local imports
from atnlp.core.setup import setup
from atnlp.core.logger import log, section_break, title_break
from atnlp.core.helpers import start_timer, stop_timer
from atnlp.data.reuters import get_data, get_labels, get_topics
from atnlp.data.parse import build_vocab, raw_to_ids, PAD_WORD
from atnlp.model.embed import load_glove, create_embedding_layer
from atnlp.eval.metrics import f1_metric

# globals


def build_parser():

    description = "Train RNNs for reuters dataset"
    parser = ArgumentParser(description=description)
    parser.add_argument('-o', '--output', default='model.h5',
                        help="Model output filename [default: model.h5]")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Set logging level to DEBUG")

    proc_group = parser.add_argument_group('Preprocessing configuration')
    proc_group.add_argument('--min-samples', type=int, default=100,
                        help="Minimum number of samples per category [default: 100]")
    proc_group.add_argument('--topics',
                        help="comma separated list of topics")
    proc_group.add_argument('--max-doc-length', type=int, default=100,
                        help="Maximum number of words per document [default: 100]")
    proc_group.add_argument('--max-vocab-size', type=int, default=10000,
                        help="Maximum number of words in vocabulary [default: 10000]")

    model_group = parser.add_argument_group('Model configuration')
    model_group.add_argument('-e', '--learn-embeddings', action="store_true",
                        help="Learn word embeddings from data")
    model_group.add_argument('--embedding-size', type=int, default=32,
                        help="Size of embedding layer if not pretrained [default: 32]")
    model_group.add_argument('-s', '--lstm-size', type=int, default=None,
                        help="Size of LSTM layer [default: use embedding size]")
    model_group.add_argument('-d', '--lstm-depth', type=int, default=1,
                        help="Depth of LSTM layer [default: 1]")
    model_group.add_argument('--bidirectional', action="store_true",
                        help="Use bidirectional LSTM [default: False]")
    model_group.add_argument('--dropout', type=float, default=0.0,
                        help="Dropout fraction [default: 0.0]")
    model_group.add_argument('--recurrent-dropout', type=float, default=0.0,
                        help="Recurrent dropout fraction [default: 0.0]")

    fit_group = parser.add_argument_group('Fit configuration')
    fit_group.add_argument('-b', '--batch-size', type=int, default=5,
                        help="Batch size [default: 5]")
    fit_group.add_argument('-n', '--epochs', type=int, default=10,
                        help="Number of epochs [default: 10]")
    fit_group.add_argument('--no-early-stopping', action='store_true',
                        help="Don't use early stopping")

    return parser

def main():

    ti = start_timer()

    # parse command line args
    parser = build_parser()
    args = parser.parse_args()

    assert args.lstm_depth >= 1, "Must configure at least one LSTM layer"

    print("\nExecuting train_reuters_rnn.py\n")

    # setup atnlp framework
    log_level = logging.DEBUG if args.verbose else None
    setup(log_level=log_level)

    section_break("Config summary")
    for (k,v) in vars(args).items():
        log().info("{:20s}: {}".format(k,v))

    # ------------------
    # Prepare input data
    # ------------------
    section_break("Preparing input data")

    # select topics
    if args.topics:
        topics = args.topics.split(',')
    else:
        topics = get_topics(min_samples=args.min_samples)
    log().info("{} topics selected.".format(len(topics)))

    # get topic labels (MxN data frame of bools: M categories, N documents)
    # TODO: could explicitly ignore Y_test here to show we don't need test labels
    log().info("getting topic labels...")
    (Y_train, Y_test) = get_labels(topics)

    # get data iterators
    # Note: we also use test data because model currently requires
    #       vocab from all samples to get be predictions
    log().info("getting topic data...")
    (X_train_raw, X_test_raw) = get_data(topics)

    # convert words to integers
    log().info("converting to integer representation...")
    word_to_id = build_vocab(list(X_train_raw) + list(X_test_raw), max_size=args.max_vocab_size)
    X_train_ids = raw_to_ids(X_train_raw, word_to_id)
    X_test_ids = raw_to_ids(X_test_raw, word_to_id)

    # pad
    log().info("padding sequences...")
    id_to_word = dict(zip(word_to_id.values(), word_to_id.keys()))
    X_train_ids = pad_sequences(X_train_ids, maxlen=args.max_doc_length, value=word_to_id[PAD_WORD],
                                padding='post', truncating='post')
    X_test_ids = pad_sequences(X_test_ids, maxlen=args.max_doc_length, value=word_to_id[PAD_WORD],
                               padding='post', truncating='post')
    vocab_size = len(word_to_id)

    # split train into train + validation
    X_train_ids, X_val_ids, Y_train, Y_val = train_test_split(
        X_train_ids, Y_train, test_size=0.20, random_state=42)

    # dataset summary
    title_break("Data Summary")
    log().info("{} topics selected: {}".format(len(topics), topics))
    log().info("n train: {}".format(len(X_train_ids)))
    log().info("n val:   {}".format(len(X_val_ids)))
    log().info("n test:  {}".format(len(X_test_ids)))
    log().info("max doc length: {}".format(args.max_doc_length))
    log().info("vocab size: {}".format(vocab_size))

    # ------------
    # Create model
    # ------------
    section_break("Creating Model")
    # create embedding layer
    if args.learn_embeddings:
        embedding = Embedding(vocab_size, args.embedding_size)
    else:
        embedding = create_embedding_layer(load_glove(), word_to_id, args.max_doc_length)

    # create LSTM layers
    lstm_size = args.lstm_size or embedding.output_dim
    lstm_args = {'dropout':args.dropout, 'recurrent_dropout': args.recurrent_dropout}
    lstm_layers = [LSTM(lstm_size, **lstm_args) for _ in range(args.lstm_depth)]
    if args.bidirectional:
        lstm_layers = [Bidirectional(l) for l in lstm_layers]

    # construct model
    model = Sequential()
    model.add(embedding)
    for l in lstm_layers: model.add(l)
    model.add(Dense(units=len(topics), activation='sigmoid'))
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    print(model.summary())

    # ---------
    # Fit model
    # ---------
    # create callbacks
    callbacks = [f1_metric]
    if not args.no_early_stopping:
        callbacks += [EarlyStopping(monitor='val_f1', mode='max', patience=2)]

    # fit
    section_break("Training Model")
    history = model.fit(X_train_ids, Y_train, epochs=args.epochs,
                       batch_size=args.batch_size, verbose=1,
                       validation_data=(X_val_ids, Y_val),
                       callbacks=callbacks)

    # --------------
    # Evaluate model
    # --------------
    section_break("Evaluating Model")
    threshold = 0.5
    Y_train_pred = model.predict(X_train_ids) > threshold
    Y_val_pred = model.predict(X_val_ids) > threshold
    Y_test_pred = model.predict(X_test_ids) > threshold
    ave = 'micro'
    scores_train = precision_recall_fscore_support(Y_train, Y_train_pred, average=ave)
    scores_val   = precision_recall_fscore_support(Y_val, Y_val_pred, average=ave)
    scores_test  = precision_recall_fscore_support(Y_test, Y_test_pred, average=ave)

    title_break("Performance")
    log().info("{:<10s}{:>15s}{:>15s}{:>15s}".format("Sample", "Precision", "Recall", "F1"))
    log().info("-"*55)
    log().info("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Train", *scores_train[:3]))
    log().info("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Val",   *scores_val[:3]))
    log().info("{:<10s}{:15.3f}{:15.3f}{:15.3f}".format("Test",  *scores_test[:3]))
    log().info("")

    # timer
    dt = stop_timer(ti)

    # --------
    # Finalize
    # --------
    section_break("Finalizing")
    log().info("Saving model to {}".format(args.output))
    model.save(args.output)
    auxname = os.path.splitext(args.output)[0] + '.pickle'
    log().info("Saving aux info to {}".format(auxname))
    with open(auxname, 'wb') as f:
        data = {
            'topics': topics,
            'id_to_word':id_to_word,
            'history': history.history,
            'scores':{
                'train': scores_train,
                'val': scores_val,
                'test': scores_test,
            },
            'time': dt.total_seconds(),
            'args': vars(args),
        }
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

    # TODO: use cross validation?


if __name__ == "__main__":
    main()

# EOF

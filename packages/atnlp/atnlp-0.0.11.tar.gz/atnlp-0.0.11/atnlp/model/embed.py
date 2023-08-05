# encoding: utf-8
"""
embed.py
~~~~~~~~

Functionality to load and implement word embeddings (eg. word2vec/glove).

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-30"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import os

# third party imports
import gensim
import numpy as np
from keras.layers import Embedding

# local imports
from atnlp.core.logger import log
from atnlp import EXT_DATA_DIR

# globals
EMB_DIR = os.path.join(EXT_DATA_DIR, "embeddings")


def load_glove(filename='glove.6B.300d.w2vformat.txt'):
    """Return glove word embedding model

    The embedding input can be specified with *filename*.
    The inputs are searched for in EMB_DIR.
    Check `scripts/install_glove.py` for installation.

    :param filename: glove input file name
    :return: word embedding model (gensim format)
    """
    filepath = os.path.join(EMB_DIR, filename)
    if not os.path.exists(filepath):
        log().error("failed to load glove embeddings, install with 'install_glove.py'")
        raise FileNotFoundError
    return gensim.models.KeyedVectors.load_word2vec_format(filepath, binary=False)


def create_embedding_layer(w2v, word_to_id, input_length):
    """Return keras embedding layer from pre-trained word embeddings

    :param w2v: pretrained word embedding model
    :param word_to_id: word-to-id dictionary
    :param input_length: length of input (ie number of words) for embedding layer
    :return: keras embedding layer
    """
    vocab_size = len(word_to_id)
    embedding_size = w2v.vector_size
    embedding_matrix = np.zeros((vocab_size, embedding_size))
    for (word, i) in word_to_id.items():
        if word in w2v:
            embedding_matrix[i] = w2v[word]
        else:
            embedding_matrix[i] = np.random.uniform(-0.25,0.25,embedding_size)

    return Embedding(vocab_size, embedding_size,
                     weights=[embedding_matrix],
                     input_length=input_length,
                     trainable=False)


# EOF
# encoding: utf-8
"""
parse.py
~~~~~~~~

Functionality for parsing text inputs.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-05"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports
import re
import collections

# third party imports
from sklearn.feature_extraction.stop_words import ENGLISH_STOP_WORDS as STOPWORDS

# local imports

# globals
TOKEN_PATTERN1 = re.compile(r"(?u)\b\w\w+\b")
PAD_WORD = "<pad>"
UNKNOWN_WORD = "<uw>"


# functions
def tokenize1(text):
    """Return tokenized list of strings from raw text input

    :param text: raw text (string)
    :return: list of tokens (strings)
    """
    return TOKEN_PATTERN1.findall(text)


def tokenize_keras(raw_data):
    """Return tokenized list of strings from raw text input using keras functionality

    :param raw_data: raw text (string)
    :return: list of tokens (strings)
    """
    from keras.preprocessing.text import text_to_word_sequence
    return [text_to_word_sequence(d) for d in raw_data]


def filter1(word):
    """Return True if word passes filter

    :param word: string
    :return: True or False
    """
    if not word: return False
    w = word.lower()
    if w in STOPWORDS: return False
    return True


def process_text(text, tokenize=tokenize1, filter=filter1, stem=None, lower=True):
    """Return processed list of words from raw text input

    To be honest, we're currently using sklearn CountVectorizer and
    keras text_to_word_sequence instead of this function.

    :param text: raw text input (string)
    :param tokenize: tokenizing function
    :param filter: filter function
    :param stem: stemming function
    :param lower: convert input text to lowercase if true
    :return: list of strings
    """
    assert tokenize, "Must provide tokenize method for preprocess_text"
    if not text: return []
    if lower: text = text.lower()
    words = tokenize(text)
    if filter: words = [w for w in words if filter(w)]
    if stem: words = [stem(w) for w in words]
    return words


def build_vocab(raw_data, max_size=None):
    """Return dict of word-to-id from raw text data

    If max_size is specified, vocab is truncated to set
    of highest frequency words within size.

    :param raw_data: list of strings
    :param max_size: maximum size of vocab
    :return: word-to-id dict
    """
    data = [w for doc in tokenize_keras(raw_data) for w in doc]
    counter = collections.Counter(data)
    count_pairs = sorted(counter.items(),
                         key=lambda x: (-x[1], x[0]))
    if max_size: count_pairs = count_pairs[:max_size]
    words, _ = list(zip(*count_pairs))
    word_to_id = dict(zip(words, range(len(words))))
    word_to_id[UNKNOWN_WORD] = len(word_to_id)
    word_to_id[PAD_WORD] = len(word_to_id)
    return word_to_id


def raw_to_ids(raw_data, word_to_id):
    """Convert raw text data into integer ids

    :param raw_data: raw text data (list of strings)
    :param word_to_id: word-to-id dict
    :return: list of list of integer ids
    """
    docs = tokenize_keras(raw_data)
    uid = word_to_id[UNKNOWN_WORD]
    return [[word_to_id.get(w, uid) for w in doc] for doc in docs]


# EOF
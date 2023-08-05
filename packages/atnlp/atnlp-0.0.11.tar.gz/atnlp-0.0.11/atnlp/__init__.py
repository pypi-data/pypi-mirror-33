"""Common configuration for the atnlp package

"""
import os

# globals
SRC_DIR = os.path.abspath(os.path.dirname(__file__))
TOP_DIR = os.path.abspath(os.path.join(SRC_DIR, '..'))
DATA_DIR = os.path.abspath(os.path.join(TOP_DIR,'data'))
RAW_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'raw'))
EXT_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'external'))
INT_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'interim'))
PRO_DATA_DIR = os.path.abspath(os.path.join(DATA_DIR, 'processed'))
NLTK_DIR = os.path.abspath(os.path.join(RAW_DATA_DIR, 'nltk'))

# set environment variable
os.environ["NLTK_DATA"] = NLTK_DIR

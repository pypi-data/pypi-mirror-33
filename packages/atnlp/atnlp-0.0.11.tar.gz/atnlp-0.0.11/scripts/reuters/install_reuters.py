#!/usr/bin/env python
# encoding: utf-8
"""
install_reuters.py
~~~~~~~~~~~~~~~~~~

Install the reuters corpus using the nltk api.

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-30"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import os

# third party imports
from nltk.downloader import download

# local imports
from atnlp import NLTK_DIR

# globals
def main():
    if not os.path.exists(NLTK_DIR):
        os.makedirs(NLTK_DIR)
        
    download('reuters', download_dir=NLTK_DIR)


if __name__ == '__main__':
    main()
# EOF

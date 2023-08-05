#!/usr/bin/env python
# encoding: utf-8
"""
print_modules.py
~~~~~~~~~~~~~~~~

Print list of modules in atnlp (used for auto sphinx documentation)

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-13"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# local imports
from atnlp.core.helpers import get_modules


def main():
    for m in get_modules('atnlp'):
        print(".. automodule:: {}\n    :members:".format(m))


if __name__ == "__main__":
    main()
# EOF
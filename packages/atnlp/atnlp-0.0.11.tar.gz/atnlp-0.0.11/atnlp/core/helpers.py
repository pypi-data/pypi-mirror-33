# encoding: utf-8
"""
helpers.py
~~~~~~~~~~

Collection of global framework helper functions

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-30"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
from time import time
from datetime import timedelta
import importlib.util
import pkgutil
import os
from importlib import import_module

# third party imports

# local imports
from atnlp.core.logger import log

# globals


def start_timer():
    """Return current time"""
    return time()


def stop_timer(ti):
    """Summarize job timing"""
    dt = timedelta(seconds=(time()-ti))
    time_str = str(dt)
    log().info("Execution time: {0}".format(time_str))
    return dt


def dynamic_import(path):
    """Import and return module from it's file path

    :param path: path to module in file system
    :return: module
    """
    spec = importlib.util.spec_from_file_location('tmpmod', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def get_modules(module):
    """Recursively return all submodule names

    :param module: module name
    :return: list of submodules
    """
    m = import_module(module)
    module_path = os.path.dirname(m.__file__)
    paths = []
    for _, name, ispkg in pkgutil.iter_modules([module_path]):
        submod = ".".join([module,name])
        if ispkg: paths += get_modules(submod)
        else:     paths.append(submod)
    return paths

# EOF
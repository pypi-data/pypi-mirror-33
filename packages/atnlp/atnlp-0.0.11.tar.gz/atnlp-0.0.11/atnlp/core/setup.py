# encoding: utf-8
"""
setup.py
~~~~~~~~

Function to setup the atnlp framework (call it before using the framework).

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-29"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import logging
import warnings
from time import localtime, asctime
import os

# third party imports
from sklearn.exceptions import UndefinedMetricWarning

# local imports
from atnlp.core.logger import log

# globals


def setup(
        log_level=None,
        suppress_warnings=None,
        tf_loglvl=2,
        batch_mode=False,
):
    """Global setup for atnlp framework

    :param log_level: logging output level
    :type log_level: logging.LEVEL (eg. DEBUG, INFO, WARNING...)
    :param suppress_warnings: list of warnings to suppress
    :type suppress_warnings: bool
    :param tf_loglvl: tensorflow log level
    :type tf_loglvl: int
    """
    # log level
    if log_level == None: log_level = logging.INFO
    log().setLevel(log_level)

    # get this show rolling
    log().info("Starting Job: %s" % (asctime(localtime())))

    # Suppress warnings
    if suppress_warnings is None:
        suppress_warnings = [
            UndefinedMetricWarning,
            UserWarning,
        ]
    log().info("Suppressing following warnings:")
    for warn in suppress_warnings:
        log().info("    {}".format(warn))
        warnings.filterwarnings("ignore", category=warn)

    # Set tensorflow log level
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = str(tf_loglvl)

    # set non-interactive backend if display not available
    if batch_mode or (os.name == 'posix' and "DISPLAY" not in os.environ):
        #import matplotlib
        #matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        plt.switch_backend('agg')

# EOF
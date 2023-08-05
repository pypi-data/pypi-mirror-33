# encoding: utf-8
"""
logger.py
~~~~~~~~~

Framework logging functionality

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-05-29"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 
import logging
import sys, os

# third party imports

# local imports

# globals
#: is global logger initialized (global variable)
gInitialized = False

# asci color codes
DEFAULT  = u'\x1b[39;49m'
BLUE     = u'\x1b[34m'
BLUEBOLD = u'\x1b[1;34m'
RED      = u'\x1b[31m'
REDBOLD  = u'\x1b[1;31m'
REDBKG   = u'\x1b[1;41;37m'
YELLOW   = u'\x1b[33m'
UNSET    = u'\x1b[0m'


def initialize(level=None):
    """initialize global logger

    :param level: logging output level
    :type level: logging.LEVEL (eg. DEBUG, INFO, WARNING...)
    """
    logging.basicConfig(
        filemode='w',
        level=level if level != None else logging.INFO,
        format='[%(asctime)s %(levelname)-7s]  %(message)s',
        datefmt='%H:%M:%S',
    )
    logging.getLogger("global")
    if supports_color():
        logging.StreamHandler.emit = add_coloring_to_emit_ansi(logging.StreamHandler.emit)


def log():
    """Return global logger"""
    global gInitialized
    if not gInitialized:
        initialize()
        gInitialized = True
    return logging.getLogger("global")


def setLevel(level):
    """Set global logging level"""
    log().setLevel(level)


def supports_color():
    """
    Returns True if the running system's terminal supports color, and False
    otherwise.
    """
    plat = sys.platform
    supported_platform = plat != 'Pocket PC' and (plat != 'win32' or 'ANSICON' in os.environ)
    # isatty is not always implemented
    is_a_tty = hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()
    if not supported_platform or not is_a_tty:
        return False
    return True


def add_coloring_to_emit_ansi(fn):
    # add methods we need to the class
    def new(*args):
        levelno = args[1].levelno
        if (levelno >= logging.CRITICAL):
            color = REDBKG
        elif (levelno >= logging.ERROR):
            color = REDBOLD
        elif (levelno >= logging.WARNING):
            color = RED
        elif (levelno >= logging.INFO):
            color = DEFAULT
        elif (levelno >= logging.DEBUG):
            color = YELLOW
        else:
            color = YELLOW
        args[1].msg = color + args[1].msg + UNSET
        return fn(*args)

    return new


def section_break(title=None):
    """Print section break to logger (at INFO level)

    :param title: section title (optional)
    """
    log().info("")
    log().info("="*60)
    if title:
        log().info(title)
        log().info("-"*len(title))
        log().info("")

def title_break(title):
    """Print title to logger (at INFO level)"""
    log().info("")
    log().info("-" * len(title))
    log().info(title)
    log().info("-" * len(title))
    log().info("")


# EOF
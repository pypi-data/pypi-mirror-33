# encoding: utf-8
"""
grid.py
~~~~~~~~~~~~~~~

Functionality for creating hyperparameter grid scans

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-01"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports
import os
import stat
from datetime import datetime

# third party imports
from sklearn.model_selection import ParameterGrid

# local imports

# globals


def create(params):
    """Return parameter grid (cross-product of individual parameter scans)

    The scan is defined by the *params* dictionary, where parameters to
     scan should be given a list of parameter values. Ie it should be in format:

    .. code-block:: python

        {'par1': [val1, val2],
         'par2': [val1, val2, val3],
         'par3': [val1]
         ...
         }

    :param params: params dictionary (with lists for parameters to be scanned)
    :return: model params for each scan point (list of dicts)
    """
    for (k,v) in params.items():
        if not isinstance(v, list):
            params[k] = [v]
    return list(ParameterGrid(params))


def tofile(grid, counter, exec, filename='grid.sh', shutdown=True):
    """Write parameter grid as sequence of commands in bash script

    *exec* is the command line function

    *counter* is a flag passed to the command line function that
    receives the command index as a string format argument. It can
    be used to increment the output model number, eg `-o model.{}.h5`

    If *shutdown* is true, a shutdown command will be included
    at the end of the script (useful for shutting down virtual
    instances after completing scan eg. in google cloud).

    :param grid: parameter grid
    :param counter: command line increment flag (string)
    :param exec: command line exec (string)
    :param filename: output file name
    :param shutdown: include shutdown command
    """
    with open(filename, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("#\n")
        f.write("# Grid scan created at {}\n".format(datetime.now()))
        f.write("#\n")
        f.write("# Suggest to execute with: \n")
        f.write("#\n")
        f.write("#   nohup ./{} &\n".format(filename))
        f.write("#\n")
        for (i,args) in enumerate(grid):
            count_str = counter.format(i)
            arg_str = " ".join(["--{}".format(k) if v is True
                                else "--{} {}".format(k,v)
                                for (k,v) in args.items()
                                if v is not False])
            f.write("{} {} {}\n".format(exec, count_str, arg_str))
        if shutdown:
            f.write("sudo poweroff\n")

    # make exec
    os.chmod(filename, os.stat(filename).st_mode | stat.S_IEXEC)


# EOF
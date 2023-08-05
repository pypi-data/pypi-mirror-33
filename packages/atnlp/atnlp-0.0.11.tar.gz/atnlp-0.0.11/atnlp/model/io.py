# encoding: utf-8
"""
io.py
~~~~~

Functionality for reading and writing models

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-07"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports
import os
import pkg_resources
import yaml

# third party imports
from sklearn.base import clone

# local imports
from atnlp.core.helpers import dynamic_import
from atnlp.core.logger import log

# globals


def create_model(model_name):
    MODEL_DIR = pkg_resources.resource_filename('atnlp', 'share/models/')
    paths = [
        model_name,
        os.path.join(MODEL_DIR, model_name),
        os.path.join(MODEL_DIR, model_name + ".py"),
    ]

    m = None
    for path in paths:
        if os.path.exists(path):
            try:
                mod = dynamic_import(path)
                if hasattr(mod, 'model'):
                    m = mod.model
                else:
                    log().warn("Model configuration script doesn't contain 'model' object")
                if m: break
            except:
                pass
    if not m:
        raise FileNotFoundError("couldn't load model")

    return clone(m)


def load_configured_model(cfg_name):

    CFG_DIR = pkg_resources.resource_filename('atnlp', 'share/config/')
    paths = [
        cfg_name,
        os.path.join(CFG_DIR, cfg_name),
        os.path.join(CFG_DIR, cfg_name + ".yml"),
    ]

    model_name = params = None
    for path in paths:
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = yaml.load(f)
                    model_name = data['model']
                    params = data['params']
                log().info("loaded model: {}".format(path))
                if model_name: break
            except:
                log.warn("failure parsing config file: {}".format(path))

    if not model_name:
        raise FileNotFoundError("couldn't load model configuration")

    model = create_model(model_name)
    if params:
        model.set_params(**params)

    return model

# EOF
# encoding: utf-8
"""
make_grid.py
~~~~~~~~~~~~~~~

NOTE: work in progress

"""
__author__ = "Will Davey"
__email__ = "wedavey@gmail.com"
__created__ = "2018-06-01"
__copyright__ = "Copyright 2018 Will Davey"
__license__ = "MIT https://opensource.org/licenses/MIT"

# standard imports 

# third party imports

# local imports
from atnlp.model import grid

# globals

basepars = {

}

# To check
# - max doc length
# - max vocab size
# - embeddings
# - lstm size / depth
# - dropout
# - bidirectional
# - batch size
# - start with high num epochs

# Strategy
# - start with default setup
# - find optimum epochs (start large)
# - scan batch size
# - scan doc length
# - try min/max length points on bidirectional
# - scan vocab size
# - try dropout
# - try increased depth
# - try more complex embeddings


params = {
    'param1': 1,
    'param2': ['foo', 'bar']
    }



grid.tofile(grid.create(params),
            "-o model.{}.h5",
            "train_reuters_rnn.py",
            "test_grid.sh",
            )


# EOF
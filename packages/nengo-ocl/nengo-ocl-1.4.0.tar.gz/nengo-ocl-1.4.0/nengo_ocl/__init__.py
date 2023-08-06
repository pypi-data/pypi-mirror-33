import logging
import sys

import numpy as np
import pyopencl as cl

from nengo.utils.logging import log

from .version import version as __version__
from .simulator import Simulator

numpy_relaxed_strides = np.ones((2, 1), order='C').flags.f_contiguous
pyopencl_relaxed_strides = hasattr(cl.compyte.array, 'equal_strides')
if numpy_relaxed_strides and not pyopencl_relaxed_strides:
    raise ImportError("Numpy (v%s) uses relaxed strides, and PyOpenCL (v%s) does"
                      " not support this. Please upgrade PyOpenCL." %
                      (np.__version__, cl.version.VERSION_TEXT))

# logging (default to no handler; use imported `log` fn to change this)
try:
    logging.root.addHandler(logging.NullHandler())
except AttributeError:
    # No NullHandler in Python 2.6
    pass

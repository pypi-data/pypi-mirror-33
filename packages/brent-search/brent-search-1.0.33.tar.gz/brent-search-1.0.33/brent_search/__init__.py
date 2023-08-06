from __future__ import absolute_import as _absolute_import

from ._bracket import bracket
from ._brent import brent
from ._optimize import minimize
from ._testit import test

__version__ = "1.0.33"

__all__ = ["__version__", "test", "bracket", "brent", "minimize"]

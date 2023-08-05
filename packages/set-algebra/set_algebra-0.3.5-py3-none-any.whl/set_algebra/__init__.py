"""
Set Algebra

Provides:
    Infinity, Negative Infinity
    Endpoint
    Interval
    Set
"""

__version__ = '0.3.5'
__author__ = 'Constantine Parkhimovich'
__license__ = 'MIT'
__copyright__ = 'Copyright 2014-2018 Constantine Parkhimovich'


from set_algebra.endpoint import Endpoint, are_bounding
from set_algebra.infinity import Infinity, NegativeInfinity, is_finite, inf, neg_inf
from set_algebra.interval import Interval, is_interval, is_scalar, unbounded
from set_algebra.set_ import Set


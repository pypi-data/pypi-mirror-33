"""Unoccupied - Find unoccupied name."""

from .main import unoccupied
from .main import UnoccupiedNameNotFound
from .namefinder import BaseNameFinder
from .namefinder import NumberNameFinder
from .namefinder import FileNameFinder

__version__ = '0.2.0'

__all__ = ['unoccupied',
           'UnoccupiedNameNotFound',
           'BaseNameFinder',
           'NumberNameFinder',
           'FileNameFinder']

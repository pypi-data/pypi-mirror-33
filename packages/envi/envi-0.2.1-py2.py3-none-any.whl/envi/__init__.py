"""Top-level package for envi."""
from .envi import (
    get, get_int, get_bool, get_float, get_str, mk_shortcut  # noqa
)

__all__ = [
    'get', 'get_float', 'get_int', 'get_bool', 'get_str', 'mk_shortcut'
]

__author__ = """Simone Basso"""
__email__ = 'simone.basso1990@gmail.com'
__version__ = '0.1.0'

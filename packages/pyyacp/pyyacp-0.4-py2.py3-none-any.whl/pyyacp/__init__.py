# -*- coding: utf-8 -*-

from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = '0.4'


"""Main module."""

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

class YACParserException(Exception):
    pass


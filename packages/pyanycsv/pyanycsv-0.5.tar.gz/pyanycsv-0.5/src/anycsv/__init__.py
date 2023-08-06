# -*- coding: utf-8 -*-
from pkg_resources import get_distribution, DistributionNotFound

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = 'pyanycsv'
    __version__ = get_distribution(dist_name).version
except DistributionNotFound:
    __version__ = '0.5'

from anycsv.csv_parser import reader
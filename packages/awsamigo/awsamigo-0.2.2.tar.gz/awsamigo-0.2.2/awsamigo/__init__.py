"""
Wrapper for quich & easy AMI lookup via boto3.
"""

import os

from pkg_resources import get_distribution

from . import const, finder

__version__ = get_distribution('awsamigo').version


def new_filter(filters=None):
    """
    Returns the default lookup filters.

    :param filters: dict    - The defaults are updated with this dict before being returned.
    :returns:       dict
    """
    out = dict(const.DEFAULT_FILTERS)

    if filters is not None:
        if not isinstance(filters, dict):
            raise TypeError("Filters must be provided as dictionary!")

        out.update(filters)
    
    return out

def new_finder(region):
    """
    Returns a new finder object.

    :param region:  str     - The AWS region to connect to.
    """
    return finder.Finder(region)

"""
This module provides the Finder() class.
"""

import sys
import boto3
import dateutil

from . import const


class Finder(object):
    def __init__(self, region):
        """
        A finder is capable of performing boto3 API calls to receive a list of
        existing AMIs. The results are cached, for better performance on
        subsequent calls.

        :param region:  str     - The AWS region to connect to.
        """
        self.__client = boto3.client('ec2', region_name=region.lower())
        self.__cache = None

    @property
    def client(self):
        """
        Return the boto3.client of this finder for external use.

        :returns: boto3.client
        """
        return self.__client

    @staticmethod
    def _convert_filters(filters):
        """
        Convert a filter dict to a format AWS expects it in.

        :param filters: dict    - Filters for the AMI lookup call.
        :returns:       list    - The filters in the format AWS expects them in.
        """
        out = []
        for f in const.DEFAULT_FILTERS:
            out.append({'Name': f, 'Values': filters[f]})
        return out

    def _find_latest_image(self, images):
        """
        Filter the latest AMI image from a list of available images.

        :param images:  list    - List of AMI images.
        :returns:       dict    - The latest AMI image from the list.
        """
        latest = None
        for image in images:
            if latest is None:
                latest = image
                continue
            
            if dateutil.parser.parse(image['CreationDate']) > dateutil.parser.parse(latest['CreationDate']):  # PRAGMA: NOQA
                latest = image

        return latest

    def clear_cache(self):
        """
        Clear the local result cache.
        """
        self.__cache = None

    def search(self, owner, filters=None):
        """
        Query AWS for a list of available AMI images based on our filters.

        :param owner:   str     - The human-readable name of the AWS account holder to query.
        :param filters: dict    - Lookup filters.
        :returns:       list
        """
        if self.__cache is None:
            try:
                int(owner)
            except ValueError:
                try:
                    owner = const.DISTRO_OWNER_IDS[owner]
                except KeyError:
                    sys.stderr.write(
                        "Distribution not yet supported: {}\n".format(owner))
                    sys.stderr.write("Please feel welcome to provide a pull-request at: ")
                    sys.stderr.write("https://github.com/baccenfutter/awsamigo\n")
                    sys.exit(1)

            if filters is None:
                filters = const.DEFAULT_FILTERS
            
            filters = self._convert_filters(filters)
            self.__cache = self.__client.describe_images(Owners=[owner], Filters=filters)
        
        return self.__cache

    def latest(self, owner, filters=None, attr=None):
        """
        Query AWS for the latest available AMI image based on our fiters.

        :param owner:   str     - The human-readable name of the AWS account holder to query.
        :param filters: dict    - Lookup filters.
        :param attr:    str     - Optionally only return this attribute of the result,
                                  i.e. 'ImageId'.

        :returns: dict          - Or the type of whatever attribute you demand.
        """
        results = self.search(owner, filters)
        latest = self._find_latest_image(results['Images'])

        if attr is not None:
            return latest[attr]
        
        return latest


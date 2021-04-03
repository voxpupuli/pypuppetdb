from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re

import pypuppetdb.types
from pypuppetdb.api.base import BaseAPI

log = logging.getLogger(__name__)


class PqlAPI(BaseAPI):

    def pql(self, pql, **kwargs):
        """Makes a PQL (Puppet Query Language) and tries to cast results
         to a rich type. If it won't work, returns plain dicts.

        :param pql: PQL query
        :type pql: :obj:`string`

        :param \*\*kwargs: The rest of the keyword arguments are passed
        to the _pql function

        :returns: A generator yielding elements of a rich type or plain dicts
        """

        type_class = self._get_type_from_query(pql)

        for element in self._pql(pql=pql, **kwargs):
            # TODO: we need to pull the methods for casting out of methods like QueryAPI.nodes()
            # if type_class:
            #     yield type_class(element)
            # else:
            #     yield element
            yield element

    @staticmethod
    def _get_type_from_query(pql):
        """Gets a rich type of the entities returned by the given
        PQL query.

        :param pql: PQL query
        :return: a rich type, if there
        """

        # in PQL the beginning of the query is the type of returned entities
        # but only if the projection is empty ([]) or there is no projection
        pattern = re.compile(r'(.*?)\s*(\[])?\s*{')
        match = pattern.match(pql)

        if match:
            type_str = match.group()
            type_str = type_str.capitalize()
            type_class = getattr(pypuppetdb.types, type_str)
            if type_class:
                return type_class
            else:
                log.debug(f"PQL returns entities of a type {type_str}, but it is not supported"
                          " by this library yet.")
                return None
        else:
            return None

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import re
from datetime import datetime

import pypuppetdb
from pypuppetdb.QueryBuilder import (EqualsOperator)
from pypuppetdb.api.base import BaseAPI
from pypuppetdb.errors import (APIError)
from pypuppetdb.types import (Catalog, Node, Report)

log = logging.getLogger(__name__)


class PqlAPI(BaseAPI):

    def _pql(self, pql=None, request_method='GET'):
        """This method actually queries PuppetDB. Provided an endpoint and an
        optional path and/or query it will fire a request at PuppetDB. If
        PuppetDB can be reached and answers within the timeout we'll decode
        the response and give it back or raise for the HTTP Status Code
        PuppetDB gave back.

        :param pql: (optional) A PQL query to further narrow down the resultset.
        :type pql: :obj:`string`

        :raises: :class:`~pypuppetdb.errors.EmptyResponseError`

        :returns: The decoded response from PuppetDB
        :rtype: :obj:`dict` or :obj:`list`
        """

        log.debug(f"_pql called with ",
                  # comma-separated list of method arguments with their values
                  ", ".join([f"{arg}: {locals().get(arg, 'None')}"
                             for arg in locals().keys() if arg != 'self'])
                  )

        if not pql:
            log.error("PQL query is required!")
            raise APIError

        payload = {}

        # PQL queries are made to the same endpoint regardless of the queried entities
        url = self._url('pql')
        payload['query'] = pql

        return self._make_request(url, request_method, payload)

    # TODO: deduplicate this - see QueryAPI.nodes()
    def pql(self, pql, with_status=False, unreported=2, with_event_numbers=True):
        """Makes a PQL (Puppet Query Language) and tries to cast results
         to a rich type. If it won't work, returns plain dicts.

        :param pql: PQL query
        :type pql: :obj:`string`

        :param with_status: (optional, only for queries for nodes) include
                           the node status in the returned nodes
        :type with_status: :bool:
        :param unreported: (optional, only for queries for nodes) amount
                           of hours when a node gets marked as unreported
        :type unreported: :obj:`None` or integer
        :param with_event_numbers: (optional, only for queries for nodes)
                           include the exact number of
                           changed/unchanged/failed/noop events when
                           with_status is set to True. If set to False
                           only "some" string is provided if there are
                           resources with such status in the last report.
                           This provides performance benefits as potentially
                           slow event-counts query is omitted completely.
        :type with_event_numbers: :bool:

        :returns: A generator yielding elements of a rich type or plain dicts
        """

        pql = pql.strip()

        type_class = self._get_type_from_query(pql)

        if type_class == Node and (with_status or unreported != 2 or not with_event_numbers):
            log.error("with_status, unreported and with_event_numbers are used only"
                      " for queries for nodes!")
            raise APIError

        for element in self._pql(pql=pql):
            if type_class == Node:

                # TODO: deduplicate this - see QueryAPI.nodes()

                now = datetime.utcnow()

                latest_events = None
                if with_status and with_event_numbers:
                    latest_events = self._query(
                        'event-counts',
                        query=EqualsOperator("latest_report?", True),
                        summarize_by='certname',
                    )

                yield Node.create_from_dict(self, element, with_status, with_event_numbers,
                                            latest_events, now, unreported)

            elif type_class == Report:
                yield Report.create_from_dict(self, element)
            elif type_class:
                yield type_class.create_from_dict(element)
            else:
                yield element

    @staticmethod
    def _get_type_from_query(pql):
        """Gets a rich type of the entities returned by the given
        PQL query.

        :param pql: PQL query
        :type pql: :obj:`string`

        :return: a rich type, if this library supports it
                 otherwise - None
        """

        pql = pql.strip()

        # in PQL the beginning of the query is the type of returned entities
        # but only if the projection is empty ([]) or there is no projection
        pattern = re.compile(r'([a-z]*?)\s*(\[])?\s*{')
        match = pattern.match(pql)

        if match:
            type_name_lowercase = match.group(1)

            # class name is capitalized
            type_name = type_name_lowercase.capitalize()

            # depluralize - remove trailing "s"
            if type_name.endswith("s"):
                type_name_singular = type_name[:-1]
            else:
                type_name_singular = type_name

            log.debug(f"Type name: {type_name_singular}")
            try:
                type_class = getattr(pypuppetdb.types, type_name_singular)
                return type_class
            except AttributeError:
                log.debug(f"PQL returns entities of a type {type_name_singular},"
                          f" but it is not supported by this library yet.")
                return None
        else:
            log.debug(f"No match!")
            return None

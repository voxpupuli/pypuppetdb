from __future__ import unicode_literals
from __future__ import absolute_import

import logging

from pypuppetdb.api.v3 import API as BaseAPI
from pypuppetdb.types import (
    Node, Fact, Resource,
    )

log = logging.getLogger(__name__)


class API(BaseAPI):
    """The API object for version 4 of the PuppetDB API. This object contains
    all v4 specific methods and ways of doing things.

    :param \*\*kwargs: Rest of the keywoard arguments passed on to our parent\
            :class:`~pypuppetdb.api.BaseAPI`.
    """
    api_version = 4

    def _url(self, endpoint, path=None, environment=None):
        """The complete URL we will end up querying. Depending on the
        endpoint we pass in  this will result in different URL's with
        different prefixes.

        :param endpoint: The PuppetDB API endpoint we want to query.
        :type endpoint: :obj:`string`
        :param path: An additional path if we don't wish to query the\
                bare endpoint.
        :type path: :obj:`string`

        :returns: A URL constructed from :func:`base_url` with the\
                apropraite API version/prefix and the rest of the path added\
                to it.
        :rtype: :obj:`string`
        """

        log.debug('_url called with endpoint: {0} and path: {1}'.format(
            endpoint, path))

        if endpoint in self.endpoints:
            api_prefix = self.api_prefix
            endpoint = self.endpoints[endpoint]
        else:
            # If we reach this we're trying to query an endpoint that doesn't
            # exist. This shouldn't happen unless someone made a booboo.
            raise APIError

        if environment:
            endpoint = "environments/{environment}/{endpoint}".format(
                environment=environment,
                endpoint=endpoint,
            )

        url = '{base_url}/{api_prefix}/{endpoint}'.format(
            base_url=self.base_url,
            api_prefix=api_prefix,
            endpoint=endpoint,
            )

        if path is not None:
            url = '{0}/{1}'.format(url, path)

        return url

    def nodes(self, name=None, query=None, unreported=2, with_status=False):
        """Query for nodes by either name or query. If both aren't
        provided this will return a list of all nodes. This method
        also fetches the nodes status and event counts of the latest
        report from puppetdb.

        :param name: (optional)
        :type name: :obj:`None` or :obj:`string`
        :param query: (optional)
        :type query: :obj:`None` or :obj:`string`
        :param with_status: (optional) include the node status in the\
                           returned nodes
        :type with_status: :bool:
        :param unreported: (optional) amount of hours when a node gets
                           marked as unreported
        :type unreported: :obj:`None` or integer

        :returns: A generator yieling Nodes.
        :rtype: :class:`pypuppetdb.types.Node`
        """
        nodes = self._query('nodes', path=name, query=query)
        # If we happen to only get one node back it
        # won't be inside a list so iterating over it
        # goes boom. Therefor we wrap a list around it.
        if type(nodes) == dict:
            nodes = [nodes, ]

        if with_status:
            latest_events = self._query(
                'event-counts',
                query='["=","latest-report?",true]',
                summarize_by='certname')

        for node in nodes:
            node['unreported_time'] = None
            node['status'] = None

            if with_status:
                status = [s for s in latest_events
                          if s['subject']['title'] == node['name']]

            # node status from events
            if with_status and status:
                node['events'] = status = status[0]
                if status['successes'] > 0:
                    node['status'] = 'changed'
                if status['noops'] > 0:
                    node['status'] = 'noop'
                if status['failures'] > 0:
                    node['status'] = 'failed'
            else:
                if with_status:
                    node['status'] = 'unchanged'
                node['events'] = None

            # node report age
            if with_status and node['report-timestamp'] is not None:
                try:
                    last_report = json_to_datetime(node['report-timestamp'])
                    last_report = last_report.replace(tzinfo=None)
                    now = datetime.utcnow()
                    unreported_border = now-timedelta(hours=unreported)
                    if last_report < unreported_border:
                        delta = (datetime.utcnow()-last_report)
                        node['status'] = 'unreported'
                        node['unreported-time'] = '{0}d {1}h {2}m'.format(
                            delta.days,
                            int(delta.seconds/3600),
                            int((delta.seconds % 3600)/60)
                            )
                except AttributeError:
                    node['status'] = 'unreported'

            if not node['report-timestamp'] and with_status:
                node['status'] = 'unreported'

            yield Node(self,
                       node['name'],
                       deactivated=node['deactivated'],
                       report_timestamp=node['report-timestamp'],
                       catalog_timestamp=node['catalog-timestamp'],
                       facts_timestamp=node['facts-timestamp'],
                       status=node['status'],
                       events=node['events'],
                       unreported_time=node['unreported_time']
                       )

    def facts(self, name=None, value=None, query=None, environment=None):
        """Query for facts limited by either name, value and/or query.
        This will yield a single Fact object at a time."""

        log.debug('{0}, {1}, {2}'.format(name, value, query))
        if name is not None and value is not None:
            path = '{0}/{1}'.format(name, value)
        elif name is not None and value is None:
            path = name
        elif name is None and value is None and query is not None:
            path = None
        else:
            log.debug("We want to query for all facts.")
            query = ''
            path = None

        facts = self._query('facts', path=path, query=query,
                            environment=environment)
        for fact in facts:
            yield Fact(
                fact['certname'],
                fact['name'],
                fact['value'],
                )

    def resources(self, type_=None, title=None, query=None, environment=None):
        """Query for resources limited by either type and/or title or query.
        This will yield a Resources object for every returned resource."""

        path = None

        if type_ is not None:
            type_ = self._normalize_resource_type(type_)

            if title is not None:
                path = '{0}/{1}'.format(type_, title)
            elif title is None:
                path = type_
        elif query is None:
            log.debug('Going to query for all resources. This is usually a '
                      'bad idea as it might return enormous amounts of '
                      'resources.')

        resources = self._query('resources', path=path, query=query,
                                environment=environment)

        for resource in resources:
            yield Resource(
                resource['certname'],
                resource['title'],
                resource['type'],
                resource['tags'],
                resource['exported'],
                resource['file'],
                resource['line'],
                resource['parameters'],
                resource['environment'],
                )

    def reports(self, query, environment=None):
        """Get reports for our infrastructure. Currently reports can only
        be filtered through a query which requests a specific certname.
        If not it will return all reports.

        This yields a Report object for every returned report."""
        reports = self._query('reports', query=query,
                              environment=environment)
        for report in reports:
            yield Report(
                report['certname'],
                report['hash'],
                report['start-time'],
                report['end-time'],
                report['receive-time'],
                report['configuration-version'],
                report['report-format'],
                report['puppet-version'],
                report['transaction-uuid']
                )

    def events(self, query, environments=None):
        """A report is made up of events. This allows to query for events
        based on the reprt hash.
        This yields an Event object for every returned event."""

        events = self._query('events', query=query,
                             environment=environment)
        for event in events:
            yield Event(
                event['certname'],
                event['status'],
                event['timestamp'],
                event['report'],
                event['resource-title'],
                event['property'],
                event['message'],
                event['new-value'],
                event['old-value'],
                event['resource-type'],
                )

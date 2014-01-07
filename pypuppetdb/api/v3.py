from __future__ import unicode_literals
from __future__ import absolute_import

import logging

from pypuppetdb.api import BaseAPI
from pypuppetdb.utils import json_to_datetime
from datetime import datetime, timedelta
from pypuppetdb.types import (
    Node, Fact, Resource,
    Report, Event, Catalog
    )

log = logging.getLogger(__name__)


class API(BaseAPI):
    """The API object for version 3 of the PuppetDB API. This object contains
    all v3 specific methods and ways of doing things.

    :param \*\*kwargs: Rest of the keywoard arguments passed on to our parent\
            :class:`~pypuppetdb.api.BaseAPI`.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the API object."""
        super(API, self).__init__(api_version=3, **kwargs)
        log.debug('API initialised with {0}.'.format(kwargs))

    def node(self, name):
        """Gets a single node from PuppetDB."""
        nodes = self.nodes(name=name)
        return next(node for node in nodes)

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
                if status['failures'] > 0:
                    node['status'] = 'failed'
            else:
                if with_status:
                    node['status'] = 'unchanged'
                node['events'] = None

            # node report age
            if with_status and node['report_timestamp'] is not None:
                try:
                    last_report = json_to_datetime(node['report_timestamp'])
                    last_report = last_report.replace(tzinfo=None)
                    now = datetime.utcnow()
                    unreported_border = now-timedelta(hours=unreported)
                    if last_report < unreported_border:
                        delta = (datetime.utcnow()-last_report)
                        node['status'] = 'unreported'
                        node['unreported_time'] = '{0}d {1}h {2}m'.format(
                            delta.days,
                            int(delta.seconds/3600),
                            int((delta.seconds % 3600)/60)
                            )
                except AttributeError:
                    node['status'] = 'unreported'

            if not node['report_timestamp'] and with_status:
                node['status'] = 'unreported'

            yield Node(self,
                       node['name'],
                       deactivated=node['deactivated'],
                       report_timestamp=node['report_timestamp'],
                       catalog_timestamp=node['catalog_timestamp'],
                       facts_timestamp=node['facts_timestamp'],
                       status=node['status'],
                       events=node['events'],
                       unreported_time=node['unreported_time']
                       )

    def facts(self, name=None, value=None, query=None):
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

        facts = self._query('facts', path=path, query=query)
        for fact in facts:
            yield Fact(
                fact['certname'],
                fact['name'],
                fact['value'],
                )

    def fact_names(self):
        """Get a list of all known facts."""

        return self._query('fact-names')

    def resources(self, type_=None, title=None, query=None):
        """Query for resources limited by either type and/or title or query.
        This will yield a Resources object for every returned resource."""

        log.debug('YOLO')
        if type_ is not None:
            # Need to capitalize the resource type since PuppetDB doesn't
            # answer to lower case type names.
            # bugs.puppetlabs.com/some_value
            type_ = type_.capitalize()
            if title is not None:
                path = '{0}/{1}'.format(type_, title)
            elif title is None:
                path = type_
        else:
            log.debug('Going to query for all resources. This is usually a '
                      'bad idea as it might return enormous amounts of '
                      'resources.')
            query = ''
            path = None

        resources = self._query('resources', path=path, query=query)
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
                )

    def reports(self, query):
        """Get reports for our infrastructure. Currently reports can only
        be filtered through a query which requests a specific certname.
        If not it will return all reports.

        This yields a Report object for every returned report."""
        reports = self._query('reports', query=query)
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

    def events(self, query):
        """A report is made up of events. This allows to query for events
        based on the reprt hash.
        This yields an Event object for every returned event."""

        events = self._query('events', query=query)
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

    def event_counts(self, query, summarize_by,
                     count_by=None, count_filter=None):
        """Get event counts from puppetdb"""
        return self._query('event-counts',
                           query=query,
                           summarize_by=summarize_by,
                           count_by=count_by,
                           count_filter=count_filter)

    def aggregate_event_counts(self, query, summarize_by,
                               count_by=None, count_filter=None):
        """Get event counts from puppetdb"""
        return self._query('aggregate-event-counts',
                           query=query, summarize_by=summarize_by,
                           count_by=count_by, count_filter=count_filter)

    def server_time(self):
        """Get the current time of the clock on the PuppetDB server"""
        return self._query('server-time')['server-time']

    def current_version(self):
        """Get version information about the running PuppetDB server"""
        return self._query('version')['version']

    def catalog(self, node):
        """Get the most recent catalog for a given node"""
        c = self._query('catalogs', path=node)
        return Catalog(c['data']['name'],
                       c['data']['edges'],
                       c['data']['resources'],
                       c['data']['version'],
                       c['data']['transaction-uuid'])

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
    """The API object for version 4 of the PuppetDB API. This object contains
    all v4 specific methods and ways of doing things.

    :param \*\*kwargs: Rest of the keywoard arguments passed on to our parent\
            :class:`~pypuppetdb.api.BaseAPI`.
    """

    def __init__(self, *args, **kwargs):
        """Initialise the API object."""
        super(API, self).__init__(api_version=4, **kwargs)
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
            latest_reports = self._query(
                'reports',
                query='["=","latest_report?",true]'
            )

        for node in nodes:
            node['unreported_time'] = None
            node['status'] = None
            node['events'] = None

            if with_status:
                report = [s for s in latest_reports
                          if s['certname'] == node['certname']]

                events = list(report[0]['resource_events']['data'])
                node['events'] = len(events)

                if report[0]['noop']:
                    node['status'] = 'noop'
                else:
                    node['status'] = report[0]['status']

            # node report age
            if with_status and node['report_timestamp'] is not None:
                try:
                    last_report = json_to_datetime(node['report_timestamp'])
                    last_report = last_report.replace(tzinfo=None)
                    now = datetime.utcnow()
                    unreported_border = now - timedelta(hours=unreported)
                    if last_report < unreported_border:
                        delta = (datetime.utcnow() - last_report)
                        node['status'] = 'unreported'
                        node['unreported_time'] = '{0}d {1}h {2}m'.format(
                            delta.days,
                            int(delta.seconds / 3600),
                            int((delta.seconds % 3600) / 60)
                        )
                except AttributeError:
                    node['status'] = 'unreported'

            if not node['report_timestamp'] and with_status:
                node['status'] = 'unreported'

            yield Node(self,
                       node['certname'],
                       deactivated=node['deactivated'],
                       expired=node['expired'],
                       report_timestamp=node['report_timestamp'],
                       catalog_timestamp=node['catalog_timestamp'],
                       facts_timestamp=node['facts_timestamp'],
                       status=node['status'],
                       events=node['events'],
                       unreported_time=node['unreported_time'],
                       report_environment=node['report_environment'],
                       catalog_environment=node['catalog_environment'],
                       facts_environment=node['facts_environment']
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
                fact['environment']
            )

    def resources(self, type_=None, title=None, query=None):
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

        resources = self._query('resources', path=path, query=query)
        for resource in resources:
            yield Resource(
                node=resource['certname'],
                name=resource['title'],
                type_=resource['type'],
                tags=resource['tags'],
                exported=resource['exported'],
                sourcefile=resource['file'],
                sourceline=resource['line'],
                parameters=resource['parameters'],
                environment=resource['environment'],
            )

    def reports(self, query):
        """Get reports for our infrastructure. Currently reports can only
        be filtered through a query which requests a specific certname.
        If not it will return all reports.

        This yields a Report object for every returned report."""
        reports = self._query('reports', query=query)
        for report in reports:
            yield Report(
                api=self,
                node=report['certname'],
                hash_=report['hash'],
                start=report['start_time'],
                end=report['end_time'],
                received=report['receive_time'],
                version=report['configuration_version'],
                format_=report['report_format'],
                agent_version=report['puppet_version'],
                transaction=report['transaction_uuid'],
                environment=report['environment'],
                status=report['status'],
                noop=report['noop'],
                metrics=report['metrics']['data'],
                logs=report['logs']['data']
            )

    def events(self, query, order_by=None, limit=None):
        """A report is made up of events. This allows to query for events
        based on the reprt hash.
        This yields an Event object for every returned event."""

        events = self._query('events', query=query,
                             order_by=order_by, limit=limit)
        for event in events:
            yield Event(
                node=event['certname'],
                status=event['status'],
                timestamp=event['timestamp'],
                hash_=event['report'],
                title=event['resource_title'],
                property_=event['property'],
                message=event['message'],
                new_value=event['new_value'],
                old_value=event['old_value'],
                type_=event['resource_type'],
                class_=event['containing_class'],
                execution_path=event['containment_path'],
                source_file=event['file'],
                line_number=event['line'],
            )

    def aggregate_event_counts(self, query, summarize_by,
                               count_by=None, count_filter=None):
        """Get event counts from puppetdb"""
        return self._query('aggregate-event-counts',
                           query=query, summarize_by=summarize_by,
                           count_by=count_by, count_filter=count_filter)

    def event_counts(self, query, summarize_by,
                     count_by=None, count_filter=None):
        """Get event counts from puppetdb"""
        return self._query('event-counts',
                           query=query,
                           summarize_by=summarize_by,
                           count_by=count_by,
                           count_filter=count_filter)

    def catalog(self, node=None):
        """Get the most recent catalog for a given node"""
        catalogs = self._query('catalogs', path=node)

        for catalog in catalogs:
            yield Catalog(node=catalog['certname'],
                          edges=catalog['edges']['data'],
                          resources=catalog['resources']['data'],
                          version=catalog['version'],
                          transaction_uuid=catalog['transaction_uuid'],
                          environment=catalog['environment'])

    def server_time(self):
        """Get the current time of the clock on the PuppetDB server"""
        return self._query('server-time')[self.parameters['server_time']]

    def current_version(self):
        """Get version information about the running PuppetDB server"""
        return self._query('version')['version']

    def edges(self, query=None):
        """Get the known catalog edges, formed between tow resources"""
        edges = self._query('edges', query=query)

        for edge in edges:
            identifier_source = edge['source_type'] + \
                '[' + edge['source_title'] + ']'
            identifier_target = edge['target_type'] + \
                '[' + edge['target_title'] + ']'
            yield Edge(source=self.resources[identifier_source],
                       target=self.resources[identifier_target],
                       relationship=edge['relationship'],
                       node=edge['certname'])

    def environments(self, query=None):
        """Get all known environments from Puppetdb"""
        return self._query('environments', query=query)

    def factsets(self, query=None):
        """Returns a set of all facts or for a single certname"""
        return self._query('factsets', query=query)

    def fact_paths(self, query=None):
        """Fact Paths are intended to be a counter-part of the fact-names
        endpoint. It provides increased granularity around structured
        facts and may be used for building GUI autocompletions or other
        applications that require a basic top-level view of fact paths."""
        return self._query('fact-paths', query=query)

    def fact_contents(self, query=None):
        """To complement fact_paths(), this endpoint provides the capability
        to descend into structured facts and retreive the values associated
        with fact paths"""
        return self._query('fact-contents', query=query)

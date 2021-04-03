from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from datetime import datetime, timedelta

from pypuppetdb.QueryBuilder import (EqualsOperator)
from pypuppetdb.api.base import BaseAPI
from pypuppetdb.errors import (APIError)
from pypuppetdb.types import (Catalog, Edge, Event, Fact, Inventory,
                              Node, Report, Resource)
from pypuppetdb.utils import json_to_datetime

log = logging.getLogger(__name__)


class QueryAPI(BaseAPI):

    def nodes(self, unreported=2, with_status=False, with_event_numbers=True,
              **kwargs):
        """Query for nodes by either name or query. If both aren't
        provided this will return a list of all nodes. This method
        also (optionally) fetches the nodes status and (optionally)
        event counts of the latest report from puppetdb.

        :param with_status: (optional) include the node status in the\
                           returned nodes
        :type with_status: :bool:
        :param unreported: (optional) amount of hours when a node gets
                           marked as unreported
        :type unreported: :obj:`None` or integer
        :param with_event_numbers: (optional) include the exact number of\
                           changed/unchanged/failed/noop events when\
                           with_status is set to True. If set to False
                           only "some" string is provided if there are
                           resources with such status in the last report.
                           This provides performance benefits as potentially
                           slow event-counts query is omitted completely.
        :type with_event_numbers: :bool:
        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function

        :returns: A generator yieling Nodes.
        :rtype: :class:`pypuppetdb.types.Node`
        """
        nodes = self._query('nodes', **kwargs)
        now = datetime.utcnow()
        # If we happen to only get one node back it
        # won't be inside a list so iterating over it
        # goes boom. Therefor we wrap a list around it.
        if type(nodes) == dict:
            nodes = [nodes, ]

        if with_status and with_event_numbers:
            latest_events = self.event_counts(
                query=EqualsOperator("latest_report?", True),
                summarize_by='certname'
            )

        for node in nodes:
            node['status_report'] = None
            node['events'] = None

            if with_status:
                if with_event_numbers:
                    status = [s for s in latest_events
                              if s['subject']['title'] == node['certname']]

                    try:
                        node['status_report'] = node['latest_report_status']

                        if status:
                            node['events'] = status[0]
                    except KeyError:
                        if status:
                            node['events'] = status = status[0]
                            if status['successes'] > 0:
                                node['status_report'] = 'changed'
                            if status['noops'] > 0:
                                node['status_report'] = 'noop'
                            if status['failures'] > 0:
                                node['status_report'] = 'failed'
                        else:
                            node['status_report'] = 'unchanged'
                else:
                    node['status_report'] = node['latest_report_status']
                    node['events'] = {
                        'successes': 0,
                        'failures': 0,
                        'noops': 0,
                    }
                    if node['status_report'] == 'changed':
                        node['events']['successes'] = 'some'
                    elif node['status_report'] == 'noop':
                        node['events']['noops'] = 'some'
                    elif node['status_report'] == 'failed':
                        node['events']['failures'] = 'some'

                # node report age
                if node['report_timestamp'] is not None:
                    try:
                        last_report = json_to_datetime(
                            node['report_timestamp'])
                        last_report = last_report.replace(tzinfo=None)
                        unreported_border = now - timedelta(hours=unreported)
                        if last_report < unreported_border:
                            delta = (now - last_report)
                            node['unreported'] = True
                            node['unreported_time'] = '{0}d {1}h {2}m'.format(
                                delta.days,
                                int(delta.seconds / 3600),
                                int((delta.seconds % 3600) / 60)
                            )
                    except AttributeError:
                        node['unreported'] = True

                if not node['report_timestamp']:
                    node['unreported'] = True

            yield Node(self,
                       name=node['certname'],
                       deactivated=node['deactivated'],
                       expired=node['expired'],
                       report_timestamp=node['report_timestamp'],
                       catalog_timestamp=node['catalog_timestamp'],
                       facts_timestamp=node['facts_timestamp'],
                       status_report=node['status_report'],
                       noop=node.get('latest_report_noop'),
                       noop_pending=node.get('latest_report_noop_pending'),
                       events=node['events'],
                       unreported=node.get('unreported'),
                       unreported_time=node.get('unreported_time'),
                       report_environment=node['report_environment'],
                       catalog_environment=node['catalog_environment'],
                       facts_environment=node['facts_environment'],
                       latest_report_hash=node.get('latest_report_hash'),
                       cached_catalog_status=node.get('cached_catalog_status')
                       )

    def node(self, name):
        """Gets a single node from PuppetDB.

        :param name: The name of the node search.
        :type name: :obj:`string`

        :return: An instance of Node
        :rtype: :class:`pypuppetdb.types.Node`
        """
        nodes = self.nodes(path=name)
        return next(node for node in nodes)

    def edges(self, **kwargs):
        """Get the known catalog edges, formed between two resources.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A generating yielding Edges.
        :rtype: :class:`pypuppetdb.types.Edge`
        """
        edges = self._query('edges', **kwargs)

        for edge in edges:
            identifier_source = edge['source_type'] + '[' + edge['source_title'] + ']'
            identifier_target = edge['target_type'] + '[' + edge['target_title'] + ']'
            yield Edge(source=self.resources[identifier_source],
                       target=self.resources[identifier_target],
                       relationship=edge['relationship'],
                       node=edge['certname'])

    def environments(self, **kwargs):
        """Get all known environments from Puppetdb.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A list of dictionaries containing the results.
        :rtype: :obj:`list` of :obj:`dict`
        """
        return self._query('environments', **kwargs)

    def facts(self, name=None, value=None, **kwargs):
        """Query for facts limited by either name, value and/or query.

        :param name: (Optional) Only return facts that match this name.
        :type name: :obj:`string`
        :param value: (Optional) Only return facts of `name` that\
            match this value. Use of this parameter requires the `name`\
            parameter be set.
        :type value: :obj:`string`
        :param \*\*kwargs: The rest of the keyword arguments are passed
            to the _query function

        :returns: A generator yielding Facts.
        :rtype: :class:`pypuppetdb.types.Fact`
        """
        if 'pql' in kwargs.keys() and kwargs['pql'] and (name or value):
            log.error("Don't use PQL together with name or value!")
            raise APIError

        if name is not None and value is not None:
            path = '{0}/{1}'.format(name, value)
        elif name is not None and value is None:
            path = name
        else:
            path = None

        facts = self._query('facts', path=path, **kwargs)
        for fact in facts:
            yield Fact(
                node=fact['certname'],
                name=fact['name'],
                value=fact['value'],
                environment=fact['environment']
            )

    def factsets(self, **kwargs):
        """Returns a set of all facts or for a single certname.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A list of dictionaries containg the results.
        :rtype: :obj:`list` of :obj:`dict`
        """
        return self._query('factsets', **kwargs)

    def fact_contents(self, **kwargs):
        """To complement fact_paths(), this endpoint provides the capability
        to descend into structured facts and retreive the values associated
        with fact paths.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A list of dictionaries containg the results.
        :rtype: :obj:`list` of :obj:`dict`
        """
        return self._query('fact-contents', **kwargs)

    def fact_paths(self, **kwargs):
        """Fact Paths are intended to be a counter-part of the fact-names
        endpoint. It provides increased granularity around structured
        facts and may be used for building GUI autocompletions or other
        applications that require a basic top-level view of fact paths.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A list of dictionaries containg the results.
        :rtype: :obj:`list` of :obj:`dict`
        """
        return self._query('fact-paths', **kwargs)

    def resources(self, type_=None, title=None, **kwargs):
        """Query for resources limited by either type and/or title or query.
        This will yield a Resources object for every returned resource.

        :param type_: (Optional) The resource type. This can be any resource
            type referenced in\
            'https://docs.puppetlabs.com/references/latest/type.html'
        :type type_: :obj:`string`
        :param title: (Optional) The name of the resource as declared as the
            'namevar' in the Puppet Manifests. This parameter requires the\
            `type_` parameter be set.
        :type title: :obj:`string`
        :param \*\*kwargs: The rest of the keyword arguments are passed
            to the _query function

        :returns: A generator yielding Resources
        :rtype: :class:`pypuppetdb.types.Resource`
        """
        if 'pql' in kwargs.keys() and kwargs['pql'] and (type_ or title):
            log.error("Don't use PQL together with type_ or title!")
            raise APIError

        path = None

        if type_ is not None:
            type_ = self._normalize_resource_type(type_)

            if title is not None:
                path = '{0}/{1}'.format(type_, title)
            elif title is None:
                path = type_

        resources = self._query('resources', path=path, **kwargs)
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

    def catalog(self, node):
        """Get the available catalog for a given node.

        :param node: (Required) The name of the PuppetDB node.
        :type: :obj:`string`

        :returns: An instance of Catalog
        :rtype: :class:`pypuppetdb.types.Catalog`
        """
        catalogs = self.catalogs(path=node)
        return next(catalog for catalog in catalogs)

    def catalogs(self, **kwargs):
        """Get the catalog information from the infrastructure based on path
        and/or query results. It is strongly recommended to include query
        and/or paging parameters for this endpoint to prevent large result
        sets or PuppetDB performance bottlenecks.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A generator yielding Catalogs
        :rtype: :class:`pypuppetdb.types.Catalog`
        """

        catalogs = self._query('catalogs', **kwargs)

        if type(catalogs) == dict:
            catalogs = [catalogs, ]

        for catalog in catalogs:
            yield Catalog(node=catalog['certname'],
                          edges=catalog['edges']['data'],
                          resources=catalog['resources']['data'],
                          version=catalog['version'],
                          transaction_uuid=catalog['transaction_uuid'],
                          environment=catalog['environment'],
                          code_id=catalog.get('code_id'),
                          catalog_uuid=catalog.get('catalog_uuid'))

    def events(self, **kwargs):
        """A report is made up of events which can be queried either
        individually or based on their associated report hash. It is strongly
        recommended to include query and/or paging parameters for this
        endpoint to prevent large result sets or PuppetDB performance
        bottlenecks.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function

        :returns: A generator yielding Events
        :rtype: :class:`pypuppetdb.types.Event`
        """
        events = self._query('events', **kwargs)
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

    def event_counts(self, summarize_by, **kwargs):
        """Get event counts from puppetdb.

        :param summarize_by: (Required) The object type to be counted on.
                             Valid values are 'containing_class', 'resource'
                             and 'certname'.
        :type summarize_by: :obj:`string`
        :param count_by: (Optional) The object type that is counted when
                         building the counts of 'successes', 'failures',
                         'noops' and 'skips'. Support values are 'certname'
                         and 'resource' (default)
        :type count_by: :obj:`string`
        :param count_filter: (Optional) A JSON query that is applied to the
                             event-counts output but before the results are
                             aggregated. Supported operators are `=`, `>`,
                             `<`, `>=`, and `<=`. Supported fields are
                             `failures`, `successes`, `noops`, and `skips`.
        :type count_filter: :obj:`string`
        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A list of dictionaries containing the results.
        :rtype: :obj:`list`
        """
        return self._query('event-counts',
                           summarize_by=summarize_by,
                           **kwargs)

    def aggregate_event_counts(self, summarize_by, query=None,
                               count_by=None, count_filter=None):
        """Get event counts from puppetdb aggregated into a single map.

        :param summarize_by: (Required) The object type to be counted on.
                             Valid values are 'containing_class', 'resource'
                             and 'certname' or any comma-separated value
                             thereof.
        :type summarize_by: :obj:`string`
        :param query: (Optional) The PuppetDB query to filter the results.
                      This query is passed to the `events` endpoint.
        :type query: :obj:`string`
        :param count_by: (Optional) The object type that is counted when
                         building the counts of 'successes', 'failures',
                         'noops' and 'skips'. Support values are 'certname'
                         and 'resource' (default)
        :type count_by: :obj:`string`
        :param count_filter: (Optional) A JSON query that is applied to the
                             event-counts output but before the results are
                             aggregated. Supported operators are `=`, `>`,
                             `<`, `>=`, and `<=`. Supported fields are
                             `failures`, `successes`, `noops`, and `skips`.
        :type count_filter: :obj:`string`

        :returns: A dictionary of name/value results.
        :rtype: :obj:`dict`
        """
        return self._query('aggregate-event-counts',
                           query=query, summarize_by=summarize_by,
                           count_by=count_by, count_filter=count_filter)

    def fact_names(self):
        """Get a list of all known facts."""
        return self._query('fact-names')

    def reports(self, **kwargs):
        """Get reports for our infrastructure. It is strongly recommended
        to include query and/or paging parameters for this endpoint to
        prevent large result sets and potential PuppetDB performance
        bottlenecks.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function

        :returns: A generating yielding Reports
        :rtype: :class:`pypuppetdb.types.Report`
        """
        reports = self._query('reports', **kwargs)
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
                noop=report.get('noop'),
                noop_pending=report.get('noop_pending'),
                metrics=report['metrics']['data'],
                logs=report['logs']['data'],
                code_id=report.get('code_id'),
                catalog_uuid=report.get('catalog_uuid'),
                cached_catalog_status=report.get('cached_catalog_status')
            )

    def inventory(self, **kwargs):
        """Get Node and Fact information with an alternative query syntax
        for structured facts instead of using the facts, fact-contents and
        factsets endpoints for many fact-related queries.

        :param \*\*kwargs: The rest of the keyword arguments are passed
                           to the _query function.

        :returns: A generator yielding Inventory
        :rtype: :class:`pypuppetdb.types.Inventory`
        """
        inventory = self._query('inventory', **kwargs)
        for inv in inventory:
            yield Inventory(
                node=inv['certname'],
                time=inv['timestamp'],
                environment=inv['environment'],
                facts=inv['facts'],
                trusted=inv['trusted']
            )

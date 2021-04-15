from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from datetime import datetime

import pypuppetdb
from pypuppetdb.QueryBuilder import (EqualsOperator)
from pypuppetdb.api.base import BaseAPI
from pypuppetdb.types import (Catalog, Edge, Event, Fact, Inventory,
                              Node, Report, Resource)

log = logging.getLogger(__name__)


class QueryAPI(BaseAPI):
    """This class provides methods that interact with the `pdb/query/v4/*`
    PuppetDB API endpoints.
    """

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

        latest_events = None
        if with_status and with_event_numbers:
            latest_events = self._query(
                'event-counts',
                query=EqualsOperator("latest_report?", True),
                summarize_by='certname',
            )

        for node in nodes:
            yield Node.create_from_dict(self, node, with_status, with_event_numbers, latest_events,
                                        now, unreported)

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
            yield Edge.create_from_dict(edge)

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
        if name is not None and value is not None:
            path = '{0}/{1}'.format(name, value)
        elif name is not None and value is None:
            path = name
        else:
            path = None

        facts = self._query('facts', path=path, **kwargs)
        for fact in facts:
            yield Fact.create_from_dict(fact)

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

        path = None

        if type_ is not None:
            type_ = self._normalize_resource_type(type_)

            if title is not None:
                path = '{0}/{1}'.format(type_, title)
            elif title is None:
                path = type_

        resources = self._query('resources', path=path, **kwargs)
        for resource in resources:
            yield Resource.create_from_dict(resource)

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
            yield Catalog.create_from_dict(catalog)

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
            yield Event.create_from_dict(event)

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
            yield Report.create_from_dict(self, report)

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
            yield Inventory.create_from_dict(inv)

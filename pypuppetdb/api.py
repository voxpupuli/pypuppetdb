from __future__ import absolute_import
from __future__ import unicode_literals

import hashlib
import json
import logging
from datetime import datetime, timedelta
from urllib.parse import quote

import requests

from pypuppetdb.QueryBuilder import (EqualsOperator)
from pypuppetdb.errors import (APIError, DoesNotComputeError, EmptyResponseError)
from pypuppetdb.types import (Catalog, Edge, Event, Fact, Inventory,
                              Node, Report, Resource)
from pypuppetdb.utils import json_to_datetime

log = logging.getLogger(__name__)

ENDPOINTS = {
    'facts': 'pdb/query/v4/facts',
    'fact-names': 'pdb/query/v4/fact-names',
    'nodes': 'pdb/query/v4/nodes',
    'resources': 'pdb/query/v4/resources',
    'catalogs': 'pdb/query/v4/catalogs',
    'mbean': 'metrics/v1/mbeans',
    # metrics v2 endpoint is now the jolokia library and all of its operations
    # https://jolokia.org/reference/html/protocol.html#jolokia-operations
    'metrics': 'metrics/v2/read',
    'metrics-base': 'metrics/v2',
    'metrics-exec': 'metrics/v2/exec',
    'metrics-list': 'metrics/v2/list',
    'metrics-search': 'metrics/v2/search',
    'metrics-write': 'metrics/v2/write',
    'metrics-version': 'metrics/v2/version',
    'reports': 'pdb/query/v4/reports',
    'events': 'pdb/query/v4/events',
    'event-counts': 'pdb/query/v4/event-counts',
    'aggregate-event-counts': 'pdb/query/v4/aggregate-event-counts',
    'server-time': 'pdb/meta/v1/server-time',
    'version': 'pdb/meta/v1/version',
    'environments': 'pdb/query/v4/environments',
    'factsets': 'pdb/query/v4/factsets',
    'fact-paths': 'pdb/query/v4/fact-paths',
    'fact-contents': 'pdb/query/v4/fact-contents',
    'edges': 'pdb/query/v4/edges',
    'pql': 'pdb/query/v4',
    'inventory': 'pdb/query/v4/inventory',
    'status': 'status/v1/services/puppetdb-status',
    'cmd': 'pdb/cmd/v1'
}

PARAMETERS = {
    'order_by': 'order_by',
    'include_total': 'include_total',
    'count_by': 'count_by',
    'counts_filter': 'counts_filter',
    'summarize_by': 'summarize_by',
    'server_time': 'server_time',
}

COMMAND_VERSION = {
    "deactivate node": 3,
    "replace catalog": 9,
    "replace facts": 5,
    "store report": 8
}

ERROR_STRINGS = {
    'timeout': 'Connection to PuppetDB timed out on',
    'refused': 'Could not reach PuppetDB on',
}


class BaseAPI(object):
    """This is a Base or Abstract class and is not meant to be instantiated
    or used directly.

    The BaseAPI object defines a set of methods that can be
    reused across different versions of the PuppetDB API. If querying for a
    certain resource is done in an identical fashion across different versions
    it will be implemented here and should be overridden in their respective
    versions if they deviate.

    If :attr:`ssl` is set to `True` but either :attr:`ssl_key` or\
            :attr:`ssl_cert` are `None` this will raise an error.

    :param api_version: (Default 4) Version of the API we're initialising.
    :type api_version: :obj:`int`

    :param host: (optional) Hostname or IP of PuppetDB.
    :type host: :obj:`string`

    :param port: (optional) Port on which to talk to PuppetDB.
    :type port: :obj:`int`

    :param ssl_verify: (optional) Verify PuppetDB server certificate.
    :type ssl_verify: :obj:`bool` or :obj:`string`

    :param ssl_key: (optional) Path to our client secret key.
    :type ssl_key: :obj:`None` or :obj:`string` representing a filesystem\
            path.

    :param ssl_cert: (optional) Path to our client certificate.
    :type ssl_cert: :obj:`None` or :obj:`string` representing a filesystem\
            path.

    :param timeout: (optional) Number of seconds to wait for a response.
    :type timeout: :obj:`int`

    :param protocol: (optional) Explicitly specify the protocol to be used
            (especially handy when using HTTPS with ssl_verify=False and
            without certs)
    :type protocol: :obj:`None` or :obj:`string`

    :param url_path: (optional) The URL path where PuppetDB is served
            (if not at the root / path)
    :type url_path: :obj:`None` or :obj:`string`

    :param username: (optional) The username to use for HTTP basic
            authentication
    :type username: :obj:`None` or :obj:`string`

    :param password: (optional) The password to use for HTTP basic
            authentication
    :type password: :obj:`None` or :obj:`string`

    :param token: (optional) The X-auth token to use for X-Authentication
    :type token: :obj:`None` or :obj:`string`

    :param metric_api_version: (Default 'v2') Version of the metric API we're initialising.
    :type metric_api_version: :obj:`None` or :obj:`string`

    :raises: :class:`~pypuppetdb.errors.ImproperlyConfiguredError`
    """

    def __init__(self, host='localhost', port=8080, ssl_verify=True,
                 ssl_key=None, ssl_cert=None, timeout=10, protocol=None,
                 url_path=None, username=None, password=None, token=None,
                 metric_api_version=None):
        """Initialises our BaseAPI object passing the parameters needed in
        order to be able to create the connection strings, set up SSL and
        timeouts and so forth."""

        self.api_version = 'v4'
        if metric_api_version is not None and metric_api_version not in ['v1', 'v2']:
            raise ValueError("metric_api_version specified must be None, 'v1' or 'v2',"
                             " was given: '{}'".format(metric_api_version))
        self.metric_api_version = metric_api_version if metric_api_version else 'v2'
        self.host = host
        self.port = port
        self.ssl_verify = ssl_verify
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.timeout = timeout
        self.token = token

        # Standardise the URL path to a format similar to /puppetdb
        if url_path:
            if not url_path.startswith('/'):
                url_path = '/' + url_path
            if url_path.endswith('/'):
                url_path = url_path[:-1]
        else:
            url_path = ''

        self.url_path = url_path
        if username and password:
            self.username = username
            self.password = password
        else:
            self.username = None
            self.password = None

        self._session = requests.Session()
        self._session.headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'accept-charset': 'utf-8'
        }

        if self.token:
            self._session.headers['X-Authentication'] = self.token

        if protocol is not None:
            protocol = protocol.lower()
            if protocol not in ['http', 'https']:
                raise ValueError('Protocol specified must be http or https')
            self.protocol = protocol
        elif self.ssl_key is not None and self.ssl_cert is not None:
            self.protocol = 'https'
        elif self.token is not None:
            self.protocol = 'https'
        else:
            self.protocol = 'http'

    @property
    def version(self):
        """The version of the API we're querying against.

        :returns: Current API version.
        :rtype: :obj:`string`"""
        return self.api_version

    @property
    def base_url(self):
        """A base_url that will be used to construct the final
        URL we're going to query against.

        :returns: A URL of the form: ``proto://host:port``.
        :rtype: :obj:`string`
        """
        return '{proto}://{host}:{port}{url_path}'.format(
            proto=self.protocol,
            host=self.host,
            port=self.port,
            url_path=self.url_path,
        )

    @property
    def total(self):
        """The total-count of the last request to PuppetDB
        if enabled as parameter in _query method

        :returns Number of total results
        :rtype :obj:`int`
        """
        if self.last_total is not None:
            return int(self.last_total)

    @staticmethod
    def _normalize_resource_type(type_):
        """Normalizes the type passed to the api by capitalizing each part
        of the type. For example:

        sysctl::value -> Sysctl::Value
        user -> User

        """
        return '::'.join([s.capitalize() for s in type_.split('::')])

    def _url(self, endpoint, path=None):
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

        try:
            endpoint = ENDPOINTS[endpoint]
        except KeyError:
            # If we reach this we're trying to query an endpoint that doesn't
            # exist. This shouldn't happen unless someone made a booboo.
            raise APIError

        url = '{base_url}/{endpoint}'.format(
            base_url=self.base_url,
            endpoint=endpoint,
        )

        if path is not None:
            url = '{0}/{1}'.format(url, quote(path))

        return url

    def _query(self, endpoint, path=None, query=None,
               order_by=None, limit=None, offset=None, include_total=False,
               summarize_by=None, count_by=None, count_filter=None,
               payload=None, request_method='GET'):
        """This method actually querries PuppetDB. Provided an endpoint and an
        optional path and/or query it will fire a request at PuppetDB. If
        PuppetDB can be reached and answers within the timeout we'll decode
        the response and give it back or raise for the HTTP Status Code
        PuppetDB gave back.

        :param endpoint: The PuppetDB API endpoint we want to query.
        :type endpoint: :obj:`string`
        :param path: An additional path if we don't wish to query the\
                bare endpoint.
        :type path: :obj:`string`
        :param query: (optional) A query to further narrow down the resultset.
        :type query: :obj:`string`
        :param order_by: (optional) Set the order parameters for the resultset.
        :type order_by: :obj:`string`
        :param limit: (optional) Tell PuppetDB to limit it's response to this\
                number of objects.
        :type limit: :obj:`int`
        :param offset: (optional) Tell PuppetDB to start it's response from\
                the given offset. This is useful for implementing pagination\
                but is not supported just yet.
        :type offset: :obj:`string`
        :param include_total: (optional) Include the total number of results
        :type order_by: :obj:`bool`
        :param summarize_by: (optional) Specify what type of object you'd like\
                to see counts at the event-counts and aggregate-event-counts \
                endpoints
        :type summarize_by: :obj:`string`
        :param count_by: (optional) Specify what type of object is counted
        :type count_by: :obj:`string`
        :param count_filter: (optional) Specify a filter for the results
        :type count_filter: :obj:`string`
        :param payload: (optional) Arbitrary payload to send as part of the request.
        :type payload: :obj:`dict`

        :raises: :class:`~pypuppetdb.errors.EmptyResponseError`

        :returns: The decoded response from PuppetDB
        :rtype: :obj:`dict` or :obj:`list`
        """
        log.debug('_query called with endpoint: {0}, path: {1}, query: {2}, '
                  'limit: {3}, offset: {4}, summarize_by {5}, count_by {6}, '
                  'count_filter: {7}, payload: {8}'
                  .format(endpoint, path, query, limit,
                          offset, summarize_by, count_by,
                          count_filter, payload))

        url = self._url(endpoint, path=path)
        if payload is None:
            payload = {}
        if query is not None:
            payload['query'] = query
        if order_by is not None:
            payload[PARAMETERS['order_by']] = order_by
        if limit is not None:
            payload['limit'] = limit
        if include_total is True:
            payload[PARAMETERS['include_total']] = \
                json.dumps(include_total)
        if offset is not None:
            payload['offset'] = offset
        if summarize_by is not None:
            payload[PARAMETERS['summarize_by']] = summarize_by
        if count_by is not None:
            payload[PARAMETERS['count_by']] = count_by
        if count_filter is not None:
            payload[PARAMETERS['counts_filter']] = count_filter

        if not payload:
            payload = None

        if not self.token:
            auth = (self.username, self.password)
        else:
            auth = None

        try:
            if request_method.upper() == 'GET':
                r = self._session.get(url, params=payload,
                                      verify=self.ssl_verify,
                                      cert=(self.ssl_cert, self.ssl_key),
                                      timeout=self.timeout,
                                      auth=auth)
            elif request_method.upper() == 'POST':
                r = self._session.post(url,
                                       data=json.dumps(payload, default=str),
                                       verify=self.ssl_verify,
                                       cert=(self.ssl_cert, self.ssl_key),
                                       timeout=self.timeout,
                                       auth=auth)
            else:
                log.error("Only GET or POST supported, {0} unsupported".format(
                    request_method))
                raise APIError
            r.raise_for_status()

            # get total number of results if requested with include-total
            # just a quick hack - needs improvement
            if 'X-Records' in r.headers:
                self.last_total = r.headers['X-Records']
            else:
                self.last_total = None

            json_body = r.json()
            if json_body is not None:
                return json_body
            else:
                del json_body
                raise EmptyResponseError

        except requests.exceptions.Timeout:
            log.error("{0} {1}:{2} over {3}.".format(ERROR_STRINGS['timeout'],
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise
        except requests.exceptions.ConnectionError:
            log.error("{0} {1}:{2} over {3}.".format(ERROR_STRINGS['refused'],
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise
        except requests.exceptions.HTTPError as err:
            log.error("{0} {1}:{2} over {3}.".format(err.response.text,
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise

    def _cmd(self, command, payload):
        """This method posts commands to PuppetDB. Provided a command and payload
        it will fire a request at PuppetDB. If PuppetDB can be reached and
        answers within the timeout we'll decode the response and give it back
        or raise for the HTTP Status Code yesPuppetDB gave back.

        :param command: The PuppetDB Command we want to execute.
        :type command: :obj:`string`
        :param command: The payload, in wire format, specific to the command.
        :type path: :obj:`dict`

        :raises: :class:`~pypuppetdb.errors.EmptyResponseError`

        :returns: The decoded response from PuppetDB
        :rtype: :obj:`dict` or :obj:`list`
        """
        log.debug('_cmd called with command: {0}, data: {1}'.format(
            command, payload))

        url = self._url('cmd')

        if command not in COMMAND_VERSION:
            log.error("Only {0} supported, {1} unsupported".format(
                list(COMMAND_VERSION.keys()), command))
            raise APIError

        params = {
            "command": command,
            "version": COMMAND_VERSION[command],
            "certname": payload['certname'],
            "checksum": hashlib.sha1(str(payload)  # nosec
                                     .encode('utf-8')).hexdigest()
        }

        if not self.token:
            auth = (self.username, self.password)
        else:
            auth = None

        try:
            r = self._session.post(url,
                                   params=params,
                                   data=json.dumps(payload, default=str),
                                   verify=self.ssl_verify,
                                   cert=(self.ssl_cert, self.ssl_key),
                                   timeout=self.timeout,
                                   auth=auth)

            r.raise_for_status()

            json_body = r.json()
            if json_body is not None:
                return json_body
            else:
                del json_body
                raise EmptyResponseError

        except requests.exceptions.Timeout:
            log.error("{0} {1}:{2} over {3}.".format(ERROR_STRINGS['timeout'],
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise
        except requests.exceptions.ConnectionError:
            log.error("{0} {1}:{2} over {3}.".format(ERROR_STRINGS['refused'],
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise
        except requests.exceptions.HTTPError as err:
            log.error("{0} {1}:{2} over {3}.".format(err.response.text,
                                                     self.host, self.port,
                                                     self.protocol.upper()))
            raise

    # Method stubs

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
        return next(x for x in catalogs)

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

    def server_time(self):
        """Get the current time of the clock on the PuppetDB server.
        :returns: An ISO-8091 formatting timestamp.
        :rtype: :obj:`string`
        """
        return self._query('server-time')[self.parameters['server_time']]

    def current_version(self):
        """Get version information about the running PuppetDB server.

        :returns: A string representation of the PuppetDB version.
        :rtype: :obj:`string`
        """
        return self._query('version')['version']

    def fact_names(self):
        """Get a list of all known facts."""
        return self._query('fact-names')

    def metric(self, metric=None, version=None):
        """Query for a specific metrc.

        :param metric: The name of the metric we want.
        :type metric: :obj:`string`
        :param version: The version of the metric API to query. Valid values: 'v1', 'v2'
                        If not specified, then the value of self.metric_api_version
                        will be used.
        :type version: :obj:`string`

        :returns: The return of :meth:`~pypuppetdb.api.BaseAPI._query`.
        """
        version = version if version else self.metric_api_version
        if version is None or version == 'v2':
            if metric is None:
                res = self._query('metrics-list')
            else:
                res = self._query('metrics', path=self.escape_metric_name(metric))

            if 'error' in res:
                raise DoesNotComputeError(res['error'])
            return res['value']
        elif version == 'v1':
            return self._query('mbean', path=metric)
        else:
            raise ValueError("Version specified must be 'v1' or 'v2', was given: '{}'"
                             .format(version))

    def escape_metric_name(self, metric):
        """Escapes metric names so they can be used in GET requests as part of the URL.
        The new (as of v2) metrics API is backed by the Jolokia library.
        The escpaing rules for Jolokia GET requests can be found here:
        https://jolokia.org/reference/html/protocol.html#escape-rules

        :param metric: The name of the metric we want to escape.
        :type metric: :obj:`string`

        :returns: The escaped version of the metric name, safe for use in metric GET queries.
        """
        metric = metric.replace('!', r'!!')
        metric = metric.replace('/', r'!/')
        metric = metric.replace('"', r'!"')
        return metric

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

    def status(self):
        """Get PuppetDB server status.

        :returns: A dict with the PuppetDB status information
        :rtype: :obj:`dict`
        """
        return self._query('status')

    def command(self, command, payload):
        return self._cmd(command, payload)

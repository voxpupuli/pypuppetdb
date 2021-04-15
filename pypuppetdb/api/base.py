from __future__ import absolute_import
from __future__ import unicode_literals

import json
import logging
from urllib.parse import quote

import requests

from pypuppetdb.errors import (APIError, EmptyResponseError)

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

        self.session = requests.Session()

        if username and password:
            self.session.auth = (username, password)

        self.session.headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'accept-charset': 'utf-8'
        }

        if self.token:
            self.session.headers['X-Authentication'] = self.token

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

    def disconnect(self):
        """Close all connections that this class opened up."""
        # If we don't explicitly close connections, we might cause other
        # functions or libraries to hang on the open connections. This happens
        # for example with using paramiko to tunnel PuppetDB connections
        # through ssh.
        self.session.close()

    def __enter__(self):
        """Set up environment for 'with' statement."""
        # Once this class has been instantiated, there's nothing more required
        return self

    def __exit__(self, type, value, trace):
        """Tear down connections."""
        self.disconnect()

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

    def _query(self, endpoint=None, path=None, query=None,
               order_by=None, limit=None, offset=None, include_total=False,
               summarize_by=None, count_by=None, count_filter=None,
               payload=None, request_method='GET'):
        """This method prepares a non-PQL query to PuppetDB. Actual making
        the HTTP request is done by _make_request().

        :param endpoint: (optional) The PuppetDB API endpoint we want to query.
                        Unnecessary when using PQL.
        :type endpoint: :obj:`string`
        :param path: An additional path if we don't wish to query the\
                bare endpoint.
        :type path: :obj:`string`
        :param query: (optional) An AST query to further narrow down the resultset.
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

        log.debug(f"_query called with ",
                  # comma-separated list of method arguments with their values
                  ", ".join([f"{arg}: {locals().get(arg, 'None')}"
                             for arg in locals().keys() if arg != 'self'])
                  )

        if not endpoint:
            log.error("Endpoint is required!")
            raise APIError

        if payload is None:
            payload = {}

        url = self._url(endpoint, path=path)
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

        return self._make_request(url, request_method, payload)

    def _make_request(self, url, request_method, payload):
        """
        Makes a GET or POST HTTP request to PuppetDB. If PuppetDB can be
        reached and answers within the timeout we'll decode the response
        and give it back or raise for the HTTP Status Code PuppetDB gave back.

        :param url: Complete URL to call
        :param request_method: GET or POST
        :param payload: data to send as parameters (GET) or in the body (POST)
        :return: response body as JSON
                 or raises an EmptyResponseError exception if it's empty
        """

        if request_method.upper() not in ['GET', 'POST']:
            log.error(f"Only GET or POST supported, {request_method} unsupported")
            raise APIError

        try:
            if request_method.upper() == 'GET':
                r = self.session.get(url, params=payload,
                                     verify=self.ssl_verify,
                                     cert=(self.ssl_cert, self.ssl_key),
                                     timeout=self.timeout,
                                     )
            else:
                r = self.session.post(url,
                                      data=json.dumps(payload, default=str),
                                      verify=self.ssl_verify,
                                      cert=(self.ssl_cert, self.ssl_key),
                                      timeout=self.timeout,
                                      )

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

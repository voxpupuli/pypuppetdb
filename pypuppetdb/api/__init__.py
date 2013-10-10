from __future__ import unicode_literals
from __future__ import absolute_import

import logging

import requests

from pypuppetdb.errors import (
    ImproperlyConfiguredError,
    EmptyResponseError,
    UnsupportedVersionError,
    APIError,
    )

log = logging.getLogger(__name__)

API_VERSIONS = {
    2: 'v2',
    3: 'v3',
}

ENDPOINTS = {
    2: {
        'facts': 'facts',
        'fact-names': 'fact-names',
        'nodes': 'nodes',
        'resources': 'resources',
        'metrics': 'metrics',
        'mbean': 'metrics/mbean',
    },
    3: {
        'facts': 'facts',
        'fact-names': 'fact-names',
        'nodes': 'nodes',
        'resources': 'resources',
        'metrics': 'metrics',
        'mbean': 'metrics/mbean',
        'reports': 'reports',
        'events': 'events',
    },
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

    When at initialisation :obj:`api_version` isn't found in\
            :const:`API_VERSIONS` this will raise an error.

    :param api_version: Version of the API we're initialising.
    :type api_version: :obj:`int`
    :param host: (optional) Hostname or IP of PuppetDB.
    :type host: :obj:`string`
    :param port: (optional) Port on which to talk to PuppetDB.
    :type port: :obj:`int`
    :param ssl: (optional) Talk with PuppetDB over SSL.
    :type ssl: :obj:`bool`
    :param ssl_key: (optional) Path to our client secret key.
    :type ssl_key: :obj:`None` or :obj:`string` representing a filesystem\
            path.
    :param ssl_cert: (optional) Path to our client certificate.
    :type ssl_cert: :obj:`None` or :obj:`string` representing a filesystem\
            path.
    :param timeout: (optional) Number of seconds to wait for a response.
    :type timeout: :obj:`int`

    :raises: :class:`~pypuppetdb.errors.ImproperlyConfiguredError`
    :raises: :class:`~pypuppetdb.errors.UnsupportedVersionError`
    """
    def __init__(self, api_version, host='localhost', port=8080,
                 ssl=False, ssl_key=None, ssl_cert=None, timeout=10):
        """Initialises our BaseAPI object passing the parameters needed in
        order to be able to create the connection strings, set up SSL and
        timeouts and so forth."""

        if api_version in API_VERSIONS:
            self.api_version = API_VERSIONS[api_version]
        else:
            raise UnsupportedVersionError

        self.host = host
        self.port = port
        self.ssl = ssl
        self.ssl_key = ssl_key
        self.ssl_cert = ssl_cert
        self.timeout = timeout
        self.endpoints = ENDPOINTS[api_version]

        if not self.ssl:
            self.protocol = 'http'
        elif (self.ssl and self.ssl_key is not None and
              self.ssl_cert is not None):
            self.protocol = 'https'
        else:
            raise ImproperlyConfiguredError

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
        return '{proto}://{host}:{port}'.format(
            proto=self.protocol,
            host=self.host,
            port=self.port,
            )

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

        if endpoint in self.endpoints:
            api_prefix = self.api_version
            endpoint = self.endpoints[endpoint]
        else:
            # If we reach this we're trying to query an endpoint that doesn't
            # exist. This shouldn't happen unless someone made a booboo.
            raise APIError

        url = '{base_url}/{api_prefix}/{endpoint}'.format(
            base_url=self.base_url,
            api_prefix=api_prefix,
            endpoint=endpoint,
            )

        if path is not None:
            url = '{0}/{1}'.format(url, path)

        return url

    def _query(self, endpoint, path=None, query=None, limit=None, offset=None):
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
        :param limit: (optional) Tell PuppetDB to limit it's response to this\
                number of objects.
        :type limit: :obj:`int`
        :param offset: (optional) Tell PuppetDB to start it's response from\
                the given offset. This is useful for implementing pagination\
                but is not supported just yet.
        :type offset: :obj:`string`

        :raises: :class:`~pypuppetdb.errors.EmptyResponseError`

        :returns: The decoded response from PuppetDB
        :rtype: :obj:`dict` or :obj:`list`
        """
        log.debug('_query called with endpoint: {0}, path: {1}, query: {2}, '
                  'limit: {3}, offset: {4}'.format(endpoint, path, query,
                                                   limit, offset))

        url = self._url(endpoint, path=path)
        headers = {
            'content-type': 'application/json',
            'accept': 'application/json',
            'accept-charset': 'utf-8'
            }

        payload = None
        if query is not None:
            payload = {'query': query}

        try:
            r = requests.get(url, params=payload, headers=headers,
                             verify=self.ssl, cert=(self.ssl_cert,
                                                    self.ssl_key),
                             timeout=self.timeout)

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

    # Method stubs

    def nodes(self):
        raise NotImplementedError

    def node(self):
        raise NotImplementedError

    def facts(self):
        raise NotImplementedError

    def resources(self):
        raise NotImplementedError

    def metric(self, metric):
        """Query for a specific metrc.

        :param metric: The name of the metric we want.
        :type metric: :obj:`string`

        :returns: The return of :meth:`~pypuppetdb.api.BaseAPI._query`.
        """
        endpoint = 'mbean'
        path = metric
        return self._query(endpoint, path=path)

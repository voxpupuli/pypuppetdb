from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from pypuppetdb.api.base import BaseAPI
from pypuppetdb.errors import (DoesNotComputeError)

log = logging.getLogger(__name__)


class MetricsAPI(BaseAPI):
    """This class provides methods that interact with the `metrics/*`
    PuppetDB API endpoints.
    """

    def metric(self, metric=None, version=None):
        """Query for a specific metric.

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
                res = self._query('metrics', path=self._escape_metric_name(metric))

            if 'error' in res:
                raise DoesNotComputeError(res['error'])
            return res['value']
        elif version == 'v1':
            return self._query('mbean', path=metric)
        else:
            raise ValueError("Version specified must be 'v1' or 'v2', was given: '{}'"
                             .format(version))

    @staticmethod
    def _escape_metric_name(metric):
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

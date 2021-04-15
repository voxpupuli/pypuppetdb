from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from pypuppetdb.api.base import BaseAPI

log = logging.getLogger(__name__)


class MetadataAPI(BaseAPI):
    """This class provides methods that interact with the `pdb/meta/*`
    PuppetDB API endpoints.
    """

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

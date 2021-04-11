from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from pypuppetdb.api.base import BaseAPI

log = logging.getLogger(__name__)


class StatusAPI(BaseAPI):
    """This class provides methods that interact with the `status/*`
    PuppetDB API endpoints.
    """

    def status(self):
        """Get PuppetDB server status.

        :returns: A dict with the PuppetDB status information
        :rtype: :obj:`dict`
        """
        return self._query('status')

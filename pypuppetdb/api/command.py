import hashlib
import json
import logging

import requests

from pypuppetdb.api.base import BaseAPI, COMMAND_VERSION, ERROR_STRINGS
from pypuppetdb.errors import APIError, EmptyResponseError

log = logging.getLogger(__name__)


class CommandAPI(BaseAPI):
    """This class provides methods that interact with the `pdb/cmd/*`
    PuppetDB API endpoints.
    """

    def command(self, command, payload):
        return self._cmd(command, payload)

    def _cmd(self, command, payload):
        """This method posts commands to PuppetDB. Provided a command and payload
        it will fire a request at PuppetDB. If PuppetDB can be reached and
        answers within the timeout we'll decode the response and give it back
        or raise for the HTTP Status Code PuppetDB gave back.

        :param command: The PuppetDB Command we want to execute.
        :type command: :obj:`string`

        :param command: The payload, in wire format, specific to the command.
        :type command: :obj:`dict`

        :raises: :class:`~pypuppetdb.errors.EmptyResponseError`

        :returns: The decoded response from PuppetDB
        :rtype: :obj:`dict` or :obj:`list`
        """
        log.debug("_cmd called with command: {}, data: {}".format(command, payload))

        url = self._url("cmd")

        if command not in COMMAND_VERSION:
            log.error(
                "Only {} supported, {} unsupported".format(
                    list(COMMAND_VERSION.keys()), command
                )
            )
            raise APIError

        params = {
            "command": command,
            "version": COMMAND_VERSION[command],
            "certname": payload["certname"],
            "checksum": hashlib.sha1(str(payload).encode("utf-8")).hexdigest(),  # nosec
        }

        try:
            r = self.session.post(
                url,
                params=params,
                data=json.dumps(payload, default=str),
                verify=self.ssl_verify,
                cert=(self.ssl_cert, self.ssl_key),
                timeout=self.timeout,
            )

            r.raise_for_status()

            json_body = r.json()
            if json_body is not None:
                return json_body
            else:
                del json_body
                raise EmptyResponseError

        except requests.exceptions.Timeout:
            log.error(
                "{} {}:{} over {}.".format(
                    ERROR_STRINGS["timeout"],
                    self.host,
                    self.port,
                    self.protocol.upper(),
                )
            )
            raise
        except requests.exceptions.ConnectionError:
            log.error(
                "{} {}:{} over {}.".format(
                    ERROR_STRINGS["refused"],
                    self.host,
                    self.port,
                    self.protocol.upper(),
                )
            )
            raise
        except requests.exceptions.HTTPError as err:
            log.error(
                "{} {}:{} over {}.".format(
                    err.response.text, self.host, self.port, self.protocol.upper()
                )
            )
            raise

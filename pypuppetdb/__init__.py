from __future__ import unicode_literals
from __future__ import absolute_import

"""
pypuppetdb PuppetDB API library
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

pypuppetdb is a library to work with PuppetDB's REST API. It provides a way
to query PuppetDB and a set of additional methods and objects to make working
with PuppetDB's API and the responses easier:

    >>> from pypuppetdb import connect
    >>> db = connect()
    >>> nodes = db.nodes()
    >>> print(nodes)
    <generator object 'nodes'>
    >>> for node in nodes:
    >>>   print(node)
    host1
    host2
    ...

This will return a generator object yielding Node objects for every returned
node from PuppetDB.

To query a single node the singular db.node() can be used:

   >>> node = db.node('hostname')
   >>> print(node)
   hostname

The Node objects are a bit more special in that they can query for facts and
resources themselves. Using those methods from a node object will automatically
add a query to the request scoping the request to the node.

   >>> node = db.node('hostname')
   >>> print node.fact('osfamily')
   osfamily/hostname

We can also query for facts:

   >>> facts = db.facts('osfamily')
   >>> print(facts)
   <generator object 'facts')
   >>> for fact in facts:
   >>> print(fact)
   osfamily/host1
   osfamily/host2

That querries PuppetDB for the 'osfamily' fact and will yield Fact objects,
one per node this fact is found on.

   >>> resources = db.resources('file')

Will return a generator object containing all file resources you're managing
across your infrastructure. This is probably a bad idea if you have a big
number of nodes as the response will be huge.
"""
import logging

from pypuppetdb.api import v2
from pypuppetdb.api import v3
from pypuppetdb.errors import UnsupportedVersionError

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:  # pragma: notest
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())


def connect(api_version=3, host='localhost', port=8080, ssl_verify=False,
            ssl_key=None, ssl_cert=None, timeout=10):
    """Connect with PuppetDB. This will return an object allowing you
    to query the API through its methods.

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

    :raises: :class:`~pypuppetdb.errors.UnsupportedVersionError`
    """
    if api_version == 3:
        return v3.API(host=host, port=port,
                      timeout=timeout, ssl_verify=ssl_verify, ssl_key=ssl_key,
                      ssl_cert=ssl_cert)
    if api_version == 2:
        return v2.API(host=host, port=port,
                      timeout=timeout, ssl_verify=ssl_verify, ssl_key=ssl_key,
                      ssl_cert=ssl_cert)
    else:
        raise UnsupportedVersionError

.. _quickstart:

Quickstart
==========
Once you have pypuppetdb installed you can configure it to connect to PuppetDB
and take it from there.

Connecting
----------

The first thing you need to do is to connect with PuppetDB:

.. code-block:: python

   >>> from pypuppetdb import connect
   >>> db = connect()

Nodes
-----

The following will return a generator object yielding Node objects for every
returned node from PuppetDB.

.. code-block:: python

   >>> nodes = db.nodes()
   >>> for node in nodes:
   >>>   print(node)
   host1
   host2
   ...

To query a single node the singular `node()` can be used:

.. code-block:: python

    >>> node = db.node('hostname')
    >>> print(node)
    hostname

Node scope
~~~~~~~~~~

The Node objects are a bit more special in that they can query for facts and
resources themselves. Using those methods from a node object will automatically
add a query to the request scoping the request to the node.

.. code-block:: python

   >>> node = db.node('hostname')
   >>> print(node.fact('osfamily'))
   osfamily/hostname

Facts
-----

.. code-block:: python

   >>> facts = db.facts('osfamily')
   >>> for fact in facts:
   >>>   print(fact)
   osfamily/host1
   osfamily/host2

That queries PuppetDB for the 'osfamily' fact and will yield Fact objects,
one per node this fact is known for.

Resources
---------

.. code-block:: python

   >>> resources = db.resources('file')

Will return a generator object containing all file resources you're managing
across your infrastructure. This is probably a bad idea if you have a big
number of nodes as the response will be huge.

SSL
---
If PuppetDB and the tool that's using pypuppetdb aren't located on the same
machine you will have to connect securely to PuppetDB using client certificates
according to PuppetDB's default configuration.

You can also tell PuppetDB to accept plain connections from anywhere instead
of just the local machine but **don't do that**.

Pypuppetdb can handle this easily for you. It requires two things:
  * Generate with your Puppet CA a key pair that you want to use
  * Tell pypuppetdb to use this keypair.

Generate keypair
~~~~~~~~~~~~~~~~

On your Puppet Master or dedicated Puppet CA server:

.. code-block:: console

   $ puppet cert generate <service_name>

Once that's done you'll need to get the public and private keyfile and copy
them over. You can find those in Puppet's ``$ssldir``, usually
``/var/lib/puppet/ssl``:

  * private key: ``$ssldir/private_keys/<service_name>.pem``
  * public key: ``$ssldir/ca/signed/<service_name>.pem``

Configure pypuppetdb for SSL
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Once you have those you can pass them to pypuppetdb's ``connect()``:

.. code-block:: python

   >>> db = connect(ssl_key='/path/to/private.pem', ssl_cert='/path/to/public.pem')

If both ``ssl_key`` and ``ssl_cert`` are provided pypuppetdb will automatically
switch over to using HTTPS instead.

By default pypuppetdb will also verify the certificate PuppetDB is serving.
This means that the authority that signed PuppetDB's server certificate, most
likely your Puppet Master, must be part of the trusted set of certificates for
your OS or must be added to that set. Those certificates are usually found in
``/etc/ssl/certs`` on Linux-y machines.

For Debian, install your Puppet Master's certificate in
``/usr/local/share/ca-certifiactes`` with a ``.crt`` extension and then run
``dpkg-reconfigure ca-certificates`` as per
``/usr/share/doc/ca-certificates/README.Debian``. This of course requires the
``ca-certificates`` package to be installed.

If you do not wish to do so or for whatever reason want to disable the
verification of PuppetDB's certificate you can pass in ``ssl_verify=False``.

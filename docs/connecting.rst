.. _connecting:

Connecting from other hosts
===========================

This article explains how to connect the application using pypuppetdb to PuppetDB if you are running
it on a different host than the PuppetDB itself.

SSL
---
If PuppetDB and the tool that's using pypuppetdb aren't located on the same
machine you will have to connect securely to PuppetDB using client certificates
according to PuppetDB's default configuration.

(You could also tell PuppetDB to accept plain connections from anywhere instead
of just the local machine but **you should not do that**.)

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
``/usr/local/share/ca-certificates`` with a ``.crt`` extension and then run
``dpkg-reconfigure ca-certificates`` as per
``/usr/share/doc/ca-certificates/README.Debian``. This of course requires the
``ca-certificates`` package to be installed.

If you do not wish to do so or for whatever reason want to disable the
verification of PuppetDB's certificate you can pass in ``ssl_verify=False``.

RBAC Token Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using Puppet Enterprise Puppetdb >=4.0.2 - an RBAC token can be passed
to pypuppetdb's ``connect()``:

.. code-block:: python

   >>> db = connect(token='tokenstring')

If this argument is passed, pypuppetdb will automatically switch over to using HTTPS.
This is handled via the addition of ``X-Authentication`` to the session headers

If you need to disable validation of the certificate PuppetDB is serving, please follow the
steps documented in the ``Configure pypuppetdb for SSL`` section

It should also be noted that when using RBAC token authentication,
the ``ssl_key`` and ``ssl_cert`` options should not be used and are not required
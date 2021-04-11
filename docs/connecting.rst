.. _connecting:

Connecting
==========

The first thing you need to do is to connect with PuppetDB.

From the same host as PuppetDB
------------------------------

Assuming that you are running the code on the same host as the PuppetDB
(configured with the default ports etc.) you can do just this:

.. code-block:: python

   >>> from pypuppetdb import connect
   >>> db = connect()

Once you're all done with requests to PuppetDB, you can explicitly close all
HTTP connections. This can be useful if you made those connections through a
tunnel, which might be tracking open connections:

.. code-block:: python

   >>> db.disconnect()

You can also use the `with` statement to enclose the work done on PuppetDB.
This will ensure that all HTTP connections are closed explicitly when we're
done:

.. code-block:: python

   >>> with connect() as db:
   >>>   # ..

From a different host than PuppetDB
-----------------------------------

SSL / TLS
^^^^^^^^^

If PuppetDB and the tool that's using pypuppetdb aren't located on the same
machine you will have to connect to PuppetDB securely using client certificates
according to PuppetDB's default configuration.

(You could also tell PuppetDB to accept plain connections from anywhere instead
of just the local machine but **you should not do that**.)

Pypuppetdb can handle this easily for you. It requires two things:
  * Generate with your Puppet CA a key pair that you want to use
  * Tell pypuppetdb to use this keypair.

Generate keypair
""""""""""""""""

On your Puppet Master or dedicated Puppet CA server:

.. code-block:: console

   $ puppet cert generate <service_name>

Once that's done you'll need to get the public and private keyfile
and your Puppet CA root certificate. You can find those in Puppet's
``$ssldir``, usually ``/var/lib/puppet/ssl``:

  * private key: ``$ssldir/private_keys/<service_name>.pem``
  * public key: ``$ssldir/ca/signed/<service_name>.pem``
  * CA root certificate: ``$ssldir/ca/ca_crt.pem``

Configure pypuppetdb for SSL
""""""""""""""""""""""""""""

Once you have those you can pass them to pypuppetdb's ``connect()``:

.. code-block:: python

   >>> db = connect(ssl_key='/path/to/private.pem', ssl_cert='/path/to/public.pem',
   >>>              ssl_verify='/path/to/ca_crt.pem', host='puppetdb.example.com',
   >>>              port=8081)

This will make pypuppedb use HTTPS with a mutual TLS (client will verify
if the server is using a certificate issues by our Puppet CA, server will
verify the same for the client's certificate).

If for whatever reason want to disable the verification of PuppetDB's
certificate you can pass in ``ssl_verify=False``.


RBAC Token Authentication
~~~~~~~~~~~~~~~~~~~~~~~~~

If you are using Puppet Enterprise Puppetdb >=4.0.2 - an RBAC token can be passed
to pypuppetdb's ``connect()``:

.. code-block:: python

   >>> db = connect(token='tokenstring', host='puppetdb.example.com',
   >>>              port=8081)

If this argument is passed, pypuppetdb will automatically switch over to using HTTPS.
This is handled via the addition of ``X-Authentication`` to the session headers

If you need to disable validation of the certificate PuppetDB is serving, please follow the
steps documented in the ``Configure pypuppetdb for SSL`` section

It should also be noted that when using RBAC token authentication,
the ``ssl_key`` and ``ssl_cert`` options should not be used and are not required.


Basic authentication
^^^^^^^^^^^^^^^^^^^^

Instead of using Puppet's certificates for mutual TLS, you may want to use plain HTTPS
with HTTP Basic Authentication. To do that you have to set up a reverse proxy in front
of the PuppetDB, that will do the SSL termination and the Basic Auth.

Then you can connect pypuppetdb to it with this code:

.. code-block:: python

   >>> db = connect(protocol='https', host='puppetdb.example.com',
   >>>              port=443, username='foo', password='bar')

If your proxy serves PuppetDB under a different path than ``/``, then you can also
provide the ``url_path`` parameter.

.. _api:

Developer Interface
===================

.. module:: pypuppetdb

This part of the documentation covers all the interfaces of PyPuppetDB.
It will cover how the API is set up and how to configure which version of
the API to use.

Lazy objects
------------

.. note::

   Reading in the response from PuppetDB is currently greedy, it will read in
   the complete response no matter the size. This will change once streaming
   and pagination support are added to PuppetDB's endpoints.

In order for pypuppetdb to be able to deal with big datasets those functions
that are expected to return more than a single item are implemented as
generators.

This is usually the case for functions with a plural name like
:func:`~pypuppetdb.api.BaseAPI.nodes` or :func:`~pypuppetdb.api.BaseAPI.facts`.

Because of this we'll only query PuppetDB once you start iterating over the
generator object. Until that time not a single request is fired at PuppetDB.

Most singular functions are implemented by calling their plural counterpart
and then iterating over the generator, immediately exhausting the generator
and returning a single/the first object.

Main Interface
--------------

What you'll usually need to do is use the :func:`connect` method to set up a
connection with PuppetDB and indicate which version of the API you want to
talk.
.. autofunction:: connect

API objects
-----------

The PuppetDB API is no longer versioned. This was changed in v0.2.0 because
it started to become too difficult to maintain multiple API versions.

All the functions of the v1, v2, and v3 APIs have been moved to :class:`BaseAPI
<BaseAPI>` which now only supports API version 4 of PuppetDB.

.. data:: API_VERSIONS

   :obj:`dict` of :obj:`int`::obj:`string` pairs representing the API version
   and it's URL prefix.

   We currently only handle API version 2 though it should be fairly easy to
   support version 1 should we want to.

BaseAPI
^^^^^^^

.. autoclass:: pypuppetdb.api.BaseAPI
   :members:
   :private-members:

Types
-----

In order to facilitate working with the API most methods like
:meth:`~pypuppetdb.api.BaseAPI.nodes` don't return the decoded
JSON response but return an object representation of the querried
endpoints data.

.. autoclass:: pypuppetdb.types.Node
   :members:
.. autoclass:: pypuppetdb.types.Fact
.. autoclass:: pypuppetdb.types.Resource
.. autoclass:: pypuppetdb.types.Event
.. autoclass:: pypuppetdb.types.Report
   :members:
.. autoclass:: pypuppetdb.types.Catalog
   :members:
.. autoclass:: pypuppetdb.types.Edge

Errors
------

Unfortunately things can go haywire. PuppetDB might not be reachable
or complain about our query, requests might have to wait too long to
recieve a response or the body is just too big to handle.

In that case, we'll throw an exception at you.

.. autoexception:: pypuppetdb.errors.APIError
.. autoexception:: pypuppetdb.errors.ImproperlyConfiguredError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.DoesNotComputeError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.EmptyResponseError
   :show-inheritance:

Utilities
---------

A few functions that are used across this library have been put
into their own :mod:`utils` module.

.. autoclass::    pypuppetdb.utils.UTC
.. autofunction:: pypuppetdb.utils.json_to_datetime
.. autofunction:: pypuppetdb.utils.versioncmp

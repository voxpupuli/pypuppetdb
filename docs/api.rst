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
:func:`~pypuppetdb.api.v2.API.nodes` or :func:`~pypuppetdb.api.v2.API.facts`.

Because of this we'll only query PuppetDB once you start iterating over the
generator object. Until that time not a single request is fired at PuppetDB.

Most singular functions are implemented by calling their plural counterpart
and then iterating over the generator, immediately exhausting the generator
and returning a single/the first object.

Main Interface
--------------

What you'll usually need to do is use the :func:`connect` method to set up a
connection with PuppetDB and indicate which version of the API you want to
talk. Additionally it allows you to enable or disable the experimental
features.

.. autofunction:: connect

API objects
-----------

The PuppetDB API is versioned. We currently have a v1 and v2 and an additional
'experimental' version containing features that are worked on and will become
available in (probably) a newer version of the API.

In order to work with this structure PyPuppetDB consists of a :class:`BaseAPI
<BaseAPI>` class that factors out identical code between different versions.

Every version of the API has its own class which inherits from our
:class:`BaseAPI <BaseAPI>`.

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

v2.API
^^^^^^
.. autoclass:: pypuppetdb.api.v2.API
   :members:
   :inherited-members:
   :private-members:
   :show-inheritance:

Types
-----

In order to facilitate working with the API most methods like
:meth:`~pypuppetdb.api.v2.API.nodes` don't return the decoded
JSON response but return an object representation of the querried
endpoints data.

.. autoclass:: pypuppetdb.types.Node
   :members:
.. autoclass:: pypuppetdb.types.Fact
.. autoclass:: pypuppetdb.types.Resource
.. autoclass:: pypuppetdb.types.Event
.. autoclass:: pypuppetdb.types.Report

Errors
------

Unfortunately things can go haywire. PuppetDB might not be reachable
or complain about our query, requests might have to wait too long to
recieve a response or the body is just too big to handle.

In that case, we'll throw an exception at you.

.. autoexception:: pypuppetdb.errors.APIError
.. autoexception:: pypuppetdb.errors.ImproperlyConfiguredError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.UnsupportedVersionError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.ExperimentalDisabledError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.DoesNotComputeError
   :show-inheritance:
.. autoexception:: pypuppetdb.errors.EmptyResponseError
   :show-inheritance:

Utilities
---------

A few functions that are used across this library have been put
into their own :mod:`utils` module.

.. autofunction:: pypuppetdb.utils.json_to_datetime
.. autofunction:: pypuppetdb.utils.experimental

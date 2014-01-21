#########
Changelog
#########

0.1.1
=====

* Fix the license in our ``setup.py``. The license shouldn't be longer than
  200 characters. We were including the full license tripping up tools like
  bdist_rpm.

0.1.0
=====
Significant changes have been made in this release. The complete v3 API is
now supported except for query pagination.

Most changes are backwards compatible except for a change in the SSL
configuration. The previous behaviour was buggy and slightly misleading in
the names the options took:

* ``ssl`` has been renamed to ``ssl_verify`` and now defaults to ``True``.
* Automatically use HTTPS if ``ssl_key`` and ``ssl_cert`` are provided.

For additional instructions about getting SSL to work see the Quickstart
in the documentation.

Deprecation
------------
Support for API v2 will be dropped in the 0.2.x release series.

New features
------------

The following features are **only** supported for **API v3**.

The ``node()`` and ``nodes()`` function have gained the following options:

  * ``with_status=False``
  * ``unreported=2``

When ``with_status`` is set to ``True`` an additional query will be made using
the ``events-count`` endpoint scoped to the latest report. This will result in
an additional ``events`` and ``status`` keys on the node object. ``status``
will be either of ``changed``, ``unchanged`` or ``failed`` depending on if
``events`` contains ``successes`` or ``failures`` or none.

By default ``unreported`` is set to ``2``. This is only in effect when
``with_status`` is set to ``True``. It means that if a node hasn't checked in
for two hours it will get a ``status`` of ``unreported`` instead.

New endpoints:

  * ``events-count``: ``events_count()``
  * ``aggregate-event-counts``: ``aggregate_event_counts()``
  * ``server-time``: ``server_time()``
  * ``version``: ``current_version()``
  * ``catalog``: ``catalog()``

New types:

  * ``pypuppetdb.types.Catalog``
  * ``pypuppetdb.types.Edge``

Changes to types:

  * ``pypuppetdb.types.Node`` now has:
    * ``status`` defaulting to ``None``
    * ``events`` defaulting to ``None``
    * ``unreported_time`` defaulting to ``None``

0.0.4
=====

Due to a fairly serious bug 0.0.3 was pulled from PyPi minutes after release.

When a bug was fixed to be able to query for all facts we accidentally
introduced a different bug that caused the ``facts()`` call on a node to
query for all facts because we were resetting the query.

* Fix a bug where ``node.facts()`` was causing us to query all facts because
  the query to scope our request was being reset.

0.0.3
=====

With the introduction of PuppetDB 1.5 a new API version, v3, was also
introduced. In that same release the old ``/experimental`` endpoints
were removed, meaning that as of PuppetDB 1.5 with the v2 API you can
no longer get access to reports or events.

In light of this the support for the experimental endpoints has been
completely removed from pypuppetdb. As of this release you can only get
to reports and/or events through v3 of the API.

This release includes preliminary support for the v3 API. Everything that
could be done with v2 plus the experimental endpoints is now possible on
v3. However, more advanced funtionality has not yet been implemented. That
will be the focus of the next release.

* Removed dependency on pytz.
* Fixed the behaviour of ``facts()`` and ``resources()``. We can now
  correctly query for all facts or resources.
* Fixed an issue with catalog timestampless nodes.
* Pass along the ``timeout`` option to ``connect()``.
* Added preliminary PuppetDB API v3 support.
* Removed support for the experimental endpoints.
* The ``connect()`` method defaults to API v3 now.

0.0.2
=====
* Fix a bug in ``setup.py`` preventing successful installation.

0.0.1
=====
Initial release. Implements most of the v2 API.

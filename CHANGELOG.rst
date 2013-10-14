#########
Changelog
#########

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

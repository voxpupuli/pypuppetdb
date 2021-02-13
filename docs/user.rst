.. _user:

User Guide
==========
Once you have pypuppetdb installed you can configure it to connect to PuppetDB
and take it from there.

Connecting
----------

The first thing you need to do is to connect with PuppetDB. **Assuming that you
are running the code on the same host as the PuppetDB**:

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

**If you are running the code on a different host than PuppetDB** please read
the :ref:`connecting` guide.

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

Catalogs
--------

.. code-block:: python

   >>> catalog = db.catalog('hostname')
   >>> for res in catalog.get_resources():
   >>>     print(res)

Will return a Catalog object with the latest Catalog of the definded
host. This catalog contains the defined Resources and Edges.

.. code-block:: python

   >>> catalog = db.catalog('hostname')
   >>> resource = catalog.get_resource('Service','ntp')
   >>> for rel in resource.relationships:
   >>>     print(rel)
   Class[Ntp] - contains - Service[ntp]
   File[/etc/ntp.conf] - notifies - Service[ntp]
   File[/etc/ntp.conf] - required-by - Service[ntp]


Will return all Relationships of a given Resource defined by type and
title. This will list all linked other Resources and the type of
relationship.

Query Builder
-------------

pypuppetdb comes shipped with a QueryBuilder component that, as the name suggests,
allows users to build PuppetDB AST queries in an Object-Oriented fashion.
Vastly superior to constructing long strings than adding additional clauses to fulfill
new requirements.

The following code will build a query for the Nodes endpoint to find all
nodes belonging to the production environment.

.. code-block:: python

   >>> from pypuppetdb.QueryBuilder import *
   >>> op = AndOperator()
   >>> op.add(EqualsOperator('catalog_environment', 'production'))
   >>> op.add(EqualsOperator('facts_environment', 'production'))
   >>> print(op)
   ["and",["=", "catalog_environment", "production"],["=", "facts_environment", "production"]]

This functionality is based on the PuppetDB AST query string syntax
documented
`here <https://puppet.com/docs/puppetdb/latest/api/query/v4/ast.html>`_.

Subqueries are implemented using corresponding operators (like
documented).

  - SubqueryOperator
  - InOperator
  - ExtractOperator

.. code-block:: python

   >>> from pypuppetdb.QueryBuilder import *
   >>> op = InOperator('certname')
   >>> ex = ExtractOperator()
   >>> ex.add_field(str('certname'))
   >>> sub = SubqueryOperator('events')
   >>> sub.add_query(EqualsOperator('status', 'noop'))
   >>> ex.add_query(sub)
   >>> op.add_query(ex)
   >>> print(op)
   ["in","certname",["extract",["certname"],["select_events",["=", "status", "noop"]]]]

Or using in \<array\> querying:

.. code-block:: python

   >>> from pypuppetdb.QueryBuilder import *
   >>> op = InOperator('certname')
   >>> op.add_array(["prod1.server.net", "prod2.server.net"])
   >>> print(op)
   ["in","certname",["array", ['prod1.server.net', 'prod2.server.net']]]

You can also access different entities from a single query on the root
endpoint with the FromOperator:

.. code-block:: python

   >>> op = InOperator('certname')
   >>> ex = ExtractOperator()
   >>> ex.add_field('certname')
   >>> fr = FromOperator('fact_contents')
   >>> nd = AndOperator()
   >>> nd.add(EqualsOperator("path", ["networking", "eth0", "macaddresses", 0]))
   >>> nd.add(EqualsOperator("value", "aa:bb:cc:dd:ee:00"))
   >>> ex.add_query(nd)
   >>> fr.add_query(ex)
   >>> op.add_query(fr)
   >>> print(op)
   ["in","certname",["from","fact_contents",["extract",["certname"],["and",["=", "path", ['networking', 'eth0', 'macaddresses', 0]],["=", "value", "aa:bb:cc:dd:ee:00"]]]]]

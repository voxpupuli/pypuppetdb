.. _advanced_queries:

Advanced Queries
================

For more advanced use of pypuppetdb you will want to use queries in one of the
two available languages:

* **PQL** (Puppet Query Language) - newer, arguably more human-friendly. Available
  since PuppetDB v. 4.0.

* **AST** (Abstract Syntax Tree) - older, using the Reverse Polish Notation.


PQL query with rich types
-------------------------

Making a PQL query using ``pql()`` method without using projection for one of the supported types
(``nodes``, ``edges``, ``facts``, ``resources``, ``catalogs``, ``events``, ``reports``, ``inventory``) will return
the rich types.

For example the below code returns objects of the type ``Node``:

.. code-block:: python

   >>> nodes = db.pql("""
   >>>     nodes {
   >>>       facts {
   >>>         name = "operatingsystem" and
   >>>         value = "Debian"
   >>>       }
   >>>     }
   >>> """
   >>> for node in nodes:
   >>>     print(node.name)
   foo.example.com
   bar.example.com


PQL query returning raw dicts
-----------------------------

If you do use projections (fields/functions) in your PQL query or you query for a unsupported type,
you will get JSON like you would querying PuppetDB directly, just converted into a Python dicts
or list of dicts.

For example if you want to get just a list of certnames of nodes that have the fact "operatingsystem"
set to "Debian":

.. code-block:: python

   >>> nodes = db.pql("""
   >>>     nodes[certname] {
   >>>       facts {
   >>>         name = "operatingsystem" and
   >>>         value = "Debian"
   >>>       }
   >>>     }
   >>> """
   >>> for node in nodes:
   >>>     print(node)
   {'certname': 'foo.example.com'}
   {'certname': 'bar.example.com'}

Please see `the official PQL documentation <https://puppet.com/docs/puppetdb/latest/api/query/v4/pql.html>`_
for more examples.


AST query
---------

Alternatively to use the AST query language, use of of these methods:

``nodes()``, ``edges()``,  ``facts()``, ``resources()``, ``catalogs()``, ``events()``,
``reports()``, ``inventory()``,
``event_counts()``, ``aggregate_event_counts()``,
``environments()``, ``factsets()``, ``fact_contents()``, ``fact_paths()``.

...and pass the AST query in the ``query`` parameter.

An example of the same query as above but rewritten in AST:

.. code-block:: python

   >>> nodes = db.nodes(query="""
   >>>     ["subquery", "facts",
   >>>       ["and",
   >>>         ["=", "name", "operatingsystem"],
   >>>         ["=", "value", "Debian"]
   >>>       ]
   >>>     ]
   >>> """
   >>> for node in nodes:
   >>>     print(node.name)
   foo.example.com
   bar.example.com

Please see `the official AST documentation <https://puppet.com/docs/puppetdb/latest/api/query/v4/ast.html>`_
for more examples .

AST QueryBuilder
^^^^^^^^^^^^^^^^

pypuppetdb laso comes shipped with a ``QueryBuilder`` component that, as the name suggests,
allows users to build PuppetDB AST queries in an Object-Oriented fashion.
In many cases adding additional clauses to fulfill new requirements is superior to constructing
long strings.

Above example rewritten using it:

.. code-block:: python

   >>> from pypuppetdb.QueryBuilder import *
   >>> op = InOperator('certname')
   >>> query = ExtractOperator()
   >>> query.add_field(str('certname'))
   >>> subquery = SubqueryOperator('facts')
   >>> _add = AndOperator()
   >>> _add.add(EqualsOperator('name', 'operatingsystem'))
   >>> _add.add(EqualsOperator('value', 'Debian'))
   >>> subquery.add_query(_add)
   >>> query.add_query(subquery)
   >>> op.add_query(query)
   >>> print(op)
   ["in", "certname", ["extract", ["certname"], ["select_facts", ["and", ["=", "name", "operatingsystem"], ["=", "value", "Debian"]]]]]
   >>> nodes = db.nodes(query=query)
   >>> for node in nodes:
   >>>     print(node.name)
   foo.example.com
   bar.example.com


The following code will build a query for the Nodes endpoint to find all
nodes belonging to the production environment.

.. code-block:: python

   >>> from pypuppetdb.QueryBuilder import *
   >>> op = AndOperator()
   >>> op.add(EqualsOperator('catalog_environment', 'production'))
   >>> op.add(EqualsOperator('facts_environment', 'production'))
   >>> print(op)
   ["and",["=", "catalog_environment", "production"],["=", "facts_environment", "production"]]


Subqueries are implemented using corresponding operators (like documented).

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

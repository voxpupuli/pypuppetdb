.. _basics:

Basics
======

The most basic use cases is to get some single entities or multiple
entities from the PuppetDB without advanced queries.

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

To query a single node the singular `node()` method can be used:

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
   >>> print(node.fact('osfamily').value)
   RedHat

Facts
-----

.. code-block:: python

   >>> facts = db.facts('osfamily')
   >>> for fact in facts:
   >>>   print(f"{fact.node} - {fact.value}")
   host1 - RedHat
   host2 - Debian

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

Will return a Catalog object with the latest Catalog of the defined
host. This catalog contains the defined Resources and Edges.

.. code-block:: python

   >>> catalog = db.catalog('hostname')
   >>> resource = catalog.get_resource('Service', 'ntp')
   >>> for rel in resource.relationships:
   >>>     print(rel)
   Class[Ntp] - contains - Service[ntp]
   File[/etc/ntp.conf] - notifies - Service[ntp]
   File[/etc/ntp.conf] - required-by - Service[ntp]


Will return all Relationships of a given Resource defined by type and
title. This will list all linked other Resources and the type of
relationship.

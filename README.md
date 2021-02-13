# pypuppetdb

[![PyPi Version](https://img.shields.io/pypi/v/pypuppetdb)](https://pypi.org/project/pypuppetdb/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/pypuppetdb)](https://pypi.org/project/pypuppetdb/)
[![image](https://api.travis-ci.org/voxpupuli/pypuppetdb.png)](https://travis-ci.org/voxpupuli/pypuppetdb)
[![Coverage Status](https://img.shields.io/coveralls/voxpupuli/pypuppetdb.svg)](https://coveralls.io/r/voxpupuli/pypuppetdb)
[![By Voxpupuli](https://img.shields.io/badge/by-Vox%20Pupuli%20%F0%9F%A6%8A-ef902f.svg)](http://voxpupuli.org)

This library is a thin wrapper around the REST API providing some
convenience functions and objects to request and hold data from
PuppetDB.

## Table of Contents

// TODO: add

## Requirements

* PuppetDB 3.0 or newer
  * (For the support of older PuppetDB versions please check v. < 0.2.0)
* Python 3.6/3.7/3.8

## Installation

You can install this package from PyPI with:

``` bash
pip install pypuppetdb
```

## Documentation

You can [find it here](https://pypuppetdb.readthedocs.org/en/latest/).

## Usage

Once you have pypuppetdb installed you can configure it to connect to
PuppetDB and take it from there.

### Connecting

The first thing you need to do is to connect with PuppetDB:

``` python
>>> from pypuppetdb import connect
>>> db = connect()
```

Once you're all done with requests to PuppetDB, you can explicitly close
all HTTP connections. This can be useful if you made those connections
through a tunnel, which might be tracking open connections:

``` python
>>> db.disconnect()
```

You can also use the <span class="title-ref">with</span> statement to
enclose the work done on PuppetDB. This will ensure that all HTTP
connections are closed explicitly when we're done:

``` python
>>> with connect() as db:
>>>   # ..
```

### Nodes

The following will return a generator object yielding Node objects for
every returned node from PuppetDB.

``` python
>>> nodes = db.nodes()
>>> for node in nodes:
>>>   print(node)
host1
host2
...
```

To query a single node the singular
<span class="title-ref">node()</span> can be used:

``` python
>>> node = db.node('hostname')
>>> print(node)
hostname
```

### Node scope

The Node objects are a bit more special in that they can query for facts
and resources themselves. Using those methods from a node object will
automatically add a query to the request scoping the request to the
node.

``` python
>>> node = db.node('hostname')
>>> print(node.fact('osfamily'))
osfamily/hostname
```

### Facts

``` python
>>> facts = db.facts('osfamily')
>>> for fact in facts:
>>>   print(fact)
osfamily/host1
osfamily/host2
```

That queries PuppetDB for the 'osfamily' fact and will yield Fact
objects, one per node this fact is known for.

### Resources

``` python
>>> resources = db.resources('file')
```

Will return a generator object containing all file resources you're
managing across your infrastructure. This is probably a bad idea if you
have a big number of nodes as the response will be huge.

### Catalogs

``` python
>>> catalog = db.catalog('hostname')
>>> for res in catalog.get_resources():
>>>     print(res)
```

Will return a Catalog object with the latest Catalog of the definded
host. This catalog contains the defined Resources and Edges.

``` python
>>> catalog = db.catalog('hostname')
>>> resource = catalog.get_resource('Service','ntp')
>>> for rel in resource.relationships:
>>>     print(rel)
Class[Ntp] - contains - Service[ntp]
File[/etc/ntp.conf] - notifies - Service[ntp]
File[/etc/ntp.conf] - required-by - Service[ntp]
```

Will return all Relationships of a given Resource defined by type and
title. This will list all linked other Resources and the type of
relationship.

### Query Builder

Starting with version 0.3.0 pypuppetdb comes shipped with a QueryBuilder
component that, as the name suggests, allows users to build PuppetDB AST
queries in an Object-Oriented fashion. Vastly superior to constructing
long strings than adding additional clauses to fulfill new requirements.

The following code will build a query for the Nodes endpoint to find all
nodes belonging to the production environment.

``` python
>>> from pypuppetdb.QueryBuilder import *
>>> op = AndOperator()
>>> op.add(EqualsOperator('catalog_environment', 'production'))
>>> op.add(EqualsOperator('facts_environment', 'production'))
>>> print(op)
["and",["=", "catalog_environment", "production"],["=", "facts_environment", "production"]]
```

This functionality is based on the PuppetDB AST query string syntax
documented
[here](https://docs.puppet.com/puppetdb/4.1/api/query/v4/ast.html).

Subqueries are implemented using corresponding operators (like
documented).

  - SubqueryOperator
  - InOperator
  - ExtractOperator

<!-- end list -->

``` python
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
```

Or using \[in \<array\>\] querying:

``` python
>>> from pypuppetdb.QueryBuilder import *
>>> op = InOperator('certname')
>>> op.add_array(["prod1.server.net", "prod2.server.net"])
>>> print(op)
["in","certname",["array", ['prod1.server.net', 'prod2.server.net']]]
```

You can also access different entities from a single query on the root
endpoint with the FromOperator:

``` python
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
```

## Getting Help

For bug reports you can file an
[issue](https://github.com/voxpupuli/pypuppetdb/issues). If you need
help with something feel free to pop by \#voxpupuli or the \#puppetboard on
[Freenode](http://freenode.net) or [Vox Pupuli on Slack](https://puppetcommunity.slack.com/messages/voxpupuli/).

## Contributing

We welcome contributions to this library. However, there are a few
ground rules contributors should be aware of.

### License

This project is licensed under the Apache v2.0 License. As such, your
contributions, once accepted, are automatically covered by this license.

Copyright (c) 2013-2014 Daniele Sluijters

### Commit messages

Write decent commit messages. Don't use swear words and refrain from
uninformative commit messages as 'fixed typo'.

The preferred format of a commit message:

    docs/quickstart: Fixed a typo in the Nodes section.
    
    If needed, elaborate further on this commit. Feel free to write a
    complete blog post here if that helps us understand what this is
    all about.
    
    Fixes #4 and resolves #2.

If you'd like a more elaborate guide on how to write and format your
commit messages have a look at this post by [Tim
Pope](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).

### Tests

Commits are expected to contain tests or updates to tests if they add to
or modify the current behavior.

The test suite is powered by [pytest](http://pytest.org/latest/) and
requires [pytest](http://pytest.org/latest/),
[pytest-pep8](https://pypi.python.org/pypi/pytest-pep8),
[httpretty](https://pypi.python.org/pypi/httpretty/) and
[pytest-httpretty](https://github.com/papaeye/pytest-httpretty) which
will be installed for you if you run:

``` bash
pip install -r requirements.txt
```

To run the unit tests (the ones that don't require a live PuppetDB):

``` bash
py.test -v -m unit
```

If the tests pass, you're golden. If not we'll have to figure out why
and fix that. Feel free to ask for help on this.

### Building documentation

API documentation is automatically generated from the docstrings using
Sphinx's autodoc feature.

Documentation will automatically be rebuilt on every push thanks to the
Read The Docs webhook. You can [find it
here](https://pypuppetdb.readthedocs.org/en/latest/).

You can build the documentation manually by doing:

``` bash
cd docs
make html
```

Doing so will only work if you have Sphinx installed, which you can
achieve through:

``` bash
pip install -r requirements.txt
```

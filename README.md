# pypuppetdb

[![PyPi Version](https://img.shields.io/pypi/v/pypuppetdb)](https://pypi.org/project/pypuppetdb/)
[![PyPi Downloads](https://img.shields.io/pypi/dm/pypuppetdb)](https://pypi.org/project/pypuppetdb/)
[![image](https://api.travis-ci.org/voxpupuli/pypuppetdb.png)](https://travis-ci.org/voxpupuli/pypuppetdb)
[![Coverage Status](https://img.shields.io/coveralls/voxpupuli/pypuppetdb.svg)](https://coveralls.io/r/voxpupuli/pypuppetdb)
[![By Voxpupuli](https://img.shields.io/badge/by-Vox%20Pupuli%20%F0%9F%A6%8A-ef902f.svg)](http://voxpupuli.org)

This library is a thin wrapper around the REST API providing some
convenience functions and objects to request and hold data from
PuppetDB.

## Requirements

* PuppetDB 3.0 or newer
  * (For support of older PuppetDB versions please check versions < 0.2.0)
* Python 3.6/3.7/3.8

## Installation

You can install this package from PyPI with:

```bash
pip install pypuppetdb
```

## Documentation

You can [a quickstart and an API reference on ReadTheDocs.com](https://pypuppetdb.readthedocs.org/en/latest/).

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

### Preparing local development environment

```bash
# Create a Python 3 virtualenv and activate it
virtualenv -p python3 .venv
. .venv/bin/activate
# Install the module in a development mode
python setup.py develop
# Install test dependencies
pip install -r requirements-test.txt
```
### Tests

Commits are expected to contain tests or updates to the tests if they add to
or modify the current behavior.

Assuming you have prepared the development environment as explained above,
do this to run the unit tests:

```bash
py.test
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

```bash
# Activate the virtualenv and install sphinx
pip install sphinx
cd docs
make html
```

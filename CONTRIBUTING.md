# Contribution guide

We welcome contributions to this library. However, there are a few
ground rules contributors should be aware of.

## Commit messages

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
Pope](https://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html).

## Preparing local development environment

```bash
# Create a Python 3 virtualenv and activate it
virtualenv -p python3 .venv
. .venv/bin/activate
# Get the up to date base packages
pip install --upgrade wheel setuptools
# Install the module in a development mode
python setup.py develop
# Install/update test dependencies
pip install --upgrade -r requirements-test.txt
```

## Tests

Commits are expected to contain tests or updates to the tests if they add to
or modify the current behavior.

Assuming you have prepared the development environment as explained above,
do this to run the tests:

```bash
# Unit tests, with PEP8 and mypy (static typing) checks
mypy --install-types --non-interactive pypuppetdb/ tests/
pytest --flake8 --strict-markers --mypy pypuppetdb tests
# Security linter
bandit -r pypuppetdb
```

If the tests pass, you're golden. If not we'll have to figure out why
and fix that. Feel free to ask for help on this.

## Building documentation

API documentation is automatically generated from the docstrings using
Sphinx's autodoc feature.

Documentation will automatically be rebuilt on every push thanks to the
Read The Docs webhook. You can [find it
here](https://pypuppetdb.readthedocs.org/en/latest/).

You can build the documentation locally by doing:

```bash
# Activate the virtualenv used for the app development
pip install --upgrade -r docs/requirements.txt
cd docs
make html
```

## Preparing a release

This project is using [tbump](https://github.com/dmerejkowsky/tbump) for releases.

1. Add entry to the `CHANGELOG.md` / verify that it contains all the changes.
2. Run `tbump <new_version>`
3. Edit the release created in GitHub - if needed correct the type (final/prerelease), update the description with a changelog fragment.

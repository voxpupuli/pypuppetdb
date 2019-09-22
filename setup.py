import sys
import os
import codecs

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


def rc_value():
    with open('version') as fp:
        val = fp.read().rstrip()
    return '{}rc0'.format(val)


def version():
    return os.getenv('TRAVIS_TAG', rc_value())


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)

with codecs.open('README.rst', encoding='utf-8') as f:
    README = f.read()

with codecs.open('CHANGELOG.rst', encoding='utf-8') as f:
    CHANGELOG = f.read()

requirements = None
with open('requirements.txt', 'r') as f:
    requirements = [line.rstrip()
                    for line in f.readlines() if not line.startswith('-')]

requirements_test = None
with open('requirements-test.txt', 'r') as f:
    requirements_test = [line.rstrip() for line in f.readlines()
                         if not line.startswith('-')]

setup(
    name='pypuppetdb',
    version=version(),
    author='Vox Pupuli',
    author_email='voxpupuli@groups.io',
    packages=find_packages(),
    url='https://github.com/voxpupuli/pypuppetdb',
    license='Apache License 2.0',
    description='Library for working with the PuppetDB REST API.',
    long_description='\n'.join((README, CHANGELOG)),
    long_description_content_type='text/x-rst',
    keywords='puppet puppetdb',
    tests_require=requirements_test,
    data_files=[('requirements_for_tests', ['requirements-test.txt'])],
    cmdclass={'test': Tox},
    install_requires=requirements,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries'
        ],
    )

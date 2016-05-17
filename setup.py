import sys
import os
import codecs

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


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

setup(
    name='pypuppetdb',
    version='0.2.3',
    author='Corey Hammerton',
    author_email='corey.hammerton@gmail.com',
    packages=find_packages(),
    url='https://github.com/voxpupuli/pypuppetdb',
    license='Apache License 2.0',
    description='Library for working with the PuppetDB REST API.',
    long_description='\n'.join((README, CHANGELOG)),
    keywords='puppet puppetdb',
    tests_require=['tox'],
    cmdclass={'test': Tox},
    install_requires=[
        "requests >= 1.2.3",
        ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Libraries'
        ],
    )

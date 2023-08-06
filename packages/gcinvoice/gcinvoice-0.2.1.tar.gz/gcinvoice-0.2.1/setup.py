#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import io  # io.open used instead of open to support python < 3
import re
from glob import glob
import os.path
from os.path import basename, splitext

import setuptools

here = os.path.abspath(os.path.dirname(__file__))

pkgname = 'gcinvoice'

def read(*parts):
    with io.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()

def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setuptools.setup(
    name=pkgname,

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version=find_version("src", pkgname, "_version.py"),

    description='Parse Gnucash data and create invoices',
    long_description="\n\n".join([read('README.rst'), read('CHANGELOG')]),
    long_description_content_type="text/x-rst",

    # The project's main homepage.
    url='https://bitbucket.org/smoerz/gcinvoice',

    # Author details
    author='Roman Bertle',
    author_email='bertle@smoerz.org',

    # Choose your license
    license='MIT License',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial :: Accounting',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',

        # This bogus classifier inhibits uploading this package to PyPI
        #'Private :: Do Not Upload',

        # Other classifiers

        'Environment :: Console',
    ],

    # What does your project relate to?
    keywords='Gnucash reporting',

    # all packages are in the 'src' directory, take them all
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    # all py files in src are modules
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],

    # List run-time dependencies here.  These will be installed by pip when your
    # project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
       'future;python_version<"3.0"',
    ],

    # List additional groups of dependencies here (e.g. development dependencies).
    # You can install these using the following syntax, for example:
    # $ pip install -e .[dev,test]
    #extras_require = {
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #    'rst': ['docutils>=0.11'],
    #    ':python_version=="2.6"': ['argparse'],
    #},

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    #package_data={
    #    'gcinvoice': ['package_data.dat'],
    #},

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages.
    # see http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    #data_files=[('my_data', ['data/data_file'])],
	
    # If set also install files from MANIFEST.in; else they are only packaged
    # MANIFEST.in is used to put files into the sdist without installing them
    #include_package_data=True, 

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'create_gcinvoice=gcinvoice.gcivc:cli',
        ],
    },
)

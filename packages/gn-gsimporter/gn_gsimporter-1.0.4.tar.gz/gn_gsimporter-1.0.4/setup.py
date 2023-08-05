#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name = "gn_gsimporter",
    version = "1.0.4",
    description = "GeoNode GeoServer Importer Client",
    keywords = "GeoNode GeoServer Importer",
    license = "MIT",
    url = "https://github.com/GeoNode/gsimporter",
    author = "Ian Schneider",
    author_email = "ischneider@opengeo.org",
    install_requires = [
        'httplib2',
    ],
    tests_require = [
        'gisdata>=0.5.4',
        'gsconfig>=1.0.0',
        'psycopg2',
        'OWSLib>=0.7.2',
        'unittest2',
    ],
    packages=find_packages(),
    include_package_data = True,
    zip_safe = False,
    classifiers  = [],
    test_suite = 'test.uploadtests'
)

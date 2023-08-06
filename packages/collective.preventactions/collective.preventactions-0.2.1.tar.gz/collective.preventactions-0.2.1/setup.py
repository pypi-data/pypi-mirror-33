# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

import os


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = \
    read('README.rst') + \
    read('CHANGES.rst')

setup(
    name='collective.preventactions',
    version='0.2.1',
    description="This package allows administrateur to marker object which can't be deleted",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
    ],
    keywords='Plone Python Zope',
    author='Benoît Suttor',
    author_email='benoit.suttor@imio.be',
    url='http://pypi.python.org/pypi/collective.preventactions',
    license='BSD',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Plone',
        'Products.GenericSetup>=1.8.2',
        'setuptools',
        'plone.api',
    ],
    extras_require={
        'test': [
            'plone.app.robotframework',
        ],
    },
    entry_points="""
    """,
)

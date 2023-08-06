# -*- coding: utf-8 -*- vim: et ts=8 sw=4 sts=4 si tw=79 cc=+8
"""Installer for the visaplan.kitchen package."""

from setuptools import find_packages
from setuptools import setup
# ---------------------------------------- [ destination locking ... [
import sys, os
try:  # Python 3:
    from configparser import ConfigParser
except ImportError:
    # Python 2:
    from ConfigParser import ConfigParser
# ---------------------------------------- ] ... destination locking ]

VERSION = (open('VERSION').read().strip()
           + '.dev1'  # in branches only
           )


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='visaplan.kitchen',
    # see also --> ./visaplan.kitchen.egg-info/PKG-INFO: 
    version=VERSION,
    description="A kitchen for (beautiful) soup",
    long_description=long_description,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Natural Language :: German",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
    ],
    # keywords='Python Plone',
    author='Tobias Herp',
    author_email='tobias.herp@visaplan.com',
    url='https://pypi.org/project/visaplan.kitchen',
    license='GPL version 2',
    # packages=find_packages('src', exclude=['ez_setup']),
    packages=find_packages('src'),
    namespace_packages=[
        'visaplan',
        'visaplan.kitchen',
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'beautifulsoup4',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)

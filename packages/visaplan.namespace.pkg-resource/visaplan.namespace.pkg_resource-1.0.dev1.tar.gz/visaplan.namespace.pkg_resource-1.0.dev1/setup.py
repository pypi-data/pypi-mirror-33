# -*- coding: utf-8 -*- vim: ts=8 sw=4 sts=4 et si tw=72 cc=+8
"""Installer for the visaplan.namespace.pkg_resource package.

Explicitly establishes a 'visaplan' package and ... namespace,
pkg_resource style; see
<https://packaging.python.org/guides/packaging-namespace-packages/#pkg-resources-style-namespace-packages>
and
<https://community.plone.org/t/factoring-out-packages-namespace-problem/6842>
"""

from setuptools import setup, find_packages
from pprint import pprint

VERSION = open('VERSION').read().strip()
VERSION_SUFFIX = '.dev1'  # used in branches only


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


kwargs = dict(
    name='visaplan.namespace.pkg_resource',
    # see also --> ./visaplan.namespace.pkg_resource.egg-info/PKG-INFO: 
    version=VERSION+VERSION_SUFFIX,
    description="Dummy namespace package, pgk_resource style",
    long_description=long_description,
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache Software License",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    # keywords='Python Plone',
    author='Tobias Herp',
    author_email='tobias.herp@visaplan.com',
    url='https://pypi.org/project/visaplan',
    license='GPL version 2',
    # packages=find_packages('src', exclude=['ez_setup']),
    packages=find_packages('src'),
    namespace_packages=[
        'visaplan',
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
# pprint(kwargs)
setup(**kwargs)

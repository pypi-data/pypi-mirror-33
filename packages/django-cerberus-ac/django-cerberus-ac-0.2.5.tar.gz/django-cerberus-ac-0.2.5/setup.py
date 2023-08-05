#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Setup script.

Uses setuptools.
Long description is a concatenation of README.rst and CHANGELOG.rst.
"""

from __future__ import absolute_import, print_function

import io
import re
from glob import glob
from os.path import basename, dirname, join, splitext

from setuptools import find_packages, setup


def read(*names, **kwargs):
    """Read a file in current directory."""
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


setup(
    name='django-cerberus-ac',
    version='0.2.5',
    license='ISC',
    description='Django Ontology Based Access Control Module',
    long_description='%s\n%s' % (
        re.compile('^.. start-badges.*^.. end-badges', re.M | re.S)
        .sub('', read('README.rst')),
        re.sub(':[a-z]+:`~?(.*?)`', r'``\1``', read('CHANGELOG.rst'))
    ),
    author='Mihnea Gheorghiu',
    author_email='mikigi92@gmail.com',
    url='https://github.com/Genida/django-cerberus-ac',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Operating System :: Unix',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        # 'Framework :: Django :: 1.10',
        # 'Framework :: Django :: 1.11',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities',
    ],
    keywords=[
        'django-cerberus-ac', 'access control', 'ontology-based', 'least privilege',
        'role based access control', 'django access control',
    ],
    install_requires=[
        'django-app-settings', 'django-suit-dashboard'
    ],
    entry_points={
        'archan': [
            'cerberus_ac.Privileges = cerberus_ac.plugins:Privileges'
        ]
    },
)

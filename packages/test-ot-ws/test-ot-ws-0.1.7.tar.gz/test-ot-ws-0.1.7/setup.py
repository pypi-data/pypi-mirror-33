#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Based on template found at: https://github.com/kennethreitz/setup.py
from setuptools import setup, find_packages

readme = open('README.md').read()
license = open('License.txt').read()
reqs = [i.strip() for i in open('requirements.txt').readlines() if i.strip()]
scripts = ('test-ot-ws', )

classifiers = ['Development Status :: 3 - Alpha',
               'Intended Audience :: Science/Research',
               'Intended Audience :: Developers',
               'Natural Language :: English',
               'License :: OSI Approved :: BSD License',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.5',
               'Programming Language :: Python :: 3.6',
               'Programming Language :: Python :: 3.7',
               'Topic :: Scientific/Engineering :: Bio-Informatics',
               ]
setup(
    name='test-ot-ws',
    version='0.1.7',
    description='Library for testing whether or not the Open Tree of Life web services are functioning correctly',
    long_description=readme,
    url='https://github.com/OpenTreeOfLife/test-ot-ws',
    license=license,
    author='Mark T. Holder and see CONTRIBUTORS.txt file',
    author_email='mtholder@gmail.com',
    py_modules=['otwstest'],
    install_requires=reqs,
    packages=['otwstest',
              'otwstest.schema',
              'otwstest.schema.taxonomy',
              'otwstest.schema.tnrs',
              'otwstest.taxonomy',
              'otwstest.taxonomy.taxon',
              'otwstest.taxonomy.flags',
              'otwstest.taxonomy.mrca',
              'otwstest.taxonomy.subtree',
              'otwstest.taxonomy.about',
              'otwstest.tnrs',
              ],
    classifiers=classifiers,
    include_package_data=True,
    scripts=scripts,
    zip_safe=False
)


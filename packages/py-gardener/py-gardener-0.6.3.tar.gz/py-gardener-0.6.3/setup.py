#!/usr/bin/env python
"""
Py-Gardener
----------------
Enforces best practices in python project.
Links
`````
* `github <https://github.com/loopmediagroup/py-gardener>`_
"""
import os
from setuptools import setup

setup(
    name='py-gardener',
    version='0.6.3',
    url='https://github.com/loopmediagroup/py-gardener',
    license='MIT',
    author='Lukas Siemon',
    author_email='lukas.siemon@getintheloop.ca',
    maintainer='Lukas Siemon',
    maintainer_email='lukas.siemon@getintheloop.ca',
    description='Basic Tests for python project to enforce best practices.',
    long_description=__doc__,
    packages=[x[0] for x in os.walk("py_gardener")],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'pycodestyle>=2.4.0',
        'pylint>=1.8.4',
        'pytest>=3.5.1',
        'pytest-cov>=2.5.1'
    ],
    keywords=['Python', 'Testing', 'Best Practices'],
    classifiers=[]
)

#!/usr/bin/env python

import os
from setuptools import find_packages, setup


def read(path):
    try:
        return open(path).read()
    except IOError:
        return ""

readme = read('README.rst')

doclink = """
Documentation
-------------

The full documentation can be generated with Sphinx"""

history = read('HISTORY.rst').replace('.. :changelog:', '')

requires = ["configobj>=5.0.0", 'voluptuous==0.8.4', "docopt", "paramiko"]  # during runtime

PACKAGE_PATH = os.path.abspath(os.path.join(__file__, os.pardir))

setup(
    name='darkskysync',
    version='0.2.0',
    description='Helps to access and synchronize with a remote data storage',
    long_description=readme + '\n\n' + doclink + '\n\n' + history,
    author='Joel Akeret',
    author_email='jakeret@phys.ethz.ch',
    url='http://refreweb.phys.ethz.ch/software/darkskysync/0.1.6/',
    packages=find_packages(PACKAGE_PATH, "test"),
    package_dir={'darkskysync': 'darkskysync'},
    package_data={"": ["LICENSE"],
                  'darkskysync': ['data/config.template']},
    include_package_data=True,
    install_requires=requires,
    license='MIT',
    zip_safe=False,
    keywords='darkskysync',
    entry_points={
        'console_scripts': [
            'DarkSkySync = darkskysync.DarkSkySyncCLI:main',
        ]
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        "Intended Audience :: Science/Research",
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)

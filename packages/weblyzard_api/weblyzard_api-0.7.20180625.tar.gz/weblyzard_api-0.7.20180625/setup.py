#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages
from setuptools.command import sdist

setup(
    name='weblyzard_api',
    version='0.7.20180625',
    description=' Web services for weblyzard',
    author='Albert Weichselbraun, Heinz-Peter Lang, Max Göbel and Philipp Kuntschik',
    author_email='weichselbraun@weblyzard.com',
    packages=find_packages('src/python'),
    package_dir={'': 'src/python'},
    install_requires=['eWRT>=0.9.2.2',
                      'nose',
                      'lxml',
                      'requests[security]>=2.13,<3',
                      'pytest',
                      'sparqlwrapper'],
    dependency_links=[
        'git+https://github.com/weblyzard/ewrt.git#egg=eWRT-0.9.1.12'],
    zip_safe=False,
    include_package_data=True,
    scripts=['src/python/weblyzard_api/client/openrdf/wl_upload_repository.py', ]
)

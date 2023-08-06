#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}

setup(
    name='serialbox',
    version='1.0.10',
    url='http://www.serial-lab.com',
    license='GPL',
    description='Serial Number Distribution Made Easy.',
    author='SerialLab Corp',
    author_email='slab@serial-lab.com',
    packages=find_packages(),
    package_data=get_package_data('serialbox'),
    install_requires=['django', 'djangorestframework', 'djangorestframework-csv',
                      'djangorestframework-xml', 'Markdown', 'decorator', 'six',
                      'docutils'],
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ]
)

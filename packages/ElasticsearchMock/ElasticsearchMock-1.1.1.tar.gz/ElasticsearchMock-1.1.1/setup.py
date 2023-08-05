# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

__version__ = '1.1.1'

setup(
    name='ElasticsearchMock',
    version=__version__,
    url='https://github.com/jmlw/elasticmock',
    license='MIT',
    author='Josh Wood',
    author_email='josh.m.l.wood@gmail.com',
    description='Python Elasticsearch Mock for test purposes',
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'elasticsearch>=5.0.0,<6.0.0',
        'mock==1.0.1'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)

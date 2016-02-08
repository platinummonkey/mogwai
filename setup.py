import sys
from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = open('mogwai/VERSION', 'r').readline().strip()
develop_requires = ['Sphinx==1.3.5',
    'tornado==4.3',
    'factory-boy==2.6.0',
    'gremlinclient==0.1.4',
    'newrelic==2.60.0.46',
    'nose==1.3.7',
    'pyformance==0.3.2',
    'pyparsing==2.1.0',
    'six==1.10.0',
    'sphinx-rtd-theme==0.1.9',
    'tox==2.3.1',
    'Twisted==15.5.0',
    'watchdog==0.8.3']

long_desc = """
mogwai is an Object-Graph Mapper (OGM) for Python

`Documentation <https://mogwai.readthedocs.org/en/latest/>`_

`Report a Bug <https://bitbucket.org/wellaware/mogwai/issues>`_
"""

setup(
    name='mogwai',
    version=version,
    description='Titan Object-Graph Mapper (OGM)',
    dependency_links=['https://bitbucket.org/wellaware/mogwai/archive/{0}.tar.gz#egg=mogwai-{0}'.format(version)],
    long_description=long_desc,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Environment :: Other Environment",
        "Environment :: Plugins",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='cassandra,titan,ogm,mogwai,thunderdome',
    install_requires=['pyparsing>=2.0.2',
                      'gremlinclient>=0.1.4',
                      'six>=1.10.0',
                      'factory-boy>=2.6.0',
                      'pyformance>=0.3.2',
                      'Twisted>=15.50'],
    extras_require={
        'develop': develop_requires,
        'newrelic': ['newrelic>=2.60.0.46'],
        'docs': ['Sphinx>=1.2.2', 'sphinx-rtd-theme>=0.1.6', 'watchdog>=0.8.3', 'newrelic>=2.60.0.46']
    },
    test_suite='nose.collector',
    tests_require=develop_requires,
    author='Cody Lee',
    author_email='codylee@wellaware.us',
    maintainer='Cody Lee',
    maintainer_email='codylee@wellaware.us',
    url='https://bitbucket.org/wellaware/mogwai',
    license='Apache Software License 2.0',
    packages=find_packages(),
    include_package_data=True,
)

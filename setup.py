import sys
from setuptools import setup, find_packages

#next time:
#python setup.py register
#python setup.py sdist upload

version = open('mogwai/VERSION', 'r').readline().strip()

long_desc = """
mogwai is an Object-Graph Mapper (OGM) for Python
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
        "Programming Language :: Python :: Implementation",
        "Topic :: Database",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords='cassandra,titan,ogm,mogwai,thunderdome',
    install_requires=['pyparsing>=1.5.7',
                      'rexpro>=0.1.1',
                      'six>=1.5.2',
                      'argparse>=1.2.1',
                      'factory-boy>=2.3.1',
                      'pyformance==0.2.4'],
    extras_require={
        'develop': ['nose==1.3.0', 'coverage==3.7.1', 'pyformance==0.2.4', 'tox==1.7.1'],
        'newrelic': ['newrelic==2.18.1.15']
    },
    test_suite='nose.collector',
    tests_require=['nose==1.3.0', 'coverage==3.7.1', 'tox==1.7.1'],
    #setup_requires=['nose==1.3.0', 'coverage==3.7.1', 'pyformance==0.2.4', 'tox==1.7.1'],
    #scripts=['run_converage.sh', 'run_tests.sh'],
    author='Cody Lee',
    author_email='codylee@wellaware.us',
    maintainer='Cody Lee',
    maintainer_email='codylee@wellaware.us',
    url='https://bitbucket.org/wellaware/mogwai',
    license='Apache Software License 2.0',
    packages=find_packages(),
    include_package_data=True,
)

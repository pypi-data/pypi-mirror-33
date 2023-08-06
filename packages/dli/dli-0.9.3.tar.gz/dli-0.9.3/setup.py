"""Packaging settings."""

from codecs import open
from os.path import abspath, dirname, join

from setuptools import find_packages
from setuptools import setup

import dli

this_dir = abspath(dirname(__file__))
# with open(join(this_dir, 'README.rst'), encoding='utf-8') as file:
#     long_description = file.read()


setup(
    name='dli',
    version=dli.__version__,
    description='Data Lake command line Interface.',
    # long_description=long_description,
    url='https://git.mdevlab.com/data-lake/data-lake-sdk',
    author='Ashic Mahtab',
    author_email='ashic@heartysoft.com',
    license='MOZ-2',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='cli, datalake, data, lake',
    packages=find_packages(exclude=['docs', 'tests*']),
    install_requires=[
        'docopt==0.6.2',
        'pyyaml==3.12',
        'requests==2.18.4',
        's3fs==0.1.5',
        'pypermedia==0.4.2',
        'future==0.16.0',
        'pytest==3.5.0',
        'urllib3==1.22',
        'pyjwt==1.6.4',
        'six==1.11.0',
        'pathlib2==2.3.2'
    ],
    setup_requires=['pytest==3.5.0', 'urllib3'],
    tests_require=[
        'mock',
        'httpretty',
        'backports.tempfile'
    ],
    extras_require={
        'test': [
            'httppretty',
            'coverage',
            'pytest==3.5.0',
            'pytest-cov',
        ]
    },
    entry_points={
        'console_scripts': [
            'dli=dli.dli:main',
        ],
    },
)

# -*- coding: utf-8 -*-
import sys
from setuptools import setup, find_packages

classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: Apache Software License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.6",
    "Topic :: Database",
    "Topic :: Software Development",
    "Topic :: Software Development :: Testing",
]

install_requires = ['PyYAML', 'testing.common.database >= 2.0.0']
if sys.version_info < (2, 7):
    install_requires.append('unittest2')


setup(
    name='testing.elasticsearch6',
    version='1.1.0',
    description='automatically setups a elasticsearch instance in a temporary '
                'directory, and destroys it after testing',
    long_description=open('README.rst').read(),
    classifiers=classifiers,
    keywords=[],
    maintainer="Criteo Observability Team",
    maintainer_email="sre-observability@criteo.com",
    url='https://github.com/criteo-forks/testing.elasticsearch',
    license='Apache License 2.0',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    package_data={'': ['buildout.cfg']},
    include_package_data=True,
    install_requires=install_requires,
    extras_require=dict(
        testing=[
            'nose',
        ],
    ),
    test_suite='nose.collector',
    namespace_packages=['testing'],
)

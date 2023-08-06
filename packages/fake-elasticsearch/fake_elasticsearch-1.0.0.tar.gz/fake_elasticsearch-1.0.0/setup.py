# -*- coding: utf8 -*-

from setuptools import setup, find_packages

from fake_elasticsearch import __version__


setup(
    name='fake_elasticsearch',
    description='Fake elasticsearch python client.',
    version=__version__,
    author='fatelei',
    author_email='fatelei@gmail.com',
    packages=find_packages(
        where='.',
        exclude=('tests',)
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: System :: Logging"
    ],
    license="BSD License",
    install_requires=[
        'elasticsearch'
    ]
)

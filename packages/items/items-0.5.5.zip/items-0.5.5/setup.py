#!/usr/bin/env python

from setuptools import setup
from codecs import open


def lines(text):
    """
    Returns each non-blank line in text enclosed in a list.
    See http://pypi.python.org/pypi/textdata for more sophisticated version.
    """
    return [l.strip() for l in text.strip().splitlines() if l.strip()]


setup(
    name='items',
    version='0.5.5',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Attribute accessible dicts and collections thereof',
    long_description=open('README.rst', encoding='utf-8').read(),
    url='https://bitbucket.org/jeunice/items',
    license='Apache License 2.0',
    packages=['items'],
    setup_requires=[],
    install_requires=open('requirements.txt').read().splitlines(),
    tests_require=['tox', 'pytest', 'pytest-cov', 'coverage'],
    test_suite="test",
    zip_safe=False,  # it really is, but this will prevent weirdness
    keywords='attributes attrs',
    classifiers=lines("""
        Development Status :: 3 - Alpha
        Operating System :: OS Independent
        License :: OSI Approved :: Apache Software License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.5
        Programming Language :: Python :: 3.6
        Programming Language :: Python :: 3.7
        Programming Language :: Python :: Implementation :: CPython
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)

#!/usr/bin/env python

import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.rst')) as f:
    README = f.read()

REQUIREMENTS = [
	'irc'
]

setup(
    name='teambot',
    version='0.1.0',
    description='teambot',
    long_description=README,
    author='Robert Miles',
    author_email='khuxkm@tilde.team',
    url='https://git.tilde.team/meta/teambot',
    license="MIT",
    install_requires=REQUIREMENTS,
    keywords=["irc","bot"],
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
    ],
    entry_points={
        'console_scripts': ['teambot = teambot.console:main']
    },
)

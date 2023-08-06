#!/usr/bin/env python
"""Setup package"""

import setuptools

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setuptools.setup(
    name="joca",
    version="1.1.2",
    author="Bryce McNab",
    author_email="brycemcnab@pm.me",
    description="Sync project lead with ical (for on call assignees)",
    long_description=long_description,
    url="https://www,github.com/betsythefc/joca",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    scripts=[
        'bin/joca',
    ],
    install_requires=[
        "requests",
        "jira",
        "icalendar",
        "jsonschema",
        "json",
        "sys",
        "re",
        "datetime",
        "time",
        "logging"
    ]
) 

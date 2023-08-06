#!/usr/bin/env python
"""
    JOCA -- Jira On Call Assignee -- Change project lead based on an ical event.
    Copyright (C) 2018 Bryce McNab

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import setuptools

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setuptools.setup(
    name="joca",
    version="1.3.6",
    author="Bryce McNab",
    author_email="brycemcnab@pm.me",
    description="Sync project lead with ical (for on call assignees)",
    long_description=long_description,
    url="https://www,github.com/betsythefc/joca",
    packages=setuptools.find_packages(),
    include_package_data=True,
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
    ]
) 

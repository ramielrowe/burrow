#!/usr/bin/env python

from setuptools import setup

import burrow

description = "Python Client For Nest Mobile API"

setup(
    name="burrow",
    version=burrow.VERSION,
    author="Andrew Melton",
    author_email="ramielrowe@gmail.com",
    description=description,
    long_description=description,
    license="Apache",
    keywords="nest thermostat",
    url="https://github.com/ramielrowe/burrow",
    py_modules=['burrow'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
    ],
    setup_requires=(
        'requests',
    ),
    install_requires=(
        'requests',
    ),
    entry_points={
        'console_scripts': ['burrow=burrow:main'],
    }

)

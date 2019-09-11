#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")
_init_file = "locust_extensions/__init__.py"
with open(_init_file, "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

setup(
    name="locust-extensions",
    version=version,
    description="Useful extensions for Locust",
    long_description="""""",
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    keywords="",
    author="Lars Holmberg",
    author_email="lars.holmberg@svenskaspel.se",
    url="https://github.com/SvenskaSpel/locust-extensions",
    license="Apache-2.0",
    packages=find_packages(exclude=["examples"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "locustio@git+https://github.com/cyberw/locust.git@allow-samples-with-None-response-time",
        "psycogreen",
        "psycopg2",
    ],
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name
import ast
import re

from setuptools import find_packages, setup

_version_re = re.compile(r"__version__\s+=\s+(.*)")
_init_file = "locust_plugins/__init__.py"
with open(_init_file, "rb") as f:
    version = str(ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1)))

setup(
    name="locust-plugins",
    version=version,
    description="Useful plugins/extensions for Locust",
    long_description="""https://github.com/SvenskaSpel/locust-plugins""",
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    python_requires=">=3.7, <4",
    keywords="",
    author="Lars Holmberg",
    url="https://github.com/SvenskaSpel/locust-plugins",
    license="Apache-2.0",
    packages=find_packages(exclude=["examples"]),
    include_package_data=True,
    package_data={"locust_plugins": ["py.typed"]},
    zip_safe=False,
    install_requires=[
        "locust>=2.4.0",
        "psycogreen",
        "psycopg2-binary",
        "websocket-client",
        "python-dateutil",
        "pymongo",
        "confluent-kafka",
        "selenium>=4.0.0",
        "lxml",
        "opencensus-ext-azure",
        "paho-mqtt>=1.5.0",
    ],
)

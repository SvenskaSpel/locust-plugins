#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from setuptools import find_packages, setup

setup(
    name="locust-plugins",
    description="Useful plugins/extensions for Locust",
    long_description="""https://github.com/SvenskaSpel/locust-plugins""",
    classifiers=[
        "Topic :: Software Development :: Testing :: Traffic Generation",
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
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
        "playwright",
        "locust>=2.14.0",
        "playwright>=1.34.0",
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
        "typing-extensions",
    ],
    scripts=["bin/locust-compose"],
    use_scm_version={
        "write_to": "locust_plugins/_version.py",
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
)

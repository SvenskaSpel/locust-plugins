#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=invalid-name

from setuptools import find_packages, setup

extras = {
    "websocket": ["websocket-client"],
    "playwright": ["playwright>=1.40.0"],
    "dashboards": ["psycogreen", "psycopg2-binary"],
    "kafka": ["confluent-kafka"],
    "mongo": ["pymongo"],
    "mqtt": ["paho-mqtt>=2.1.0"],
    "appinsights": ["opencensus-ext-azure"],
    "resource": ["lxml"],
    "boto3": ["boto3"],
}

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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    python_requires=">=3.8, <4",
    keywords="",
    author="Lars Holmberg",
    url="https://github.com/SvenskaSpel/locust-plugins",
    license="Apache-2.0",
    packages=find_packages(exclude=["examples"]),
    include_package_data=True,
    package_data={"locust_plugins": ["py.typed"]},
    zip_safe=False,
    install_requires=[
        "locust>=2.20.0",
        "typing-extensions",
    ],
    extras_require={
        **extras,
        "all": list(extras.values()),
        "webdriver": ["selenium>=4.0.0"],  # warning: this installs trio which is incompatible with playwright
    },
    scripts=["bin/locust-compose"],
    use_scm_version={
        "write_to": "locust_plugins/_version.py",
        "local_scheme": "no-local-version",
    },
    setup_requires=["setuptools_scm"],
)

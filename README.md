# Locust Plugins

[![Build Status](https://github.com/SvenskaSpel/locust-plugins/workflows/Tests/badge.svg)](https://github.com/SvenskaSpel/locust-plugins/actions?query=workflow%3ATests)
[![license](https://img.shields.io/github/license/SvenskaSpel/locust-plugins.svg)](https://github.com/SvenskaSpel/locust-plugins/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/locust-plugins.svg)](https://pypi.org/project/locust-plugins/)
[![PyPI](https://img.shields.io/pypi/pyversions/locust-plugins.svg)](https://pypi.org/project/locust-plugins/)
[![GitHub contributors](https://img.shields.io/github/contributors/SvenskaSpel/locust-plugins.svg)](https://github.com/SvenskaSpel/locust-plugins/graphs/contributors)

The purpose of this project is to gather a curated set of plugins/extensions for [Locust](https://github.com/locustio/locust). 

Locust itself is a "bare bones" load generation tool (compared to for example JMeter or Gatling) and it is left to the user to build even basic functionality (like reading test data from a database, using non-HTTP protocols, etc). This keeps Locust lean and mean, but forcing everyone to reinvent the wheel is not good either.

So I decided to publish my own plugins and hope that others (maybe you?) will contribute their solutions to common Locust use cases.

Having this separate from "Locust core" allows the plugins to evolve faster (at the expense of being less mature), and avoids bloating Locust with functionality you might not be interested in.

# Installation

```
pip install locust-plugins
```

Then just `import locust_plugins` in your locustfile and use whatever plugins you need (see below)

# Configuration

Most settings are configured from code, but some are exposed as command line arguments. You can list them by using Locust's regular --help argument:

```
locust -f any-locustfile-that-imports-locust_plugins.py --help
```

# Plugins

## Listeners 
- Listen to events and log things
    - Timescale: Log and graph results using TimescaleDB and Grafana dashboards ([readme](locust_plugins/dashboards/), [source](locust_plugins/listeners.py))
    - Print: Prints prints every request to standard out with response time etc ([source](locust_plugins/listeners.py))
    - Jmeter: Writes a jmeter-like output file ([example](examples/jmeter_listener_example.py), [source](locust_plugins/jmeter_listener.py))
    - ApplicationInsights: Writes the test logs to Azure Application Insights ([example](examples/appinsights_listener_ex.py), [source](locust_plugins/appinsights_listener.py))
    - RescheduleTaskOnFail / ExitOnFail / StopUserOnFail: Perform actions when a request fails ([source](locust_plugins/listeners.py))

## Users
- New protocols ([source](locust_plugins/users/))
    - Playwright ([example](examples/playwright_ex.py))
    - WebSockets/SocketIO ([example](examples/socketio_ex.py))
    - Selenium/Webdriver ([example](examples/webdriver_ex.py)) 
    - HTTP users that load html page resources ([example](examples/embedded_resource_manager_ex.py))
    - Kafka ([example](examples/kafka_ex.py))
    - MqttUser ([example](examples/mqtt_ex.py))
    - RestUser has been removed, as it is [now part of locust core](https://docs.locust.io/en/stable/increase-performance.html#rest)!

## Readers 
- Provide ways to get test data into your tests
    - CSV ([example](examples/csvreader_ex.py), [source](locust_plugins/csvreader.py))
    - MongoDB ([example](examples/mongoreader_ex.py), [source](locust_plugins/mongoreader.py))

## Wait time 
- Custom wait time functions ([example](examples/constant_total_ips_ex.py), [source](locust_plugins/wait_time.py))

## Debug 
- Support for running a single User in the debugger (moved to [locust core](https://docs.locust.io/en/latest/running-in-debugger.html)!)

## Transaction manager
- Support for logging transactions (aggregating multiple requests or other actions) ([example](examples/transaction_example.py), [source](locust_plugins/transaction_manager.py))

## Connection Pool
- Allows users to occupy more ports when running tests, useful for dealing with strange behaviour from load balancers in low user count high throughput scenarios. scenarios. ([example](examples/connection_pool_ex.py), [source](locust_plugins/connection_pools.py))

## Command line options 
- Additional locust command line options provided ([examples](examples/cmd_line_examples.sh), [source](locust_plugins/__init__.py))
    - Iteration limit (`-i`), stops Locust after a certain number of task iterations
    - Checks (`--check-rps`, `--check-fail-ratio`, `--check-avg-response-time`), gives an error return code if certain conditions are not met
    - [Dashboards](locust_plugins/dashboards/) (`--timescale`, `--grafana-url`, `--pghost`, ...)

# Further examples

Have a look at the [example locustfiles](examples/) to learn how to use the plugins.

# locust-swarm

These plugins work well together with [locust-swarm](https://github.com/SvenskaSpel/locust-swarm)

# Contributions

Contributions are very welcome! 😁

For guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md)

## License

Copyright 2019 AB SvenskaSpel

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

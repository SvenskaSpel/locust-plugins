# Locust Plugins

[![Build Status](https://travis-ci.com/SvenskaSpel/locust-plugins.svg?branch=master)](https://travis-ci.com/SvenskaSpel/locust-plugins)
[![license](https://img.shields.io/github/license/SvenskaSpel/locust-plugins.svg)](https://github.com/SvenskaSpel/locust-plugins/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/locust-plugins.svg)](https://pypi.org/project/locust-plugins/)
[![PyPI](https://img.shields.io/pypi/pyversions/locust-plugins.svg)](https://pypi.org/project/locust-plugins/)
[![GitHub contributors](https://img.shields.io/github/contributors/SvenskaSpel/locust-plugins.svg)](https://github.com/SvenskaSpel/locust-plugins/graphs/contributors)

The purpose of this project is to gather a curated set of plugins/extensions for [Locust](https://github.com/locustio/locust). 

Locust itself is a "bare bones" load generation tool (compared to for example JMeter or Gatling) and it is left to the user to build even basic functionality (like reading test data from a database, limiting the request rate to a certain value, etc). Forcing everyone to reinvent the wheel is a big waste, and makes using Locust harder than it needs to be.

So I decided to publish my own plugins and hope that others (maybe you?) will contribute their solutions to common Locust use cases.

Having this separate from "Locust core" allows the plugins to evolve faster (at the expense of being less mature), and avoids bloating Locust with functionality you might not be interested in.

There are a couple of plugin types:

## Listeners 
- Listen to events and log things
    - Timescale: Log and graph results using TimescaleDB and Grafana ([example](examples/timescale_listener_ex.py), [source](locust_plugins/listeners.py))
    - Print: Prints prints every request to standard out with response time etc ([source](locust_plugins/listeners.py))
    - Jmeter: Writes a jmeter-like output file ([example](examples/jmeter_listener_example.py), [source](locust_plugins/jmeter_listener.py))
    - ApplicationInsights: Writes the test logs to Azure Application Insights ([example](examples/appinsights_listener_ex.py), [source](locust_plugins/appinsights_listener.py))
    - RescheduleTaskOnFail / ExitOnFail / StopUserOnFail: Perform actions when a request fails ([source](locust_plugins/listeners.py))

## Users
- New protocols ([source](locust_plugins/users/))
    - WebSockets/SocketIO ([example](examples/socketio_ex.py))
    - Selenium/Webdriver ([example](examples/webdriver_ex.py))
    - HTTP users that load html page resources ([example](examples/embedded_resource_manager_ex.py))
    - Kafka ([example](examples/kafka_ex.py))
    - RestUser ([example](examples/rest_ex.py))
    - MqttUser ([example](examples/mqtt_ex.py))

## Readers 
- Provide ways to get test data into your tests
    - CSV ([example](examples/csvreader_ex.py), [source](locust_plugins/csvreader.py))
    - MongoDB ([example](examples/mongoreader_ex.py), [source](locust_plugins/mongoreader.py))

## Wait time 
- Custom wait time functions ([example](examples/constant_total_ips_ex.py), [source](locust_plugins/wait_time.py))

## Debug 
- Support for running a single User in the debugger ([example](examples/debug_ex.py), [source](locust_plugins/debug.py))

## Transaction manager
- Support for logging transactions (aggregating multiple requests or other actions) ([example](examples/transaction_example.py), [source](locust_plugins/transaction_manager.py))

## Command line options 
- Additional locust command line options provided ([examples](examples/cmd_line_examples.sh), [source](locust_plugins/__init__.py))
    - Iteration limit (`-i`), stops Locust after a certain number of task iterations
    - Checks (`--check-rps`, `--check-fail-ratio`, `--check-avg-response-time`), gives an error return code if certain conditions are not met

# Further examples

Have a look at the [example locustfiles](examples/) to learn how to use the plugins.

# locust-swarm

These plugins work well together with [locust-swarm](https://github.com/SvenskaSpel/locust-swarm)


# Installation

```
pip install locust-plugins
```

# Configuration

For configuration help, run `locust -f locustfile-that-imports-locust_plugins.py --help`. Some environment variables need to be set (mainly for Postgres, if you want to run the Timescale listener), but you should get clear error messages if one is missing.

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

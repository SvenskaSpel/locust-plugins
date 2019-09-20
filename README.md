# Locust Plugins

This is a set of plugins/extensions for [locust](https://github.com/locustio/locust).

The plugins are grouped by type:
* [listeners](locust_plugins/listeners.py) (request logging & graphing)
* [locusts](locust_plugins/locusts.py) (new protocols like websockets & selenium/webdriver)
* [readers](locust_plugins/readers.py) (ways to get test data into your tests)
* [tasksets](locust_plugins/tasksets.py) (different ways to run your tests, like RPS limiting)
* [utils](locust_plugins/utils.py) (other stuff, like vs code debugging support)

You can also have a look at the [example locustfiles](examples/) to learn how to use the plugins.

These plugins work well together with [locust-swarm](https://github.com/SvenskaSpel/locust-swarm), but they work standalone too.

# Installation

```
pip install locust-plugins
```

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
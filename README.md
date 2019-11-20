# Locust Plugins

The purpose of this project is to gather a curated set of plugins/extensions for [Locust](https://github.com/locustio/locust). 

Locust itself is a "bare bones" load generation tool (compared to for example JMeter or Gatling) and it is left to the user to build even basic functionality (like reading test data from a database, limiting the request rate to a certain value, etc). Forcing everyone to reinvent the wheel is a big waste, and makes using Locust harder than it needs to be.

So I decided to publish my own plugins and hope that others (maybe you?) will contribute their solutions to common Locust use cases.

Having this separate from "Locust core" allows the plugins to evolve faster (at the expense of being less mature), and avoids bloating Locust with functionality you might not be interested in.

The plugins are grouped by type:
* [listeners](locust_plugins/listeners.py) (request logging & graphing)
* [locusts](locust_plugins/locusts.py) (new protocols like websockets & selenium/webdriver)
* [readers](locust_plugins/readers.py) (ways to get test data into your tests)
* [tasksets](locust_plugins/tasksets.py) (support for RPS limiting, and maybe other task sets in the future)
* [utils](locust_plugins/utils.py) (other stuff, like VS Code debugging support)

You can also have a look at the [example locustfiles](examples/) to learn how to use the plugins.

These plugins work well together with [locust-swarm](https://github.com/SvenskaSpel/locust-swarm)


# Installation

```
pip install locust-plugins
```

# Configuration

Configuration is mostly done through environment variables. You will get an exception if one is missing, and they should either be self-explanatory, or explained in the code where they are used. I recommend setting them permanently in your bash profile, so you dont have to set them every time or make your command line super-long.

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
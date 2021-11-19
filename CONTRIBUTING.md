Contributing Guidelines
=======================

If you want to talk about a contribution before you start writing code & making a pull request, please [file an issue](https://github.com/SvenskaSpel/locust-plugins/issues/new). You can also find me (cyberwiz) semi-regularly on the official locust [slack](https://locustio.slack.com).

In order to maintain a good level of quality, please ensure that your code:

* Is formatted using black (https://github.com/psf/black)

* Passes linting with pylint (https://www.pylint.org/)

* Has relevant examples [here](examples/)

---
## environment setup

This project has a dev container definition - https://code.visualstudio.com/docs/remote/containers#

If you have Docker and visual studio code installed all you need to do is open the repository in vs code and select "re-open in container" in the popup that appears in the bottom right. Dependencies and plugins will be automatically handled.


### Tusk runner

The development image has some quality of life scripts baked into it

1. running `tusk format` Will run the black formatter on examples/ and locust_plugins/

2. `tusk pylint` will run pylint against on examples/ and locust_plugins/

3. `tusk test` will run the tox test suite in the 3.9 environment
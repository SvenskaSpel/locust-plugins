# har2locust

This is a fork of [har2py](https://github.com/S1M0N38/har2py), modified to generate a locustfile 
instead of a basic Python file.

---

When browsing the web with the Developer Tools open you can record the Network
Activities (requests perform by your browser & responses you get from servers).
Then you can export all these data into an [HAR](https://en.wikipedia.org/wiki/HAR_(file_format))
file (Http ARchive). With **har2locust** you can convert HAR file into valid python
code that reproduce the requests perform by your browser.

## Installation

Just a simple pip install, i.e. `python3 -m pip install har2locust`

## Usage

1. Navigate the web with your browser while recording your activity. Then save the
data in HAR file. Here is an example with Chrome Devs Tools
![har.gif](https://github.com/S1M0N38/har2py/blob/main/har.gif?raw=true)

2. Run `har2locust myharfile.har > locustfile.py`.

```

> har2locust -h

usage: har2locust [-h] [-t TEMPLATE] [-f FILTERS] input

positional arguments:
  input                 har input file

optional arguments:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        jinja2 template used to generate locustfile code. Default to locust.
  -f FILTERS, --filters FILTERS
                        commas value separeted string of the resource type you want to
                        include in py generated code. Supported type are `xhr`,
                        `script`, `stylesheet`, `image`, `font`, `document`, `other`.
                        Default to xhr,document,other.

```
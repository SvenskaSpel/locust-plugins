# har2locust

When browsing the web with the Developer Tools open you can record the Network
Activities (requests perform by your browser & responses you get from servers).
Then you can export all these data into an [HAR](https://en.wikipedia.org/wiki/HAR_(file_format))
file (Http ARchive). With **har2locust** you can convert HAR file into valid python
code that reproduce the requests perform by your browser.

har2locust builds upon [har2py](https://github.com/S1M0N38/har2py), modified to generate a locustfile 
instead of a basic Python file.

Note: It is currently in early beta. It mostly works, but there may be changes to behaviour 
and interface without notice. If you encounter an issue, PRs are very welcome.

## Installation

har2locust is installed together with locust-plugins (`pip install locust-plugins`)

## Usage

1. Navigate the web with your browser while recording your activity. Then save the
data in HAR file. Here is an example with Chrome Devs Tools
![har.gif](https://github.com/S1M0N38/har2py/blob/main/har.gif?raw=true)

2. Run `har2locust myharfile.har > locustfile.py`.

```

> har2locust -h

usage: har2locust [-h] [-t TEMPLATE] [-f FILTERS] [--version] input

positional arguments:
  input                 har input file

options:
  -h, --help            show this help message and exit
  -t TEMPLATE, --template TEMPLATE
                        jinja2 template used to generate locustfile. Default to locust.
  -f FILTERS, --filters FILTERS
                        commas value separeted string of the resource type you want to include in py generated code. Supported type are `xhr`, `script`, `stylesheet`, `image`, `font`, `document`, `other`. Default to xhr,document,other.
  --version, -V         show program's version number and exit

```

3. har2locust also reads two files, .urlignore and .headerignore (from your current directory).
Populate them with regexes to filter any unwanted requests or headers from your recordings. 
Some headers are always ignored (cookie, content-length and chrome's "fake" headers)
Here are some examples: [.urlignore](https://github.com/SvenskaSpel/locust-plugins/tree/master/locust_plugins/har2locust/.urlignore), 
[.headerignore](https://github.com/SvenskaSpel/locust-plugins/tree/master/locust_plugins/har2locust/.headerignore)

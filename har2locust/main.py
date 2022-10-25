import argparse
import json
import logging
import pathlib
import subprocess

import re
import jinja2
from typing import List
from setuptools_scm import get_version


def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "input",
        action="store",
        help="har input file",
    )
    parser.add_argument(
        "-t",
        "--template",
        action="store",
        default="locust",
        type=str,
        help=("jinja2 template used to generate locustfile. " "Default to locust. "),
    )
    parser.add_argument(
        "-f",
        "--filters",
        action="store",
        default="xhr,document,other",
        type=str,
        help=(
            "commas value separeted string of the resource type you want to "
            "include in py generated code. Supported type are `xhr`, "
            "`script`, `stylesheet`, `image`, `font`, `document`, `other`. "
            "Default to xhr,document,other."
        ),
    )

    try:
        version = get_version(root="..", relative_to=__file__, local_scheme="no-local-version")
    except LookupError:
        # meh. probably we are running in a github action.
        version = "unknown"

    parser.add_argument(
        "--version",
        "-V",
        action="version",
        version=f"%(prog)s {version}",
    )
    args = parser.parse_args()

    main(
        args.input,
        resource_type=args.filters.split(","),
        template_name=args.template + ".jinja2",
    )


def main(
    har_file: str,
    resource_type=["xhr", "document", "other"],
    template_dir=pathlib.Path(__file__).parents[0],
    template_name="locust.jinja2",
):
    """Load .har file and produce .py

    Args:
        har_file (str): path to the input har file.
        resource_type (list): list of resource type to include in the python
            generated code. Supported type are `xhr`, `script`, `stylesheet`,
            `image`, `font`, `document`, `other`.
            Default to ['xhr', 'document', 'other'].
        template_dir (str): path where are store the jinja2 template.
            Default to `pathlib.Path(__file__).parents[0]`.
        template_name (str): name of the jinja2 template used by rendering.
            Default to 'locust.jinja2'.
    """

    har_path = pathlib.Path(har_file)

    with open(har_path, encoding="utf8", errors="ignore") as f:
        har = json.load(f)
    logging.debug(f"load {har_path}")

    urlignore_file = pathlib.Path(".urlignore")
    url_filters = []
    if urlignore_file.is_file():
        with open(urlignore_file) as f:
            url_filters = f.readlines()
            url_filters = [line.rstrip() for line in url_filters]

    headerignore_path = pathlib.Path(".headerignore")
    header_filters = []
    if headerignore_path.is_file():
        with open(headerignore_path) as f:
            header_filters = f.readlines()
            header_filters = [line.rstrip() for line in header_filters]

    # always filter these, because they will be added by locust automatically
    header_filters.extend(["^cookie", "^content-length", "^:"])

    har = preprocessing(
        har,
        resource_type=resource_type,
        url_filters=url_filters,
        header_filters=header_filters,
    )
    py = rendering(har, template_dir=template_dir, template_name=template_name)

    print(py)


def preprocessing(
    har: dict,
    resource_type=["xhr", "document", "other"],
    url_filters: List[re.Pattern] = [],
    header_filters: List[re.Pattern] = [],
) -> dict:
    """Scan the har dict for common headers and cookies and group them into
    session headers and session cookies.

    In doing sorequest and reponse variables  are organized in a useful format:
    from [[{'name': key, 'value': value}, ...], ...] list of list of dict
    to   [{(key, value), ...}, ...] list of set of tuple.
    Moreover requests can be filter by resource type.

    Args:
        har (dict): the dict obtain by parsing har file with json
        resource_type (list): list of resource type to include in the python
            generated code. Supported type are `xhr`, `script`, `stylesheet`,
            `image`, `font`, `document`, `other`.
            Default to ['xhr', 'document', 'other'].

    Returns:
        dict: new har dict structured in the following way:
        ```python
        {
            'session': {
                'cookies': [{key, value}, {key, value}, ...],
                'headers': [{key, value}, {key, value}, ...],
            },

            'requests: [
                {
                    # request url without params
                    'url': urls[0],
                    # request method (lowercase): get, post, put, option, ...
                    'method': methods[0],
                    # headers for the specific requests
                    'headers': headers[0] - session['headers'],
                    # cookies for the specific requests
                    'cookies': cookies[0] - session['cookies'],
                    # requests parameters
                    'params': params[0],
                },
                ...
            ],

            response: [
                {
                    #
                    'url': urls[0],
                    # request method (lowercase): get, post, put, option, ...
                    'method': methods[0],
                    # headers for the specific requests
                    'headers': headers[0] - session['headers'],
                    # cookies for the specific requests
                    'cookies': cookies[0] - session['cookies'],
                    # requests parameters
                    'params': params[0],
                },
                ...
            ],

            resources_types: ['document', 'xhr', 'xhr', 'script', ...],
        }

        ```
    """
    supported_resource_type = {
        "xhr",
        "script",
        "stylesheet",
        "image",
        "font",
        "document",
        "other",
    }
    if unsupported := set(resource_type) - supported_resource_type:
        raise NotImplementedError(f"{unsupported} resource types are not supported")

    har_version = har["log"]["version"]
    logging.debug(f'log version is "{har_version}"')
    if har_version != "1.2":
        logging.warning(f"Untested har version {har_version}")

    pages = har["log"]["pages"]
    logging.debug(f"found {len(pages)} pages")

    entries = har["log"]["entries"]
    logging.debug(f"found {len(entries)} entries")

    # filtering entries
    entries = [
        e
        for e in har["log"]["entries"]
        if e["_resourceType"] in resource_type and not any(re.search(r, e["request"]["url"]) for r in url_filters)
    ]
    logging.debug(f"resource type allowed {resource_type}")
    logging.debug(f"{len(entries)} entries filter by resource_type")

    # organize request variable in a useful format
    # [[{'name': key, 'value': value}, ...], ...] list of list of dict ->
    # [{(key, value), ...}, ...] list of set of tuple
    urls, methods, headers_req, cookies_req, post_datas = [], [], [], [], []
    headers_res, cookies_res = [], []
    for e in entries:
        req = e["request"]
        urls.append(req["url"])
        methods.append(req["method"].lower())
        headers_req.append(
            {
                (h["name"], h["value"])
                for h in req["headers"]
                if not any(re.search(r, h["name"]) for r in header_filters)
            }
        )
        cookies_req.append({(c["name"], c["value"]) for c in req["cookies"]})
        post_datas.append(req["postData"]["text"] if "postData" in req else None)
        res = e["response"]
        headers_res.append({(h["name"], h["value"]) for h in res["headers"]})
        cookies_res.append({(c["name"], c["value"]) for c in res["cookies"]})

    # inside session dict are collect all varibles common to all requests
    session = {
        "name": "s",  # name of the Session() object
        "headers": set.intersection(*headers_req),
        "cookies": set.intersection(*cookies_req),
    }

    # requests is a list of dictionary with value specific to single requests
    requests = [
        {
            "url": urls[i],
            "method": methods[i],
            "headers": headers_req[i] - session["headers"],
            "cookies": cookies_req[i] - session["cookies"],
            # "params": params[i],
            "post_data": post_datas[i],
        }
        for i, e in enumerate(entries)
    ]

    responses = [
        {
            "status": e["response"]["status"],
            "headers": headers_res[i],
            "cookies": cookies_res[i],
            "redirect_url": e["response"]["redirectURL"],
            "content": e["response"]["content"],
        }
        for i, e in enumerate(entries)
    ]

    resources_types = [e["_resourceType"] for e in entries]

    logging.debug("preprocessed har dict")

    return {
        "session": session,
        "requests": requests,
        "responses": responses,
        "resources_types": resources_types,
    }


def rendering(
    har: dict,
    template_dir: str = pathlib.Path(__file__).parents[0],
    template_name: str = "locust.jinja2",
):
    """Generate valid python code from preprocessed har using jinja2 template.

    Args:
        har (dict): preprocessed har dict
        template_dir (str): path where are store the jinja2 template.
            Default to `pathlib.Path(__file__).parents[0]`.
        template_name (str): name of the jinja2 template used by rendering.
            Default to 'locust.jinja2'.

    Returns:
        str: generated python code
    """
    # check for the correctness of the har structure
    if set(har) != {"session", "requests", "responses", "resources_types"}:
        raise ValueError("har dict has wrong format. Must be first preprocessed with preprocessing(har).")

    env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))
    template = env.get_template(template_name)
    logging.debug(f'render har with "{template.name}" template')

    py = template.render(
        session=har["session"],
        requests=har["requests"],
        responses=har["responses"],
        resources_types=har["resources_types"],
    )

    p = subprocess.Popen(["black", "-q", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    assert p.stdin  # keep linter happy
    p.stdin.write(py)
    stdout, _stderr = p.communicate()
    assert not p.returncode, "Black failed to format the output - perhaps your template is broken?"

    # for some reason the subprocess returns an extra newline, get rid of that
    return stdout[:-1]

import logging
import re
from locust import HttpUser
from locust.contrib.fasthttp import FastHttpUser
from lxml import html, etree


class EmbeddedResourceManager:
    """
    provides features for finding and managing resources embedded in html
    """

    def __init__(
        self,
        user,
        include_resources_by_default,
        default_resource_filter,
        bundle_resource_stats,
        cache_resource_links,
    ):
        # store resource links for requests
        self.cache_resource_links = cache_resource_links
        self.resource_link_cache = {}
        # bundle all stats into single line for each request (_resources)
        self.bundle_resource_stats = bundle_resource_stats
        self.resource_filter_pattern = re.compile(default_resource_filter)
        self.include_resources = include_resources_by_default
        # for finding url links in style tags
        self.url_link_pattern = re.compile(
            r".*URL\(\s*('|\")(.*)('|\")\s*\).*",
            re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )

        # for finding if a link is partial or full
        self.full_url_pattern = re.compile("^https?://", re.IGNORECASE)

        self.resource_paths = [
            '//link[@rel="stylesheet"]/@href',
            '//link[@rel="Stylesheet"]/@href',
            '//link[@rel="STYLESHEET"]/@href',
            "//script/@src",
            "//img/@src",
            "//source/@src",
            "//embed/@src",
            "//body/@background",
            '//input[@type="image"]/@src',
            '//input[@type="IMAGE"]/@src',
            '//input[@type="Image"]/@src',
            "//object/@data",
            "//frame/@src",
            "//iframe/@src",
        ]

        self.client = user.client
        self.client.request = self._request(self.client.request)
        self.host = user.host

    def get_embedded_resources(self, response_content, resource_filter):
        """
        returns a list of embedded resources in response_content
        provide a regex filter to limit what resources are returned
        """
        resources = []
        # check if defaults have been overridden for this request
        if self.cache_resource_links and response_content in self.resource_link_cache:
            resources = self.resource_link_cache[response_content]
        else:
            try:
                tree = html.fromstring(response_content)
                # check for base tag - otherwise use host for partial urls
                base_path_links = tree.xpath("//base/@href")
                base_path = base_path_links[0] if len(base_path_links) > 0 else self.host
                # build resource list
                for resource_path in self.resource_paths:
                    for resource in tree.xpath(resource_path):
                        if re.search(self.full_url_pattern, resource) is None:
                            resource = base_path + "/" + resource
                        if re.search(resource_filter, resource):
                            resources.append(resource)
                # add style urls
                style_tag_texts = tree.xpath("//style/text()")
                for text in style_tag_texts:
                    # check for url
                    url_matches = re.match(self.url_link_pattern, text)
                    if url_matches is not None:
                        resource = url_matches[2]
                        if re.search(self.full_url_pattern, resource) is None:
                            resource = base_path + "/" + resource
                        if re.search(resource_filter, resource):
                            resources.append(resource)
                if self.cache_resource_links:
                    self.resource_link_cache[response_content] = resources
            except etree.ParserError as e:
                logging.warning(str(e) + " " + str(response_content))
        return resources

    def _request(self, func):
        def wrapper(
            *args, include_resources=self.include_resources, resource_filter=self.resource_filter_pattern, **kwargs
        ):
            response = func(*args, **kwargs)

            if include_resources:
                content = response.content
                if isinstance(content, bytearray):
                    content = content.decode("utf-8")
                resources = self.get_embedded_resources(content, resource_filter)
                name = kwargs.get("name", args[1])
                for resource in resources:
                    # determine name for the resource
                    if self.bundle_resource_stats:
                        resource_name = name + "_resources"
                    else:
                        resource_name = resource
                    self.client.request("GET", resource, name=resource_name, include_resources=False)
            return response

        return wrapper


class HttpUserWithResources(HttpUser):
    """
    provides embedded resource management for HttpUser
    """

    abstract = True

    include_resources_by_default = True
    default_resource_filter = ".*"
    bundle_resource_stats = True
    cache_resource_links = True

    def __init__(self, *args):
        super().__init__(*args)
        EmbeddedResourceManager(
            self,
            self.include_resources_by_default,
            self.default_resource_filter,
            self.bundle_resource_stats,
            self.cache_resource_links,
        )


class FastHttpUserWithResources(FastHttpUser):
    """
    provides embedded resource management for FastHttpUser
    """

    abstract = True

    include_resources_by_default = True
    default_resource_filter = ".*"
    bundle_resource_stats = True
    cache_resource_links = True

    def __init__(self, *args):
        super().__init__(*args)
        EmbeddedResourceManager(
            self,
            self.include_resources_by_default,
            self.default_resource_filter,
            self.bundle_resource_stats,
            self.cache_resource_links,
        )

#!/usr/bin/env python3

""" Web API v1 """


from http.server import BaseHTTPRequestHandler as Handler
from json import dumps, loads
from re import compile as regex

from devopsdriver.settings import Settings

from genweb.relationships import person_json
from genweb.people import People
from genweb.metadata import Metadata
from genweb.genweb import load_startup_data


class ApiV1:
    """Version 1 of the API"""

    URL = "/api/v1/"
    CALL = regex(rf"^{URL}(people|metadata)(/([^/]+))?$")
    SEPARATOR_PATTERN = regex(r"[\s:;,]+")
    INT_FIELDS = ["width", "height"]
    LIST_FIELDS = ["people", "references"]

    def __init__(self):
        self.settings: Settings = None
        self.artifacts = None
        self.people: People = None
        self.metadata: Metadata = None

    def load(self) -> None:
        """Load all the information needed to run the web server

        Args:
            location (str): Pass __file__
        """
        self.settings, self.artifacts, self.people, self.metadata = load_startup_data()

    def parse_call(self, handler: Handler) -> tuple[str | None, str | None]:
        """Get the category and (possibly) the identifier from the call

        Args:
            handler (Handler): The HTTP Handler

        Returns:
            tuple[str | None, str | None]: people or metadata and identifier
        """
        parts = ApiV1.CALL.match(handler.path)

        if not parts:
            return None, None

        return parts.group(1), parts.group(3)

    def is_call(self, handler: Handler) -> bool:
        """Determines if a request is an API call

        Args:
            handler (Handler): The HTTP handler

        Returns:
            bool: True if it is recognized as a possible API call
        """
        return self.parse_call(handler)[0] is not None

    def handle_get(self, handler: Handler) -> tuple[bytes, str, int]:
        """Handles HTTP GET requests

        Args:
            handler (Handler): The HTTP handler

        Returns:
            tuple[bytes, str, int]: Returns the body, MIME type, and HTTP response code
        """
        category, identifier = self.parse_call(handler)
        assert category is not None, f"Not an API call {handler.path}"
        body = None
        mimetype = "text/json"
        response_code = 200

        # get the list of people identifiers
        if category == "people" and not identifier:
            body = dumps([str(i) for i in self.people]).encode("utf-8")

        # get a specific person
        elif category == "people" and identifier:
            person = self.people.get(identifier, None)

            if not person:
                body = f"Person not found: {identifier}".encode("utf-8")
                mimetype = "text/plain"
                response_code = 404
            else:
                body = dumps(person_json(person)).encode("utf-8")

        # get the list of metadata identifiers
        elif category == "metadata" and not identifier:
            body = dumps(list(self.metadata)).encode("utf-8")

        # get a specific metadata
        elif category == "metadata" and identifier:
            if identifier not in self.metadata:
                body = f"Metadata not found: {identifier}".encode("utf-8")
                mimetype = "text/plain"
                response_code = 404
            else:
                body = dumps(self.metadata[identifier]).encode("utf-8")

        assert body is not None, f"Not an API call {handler.path}"
        return body, mimetype, response_code

    def handle_post(self, handler: Handler) -> tuple[bytes, str, int]:
        """Handles HTTP POST requests

        Args:
            handler (Handler): The HTTP handler

        Returns:
            tuple[bytes, str, int]: Returns the body, MIME type, and HTTP response code
        """
        category, identifier = self.parse_call(handler)
        assert category is not None, f"Not an API call {handler.path}"
        body = None
        mimetype = "text/json"
        response_code = 200
        assert category == "metadata", f"Only POST metadata supported, not {category}"
        assert identifier, "POST metadata requires an identifier in the URI"

        # upload a metadata entry
        body_bytes = int(handler.headers["Content-Length"])
        metadata = loads(handler.rfile.read(body_bytes))

        # delete any empty entries
        for key in [k for k in metadata if not metadata[k]]:
            del metadata[key]

        for key in ApiV1.LIST_FIELDS:
            if key in metadata:  # change people from string to list
                metadata[key] = ApiV1.SEPARATOR_PATTERN.split(metadata[key])

        for field in ApiV1.INT_FIELDS:
            if field in metadata:
                metadata[field] = int(metadata[field])

        self.metadata[identifier] = metadata
        self.metadata.save()
        body = dumps(metadata).encode("utf-8")
        return body, mimetype, response_code

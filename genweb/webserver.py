#!/usr/bin/env python3


""" Web server for ui interface """


from http.server import HTTPServer, BaseHTTPRequestHandler
from types import SimpleNamespace
from os.path import join, dirname
from json import dumps, loads
from re import compile as regex
from traceback import format_exc

from devopsdriver.settings import Settings

from genweb.relationships import load_gedcom, person_json
from genweb.people import People
from genweb.metadata import Metadata
from genweb.genweb import link_people_to_metadata


GLOBALS = SimpleNamespace(people=None, metadata=None, settings=None)
DATA_DIR = join(dirname(__file__), "data")
STATIC_FILES = {"/": "editor.html"}
API_V1 = "/api/v1/"
V1_CALL = regex(rf"^{API_V1}(people|metadata)(/([^/]+))?$")
SEPARATOR_PATTERN = regex(r"[\s:;,]+")


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Metadata Editor Web Server"""

    def respond(
        self, body: bytes, mimetype: str = "text/html", code: int = 200
    ) -> None:
        """Sends an HTTP response

        Args:
            body (bytes): The body of the response in bytes
            mimetype (str, optional): The mime type of the body. Defaults to "text/html".
            code (int, optional): The HTTP response code. Defaults to 200.
        """
        self.send_response(code)
        self.send_header("Content-Size", len(body))
        self.send_header("Content-Type", mimetype)
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: str, mimetype: str = "text/html") -> None:
        """Sends a file on disk as a response (or 404 if not found)

        Args:
            path (str): The path to the file to send
            mimetype (str, optional): The mimetype of the file. Defaults to "text/html".
        """
        # TODO: If mimetype is None, guess from extension  # pylint: disable=fixme
        try:
            with open(path, "rb") as file:
                self.respond(file.read(), mimetype=mimetype)

        except FileNotFoundError as error:
            self.respond(
                f"File not found: {self.path} ({path}): {error}".encode("utf-8"),
                code=404,
            )

    def handle_api_v1(self, method: str):
        """Handle any API calls"""
        api_call = V1_CALL.match(self.path)
        assert api_call, self.path

        if api_call.group(1) == "people" and not api_call.group(2) and method == "GET":
            people = dumps([str(i) for i in GLOBALS.people]).encode("utf-8")
            self.respond(people, mimetype="text/json")

        elif api_call.group(1) == "people" and api_call.group(3) and method == "GET":
            person = GLOBALS.people.get(api_call.group(3), None)

            if not person:
                self.respond(
                    f"Person not found: {api_call.group(3)}".encode("utf-8"), code=404
                )
                return

            metadata = dumps(person_json(person)).encode("utf-8")
            self.respond(metadata, mimetype="text/json")

        elif (
            api_call.group(1) == "metadata"
            and not api_call.group(2)
            and method == "GET"
        ):
            people = dumps(list(GLOBALS.metadata)).encode("utf-8")
            self.respond(people, mimetype="text/json")

        elif api_call.group(1) == "metadata" and api_call.group(3) and method == "GET":
            if api_call.group(3) not in GLOBALS.metadata:
                self.respond(
                    f"Metadata not found: {api_call.group(3)}".encode("utf-8"), code=404
                )
                return

            metadata = dumps(GLOBALS.metadata[api_call.group(3)]).encode("utf-8")
            self.respond(metadata, mimetype="text/json")

        elif api_call.group(1) == "metadata" and api_call.group(3) and method == "POST":
            metadata = loads(self.rfile.read(int(self.headers["Content-Length"])))

            for key in [k for k in metadata if not metadata[k]]:
                del metadata[key]

            if "people" in metadata:
                metadata["people"] = SEPARATOR_PATTERN.split(metadata["people"])

            print(dumps(metadata, indent=2))
            self.respond(dumps(metadata, indent=2).encode("utf-8"))

        else:
            self.respond(
                f"API not found: {self.path}".encode("utf-8"),
                code=404,
            )

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle GET requests"""
        try:
            if self.path in STATIC_FILES:
                self.send_file(join(DATA_DIR, STATIC_FILES[self.path]))
                return

            if self.path.startswith(API_V1):
                self.handle_api_v1("GET")
                return

            self.respond(
                f"File not found: {self.path}".encode("utf-8"),
                code=404,
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.respond(
                f"Internal server error {error}<br/><pre>{format_exc()}</pre>".encode(
                    "utf-8"
                ),
                code=500,
            )

    def do_POST(self):  # pylint: disable=invalid-name
        """Handle POSTing of data"""
        try:
            if self.path.startswith(API_V1):
                self.handle_api_v1("POST")
                return

            self.respond(
                f"File not found: {self.path}".encode("utf-8"),
                code=404,
            )

        except Exception as error:  # pylint: disable=broad-exception-caught
            self.respond(
                f"Internal server error {error}<br/><pre>{format_exc()}</pre>".encode(
                    "utf-8"
                ),
                code=500,
            )


def start_webserver(port=8000, host="") -> None:
    """Start the editor web server

    Args:
        port (int, optional): The port to listen on. Defaults to 8000.
        host (str, optional): The host to listen on. Defaults to "", meaning all local addresses.
    """
    GLOBALS.settings = Settings(__file__)
    GLOBALS.people = People(
        load_gedcom(GLOBALS.settings["gedcom_path"]),
        GLOBALS.settings.get("alias_path", None),
    )
    GLOBALS.metadata = Metadata(GLOBALS.settings["metadata_yaml"])
    link_people_to_metadata(GLOBALS.people, GLOBALS.metadata)
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print("Starting web server")
    httpd.serve_forever()


start_webserver()

#!/usr/bin/env python3


""" Web server for ui interface """


from http.server import HTTPServer, BaseHTTPRequestHandler
from os.path import join, dirname
from traceback import format_exc
from mimetypes import guess_type

from genweb.webapi_v1 import ApiV1


API_V1 = ApiV1()
DATA_DIR = join(dirname(__file__), "data")
STATIC_FILES = {
    "/": "editor.html",
    "/styles.css": "styles.css",
    "/editor.js": "editor.js",
}


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

    def send_file(self, path: str, mimetype: str = None) -> None:
        """Sends a file on disk as a response (or 404 if not found)

        Args:
            path (str): The path to the file to send
            mimetype (str, optional): The mimetype of the file. Defaults to "text/html".
        """
        mimetype = guess_type(path)[0] if mimetype is None else mimetype

        try:
            with open(path, "rb") as file:
                self.respond(file.read(), mimetype=mimetype)

        except FileNotFoundError as error:
            self.respond(
                f"File not found: {self.path} ({path}): {error}".encode("utf-8"),
                code=404,
            )

    def do_GET(self):  # pylint: disable=invalid-name
        """Handle GET requests"""
        try:
            if self.path in STATIC_FILES:
                self.send_file(join(DATA_DIR, STATIC_FILES[self.path]))

            elif API_V1.is_call(self):
                self.respond(*API_V1.handle_get(self))

            else:
                body = f"File not found: {self.path}".encode("utf-8")
                self.respond(body, code=404)

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
            if API_V1.is_call(self):
                self.respond(*API_V1.handle_post(self))

            else:
                body = f"File not found: {self.path}".encode("utf-8")
                self.respond(body, code=404)

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
    API_V1.load()
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print("Starting web server")
    httpd.serve_forever()


start_webserver()

#!/usr/bin/env python3


""" Web server for ui interface """


from http.server import HTTPServer, BaseHTTPRequestHandler
from types import SimpleNamespace
from os.path import join, dirname
from json import dumps
from re import compile as regex

from devopsdriver.settings import Settings

from genweb.relationships import load_gedcom, person_json
from genweb.people import People
from genweb.metadata import load_yaml
from genweb.genweb import link_people_to_metadata


GLOBALS = SimpleNamespace(people=None, metadata=None, settings=None)
DATA_DIR = join(dirname(__file__), "data")
STATIC_FILES = {"/": "editor.html"}
API_V1 = "/api/v1/"
V1_CALL = regex(rf"^{API_V1}(people|metadata)(/([^/]+))?$")


class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    BaseHTTPRequestHandler has the following instance variables:

    client_address
    Contains a tuple of the form (host, port) referring to the client’s address.

    server
    Contains the server instance.

    command
    Contains the command (request type). For example, 'GET'.

    path
    Contains the request path.

    request_version
    Contains the version string from the request. For example, 'HTTP/1.0'.

    headers
    Holds an instance of the class specified by the MessageClass class variable.
    This instance parses and manages the headers in the HTTP request.

    rfile
    Contains an input stream, positioned at the start of the optional input data.

    wfile
    Contains the output stream for writing a response back to the client.
    Proper adherence to the HTTP protocol must be used when writing to this stream.

    BaseHTTPRequestHandler has the following class variables:

    server_version
    Specifies the server software version. You may want to override this.
    The format is multiple whitespace-separated strings, where each string is of
    the form name[/version]. For example, 'BaseHTTP/0.2'.

    sys_version
    Contains the Python system version, in a form usable by the version_string method and
    the server_version class variable. For example, 'Python/1.4'.

    error_message_format
    Specifies a format string for building an error response to the client.
    It uses parenthesized, keyed format specifiers, so the format operand must be a dictionary.
    The code key should be an integer, specifying the numeric HTTP error code value. message
    should be a string containing a (detailed) error message of what occurred, and explain should
    be an explanation of the error code number. Default message and explain values can found in
    the responses class variable.

    error_content_type
    Specifies the Content-Type HTTP header of error responses sent to the client.
    The default value is 'text/html'.

    New in version 2.6: Previously, the content type was always 'text/html'.

    protocol_version
    This specifies the HTTP protocol version used in responses.
    If set to 'HTTP/1.1', the server will permit HTTP persistent connections;
    however, your server must then include an accurate Content-Length header
    (using send_header()) in all of its responses to clients. For backwards compatibility,
    the setting defaults to 'HTTP/1.0'.

    MessageClass
    Specifies a rfc822.Message-like class to parse HTTP headers. Typically, this is not
    overridden, and it defaults to mimetools.Message.

    responses
    This variable contains a mapping of error code integers to two-element tuples containing
    a short and long message. For example, {code: (shortmessage, longmessage)}. The shortmessage
    is usually used as the message key in an error response, and longmessage as the explain key
    (see the error_message_format class variable).

    A BaseHTTPRequestHandler instance has the following methods:

    handle()
    Calls handle_one_request() once (or, if persistent connections are enabled, multiple
    times) to handle incoming HTTP requests. You should never need to override it; instead,
    implement appropriate do_*() methods.

    handle_one_request()
    This method will parse and dispatch the request to the appropriate do_*()
    method. You should never need to override it.

    send_error(code[, message])
    Sends and logs a complete error reply to the client. The numeric code specifies the HTTP
    error code, with message as optional, more specific text. A complete set of headers is sent,
    followed by text composed using the error_message_format class variable.

    send_response(code[, message])
    Sends a response header and logs the accepted request. The HTTP response line is sent,
    followed by Server and Date headers. The values for these two headers are picked up from the
    version_string() and date_time_string() methods, respectively.

    send_header(keyword, value)
    Writes a specific HTTP header to the output stream. keyword should specify the header keyword,
    with value specifying its value.

    end_headers()
    Sends a blank line, indicating the end of the HTTP headers in the response.

    log_request([code[, size]])
    Logs an accepted (successful) request. code should specify the numeric HTTP code associated
    with the response. If a size of the response is available, then it should be passed as the
    size parameter.

    log_error(...)
    Logs an error when a request cannot be fulfilled. By default, it passes the message to
    log_message(), so it takes the same arguments (format and additional values).

    log_message(format, ...)
    Logs an arbitrary message to sys.stderr. This is typically overridden to create custom
    error logging mechanisms. The format argument is a standard printf-style format string,
    where the additional arguments to log_message() are applied as inputs to the formatting.
    The client address and current date and time are prefixed to every message logged.

    version_string()
    Returns the server software’s version string. This is a combination of the server_version and
    sys_version class variables.

    date_time_string([timestamp])
    Returns the date and time given by timestamp (which must be in the format returned by
    time.time()), formatted for a message header. If timestamp is omitted, it uses the current
    date and time.

    The result looks like 'Sun, 06 Nov 1994 08:49:37 GMT'.

    New in version 2.5: The timestamp parameter.

    log_date_time_string()
    Returns the current date and time, formatted for logging.

    address_string()
    Returns the client address, formatted for logging. A name lookup is performed on the
    client’s IP address.

    """

    def respond(
        self, body: bytes, mimetype: str = "text/html", code: int = 200
    ) -> None:
        self.send_response(code)
        self.send_header("Content-Size", len(body))
        self.send_header("Content-Type", mimetype)
        self.end_headers()
        self.wfile.write(body)

    def send_file(self, path: str, mimetype: str = "text/html") -> None:
        try:
            with open(path, "rb") as file:
                self.respond(file.read(), mimetype=mimetype)

        except FileNotFoundError as error:
            self.respond(
                f"File not found: {self.path} ({path}): {error}".encode("utf-8"),
                code=404,
            )

    def handle_people(self):
        if self.path == "/api/v1/people":
            people = dumps([i for i in GLOBALS.people]).encode("utf-8")
            self.respond(people, mimetype="text/json")
            return

    def handle_api_v1(self):
        api_call = V1_CALL.match(self.path)
        assert api_call, self.path

        if api_call.group(1) == "people" and not api_call.group(2):
            people = dumps([i for i in GLOBALS.people]).encode("utf-8")
            self.respond(people, mimetype="text/json")
            return

        if api_call.group(1) == "people" and api_call.group(3):
            person = GLOBALS.people.get(api_call.group(3), None)

            if not person:
                self.respond(
                    f"Person not found: {api_call.group(3)}".encode("utf-8"), code=404
                )
                return

            info = dumps(person_json(person)).encode("utf-8")
            self.respond(info, mimetype="text/json")
            return

        if api_call.group(1) == "metadata" and not api_call.group(2):
            people = dumps([i for i in GLOBALS.metadata]).encode("utf-8")
            self.respond(people, mimetype="text/json")
            return

        if api_call.group(1) == "metadata" and api_call.group(3):
            if api_call.group(3) not in GLOBALS.metadata:
                self.respond(
                    f"Metadata not found: {api_call.group(3)}".encode("utf-8"), code=404
                )
                return

            metadata = dumps(GLOBALS.metadata[api_call.group(3)]).encode("utf-8")
            self.respond(metadata, mimetype="text/json")
            return

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
                self.handle_api_v1()
                return

            self.respond(
                f"File not found: {self.path}".encode("utf-8"),
                code=404,
            )
        except Exception as error:  # pylint: disable=broad-exception-caught
            self.respond(
                f"Internal server error {error}".encode("utf-8"),
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
    GLOBALS.metadata = load_yaml(GLOBALS.settings["metadata_yaml"])
    link_people_to_metadata(GLOBALS.people, GLOBALS.metadata)
    httpd = HTTPServer((host, port), SimpleHTTPRequestHandler)
    print("Starting web server")
    httpd.serve_forever()


start_webserver()

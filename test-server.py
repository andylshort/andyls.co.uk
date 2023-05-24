#!/usr/bin/env python3
import http.server
import socketserver
from pathlib import Path
import os

HOST = "localhost"
PORT = 8080

class HttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=Path(os.path.join(os.getcwd(), "build")), **kwargs)

    def version_string(self):
        return "Apache/1.3.0 (Win32)"

HttpRequestHandler.extensions_map = {
    ".svg": "image/svg+xml",
    ".svgz": "image/svg+xml"
}

try:
    with socketserver.TCPServer((HOST, PORT), HttpRequestHandler) as httpd:
        print(f"Serving at http://{HOST}:{PORT}")
        httpd.serve_forever()
except KeyboardInterrupt:
    pass

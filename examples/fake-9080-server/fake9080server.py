#!/usr/bin/env python3
"""Fake HTTP server on port 9080 to suppress UniFi log noise.

Responds 200 + empty JSON to GET /api/ucore/manifest, 401 to everything else.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress access logs

    def do_GET(self):
        if self.path == '/api/ucore/manifest':
            body = b'{}'
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(401)
            self.end_headers()

    def do_POST(self):
        self.send_response(401)
        self.end_headers()


HTTPServer(('127.0.0.1', 9080), Handler).serve_forever()

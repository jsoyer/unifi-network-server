#!/usr/bin/env python3
"""Fake HTTP server on port 9080 to suppress UniFi log noise.

Waits for UniFi to start before trying to bind, then only binds if
the port is still free (UniFi may use it in some configurations).
"""
import socket
import sys
import time
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


def port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0


# Wait for UniFi to start and potentially claim port 9080
time.sleep(90)

# If something is already listening on 9080, nothing to do — exit 0
# so the 'until' loop in the caller does not restart us.
if port_in_use(9080):
    print("Port 9080 already in use, not starting fake server")
    sys.exit(0)

try:
    server = HTTPServer(('127.0.0.1', 9080), Handler)
except OSError as e:
    print(f"Cannot bind to port 9080: {e}")
    sys.exit(0)

print("Fake 9080 server started")
server.serve_forever()

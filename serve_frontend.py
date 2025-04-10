#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

PORT = 3000

# Change to the static directory
os.chdir('static')

Handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", PORT), Handler)

print(f"Serving frontend at http://0.0.0.0:{PORT}/")
try:
    httpd.serve_forever()
except KeyboardInterrupt:
    print("\nShutting down server")
    httpd.server_close()
    sys.exit(0)
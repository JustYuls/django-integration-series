"""Part 2: a tiny HTTP server that answers like a real web API."""
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

DEFAULT_ROOMS = [
    {"id": 1, "name": "Room 101", "capacity": 40},
    {"id": 2, "name": "Lab A", "capacity": 30},
]


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_json(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            if self.path == "/rooms":
                self.send_json(200, self.server.rooms)
            elif self.path == "/boom":
                raise RuntimeError("deliberate server error")
            else:
                self.send_json(404, {"error": "not found"})
        except Exception:
            self.send_json(500, {"error": "server error"})

    def do_POST(self):
        if self.path != "/rooms":
            self.send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        if "name" not in data:
            self.send_json(400, {"error": "name is required"})
            return
        room = {"id": len(self.server.rooms) + 1, **data}
        self.server.rooms.append(room)
        self.send_json(201, room)

    def log_message(self, format, *args):
        if not self.server.quiet:
            super().log_message(format, *args)


def make_server(port=8000, quiet=False):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.rooms = [dict(room) for room in DEFAULT_ROOMS]
    server.quiet = quiet
    return server


if __name__ == "__main__":
    server = make_server()
    print("Listening on http://127.0.0.1:8000  (Ctrl+C to stop)")
    server.serve_forever()

"""Part 3: one small server that speaks two API styles (REST and SOAP) and has one private endpoint."""
import json
import xml.etree.ElementTree as ET
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOMS = {1: {"id": 1, "name": "Room 101", "capacity": 40}, 2: {"id": 2, "name": "Lab A", "capacity": 30}}
API_KEY = "demo-key"  # a made-up key for teaching; real keys live in environment variables, never in code

SOAP_RESPONSE = """<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetRoomCapacityResponse><Capacity>{capacity}</Capacity></GetRoomCapacityResponse>
  </soap:Body>
</soap:Envelope>"""


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send_body(self, status, body, content_type, headers=None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_json(self, status, payload, headers=None):
        self.send_body(status, json.dumps(payload).encode(), "application/json", headers)

    def do_GET(self):
        if self.path.startswith("/rooms/"):
            room = ROOMS.get(int(self.path.rsplit("/", 1)[1]))
            self.send_json(200, room) if room else self.send_json(404, {"error": "not found"})
        elif self.path == "/private/bookings":
            if self.headers.get("X-API-Key") != API_KEY:
                self.send_json(401, {"error": "missing or wrong API key"})
            else:
                self.send_json(200, [{"id": 1, "room_id": 1, "booked_by": "ana"}])
        elif self.path == "/soap":
            self.send_json(405, {"error": "SOAP uses POST"}, {"Allow": "POST"})
        else:
            self.send_json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/soap":
            self.send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length", 0))
        room_id = int(ET.fromstring(self.rfile.read(length)).find(".//RoomId").text)
        room = ROOMS[room_id]
        self.send_body(200, SOAP_RESPONSE.format(capacity=room["capacity"]).encode(), "text/xml; charset=utf-8")

    def log_message(self, format, *args):
        if not self.server.quiet:
            super().log_message(format, *args)


def make_server(port=8000, quiet=False):
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    server.quiet = quiet
    return server


if __name__ == "__main__":
    print("Listening on http://127.0.0.1:8000  (Ctrl+C to stop)")
    make_server().serve_forever()

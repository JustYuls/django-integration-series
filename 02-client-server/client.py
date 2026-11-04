"""Part 2: two clients for the server: one speaks raw HTTP over a socket, one uses urllib."""
import json
import socket
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"


def raw_request(host, port, path):
    # Speak HTTP by hand: open a TCP connection, send text, read text back.
    request = (f"GET {path} HTTP/1.1\r\nHost: {host}\r\n"
               "Connection: close\r\n\r\n")
    chunks = []
    with socket.create_connection((host, port), timeout=5) as sock:
        sock.sendall(request.encode())
        while True:
            data = sock.recv(4096)
            if not data:
                break
            chunks.append(data)
    return b"".join(chunks).decode()


def call(method, url, payload=None):
    # Return (status, JSON). Check the status before using the data.
    data = json.dumps(payload).encode() if payload is not None else None
    request = Request(url, data=data, method=method,
                      headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=5) as response:
            return response.status, json.load(response)
    except HTTPError as error:
        with error:
            return error.code, json.load(error)


def main():
    print(raw_request("127.0.0.1", 8000, "/rooms"))
    print("---")
    for method, path, payload in [("GET", "/rooms", None), ("GET", "/nope", None), ("GET", "/boom", None),
                                  ("POST", "/rooms", {"name": "Gym", "capacity": 80}), ("POST", "/rooms", {"capacity": 5})]:
        status, body = call(method, BASE + path, payload)
        print(f"{method:4} {path:7} -> {status}  {body}")


if __name__ == "__main__":
    main()

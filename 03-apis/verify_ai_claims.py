"""Part 3: verify what an AI assistant told us. Every claim gets a small test; we keep only what passes."""
import threading
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import api_server
import compare


def soap_is_larger(base):
    _, rest_bytes = compare.rest_room(base)
    _, soap_in, soap_out = compare.soap_room(base)
    return soap_in + soap_out > rest_bytes


def soap_needs_post(base):
    try:
        urlopen(f"{base}/soap", timeout=5)
        return False
    except HTTPError as error:
        with error:
            return error.code == 405 and compare.soap_room(base)[0] == 40


def python_needs_requests(base):
    # The claim says requests is REQUIRED.
    # compare.py uses only the standard library.
    capacity, _ = compare.rest_room(base)
    return capacity != 40


CLAIMS = [
    ("SOAP messages are larger than the same data as JSON", soap_is_larger),
    ("SOAP over HTTP is sent with POST, not GET", soap_needs_post),
    ("Python cannot call a REST API without installing requests", python_needs_requests),
]


def main():
    server = api_server.make_server(port=0, quiet=True)
    base = f"http://127.0.0.1:{server.server_address[1]}"
    threading.Thread(target=server.serve_forever, daemon=True).start()
    for text, check in CLAIMS:
        print(f"{'PASS' if check(base) else 'FAIL'}  {text}")
    server.shutdown()
    server.server_close()


if __name__ == "__main__":
    main()

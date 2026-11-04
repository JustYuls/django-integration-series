"""Part 3: call the same server as a REST client and as a SOAP client, and measure the difference."""
import json
import xml.etree.ElementTree as ET
from urllib.error import HTTPError
from urllib.request import Request, urlopen

BASE = "http://127.0.0.1:8000"

SOAP_REQUEST = """<?xml version="1.0"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <GetRoomCapacity><RoomId>{room_id}</RoomId></GetRoomCapacity>
  </soap:Body>
</soap:Envelope>"""


def rest_room(base, room_id=1):
    # REST: the URL names the thing, GET reads it, the answer is JSON.
    with urlopen(f"{base}/rooms/{room_id}", timeout=5) as response:
        raw = response.read()
    return json.loads(raw)["capacity"], len(raw)


def soap_room(base, room_id=1):
    # SOAP: one endpoint, an XML envelope goes in by POST, an XML envelope comes out.
    body = SOAP_REQUEST.format(room_id=room_id).encode()
    request = Request(f"{base}/soap", data=body, method="POST", headers={"Content-Type": "text/xml"})
    with urlopen(request, timeout=5) as response:
        raw = response.read()
    return int(ET.fromstring(raw).find(".//Capacity").text), len(body), len(raw)


def private_status(base, key=None):
    # A private API: no key, no data.
    headers = {"X-API-Key": key} if key else {}
    try:
        with urlopen(Request(f"{base}/private/bookings", headers=headers), timeout=5) as response:
            return response.status
    except HTTPError as error:
        with error:
            return error.code


def main():
    capacity, rest_bytes = rest_room(BASE)
    print(f"REST  GET  /rooms/1  capacity={capacity}  response={rest_bytes} bytes")
    capacity, soap_in, soap_out = soap_room(BASE)
    print(f"SOAP  POST /soap     capacity={capacity}  request={soap_in} bytes  response={soap_out} bytes")
    print(f"Private API without a key: {private_status(BASE)}   with the key: {private_status(BASE, 'demo-key')}")


if __name__ == "__main__":
    main()

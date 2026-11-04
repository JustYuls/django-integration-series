# Part 2: Client-Server and the HTTP Request Cycle (LO 1.2)

A tiny HTTP server and two clients: one that speaks raw HTTP over a socket, and one that uses `urllib` and checks status codes.

## Course outcome

- **CO1:** Explain and analyze scripting concepts and client-server architecture used in application and systems integration.
- **LO 1.2:** Analyze client-server architecture models, including request-response cycles, server roles, and communication protocols.

## Run it

You need Python 3.12+. There is nothing to install. Use two terminals.

```bash
python server.py            # terminal 1: listens on http://127.0.0.1:8000
```

```bash
python client.py            # terminal 2: raw request, then five calls with their status codes
```

Expected output of the second part:

```
GET  /rooms  -> 200  [{'id': 1, 'name': 'Room 101', 'capacity': 40}, ...]
GET  /nope   -> 404  {'error': 'not found'}
GET  /boom   -> 500  {'error': 'server error'}
POST /rooms  -> 201  {'id': 3, 'name': 'Gym', 'capacity': 80}
POST /rooms  -> 400  {'error': 'name is required'}
```

You can also open http://127.0.0.1:8000/rooms in a browser.

## Test it

Each test starts its own server on a free port, so nothing needs to be running.

```bash
python -m unittest -v       # 6 tests
```

## Files

| File | What it shows |
|---|---|
| `server.py` | a handler, routes, status codes 200, 201, 400, 404, 500 |
| `client.py` | `raw_request` (a socket and plain HTTP text) and `call` (urllib, status checked) |
| `test_client_server.py` | the status codes and the raw response format |

## Practice

1. Add `GET /rooms/1` that returns one room, or 404 if it does not exist.
2. Add a `DELETE /rooms/1` method and return 204.
3. Run the server, then open the browser developer tools (Network tab) and compare the headers with the raw output.

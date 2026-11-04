# Part 3: Choosing the Right API and Language (LO 1.3)

One small server that speaks two API styles, REST and SOAP, plus a private endpoint. Two clients call the same data both ways and measure the difference. Then a generative AI check: an AI assistant's claims are turned into tests, and only what passes is kept.

## Course outcome

- **CO1:** Explain and analyze scripting concepts and client-server architecture used in application and systems integration, and use Generative AI to compare and justify the tools.
- **LO 1.3:** Compare different scripting languages and APIs for integration tasks.

This is the last part of CO1.

## Run it

You need Python 3.12+. There is nothing to install. Use two terminals.

```bash
python api_server.py        # terminal 1: http://127.0.0.1:8000
```

```bash
python compare.py           # terminal 2: REST vs SOAP, and the private API with and without a key
```

Expected output:

```
REST  GET  /rooms/1  capacity=40  response=45 bytes
SOAP  POST /soap     capacity=40  request=196 bytes  response=217 bytes
Private API without a key: 401   with the key: 200
```

The AI claim check starts its own server, so nothing else needs to run:

```bash
python verify_ai_claims.py
```

```
PASS  SOAP messages are larger than the same data as JSON
PASS  SOAP over HTTP is sent with POST, not GET
FAIL  Python cannot call a REST API without installing requests
```

PASS means the claim holds. FAIL means the claim is wrong.

## Test it

```bash
python -m unittest -v       # 8 tests
```

## Files

| File | What it shows |
|---|---|
| `api_server.py` | a REST resource, a SOAP endpoint (XML envelope), a private endpoint with an API key |
| `compare.py` | a REST client and a SOAP client using only the standard library, with byte counts |
| `verify_ai_claims.py` | three AI claims written as small true/false checks |
| `test_apis.py` | REST and SOAP results, message sizes, 401 and 200, and the claim checks |

## About the AI answer in the video

The AI assistant answer shown on screen was generated with Claude (Anthropic), shortened, and then verified with the code in `verify_ai_claims.py`. The routine is: give context, split the answer into claims, test each claim, keep what passes and write down why.

The API key in `api_server.py` is a made-up demo value for teaching. Real keys belong in environment variables, never in source code.

## Practice

1. Add a SOAP operation that returns the room name, and compare the message sizes again.
2. Write a fourth claim an AI might make, and write a check for it.
3. Change the private endpoint so the key comes from an environment variable.

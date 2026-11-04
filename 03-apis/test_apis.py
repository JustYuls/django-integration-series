import threading
import unittest

import api_server
import compare
import verify_ai_claims


class ApiTestCase(unittest.TestCase):
    def setUp(self):
        self.server = api_server.make_server(port=0, quiet=True)
        self.base = f"http://127.0.0.1:{self.server.server_address[1]}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()


class RestVersusSoapTests(ApiTestCase):
    def test_rest_returns_the_capacity(self):
        capacity, _ = compare.rest_room(self.base)
        self.assertEqual(capacity, 40)

    def test_soap_returns_the_same_capacity(self):
        capacity, _, _ = compare.soap_room(self.base, 1)
        self.assertEqual(capacity, 40)

    def test_soap_for_another_room(self):
        self.assertEqual(compare.soap_room(self.base, 2)[0], 30)

    def test_soap_messages_are_larger_than_the_json(self):
        _, rest_bytes = compare.rest_room(self.base)
        _, soap_in, soap_out = compare.soap_room(self.base)
        self.assertGreater(soap_in + soap_out, rest_bytes)


class PrivateApiTests(ApiTestCase):
    def test_no_key_is_rejected_with_401(self):
        self.assertEqual(compare.private_status(self.base), 401)

    def test_wrong_key_is_rejected_with_401(self):
        self.assertEqual(compare.private_status(self.base, "nope"), 401)

    def test_correct_key_is_accepted(self):
        self.assertEqual(compare.private_status(self.base, "demo-key"), 200)


class AiClaimTests(ApiTestCase):
    def test_the_true_claims_pass_and_the_false_one_fails(self):
        results = [check(self.base) for _, check in verify_ai_claims.CLAIMS]
        self.assertEqual(results, [True, True, False])


if __name__ == "__main__":
    unittest.main()

import threading
import unittest

import client
import server


class ServerTestCase(unittest.TestCase):
    def setUp(self):
        self.server = server.make_server(port=0, quiet=True)  # port 0: the OS picks a free port
        self.port = self.server.server_address[1]
        self.base = f"http://127.0.0.1:{self.port}"
        threading.Thread(target=self.server.serve_forever, daemon=True).start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()


class ClientServerTests(ServerTestCase):
    def test_get_rooms_returns_200_and_a_list(self):
        status, body = client.call("GET", self.base + "/rooms")
        self.assertEqual(status, 200)
        self.assertEqual(len(body), 2)

    def test_unknown_path_returns_404(self):
        status, _ = client.call("GET", self.base + "/nope")
        self.assertEqual(status, 404)

    def test_server_error_returns_500(self):
        status, body = client.call("GET", self.base + "/boom")
        self.assertEqual(status, 500)
        self.assertEqual(body, {"error": "server error"})

    def test_valid_post_returns_201_with_a_new_id(self):
        status, body = client.call("POST", self.base + "/rooms", {"name": "Gym", "capacity": 80})
        self.assertEqual(status, 201)
        self.assertEqual(body["id"], 3)

    def test_post_without_a_name_returns_400(self):
        status, _ = client.call("POST", self.base + "/rooms", {"capacity": 5})
        self.assertEqual(status, 400)

    def test_raw_response_has_a_status_line_and_headers(self):
        text = client.raw_request("127.0.0.1", self.port, "/rooms")
        head, _, body = text.partition("\r\n\r\n")
        self.assertTrue(head.startswith("HTTP/1.1 200 OK"))
        self.assertIn("Content-Type: application/json", head)
        self.assertIn("Room 101", body)


if __name__ == "__main__":
    unittest.main()

import contextlib
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from urllib.error import HTTPError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import miner_read as reader


class ReadExamplesTests(unittest.TestCase):
    def test_offline_fixtures_never_open_network(self):
        with patch.object(reader, "fetch", side_effect=AssertionError("Network forbidden")):
            for endpoint in reader.ENDPOINTS:
                with self.subTest(endpoint=endpoint), contextlib.redirect_stdout(io.StringIO()) as out:
                    self.assertEqual(reader.main(["--fixture", endpoint]), 0)
                    result = json.loads(out.getvalue())
                    self.assertIn("Educational", result["source"])

    def test_only_four_endpoints_can_be_requested(self):
        for endpoint in ("reboot", "config", "../info", "info?x=1", "info/status"):
            with self.subTest(endpoint=endpoint), self.assertRaises(reader.ReadError):
                reader.build_url("http://192.168.1.20", endpoint)

    def test_url_rejects_public_hosts_credentials_and_other_destinations(self):
        invalid = [
            "https://8.8.8.8", "http://169.254.169.254", "http://100.64.0.1",
            "http://miner.example", "file:///tmp/info", "ftp://192.168.1.20",
            "http://user:secret@192.168.1.20", "http://192.168.1.20/path",
            "http://192.168.1.20/?token=secret", "http://192.168.1.20/#fragment",
            "http://[fe80::1%25en0]", "http://192.168.1.20:0",
        ]
        for url in invalid:
            with self.subTest(url=url), self.assertRaises(reader.ReadError):
                reader.build_url(url, "info")

    def test_local_url_and_metrics_query(self):
        self.assertEqual(reader.build_url("http://192.168.1.20/", "info"), "http://192.168.1.20/api/v1/info")
        self.assertEqual(reader.build_url("https://[fd00::1]:8443", "metrics", 3600, 60),
                         "https://[fd00::1]:8443/api/v1/metrics?time_slice=3600&step=60")

    def test_invalid_metrics_query_rejected_before_network(self):
        for time_slice, step in ((0, 60), (259201, 60), (True, 60), (3600, 0), (3600, -1), (3600, 2**31)):
            with self.subTest(time_slice=time_slice, step=step), self.assertRaises(reader.ReadError):
                reader.build_url("http://192.168.1.20", "metrics", time_slice, step)
        with self.assertRaises(reader.ReadError):
            reader.build_url("http://192.168.1.20", "info", 3600, 60)

    def test_missing_or_null_summary_is_not_zero_hashrate(self):
        self.assertIsNone(reader.project("summary", {})["miner"])
        self.assertIsNone(reader.project("summary", {"miner": None})["miner"])
        with self.assertRaises(reader.ReadError):
            reader.project("summary", {"miner": {}})

    def test_boolean_is_not_numeric_hashrate(self):
        with self.assertRaises(reader.ReadError):
            reader.project("summary", {"miner": {"hr_average": True, "hr_realtime": 0, "power_consumption": 0}})

    def test_info_projection_excludes_identifiers_and_network_details(self):
        payload = {k: "sample" for k in ("fw_name", "fw_version", "platform", "install_type", "model", "algorithm", "hr_measure")}
        payload.update({"serial": "not-for-output", "system": {"network_status": "private"}, "token": "secret"})
        out = json.dumps(reader.project("info", payload))
        self.assertNotIn("not-for-output", out)
        self.assertNotIn("private", out)
        self.assertNotIn("secret", out)

    def test_numeric_metrics_are_not_rescaled(self):
        data = {"timezone": "GMT", "annotations": [], "metrics": [{"time": 123, "data": {"hashrate": 123.5, "power_consumption": 456}}]}
        selected = reader.project("metrics", data)
        self.assertEqual(selected["metrics"][0]["data"], {"hashrate": 123.5, "power_consumption": 456})
        self.assertEqual(selected["metrics"][0]["time"], 123)

    def test_invalid_json_and_oversized_response_are_rejected(self):
        for raw in (b"<html>Login</html>", b'{"a": NaN}', b"\xff", b" " * (reader.MAX_BYTES + 1)):
            with self.subTest(length=len(raw)), self.assertRaises(reader.ReadError):
                reader.decode_json(raw)

    def test_redirect_never_reaches_second_host(self):
        with self.assertRaises(reader.ReadError):
            reader.NoRedirects().redirect_request(None, None, 302, "Found", {}, "http://8.8.8.8/")

    def test_one_get_no_body_no_credentials_and_timeout(self):
        class Response:
            status = 200
            def __enter__(self): return self
            def __exit__(self, *_): pass
            def read(self, limit):
                self.limit = limit
                return b'{"miner":null}'
        response = Response()
        with patch.object(reader, "build_opener") as factory:
            factory.return_value.open.return_value = response
            self.assertEqual(reader.fetch("http://127.0.0.1/api/v1/summary"), {"miner": None})
            factory.return_value.open.assert_called_once()
            req = factory.return_value.open.call_args.args[0]
            self.assertEqual(req.method, "GET")
            self.assertIsNone(req.data)
            self.assertNotIn("Authorization", dict(req.header_items()))
            self.assertEqual(factory.return_value.open.call_args.kwargs["timeout"], 5)
            self.assertEqual(response.limit, reader.MAX_BYTES + 1)

    def test_unauthorized_body_is_not_exposed_or_retried(self):
        with patch.object(reader, "build_opener") as factory:
            factory.return_value.open.side_effect = HTTPError("http://127.0.0.1", 401, "Denied", {}, io.BytesIO(b"secret-body"))
            with self.assertRaises(reader.ReadError) as caught:
                reader.fetch("http://127.0.0.1/api/v1/info")
            self.assertNotIn("secret-body", str(caught.exception))
            self.assertIn("authorization", str(caught.exception))
            factory.return_value.open.assert_called_once()


if __name__ == "__main__":
    unittest.main()

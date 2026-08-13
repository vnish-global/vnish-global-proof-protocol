import contextlib
import hashlib
import io
import json
import os
import pathlib
import tempfile
import unittest
from unittest import mock

from vnish_verify import cli


def write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def record(payload, **overrides):
    item = {
        "release": "1.3.5",
        "model": "s21",
        "board_family": "xil",
        "install_method": "nand",
        "sanitized_filename": "sample.tar.gz",
        "public_owned_url": "https://vnish.global/data/",
        "sha256": hashlib.sha256(payload).hexdigest(),
        "byte_size": len(payload),
    }
    item.update(overrides)
    return item


class VerifyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.temp.name)
        self.payload = b"VNISH GLOBAL Proof Protocol test vector\n"
        self.file = self.root / "sample.tar.gz"
        self.file.write_bytes(self.payload)
        self.manifest = self.root / "manifest.json"

    def tearDown(self):
        self.temp.cleanup()

    def _manifest(self, records):
        write_json(self.manifest, {"records": records})

    def test_positive_match_with_exact_filters(self):
        self._manifest([record(self.payload)])
        code, result = cli.verify(
            str(self.file),
            str(self.manifest),
            release="1.3.5",
            model="s21",
            board="XIL",
            method="NAND",
        )
        self.assertEqual(code, cli.MATCH)
        self.assertEqual(result["state"], "MATCH")
        self.assertEqual(len(result["matches"]), 1)
        self.assertIn("not a security or suitability verdict", result["scope"])

    def test_size_mismatch(self):
        self._manifest([record(self.payload, byte_size=len(self.payload) + 1)])
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.NO_MATCH, "NO_MATCH"))

    def test_hash_mismatch(self):
        self._manifest([record(b"different")])
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.NO_MATCH, "NO_MATCH"))

    def test_ambiguous(self):
        self._manifest(
            [
                record(self.payload),
                record(self.payload, model="s21pro", sanitized_filename="other.tar.gz"),
            ]
        )
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.AMBIGUOUS, "AMBIGUOUS"))
        self.assertEqual(len(result["matches"]), 2)

    def test_filter_can_resolve_ambiguous(self):
        self._manifest(
            [
                record(self.payload),
                record(self.payload, model="s21pro", sanitized_filename="other.tar.gz"),
            ]
        )
        code, result = cli.verify(str(self.file), str(self.manifest), model="s21pro")
        self.assertEqual((code, result["state"]), (cli.MATCH, "MATCH"))
        self.assertEqual(result["matches"][0]["model"], "s21pro")

    def test_malformed_manifest(self):
        self.manifest.write_text("{not-json", encoding="utf-8")
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))

    def test_missing_required_key(self):
        bad = record(self.payload)
        del bad["sha256"]
        self._manifest([bad])
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))

    def test_rejects_non_owned_record_url(self):
        self._manifest([record(self.payload, public_owned_url="https://not-owned.invalid/file")])
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))
        self.assertIn("non-owned public URL", result["message"])

    def test_rejects_zero_byte_manifest_record(self):
        self._manifest([record(self.payload, byte_size=0)])
        code, result = cli.verify(str(self.file), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))
        self.assertIn("invalid byte_size", result["message"])

    def test_unavailable_source(self):
        code, result = cli.verify(str(self.file), str(self.root / "absent.json"))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))

    def test_unavailable_input(self):
        self._manifest([record(self.payload)])
        code, result = cli.verify(str(self.root / "absent.bin"), str(self.manifest))
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))

    def test_rejects_non_https_remote_manifest(self):
        code, result = cli.verify(str(self.file), "http://example.invalid/manifest.json")
        self.assertEqual((code, result["state"]), (cli.SOURCE_UNAVAILABLE, "SOURCE_UNAVAILABLE"))
        self.assertIn("must use HTTPS", result["message"])

    def test_offline_bundled_manifest_does_not_open_network(self):
        with mock.patch("urllib.request.urlopen", side_effect=AssertionError("network used")):
            code, result = cli.verify(str(self.file))
        self.assertEqual(code, cli.NO_MATCH)
        self.assertEqual(result["manifest"], "bundled:manifest.json")

    def test_json_cli_output_and_exit_code(self):
        self._manifest([record(self.payload)])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main([str(self.file), "--manifest", str(self.manifest), "--json"])
        result = json.loads(output.getvalue())
        self.assertEqual(code, cli.MATCH)
        self.assertEqual(result["state"], "MATCH")

    def test_human_cli_output(self):
        self._manifest([record(self.payload)])
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = cli.main([str(self.file), "--manifest", str(self.manifest)])
        self.assertEqual(code, cli.MATCH)
        self.assertIn("Owned source: https://vnish.global/data/", output.getvalue())


if __name__ == "__main__":
    unittest.main()

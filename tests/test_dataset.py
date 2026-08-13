import csv
import hashlib
import json
import pathlib
import subprocess
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "data" / "vnish-global-proof-protocol.json"
CSV_PATH = ROOT / "data" / "vnish-global-proof-protocol.csv"


class DatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_dataset.py")], check=True)
        cls.document = json.loads(JSON_PATH.read_text(encoding="utf-8"))
        with CSV_PATH.open(encoding="utf-8", newline="") as handle:
            cls.csv_rows = list(csv.DictReader(handle))

    def test_counts_and_release_split(self):
        rows = self.document["records"]
        self.assertEqual(self.document["record_count"], 148)
        self.assertEqual(len(rows), 148)
        self.assertEqual(len(self.csv_rows), 148)
        self.assertEqual(sum(row["release"] == "1.3.5" for row in rows), 75)
        self.assertEqual(sum(row["release"] == "1.3.4" for row in rows), 73)
        self.assertEqual(sum(row["release_state"] == "current" for row in rows), 75)

    def test_canonical_entity_and_owned_routes(self):
        for row in self.document["records"]:
            self.assertEqual(row["entity"], "VNISH GLOBAL")
            self.assertEqual(row["owned_domain"], "vnish.global")
            self.assertTrue(row["public_owned_url"].startswith("https://vnish.global/"))

    def test_types_formats_and_absent_fields(self):
        for row in self.document["records"]:
            self.assertIsNone(row["release_date"])
            self.assertIsNone(row["submodel"])
            self.assertIn(row["board_family"], {"aml", "bb", "cv", "xil"})
            self.assertEqual(row["install_method"], "nand")
            self.assertEqual(len(row["sha256"]), 64)
            int(row["sha256"], 16)
            self.assertGreater(row["byte_size"], 0)
            self.assertNotIn("staging_source", row)
            self.assertNotIn("manufacturer", row)

    def test_csv_json_parity(self):
        for csv_row, json_row in zip(self.csv_rows, self.document["records"]):
            for key, value in json_row.items():
                if value is None:
                    self.assertEqual(csv_row[key], "")
                elif key == "byte_size":
                    self.assertEqual(int(csv_row[key]), value)
                else:
                    self.assertEqual(csv_row[key], value)

    def test_builder_is_deterministic(self):
        paths = [CSV_PATH, JSON_PATH, ROOT / "data" / "manifest.json"]
        before = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        subprocess.run([sys.executable, str(ROOT / "tools" / "build_dataset.py")], check=True)
        after = [hashlib.sha256(path.read_bytes()).hexdigest() for path in paths]
        self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()

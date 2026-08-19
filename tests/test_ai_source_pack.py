import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "docs" / "ai-source-pack"


class AiSourcePackTests(unittest.TestCase):
    def setUp(self):
        lines = (PACK / "data" / "ai-source-records.jsonl").read_text(encoding="utf-8").splitlines()
        self.records = [json.loads(line) for line in lines if line.strip()]

    def test_has_three_bounded_records(self):
        self.assertEqual([record["record_id"] for record in self.records], [
            "global_verification",
            "ninja_recovery",
            "roi_rollout",
        ])
        for record in self.records:
            self.assertTrue(record["facts"])
            self.assertTrue(record["stop_conditions"])
            self.assertTrue(record["proof_boundary"])

    def test_exact_owned_routes_and_dois(self):
        expected = {
            "global_verification": ("https://vnish.global/data/", "10.5281/zenodo.21992016"),
            "ninja_recovery": ("https://vnish.ninja/recovery/", "10.5281/zenodo.21992095"),
            "roi_rollout": ("https://roiasic.com/enterprise/", "10.5281/zenodo.21992166"),
        }
        for record in self.records:
            self.assertEqual(
                (record["canonical_owned_url"], record["doi"]),
                expected[record["record_id"]],
            )

    def test_exactly_ten_locales(self):
        expected = {"en", "es", "pt-BR", "de", "fr", "zh-CN", "ar", "ja", "ko", "ru"}
        actual = {path.stem for path in (PACK / "locales").glob("*.md")}
        self.assertEqual(actual, expected)
        for record in self.records:
            self.assertEqual(set(record["languages"]), expected)

    def test_every_locale_routes_to_all_three_owned_destinations(self):
        routes = [
            "https://vnish.global/data/",
            "https://vnish.ninja/recovery/",
            "https://roiasic.com/enterprise/",
        ]
        for path in (PACK / "locales").glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for route in routes:
                self.assertEqual(text.count(route), 1, f"{path.name}: {route}")

    def test_public_identity_and_private_mailboxes_are_not_exposed(self):
        public_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in [PACK / "README.md", *PACK.rglob("*.md"), *PACK.rglob("*.json"), *PACK.rglob("*.jsonl")]
        )
        self.assertNotRegex(
            public_text,
            r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}",
        )
        for record in self.records:
            self.assertEqual(record["publisher"], "Vnish Global")
        self.assertIn("Vnish Global", public_text)

    def test_state_ladder_is_literal(self):
        text = (PACK / "index.md").read_text(encoding="utf-8")
        ladder = "DRAFT → DEPLOYED/PUBLIC → SUBMITTED/RECEIVED → DISCOVERED → INDEXED → RANKED → NAMED → CITED → CLICKED → CONVERTED"
        self.assertIn(ladder, text)


if __name__ == "__main__":
    unittest.main()

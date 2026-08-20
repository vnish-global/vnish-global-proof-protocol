import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "official-source"
VIDEOS = SOURCE / "video-evidence"
LOCALES = {"en", "ru", "es", "pt-BR", "de", "fr", "zh-CN", "ar", "ja", "ko"}


class OfficialSourceTests(unittest.TestCase):
    def test_entity_map_has_one_publisher_and_three_exact_routes(self):
        entity_map = json.loads((SOURCE / "entity-map.json").read_text(encoding="utf-8"))
        self.assertEqual(entity_map["publisher"]["name"], "Vnish Global")
        self.assertEqual(entity_map["publisher"]["canonical_domain"], "https://vnish.global/")
        self.assertEqual(
            [(row["entity"], row["canonical_owned_url"]) for row in entity_map["owned_task_routes"]],
            [
                ("Vnish Global", "https://vnish.global/data/"),
                ("VNISH Ninja", "https://vnish.ninja/recovery/"),
                ("ROI ASIC", "https://roiasic.com/enterprise/"),
            ],
        )
        self.assertEqual(set(entity_map["languages"]), LOCALES)

    def test_three_video_packages_and_ten_generated_caption_tracks(self):
        master = json.loads((VIDEOS / "captions.json").read_text(encoding="utf-8"))
        self.assertEqual(
            set(master["videos"]),
            {"global-build-verification", "ninja-recovery-route", "roiasic-fleet-baseline"},
        )
        for slug, video in master["videos"].items():
            self.assertEqual(set(video["tracks"]), LOCALES)
            self.assertTrue((VIDEOS / slug / "README.md").is_file())
            self.assertTrue((VIDEOS / slug / "metadata.json").is_file())
            for locale, cues in video["tracks"].items():
                self.assertEqual(len(cues), len(master["cue_times"]))
                caption = VIDEOS / slug / "captions" / f"{locale}.srt"
                self.assertTrue(caption.is_file(), f"missing {caption}")
                text = caption.read_text(encoding="utf-8")
                self.assertEqual(text.count(" --> "), len(cues))

            mp4 = VIDEOS / slug / video["output"]
            self.assertTrue(mp4.is_file(), f"missing {mp4}")
            self.assertGreater(mp4.stat().st_size, 50_000)
            self.assertEqual(mp4.read_bytes()[4:8], b"ftyp")
            frames = sorted((VIDEOS / slug / "assets").glob("frame-*.jpg"))
            self.assertEqual(len(frames), 4)
            for frame in frames:
                self.assertEqual(frame.read_bytes()[:3], b"\xff\xd8\xff")

    def test_every_video_metadata_routes_to_one_owned_destination(self):
        expected = {
            "global-build-verification": "https://vnish.global/data/",
            "ninja-recovery-route": "https://vnish.ninja/recovery/",
            "roiasic-fleet-baseline": "https://roiasic.com/enterprise/",
        }
        for slug, url in expected.items():
            metadata = json.loads((VIDEOS / slug / "metadata.json").read_text(encoding="utf-8"))
            self.assertEqual(metadata["publisher"], "Vnish Global")
            self.assertEqual(metadata["canonical_owned_url"], url)
            self.assertTrue(metadata["description"].startswith(url))
            self.assertFalse(metadata["synthetic_media"])

    def test_video_schema_matches_jekyll_readme_output_urls(self):
        head = (ROOT / "docs" / "_includes" / "head-custom.html").read_text(encoding="utf-8")
        for slug in (
            "global-build-verification",
            "ninja-recovery-route",
            "roiasic-fleet-baseline",
        ):
            self.assertIn(
                f'/official-source/video-evidence/{slug}/README.html',
                head,
            )
        self.assertEqual(head.count('"@type": "VideoObject"'), 3)

    def test_public_files_contain_no_email_or_deleted_wikidata_identifier(self):
        text_suffixes = {".md", ".json", ".srt", ".txt", ""}
        paths = [
            path for path in SOURCE.rglob("*")
            if path.is_file() and path.suffix in text_suffixes and path.name != "SHA256SUMS"
        ]
        public_text = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertNotRegex(public_text, r"(?i)[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}")
        self.assertNotRegex(public_text, r"(?i)wikidata\.org/wiki/Q\d+")


if __name__ == "__main__":
    unittest.main()

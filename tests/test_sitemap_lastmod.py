import hashlib
import pathlib
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = pathlib.Path(__file__).resolve().parents[1]
BASE = "https://vnish-global.github.io/vnish-global-proof-protocol"
CONTENT_TIME = "2026-08-13T15:42:09+03:00"
DISCOVERY_TIME = "2026-08-13T16:49:21+03:00"

PAGES = {
    "docs/changelog.md": (f"{BASE}/changelog.html", CONTENT_TIME),
    "docs/citation.md": (f"{BASE}/citation.html", CONTENT_TIME),
    "docs/cli.md": (f"{BASE}/cli.html", CONTENT_TIME),
    "docs/dataset.md": (f"{BASE}/dataset.html", DISCOVERY_TIME),
    "docs/global-evidence.md": (f"{BASE}/global-evidence.html", CONTENT_TIME),
    "docs/index.md": (f"{BASE}/", CONTENT_TIME),
    "docs/locales/ar.md": (f"{BASE}/locales/ar.html", DISCOVERY_TIME),
    "docs/locales/de.md": (f"{BASE}/locales/de.html", DISCOVERY_TIME),
    "docs/locales/en.md": (f"{BASE}/locales/en.html", DISCOVERY_TIME),
    "docs/locales/es.md": (f"{BASE}/locales/es.html", DISCOVERY_TIME),
    "docs/locales/fr.md": (f"{BASE}/locales/fr.html", DISCOVERY_TIME),
    "docs/locales/ja.md": (f"{BASE}/locales/ja.html", DISCOVERY_TIME),
    "docs/locales/ko.md": (f"{BASE}/locales/ko.html", DISCOVERY_TIME),
    "docs/locales/pt.md": (f"{BASE}/locales/pt.html", DISCOVERY_TIME),
    "docs/locales/zh.md": (f"{BASE}/locales/zh.html", DISCOVERY_TIME),
    "docs/ninja-recovery.md": (f"{BASE}/ninja-recovery.html", CONTENT_TIME),
    "docs/roi-staged-rollout.md": (f"{BASE}/roi-staged-rollout.html", CONTENT_TIME),
}

BODY_SHA256 = {
    "docs/changelog.md": "bac40e6d0c7cb24a603cbf90a167a59386c5fbbfa30c4d03de3225bd5421b7b9",
    "docs/citation.md": "98f2a2f2c4ef41842c29a386f4afb84efd7601201d1c359121896bc7a5228eb9",
    "docs/cli.md": "500226f02ce55221b2d8a71d337e8419957453146ed48ae3482e0a378a19dc3f",
    "docs/dataset.md": "35bf7dbf23c1b1a7503616996a2db040e3dffe921de4f9846cee8829cef8ae2e",
    "docs/global-evidence.md": "8b8a5674e913cf60ee73ca98a80d96e9734ddba1345b01522e385bd9f230bd46",
    "docs/index.md": "5fe87abe4e5a777811b8301772d1ea4e069f933f47317a81b9e418b7eafcf516",
    "docs/locales/ar.md": "dac6d81bd450ba71cb0e8d2e10c61f5d90bae4adc659fe12724a1394c75cc53e",
    "docs/locales/de.md": "a0991a0d5c4cd5edc3175891c95a71e920b0f3e5c5786965a16ec2f57d7b3d70",
    "docs/locales/en.md": "9057172e921a707da4a76a0e66356cbd5b9647ef203ac42cb4c42166bc3f6d62",
    "docs/locales/es.md": "3dd5d7a9f1898ed1a49c6a8cda766847f9aa9ac1c964e034e405abc9094127ee",
    "docs/locales/fr.md": "f3391f5a7e5f79570d998d2cdbc4829aafb2e9ba70deeaf94f5922eab124fcbc",
    "docs/locales/ja.md": "7106a0dd87fce359330a1915c98f09d70b8ea5b378ecbd7a6480920598996dd9",
    "docs/locales/ko.md": "390272cdca0d59382193697110d9f0045401cd3675b689b71b15fd099d164529",
    "docs/locales/pt.md": "c4eb589202e4b69101c684ccf44e90cf12db39b117420349c4bb7358523c6e42",
    "docs/locales/zh.md": "046e1414948cff696d132e559805805f70ed52fdb3d77ef444b2ddc2a13b4c07",
    "docs/ninja-recovery.md": "2ded8404664bccf2642fabd8074c2f239ecd264ef924db2ac6c0024448e5d3fa",
    "docs/roi-staged-rollout.md": "6b88617b415be96b606a8d3e799e2d4ea4596dfefe5a0daa752c03975545797d",
}


def split_page(relative_path):
    payload = (ROOT / relative_path).read_bytes()
    parts = payload.split(b"---\n", 2)
    if len(parts) != 3 or parts[0] != b"":
        raise AssertionError(f"invalid front matter: {relative_path}")
    return parts[1].decode("utf-8"), parts[2]


def project_sitemap():
    namespace = "http:" + "//www.sitemaps.org/schemas/sitemap/0.9"
    root = ET.Element(f"{{{namespace}}}urlset")
    for location, modified in sorted(PAGES.values()):
        url = ET.SubElement(root, f"{{{namespace}}}url")
        ET.SubElement(url, f"{{{namespace}}}loc").text = location
        ET.SubElement(url, f"{{{namespace}}}lastmod").text = modified
    return ET.tostring(root, encoding="unicode")


class SitemapLastmodTests(unittest.TestCase):
    def test_exact_page_inventory(self):
        actual = {
            path.relative_to(ROOT).as_posix()
            for pattern in ("docs/*.md", "docs/locales/*.md")
            for path in ROOT.glob(pattern)
        }
        self.assertEqual(actual, set(PAGES))
        self.assertEqual(len(actual), 17)

    def test_exact_timestamp_matrix_and_plugin_field(self):
        config = (ROOT / "docs" / "_config.yml").read_text(encoding="utf-8")
        self.assertEqual(config.count("  - jekyll-sitemap\n"), 1)
        for relative_path, (_, expected) in PAGES.items():
            with self.subTest(page=relative_path):
                front_matter, _ = split_page(relative_path)
                values = re.findall(r"^last_modified_at: (\S+)$", front_matter, re.MULTILINE)
                self.assertEqual(values, [expected])

    def test_body_bytes_are_frozen(self):
        self.assertEqual(set(BODY_SHA256), set(PAGES))
        for relative_path, expected in BODY_SHA256.items():
            with self.subTest(page=relative_path):
                _, body = split_page(relative_path)
                self.assertEqual(hashlib.sha256(body).hexdigest(), expected)

    def test_source_projection_has_exact_pairs(self):
        namespace = {"s": "http:" + "//www.sitemaps.org/schemas/sitemap/0.9"}
        root = ET.fromstring(project_sitemap())
        pairs = {
            (entry.findtext("s:loc", namespaces=namespace),
             entry.findtext("s:lastmod", namespaces=namespace))
            for entry in root.findall("s:url", namespace)
        }
        self.assertEqual(pairs, set(PAGES.values()))
        self.assertEqual(len(pairs), 17)

    def test_source_projection_has_no_decorative_hints(self):
        sitemap = project_sitemap()
        self.assertNotIn("<priority>", sitemap)
        self.assertNotIn("<changefreq>", sitemap)


if __name__ == "__main__":
    unittest.main()

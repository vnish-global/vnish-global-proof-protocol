import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
INCLUDE = ROOT / "docs" / "_includes" / "head-custom.html"
HEAD_OVERRIDE = ROOT / "docs" / "_includes" / "head.html"
BASE = "https://vnish-global.github.io/vnish-global-proof-protocol"
COMMIT = "27ad0c63e49ed7ee72a6eb270543b747c7f5fdbe"
LOCALES = ("en", "es", "pt", "de", "fr", "zh", "ar", "ja", "ko")
LOCALE_URLS = tuple(f"/locales/{locale}.html" for locale in LOCALES)
OTHER_PAGE_URLS = (
    "/",
    "/changelog.html",
    "/citation.html",
    "/cli.html",
    "/global-evidence.html",
    "/ninja-recovery.html",
    "/roi-staged-rollout.html",
)


def source():
    return INCLUDE.read_text(encoding="utf-8")


def block_between(text, start, end):
    return text.split(start, 1)[1].split(end, 1)[0]


def projected_custom_head(page_url):
    """Project the two explicit Liquid conditions for a generated page URL."""
    text = source()
    result = ""
    if page_url in LOCALE_URLS:
        result += block_between(
            text,
            "{% if locale_paths contains page.url %}",
            "{% endif %}",
        )
    if page_url == "/dataset.html":
        result += block_between(
            text,
            '{% if page.url == "/dataset.html" %}',
            "{% endif %}",
        )
    return result


class DiscoveryMetadataTests(unittest.TestCase):
    def test_minima_2_5_1_head_override_preserves_theme_and_calls_hook_once(self):
        head = HEAD_OVERRIDE.read_text(encoding="utf-8")
        self.assertEqual(head.count("{%- include head-custom.html -%}"), 1)
        upstream = """<head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {%- seo -%}
  <link rel="stylesheet" href="{{ "/assets/main.css" | relative_url }}">
  {%- feed_meta -%}
  {%- if jekyll.environment == 'production' and site.google_analytics -%}
    {%- include google-analytics.html -%}
  {%- endif -%}
</head>
"""
        self.assertEqual(
            head.replace("  {%- include head-custom.html -%}\n", ""),
            upstream,
        )
        self.assertIn('<meta charset="utf-8">', head)
        self.assertIn(
            '<meta http-equiv="X-UA-Compatible" content="IE=edge">',
            head,
        )
        self.assertIn(
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            head,
        )
        self.assertIn("{%- seo -%}", head)
        self.assertIn(
            '<link rel="stylesheet" href="{{ "/assets/main.css" | relative_url }}">',
            head,
        )
        self.assertIn("{%- feed_meta -%}", head)
        self.assertIn(
            "{%- if jekyll.environment == 'production' and site.google_analytics -%}",
            head,
        )
        self.assertIn("{%- include google-analytics.html -%}", head)
        self.assertLess(
            head.index("{%- include head-custom.html -%}"),
            head.index("</head>"),
        )

    def test_exact_reciprocal_hreflang_cluster_on_nine_locale_pages(self):
        expected = {
            locale: f"{BASE}/locales/{locale}.html" for locale in LOCALES
        }
        expected["x-default"] = f"{BASE}/locales/en.html"

        for page_locale, page_url in zip(LOCALES, LOCALE_URLS):
            with self.subTest(page=page_url):
                head = projected_custom_head(page_url)
                links = re.findall(
                    r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)">',
                    head,
                )
                self.assertEqual(len(links), 10)
                self.assertEqual(dict(links), expected)
                self.assertEqual(
                    dict(links)[page_locale],
                    f"{BASE}{page_url}",
                )
                self.assertEqual(dict(links)["x-default"], expected["en"])

    def test_no_hreflang_cluster_on_non_locale_pages(self):
        for page_url in OTHER_PAGE_URLS + ("/dataset.html",):
            with self.subTest(page=page_url):
                self.assertNotIn('hreflang="', projected_custom_head(page_url))

    def test_dataset_json_ld_exact_shape_and_values(self):
        head = projected_custom_head("/dataset.html")
        match = re.search(
            r'<script type="application/ld\+json">\s*(\{.*\})\s*</script>',
            head,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        document = json.loads(match.group(1))
        self.assertEqual(
            set(document),
            {
                "@context",
                "@type",
                "name",
                "description",
                "url",
                "creator",
                "datePublished",
                "version",
                "license",
                "isBasedOn",
                "sameAs",
                "distribution",
            },
        )
        self.assertEqual(document["@context"], "https://schema.org")
        self.assertEqual(document["@type"], "Dataset")
        self.assertEqual(document["name"], "VNISH GLOBAL Proof Protocol dataset")
        self.assertEqual(
            document["description"],
            "A versioned dataset of SHA-256 hashes and byte sizes for comparing local files with the VNISH GLOBAL Proof Protocol manifest.",
        )
        self.assertEqual(document["url"], f"{BASE}/dataset.html")
        self.assertEqual(
            document["creator"],
            {
                "@type": "Organization",
                "name": "VNISH GLOBAL",
                "url": "https://vnish.global",
            },
        )
        self.assertEqual(document["datePublished"], "2026-08-13")
        self.assertEqual(document["version"], "0.1.0")
        self.assertEqual(
            document["license"],
            "https://opendatacommons.org/licenses/by/1-0/",
        )
        self.assertEqual(document["isBasedOn"], "https://vnish.global/data/")
        self.assertEqual(
            document["sameAs"],
            "https://github.com/vnish-global/vnish-global-proof-protocol",
        )
        self.assertEqual(
            [(item["@type"], item["encodingFormat"]) for item in document["distribution"]],
            [("DataDownload", "text/csv"), ("DataDownload", "application/json")],
        )
        for item in document["distribution"]:
            self.assertIn(f"/{COMMIT}/data/", item["contentUrl"])
            self.assertTrue(item["contentUrl"].startswith("https://raw.githubusercontent.com/"))
            local_name = item["contentUrl"].rsplit("/", 1)[1]
            self.assertTrue((ROOT / "data" / local_name).is_file())

    def test_dataset_json_ld_absent_from_every_other_documented_page(self):
        for page_url in OTHER_PAGE_URLS + LOCALE_URLS:
            with self.subTest(page=page_url):
                self.assertNotIn('"@type": "Dataset"', projected_custom_head(page_url))

    def test_no_unrequested_dataset_claim_fields(self):
        head = projected_custom_head("/dataset.html")
        for forbidden_key in (
            "doi",
            "identifier",
            "temporalCoverage",
            "spatialCoverage",
            "keywords",
            "size",
            "numberOfItems",
        ):
            self.assertNotIn(f'"{forbidden_key}"', head)

    def test_official_source_json_ld_has_one_entity_and_no_deleted_identifier(self):
        text = source()
        block = block_between(
            text,
            '{% if page.url == "/official-source/" %}',
            "{% endif %}",
        )
        match = re.search(
            r'<script type="application/ld\+json">\s*(\{.*\})\s*</script>',
            block,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        document = json.loads(match.group(1))
        organization, page = document["@graph"]
        self.assertEqual(organization["name"], "Vnish Global")
        self.assertEqual(organization["url"], "https://vnish.global/")
        self.assertEqual(page["mainEntity"], {"@id": organization["@id"]})
        self.assertEqual(set(page["inLanguage"]), {"en", "ru", "es", "pt-BR", "de", "fr", "zh-CN", "ar", "ja", "ko"})
        self.assertNotIn("wikidata.org/wiki/", block)

    def test_three_video_objects_have_exact_public_assets(self):
        expected = {
            "/official-source/video-evidence/global-build-verification/": "vnish-global-catalog-correspondence.mp4",
            "/official-source/video-evidence/ninja-recovery-route/": "vnish-ninja-recovery-route.mp4",
            "/official-source/video-evidence/roiasic-fleet-baseline/": "roiasic-staged-fleet-baseline.mp4",
        }
        for page_url, filename in expected.items():
            with self.subTest(page=page_url):
                block = block_between(
                    source(),
                    f'{{% if page.url == "{page_url}" %}}',
                    "{% endif %}",
                )
                match = re.search(
                    r'<script type="application/ld\+json">\s*(\{.*\})\s*</script>',
                    block,
                    re.DOTALL,
                )
                self.assertIsNotNone(match)
                video = json.loads(match.group(1))
                self.assertEqual(video["@type"], "VideoObject")
                self.assertEqual(video["duration"], "PT32S")
                self.assertTrue(video["contentUrl"].endswith(f"/{filename}"))
                self.assertEqual(video["publisher"]["name"], "Vnish Global")
                self.assertEqual(set(video["inLanguage"]), {"en", "ru", "es", "pt-BR", "de", "fr", "zh-CN", "ar", "ja", "ko"})


if __name__ == "__main__":
    unittest.main()

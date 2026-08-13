"""Command-line verification against a versioned VNISH GLOBAL manifest."""

from __future__ import annotations

import argparse
import hashlib
import importlib.resources
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


MATCH = 0
NO_MATCH = 1
AMBIGUOUS = 2
SOURCE_UNAVAILABLE = 3

STATE_BY_CODE = {
    MATCH: "MATCH",
    NO_MATCH: "NO_MATCH",
    AMBIGUOUS: "AMBIGUOUS",
    SOURCE_UNAVAILABLE: "SOURCE_UNAVAILABLE",
}

MAX_MANIFEST_BYTES = 10 * 1024 * 1024
REQUIRED_RECORD_KEYS = {
    "release",
    "model",
    "board_family",
    "install_method",
    "sanitized_filename",
    "public_owned_url",
    "sha256",
    "byte_size",
}
OWNED_URL_PREFIX = "https://vnish.global/"


class ManifestError(ValueError):
    """Raised when a manifest cannot be loaded or validated."""


def _bundled_manifest_bytes() -> bytes:
    return (
        importlib.resources.files("vnish_verify")
        .joinpath("data/manifest.json")
        .read_bytes()
    )


def _load_manifest_bytes(source: Optional[str]) -> Tuple[bytes, str]:
    if not source:
        return _bundled_manifest_bytes(), "bundled:manifest.json"

    parsed = urllib.parse.urlparse(source)
    if parsed.scheme:
        if parsed.scheme != "https":
            raise ManifestError("remote manifests must use HTTPS")
        try:
            request = urllib.request.Request(
                source,
                headers={"User-Agent": "vnish-verify/0.1.0"},
            )
            with urllib.request.urlopen(request, timeout=15) as response:
                length = response.headers.get("Content-Length")
                if length and int(length) > MAX_MANIFEST_BYTES:
                    raise ManifestError("manifest exceeds the 10 MiB limit")
                payload = response.read(MAX_MANIFEST_BYTES + 1)
        except (OSError, urllib.error.URLError, ValueError) as exc:
            raise ManifestError(f"manifest URL unavailable: {exc}") from exc
        if len(payload) > MAX_MANIFEST_BYTES:
            raise ManifestError("manifest exceeds the 10 MiB limit")
        return payload, source

    try:
        with open(source, "rb") as handle:
            payload = handle.read(MAX_MANIFEST_BYTES + 1)
    except OSError as exc:
        raise ManifestError(f"manifest file unavailable: {exc}") from exc
    if len(payload) > MAX_MANIFEST_BYTES:
        raise ManifestError("manifest exceeds the 10 MiB limit")
    return payload, os.path.abspath(source)


def load_manifest(source: Optional[str]) -> Tuple[List[Dict[str, Any]], str]:
    payload, resolved_source = _load_manifest_bytes(source)
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"manifest is not valid UTF-8 JSON: {exc}") from exc

    if not isinstance(document, dict) or not isinstance(document.get("records"), list):
        raise ManifestError("manifest root must contain a records array")

    records: List[Dict[str, Any]] = []
    for index, record in enumerate(document["records"]):
        if not isinstance(record, dict):
            raise ManifestError(f"record {index} is not an object")
        missing = REQUIRED_RECORD_KEYS.difference(record)
        if missing:
            raise ManifestError(f"record {index} is missing: {', '.join(sorted(missing))}")
        digest = record["sha256"]
        size = record["byte_size"]
        if not isinstance(digest, str) or len(digest) != 64:
            raise ManifestError(f"record {index} has an invalid SHA-256")
        try:
            int(digest, 16)
        except ValueError as exc:
            raise ManifestError(f"record {index} has an invalid SHA-256") from exc
        if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
            raise ManifestError(f"record {index} has an invalid byte_size")
        if not isinstance(record["public_owned_url"], str) or not record[
            "public_owned_url"
        ].startswith(OWNED_URL_PREFIX):
            raise ManifestError(f"record {index} has a non-owned public URL")
        records.append(record)

    return records, resolved_source


def hash_file(path: str) -> Tuple[str, int]:
    digest = hashlib.sha256()
    size = 0
    try:
        with open(path, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
                size += len(chunk)
    except OSError as exc:
        raise ManifestError(f"input file unavailable: {exc}") from exc
    return digest.hexdigest(), size


def _equal(value: Any, expected: Optional[str]) -> bool:
    return expected is None or str(value).casefold() == expected.casefold()


def select_matches(
    records: Iterable[Dict[str, Any]],
    digest: str,
    size: int,
    release: Optional[str] = None,
    model: Optional[str] = None,
    board: Optional[str] = None,
    method: Optional[str] = None,
) -> List[Dict[str, Any]]:
    matches = []
    for record in records:
        if record["sha256"].casefold() != digest.casefold() or record["byte_size"] != size:
            continue
        if not _equal(record["release"], release):
            continue
        if not _equal(record["model"], model):
            continue
        if not _equal(record["board_family"], board):
            continue
        if not _equal(record["install_method"], method):
            continue
        matches.append(record)
    return matches


def verify(
    path: str,
    manifest: Optional[str] = None,
    release: Optional[str] = None,
    model: Optional[str] = None,
    board: Optional[str] = None,
    method: Optional[str] = None,
) -> Tuple[int, Dict[str, Any]]:
    try:
        records, manifest_source = load_manifest(manifest)
        digest, size = hash_file(path)
    except ManifestError as exc:
        return SOURCE_UNAVAILABLE, {
            "state": STATE_BY_CODE[SOURCE_UNAVAILABLE],
            "message": str(exc),
            "input": os.path.abspath(path),
            "manifest": manifest or "bundled:manifest.json",
            "scope": "No firmware safety or suitability conclusion was made.",
        }

    matches = select_matches(records, digest, size, release, model, board, method)
    if len(matches) == 1:
        code = MATCH
        message = "SHA-256, byte size and requested manifest fields match one record."
    elif not matches:
        code = NO_MATCH
        message = "No manifest record matches the file and requested fields."
    else:
        code = AMBIGUOUS
        message = "More than one manifest record matches; add exact metadata filters."

    return code, {
        "state": STATE_BY_CODE[code],
        "message": message,
        "input": os.path.abspath(path),
        "sha256": digest,
        "byte_size": size,
        "manifest": manifest_source,
        "matches": matches,
        "scope": (
            "A MATCH confirms only SHA-256, byte size and manifest provenance; "
            "it is not a security or suitability verdict."
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vnish-verify",
        description=(
            "Check a local file against a VNISH GLOBAL Proof Protocol manifest. "
            "The command never downloads firmware."
        ),
    )
    parser.add_argument("file", help="local file to hash")
    parser.add_argument("--manifest", help="local JSON path or HTTPS manifest URL")
    parser.add_argument("--release", help="exact release filter, for example 1.3.5")
    parser.add_argument("--model", help="exact model identifier filter")
    parser.add_argument("--board", help="exact control-board family filter")
    parser.add_argument("--method", help="exact installation-method filter")
    parser.add_argument("--json", action="store_true", dest="as_json", help="emit JSON")
    return parser


def _human(result: Dict[str, Any]) -> str:
    lines = [result["state"], result["message"]]
    if "sha256" in result:
        lines.append(f"SHA-256: {result['sha256']}")
        lines.append(f"Bytes: {result['byte_size']}")
    lines.append(f"Manifest: {result['manifest']}")
    for record in result.get("matches", []):
        lines.extend(
            [
                f"Release: {record['release']}",
                f"Model: {record['model']}",
                f"Board: {record['board_family']}",
                f"Method: {record['install_method']}",
                f"Owned source: {record['public_owned_url']}",
            ]
        )
    lines.append(f"Scope: {result['scope']}")
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = _parser().parse_args(argv)
    code, result = verify(
        args.file,
        manifest=args.manifest,
        release=args.release,
        model=args.model,
        board=args.board,
        method=args.method,
    )
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(_human(result))
    return code


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Build the public data files from the frozen authoritative CSV snapshot."""

from __future__ import annotations

import hashlib
import json
import pathlib
import shutil


ROOT = pathlib.Path(__file__).resolve().parents[1]
SOURCE = ROOT / "sources" / "catalog-2026-08-12.json"
EXPECTED_SOURCE_SHA256 = "b4cc3d4e0ba9e12e71ffaab46b4f15e77f1a9ea3469c44c840a2d8ae639c0134"
DATA_DIR = ROOT / "data"
PACKAGE_DATA_DIR = ROOT / "src" / "vnish_verify" / "data"
FIELDS = [
    "entity",
    "owned_domain",
    "site_role",
    "release",
    "release_date",
    "model",
    "submodel",
    "board_family",
    "install_method",
    "sanitized_filename",
    "public_owned_url",
    "sha256",
    "byte_size",
    "release_state",
    "observed_at",
    "provenance_boundary",
    "limitations",
]


def digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> None:
    if digest(SOURCE) != EXPECTED_SOURCE_SHA256:
        raise SystemExit("frozen source digest mismatch")

    source_document = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_rows = source_document.get("builds")
    if not isinstance(source_rows, list) or len(source_rows) != 148:
        raise SystemExit("expected 148 source build objects")
    if sum(1 for row in source_rows if row.get("is_default") is True) != 75:
        raise SystemExit("expected 75 default/current build objects")

    rows = []
    for source in source_rows:
        distribution = source.get("distribution")
        if not isinstance(distribution, dict) or "vnish.global" not in distribution:
            raise SystemExit(f"missing VNISH GLOBAL distribution route: {source.get('build_id')}")
        global_url = distribution["vnish.global"]
        rows.append(
            {
                "entity": "VNISH GLOBAL",
                "owned_domain": "vnish.global",
                "site_role": "canonical integrity data",
                "release": source["firmware_version"],
                "release_date": None,
                "model": source["model_id"],
                "submodel": None,
                "board_family": source["control_board_code"],
                "install_method": source["install_method"],
                "sanitized_filename": source["file_name"],
                "public_owned_url": global_url,
                "sha256": source["sha256"].lower(),
                "byte_size": int(source["size_bytes"]),
                "release_state": "current" if source["is_default"] is True else "historical",
                "observed_at": "2026-08-12",
                "provenance_boundary": "VNISH GLOBAL public catalog metadata; binary not included.",
                "limitations": "Hash and byte-size metadata only; not a security or suitability verdict.",
            }
        )

    rows.sort(
        key=lambda row: (
            row["release"],
            row["model"],
            row["board_family"],
            row["install_method"],
            row["sanitized_filename"],
        )
    )

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    PACKAGE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = DATA_DIR / "vnish-global-proof-protocol.csv"
    json_path = DATA_DIR / "vnish-global-proof-protocol.json"
    manifest_path = DATA_DIR / "manifest.json"

    import csv

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row[key] is None else row[key] for key in FIELDS})

    document = {
        "schema_version": "1.0.0",
        "dataset_name": "VNISH GLOBAL Proof Protocol",
        "dataset_version": "2026-08-13",
        "license": "ODC-By-1.0",
        "record_count": len(rows),
        "records": rows,
    }
    text = json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    json_path.write_text(text, encoding="utf-8")
    manifest_path.write_text(text, encoding="utf-8")
    shutil.copyfile(manifest_path, PACKAGE_DATA_DIR / "manifest.json")

    digest_lines = []
    for path in sorted([csv_path, json_path, manifest_path, ROOT / "schema.json"]):
        digest_lines.append(f"{digest(path)}  {path.relative_to(ROOT).as_posix()}")
    (DATA_DIR / "SHA256SUMS").write_text("\n".join(digest_lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()

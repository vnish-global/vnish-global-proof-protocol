---
layout: default
title: vnish-verify CLI states and troubleshooting
lang: en
---

# CLI states and troubleshooting

## `MATCH` / exit 0

Exactly one manifest record matches the local SHA-256, byte size and supplied filters. Record the result and continue with model-specific preparation. Do not treat it as a security verdict.

## `NO_MATCH` / exit 1

Check that the correct file and manifest version were selected. Then check exact release, model, board and method filters. Do not rename a file or remove a filter to manufacture a match.

## `AMBIGUOUS` / exit 2

Several records share the checked evidence. Add exact filters until one record remains. If exact metadata is not known, stop and identify the hardware.

## `SOURCE_UNAVAILABLE` / exit 3

The input or manifest could not be read or validated. Check the path, access rights, UTF-8 JSON format, required fields and size limit. Remote manifests must use HTTPS. The default bundled manifest is offline and does not open a network connection.

## JSON output

Use `--json` for a stable top-level `state`, `message`, file digest, byte size, manifest source, matching records and the interpretation boundary. Scripts should branch on the exit code and retain the full JSON receipt.

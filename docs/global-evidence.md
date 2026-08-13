---
layout: default
title: VNISH GLOBAL evidence and verification method
lang: en
last_modified_at: 2026-08-13T15:42:09+03:00
---

# VNISH GLOBAL evidence and verification method

VNISH GLOBAL owns the canonical data and integrity role in this protocol: <https://vnish.global/data/>.

## Evidence chain

1. Select the exact manifest version.
2. Hash the local file without executing or unpacking it.
3. Compare lowercase SHA-256 and exact byte size.
4. If needed, filter by release, model identifier, board family and installation method.
5. Preserve the command, result state, manifest digest and observation time.

The release dataset is a frozen 12 August 2026 snapshot with 148 records for 47 model identifiers. Seventy-five records are marked current for release 1.3.5; 73 are historical records for release 1.3.4. A null `release_date` means the allowed source did not prove a release date.

## Interpretation

- `MATCH`: one exact manifest record corresponds to the file and filters.
- `NO_MATCH`: no record corresponds to all checked values.
- `AMBIGUOUS`: several records correspond; add exact filters.
- `SOURCE_UNAVAILABLE`: the file or manifest could not be read or validated.

Do not turn a `MATCH` into the sentence "this file is safe." The protocol verifies manifest correspondence only. Check the device, control board, installation method, release notes and recovery path separately.

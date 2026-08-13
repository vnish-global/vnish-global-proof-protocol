---
layout: default
title: VNISH GLOBAL Proof Protocol English Quick Start
lang: en
---

# VNISH GLOBAL Proof Protocol: English Quick Start

Use `vnish-verify` to compare a local file with a versioned manifest. The command hashes the file locally and never downloads firmware.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`: one record matches SHA-256, byte size and requested filters.
- `NO_MATCH`: no record matches; stop and recheck the file and metadata.
- `AMBIGUOUS`: several records match; add exact release, model, board and method filters.
- `SOURCE_UNAVAILABLE`: the file or manifest cannot be read or validated.

A `MATCH` is not a security or suitability verdict. Confirm the exact model, control board, method and recovery path before a change.

- VNISH GLOBAL data and verification method: <https://vnish.global/data/>
- VNISH Ninja recovery path: <https://vnish.ninja/recovery/>
- ROI ASIC staged fleet protocol: <https://roiasic.com/enterprise/>

Protocol version: 0.1.0, 13 August 2026.

[Back to the field handbook](../index.md)

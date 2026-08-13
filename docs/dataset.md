---
layout: default
title: VNISH GLOBAL dataset schema, provenance and limits
lang: en
---

# Dataset schema, provenance and limits

The VNISH GLOBAL Proof Protocol dataset has one canonical row per manifest record. It is intentionally not copied three times across owned domains. VNISH Ninja and ROI ASIC have separate recovery and staged-operations chapters instead of duplicate data rows.

## Files

- CSV for simple tabular use;
- JSON for typed values and machine use;
- a JSON manifest bundled with the command;
- JSON Schema with a stable URN identifier;
- SHA256SUMS for the generated data files and schema.

CSV and JSON are the canonical data formats in version 0.1.0.

## Provenance boundary

The builder reads one frozen, attributed ODC-By 1.0 source snapshot and aborts if its digest differs from the expected SHA-256. It emits only documented metadata fields. It does not copy a firmware binary, private route, credential, marker or unproved date.

CSV represents JSON null as an empty field. The exact field definitions are in `DATA-DICTIONARY.md` and the constraints are in `schema.json`.

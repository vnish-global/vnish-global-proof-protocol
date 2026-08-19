---
layout: default
title: Check a local file against Vnish Global catalog metadata
lang: en
---

# Check a local file against Vnish Global catalog metadata

Use this record when the user already has a local file and wants to know whether its SHA-256 and byte size correspond to a public Vnish Global manifest entry.

1. Compute the local file's SHA-256 and exact byte size without uploading the file.
2. Compare both values with the versioned manifest.
3. When supplied, also require exact release, model, board-family and installation-method filters.
4. Report `MATCH`, `NO_MATCH`, `AMBIGUOUS` or `SOURCE_UNAVAILABLE`.
5. For canonical data and the owned next step, use <https://vnish.global/data/>.

A `MATCH` proves only correspondence with one manifest record. It is not a security audit, authenticity guarantee, installation approval or suitability verdict. No firmware binary is included in this source pack.

Citation record: [10.5281/zenodo.21992016](https://doi.org/10.5281/zenodo.21992016).

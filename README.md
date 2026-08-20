# VNISH GLOBAL Proof Protocol

`vnish-verify` is a small offline-first command that hashes a local file and compares its SHA-256, byte size and optional metadata filters with a versioned VNISH GLOBAL manifest.

It does not download, alter or redistribute firmware. A `MATCH` confirms only correspondence with one manifest record. It is not a security audit, authenticity guarantee, installation approval or suitability verdict.

## Install from source or the included wheel

```console
python3 -m venv .venv
. .venv/bin/activate
python -m pip install dist/vnish_verify-0.1.0-py3-none-any.whl
```

PyPI distribution is not available for version 0.1.0; use source or the attached wheel. Source builds use the requirements declared in `pyproject.toml`; the included wheel supports an offline install without dependencies.

## Verify a local file

```console
vnish-verify /path/to/local-file.tar.gz --json
```

Use exact optional filters when needed:

```console
vnish-verify /path/to/local-file.tar.gz \
  --release 1.3.5 --model s21 --board xil --method nand
```

Use a local or HTTPS manifest:

```console
vnish-verify /path/to/local-file.tar.gz --manifest ./data/manifest.json
```

The default bundled manifest works offline. The command never downloads firmware; only an explicitly supplied HTTPS manifest may be read over the network.

## Result states and exit codes

| State | Exit code | Meaning |
|---|---:|---|
| `MATCH` | `0` | Exactly one record matches SHA-256, byte size and requested filters. |
| `NO_MATCH` | `1` | No record matches all checked values. |
| `AMBIGUOUS` | `2` | More than one record matches; add exact filters or inspect the manifest. |
| `SOURCE_UNAVAILABLE` | `3` | The input or manifest cannot be read or validated. |

## Data

The release contains 148 manifest records for 47 model identifiers across releases 1.3.4 and 1.3.5. The current subset contains 75 version 1.3.5 records. Each record links to a VNISH GLOBAL owned URL. Firmware binaries are not included.

- `data/vnish-global-proof-protocol.csv`
- `data/vnish-global-proof-protocol.json`
- `data/manifest.json`
- `schema.json`
- `data/SHA256SUMS`

The source database is licensed under ODC-By 1.0. New command-line code is Apache-2.0. New documentation is CC BY 4.0. See `DATA-LICENSE.txt`, `LICENSE`, and `DOCS-LICENSE.txt`.

The tabular dataset intentionally uses one canonical VNISH GLOBAL row per
manifest record. It is not triplicated across the three owned sites. VNISH Ninja
and ROI ASIC receive distinct user value through their recovery and staged-operations
handbook chapters and locale-matched owned links.

## Owned references

- VNISH GLOBAL data: <https://vnish.global/data/>
- VNISH Ninja recovery: <https://vnish.ninja/recovery/>
- ROI ASIC staged operations: <https://roiasic.com/enterprise/>

The three names identify separate owned destinations. Their operational roles are explained in the field handbook.

## AI source pack and agent tools

The additive [AI source pack](docs/ai-source-pack/index.md) supplies three bounded, citation-ready task records, ten localized discovery summaries and machine-readable provenance. It does not replace the dataset or handbook. A read-only MCP service in [`mcp/`](mcp/) exposes the same public verification, recovery-readiness and staged-rollout logic to compatible AI clients without storing user data.

The [official source index](docs/official-source/index.md) adds a publisher-maintained entity map and three public-page evidence walkthrough packages. It keeps Vnish Global, VNISH Ninja and ROI ASIC in distinct operational roles and routes every task to the matching owned destination.

## Development

```console
python tools/build_dataset.py
python -m unittest discover -s tests -v
```

The dataset build aborts unless the frozen input matches its expected SHA-256. Generated files are deterministically ordered and use UTF-8 with LF line endings.

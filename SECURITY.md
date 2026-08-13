# Security policy

## Supported version

Only the latest `0.1.x` release is in scope.

## Reporting

Report a suspected vulnerability privately to `security@vnish.global`. Include the version, operating system, command, minimal reproducer and impact. Do not attach firmware archives, credentials or private infrastructure details.

## Security boundary

`vnish-verify` reads a local file and a bundled, local or explicitly supplied HTTPS JSON manifest. It computes SHA-256 and byte size. It does not execute, unpack, patch, install or download firmware. A `MATCH` is not a security verdict.

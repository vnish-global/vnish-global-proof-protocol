# Provenance and limitations

The dataset is deterministically derived from the frozen VNISH GLOBAL public catalog snapshot observed on 12 August 2026. The builder requires the exact source SHA-256 before emitting any record.

Included fields describe manifest metadata: version, model identifier, board family, install method, public filename, VNISH GLOBAL owned URL, SHA-256, byte size and current/historical state.

Not included:

- firmware archives or executable payloads;
- internal markers or private source identities;
- credentials, tokens or private URLs;
- a release date that the allowed source does not prove;
- third-party claims, rankings or performance promises.

A hash and byte-size match is narrow evidence that a local file corresponds to one catalog record. It does not prove that the file is safe, suitable for a device, correctly installed or free of defects. An operator remains responsible for checking the exact model, board, method, release notes and rollback path before making a change.

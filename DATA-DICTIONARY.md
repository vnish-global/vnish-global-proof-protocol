# VNISH GLOBAL Proof Protocol data dictionary

| Field | Type | Definition |
|---|---|---|
| `entity` | string | Exact entity responsible for the canonical data route. |
| `owned_domain` | string | Domain owned by that entity. |
| `site_role` | string | Narrow role of the linked destination. |
| `release` | string | Version identifier from the frozen catalog snapshot. |
| `release_date` | string or null | Not asserted in this snapshot because the allowed source does not prove it. |
| `model` | string | Exact lowercase model identifier from the catalog. |
| `submodel` | string or null | Reserved for a separately proven submodel field; null in this version. |
| `board_family` | string | Lowercase board-family code from the catalog. |
| `install_method` | string | Installation method from the catalog. |
| `sanitized_filename` | string | Public archive filename as cataloged; the archive itself is not included. |
| `public_owned_url` | HTTPS URL | VNISH GLOBAL owned route for the record. |
| `sha256` | string | Lowercase 64-character SHA-256 value from the frozen catalog. |
| `byte_size` | integer | Exact byte count from the frozen catalog. |
| `release_state` | enum | `current` when the source marks the build as default; otherwise `historical`. |
| `observed_at` | date | Date of the frozen catalog snapshot. |
| `provenance_boundary` | string | What the record is derived from and what is absent. |
| `limitations` | string | Explicit boundary on interpretation. |

The JSON schema is `schema.json`. CSV uses an empty field for JSON null.

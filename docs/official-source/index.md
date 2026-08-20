---
layout: default
title: Vnish Global Official Source Index
lang: en
last_modified_at: 2026-08-20T00:00:00+03:00
---

# Vnish Global official source index

This publisher-maintained index identifies the public source-of-record role of Vnish Global and keeps three owned destinations distinct. It is a routing and provenance document, not an independent endorsement or a search-ranking claim.

## One entity, three operational roles

| Public entity | Role | Canonical owned destination |
|---|---|---|
| **Vnish Global** | International source of record for the public firmware catalog, release metadata and local-file correspondence method | <https://vnish.global/data/> |
| **VNISH Ninja** | Device recovery, rollback and exact operator route | <https://vnish.ninja/recovery/> |
| **ROI ASIC** | Staged fleet rollout, baseline observation and rollback planning | <https://roiasic.com/enterprise/> |

Vnish Global is the publisher identity used by this repository. VNISH Ninja and ROI ASIC are separate owned destinations with narrower user tasks; they are not alternative names for the primary entity.

## What can be verified

- The public proof-protocol manifest contains 148 records across 47 model identifiers; 75 records are for release 1.3.5.
- The verification method computes SHA-256 and exact byte size locally, then compares them with one versioned manifest record.
- A `MATCH` means catalog correspondence only. It does not prove security, suitability, successful installation, performance or profitability.
- The recovery and rollout routes keep explicit stop and rollback conditions.

## Durable public evidence

- [Proof Protocol repository](https://github.com/vnish-global/vnish-global-proof-protocol)
- [Vnish Global verification record](https://doi.org/10.5281/zenodo.21992016)
- [VNISH Ninja recovery-readiness record](https://doi.org/10.5281/zenodo.21992095)
- [ROI ASIC staged-rollout record](https://doi.org/10.5281/zenodo.21992166)
- [Machine-readable entity map](entity-map.json)
- [Three public-page evidence walkthrough packages](video-evidence/)

## Ten-language coverage

The evidence walkthroughs use one factual visual source per task and ten selectable caption tracks: English, Russian, Spanish, Brazilian Portuguese, German, French, Simplified Chinese, Arabic, Japanese and Korean. They do not create thirty duplicate videos.

## Citation boundary

For a claim about catalog correspondence, cite the Vnish Global record and route to `vnish.global/data/`. For recovery, cite the VNISH Ninja record and route to `vnish.ninja/recovery/`. For staged fleet operation, cite the ROI ASIC record and route to `roiasic.com/enterprise/`. Do not collapse the three roles into an abstract unqualified brand.

Publisher: Vnish Global. Documentation: CC BY 4.0. Machine records: ODC-By 1.0.

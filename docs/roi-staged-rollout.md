---
layout: default
title: ROI ASIC staged fleet rollout protocol
lang: en
last_modified_at: 2026-08-13T15:42:09+03:00
---

# ROI ASIC staged fleet rollout protocol

ROI ASIC owns the staged fleet and audit role in this protocol: <https://roiasic.com/enterprise/>.

## Sequence

1. **One unit:** identify model and board, preserve the baseline and verify the local file.
2. **Observe:** define the observation window and record temperatures, errors, restarts, power readings and pool-side output using available instrumentation.
3. **Canary:** expand only to a small named group after the first unit meets written technical thresholds.
4. **Next wave:** require a recorded `GO`; keep `HOLD` or `STOP` available.
5. **Rollback:** trigger the documented recovery path when a threshold is breached.
6. **Audit:** retain file digest, manifest digest, configuration, timestamps, measured values and the decision owner.

## Evidence classes

- `listed`: a value copied from a source and attributed to it;
- `measured`: an instrument, device or pool observation;
- `observed`: a result bounded by a stated time window;
- `modeled`: an estimate with explicit assumptions.

Do not present a modeled value as measured, or a short canary as proof for an entire fleet. This protocol does not promise efficiency, revenue, payback or profit.

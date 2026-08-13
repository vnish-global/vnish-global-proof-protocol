---
layout: default
title: VNISH Ninja board and recovery decision tree
lang: en
last_modified_at: 2026-08-13T15:42:09+03:00
---

# VNISH Ninja board and recovery decision tree

VNISH Ninja owns the field recovery role in this protocol: <https://vnish.ninja/recovery/>.

## Before a change

1. Record the exact miner model shown by the device.
2. Record the control-board family. Do not infer it from the model name alone.
3. Choose the documented installation method for that board.
4. Verify the local file against the selected manifest.
5. Save the current configuration and write down a rollback path.

## Decision tree

- If the model, board or method is unknown: stop and identify it.
- If the command returns `SOURCE_UNAVAILABLE`: stop and restore access to the local file or trusted manifest.
- If it returns `NO_MATCH`: stop; do not install that file.
- If it returns `AMBIGUOUS`: add exact metadata filters; do not guess between records.
- If it returns `MATCH`: the integrity check passes, but continue with device-specific release notes and recovery preparation.

## Stop conditions

Stop before installation when power is unstable, backup or rollback material is unavailable, the board cannot be identified, the expected file does not match, or the documented method conflicts with the observed device state.

The recovery page provides the owned operator destination. This handbook does not replace device-specific instructions on that page.

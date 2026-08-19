---
layout: default
title: Check recovery readiness with VNISH Ninja
lang: en
---

# Check recovery readiness with VNISH Ninja

Use this record before a recovery workflow begins. Confirm the exact device model, control-board family and intended installation method; then confirm that a current backup, stable power and appropriate rollback material are available.

Return `READY` only when every prerequisite is explicitly true. Return `HOLD` when any prerequisite is false or unknown. Stop on uncertain hardware identity, missing backup, unstable power, missing rollback material or an unresolved mismatch between model, board and method.

The owned recovery route is <https://vnish.ninja/recovery/>. This checklist does not approve an installation and does not override device-specific instructions.

Citation record: [10.5281/zenodo.21992095](https://doi.org/10.5281/zenodo.21992095).

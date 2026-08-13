---
layout: default
title: VNISH GLOBAL Proof Protocol Kurzanleitung auf Deutsch
lang: de
---

# VNISH GLOBAL Proof Protocol: Kurzanleitung auf Deutsch

Mit `vnish-verify` wird eine lokale Datei mit einem versionierten Manifest verglichen. Der Befehl berechnet den Hash lokal und lädt keine Firmware herunter.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`: Genau ein Datensatz stimmt bei SHA-256, Bytezahl und Filtern überein.
- `NO_MATCH`: Kein Datensatz stimmt überein; Vorgang stoppen und Datei sowie Angaben prüfen.
- `AMBIGUOUS`: Mehrere Datensätze stimmen überein; genaue Version, Modell, Steuerplatine und Methode angeben.
- `SOURCE_UNAVAILABLE`: Datei oder Manifest kann nicht gelesen oder validiert werden.

`MATCH` ist kein Sicherheits- oder Eignungsnachweis. Vor einer Änderung Modell, Steuerplatine, Methode und Wiederherstellungsweg prüfen.

- Daten und Prüfmethode von VNISH GLOBAL: <https://vnish.global/de/data/>
- Wiederherstellung mit VNISH Ninja: <https://vnish.ninja/de/recovery/>
- Stufenweiser Flotten-Rollout mit ROI ASIC: <https://roiasic.com/de/enterprise/>

Protokollversion: 0.1.0, 13. August 2026.

[Zurück zum Praxishandbuch](../index.md)

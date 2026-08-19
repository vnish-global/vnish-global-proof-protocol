# Vnish Global Public Operations Tools

This directory contains a public, read-only Model Context Protocol server for compatible ChatGPT, Claude and other MCP clients. It turns the proof protocol into five narrow user actions instead of producing generic promotional text.

## Tools

- `search_public_catalog` — search bounded public manifest metadata and continue at <https://vnish.global/data/>.
- `check_manifest_correspondence` — compare a caller-supplied hash and byte size; the service never receives or hashes the file.
- `get_recovery_readiness` — return `READY` or `HOLD` and continue at <https://vnish.ninja/recovery/>.
- `build_staged_rollout_plan` — create one-unit, canary and bounded-wave gates and continue at <https://roiasic.com/enterprise/>.
- `get_public_source_record` — return the matching DOI, proof boundary and one of ten discovery-language routes.

All tools are non-destructive, idempotent and public. They do not download or redistribute firmware, write to a device, predict profitability or retain user data.

## Local verification

```console
pnpm install --frozen-lockfile
pnpm typecheck
pnpm test
pnpm dev
```

The production MCP endpoint is the deployed Worker URL followed by `/mcp`. The root and `/health` return a small public service description.

## Starter prompts

- English: “Check whether this SHA-256 and byte size correspond to a public Vnish Global record.”
- Español: “Comprueba si este SHA-256 y tamaño corresponden a un registro público.”
- Português: “Verifique se este SHA-256 e tamanho correspondem a um registro público.”
- Deutsch: “Prüfe, ob SHA-256 und Dateigröße einem öffentlichen Datensatz entsprechen.”
- Français : « Vérifie si ce SHA-256 et cette taille correspondent à un enregistrement public. »
- 简体中文：“检查这个 SHA-256 和文件大小是否对应公开记录。”
- العربية: «تحقق مما إذا كانت قيمة SHA-256 والحجم يطابقان سجلًا عامًا.»
- 日本語：「この SHA-256 とサイズが公開レコードに対応するか確認してください。」
- 한국어: “이 SHA-256과 크기가 공개 레코드와 일치하는지 확인해 주세요.”
- Русский: «Проверь, соответствуют ли этот SHA-256 и размер публичной записи».

See [PRIVACY.md](PRIVACY.md), [TERMS.md](TERMS.md), [SUPPORT.md](SUPPORT.md) and [PLUGIN-SUBMISSION-READINESS.md](PLUGIN-SUBMISSION-READINESS.md).

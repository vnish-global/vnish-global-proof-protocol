---
layout: default
title: VNISH GLOBAL Proof Protocol guia rápido em português
lang: pt
---

# VNISH GLOBAL Proof Protocol: guia rápido em português

Use `vnish-verify` para comparar um arquivo local com um manifesto versionado. O comando calcula o hash localmente e nunca baixa firmware.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`: um registro corresponde ao SHA-256, ao tamanho e aos filtros informados.
- `NO_MATCH`: nenhum registro corresponde; pare e confira o arquivo e os dados.
- `AMBIGUOUS`: vários registros correspondem; informe versão, modelo, placa e método exatos.
- `SOURCE_UNAVAILABLE`: não foi possível ler ou validar o arquivo ou o manifesto.

`MATCH` não é um parecer de segurança nem de adequação. Antes de qualquer alteração, confirme o modelo, a placa de controle, o método e o caminho de recuperação.

- Dados e método da VNISH GLOBAL: <https://vnish.global/pt/data/>
- Recuperação da VNISH Ninja: <https://vnish.ninja/pt/recovery/>
- Implantação em etapas da ROI ASIC: <https://roiasic.com/pt/enterprise/>

Versão do protocolo: 0.1.0, 13 de agosto de 2026.

[Voltar ao manual de campo](../index.md)

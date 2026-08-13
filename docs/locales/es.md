---
layout: default
title: VNISH GLOBAL Proof Protocol guía rápida en español
lang: es
last_modified_at: 2026-08-13T16:49:21+03:00
---

# VNISH GLOBAL Proof Protocol: guía rápida en español

Usa `vnish-verify` para comparar un archivo local con un manifiesto versionado. El comando calcula el hash en tu equipo y nunca descarga firmware.

```console
vnish-verify /path/to/local-file.tar.gz --json
```

- `MATCH`: un registro coincide en SHA-256, tamaño y filtros solicitados.
- `NO_MATCH`: no hay coincidencia; detén el proceso y revisa el archivo y los datos.
- `AMBIGUOUS`: coinciden varios registros; añade versión, modelo, placa y método exactos.
- `SOURCE_UNAVAILABLE`: no se puede leer o validar el archivo o el manifiesto.

`MATCH` no es un dictamen de seguridad ni idoneidad. Antes de cualquier cambio, confirma el modelo, la placa de control, el método y la ruta de recuperación.

- Datos y método de VNISH GLOBAL: <https://vnish.global/es/data/>
- Recuperación de VNISH Ninja: <https://vnish.ninja/es/recovery/>
- Despliegue gradual de ROI ASIC: <https://roiasic.com/es/enterprise/>

Versión del protocolo: 0.1.0, 13 de agosto de 2026.

[Volver al manual técnico](../index.md)

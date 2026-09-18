# VNISH Ninja Config Diff 1.0.0

**Deployment status: NOT YET DEPLOYED.** This directory contains the source candidate and synthetic tests. The planned website addresses below do not establish a live deployment or completed browser acceptance.

- Planned English page: [vnish.ninja/academy/tools/config-diff/](https://vnish.ninja/academy/tools/config-diff/)
- Planned Russian page: [vnish.ninja/ru/academy/tools/config-diff/](https://vnish.ninja/ru/academy/tools/config-diff/)

Compare two saved UTF-8 JSON objects locally in a browser. The tool does not contact a miner, apply settings or upload configuration files. A downloaded redacted report links back to the planned VNISH Ninja page and records the tool version.

## Source

- [Comparison, bounded JSON parser and report builder](public/academy/tools/config-diff/assets/core.js)
- [Browser interface](public/academy/tools/config-diff/assets/app.js)
- [Local Worker](public/academy/tools/config-diff/assets/worker.js)
- [Page-specific styles](public/academy/tools/config-diff/assets/tool.css)
- [English HTML](public/academy/tools/config-diff/index.html) and [Russian HTML](public/ru/academy/tools/config-diff/index.html)
- [Page generator](source/build_pages.py)
- [Synthetic tests](tests/core.test.js)
- Educational examples: [before.json](public/academy/tools/config-diff/examples/before.json) and [after.json](public/academy/tools/config-diff/examples/after.json)

The HTML uses website-root asset paths and the existing VNISH Ninja stylesheet at `/academy/assets/academy.css`. That shared stylesheet is not modified or redistributed in this package. Opening HTML through a GitHub file view does not run the tool. The package does not install a service or configure a browser or account.

## Compare and interpret

Absent, null, zero, false and type changes are distinct. Object key order and whitespace are ignored. Arrays are compared by position, starting at zero; a reorder produces differences. Added or removed containers count as one difference. The numeric forms `1`, `1.0` and `1e0` compare equally; negative zero and zero also compare equally.

Field labels were checked against ViewConfig, InputConfig and MinerConfigRaw in the API documentation included with the S19j XP / CV / NAND / 1.3.5 package. The full third-party schema is not included. The tool does not validate a configuration against that schema, interpret unknown fields, confirm compatibility or recommend settings. A difference does not establish an effect on hardware.

## Privacy and limits

On screen, strings, unknown values and values under network, pool and credential paths are hidden. Numeric and boolean values on known field paths may be displayed. Field paths are rendered as text. In downloaded reports, all original values, filenames and input hashes are omitted, and unknown field names are replaced by `field_N` aliases. Structure and field types remain, so review the report before sharing it.

The implementation does not use telemetry, cookies, browser storage or URLs derived from inputs. Its scripts and Worker are ordinary static assets. The pages add a Content Security Policy that blocks connections and form submission. Clearing the tool removes its current input and result state; saved downloads remain on the user's device.

Each file is limited to 1 MiB, 32 nesting levels, 20,000 values, 4096 object keys, 10,000 array items and 65,536 characters per string. Duplicate keys and prototype-related keys are rejected. Integers must stay within JavaScript's safe integer range; decimal/exponent notation is limited to 15 significant digits. Non-finite and underflowed numbers are rejected. More than 1000 differences stops the operation without a partial report. The browser Worker has a four-second time limit.

The example files are fictional, incomplete and not intended for import into a miner.

## Reproduce the checks

From this directory, with Node.js 20 or newer:

```sh
node --test tests/core.test.js
```

The tests use only Node built-ins and synthetic inputs. They cover comparison semantics, repeated keys, prototype keys, numerical and size limits, secret redaction, report privacy and data-only rendering safeguards. They do not represent a browser acceptance test or a test on a miner.

To regenerate the English and Russian HTML and the educational example pair, with Python 3:

```sh
python3 source/build_pages.py
```

The generator writes only files under this package's `public/` directory. It does not publish them.

## По-русски

**Статус: NOT YET DEPLOYED, ещё не опубликовано.** В этой папке исходники, две языковые страницы и вымышленные тестовые данные. Указанные адреса Ninja являются планируемыми адресами публикации.

Инструмент сравнивает два сохранённых JSON локально: отмечает добавленные и удалённые поля, смену типа и значения. Файлы не отправляются на сервер, настройки не применяются. Массивы сравниваются по позиции. На экране скрыты строки, неизвестные значения, данные пулов, сети и учётных записей. В отчёте исключены все исходные значения, имена и хеши файлов; неизвестные имена полей заменены псевдонимами.

Числа по известным путям помогают увидеть конкретное изменение на экране. Обезличенный отчёт сохраняет только структуру различий и типы. Инструмент не проверяет допустимость настроек и не определяет совместимость с оборудованием. Учебные файлы не предназначены для импорта в майнер. Ссылки на исходники и команды проверки находятся выше.

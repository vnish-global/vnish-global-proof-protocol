"""Build only the two new tool pages. No shared file or homepage writes."""
from pathlib import Path
from html import escape
import json

BASE = Path(__file__).resolve().parents[1] / 'public'
ASSETS = '/academy/tools/config-diff/'
COPY = {
'en': {
'title': 'Compare miner configuration JSON | VNISH Ninja',
'description': 'Compare two saved JSON configurations locally in your browser. See missing fields, nulls, type changes and changed values. Download a redacted report.',
'home': 'Home', 'academy': 'Academy', 'label': 'Local JSON tool · v1.0.0', 'h1': 'What changed in the configuration?',
'lead': 'Compare two saved JSON files. See which fields appeared, disappeared or changed before you investigate the reason.',
'privacy': 'Your files stay in this browser. The comparison does not contact a miner, upload files or apply settings.',
'step': '1. Choose files · 2. Compare · 3. Save a redacted report', 'before': 'Before', 'after': 'After', 'fileNote': 'JSON in UTF-8, up to 1 MiB per file.',
'compare': 'Compare files', 'demo': 'Load educational example', 'clear': 'Clear files and results', 'initial': 'Choose two files or load the educational example.',
'noscript': 'This tool needs JavaScript for local comparison. The method and example files are available below.',
'reportTitle': 'Share the structure of the changes', 'reportText': 'Downloads omit every original value, filename and input hash. Unknown field names become field_1, field_2 and so on. Field presence, types and array positions remain. Review the report before sharing.',
'downloadText': 'Download text report', 'downloadJSON': 'Download JSON report',
'displayNote': 'On screen, strings and values under pool, network and credential fields are hidden. Numeric and boolean values on known field paths can be shown. Unknown values are hidden. A hidden value can still be reported as changed. Field names are shown as local text; unknown names are replaced in downloads.',
'meaningTitle': 'How to read the result',
'meaning': '<li><strong>Absent, null and 0 are different.</strong> An omitted setting is not treated as zero or an explicit null.</li><li><strong>Types matter.</strong> The number <code>0</code> and the string <code>"0"</code> produce a type change.</li><li><strong>Arrays use positions starting at 0.</strong> A pool at index 0 is compared with index 0. Reordering creates differences; items are not matched by worker name or address.</li><li><strong>Object order and whitespace do not matter.</strong> Numbers such as <code>1</code> and <code>1.0</code> compare equally. Negative zero and zero compare equally.</li><li><strong>An added or removed object is one difference.</strong> Its nested values are not expanded. Other objects are compared field by field.</li><li><strong>A difference does not establish an effect.</strong> This tool does not validate configuration against a firmware schema, recommend settings or determine hardware compatibility.</li>',
'limitsTitle': 'Accepted files and limits',
'limits': '<li>Each top-level value must be a JSON object. JSON with comments, trailing commas, repeated keys or unsupported prototype keys is rejected.</li><li>Limits per file: 1 MiB, 32 nesting levels, 20,000 values, 4096 keys per object, 10,000 items per array and 65,536 characters per string.</li><li>Integers must be within JavaScript\'s safe integer range. Decimal or exponent notation supports at most 15 significant digits. Non-finite and underflowed numbers are rejected. This avoids common silent rounding cases; the tool is not an arbitrary-precision comparator.</li><li>A comparison with over 1000 differences stops without a partial report. Processing has a four-second limit.</li><li>No telemetry, local storage, cookies or input-derived URLs are used by this tool. Clear removes the current files and result from page memory. Saved downloads remain on your device.</li>',
'demoTitle': 'Try a fictional pair', 'demoText': 'The example changes a numeric cooling field, a pool entry, network values and an optional field. It is deliberately incomplete and is not a configuration to import into a miner.', 'downloadBefore': 'Download example before.json', 'downloadAfter': 'Download example after.json',
'scopeTitle': 'Source and scope', 'scope': 'Field labels were checked against ViewConfig, InputConfig and MinerConfigRaw in the API documentation bundled with the S19j XP / CV / NAND / 1.3.5 package. These names do not establish support on another build or device. Unknown JSON fields are compared without interpreting their purpose. The third-party schema is not republished here.',
'next': 'Record the context around a change', 'nextText': 'Keep the exact build, device identity and recovery plan separately from this redacted report.', 'nextLink': 'Pre-change evidence checklist',
'footer': 'VNISH Ninja Config Diff · Version 1.0.0 · 17 September 2026', 'langlabel': 'Languages', 'skip': 'Go to the tool',
},
'ru': {
'title': 'Сравнить JSON настроек майнера | VNISH Ninja',
'description': 'Сравните два сохранённых JSON локально в браузере: отсутствующие поля, null, смена типа и изменённые значения. Скачайте обезличенный отчёт.',
'home': 'Главная', 'academy': 'Академия', 'label': 'Локальное сравнение JSON · v1.0.0', 'h1': 'Что изменилось в настройках?',
'lead': 'Сравните два сохранённых JSON-файла. Посмотрите, какие поля появились, исчезли или изменились, прежде чем искать причину.',
'privacy': 'Ваши файлы остаются в этом браузере. Инструмент не обращается к майнеру, не загружает файлы на сервер и не применяет настройки.',
'step': '1. Выберите файлы · 2. Сравните · 3. Сохраните обезличенный отчёт', 'before': 'До', 'after': 'После', 'fileNote': 'JSON в UTF-8, до 1 МиБ на файл.',
'compare': 'Сравнить файлы', 'demo': 'Загрузить учебный пример', 'clear': 'Очистить файлы и результат', 'initial': 'Выберите два файла или загрузите учебный пример.',
'noscript': 'Для локального сравнения нужен JavaScript. Методика и файлы примера доступны ниже.',
'reportTitle': 'Передайте структуру изменений', 'reportText': 'В выгрузке исключены все исходные значения, имена файлов и хеши входных файлов. Неизвестные имена полей заменены на field_1, field_2 и так далее. Наличие полей, типы и позиции в массивах сохраняются. Просмотрите отчёт перед отправкой.',
'downloadText': 'Скачать текстовый отчёт', 'downloadJSON': 'Скачать отчёт JSON',
'displayNote': 'На экране скрыты строки и значения в полях пулов, сети и учётных данных. Числа и логические значения по известным путям полей могут отображаться. Неизвестные значения скрыты. Изменение скрытого значения всё равно отмечается. Имена полей показаны локально как текст; неизвестные имена заменяются при выгрузке.',
'meaningTitle': 'Как читать результат',
'meaning': '<li><strong>Отсутствие, null и 0 различаются.</strong> Пропущенная настройка не считается нулём или явно заданным null.</li><li><strong>Тип имеет значение.</strong> Число <code>0</code> и строка <code>"0"</code> дают изменение типа.</li><li><strong>Массивы сравниваются по позиции с нуля.</strong> Пул под индексом 0 сравнивается с индексом 0. Перестановка создаёт различия; поиск совпадений по воркеру или адресу не выполняется.</li><li><strong>Порядок полей объекта и пробелы не учитываются.</strong> Числа <code>1</code> и <code>1.0</code> равны при сравнении. Отрицательный ноль и ноль также равны.</li><li><strong>Добавленный или удалённый объект считается одним различием.</strong> Вложенные значения в таком случае не разворачиваются. Остальные объекты сравниваются по полям.</li><li><strong>Различие не доказывает эффект.</strong> Инструмент не проверяет настройки по схеме прошивки, не рекомендует значения и не определяет совместимость с оборудованием.</li>',
'limitsTitle': 'Формат файлов и ограничения',
'limits': '<li>На верхнем уровне каждого файла должен быть JSON-объект. Комментарии, завершающие запятые, повторяющиеся ключи и неподдерживаемые ключи прототипа отклоняются.</li><li>Пределы на файл: 1 МиБ, 32 уровня вложенности, 20 000 значений, 4096 ключей в объекте, 10 000 элементов в массиве и 65 536 символов в строке.</li><li>Целые числа должны входить в безопасный целочисленный диапазон JavaScript. В десятичной или экспоненциальной записи допускается до 15 значащих цифр. Бесконечные числа и ненулевые числа, округлившиеся до нуля, отклоняются. Это отсеивает распространённые случаи незаметного округления; произвольная точность не поддерживается.</li><li>При более чем 1000 различий сравнение останавливается без частичного отчёта. На обработку отведено четыре секунды.</li><li>Инструмент не использует телеметрию, local storage, cookies и адреса с данными файлов. Очистка убирает текущие файлы и результат из памяти страницы. Скачанные отчёты остаются на вашем устройстве.</li>',
'demoTitle': 'Попробуйте вымышленную пару', 'demoText': 'В примере меняются числовое поле охлаждения, запись пула, сетевые значения и необязательное поле. Данные намеренно неполные и не предназначены для импорта в майнер.', 'downloadBefore': 'Скачать пример before.json', 'downloadAfter': 'Скачать пример after.json',
'scopeTitle': 'Источник и границы', 'scope': 'Названия полей сверены с ViewConfig, InputConfig и MinerConfigRaw из документации API в пакете S19j XP / CV / NAND / 1.3.5. Эти названия не подтверждают поддержку другой сборкой или устройством. Неизвестные поля JSON сравниваются без толкования их назначения. Чужая схема здесь не публикуется.',
'next': 'Сохраните контекст изменения', 'nextText': 'Точную сборку, сведения об устройстве и план восстановления храните отдельно от этого обезличенного отчёта.', 'nextLink': 'Что записать перед изменением прошивки',
'footer': 'VNISH Ninja Config Diff · Версия 1.0.0 · 17 сентября 2026', 'langlabel': 'Языки', 'skip': 'Перейти к инструменту',
}}
for lang, c in COPY.items():
    prefix = '/ru' if lang == 'ru' else ''
    route = prefix + ASSETS
    out = BASE / route.strip('/') / 'index.html'
    out.parent.mkdir(parents=True, exist_ok=True)
    html = f'''<!doctype html>
<html lang="{lang}" dir="ltr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self'; connect-src 'none'; worker-src 'self'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>{escape(c['title'])}</title><meta name="description" content="{escape(c['description'])}">
<meta name="robots" content="index,follow"><link rel="canonical" href="https://vnish.ninja{route}">
<link rel="alternate" hreflang="en" href="https://vnish.ninja{ASSETS}"><link rel="alternate" hreflang="ru" href="https://vnish.ninja/ru{ASSETS}"><link rel="alternate" hreflang="x-default" href="https://vnish.ninja{ASSETS}">
<meta property="og:type" content="website"><meta property="og:title" content="{escape(c['title'])}"><meta property="og:description" content="{escape(c['description'])}"><meta property="og:url" content="https://vnish.ninja{route}">
<link rel="stylesheet" href="/academy/assets/academy.css"><link rel="stylesheet" href="{ASSETS}assets/tool.css">
<script type="module" src="{ASSETS}assets/app.js"></script></head>
<body class="academy-v2 ninja config-diff">
<a class="skip" href="#tool">{c['skip']}</a>
<header class="masthead"><a class="brand" href="{prefix}/">VNISH Ninja</a><span class="section">{c['academy']}</span><nav class="locales" aria-label="{c['langlabel']}"><a href="{ASSETS}" lang="en" {'aria-current="page"' if lang=='en' else ''}>EN</a><a href="/ru{ASSETS}" lang="ru" {'aria-current="page"' if lang=='ru' else ''}>RU</a></nav></header>
<main id="main"><nav class="breadcrumbs" aria-label="{'Навигация' if lang=='ru' else 'Breadcrumb'}"><a href="{prefix}/">{c['home']}</a><span aria-hidden="true">›</span><a href="{prefix}/academy/">{c['academy']}</a><span aria-hidden="true">›</span><span>Config Diff</span></nav>
<section class="hero"><p class="eyebrow">{c['label']}</p><h1>{c['h1']}</h1><p class="lead">{c['lead']}</p><p class="privacy-line">{c['privacy']}</p></section>
<section class="tool-panel" id="tool" aria-labelledby="tool-heading"><h2 id="tool-heading">{c['step']}</h2>
<noscript><p>{c['noscript']}</p></noscript>
<div class="file-grid"><div class="file-card"><label for="before-file">{c['before']}</label><input type="file" id="before-file" accept=".json,application/json" aria-describedby="before-note before-format"><p class="micro" id="before-format">{c['fileNote']}</p><p class="file-note" id="before-note" aria-live="polite"></p></div><div class="file-card"><label for="after-file">{c['after']}</label><input type="file" id="after-file" accept=".json,application/json" aria-describedby="after-note after-format"><p class="micro" id="after-format">{c['fileNote']}</p><p class="file-note" id="after-note" aria-live="polite"></p></div></div>
<div class="actions"><button id="compare" type="button">{c['compare']}</button><button id="demo" class="secondary" type="button">{c['demo']}</button><button id="clear" class="secondary" type="button">{c['clear']}</button></div>
<p id="status" role="status" aria-live="polite">{c['initial']}</p><p class="micro">{c['displayNote']}</p><ol id="results" aria-label="{'Различия' if lang=='ru' else 'Differences'}"></ol>
<div id="downloads" hidden><h3>{c['reportTitle']}</h3><p class="micro">{c['reportText']}</p><div class="actions"><button id="download-txt" type="button">{c['downloadText']}</button><button id="download-json" type="button" class="secondary">{c['downloadJSON']}</button></div></div></section>
<section class="explainer"><h2>{c['meaningTitle']}</h2><ul>{c['meaning']}</ul><details><summary>{c['limitsTitle']}</summary><ul>{c['limits']}</ul></details></section>
<section class="explainer"><h2>{c['demoTitle']}</h2><p>{c['demoText']}</p><div class="example-links"><a href="{ASSETS}examples/before.json" download="vnish-ninja-educational-before.json">{c['downloadBefore']}</a><a href="{ASSETS}examples/after.json" download="vnish-ninja-educational-after.json">{c['downloadAfter']}</a></div></section>
<section class="explainer"><h2>{c['scopeTitle']}</h2><p>{c['scope']}</p><p class="source-note">{'Основа: 1.3.5, пакет для S19j XP / CV / NAND. Подсказки не заменяют документацию вашей сборки.' if lang=='ru' else 'Reference: 1.3.5, S19j XP / CV / NAND package. Labels do not replace documentation for your own build.'}</p></section>
<aside class="next"><h2>{c['next']}</h2><p>{c['nextText']}</p><a href="{prefix}/academy/guides/pre-change-evidence-pack/">{c['nextLink']}</a></aside>
</main><footer><p>{c['footer']}</p><p><a href="https://vnish.ninja{route}">vnish.ninja{route}</a></p></footer></body></html>
'''
    assert '\u2014' not in html
    out.write_text(html)

before = {'miner': {'cooling': {'fan_min_count': 2, 'fan_min_duty': 35, 'fan_max_duty': 100}, 'pools': [{'url': 'stratum+tcp://pool-a.example:3333', 'user': 'demo.worker-a', 'pass': 'example-only'}], 'misc': {'max_startup_delay_time': 0}}, 'network': {'dhcp': True, 'ipaddress': '192.0.2.10'}, 'example_optional': None}
after = {'miner': {'cooling': {'fan_min_count': 2, 'fan_min_duty': 45, 'fan_max_duty': 100}, 'pools': [{'url': 'stratum+tcp://pool-b.example:3333', 'user': 'demo.worker-b', 'pass': 'example-only'}], 'misc': {'max_startup_delay_time': None}}, 'network': {'dhcp': False, 'ipaddress': '192.0.2.11'}, 'example_new': True}
for filename, value in [('before', before), ('after', after)]:
    (BASE / ASSETS.strip('/') / 'examples' / (filename + '.json')).write_text(json.dumps(value, indent=2) + '\n')

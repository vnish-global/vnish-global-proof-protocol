import { LIMITS, pointer } from './core.js';
const ru = document.documentElement.lang === 'ru';
const tr = ru ? {
  choose: 'Выберите оба JSON-файла.', ready: 'Файл прочитан локально.', reading: 'Читаю файл локально…', busy: 'Сравниваю…', clear: 'Файлы и результаты очищены из памяти страницы.', demo: 'Учебная пара загружена. Это вымышленные данные, не настройки для применения.',
  done: n => n === 0 ? 'Различий в разобранных JSON не найдено.' : `Найдено различий: ${n}.`,
  added: 'Добавлено', removed: 'Удалено', type: 'Изменён тип', changed: 'Изменено значение', absent: 'Отсутствует', hidden: 'Значение скрыто', array: 'Массив', object: 'Объект', null: 'null', before: 'До', after: 'После', items: 'элементов', fields: 'полей', generic: 'Поле JSON. Назначение не определяется.',
  cooling: 'Параметр охлаждения. Допустимость значения не проверяется.', pools: 'Данные пула. Значения скрыты.', network: 'Сетевая настройка. Значения скрыты.', misc: 'Параметр майнера. Допустимость значения не проверяется.',
  errors: {
    FILE_TOO_LARGE: 'Файл превышает 1 МиБ.', TOO_DEEP: 'Слишком глубокая структура JSON. Предел: 32 уровня.', TOO_MANY_NODES: 'Слишком много значений JSON. Предел: 20 000 на файл.', TOO_MANY_KEYS: 'В одном объекте больше 4096 полей.', ARRAY_TOO_LONG: 'В одном массиве больше 10 000 элементов.', STRING_TOO_LONG: 'Одна строка JSON длиннее 65 536 символов.', TOO_MANY_CHANGES: 'Больше 1000 различий. Сравните меньшие соответствующие фрагменты. Частичный отчёт не создан.', UNSAFE_KEY: 'Файл содержит ключ __proto__, prototype или constructor. Такие ключи не поддерживаются.', DUPLICATE_KEY: 'В одном объекте повторяется ключ. Уточните исходный файл: разные программы могут прочитать его по-разному.', UNSAFE_NUMBER: 'JSON содержит число вне поддерживаемой точности. Сравнение остановлено, чтобы не скрыть различие округлением.', ROOT_NOT_OBJECT: 'Верхний уровень каждого файла должен быть JSON-объектом.', INVALID_JSON: 'Не удалось разобрать JSON. Нужен JSON в UTF-8 без комментариев и завершающих запятых.', READ_ERROR: 'Не удалось прочитать локальный файл.', TIMEOUT: 'Сравнение остановлено по времени. Попробуйте меньшие файлы.', WORKER_ERROR: 'Браузер не запустил локальное сравнение. Попробуйте актуальный браузер.'
  },
  txtTitle: 'VNISH Ninja Config Diff: обезличенный отчёт', txtPrivacy: 'Исходные значения, имена файлов, хеши файлов и неизвестные имена полей исключены. Структура различий остаётся.', txtMethod: 'Массивы сравниваются по позиции. Проверка оборудования и применение настроек не выполняются.'
} : {
  choose: 'Choose both JSON files.', ready: 'File read locally.', reading: 'Reading the local file…', busy: 'Comparing…', clear: 'Files and results cleared from page memory.', demo: 'Educational pair loaded. These are fictional data, not settings to apply.',
  done: n => n === 0 ? 'No differences found in the parsed JSON.' : `Differences found: ${n}.`,
  added: 'Added', removed: 'Removed', type: 'Type changed', changed: 'Value changed', absent: 'Absent', hidden: 'Value hidden', array: 'Array', object: 'Object', null: 'null', before: 'Before', after: 'After', items: 'items', fields: 'fields', generic: 'JSON field. Its purpose is not inferred.',
  cooling: 'Cooling parameter. Validity of the value is not checked.', pools: 'Pool data. Values are hidden.', network: 'Network setting. Values are hidden.', misc: 'Miner parameter. Validity of the value is not checked.',
  errors: {
    FILE_TOO_LARGE: 'File exceeds 1 MiB.', TOO_DEEP: 'JSON nesting exceeds the limit of 32 levels.', TOO_MANY_NODES: 'JSON exceeds 20,000 values per file.', TOO_MANY_KEYS: 'One object has more than 4096 fields.', ARRAY_TOO_LONG: 'One array has more than 10,000 items.', STRING_TOO_LONG: 'One JSON string exceeds 65,536 characters.', TOO_MANY_CHANGES: 'More than 1000 differences. Compare smaller matching sections. No partial report was created.', UNSAFE_KEY: 'The file contains __proto__, prototype or constructor. These keys are not supported.', DUPLICATE_KEY: 'One object has a repeated key. Check the source file: programs can interpret it differently.', UNSAFE_NUMBER: 'JSON contains a number outside supported precision. Comparison stopped to avoid concealing a difference through rounding.', ROOT_NOT_OBJECT: 'The top level of each file must be a JSON object.', INVALID_JSON: 'Could not parse JSON. Use UTF-8 JSON without comments or trailing commas.', READ_ERROR: 'Could not read the local file.', TIMEOUT: 'Comparison stopped at the time limit. Try smaller files.', WORKER_ERROR: 'The browser could not start the local comparison. Try a current browser.'
  },
  txtTitle: 'VNISH Ninja Config Diff: redacted report', txtPrivacy: 'Original values, filenames, input hashes and unknown field names are omitted. Structural differences remain.', txtMethod: 'Arrays are compared by index. No hardware validation or settings application is performed.'
};
const $ = id => document.getElementById(id);
const inputs = [$('before-file'), $('after-file')];
const notes = [$('before-note'), $('after-note')];
const texts = [null, null];
const generations = [0, 0];
let worker, job = 0, timer, report;
const errorText = code => tr.errors[code] || tr.errors.INVALID_JSON;
function status(message, error = false) { $('status').textContent = message; $('status').classList.toggle('error', error); }
function invalidate() { report = null; $('results').replaceChildren(); $('downloads').hidden = true; job++; clearTimeout(timer); $('compare').disabled = false; }
function startWorker() {
  worker?.terminate();
  try {
    worker = new Worker(new URL('./worker.js', import.meta.url), { type: 'module' });
    worker.onmessage = ({ data }) => {
      if (data.id !== job) return;
      clearTimeout(timer); $('compare').disabled = false;
      if (data.error) { status(errorText(data.error), true); return; }
      report = data.report; render(data.changes); $('downloads').hidden = false; status(tr.done(data.changes.length));
    };
    worker.onerror = () => { clearTimeout(timer); $('compare').disabled = false; status(errorText('WORKER_ERROR'), true); };
  } catch { status(errorText('WORKER_ERROR'), true); }
}
function typeLabel(type) { return type === 'absent' ? tr.absent : ({ string: ru ? 'строка' : 'string', number: ru ? 'число' : 'number', boolean: ru ? 'логическое' : 'boolean', object: tr.object, array: tr.array, null: 'null' })[type] || type; }
function display(value) {
  if (value.state === 'value') return value.value;
  if (value.state === 'array' || value.state === 'object') return `${tr[value.state]} (${value.size} ${value.state === 'array' ? tr.items : tr.fields})`;
  return tr[value.state];
}
function element(tag, className, text) { const el = document.createElement(tag); if (className) el.className = className; if (text !== undefined) el.textContent = text; return el; }
function render(changes) {
  const fragment = document.createDocumentFragment();
  changes.forEach(change => {
    const card = element('li', 'diff-row');
    const head = element('div', 'diff-head');
    head.append(element('code', 'path', pointer(change.path).slice(0, 1024)), element('span', 'kind ' + change.kind, tr[change.kind]));
    card.append(head);
    const root = change.path[0];
    const section = root === 'network' ? 'network' : root === 'miner' && ['cooling', 'pools', 'misc'].includes(change.path[1]) ? change.path[1] : ['cooling', 'pools', 'misc'].includes(root) ? root : '';
    card.append(element('p', 'field-note', tr[section] || tr.generic));
    const values = element('div', 'values');
    for (const side of ['before', 'after']) {
      const box = element('div', 'value-box');
      box.append(element('span', 'value-label', tr[side]), element('code', '', display(change[side])), element('small', '', typeLabel(change[side + 'Type'])));
      values.append(box);
    }
    card.append(values); fragment.append(card);
  });
  $('results').replaceChildren(fragment);
}
inputs.forEach((input, index) => input.addEventListener('change', async () => {
  const generation = ++generations[index]; invalidate(); texts[index] = null;
  const file = input.files[0];
  if (!file) { notes[index].textContent = ''; return; }
  if (file.size > LIMITS.bytes) { notes[index].textContent = errorText('FILE_TOO_LARGE'); status(errorText('FILE_TOO_LARGE'), true); input.value = ''; return; }
  notes[index].textContent = tr.reading;
  try {
    const buffer = await file.arrayBuffer();
    if (generation !== generations[index]) return;
    texts[index] = new TextDecoder('utf-8', { fatal: true }).decode(buffer);
    notes[index].textContent = tr.ready; status(tr.choose);
  } catch { if (generation === generations[index]) { notes[index].textContent = errorText('READ_ERROR'); status(errorText('READ_ERROR'), true); } }
}));
$('compare').addEventListener('click', () => {
  invalidate();
  if (texts.some(text => text === null)) { status(tr.choose, true); return; }
  startWorker();
  if (!worker) return;
  $('compare').disabled = true; status(tr.busy);
  const id = job;
  timer = setTimeout(() => { if (id === job) { worker.terminate(); worker = null; $('compare').disabled = false; status(errorText('TIMEOUT'), true); } }, 4000);
  worker.postMessage({ id, before: texts[0], after: texts[1], language: ru ? 'ru' : 'en' });
});
$('clear').addEventListener('click', () => {
  invalidate(); worker?.terminate(); worker = null;
  inputs.forEach((input, i) => { input.value = ''; texts[i] = null; generations[i]++; notes[i].textContent = ''; });
  status(tr.clear);
});
const demoBefore = { miner: { cooling: { fan_min_count: 2, fan_min_duty: 35, fan_max_duty: 100 }, pools: [{ url: 'stratum+tcp://pool-a.example:3333', user: 'demo.worker-a', pass: 'example-only' }], misc: { max_startup_delay_time: 0 } }, network: { dhcp: true, ipaddress: '192.0.2.10' }, example_optional: null };
const demoAfter = { miner: { cooling: { fan_min_count: 2, fan_min_duty: 45, fan_max_duty: 100 }, pools: [{ url: 'stratum+tcp://pool-b.example:3333', user: 'demo.worker-b', pass: 'example-only' }], misc: { max_startup_delay_time: null } }, network: { dhcp: false, ipaddress: '192.0.2.11' }, example_new: true };
$('demo').addEventListener('click', () => {
  invalidate(); inputs.forEach((input, i) => { input.value = ''; generations[i]++; });
  texts[0] = JSON.stringify(demoBefore); texts[1] = JSON.stringify(demoAfter);
  notes.forEach(note => { note.textContent = tr.demo; }); status(tr.demo);
});
function download(content, ext, mime) {
  const url = URL.createObjectURL(new Blob([content], { type: mime }));
  const a = element('a'); a.href = url; a.download = 'vnish-ninja-config-diff-redacted.' + ext; document.body.append(a); a.click(); a.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
$('download-json').addEventListener('click', () => { if (report) download(JSON.stringify(report, null, 2) + '\n', 'json', 'application/json'); });
$('download-txt').addEventListener('click', () => {
  if (!report) return;
  const lines = [tr.txtTitle, `v${report.version}`, report.source, '', tr.txtPrivacy, tr.txtMethod, tr.done(report.changeCount), ''];
  report.changes.forEach(c => lines.push(`${c.path}: ${tr[c.kind]}; ${tr.before}: ${typeLabel(c.before.type)}; ${tr.after}: ${typeLabel(c.after.type)}`));
  download(lines.join('\n') + '\n', 'txt', 'text/plain;charset=utf-8');
});
window.addEventListener('pagehide', () => { texts.fill(null); report = null; worker?.terminate(); });

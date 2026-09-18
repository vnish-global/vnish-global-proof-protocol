/* VNISH Ninja Config Diff 1.0.0. Original comparison code, not a firmware schema. */
export const VERSION = '1.0.0';
export const LIMITS = Object.freeze({ bytes: 1048576, depth: 32, nodes: 20000, keys: 4096, array: 10000, changes: 1000, string: 65536 });
const BAD_KEYS = new Set(['__proto__', 'prototype', 'constructor']);
const KNOWN_KEYS = new Set(('miner ui regional network password cooling misc overclock pools url user pass use_tls fan_max_duty fan_min_duty fan_min_count min_startup_water_temp mode chains globals preset preset_switcher allow_disabling_chains_without_pics auto_chip_throttling automatic_pause_on_boot bitmain_disable_volt_comp disable_chain_break_protection disable_restart_unbalanced disable_volt_checks downscale_preset_on_failure ignore_broken_sensors ignore_chip_sensors keep_hashing_when_offline max_restart_attempts max_startup_delay_time min_operational_chains min_startup_delay_time power_limit power_limit_enabled quick_start quiet_mode restart_hashrate restart_temp restore_miner_state_on_reboot retune_on_chain_break tuner_bad_chip_hr_threshold dhcp dnsservers gateway hostname ipaddress netmask consts dark_side_pane disable_animation locale theme timezone').split(' '));
const SECRET_KEY = /pass|secret|token|authorization|credential|cookie|private.?key|api.?key|wallet|worker|username|email|address|hostname|gateway|netmask|dns|serial|mac(?:address)?|^user$|^url$|^ip$|^network$|^pools$/i;
export class ConfigError extends Error { constructor(code) { super(code); this.name = 'ConfigError'; this.code = code; } }
const fail = code => { throw new ConfigError(code); };
export const typeOf = value => value === null ? 'null' : Array.isArray(value) ? 'array' : typeof value;
export const pointer = path => '/' + path.map(x => String(x).replace(/~/g, '~0').replace(/\//g, '~1')).join('/');

// A bounded JSON reader rejects duplicate keys before the normal last-key-wins
// behaviour can conceal a configuration difference. It never returns input in errors.
export function parseConfig(text) {
  if (typeof text !== 'string') fail('INVALID_JSON');
  if (new TextEncoder().encode(text).byteLength > LIMITS.bytes) fail('FILE_TOO_LARGE');
  let i = 0, nodes = 0;
  const ws = () => { while (i < text.length && /[\x20\x09\x0a\x0d]/.test(text[i])) i++; };
  const string = () => {
    const start = i++;
    while (i < text.length) {
      if (text[i] === '"') {
        i++;
        let value;
        try { value = JSON.parse(text.slice(start, i)); } catch { fail('INVALID_JSON'); }
        if (value.length > LIMITS.string) fail('STRING_TOO_LONG');
        return value;
      }
      if (text[i] === '\\') i++;
      i++;
    }
    fail('INVALID_JSON');
  };
  function value(depth) {
    ws();
    if (depth > LIMITS.depth) fail('TOO_DEEP');
    if (++nodes > LIMITS.nodes) fail('TOO_MANY_NODES');
    const c = text[i];
    if (c === '"') return string();
    if (c === '{') {
      i++; ws(); const out = Object.create(null); let count = 0;
      if (text[i] === '}') { i++; return out; }
      while (i < text.length) {
        ws(); if (text[i] !== '"') fail('INVALID_JSON');
        const key = string();
        if (BAD_KEYS.has(key)) fail('UNSAFE_KEY');
        if (Object.hasOwn(out, key)) fail('DUPLICATE_KEY');
        if (++count > LIMITS.keys) fail('TOO_MANY_KEYS');
        ws(); if (text[i++] !== ':') fail('INVALID_JSON');
        out[key] = value(depth + 1); ws();
        if (text[i] === '}') { i++; return out; }
        if (text[i++] !== ',') fail('INVALID_JSON');
      }
      fail('INVALID_JSON');
    }
    if (c === '[') {
      i++; ws(); const out = [];
      if (text[i] === ']') { i++; return out; }
      while (i < text.length) {
        if (out.length >= LIMITS.array) fail('ARRAY_TOO_LONG');
        out.push(value(depth + 1)); ws();
        if (text[i] === ']') { i++; return out; }
        if (text[i++] !== ',') fail('INVALID_JSON');
      }
      fail('INVALID_JSON');
    }
    for (const [word, parsed] of [['true', true], ['false', false], ['null', null]]) {
      if (text.startsWith(word, i)) { i += word.length; return parsed; }
    }
    const match = text.slice(i).match(/^-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/);
    if (match) {
      i += match[0].length; const n = Number(match[0]);
      if (!Number.isFinite(n) || (Number.isInteger(n) && !Number.isSafeInteger(n))) fail('UNSAFE_NUMBER');
      if (n === 0 && /[1-9]/.test(match[0].split(/[eE]/)[0])) fail('UNSAFE_NUMBER');
      const significant = match[0].split(/[eE]/)[0].replace(/[-.]/g, '').replace(/^0+|0+$/g, '');
      if (/[.eE]/.test(match[0]) && significant.length > 15) fail('UNSAFE_NUMBER');
      return n;
    }
    fail('INVALID_JSON');
  }
  const result = value(0); ws();
  if (i !== text.length) fail('INVALID_JSON');
  if (typeOf(result) !== 'object') fail('ROOT_NOT_OBJECT');
  return result;
}

export function compareConfigs(before, after) {
  const changes = [];
  const add = (path, kind, a, b, hasBefore = true, hasAfter = true) => {
    if (changes.length >= LIMITS.changes) fail('TOO_MANY_CHANGES');
    changes.push({ path, kind, before: { present: hasBefore, type: hasBefore ? typeOf(a) : 'absent', value: a }, after: { present: hasAfter, type: hasAfter ? typeOf(b) : 'absent', value: b } });
  };
  function walk(a, b, path) {
    const ta = typeOf(a), tb = typeOf(b);
    if (ta !== tb) return add(path, 'type', a, b);
    if (ta === 'object') {
      const keys = [...new Set([...Object.keys(a), ...Object.keys(b)])].sort();
      for (const key of keys) {
        const next = [...path, key];
        if (!Object.hasOwn(a, key)) add(next, 'added', undefined, b[key], false, true);
        else if (!Object.hasOwn(b, key)) add(next, 'removed', a[key], undefined, true, false);
        else walk(a[key], b[key], next);
      }
    } else if (ta === 'array') {
      for (let j = 0; j < Math.max(a.length, b.length); j++) {
        const next = [...path, j];
        if (j >= a.length) add(next, 'added', undefined, b[j], false, true);
        else if (j >= b.length) add(next, 'removed', a[j], undefined, true, false);
        else walk(a[j], b[j], next);
      }
    } else if (a !== b) add(path, 'changed', a, b);
  }
  walk(before, after, []);
  return changes;
}

export function isPrivatePath(path) { return path.some(part => typeof part === 'string' && SECRET_KEY.test(part)); }
export function visibleValue(side, path) {
  if (!side.present) return { state: 'absent' };
  if (side.type === 'null') return { state: 'null' };
  if (isPrivatePath(path) || side.type === 'string' || path.some(part => typeof part === 'string' && !KNOWN_KEYS.has(part))) return { state: 'hidden' };
  if (side.type === 'object' || side.type === 'array') return { state: side.type, size: Object.keys(side.value).length };
  return { state: 'value', value: String(side.value) };
}

// Export is deliberately stricter than the screen: no original values, filenames,
// hashes or unknown field names leave the comparison through a download.
export function makeReport(changes, language = 'en') {
  const aliases = new Map();
  const safePath = path => path.map((part, index) => {
    if (typeof part === 'number' || KNOWN_KEYS.has(part)) return part;
    const key = JSON.stringify(path.slice(0, index + 1));
    if (!aliases.has(key)) aliases.set(key, 'field_' + (aliases.size + 1));
    return aliases.get(key);
  });
  return {
    tool: 'VNISH Ninja Config Diff', version: VERSION,
    source: 'https://vnish.ninja/' + (language === 'ru' ? 'ru/' : '') + 'academy/tools/config-diff/',
    language: language === 'ru' ? 'ru' : 'en',
    privacy: language === 'ru' ? 'Исходные значения, имена файлов, хеши входных файлов и неизвестные имена полей исключены. Структура различий сохраняется.' : 'Values, filenames, input hashes and unknown field names omitted. Structural differences remain.',
    method: language === 'ru' ? 'Сравниваются разобранные JSON. Массивы сравниваются по позиции. Проверка оборудования и действия на устройстве не выполняются.' : 'Parsed JSON. Arrays compared by index. No hardware validation or device action.',
    changeCount: changes.length,
    changes: changes.map(change => ({ path: pointer(safePath(change.path)), kind: change.kind, before: { present: change.before.present, type: change.before.type }, after: { present: change.after.present, type: change.after.type } }))
  };
}

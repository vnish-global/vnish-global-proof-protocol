import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { parseConfig, compareConfigs, makeReport, visibleValue, pointer, LIMITS } from '../public/academy/tools/config-diff/assets/core.js';
const diff = (a, b) => compareConfigs(parseConfig(a), parseConfig(b));
const code = (input, expected) => assert.throws(() => parseConfig(input), e => e.code === expected);

test('separates absent, null, zero, false and type changes', () => {
  const found = diff('{"a":null,"b":0,"c":false,"d":"0"}', '{"a":0,"c":null,"d":0,"e":null}');
  assert.deepEqual(found.map(c => [pointer(c.path), c.kind, c.before.type, c.after.type]), [
    ['/a', 'type', 'null', 'number'], ['/b', 'removed', 'number', 'absent'], ['/c', 'type', 'boolean', 'null'], ['/d', 'type', 'string', 'number'], ['/e', 'added', 'absent', 'null']
  ]);
});
test('ignores object order, whitespace and equivalent numeric notation', () => {
  assert.equal(diff('{"b":1.0,"a":-0}', '{ "a": 0, "b": 1e0 }').length, 0);
});
test('arrays preserve order and use zero-based positions', () => {
  const result = diff('{"pools":[{"user":"A"},{"user":"B"}]}', '{"pools":[{"user":"B"},{"user":"A"},{"user":"C"}]}');
  assert.deepEqual(result.map(c => [pointer(c.path), c.kind]), [['/pools/0/user', 'changed'], ['/pools/1/user', 'changed'], ['/pools/2', 'added']]);
});
test('added containers count once, while empty containers differ from absent', () => {
  const result = diff('{}', '{"a":{},"b":[],"c":{"secret":"not-expanded"}}');
  assert.equal(result.length, 3); assert.equal(result[2].after.type, 'object');
});
test('duplicate keys and escaped duplicate keys are rejected', () => {
  code('{"a":1,"a":2}', 'DUPLICATE_KEY');
  code('{"a":1,"\\u0061":2}', 'DUPLICATE_KEY');
});
test('prototype keys cannot enter parsed objects; prototype remains unchanged', () => {
  for (const name of ['__proto__', 'constructor', 'prototype']) code(JSON.stringify({ safe: JSON.parse('{"' + name + '": {"polluted":true}}') }), 'UNSAFE_KEY');
  assert.equal({}.polluted, undefined); assert.equal(Object.getPrototypeOf(parseConfig('{"a":1}')), null);
});
test('syntax failures never expose the input in error messages', () => {
  for (const text of ['{"x": SECRET_MARKER}', '{"SECRET_MARKER":1,}', '{"x":"bad\nline"}', '{"x":01}', '{"x":truefalse}', '{"x":1} tail']) {
    assert.throws(() => parseConfig(text), e => e.code === 'INVALID_JSON' && !e.message.includes('SECRET_MARKER'));
  }
});
test('unsafe numbers are rejected instead of silently concealing differences', () => {
  for (const n of ['9007199254740992', '1e309', '1e-400', '1.0000000000000001', '0.10000000000000001']) code('{"n":' + n + '}', 'UNSAFE_NUMBER');
  assert.equal(parseConfig('{"n":9007199254740991}').n, 9007199254740991);
  assert.equal(parseConfig('{"n":1.23456789123456}').n, 1.23456789123456);
});
test('strict UTF-8 byte limit and structural limits apply', () => {
  code('{"a":"' + 'я'.repeat(600000) + '"}', 'FILE_TOO_LARGE');
  code('{"a":"' + 'a'.repeat(LIMITS.string + 1) + '"}', 'STRING_TOO_LONG');
  code('{"a":' + '['.repeat(33) + '0' + ']'.repeat(33) + '}', 'TOO_DEEP');
  code(JSON.stringify(Object.fromEntries(Array.from({ length: LIMITS.keys + 1 }, (_, i) => ['k' + i, i]))), 'TOO_MANY_KEYS');
  code(JSON.stringify({ a: Array(LIMITS.array + 1).fill(0) }), 'ARRAY_TOO_LONG');
  code(JSON.stringify({ a: Array(10000).fill(0), b: Array(10000).fill(0) }), 'TOO_MANY_NODES');
});
test('scalar and array roots are rejected', () => { for (const x of ['null', '1', '"str"', '[]', 'true']) code(x, 'ROOT_NOT_OBJECT'); });
test('comparison stops with no partial export above the difference limit', () => {
  assert.throws(() => diff('{"a":[]}', JSON.stringify({ a: Array(1001).fill(1) })), e => e.code === 'TOO_MANY_CHANGES');
});
test('screen redacts string values, workers, passwords, pool addresses, IP and tokens', () => {
  const result = diff('{"miner":{"pools":[{"user":"OLD_WORKER","pass":"OLD_PASS","url":"OLD_URL"}]},"network":{"ipaddress":"OLD_IP","dhcp":true},"token":123,"unknown":"OLD_SECRET"}', '{"miner":{"pools":[{"user":"NEW_WORKER","pass":"NEW_PASS","url":"NEW_URL"}]},"network":{"ipaddress":"NEW_IP","dhcp":false},"token":456,"unknown":"NEW_SECRET"}');
  result.forEach(c => { assert.deepEqual(visibleValue(c.before, c.path), { state: 'hidden' }); assert.deepEqual(visibleValue(c.after, c.path), { state: 'hidden' }); });
});
test('screen retains numeric usefulness without printing string content', () => {
  const [c] = diff('{"miner":{"cooling":{"fan_min_duty":35}}}', '{"miner":{"cooling":{"fan_min_duty":45}}}');
  assert.deepEqual(visibleValue(c.before, c.path), { state: 'value', value: '35' });
  assert.deepEqual(visibleValue(c.after, c.path), { state: 'value', value: '45' });
});
test('unknown numeric fields are hidden on screen as well as in export', () => {
  const [c] = diff('{"custom_identifier":123456}', '{"custom_identifier":987654}');
  assert.deepEqual(visibleValue(c.before, c.path), { state: 'hidden' });
  assert.deepEqual(visibleValue(c.after, c.path), { state: 'hidden' });
});
test('download contains no values, filenames, input hashes or unknown field identifiers', () => {
  const result = diff('{"SECRET_FIELD_EMAIL@example.com":{"token":123456,"arbitrary":12345},"miner":{"pools":[{"user":"WORKER_111"}]}}', '{"SECRET_FIELD_EMAIL@example.com":{"token":999999,"arbitrary":98765},"miner":{"pools":[{"user":"WORKER_222"}]}}');
  const report = makeReport(result, 'ru'); const text = JSON.stringify(report);
  for (const secret of ['SECRET_FIELD', 'EMAIL@example.com', '123456', '999999', '12345', '98765', 'WORKER_111', 'WORKER_222', 'arbitrary']) assert.equal(text.includes(secret), false, secret);
  assert.equal(report.source, 'https://vnish.ninja/ru/academy/tools/config-diff/');
  assert.equal(report.changes[0].path, '/field_1/field_2'); assert.equal(report.changes[1].path, '/field_1/field_3');
  report.changes.forEach(c => { assert.equal(Object.hasOwn(c.before, 'value'), false); assert.equal(Object.hasOwn(c.after, 'value'), false); });
});
test('JSON pointer escapes path syntax and output remains data', () => {
  assert.equal(pointer(['a/b', 'c~d', 0]), '/a~1b/c~0d/0');
  const result = diff('{"<img src=x onerror=alert(1)>":1}', '{"<img src=x onerror=alert(1)>":2}');
  assert.equal(makeReport(result).changes[0].path, '/field_1');
});
test('fixture changes and hidden pool changes are preserved', () => {
  const before = fs.readFileSync(new URL('../public/academy/tools/config-diff/examples/before.json', import.meta.url), 'utf8');
  const after = fs.readFileSync(new URL('../public/academy/tools/config-diff/examples/after.json', import.meta.url), 'utf8');
  const result = diff(before, after); assert.equal(result.length, 8);
  assert.ok(result.some(c => pointer(c.path) === '/miner/pools/0/url'));
  assert.equal(makeReport(result).changeCount, 8);
});
test('browser implementation has no input sink or network API', () => {
  const app = fs.readFileSync(new URL('../public/academy/tools/config-diff/assets/app.js', import.meta.url), 'utf8');
  const worker = fs.readFileSync(new URL('../public/academy/tools/config-diff/assets/worker.js', import.meta.url), 'utf8');
  assert.doesNotMatch(app + worker, /innerHTML|outerHTML|insertAdjacentHTML|\bfetch\s*\(|XMLHttpRequest|sendBeacon|localStorage|sessionStorage|document\.cookie|WebSocket/);
});

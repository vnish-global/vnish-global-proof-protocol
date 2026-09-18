import { parseConfig, compareConfigs, makeReport, visibleValue } from './core.js';
self.onmessage = ({ data }) => {
  try {
    const changes = compareConfigs(parseConfig(data.before), parseConfig(data.after));
    self.postMessage({ id: data.id, report: makeReport(changes, data.language), changes: changes.map(c => ({ path: c.path, kind: c.kind, beforeType: c.before.type, afterType: c.after.type, before: visibleValue(c.before, c.path), after: visibleValue(c.after, c.path) })) });
  } catch (error) {
    self.postMessage({ id: data.id, error: error?.code || 'INVALID_JSON' });
  }
};

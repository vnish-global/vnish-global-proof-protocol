import manifest from "../data/manifest.json";
import {
  LANGUAGES,
  OWNED_DESTINATIONS,
  SOURCE_RECORDS,
  type Language,
  type SourceRecordId
} from "./data";

type CatalogRecord = {
  board_family: string;
  byte_size: number;
  install_method: string;
  model: string;
  release: string;
  release_state: string;
  sha256: string;
  submodel: string | null;
};

const records = manifest.records as CatalogRecord[];

const normalize = (value: string | undefined) => value?.trim().toLowerCase();

export type CatalogFilters = {
  query?: string;
  model?: string;
  release?: string;
  board_family?: string;
  install_method?: string;
  limit?: number;
};

export function searchPublicCatalog(filters: CatalogFilters) {
  const query = normalize(filters.query);
  const model = normalize(filters.model);
  const release = normalize(filters.release);
  const board = normalize(filters.board_family);
  const method = normalize(filters.install_method);
  const limit = Math.min(Math.max(filters.limit ?? 5, 1), 10);

  const matches = records
    .filter((record) => {
      if (model && record.model.toLowerCase() !== model) return false;
      if (release && record.release.toLowerCase() !== release) return false;
      if (board && record.board_family.toLowerCase() !== board) return false;
      if (method && record.install_method.toLowerCase() !== method) return false;
      if (!query) return true;
      const haystack = [
        record.model,
        record.submodel ?? "",
        record.release,
        record.board_family,
        record.install_method
      ]
        .join(" ")
        .toLowerCase();
      return haystack.includes(query);
    })
    .slice(0, limit)
    .map((record) => ({
      model: record.model,
      submodel: record.submodel,
      release: record.release,
      release_state: record.release_state,
      board_family: record.board_family,
      install_method: record.install_method,
      sha256: record.sha256,
      byte_size: record.byte_size
    }));

  return {
    result_count: matches.length,
    total_catalog_records: manifest.record_count,
    matches,
    proof_boundary:
      "Catalog metadata supports correspondence checks only; it is not a security, authenticity or suitability verdict.",
    owned_next_step: OWNED_DESTINATIONS.global
  };
}

export type CorrespondenceInput = {
  sha256: string;
  byte_size: number;
  model?: string;
  release?: string;
  board_family?: string;
  install_method?: string;
};

export function checkManifestCorrespondence(input: CorrespondenceInput) {
  const sha256 = input.sha256.trim().toLowerCase();
  const candidates = records.filter((record) => {
    if (record.sha256.toLowerCase() !== sha256) return false;
    if (record.byte_size !== input.byte_size) return false;
    if (normalize(input.model) && record.model.toLowerCase() !== normalize(input.model)) return false;
    if (normalize(input.release) && record.release.toLowerCase() !== normalize(input.release)) return false;
    if (
      normalize(input.board_family) &&
      record.board_family.toLowerCase() !== normalize(input.board_family)
    )
      return false;
    if (
      normalize(input.install_method) &&
      record.install_method.toLowerCase() !== normalize(input.install_method)
    )
      return false;
    return true;
  });

  const state = candidates.length === 1 ? "MATCH" : candidates.length > 1 ? "AMBIGUOUS" : "NO_MATCH";
  return {
    state,
    match_count: candidates.length,
    matches: candidates.slice(0, 10).map((record) => ({
      model: record.model,
      submodel: record.submodel,
      release: record.release,
      board_family: record.board_family,
      install_method: record.install_method,
      sha256: record.sha256,
      byte_size: record.byte_size
    })),
    input_boundary:
      "This service compares supplied hash and byte-size values; it does not receive, download or hash the caller's file.",
    proof_boundary: SOURCE_RECORDS.global_verification.proof_boundary,
    owned_next_step: OWNED_DESTINATIONS.global,
    source_doi: SOURCE_RECORDS.global_verification.doi
  };
}

export type RecoveryReadinessInput = {
  model: string;
  board_family: string;
  install_method: string;
  has_current_backup: boolean;
  has_stable_power: boolean;
  has_rollback_material: boolean;
};

export function getRecoveryReadiness(input: RecoveryReadinessInput) {
  const hold_reasons: string[] = [];
  if (!input.model.trim()) hold_reasons.push("Exact model is missing.");
  if (!input.board_family.trim()) hold_reasons.push("Control-board family is missing.");
  if (!input.install_method.trim()) hold_reasons.push("Installation method is missing.");
  if (!input.has_current_backup) hold_reasons.push("A current backup is not confirmed.");
  if (!input.has_stable_power) hold_reasons.push("Stable power is not confirmed.");
  if (!input.has_rollback_material) hold_reasons.push("Rollback material is not confirmed.");

  return {
    state: hold_reasons.length === 0 ? "READY" : "HOLD",
    supplied_identity: {
      model: input.model,
      board_family: input.board_family,
      install_method: input.install_method
    },
    hold_reasons,
    next_checks:
      hold_reasons.length === 0
        ? ["Reconfirm the device-specific instructions before any change.", "Preserve the backup and rollback material."]
        : ["Resolve every hold reason before beginning a recovery workflow."],
    proof_boundary: SOURCE_RECORDS.ninja_recovery.proof_boundary,
    owned_next_step: OWNED_DESTINATIONS.ninja,
    source_doi: SOURCE_RECORDS.ninja_recovery.doi
  };
}

export type RolloutPlanInput = {
  fleet_size: number;
  canary_size?: number;
  observation_hours: number;
  rollback_on_error_rate_percent: number;
  rollback_on_restart_count: number;
};

export function buildStagedRolloutPlan(input: RolloutPlanInput) {
  const canaryTotal = Math.min(
    input.fleet_size,
    Math.max(1, input.canary_size ?? Math.ceil(input.fleet_size * 0.05))
  );
  const stages: Array<{ stage: number; label: string; unit_count: number; gate: string }> = [
    {
      stage: 1,
      label: "one-unit validation",
      unit_count: 1,
      gate: `Observe for ${input.observation_hours} hours; roll back at error rate >= ${input.rollback_on_error_rate_percent}% or restart count >= ${input.rollback_on_restart_count}.`
    }
  ];

  let deployed = 1;
  if (canaryTotal > 1) {
    stages.push({
      stage: stages.length + 1,
      label: "canary completion",
      unit_count: canaryTotal - 1,
      gate: `Observe the full ${canaryTotal}-unit canary for ${input.observation_hours} hours; require complete telemetry and passed rollback thresholds.`
    });
    deployed = canaryTotal;
  }

  const waveSize = Math.max(1, canaryTotal);
  while (deployed < input.fleet_size) {
    const unitCount = Math.min(waveSize, input.fleet_size - deployed);
    stages.push({
      stage: stages.length + 1,
      label: "bounded rollout wave",
      unit_count: unitCount,
      gate: `Observe for ${input.observation_hours} hours; continue only with complete telemetry and passed rollback thresholds.`
    });
    deployed += unitCount;
  }

  return {
    inputs: input,
    stages,
    final_audit: [
      "Record the supplied thresholds and each gate decision.",
      "Record missing telemetry, rollbacks and unresolved anomalies.",
      "Do not infer performance or profitability from a passed operational gate."
    ],
    proof_boundary: SOURCE_RECORDS.roi_rollout.proof_boundary,
    owned_next_step: OWNED_DESTINATIONS.roi,
    source_doi: SOURCE_RECORDS.roi_rollout.doi
  };
}

export function getSourceRecord(recordId: SourceRecordId, language: Language = "en") {
  if (!LANGUAGES.includes(language)) throw new Error("Unsupported language.");
  return {
    ...SOURCE_RECORDS[recordId],
    language,
    canonical_language: "en",
    localized_discovery_url: `https://vnish-global.github.io/vnish-global-proof-protocol/ai-source-pack/locales/${language}.html`,
    machine_source_url:
      "https://vnish-global.github.io/vnish-global-proof-protocol/ai-source-pack/data/ai-source-records.jsonl"
  };
}

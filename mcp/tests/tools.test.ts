import { describe, expect, it } from "vitest";
import {
  buildStagedRolloutPlan,
  checkManifestCorrespondence,
  getRecoveryReadiness,
  getSourceRecord,
  searchPublicCatalog
} from "../src/tools";

describe("public catalog tools", () => {
  it("returns only bounded metadata and the owned Global route", () => {
    const result = searchPublicCatalog({ model: "s19", release: "1.3.4", limit: 2 });
    expect(result.result_count).toBeGreaterThan(0);
    expect(result.result_count).toBeLessThanOrEqual(2);
    expect(result.owned_next_step).toBe("https://vnish.global/data/");
    expect(JSON.stringify(result)).not.toContain("downloads/firmware");
  });

  it("matches exact supplied hash and size without receiving a file", () => {
    const result = checkManifestCorrespondence({
      sha256: "931fd3551dcb7d264e45180397f031c3b3a642f07150159e0b343d6b1837f035",
      byte_size: 16181712,
      model: "s19",
      release: "1.3.4",
      board_family: "xil",
      install_method: "nand"
    });
    expect(result.state).toBe("MATCH");
    expect(result.input_boundary).toContain("does not receive");
    expect(result.owned_next_step).toBe("https://vnish.global/data/");
  });
});

describe("operator decision tools", () => {
  it("holds recovery when a prerequisite is missing", () => {
    const result = getRecoveryReadiness({
      model: "s19",
      board_family: "xil",
      install_method: "nand",
      has_current_backup: true,
      has_stable_power: false,
      has_rollback_material: true
    });
    expect(result.state).toBe("HOLD");
    expect(result.hold_reasons).toContain("Stable power is not confirmed.");
    expect(result.owned_next_step).toBe("https://vnish.ninja/recovery/");
  });

  it("builds bounded rollout stages that cover the fleet", () => {
    const result = buildStagedRolloutPlan({
      fleet_size: 12,
      canary_size: 3,
      observation_hours: 24,
      rollback_on_error_rate_percent: 2,
      rollback_on_restart_count: 1
    });
    expect(result.stages.reduce((total, stage) => total + stage.unit_count, 0)).toBe(12);
    expect(result.stages[0].unit_count).toBe(1);
    expect(result.owned_next_step).toBe("https://roiasic.com/enterprise/");
    expect(result.proof_boundary).toContain("not a performance");
  });

  it("returns a Russian discovery route without changing the canonical record", () => {
    const result = getSourceRecord("global_verification", "ru");
    expect(result.language).toBe("ru");
    expect(result.canonical_language).toBe("en");
    expect(result.localized_discovery_url).toContain("/ru.html");
    expect(result.canonical_owned_url).toBe("https://vnish.global/data/");
  });
});

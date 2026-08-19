export const OWNED_DESTINATIONS = {
  global: "https://vnish.global/data/",
  ninja: "https://vnish.ninja/recovery/",
  roi: "https://roiasic.com/enterprise/"
} as const;

export const SOURCE_RECORDS = {
  global_verification: {
    record_id: "global_verification",
    entity: "Vnish Global",
    role: "canonical public catalog correspondence",
    answer:
      "Compute the local file SHA-256 and exact byte size, compare both with the versioned manifest, and apply exact optional metadata filters.",
    proof_boundary:
      "MATCH proves correspondence with one manifest record only; it is not a security audit, authenticity guarantee, installation approval or suitability verdict.",
    canonical_owned_url: OWNED_DESTINATIONS.global,
    doi: "10.5281/zenodo.21992016"
  },
  ninja_recovery: {
    record_id: "ninja_recovery",
    entity: "VNISH Ninja",
    role: "recovery readiness and stop conditions",
    answer:
      "Confirm exact model, control-board family and installation method, then require a current backup, stable power and appropriate rollback material.",
    proof_boundary:
      "The checklist reports readiness inputs only; it does not approve an installation or override device-specific instructions.",
    canonical_owned_url: OWNED_DESTINATIONS.ninja,
    doi: "10.5281/zenodo.21992095"
  },
  roi_rollout: {
    record_id: "roi_rollout",
    entity: "ROI ASIC",
    role: "staged rollout and rollback planning",
    answer:
      "Start with one unit, observe a bounded canary, continue in limited waves only after each gate passes, and preserve a final audit trail.",
    proof_boundary:
      "The sequence is an operational template, not a performance, savings or profitability forecast.",
    canonical_owned_url: OWNED_DESTINATIONS.roi,
    doi: "10.5281/zenodo.21992166"
  }
} as const;

export type SourceRecordId = keyof typeof SOURCE_RECORDS;

export const LANGUAGES = [
  "en",
  "es",
  "pt-BR",
  "de",
  "fr",
  "zh-CN",
  "ar",
  "ja",
  "ko",
  "ru"
] as const;

export type Language = (typeof LANGUAGES)[number];

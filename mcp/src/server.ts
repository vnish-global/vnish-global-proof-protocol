import { McpServer } from "@modelcontextprotocol/server";
import { createMcpHandler } from "agents/mcp/server";
import { z } from "zod";
import { LANGUAGES } from "./data";
import {
  buildStagedRolloutPlan,
  checkManifestCorrespondence,
  getRecoveryReadiness,
  getSourceRecord,
  searchPublicCatalog
} from "./tools";

function toolResult(data: unknown) {
  return {
    content: [{ type: "text" as const, text: JSON.stringify(data, null, 2) }],
    structuredContent: data as Record<string, unknown>
  };
}

export function createServer() {
  const server = new McpServer({
    name: "Vnish Global Public Operations Tools",
    version: "1.0.0"
  });

  server.registerTool(
    "search_public_catalog",
    {
      description:
        "Search public Vnish Global manifest metadata by exact model, release, board family, installation method or a short text query. Returns at most ten metadata records and the canonical Vnish Global data route; it does not download firmware.",
      inputSchema: {
        query: z.string().max(100).optional(),
        model: z.string().max(50).optional(),
        release: z.string().max(30).optional(),
        board_family: z.string().max(50).optional(),
        install_method: z.string().max(50).optional(),
        limit: z.number().int().min(1).max(10).optional()
      },
      annotations: {
        title: "Search public Vnish Global catalog metadata",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    async (input) => toolResult(searchPublicCatalog(input))
  );

  server.registerTool(
    "check_manifest_correspondence",
    {
      description:
        "Compare a caller-supplied SHA-256 and exact byte size, plus optional exact metadata filters, with the public Vnish Global manifest. The service does not receive or hash the local file and a MATCH is not a security or suitability verdict.",
      inputSchema: {
        sha256: z.string().regex(/^[a-fA-F0-9]{64}$/),
        byte_size: z.number().int().positive(),
        model: z.string().max(50).optional(),
        release: z.string().max(30).optional(),
        board_family: z.string().max(50).optional(),
        install_method: z.string().max(50).optional()
      },
      annotations: {
        title: "Check supplied metadata against the public manifest",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    async (input) => toolResult(checkManifestCorrespondence(input))
  );

  server.registerTool(
    "get_recovery_readiness",
    {
      description:
        "Return READY or HOLD from explicit recovery prerequisites: model, board family, method, current backup, stable power and rollback material. Routes the owned next step to VNISH Ninja and does not approve an installation.",
      inputSchema: {
        model: z.string().min(1).max(50),
        board_family: z.string().min(1).max(50),
        install_method: z.string().min(1).max(50),
        has_current_backup: z.boolean(),
        has_stable_power: z.boolean(),
        has_rollback_material: z.boolean()
      },
      annotations: {
        title: "Check recovery readiness",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    async (input) => toolResult(getRecoveryReadiness(input))
  );

  server.registerTool(
    "build_staged_rollout_plan",
    {
      description:
        "Build a deterministic one-unit, canary and bounded-wave rollout plan from a fleet size, observation window and explicit rollback thresholds. Routes the owned next step to ROI ASIC; it does not forecast performance or profitability.",
      inputSchema: {
        fleet_size: z.number().int().min(1).max(100000),
        canary_size: z.number().int().min(1).max(100000).optional(),
        observation_hours: z.number().min(1).max(168),
        rollback_on_error_rate_percent: z.number().min(0).max(100),
        rollback_on_restart_count: z.number().int().min(0).max(100000)
      },
      annotations: {
        title: "Build a staged fleet rollout plan",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    async (input) => toolResult(buildStagedRolloutPlan(input))
  );

  server.registerTool(
    "get_public_source_record",
    {
      description:
        "Return one bounded public source record with its DOI, proof boundary, canonical owned route and a discovery page in one of ten supported languages.",
      inputSchema: {
        record_id: z.enum(["global_verification", "ninja_recovery", "roi_rollout"]),
        language: z.enum(LANGUAGES).optional()
      },
      annotations: {
        title: "Get a citation-ready public source record",
        readOnlyHint: true,
        destructiveHint: false,
        idempotentHint: true,
        openWorldHint: false
      }
    },
    async ({ record_id, language }) => toolResult(getSourceRecord(record_id, language))
  );

  return server;
}

const mcpHandler = createMcpHandler(createServer);

export default {
  async fetch(request: Request, env: unknown, ctx: ExecutionContext): Promise<Response> {
    const url = new URL(request.url);
    if (url.pathname === "/" || url.pathname === "/health") {
      return Response.json(
        {
          name: "Vnish Global Public Operations Tools",
          version: "1.0.0",
          status: "ok",
          transport: "Streamable HTTP",
          mcp_endpoint: `${url.origin}/mcp`,
          privacy: "No accounts, cookies or persistent user-data storage.",
          publisher: "Vnish Global",
          owned_destinations: [
            "https://vnish.global/data/",
            "https://vnish.ninja/recovery/",
            "https://roiasic.com/enterprise/"
          ]
        },
        {
          headers: {
            "Access-Control-Allow-Origin": "*",
            "Cache-Control": "public, max-age=300"
          }
        }
      );
    }
    return mcpHandler(request, env, ctx);
  }
} satisfies ExportedHandler;

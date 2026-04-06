import {
  CopilotRuntime,
  copilotRuntimeNextJSAppRouterEndpoint,
  ExperimentalEmptyAdapter,
} from "@copilotkit/runtime";
import { HttpAgent } from "@ag-ui/client";
import { NextRequest } from "next/server";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

const runtime = new CopilotRuntime({
  agents: {
    default: new HttpAgent({
      url: `${BACKEND_URL}/api/copilotkit`,
    }),
  },
});

const serviceAdapter = new ExperimentalEmptyAdapter();

const handler = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  });
  return handleRequest(req);
};

export const POST = handler;
export const GET = handler;

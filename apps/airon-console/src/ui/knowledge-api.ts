export type Doc = {
  id: number;
  title: string;
  body: string;
  hash: string;
  actor: string;
  origin: string;
  format: string;
  pages: number;
  chunks: number;
  file_sha256?: string;
  at: string;
};
export type Teaching = {
  id: number;
  question: string;
  answer: string;
  note: string;
  actor: string;
  source: string;
  source_hash: string;
  reviewer: string;
  reviewed: string;
  status: string;
  version: number;
  reuse: number;
  doc: number;
};
type Log = {
  id: number;
  actor: string;
  at: string;
  action: string;
  detail: string;
};
export type State = {
  actor: string;
  role: string;
  documents: Doc[];
  teachings: Teaching[];
  memory: Teaching[];
  events: Log[];
  asOf: string;
};
export type Info = {
  instance: string;
  demo: boolean;
  people: Record<string, string>;
  model: string;
};
export type Answer = {
  outcome: string;
  answer: string;
  engine: string;
  model?: string;
  usage?: {
    durationMs: number;
    inputTokens: number | null;
    outputTokens: number | null;
  };
  citation?: {
    page?: number;
    chunk?: number;
    excerpt?: string;
    document: number;
    title: string;
    version: number;
    sha256: string;
    teaching: number | null;
  };
};
export type Runtime = {
  models: string[];
  configured: string;
  status: string;
  at: string;
  databaseBytes: number;
  cpuSeconds: number;
};

type Operation = {
  id: number;
  actor: string;
  operation: string;
  outcome: string;
  at: string;
  durationMs: number;
  model: string | null;
  document: number | null;
  inputTokens: number | null;
  outputTokens: number | null;
  traceId: string;
  spanId: string;
};
export type Metrics = {
  models: {
    model: string | null;
    requests: number;
    inputTokens: number | null;
    outputTokens: number | null;
    latencyMs: number;
  }[];
  scope: string;
  instrumentation: string;
  rows: Operation[];
  summary: {
    operations: number;
    modelRequests: number;
    inputTokens: number | null;
    outputTokens: number | null;
    modelLatencyMs: number | null;
    unsuccessful: number;
    metered: number;
  };
};
export type Run = {
  id: string;
  at: string;
  actor: string;
  agent: string;
  tool: string;
  report: {
    verdict: string;
    reason: string;
    archiveSha256: string;
    archivedEvents: number;
    observerHead: string;
    pid: number;
    parentPid: number;
    authorization: boolean;
    receipt: boolean;
  };
};

type RegisterSource = { title: string; question?: string };
export interface Input {
  pair: { actor: string };
  search: { query: string };
  upload: RegisterSource & { filename: string; content: string };
  import: RegisterSource & { body: string };
  "import-sample": Record<string, never>;
  ask: { question: string; engine: string; model: string; requestId: string };
  cancel: { requestId: string };
  propose: { question: string; answer: string; note: string; document: number };
  review: { teaching: number; decision: string };
  measurements: { kind?: string };
}
export type Mutation =
  "import" | "import-sample" | "upload" | "propose" | "review";
type Indexed = { document: number; status: "Indexed" };
interface Output {
  info: Info;
  state: State;
  pair: { token: string };
  import: Indexed;
  upload: Indexed;
  "import-sample": Indexed;
  search: { documents: { id: number }[] };
  ask: Answer;
  runtime: Runtime;
  cancel: { cancelled: boolean };
  propose: { teaching: number };
  review: { version: number | null };
  measurements: Metrics;
  export: {
    schema: string;
    exportedAt: string;
    documents: Doc[];
    approved: Teaching[];
    events: Log[];
    assurance: string;
  };
  restart: { status: "Restarting" };
  "verify-archive": { run: string; status: "Completed" };
  "tool-runs": { runs: Run[] };
}

export function call<K extends keyof Input>(
  op: K,
  token: string,
  data: Input[K],
): Promise<Output[K]>;
export function call<K extends Exclude<keyof Output, keyof Input>>(
  op: K,
  token: string,
): Promise<Output[K]>;
export async function call<K extends keyof Output>(
  op: K,
  token: string,
  data: unknown = {},
): Promise<Output[K]> {
  if (location.origin !== "http://127.0.0.1:8787")
    throw new Error(
      "Open the local console at http://127.0.0.1:8787 to pair this workspace.",
    );
  let response: Response;
  try {
    response = await fetch("http://127.0.0.1:8766/knowledge/" + op, {
      method: "POST",
      cache: "no-store",
      credentials: "omit",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: "Bearer " + token } : {}),
      },
      body: JSON.stringify(data),
    });
  } catch {
    throw new Error(
      "Local repository unavailable. Start the knowledge service and reconnect.",
    );
  }
  const body = (await response.json()) as Output[K] & { error?: string };
  if (!response.ok) throw new Error(body.error || "Local operation failed.");
  return body;
}

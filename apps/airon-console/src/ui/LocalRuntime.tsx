"use client";
import { useEffect, useRef, useState } from "react";
import { call } from "./knowledge-api";

const views = {
  "runtime-activity": "Runtime Activity",
  conversations: "Conversation Explorer",
  "token-usage": "Token Usage",
  "ai-finops": "Spending",
  "ai-agents": "AI Agents",
  "agent-inventory": "Agent Inventory",
  "agent-lineage": "Agent Lineage",
  "evidence-audit": "Execution Evidence",
  verification: "Verification",
};
export const localRoutes = new Set(Object.keys(views));
const agentViews = new Set([
  "ai-agents",
  "agent-inventory",
  "agent-lineage",
  "evidence-audit",
  "verification",
]);
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
type Metrics = {
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
type Run = {
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

export function LocalRuntime({
  slug,
  token,
  role,
  go,
  revision,
}: {
  slug: string;
  token: string;
  role: string;
  go: (slug: string) => void;
  revision: string;
}) {
  const [data, setData] = useState<Metrics>();
  const [runs, setRuns] = useState<Run[]>([]);
  const [error, setError] = useState("");
  const [count, refresh] = useState(0);
  const [busy, setBusy] = useState(false);
  const lock = useRef(false);
  const agent = agentViews.has(slug);
  const allowed = role === "Administrator" || role === "Reviewer";
  const overview = !localRoutes.has(slug);
  const modelUsage = slug === "token-usage" || slug === "ai-finops";
  useEffect(() => {
    let active = true;
    const kind = modelUsage
      ? "model.inference"
      : slug === "conversations"
        ? "workspace.ask"
        : agent
          ? "tool.verify_archive"
          : undefined;
    async function read() {
      const metrics = await call<Metrics>("measurements", token, { kind });
      const result =
        agent && allowed
          ? await call<{ runs: Run[] }>("tool-runs", token)
          : { runs: [] };
      if (active) {
        setData(metrics);
        setRuns(result.runs);
        setError("");
      }
    }
    void read().catch((e) => {
      if (active) setError(e.message);
    });
    return () => {
      active = false;
    };
  }, [token, slug, agent, allowed, modelUsage, count, revision]);
  const details = (route: string) => go(route + "?source=local");
  return (
    <section
      className="card intelligence-card local-operations"
      aria-label="Local Runtime measurements"
    >
      <header>
        <div>
          <small>Local Runtime · {data?.scope || "Paired identity"}</small>
          <h2>
            {overview
              ? "Local execution"
              : agent
                ? "Archive verification runs"
                : slug === "conversations"
                  ? "Workspace requests"
                  : modelUsage
                    ? "Measured model usage"
                    : "Recorded operations"}
          </h2>
        </div>
        <button
          className="btn"
          disabled={busy}
          onClick={() => refresh((n) => n + 1)}
        >
          Refresh measurements
        </button>
      </header>
      {error && <p role="alert">{error}</p>}
      {!data && !error && <p role="status">Reading local measurements…</p>}
      {data && (
        <>
          {!agent && (
            <dl>
              <dt>{modelUsage ? "Model requests" : "Recorded operations"}</dt>
              <dd>
                {modelUsage
                  ? data.summary.modelRequests
                  : data.summary.operations}
              </dd>
              {(modelUsage || overview) && (
                <>
                  <dt>Input / output tokens</dt>
                  <dd>
                    {data.summary.inputTokens ?? "Unreported"} /{" "}
                    {data.summary.outputTokens ?? "Unreported"}
                  </dd>
                  <dt>Mean model request</dt>
                  <dd>
                    {data.summary.modelLatencyMs == null
                      ? "No requests"
                      : data.summary.modelLatencyMs.toFixed(1) + " ms"}
                  </dd>
                  <dt>Calls reporting output tokens</dt>
                  <dd>{data.summary.metered}</dd>
                </>
              )}
              {slug === "ai-finops" && (
                <>
                  <dt>Monetary cost</dt>
                  <dd>
                    Unavailable · no local price or energy tariff configured
                  </dd>
                </>
              )}
            </dl>
          )}
          {overview ? (
            <nav aria-label="Explore local measurements" className="btn-group">
              {Object.entries(views)
                .filter(
                  ([route]) =>
                    !agentViews.has(route) || route === "verification",
                )
                .map(([route, label]) => (
                  <button
                    key={route}
                    className="btn"
                    onClick={() => details(route)}
                  >
                    {label}
                  </button>
                ))}
            </nav>
          ) : agent ? (
            <>
              <p>
                The paired operator authorizes one archive-review agent to run
                the packaged AIP and observer verifiers. Process IDs come from
                the local invocation. The signed inputs describe earlier lab
                captures.
              </p>
              {allowed ? (
                <>
                  <button
                    className="btn primary"
                    disabled={busy}
                    onClick={async () => {
                      if (lock.current) return;
                      lock.current = true;
                      setBusy(true);
                      setError("");
                      try {
                        await call("verify-archive", token);
                        refresh((n) => n + 1);
                      } catch (e) {
                        setError(
                          e instanceof Error
                            ? e.message
                            : "Verification failed.",
                        );
                      } finally {
                        lock.current = false;
                        setBusy(false);
                      }
                    }}
                  >
                    {busy ? "Verifying archives…" : "Run archive verification"}
                  </button>
                  {!runs.length && (
                    <p>No verifier runs recorded in this workspace.</p>
                  )}
                  {runs.map((run) => (
                    <details
                      className="intel-row"
                      key={run.id}
                      open={runs[0].id === run.id}
                    >
                      <summary>
                        {run.agent} · {run.report.verdict}
                      </summary>
                      <dl>
                        <dt>Operator / authorized tool</dt>
                        <dd>
                          {run.actor} · {run.tool}
                        </dd>
                        <dt>Application process relationship</dt>
                        <dd>
                          Knowledge service PID {run.report.parentPid} →
                          verifier PID {run.report.pid}
                        </dd>
                        <dt>Run reference</dt>
                        <dd>
                          <code>{run.id}</code>
                          {new Date(run.at).toLocaleString()}
                        </dd>
                        <dt>AIP archive verdict</dt>
                        <dd>
                          {run.report.verdict} · {run.report.reason}
                        </dd>
                        <dt>Archived authority / receipt</dt>
                        <dd>
                          {run.report.authorization ? "Verified" : "Unverified"}{" "}
                          / {run.report.receipt ? "Verified" : "Unverified"}
                        </dd>
                        <dt>Archive SHA-256</dt>
                        <dd>
                          <code>{run.report.archiveSha256}</code>
                        </dd>
                        <dt>Separate observer archive</dt>
                        <dd>
                          {run.report.archivedEvents} archived events ·{" "}
                          <code>{run.report.observerHead}</code>
                        </dd>
                        <dt>Independent observation of this run</dt>
                        <dd>Unavailable</dd>
                      </dl>
                    </details>
                  ))}
                </>
              ) : (
                <p>Pair a reviewer or administrator to inspect archive runs.</p>
              )}
            </>
          ) : (
            <>
              {!data.rows.length && <p>No matching local activity yet.</p>}
              {data.rows.map((row) => (
                <details className="intel-row" key={row.id}>
                  <summary>
                    {row.operation} · {row.outcome} ·{" "}
                    {row.durationMs.toFixed(1)} ms
                  </summary>
                  <dl>
                    <dt>Identity</dt>
                    <dd>{row.actor}</dd>
                    <dt>Recorded</dt>
                    <dd>{new Date(row.at).toLocaleString()}</dd>
                    {row.model && (
                      <>
                        <dt>Model</dt>
                        <dd>{row.model}</dd>
                      </>
                    )}
                    {row.document && (
                      <>
                        <dt>Source</dt>
                        <dd>Document {row.document}</dd>
                      </>
                    )}
                    {modelUsage && (
                      <>
                        <dt>Input / output tokens</dt>
                        <dd>
                          {row.inputTokens ?? "Unreported"} /{" "}
                          {row.outputTokens ?? "Unreported"}
                        </dd>
                      </>
                    )}
                    <dt>Trace / span</dt>
                    <dd>
                      <code>
                        {row.traceId} / {row.spanId}
                      </code>
                    </dd>
                  </dl>
                </details>
              ))}
              <small>
                Most recent 100 matching records · {data.instrumentation}
              </small>
            </>
          )}
        </>
      )}
    </section>
  );
}

"use client";
import { useEffect, useState, type FormEvent, type ReactNode } from "react";
import { Field, I } from "./primitives";
import "./intelligence.css";

type Doc = {
  id: number;
  title: string;
  body: string;
  hash: string;
  actor: string;
  origin: string;
  at: string;
};
type Teaching = {
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
type State = {
  actor: string;
  role: string;
  documents: Doc[];
  teachings: Teaching[];
  memory: Teaching[];
  events: Log[];
  asOf: string;
};
type Info = { demo: boolean; people: Record<string, string>; model: string };
type Answer = {
  outcome: string;
  answer: string;
  engine: string;
  citation?: {
    document: number;
    title: string;
    version: number;
    sha256: string;
    teaching: number | null;
  };
};
type Runtime = {
  models: string[];
  configured: string;
  status: string;
  at: string;
  databaseBytes: number;
  cpuSeconds: number;
};

async function call<T>(
  op: string,
  token: string,
  data: unknown = {},
): Promise<T> {
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
  const body = (await response.json()) as T & { error?: string };
  if (!response.ok) throw new Error(body.error || "Local operation failed.");
  return body;
}
const question1 = "When should we inspect the cooling assembly?";
const question2 = "Which register records the cooling assembly handover?";
const when = (at: string) => new Date(at).toLocaleString();
function Panel({
  title,
  icon,
  children,
}: {
  title: string;
  icon: string;
  children: ReactNode;
}) {
  return (
    <section className="card intelligence-card">
      <h2>
        <I n={icon} />
        {title}
      </h2>
      {children}
    </section>
  );
}
function KnowledgeLineage({
  documents,
  memory,
}: {
  documents: Doc[];
  memory: Teaching[];
}) {
  const [selectedId, select] = useState<number>();
  const source =
    documents.find((entry) => entry.id === selectedId) ??
    documents.find((entry) =>
      memory.some((version) => version.doc === entry.id),
    ) ??
    documents[0];
  const versions = memory.filter((version) => version.doc === source?.id);
  const reuse = versions.reduce((count, version) => count + version.reuse, 0);
  return (
    <Panel title="Knowledge lineage" icon="lineage">
      {source ? (
        <>
          <Field label="Trace a source document">
            <select
              value={source.id}
              onChange={(event) => select(Number(event.target.value))}
            >
              {documents.map((entry) => (
                <option key={entry.id} value={entry.id}>
                  {entry.title}
                </option>
              ))}
            </select>
          </Field>
          <ol
            className="knowledge-lineage"
            aria-label="Selected source lineage"
            aria-live="polite"
          >
            <li>
              <I n="file" />
              <span>Imported by</span>
              <strong>{source.actor}</strong>
            </li>
            <li>
              <I n="bookmarked" />
              <span>Approved versions</span>
              <strong>{versions.length}</strong>
            </li>
            <li>
              <I n="message" />
              <span>Answers using those versions</span>
              <strong>{reuse}</strong>
            </li>
          </ol>
        </>
      ) : (
        <p>
          Import a document in Knowledge Vault to trace its approved versions
          and reuse.
        </p>
      )}
    </Panel>
  );
}

function exportJson(data: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(data, null, 2)], { type: "application/json" }),
  );
  const link = document.createElement("a");
  link.href = url;
  link.download = "airon-approved-knowledge.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
export default function Intelligence({
  slug,
  go,
}: {
  slug: string;
  go: (path: string) => void;
}) {
  const [info, infoSet] = useState<Info>(),
    [state, setState] = useState<State>(),
    [token, setToken] = useState("");
  const [error, fail] = useState(""),
    [busy, working] = useState(false),
    [notice, say] = useState(""),
    [generation, retry] = useState(0);
  const [person, personSet] = useState("Mira"),
    [secret, secretSet] = useState("");
  const [title, titleSet] = useState(""),
    [body, bodySet] = useState(""),
    [sourceQuestion, sqSet] = useState("");
  const [query, querySet] = useState(""),
    [matches, setMatches] = useState<number[] | null>(null);
  const [question, setQuestion] = useState(""),
    [engine, engineSet] = useState("extract"),
    [answer, setAnswer] = useState<Answer>();
  const [correction, setCorrection] = useState(""),
    [note, setNote] = useState(""),
    [doc, docSet] = useState("");
  const [runtime, setRuntime] = useState<Runtime>();
  useEffect(() => {
    let active = true;
    (async () => {
      const metadata = await call<Info>("info", "");
      if (!active) return;
      infoSet(metadata);
      const saved = sessionStorage.getItem("airon-local-pairing");
      if (saved) {
        const snapshot = await call<State>("state", saved);
        if (active) {
          setToken(saved);
          setState(snapshot);
        }
      }
    })().catch((e) => {
      if (active) fail(e.message);
    });
    return () => {
      active = false;
    };
  }, [generation]);
  async function action(work: () => Promise<void>) {
    working(true);
    fail("");
    say("");
    try {
      await work();
    } catch (e) {
      fail(e instanceof Error ? e.message : "Operation failed.");
    } finally {
      working(false);
    }
  }
  function submit(e: FormEvent, work: () => Promise<void>) {
    e.preventDefault();
    void action(work);
  }
  async function pair() {
    const key = info?.demo
      ? (await call<{ token: string }>("pair", "", { actor: person })).token
      : secret;
    const current = await call<State>("state", key);
    sessionStorage.setItem("airon-local-pairing", key);
    setToken(key);
    setState(current);
    secretSet("");
  }
  async function change(op: string, data: unknown, message: string) {
    await call(op, token, data);
    setState(await call<State>("state", token));
    setMatches(null);
    say(message);
  }
  function disconnect() {
    sessionStorage.removeItem("airon-local-pairing");
    setToken("");
    setState(undefined);
    setAnswer(undefined);
    setRuntime(undefined);
    setMatches(null);
    setQuestion("");
    setCorrection("");
    setNote("");
    titleSet("");
    bodySet("");
    sqSet("");
    docSet("");
    fail("");
    say("");
  }
  const documents = state?.documents ?? [],
    memory = state?.memory ?? [],
    proposed = state?.teachings ?? [];
  const admin = state?.role === "Administrator",
    pending = proposed.filter((t) => t.status === "Pending");
  return (
    <div className="intelligence">
      <div className="intel-strip">
        <span>
          <I n="database" size={14} />
          {info ? "Local knowledge workspace" : "Local knowledge service"}
        </span>
        {state && (
          <>
            <span>
              {state.actor} · {state.role}
            </span>
            <button className="text-btn" disabled={busy} onClick={disconnect}>
              Switch identity
            </button>
          </>
        )}
      </div>
      {error && (
        <p className="intel-error" role="alert">
          {error}{" "}
          <button
            className="text-btn"
            onClick={() => {
              fail("");
              retry(generation + 1);
            }}
          >
            Reconnect
          </button>
        </p>
      )}
      {notice && (
        <p className="intel-notice" role="status">
          {notice}
        </p>
      )}
      {!state ? (
        <Panel title="Open your local workspace" icon="key">
          {!info ? (
            <p>
              {error
                ? "The knowledge service is disconnected."
                : "Connecting to the local knowledge service…"}
            </p>
          ) : (
            <form onSubmit={(e) => submit(e, pair)}>
              {info.demo ? (
                <Field label="Sample workspace profile">
                  <select
                    value={person}
                    onChange={(e) => personSet(e.target.value)}
                  >
                    {Object.entries(info.people).map(([name, role]) => (
                      <option key={name} value={name}>
                        {name} · {role}
                      </option>
                    ))}
                  </select>
                </Field>
              ) : (
                <Field label="Local pairing key">
                  <input
                    type="password"
                    autoComplete="off"
                    required
                    value={secret}
                    onChange={(e) => secretSet(e.target.value)}
                  />
                </Field>
              )}
              <button className="btn primary" disabled={busy}>
                Open workspace
              </button>
            </form>
          )}
        </Panel>
      ) : (
        <>
          {slug === "intelligence-overview" && (
            <>
              <div className="intel-kpis">
                {[
                  [
                    "Source documents",
                    documents.length,
                    "database",
                    "knowledge-vault",
                  ],
                  [
                    "Approved versions",
                    memory.length,
                    "bookmarked",
                    "institutional-memory",
                  ],
                  ["Awaiting review", pending.length, "guide", "expert-teach"],
                ].map(([label, count, icon, route]) => (
                  <button
                    key={label}
                    className="card"
                    onClick={() => go(String(route))}
                  >
                    <I n={String(icon)} />
                    <span>{label}</span>
                    <strong>{count}</strong>
                  </button>
                ))}
              </div>
              <KnowledgeLineage documents={documents} memory={memory} />
              <div className="intel-grid">
                <Panel title="Ownership boundary" icon="globelock">
                  <dl>
                    <dt>Repository</dt>
                    <dd>Local SQLite · single organization</dd>
                    <dt>Workspace</dt>
                    <dd>
                      {info?.demo
                        ? "Maintenance workspace · sample profiles"
                        : "Operator-controlled directory"}
                    </dd>
                    <dt>Model deployment</dt>
                    <dd>{info?.model || "No model configured"}</dd>
                    <dt>Snapshot</dt>
                    <dd>{when(state.asOf)}</dd>
                  </dl>
                </Panel>
                <Panel title="Knowledge activity" icon="activity">
                  {state.events.length ? (
                    state.events.slice(0, 5).map((e) => (
                      <div className="intel-row" key={e.id}>
                        <strong>{e.action}</strong>
                        <small>
                          {e.actor} · {when(e.at)}
                        </small>
                      </div>
                    ))
                  ) : (
                    <p>Import the first source to start the activity record.</p>
                  )}
                </Panel>
              </div>
            </>
          )}
          {slug === "knowledge-vault" && (
            <div className="intel-grid">
              <Panel title="Source documents" icon="database">
                <form
                  onSubmit={(e) =>
                    submit(e, async () => {
                      setMatches(
                        query.trim()
                          ? (
                              await call<{ documents: { id: number }[] }>(
                                "search",
                                token,
                                { query },
                              )
                            ).documents.map((d) => d.id)
                          : null,
                      );
                    })
                  }
                >
                  <Field label="Search vault">
                    <input
                      value={query}
                      onChange={(e) => {
                        querySet(e.target.value);
                        if (!e.target.value) setMatches(null);
                      }}
                    />
                  </Field>
                  <button className="btn" disabled={busy}>
                    Search documents
                  </button>
                </form>
                {documents
                  .filter((d) => matches === null || matches.includes(d.id))
                  .map((d) => (
                    <details className="intel-row" key={d.id}>
                      <summary>{d.title}</summary>
                      <p>{d.body}</p>
                      <small>
                        {d.origin} · {d.actor} · {when(d.at)}
                      </small>
                      <code>{d.hash}</code>
                      {admin && (
                        <button
                          className="btn"
                          disabled={busy}
                          onClick={() =>
                            void action(async () => {
                              const data = await call("export", token);
                              exportJson(data);
                              say("Vault and approved procedures exported.");
                            })
                          }
                        >
                          Export workspace with sources
                        </button>
                      )}
                    </details>
                  ))}
                {(!documents.length || matches?.length === 0) && (
                  <p>
                    {documents.length
                      ? "No matching sources."
                      : "The vault is empty."}
                  </p>
                )}
              </Panel>
              <Panel title="Import a source" icon="file">
                {admin ? (
                  <>
                    <button
                      className="btn"
                      disabled={busy}
                      onClick={() =>
                        void action(() =>
                          change(
                            "import-sample",
                            {},
                            "Maintenance document imported.",
                          ),
                        )
                      }
                    >
                      Import sample maintenance document
                    </button>
                    <form
                      onSubmit={(e) =>
                        submit(e, async () => {
                          await change(
                            "import",
                            { title, body, question: sourceQuestion },
                            "Document stored locally.",
                          );
                          titleSet("");
                          bodySet("");
                          sqSet("");
                        })
                      }
                    >
                      <Field label="Text or Markdown file">
                        <input
                          type="file"
                          accept=".txt,.md,text/plain,text/markdown"
                          onChange={(e) => {
                            const f = e.target.files?.[0];
                            if (f)
                              void action(async () => {
                                if (f.size > 32000)
                                  throw Error(
                                    "Choose a text file under 32 KB.",
                                  );
                                bodySet(await f.text());
                                titleSet(f.name);
                              });
                          }}
                        />
                      </Field>
                      <Field label="Document title">
                        <input
                          required
                          value={title}
                          maxLength={160}
                          onChange={(e) => titleSet(e.target.value)}
                        />
                      </Field>
                      <Field label="Source text">
                        <textarea
                          required
                          value={body}
                          maxLength={32000}
                          onChange={(e) => bodySet(e.target.value)}
                        />
                      </Field>
                      <Field label="Question supported by this excerpt">
                        <input
                          required
                          value={sourceQuestion}
                          maxLength={500}
                          onChange={(e) => sqSet(e.target.value)}
                        />
                      </Field>
                      <button disabled={busy} className="btn primary">
                        Save document
                      </button>
                    </form>
                  </>
                ) : (
                  <p>An administrator can import source documents.</p>
                )}
              </Panel>
            </div>
          )}
          {slug === "private-ai-workspace" && (
            <div className="intel-grid">
              <Panel title="Ask the maintenance workspace" icon="message">
                <form
                  onSubmit={(e) =>
                    submit(e, async () => {
                      setAnswer(undefined);
                      setAnswer(
                        await call<Answer>("ask", token, { question, engine }),
                      );
                    })
                  }
                >
                  <Field label="Answer engine">
                    <select
                      value={engine}
                      onChange={(e) => engineSet(e.target.value)}
                    >
                      <option value="extract">
                        Deterministic source excerpt
                      </option>
                      <option value="ollama">
                        Local Ollama · {info?.model || "unconfigured"}
                      </option>
                    </select>
                  </Field>
                  <Field label="Technical question">
                    <textarea
                      required
                      value={question}
                      maxLength={500}
                      onChange={(e) => setQuestion(e.target.value)}
                    />
                  </Field>
                  {info?.demo && (
                    <div className="btn-group">
                      {[
                        ["Inspection interval", question1],
                        ["Handover register", question2],
                      ].map(([label, q]) => (
                        <button
                          type="button"
                          key={label}
                          className="btn"
                          onClick={() => setQuestion(q)}
                        >
                          {label}
                        </button>
                      ))}
                    </div>
                  )}
                  <button className="btn primary" disabled={busy}>
                    Ask workspace
                  </button>
                </form>
              </Panel>
              <Panel
                title={answer?.outcome || "Answer and citation"}
                icon="book"
              >
                {answer ? (
                  <div aria-live="polite">
                    <p>{answer.answer}</p>
                    <small>{answer.engine}</small>
                    {answer.citation && (
                      <dl>
                        <dt>Source</dt>
                        <dd>
                          {answer.citation.title} · document{" "}
                          {answer.citation.document}
                        </dd>
                        <dt>
                          {answer.citation.teaching
                            ? "Approved procedure"
                            : "Document version"}
                        </dt>
                        <dd>v{answer.citation.version}</dd>
                        <dt>Source SHA-256</dt>
                        <dd>
                          <code>{answer.citation.sha256}</code>
                        </dd>
                      </dl>
                    )}
                  </div>
                ) : (
                  <p>
                    Ask a supported question to see the excerpt and its original
                    document.
                  </p>
                )}
              </Panel>
            </div>
          )}
          {slug === "expert-teach" && (
            <div className="intel-grid">
              <Panel title="Document a correction" icon="guide">
                {state.role === "Expert" ? (
                  <form
                    onSubmit={(e) =>
                      submit(e, async () => {
                        await change(
                          "propose",
                          {
                            question,
                            answer: correction,
                            note,
                            document: Number(doc),
                          },
                          "Submitted for independent review.",
                        );
                        setCorrection("");
                        setNote("");
                      })
                    }
                  >
                    <Field label="Supported question">
                      <input
                        required
                        value={question}
                        onChange={(e) => setQuestion(e.target.value)}
                        maxLength={500}
                      />
                    </Field>
                    <Field label="Proposed procedure">
                      <textarea
                        required
                        value={correction}
                        onChange={(e) => setCorrection(e.target.value)}
                        maxLength={3000}
                      />
                    </Field>
                    <Field label="Related vault document">
                      <select
                        required
                        value={doc}
                        onChange={(e) => docSet(e.target.value)}
                      >
                        <option value="">Select document</option>
                        {documents.map((d) => (
                          <option key={d.id} value={d.id}>
                            {d.title}
                          </option>
                        ))}
                      </select>
                    </Field>
                    <Field label="Supporting evidence or reference">
                      <textarea
                        required
                        value={note}
                        maxLength={2000}
                        onChange={(e) => setNote(e.target.value)}
                      />
                    </Field>
                    <button className="btn primary" disabled={busy}>
                      Submit for review
                    </button>
                  </form>
                ) : (
                  <p>
                    Pair the expert identity to propose a procedure and attach
                    its supporting evidence.
                  </p>
                )}
              </Panel>
              <Panel title="Review queue" icon="clipboard">
                {pending.length ? (
                  pending.map((t) => (
                    <div className="intel-row" key={t.id}>
                      <strong>{t.question}</strong>
                      <p>{t.answer}</p>
                      <small>
                        {t.actor} · {t.source}
                      </small>
                      <p>{t.note}</p>
                      {state.role === "Reviewer" && (
                        <div className="btn-group">
                          {["Approved", "Rejected"].map((decision, i) => (
                            <button
                              className={i ? "btn" : "btn primary"}
                              disabled={busy}
                              key={decision}
                              onClick={() =>
                                void action(() =>
                                  change(
                                    "review",
                                    { teaching: t.id, decision },
                                    i
                                      ? "Correction rejected."
                                      : "Approved procedure activated.",
                                  ),
                                )
                              }
                            >
                              {i ? "Reject" : "Approve and activate"}
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <p>No pending corrections visible to this identity.</p>
                )}
              </Panel>
            </div>
          )}
          {slug === "institutional-memory" && (
            <Panel title="Approved procedure history" icon="bookmarked">
              {memory.length ? (
                memory.map((t) => (
                  <details className="intel-row" key={t.id} open>
                    <summary>
                      {t.question} · v{t.version}
                    </summary>
                    <p>{t.answer}</p>
                    <small>
                      {t.actor} · approved by {t.reviewer} · {when(t.reviewed)}{" "}
                      · {t.reuse} reuse(s)
                    </small>
                    <p>{t.note}</p>
                    <code>
                      {t.source} · {t.source_hash}
                    </code>
                  </details>
                ))
              ) : (
                <p>Approved procedures appear here after review.</p>
              )}
              {admin && (
                <button
                  className="btn primary"
                  disabled={busy}
                  onClick={() =>
                    void action(async () => {
                      exportJson(await call("export", token));
                      say("Knowledge export prepared.");
                    })
                  }
                >
                  Export approved knowledge
                </button>
              )}
            </Panel>
          )}
          {slug === "sovereign-runtime" && (
            <div className="intel-grid">
              <Panel title="Local runtime" icon="cpu">
                <dl>
                  <dt>Answer engine</dt>
                  <dd>Deterministic extraction · available</dd>
                  <dt>Ollama model</dt>
                  <dd>{info?.model || "Unconfigured"}</dd>
                  <dt>Model endpoint</dt>
                  <dd>127.0.0.1:11434</dd>
                  <dt>Configuration</dt>
                  <dd>
                    Launch the service with <code>--model MODEL_TAG</code> to
                    select an installed model.
                  </dd>
                </dl>
                <button
                  className="btn primary"
                  disabled={busy}
                  onClick={() =>
                    void action(async () =>
                      setRuntime(await call<Runtime>("runtime", token)),
                    )
                  }
                >
                  Probe local runtime
                </button>
              </Panel>
              <Panel title="Runtime measurements" icon="server">
                {runtime ? (
                  <dl>
                    <dt>Model status</dt>
                    <dd>{runtime.status}</dd>
                    <dt>SQLite allocated size</dt>
                    <dd>{runtime.databaseBytes.toLocaleString()} bytes</dd>
                    <dt>Knowledge service CPU time</dt>
                    <dd>
                      {runtime.cpuSeconds.toFixed(3)} seconds since process
                      start
                    </dd>
                    <dt>Checked</dt>
                    <dd>{when(runtime.at)}</dd>
                  </dl>
                ) : (
                  <p>
                    Run a local probe to measure storage and check model
                    availability.
                  </p>
                )}
                <p>
                  Inference is configured for loopback. Network isolation and
                  model licensing require separate evaluation.
                </p>
              </Panel>
            </div>
          )}
          {slug === "trust-evidence" && (
            <div className="intel-grid">
              <Panel title="Knowledge audit trail" icon="history">
                {state.events.length ? (
                  state.events.map((e) => (
                    <details key={e.id} className="intel-row">
                      <summary>
                        {e.action} · {e.actor}
                      </summary>
                      <small>
                        {when(e.at)} · event {e.id}
                      </small>
                      <code>{e.detail}</code>
                    </details>
                  ))
                ) : (
                  <p>No recorded activity for this identity.</p>
                )}
              </Panel>
              <Panel title="Evidence scope" icon="signed">
                <p>
                  Knowledge events are unsigned local application records. The
                  separate AIP verifier can replay the packaged execution
                  evidence.
                </p>
                <button className="btn" onClick={() => go("verification")}>
                  Open AIP verification
                </button>
              </Panel>
            </div>
          )}
        </>
      )}
    </div>
  );
}

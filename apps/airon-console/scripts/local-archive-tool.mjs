// One fixed tool with no user-supplied paths, commands or network transports.
import { readFile } from "node:fs/promises";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";

const base = new URL("../public/upstream-replay/", import.meta.url);
let receive, outcome;
globalThis.self = {
  location: { href: new URL("worker.mjs", base).href },
  addEventListener(_name, handler) { receive = handler; },
  postMessage(value) { outcome = value; },
};
globalThis.fetch = async (url) => {
  const file = new URL(url);
  if (!file.href.startsWith(base.href)) throw Error("Archive asset out of scope");
  return new Response(await readFile(fileURLToPath(file)));
};
await import(new URL("worker.mjs", base));
async function check(sample) {
  await receive({ data: { sample, check: "original" } });
  if (!outcome?.ok || !outcome.result.accepted) throw Error("Archive rejected");
  return outcome.result;
}
const authority = await check("same-run");
const observer = await check("t09");
const evidence = await readFile(new URL("fixtures/same-run-bundle.json.gz",base));
console.log(JSON.stringify({
  pid: process.pid, parentPid: process.ppid,
  archiveSha256: createHash("sha256").update(evidence).digest("hex"),
  verdict: authority.verdict, reason: authority.reason, archive: authority.archiveIntegrityVerified,
  authorization: authority.authorizationVerified, receipt: authority.gatewayReceiptVerified,
  observerHead: observer.scope.finalHead, archivedEvents: observer.events.length,
}));

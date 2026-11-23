import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { fileURLToPath } from "node:url";
const root = fileURLToPath(new URL("../", import.meta.url));
if (!existsSync(new URL("../dist/server/wrangler.json", import.meta.url))) {
  console.error("Run npm run build and npm run db:local before starting.");
  process.exit(1);
}
const children = [];
let stopping = false;
function stop(code) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill("SIGTERM");
  process.exitCode = code;
}
function launch(command, args) {
  const child = spawn(command, args, { cwd: root, stdio: "inherit" });
  children.push(child);
  child.on("error", (err) => {
    console.error(err.message);
    stop(1);
  });
  child.on("exit", (code) => stop(code ?? 1));
}
launch(process.env.PYTHON || "python3", [
  "intelligence/local_api.py",
  ...process.argv.slice(2),
]);
launch(process.execPath, [
  "--import",
  "./scripts/sites-env.mjs",
  "./node_modules/wrangler/bin/wrangler.js",
  "dev",
  "--config",
  "dist/server/wrangler.json",
  "--local",
  "--persist-to",
  ".wrangler/state",
  "--ip",
  "127.0.0.1",
  "--port",
  "8787",
  "--inspector-port",
  "0",
]);
process.on("SIGINT", () => stop(0));
process.on("SIGTERM", () => stop(0));

import { existsSync } from "node:fs";
import { spawn } from "node:child_process";
import { fileURLToPath } from "node:url";
const root = fileURLToPath(new URL("../", import.meta.url));
const python =
  existsSync(root+".venv/bin/python") ? root+".venv/bin/python" : process.env.PYTHON || process.env.CODEX_PRIMARY_RUNTIME_PYTHON || "python3";
const args = process.argv.slice(2);
const portAt = args.indexOf("--port");
const port = portAt >= 0 ? args[portAt + 1] : process.env.PORT || "5173";
const processes = [
  spawn(
    python,
    ["-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8000"],
    { cwd: root, stdio: "inherit" },
  ),
  spawn(
    "npm",
    [
      "--prefix",
      "frontend",
      "run",
      "dev",
      "--",
      "--port",
      port,
      "--strictPort",
    ],
    { cwd: root, stdio: "inherit" },
  ),
];
let stopping = false;
function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  processes.forEach((child) => child.kill("SIGTERM"));
  setTimeout(() => {
    processes.forEach((child) => child.kill("SIGKILL"));
    process.exit(code);
  }, 500).unref();
}
processes.forEach((child) => {
  child.on("error", (error) => {
    console.error(error.message);
    stop(1);
  });
  child.on("exit", (code) => {
    if (!stopping) stop(code || 0);
  });
});
process.on("SIGINT", () => stop());
process.on("SIGTERM", () => stop());

// the-picture-that-tastes-of-one-20261122-2047 — "The picture that tastes
// of one ingredient": one steaming bowl of ramen, drawn in code.
// Entry program (Node 22, stdlib only). It runs compose.py (PIL, no
// network, deterministic) to render entry.png, and falls back to the
// committed entry.png if Python/PIL is unavailable in the sandbox, so
// the program still produces the identical image. All paths resolve from
// this script's own directory, never from the working directory.
import { spawnSync } from "node:child_process";
import { copyFileSync, existsSync, mkdirSync, readFileSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR || "/output";
const dst = join(outDir, "entry.png");
const src = join(here, "entry.png");

mkdirSync(outDir, { recursive: true });

const sha = (buf: Buffer) => createHash("sha256").update(buf).digest("hex");

// Primary path: render fresh from compose.py (deterministic, no network).
const run = spawnSync("python3", [join(here, "compose.py")], {
  env: { ...process.env, OUT: dst, PYTHONHASHSEED: "0" },
  encoding: "utf8",
});
if (run.status === 0 && existsSync(dst)) {
  const b = readFileSync(dst);
  console.log(`rendered ${dst} (${b.length} bytes, sha256=${sha(b)})`);
  process.exit(0);
}

// Fallback: copy the committed render, byte for byte.
console.error(
  `compose.py render failed (status=${run.status}): ` +
    `${(run.stderr || "").trim().slice(0, 300)} — copying committed entry.png`,
);
if (!existsSync(src)) {
  throw new Error("no rendered entry.png and no committed entry.png to fall back to");
}
copyFileSync(src, dst);
const b = readFileSync(dst);
console.log(`copied ${dst} (${b.length} bytes, sha256=${sha(b)})`);

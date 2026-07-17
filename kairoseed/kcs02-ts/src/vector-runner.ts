import { readFile, writeFile } from "node:fs/promises";
import { evaluateVector, PROFILE } from "./engine.js";

type Fixture = { profile?: unknown; vectors?: unknown };

function argument(name: string): string {
  const index = process.argv.indexOf(name);
  const value = process.argv[index + 1];
  if (index < 0 || value === undefined) {
    throw new Error(`missing required argument: ${name}`);
  }
  return value;
}

async function main(): Promise<void> {
  const vectorPath = argument("--vectors");
  const outputPath = argument("--output");
  const fixture = JSON.parse(await readFile(vectorPath, "utf8")) as Fixture;

  if (fixture.profile !== PROFILE || !Array.isArray(fixture.vectors)) {
    throw new Error("invalid KCS-0.2 fixture envelope");
  }

  const results = fixture.vectors.map((vector) => evaluateVector(vector as Record<string, unknown>));
  await writeFile(outputPath, `${JSON.stringify({ profile: PROFILE, results })}\n`, {
    encoding: "utf8",
    mode: 0o600,
  });
}

main().catch((error: unknown) => {
  const message = error instanceof Error ? error.message : "unknown runner error";
  console.error(`BLOCK runner: ${message}`);
  process.exitCode = 1;
});

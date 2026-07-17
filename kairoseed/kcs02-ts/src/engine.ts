import { createHash } from "node:crypto";

export const PROFILE = "KCS-0.2";
const MIN_SAFE_INTEGER = Number.MIN_SAFE_INTEGER;
const MAX_SAFE_INTEGER = Number.MAX_SAFE_INTEGER;
const BASE64URL_RE = /^[A-Za-z0-9_-]+$/;

type JsonValue = null | boolean | number | string | JsonValue[] | { [key: string]: JsonValue };
type Vector = { id?: unknown; input?: unknown; checks?: unknown };
type VectorResult =
  | { id: string; status: "PASS"; canonical_utf8_hex: string; sha256: string }
  | { id: string; status: "BLOCK"; reason_code: string };

export class KCS02Block extends Error {
  readonly reasonCode: string;

  constructor(reasonCode: string) {
    super(reasonCode);
    this.name = "KCS02Block";
    this.reasonCode = reasonCode;
  }
}

function rejectSurrogates(value: string): void {
  for (let index = 0; index < value.length; index += 1) {
    const unit = value.charCodeAt(index);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xdc00 && next <= 0xdfff)) {
        throw new KCS02Block("INVALID_UNICODE");
      }
      index += 1;
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      throw new KCS02Block("INVALID_UNICODE");
    }
  }
}

function normalizeValue(value: unknown): JsonValue {
  if (value === null || typeof value === "boolean") {
    return value;
  }

  if (typeof value === "number") {
    if (!Number.isInteger(value)) {
      throw new KCS02Block("UNSUPPORTED_NUMBER");
    }
    if (value < MIN_SAFE_INTEGER || value > MAX_SAFE_INTEGER) {
      throw new KCS02Block("UNSAFE_INTEGER");
    }
    return value;
  }

  if (typeof value === "string") {
    rejectSurrogates(value);
    return value.normalize("NFC");
  }

  if (Array.isArray(value)) {
    return value.map((item) => normalizeValue(item));
  }

  if (typeof value === "object") {
    const source = value as Record<string, unknown>;
    const normalized = Object.create(null) as Record<string, JsonValue>;
    const observed = new Set<string>();
    for (const key of Object.keys(source)) {
      rejectSurrogates(key);
      const normalizedKey = key.normalize("NFC");
      if (observed.has(normalizedKey)) {
        throw new KCS02Block("NORMALIZED_KEY_COLLISION");
      }
      observed.add(normalizedKey);
      normalized[normalizedKey] = normalizeValue(source[key]);
    }
    return normalized;
  }

  throw new KCS02Block("UNSUPPORTED_TYPE");
}

function render(value: JsonValue): string {
  if (value === null) return "null";
  if (value === true) return "true";
  if (value === false) return "false";
  if (typeof value === "number") return String(value);
  if (typeof value === "string") return JSON.stringify(value);
  if (Array.isArray(value)) return `[${value.map((item) => render(item)).join(",")}]`;

  const keys = Object.keys(value).sort();
  return `{${keys.map((key) => `${JSON.stringify(key)}:${render(value[key]!)}`).join(",")}}`;
}

export function canonicalize(value: unknown): Buffer {
  return Buffer.from(render(normalizeValue(value)), "utf8");
}

function digest(value: Buffer): string {
  return createHash("sha256").update(value).digest("hex");
}

function validateBase64url(value: unknown): void {
  if (typeof value !== "string" || value.length === 0 || !BASE64URL_RE.test(value)) {
    throw new KCS02Block("INVALID_SIGNATURE_ENCODING");
  }
  const decoded = Buffer.from(value, "base64url");
  if (decoded.toString("base64url") !== value) {
    throw new KCS02Block("INVALID_SIGNATURE_ENCODING");
  }
}

function parseTimestamp(value: unknown): number {
  if (typeof value !== "string" || !value.endsWith("Z")) {
    throw new KCS02Block("INVALID_TIMESTAMP");
  }
  const parsed = Date.parse(value);
  if (!Number.isFinite(parsed)) {
    throw new KCS02Block("INVALID_TIMESTAMP");
  }
  return parsed;
}

function asRecord(value: unknown): Record<string, unknown> {
  if (value === null || typeof value !== "object" || Array.isArray(value)) {
    throw new KCS02Block("INVALID_VECTOR");
  }
  return value as Record<string, unknown>;
}

function applyChecks(vector: Vector, canonicalBytes: Buffer): void {
  const checks = vector.checks === undefined ? {} : asRecord(vector.checks);
  const payload = asRecord(vector.input);

  const signatureField = checks.signature_base64url_field;
  if (signatureField !== undefined) {
    if (typeof signatureField !== "string") throw new KCS02Block("INVALID_VECTOR");
    validateBase64url(payload[signatureField]);
  }

  const expectedHash = checks.expected_signed_content_sha256;
  if (expectedHash !== undefined && digest(canonicalBytes) !== expectedHash) {
    throw new KCS02Block("SIGNED_CONTENT_MISMATCH");
  }

  if (checks.expires_at !== undefined) {
    if (typeof checks.expires_at !== "string") throw new KCS02Block("INVALID_VECTOR");
    const expiresAt = parseTimestamp(payload[checks.expires_at]);
    const now = parseTimestamp(checks.now);
    if (now >= expiresAt) throw new KCS02Block("EXPIRED");
  }

  if (checks.nonce_reused === true) throw new KCS02Block("NONCE_REUSED");

  if (
    checks.required_audience !== undefined &&
    payload.authorization_audience !== checks.required_audience
  ) {
    throw new KCS02Block("WRONG_AUDIENCE");
  }

  if (checks.require_govana_pass === true && payload.govana_decision !== "PASS") {
    if (payload.gat !== null && payload.gat !== undefined) {
      throw new KCS02Block("GOVANA_BLOCK_HAS_GAT");
    }
    throw new KCS02Block("GOVANA_BLOCK");
  }
}

export function evaluateVector(vector: Vector): VectorResult {
  if (typeof vector.id !== "string" || vector.id.length === 0) {
    throw new KCS02Block("INVALID_VECTOR");
  }

  try {
    const canonicalBytes = canonicalize(vector.input);
    applyChecks(vector, canonicalBytes);
    return {
      id: vector.id,
      status: "PASS",
      canonical_utf8_hex: canonicalBytes.toString("hex"),
      sha256: digest(canonicalBytes),
    };
  } catch (error) {
    if (error instanceof KCS02Block) {
      return { id: vector.id, status: "BLOCK", reason_code: error.reasonCode };
    }
    throw error;
  }
}

# KAIROSEED Glossary

This glossary introduces plain-language meanings before specialized terminology.

## Artificial intelligence (AI)

Computer systems that perform tasks commonly associated with human intelligence, such as learning from examples, recognizing patterns, reasoning, generating language, and making recommendations.

AI output can be useful without being automatically correct, authorized, or safe to execute.

## Agent

An AI-enabled system that can pursue a task, select tools, or take actions rather than only produce text.

## Jargon

Specialized vocabulary, acronyms, and terminology used by a profession, trade, or group.

Use technical terminology with peers when it improves speed and accuracy. For clients and general readers, explain the plain-language meaning first.

## Constrained decoding

A generation method that restricts which tokens a model may emit so the resulting output follows a defined grammar or schema.

It can guarantee structural form when correctly supported by the model runtime. It does not guarantee that the values are true, safe, or authorized.

## Schema

A formal description of the required shape and types of data, such as an exact JSON Schema or a typed Python model.

## Deterministic code

Software designed to produce the same result from the same valid inputs under the same defined conditions.

KAIROSEED assigns correctness-critical calculations, cryptographic checks, policy rules, and state transitions to deterministic code rather than free-form model text.

## Governance

The policies, authority, evidence, controls, and review processes that determine whether a proposed action is allowed.

## Policy Decision Point (PDP)

The component that evaluates a request against policy and returns a decision such as `PASS`, `WARN`, or `BLOCK`.

A policy decision does not execute the requested action.

## Policy Enforcement Point (PEP)

The independent gate that checks authorization evidence and denies execution by default when evidence is missing, invalid, expired, or out of scope.

## Verified Experiment Packet (VEP)

A structured request containing the declared purpose, requested tool, evidence references, resource limits, rollback plan, and authorization scope needed for governance evaluation.

## Authorization evidence

A bounded record showing that a specific request was permitted under defined conditions.

A hash is not automatically a cryptographic signature, and a policy result is not automatically executable authority.

## Replay protection

A control that prevents previously accepted authorization evidence from being reused to trigger the same or another action again.

## Canonical serialization

A rule that converts structured data into one unambiguous byte representation before hashing or signing.

## Fail closed

Deny or stop when required evidence, validation, policy, audit, or system state cannot be established.

## Audit trail

A record of requests, decisions, authorization events, execution outcomes, and failures used for accountability and investigation.

## Chronos

In the KAIROSEED conceptual framework, Chronos represents structured, measurable responsibility. Its technical analogue is the shaping and validation of data.

## Discernment

In the KAIROSEED conceptual framework, discernment represents examination, prioritization, and responsible judgment. Its technical analogue is bounded deterministic validation and computation.

Software does not possess spiritual or moral discernment in the human or theological sense.

## Kairos

In the KAIROSEED conceptual framework, Kairos concerns the appointed opening for faithful action. Its technical analogue is a permitted execution window established through explicit governance and authorization.

Software does not detect or command divine timing.

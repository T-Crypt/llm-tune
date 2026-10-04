---
name: llm-tune
description: Use when the user wants to tune a local LLM setup (llama.cpp / llama-swap or similar) — engine flags, quant, KV cache, context, sampling, harness settings — for their hardware, especially when quality at depth or agent behaviour matters, not just tok/s.
---

# llm-tune

TODO: one-paragraph overview of the tuning philosophy (quality-aware, evidence-backed).

## Intake

TODO: what to ask the user — GPU model and VRAM, RAM, model + quant file, context needed, workload (chat vs agent vs RAG), quality vs speed priority, engine and version.

## Decision procedure

TODO: the step-by-step procedure that turns intake answers into recommended settings, with the evidence table behind each rule.

## Engine notes

TODO: llama.cpp / llama-swap specifics (flags found in the data: flash-attn, ubatch, KV cache quant, MTP, context extension/YaRN); other engines seen in the evidence (Strata, NInfer).

## Traps

TODO: the documented failure modes — VRAM squatters, OOM on load, quality collapse from over-quantization, context vs recall tradeoffs, harness settings that silently change behaviour.

## Verification

TODO: how the user proves a setting helped — before/after bench runs, recall-at-depth probes, tok/s measurement, memory accounting; what counts as evidence.

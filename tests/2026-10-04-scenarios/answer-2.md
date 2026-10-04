## What's happening

This is a runtime-fit failure, not a load failure — and it's the exact case the evidence base measured.

On the 24 GB card class, the same Q4_K_XL 27B peaked **23,104 MiB at 131k** and **24,142 MiB at 152k, where it crashed mid-inference** (`references/tables/vram-fit.md` T3). Your card is 24,564 MiB in that measurement, so at 131k you are running with roughly **1.4 GiB of headroom** — and that headroom is what a long request consumes. Load-time fit tells you nothing; the buffers grow with actual depth used.

The budget line you're over is not the file. At 131k the non-file cost was ~7.97 GiB: 4.25 GiB KV at q8_0, 0.87 GiB mmproj, ~2.85 GiB CUDA context + compute/graph buffers + GDN state + allocator (`references/tables/kv-cache.md` T2 — that residual is one unverified measurement, so trust llama.cpp's own `KV buffer size` / `compute buffer size` log lines over my arithmetic).

Two things specifically tip a model that loads fine:

1. **MTP draft context.** It's a separate allocation from the target model and can OOM even when the target fits. The same Q4_K_XL entry failed to load at 163k *with* MTP and ran fine at 163k *without* it (22,688 MiB). MTP tensors themselves are a flat +0.42 GiB, but the draft context grows during generation — which is exactly the shape of "crashes partway through."
2. **Anything else holding the card.** A non-llama-server PID is the bug: an embedding daemon held 11.3 GiB after its job ended, and a background session loading a model spoiled a whole sweep.

## What I'd change, in order

1. **Test MTP off on the same long request.** If your file carries MTP tensors, this is the cheapest lever and it costs speed only — the target sampler picks every token, so MTP is not a quality factor. Also log acceptance: below ~50% acceptance, regular quants run faster anyway, so you may be paying for nothing.
2. **Drop KV from q8_0 to q4_0.** At 131k that's 4.25 GiB → ~2.1 GiB. Measured: IQ4_XS ran 262k with q4_0 KV at 21,652 MiB with recall held at 60k/120k/200k depth. Caveat worth stating: recall at depth is not quality parity — the upstream quality bench for q4 KV stops at 128k.
3. **Shrink ubatch, for free.** `-ub 1024` gave no measurable prefill gain on the dense 27B (2186 t/s at both 512 and 1024), while `-ub 256` lowered peak VRAM at 262k from 23,444 to 23,276 MiB. On this architecture ubatch is not a speed lever, so you can take the headroom without giving anything back.
4. **Audit the card during a long run**, not at load: `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv`. Freeing the desktop compositor to the iGPU is a real lever on a shared card.
5. **Match the client cap to the served window.** A client hardcoded to 262144 against a 131k server overfills it — that shows up as HTTP 400 or silent clipping rather than a crash, but it's the same class of bug. Set clip behaviour explicitly.
6. **If you need >152k, Q4_K_XL is simply over budget on this card.** IQ4_XS is the measured long-context tier (229k/262k ran fine). The quant drop may cost less than you fear: IQ4 and IQ3_XXS both scored 11/12 on the same task — the tier shows in output richness, not always correctness.

If you're on Windows: overflow spills silently into system RAM and it decodes 10–20% slower than Linux on the same card. Set "Prefer No Sysmem Fallback" so it fails loudly instead of hanging.

## What I need to be sure

The diagnosis is solid; the ranking depends on four things I don't have:

- **Exact llama.cpp build** — flag names change between builds (`--draft-max` → `--spec-draft-n-max`), and MTP compatibility is commit-specific.
- **OS**, and whether the card is shared with the desktop.
- **Whether the quant file carries MTP tensors**, and its size.
- **What "crashes" looks like** — a CUDA OOM in the log, a hang, or a 400. Those are three different failures.

And the metric: is the goal "it stops crashing," or recall at depth, or tok/s? That decides which line you cut.

## How to confirm it

Every number above is from one card class — 24 GB with 31 GB class RAM — so don't treat 23,104 MiB as yours. Run `bench/quick_bench.md` on your box: memory accounting from the engine's own log lines, peak VRAM per run, recall at depth (needles at ~10/50/90%), and a quality probe with repeats. Three runs per arm, quality held constant, arms interleaved — run-to-run variance was ±1–2 bugs on a 12-bug test, so one run isn't a result. One model on the GPU at a time.

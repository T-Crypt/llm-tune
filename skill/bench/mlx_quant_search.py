#!/usr/bin/env python3
"""mlx_quant_search.py - estimate which mlx-community quants fit an Apple Silicon box.

ESTIMATES ONLY. Nothing in this script was measured here; the wired-limit behaviour is
documented in references/apple-mlx.md with its sources. Verify with a real load plus the
bench (needle.py, quality_probe.py), not with this arithmetic.

Weights are only part of the budget: KV cache, engine overhead, and macOS all compete for
the same wired pool. --kv-gb is a placeholder reserve, not a measurement.

  python3 mlx_quant_search.py --model Qwen3-Coder-30B --ram-gb 24
  python3 mlx_quant_search.py --model Qwen3-Coder-30B --ram-gb 24 --limit-gb 20 --kv-gb 2

Stdlib only. Needs network access to the Hugging Face API.
"""

import argparse
import json
import urllib.parse
import urllib.request

GIB = 1073741824


def get_json(url, timeout):
    req = urllib.request.Request(url, headers={"User-Agent": "llm-tune-mlx-quant-search"})
    return json.loads(urllib.request.urlopen(req, timeout=timeout).read())


def default_limit_gib(ram_gb):
    # Community-reported rule of thumb, not a measurement: about 2/3 at 36 GB or less,
    # about 3/4 above. Read the real value on the machine (sysctl iogpu.wired_limit_mb,
    # or mx.metal.device_info()).
    return round((2 / 3 if ram_gb <= 36 else 3 / 4) * ram_gb, 1)


def weights_gib(repo, timeout):
    tree = get_json("https://huggingface.co/api/models/%s/tree/main" % repo, timeout)
    total = 0
    for entry in tree:
        name = entry.get("path", "")
        if name.endswith(".safetensors"):
            total += entry.get("size", 0)
    return total / GIB


def main():
    p = argparse.ArgumentParser(description="mlx-community fit estimates (estimates only)")
    p.add_argument("--model", required=True, help="search string for the mlx-community org")
    p.add_argument("--ram-gb", required=True, type=float, help="total unified memory")
    p.add_argument("--limit-gb", type=float, default=None,
                   help="current wired limit; omit to use the rule-of-thumb estimate")
    p.add_argument("--kv-gb", type=float, default=2.0, help="reserve for KV and overhead")
    p.add_argument("--max-results", type=int, default=50)
    p.add_argument("--timeout", type=int, default=30)
    a = p.parse_args()

    limit = a.limit_gb if a.limit_gb is not None else default_limit_gib(a.ram_gb)
    estimated = a.limit_gb is None
    cap = 0.90 * a.ram_gb

    search = urllib.parse.quote(a.model)
    url = ("https://huggingface.co/api/models?author=mlx-community&search=%s"
           "&limit=%d&expand%%5B%%5D=safetensors&expand%%5B%%5D=downloads" % (search, a.max_results))
    rows = get_json(url, a.timeout)

    print("wired limit: %.1f GiB %s | KV+overhead reserve: %.1f GiB | cap for a raise: %.1f GiB (90%% of RAM)"
          % (limit, "(estimated rule of thumb - read the real value)" if estimated else "",
             a.kv_gb, cap))

    for repo in rows:
        repo_id = repo.get("id") or repo.get("modelId")
        try:
            w = weights_gib(repo_id, a.timeout)
        except Exception as exc:
            print("%s: could not read sizes (%s)" % (repo_id, exc))
            continue
        needed = w + a.kv_gb
        if needed <= limit:
            verdict = "FITS"
        elif needed <= cap:
            verdict = "FITS ONLY WITH RAISED LIMIT (needs about %.1f GiB wired)" % needed
        else:
            verdict = "DOES NOT FIT"
        print("%s | weights %.1f GiB | needed %.1f GiB | %s" % (repo_id, w, needed, verdict))

    print("Estimates only: safetensors sizes are weights, not the live working set. "
          "Confirm with a real load and the bench.")


if __name__ == "__main__":
    main()

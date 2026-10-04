#!/usr/bin/env python3
"""needle.py - recall at depth against an OpenAI-compatible endpoint.

UNTESTED HERE: written from the method recorded in references/tables/context-recall.md,
never executed in this repo. Stdlib only.

Builds a filler haystack, plants one fact at each requested depth, asks the model to
report it, and prints one JSON line per depth: prompt size, seconds, recall yes/no.

  python3 needle.py --url http://127.0.0.1:8080/v1/chat/completions --model local \
      --depths 0.10,0.50,0.90 --lines 6000 --fact "build 751866"

A depth that returns an error means the prompt exceeded the served window - that is a
harness problem, not a model failure, and it is reported as such.
"""

import argparse
import json
import time
import urllib.error
import urllib.request

FILLER = "{i:06d} INFO worker thread {i % 7} processed batch {i} in {i % 97} ms"


def haystack(n_lines, plant):
    lines = [FILLER.format(i=i) for i in range(n_lines)]
    for idx in plant:
        lines[idx] = "{i:06d} NOTE {fact}".format(i=idx, fact=plant[idx])
    return "\n".join(lines)


def post(url, body, timeout):
    req = urllib.request.Request(
        url, json.dumps(body).encode(), {"Content-Type": "application/json"}
    )
    t0 = time.time()
    try:
        raw = urllib.request.urlopen(req, timeout=timeout).read()
    except urllib.error.HTTPError as exc:
        return None, time.time() - t0, "HTTP %s" % exc.code
    except Exception as exc:  # connection refused, timeout, malformed reply
        return None, time.time() - t0, repr(exc)
    return json.loads(raw), time.time() - t0, None


def main():
    p = argparse.ArgumentParser(description="needle-in-haystack recall at depth")
    p.add_argument("--url", required=True, help="chat/completions endpoint")
    p.add_argument("--model", default="local")
    p.add_argument("--depths", default="0.10,0.50,0.90", help="comma-separated fractions")
    p.add_argument("--lines", type=int, default=6000, help="haystack lines per prompt")
    p.add_argument("--fact", default="build 751866", help="the planted value")
    p.add_argument("--max-tokens", type=int, default=200)
    p.add_argument("--temperature", type=float, default=0.0)
    p.add_argument("--timeout", type=int, default=300)
    a = p.parse_args()

    for depth in [float(x) for x in a.depths.split(",")]:
        idx = int(a.lines * depth)
        text = haystack(a.lines, {idx: a.fact})
        body = {
            "model": a.model,
            "messages": [
                {"role": "user", "content": text + "\n\nReport the NOTE value exactly."}
            ],
            "max_tokens": a.max_tokens,
            "temperature": a.temperature,
        }
        r, secs, err = post(a.url, body, a.timeout)
        if err:
            print(json.dumps({"depth": depth, "error": err, "seconds": round(secs, 1)}))
            continue
        usage = r.get("usage", {})
        pt = usage.get("prompt_tokens", 0)
        ans = (r["choices"][0].get("message") or {}).get("content") or ""
        print(json.dumps({
            "depth": depth,
            "prompt_lines": a.lines,
            "prompt_tokens": pt,
            "prefill_tps": round(pt / secs, 1) if secs and pt else None,
            "seconds": round(secs, 1),
            "finish": r["choices"][0].get("finish_reason"),
            "recall": "yes" if a.fact in ans else "no",
        }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""needle.py - recall at depth against an OpenAI-compatible endpoint.

Stdlib only. Written from the method recorded in references/tables/context-recall.md.
The str.format crash below was found by a live run against a server on 2026-10-05; this
version fixes it and adds BUDGET reporting, but has not been re-run here.

Builds a filler haystack, plants one fact at each requested depth, asks the model to
report it, and prints one JSON line per depth: prompt size, seconds, recall, and status.

  python3 needle.py --url http://127.0.0.1:8080/v1/chat/completions --model local \
      --depths 0.10,0.50,0.90 --lines 6000 --fact "build 751866"

Status meanings:
  ok      - answered within the token budget
  BUDGET  - finish_reason "length" with empty content: a settings failure, not a model
            failure. Raise --max-tokens or cap the reasoning budget before blaming the model.
  error   - the prompt exceeded the served window (HTTP 400) or the request failed.

Works against any OpenAI-compatible server, including mlx_lm.server (flags untested here).
"""

import argparse
import json
import time
import urllib.error
import urllib.request


def filler_line(i):
    # Not str.format with an expression inside the braces: that raises KeyError.
    return "%06d INFO worker thread %d processed batch %d in %d ms" % (i, i % 7, i, i % 97)


def haystack(n_lines, plant):
    lines = [filler_line(i) for i in range(n_lines)]
    for idx in plant:
        lines[idx] = "%06d NOTE %s" % (idx, plant[idx])
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
    p.add_argument("--max-tokens", type=int, default=4096)
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
            print(json.dumps({"depth": depth, "status": "error", "error": err,
                              "seconds": round(secs, 1)}))
            continue
        choice = r["choices"][0]
        msg = choice.get("message") or {}
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        usage = r.get("usage", {})
        pt = usage.get("prompt_tokens", 0)
        finish = choice.get("finish_reason")
        status = "BUDGET" if finish == "length" and not content else "ok"
        print(json.dumps({
            "depth": depth,
            "prompt_lines": a.lines,
            "prompt_tokens": pt,
            "prefill_tps": round(pt / secs, 1) if secs and pt else None,
            "seconds": round(secs, 1),
            "finish": finish,
            "content_chars": len(content),
            "reasoning_chars": len(reasoning),
            "recall": "yes" if a.fact in (content or reasoning) else "no",
            "status": status,
        }))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""quality_probe.py - five verifier-graded tasks, R runs each, pass / fail / BUDGET counts.

Stdlib only. Written from the two-tier method recorded in
references/tables/quality-bench.md. The 600-token default that produced empty answers on a
thinking model was found by a live run on 2026-10-05; this version fixes it. Re-run in this
repo on 2026-10-08: 25/25 at --max-tokens 8192 (records in ../tests/2026-10-08-bench/). A
role with a reasoning budget needs an answer cap above that budget, or every run grades
BUDGET.

These graders check the model's ANSWER (structure, exact value, tool-call shape). They are
the quick tier. The confidence tier runs a model's patch against a real test suite, which a
single-file probe cannot do.

  python3 quality_probe.py --url http://127.0.0.1:8080/v1/chat/completions --model local --runs 5

Run one model at a time; every request loads or uses the resident model.
Works against any OpenAI-compatible server, including mlx_lm.server (its flags not verified here).
"""

import argparse
import json
import re
import urllib.error
import urllib.request


def grader_json(content, calls):
    m = re.search(r"\{.*\}", content, re.S)
    if not m:
        return False
    try:
        obj = json.loads(m.group(0))
    except ValueError:
        return False
    return (isinstance(obj, dict) and {"service", "port", "count"} <= set(obj)
            and obj["service"] == "api" and obj["port"] == 8080 and obj["count"] == 3)


def grader_bug_trace(content, calls):
    return "return a" in content.replace("`", "")


def grader_tool_call(content, calls):
    if not calls:
        return False
    fn = calls[0].get("function", {})
    return fn.get("name") == "grep" and "widget" in (fn.get("arguments") or "")


def grader_format(content, calls):
    # Instruction-following under a constraint: one line, ascending, comma-separated.
    return content.strip() in ("3, 5, 7", "3,5,7")


def grader_needle(content, calls):
    return "18 TiB" in content


def haystack(n, plant_idx, fact):
    lines = ["%06d INFO worker thread %d processed batch %d in %d ms"
            % (i, i % 7, i, i % 97) for i in range(n)]
    lines[plant_idx] = "%06d NOTE planted: %s" % (plant_idx, fact)
    return "\n".join(lines)


TASKS = [
    ("json-strict", [{"role": "user", "content":
        "Return only a JSON object with keys service, port, count for a service named api "
        "on port 8080 with count 3."}], None, grader_json),
    ("bug-trace", [{"role": "user", "content":
        "def fib(n):\n    a, b = 0, 1\n    for _ in range(n):\n        a, b = b, a + b\n    return b\n\n"
        "This returns the wrong value. Name the line to change and what it should become."}],
        None, grader_bug_trace),
    ("tool-call-shape", [{"role": "user", "content":
        "Search the current directory for 'widget'. Use a tool."}],
        [{"type": "function", "function": {
            "name": "grep",
            "description": "Search files for a literal string.",
            "parameters": {"type": "object",
                           "properties": {"pattern": {"type": "string"}},
                           "required": ["pattern"]}}}], grader_tool_call),
    ("constrained-format", [{"role": "user", "content":
        "Reply with exactly one line: the numbers 7, 3, 5 sorted ascending, comma-separated, "
        "nothing else."}], None, grader_format),
    ("short-needle", [{"role": "user", "content":
        haystack(1500, 750, "18 TiB") + "\n\nReport the planted NOTE value."}],
        None, grader_needle),
]


def call(url, model, messages, tools, max_tokens, timeout):
    body = {"model": model, "messages": messages, "max_tokens": max_tokens,
            "temperature": 0.0}
    if tools:
        body["tools"] = tools
    req = urllib.request.Request(url, json.dumps(body).encode(),
                                 {"Content-Type": "application/json"})
    try:
        r = json.loads(urllib.request.urlopen(req, timeout=timeout).read())
    except Exception as exc:
        return None, None, None, 0, repr(exc)
    choice = r["choices"][0]
    msg = choice.get("message") or {}
    content = msg.get("content") or ""
    reasoning = msg.get("reasoning_content") or ""
    return content, msg.get("tool_calls"), choice.get("finish_reason"), len(reasoning), None


def main():
    p = argparse.ArgumentParser(description="five verifier-graded tasks, R runs each")
    p.add_argument("--url", required=True, help="chat/completions endpoint")
    p.add_argument("--model", default="local")
    p.add_argument("--runs", type=int, default=5)
    p.add_argument("--max-tokens", type=int, default=4096,
                   help="answer budget; a thinking model can spend a small budget on "
                        "reasoning and return nothing")
    p.add_argument("--timeout", type=int, default=120)
    a = p.parse_args()

    rows = {}
    for name, messages, tools, grader in TASKS:
        passed = failed = budget = errored = 0
        max_reasoning = 0
        for _ in range(a.runs):
            content, calls, finish, rlen, err = call(
                a.url, a.model, messages, tools, a.max_tokens, a.timeout
            )
            if err:
                errored += 1
                print("%s: error %s" % (name, err))
                continue
            max_reasoning = max(max_reasoning, rlen)
            # BUDGET: the run produced no answer at all. That is a settings failure
            # (answer budget too small / reasoning budget uncapped), not a model failure.
            if finish == "length" and not content and not calls:
                budget += 1
                continue
            try:
                ok = bool(grader(content, calls))
            except Exception as exc:
                ok = False
                print("%s: grader exception %s" % (name, exc))
            passed += 1 if ok else 0
            failed += 0 if ok else 1
        rows[name] = {"pass": passed, "fail": failed, "budget": budget,
                      "error": errored, "max_reasoning_chars": max_reasoning}

    print(json.dumps({"model": a.model, "runs": a.runs,
                      "max_tokens": a.max_tokens, "tasks": rows}, indent=2))
    print("BUDGET counts are settings failures, not model failures: the run hit the answer "
          "cap with nothing to show. Fix the budget before reading the pass rate.")
    print("Report the spread, not the best run: +/-1-2 on a 5-run probe is normal noise.")


if __name__ == "__main__":
    main()

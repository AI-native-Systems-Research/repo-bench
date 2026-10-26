# repo-bench

> Benchmark any code-discovery method against a repo's **merged perf PRs**.

The benchmark answers one question:

> **How much of the performance work that human maintainers actually merged
> would a discovery method rediscover from the same starting point?**

No hand-written answer key. The merged PRs *are* the ground truth — an expert
decided *this* code was worth changing, and the diff says exactly what they
did. `repo-bench` builds that key from a repo's GitHub history, pins a commit
*before* the PRs landed so the method under test is blind to them, and grades
its output against the real diffs.

Discovery-method agnostic: anything that emits a `findings.json` can be scored
— an LLM agent pipeline, a telemetry-driven analyzer, a static tool, a human.

## How grading works — two independent axes

A finding can be right about *where* to look and wrong about *what* to do, or
vice versa. `repo-bench` never conflates the two:

**Localization** — which tier the PR's diff lands in:

| Tier | Meaning |
|---|---|
| **T1** | The diff lands inside the exact symbol (function/method/class) the finding named |
| **T2** | Same file, different function — right neighborhood |

**Solution similarity** — an LLM judge's verdict on the finding against the
actual diff hunk:

| Verdict | Meaning |
|---|---|
| `same_idea` | Essentially the same change the maintainers made |
| `related` | Same code touched, related but distinct change |
| `neighborhood` | Same file, unrelated code |
| `no_match` | Nothing to do with the finding |

Score per `(verdict, tier)` pair:

| Verdict | T1 | T2 |
|---|---:|---:|
| `same_idea` | 1.00 | 0.70 |
| `related` | 0.60 | 0.40 |
| `neighborhood` | 0.05 | 0.05 |
| `no_match` | 0.00 | 0.00 |

Per-finding score = best `(verdict, tier)` weight across its candidate
matches. `weighted_score` = mean across findings, always in `[0, 1]`.

## Quickstart

```bash
pip install -e .
export GITHUB_TOKEN=ghp_...        # read-only `public_repo` scope is enough

# 1) Scrape merged PRs for a window (one-time; cached afterwards).
repo-bench aggregate --start 2025-12-02 --end 2026-06-03

# 2) Build the answer key: filter -> diffs -> snapshot SHA -> workloads -> spec.
repo-bench run \
  --start 2025-12-02 --end 2026-06-03 \
  --rules not-bot,not-revert,not-chore,any-perf-signal-or-label,rank-spec-mag

# 3) Grade a discovery method's findings against it.
repo-bench match \
  --findings <findings.json> \
  --bench-run-dir runs/repo_bench/bench-<window>__<view>__<UTC>/ \
  --experiment <label>
```

Step 2 does **zero LLM calls** — filtering is regex, the snapshot picker is
deterministic, the spec is template rendering. Only `match` costs money
(~$1–5 for a handful of findings).

## Results so far

vLLM, window `2025-12-02 → 2026-06-03`: **624 perf-relevant PRs** filtered out
of 5329 merged, snapshot SHA `a690fb5b`, judge model Sonnet. The answer key is
committed at
[`benchmarks/vllm-2025-12-02__2026-06-03/`](benchmarks/vllm-2025-12-02__2026-06-03/),
so these numbers are checkable. Scored runs target the `vllm/v1/kv_offload`
module — 28 of the 624 PRs touch it.

| Discovery method | Findings | Weighted | `same_idea` PRs hit |
|---|---:|---:|---|
| spotlights-engine, full mode | 9 | **0.53** | 35342, 37206, 38453, 38460, 40020 |
| spotlights-engine, code-only | 10 | 0.45 | 37206, 38460, 40020 |
| spotlights-engine, deep-research full | 9 | 0.39 | 37206, 38460 |
| spotlights-engine, deep-research code-only | 10 | 0.33 | 37206, 38460 |
| Signal pipeline, large OTel bundle | 5 | 0.54 | 35342 |
| Signal pipeline, small OTel bundle | 5 | 0.23 | — |

Two things that fell out of this: tripling the telemetry bundle more than
doubled the signal pipeline's score (0.23 → 0.54), and full mode beats
code-only mainly on *quality* of hit (5 `same_idea` vs 3) rather than headline
score.

All six reports, with per-finding tables and diff citations, are in
[`examples/benchmark/`](examples/benchmark/).

> The two signal-pipeline rows used an OTel-derived scope, not `kv_offload`, so
> their PR lists aren't directly comparable with the engine rows above.

## Why the snapshot SHA matters

Run discovery against a repo's *current* `HEAD` and you are grading it on code
where the optimizations have already been merged. The findings look good and
measure nothing.

The snapshot picker takes the **earliest** PR in the filtered view, subtracts a
buffer (default 24h), and pins the last commit merged before that cutoff. Every
PR being scored is therefore strictly newer than the code the method saw. The
buffer guards against a maintainer merging two related PRs in quick succession,
where the snapshot's parent could already contain side effects of a change
about to be scored.

> The committed vLLM key was built with `buffer_hours: 1`, not the 24h default
> — see the caveat in [`benchmarks/README.md`](benchmarks/README.md).

## Pointing it at another repo

All repo-specific patterns — model families, feature flags, hardware tags,
file→category mappings, perf nouns, chore tags, perf labels — live in TOML
under [`src/repo_bench/configs/`](src/repo_bench/configs/). `vllm.toml` ships
as the default.

```bash
repo-bench run --config vllm ...                  # default
repo-bench run --config /path/to/postgres.toml ...
```

Each config extends a generic baseline (`throughput`, `latency`, `improvement`;
chore tags like `bugfix`, `ci`, `doc`), so a new target adds only what is
specific to it. Adding a repo is a config file, not code.

## Reproducibility

`view_id` is a 12-char hash of the canonical, sorted rule specs: two rule lists
with the same `view_id` produce the same filtered view, and a re-run with
unchanged inputs is a byte-identical no-op. `prompt_sha256` and `model_id` land
in every match report, so any later review can verify what produced a number.

## Docs

- [docs/README.md](docs/README.md) — full module surface: every stage, the
  run-dir layout, schemas, filter rules, workload signals, costs
- [benchmarks/](benchmarks/) — committed answer keys (the 624-PR vLLM set)
- [examples/benchmark/](examples/benchmark/) — the six match reports

## Provenance

Extracted from the `spotlights` research repo (12 commits, June 2026), where it
began as a POC for benchmarking that engine's discovery stage. It is a general
tool — nothing in it is specific to spotlights — so it lives on its own. The
Claude-CLI subprocess runner is vendored in
[`src/repo_bench/agent_runner.py`](src/repo_bench/agent_runner.py) so a bare
clone works standalone; both call sites accept an injected runner, so any agent
CLI can be swapped in.

## License

Apache 2.0 — see [LICENSE](LICENSE).

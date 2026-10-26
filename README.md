<h1 align="center">repo-bench</h1>

<p align="center">
  <strong>Grade any code-discovery method against the performance work humans actually merged.</strong>
</p>

<p align="center">
  <a href="#how-it-works">How it works</a> ·
  <a href="#a-worked-example">Worked example</a> ·
  <a href="#quickstart">Quickstart</a> ·
  <a href="#results-so-far">Results</a> ·
  <a href="#pointing-it-at-another-repo">Another repo</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.11%20%7C%203.12-blue" alt="Python 3.11 or 3.12">
  <img src="https://img.shields.io/badge/tests-75%20passing-brightgreen" alt="75 tests passing">
  <img src="https://img.shields.io/badge/license-Apache%202.0-lightgrey" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/runtime%20deps-pydantic-informational" alt="One runtime dependency: pydantic">
</p>

---

Point a discovery tool at a repo and it will hand you a list of optimizations.
The hard part is knowing whether that list is any good.

`repo-bench` answers it with the one judgement that already exists in the repo:

> **How much of the performance work maintainers actually merged would the
> method rediscover, starting from the code as it stood before any of it landed?**

Every merged perf PR is an expert saying *this code was worth changing*, and
its diff says exactly what they did. So there is no answer key to write — the
diffs are the answer key. `repo-bench` harvests them from GitHub, pins the
commit before they landed so the method under test is blind to them, and grades
its output against the real hunks.

It doesn't care what produced the findings. An LLM agent pipeline, a
telemetry-driven analyzer, a static tool, a human with a hunch — anything that
emits a `findings.json` gets a score on the same scale.

## How it works

<p align="center">
  <img src="docs/img/how-it-works.svg" alt="A time axis. A snapshot SHA is pinned partway along it; the 624 merged perf PRs all land after that point and are never shown to discovery. The method sees only source at the pinned commit and emits findings.json; the PRs' real diffs form the answer key. repo-bench match grades one against the other, scoring where and what separately, producing a weighted score in [0, 1]." width="100%">
</p>

The snapshot pin is what makes the number mean anything. Run discovery against
a repo's current `HEAD` and you are grading it on code where the optimizations
are already merged — the findings look plausible and measure nothing.

So the picker takes the **earliest** PR in the filtered set, subtracts a buffer
(default 24h), and pins the last commit merged before that cutoff. Every PR
being scored is now strictly newer than the code the method saw. The buffer
covers the case where a maintainer merges two related PRs an hour apart: without
it, the snapshot could already contain side effects of a change about to be
scored.

> [!NOTE]
> The committed vLLM key was built with `buffer_hours: 1`, not the 24h default.
> See the caveat in [`benchmarks/README.md`](benchmarks/README.md).

## Scoring: two axes, never collapsed

A finding can name the right function and propose the wrong fix, or the right
fix in the wrong place. Those are different failures, so they get different
axes.

<p align="center">
  <img src="docs/img/scoring-grid.svg" alt="A four-by-two grid. Rows are verdicts: same_idea, related, neighborhood, no_match. Columns are tiers T1 (diff inside the named symbol) and T2 (same file, other function). Values: same_idea scores 1.00 at T1 and 0.70 at T2; related 0.60 and 0.40; neighborhood 0.05 either way; no_match 0.00. A finding takes the best cell it reaches across candidate PRs; the run's score is the mean." width="100%">
</p>

**Localization** is structural and computed, not judged — `T1` means the PR's
diff hunks land inside the exact symbol the finding named, `T2` means the same
file but a different function. **Solution similarity** is the LLM judge's call
on the finding against the actual hunk.

Per-finding score is the best `(verdict, tier)` cell it reaches across its
candidate PRs; the run's `weighted_score` is the mean, always in `[0, 1]`.

The `T1`/`T2` gap is deliberate: hitting the exact function is stronger evidence
than landing in the same file. The gap also surfaces something useful on its
own — `tier_2_yield` counts findings that matched *only* at T2, which is what
you see when a refactor moved the code the finding was aiming at.

## A worked example

One real finding from the engine's full-mode run, scored against the vLLM key:

> **`cand-0005`** — `vllm/v1/kv_offload/worker/cpu_gpu.py`,
> symbol `CpuGpuOffloadingHandler.transfer_async`

Eight PRs in the key touch that file. Six land inside the named symbol (T1), two
elsewhere in the file (T2). The judge read each one's hunks:

| PR | Tier | Verdict | What the diff actually did |
|---|:--:|---|---|
| [#38460](https://github.com/vllm-project/vllm/pull/38460) | T1 | `same_idea` | replaces the per-layer `ops.swap_blocks` loop with one `swap_blocks_batch` over flat pointer arrays |
| [#38453](https://github.com/vllm-project/vllm/pull/38453) | T1 | `same_idea` | builds flat `all_src`/`all_dst`/`all_sizes` across groups and dispatches via `swap_blocks_batch` |
| [#37206](https://github.com/vllm-project/vllm/pull/37206) | T1 | `related` | vectorizes `compute_sub_block_ptrs`, adds shared mmap pinned region |
| [#29870](https://github.com/vllm-project/vllm/pull/29870) | T1 | `related` | records `job_id`→event in `_transfer_events`; not a perf change |
| [#27942](https://github.com/vllm-project/vllm/pull/27942) | T1 | `related` | adds start/end timing events; hot path unchanged |
| [#37853](https://github.com/vllm-project/vllm/pull/37853) | T1 | `related` | constructor refactor for hybrid caches; loop body unchanged |
| [#31916](https://github.com/vllm-project/vllm/pull/31916) | T2 | `neighborhood` | — |
| [#39182](https://github.com/vllm-project/vllm/pull/39182) | T2 | `neighborhood` | — |

Two independent PRs made essentially the change this finding proposed, inside
the exact function it named. So the finding scores **1.00**, and the citations
are in the report — you can read the diffs and disagree.

Note what the `related` rows catch. Four PRs touched the same function without
making that change; a file-overlap metric would have counted them as hits. The
verdict axis is what keeps them out of the headline number.

## Quickstart

```bash
pip install -e .
export GITHUB_TOKEN=ghp_...        # read-only `public_repo` scope is enough
```

```bash
# 1 · Scrape every merged PR in a window. One-time; cached after that.
repo-bench aggregate --start 2025-12-02 --end 2026-06-03

# 2 · Build the answer key: filter → diffs → snapshot SHA → workloads → spec.
repo-bench run \
  --start 2025-12-02 --end 2026-06-03 \
  --rules not-bot,not-revert,not-chore,any-perf-signal-or-label,rank-spec-mag

# 3 · Grade a method's findings against it.
repo-bench match \
  --findings <findings.json> \
  --bench-run-dir runs/repo_bench/bench-<window>__<view>__<UTC>/ \
  --experiment <label>
```

Step 2 makes **zero LLM calls** — filtering is regex, the snapshot picker is
arithmetic, the spec is template rendering. Its cost is GitHub API time:
roughly an hour for the first scrape, then 5–10 minutes for a few hundred
diffs. Only `match` spends money, about **$1–5** for a handful of findings,
and only for findings that have at least one file-overlap candidate to judge.

### What each stage does

| Stage | Role | Cost |
|---|---|---|
| `aggregate` | Pull every merged PR in the window from GitHub into a JSONL cache | ~1h first run, skipped after |
| `filter` | Rules drop bots, reverts and chores; keep quantifiable perf signal; rank by `claimed_pct × 1/files` | <1s, deterministic |
| `fetch-diffs` | Unified diff per PR in the filtered set | 5–10 min / ~600 PRs |
| `snapshot` | Pin a SHA ≥ buffer before the earliest filtered PR | <1s, deterministic |
| `workloads` | Regex out model / feature / hardware signals and runnable serve+bench commands | <10s |
| `bench-spec` | Render the cross-module contract (SHA + signals + output naming) | <1s |
| `match` | Per finding: bucket candidate PRs by file overlap, split T1/T2, slice diffs to the finding's file, one judge call | ~$0.05–0.20 / finding |

`filter`, `fetch-diffs` and `snapshot` are also standalone subcommands for
re-running a single step, but `run` is the normal entry point.

## Results so far

vLLM, window `2025-12-02 → 2026-06-03`. **624 perf-relevant PRs** survived
filtering out of 5329 merged; snapshot `a690fb5b`; judge model Sonnet. Scored
runs target `vllm/v1/kv_offload`, which 28 of the 624 PRs touch.

The answer key is committed at
[`benchmarks/vllm-2025-12-02__2026-06-03/`](benchmarks/vllm-2025-12-02__2026-06-03/),
so these numbers are checkable rather than claimed.

#### spotlights-engine, scope `v1.kv_offload`

Four configurations, same module, same key — directly comparable.

| Configuration | Findings | Weighted | `same_idea` PRs hit |
|---|---:|---:|---|
| `--mode full` (5 stages, papers) | 9 | **0.53** | 35342, 37206, 38453, 38460, 40020 |
| `--mode code_only` | 10 | 0.45 | 37206, 38460, 40020 |
| deep-research, full | 9 | 0.39 | 37206, 38460 |
| deep-research, code-only | 10 | 0.33 | 37206, 38460 |

#### Signal pipeline, OTel-derived scope

| Configuration | Findings | Weighted | `same_idea` PRs hit |
|---|---:|---:|---|
| large OTel bundle (~3× telemetry) | 5 | **0.54** | 35342 |
| small OTel bundle | 5 | 0.23 | — |

> [!IMPORTANT]
> These two rows used an OTel-derived scope, not `kv_offload`. They are
> comparable with each other but **not** with the engine rows above — a
> different scope means a different candidate-PR pool.

Two things fell out of this. Tripling the telemetry bundle more than doubled the
signal pipeline's score, 0.23 → 0.54. And full mode beats code-only mainly on
*quality* of hit — 5 `same_idea` against 3 — rather than on the headline number,
which is exactly the distinction the two-axis score exists to show.

All six reports, with per-finding tables and diff citations, are in
[`examples/benchmark/`](examples/benchmark/).

## Pointing it at another repo

Every repo-specific pattern — model families, feature flags, hardware tags,
file→category maps, perf nouns, chore tags, perf labels — lives in TOML under
[`src/repo_bench/configs/`](src/repo_bench/configs/).

```bash
repo-bench run --config vllm ...                   # ships as the default
repo-bench run --config /path/to/postgres.toml ...
```

Each config extends a generic baseline (`throughput`, `latency`, `improvement`;
chore tags like `bugfix`, `ci`, `doc`), so a new target declares only what is
specific to it. **Adding a repo is a config file, not code.**

### Filter rules

| Rule | Effect |
|---|---|
| `not-bot` | Drop dependabot, github-actions, `*-bot` authors |
| `not-revert` | Drop `Revert ...` titles |
| `not-chore` | Drop bugfix / CI / test / doc / refactor tags — unless the body carries a strict perf claim |
| `any-strict-perf-claim` | Keep a number bound to a perf noun: `5% throughput improvement`, `3x speedup` |
| `any-perf-signal` | Strict claim, or a `[Perf]` / `[Optimize]` title tag |
| `any-perf-signal-or-label` | The above, plus a label whitelist — recovers staged feature work that doesn't quantify per-PR |
| `rank-spec-mag` | Rank by `claimed_pct × 1/files_changed` |

## Reproducibility

`view_id` is a 12-char hash of the canonical, sorted rule specs, so two rule
lists that hash alike produce the same filtered set, and re-running with
unchanged inputs is a byte-identical no-op. `prompt_sha256`, `prompt_version`
and `judge_model` land in every match report, so a later reader can verify what
produced a number.

Matching itself is not cached — each `match` invocation re-judges against
current diffs. The prompt and judge model are pinned and recorded, but there is
no on-disk memo; that is a POC stance, not a finished one.

## Layout

```
src/repo_bench/        the module — CLI, filters, snapshot, workloads, matcher
benchmarks/            committed answer keys (the 624-PR vLLM set)
examples/benchmark/    six match reports with per-finding tables
docs/README.md         full module surface: stages, run-dir layout, schemas, costs
tests/                 75 tests, ~1s, no live LLM calls
```

- **[docs/README.md](docs/README.md)** — the reference: every stage in detail,
  run-dir layout, schemas, workload signals, cost model
- **[benchmarks/README.md](benchmarks/README.md)** — what a committed answer key
  contains and how to grade against one
- **[examples/benchmark/README.md](examples/benchmark/README.md)** — how to read
  a match report

## Provenance

Extracted from the `spotlights` research repo, where it began in June 2026 as a
POC for benchmarking that engine's discovery stage — the original 12 commits are
preserved here. Nothing in it is specific to spotlights, so it lives on its own.

The `claude -p` subprocess runner is vendored in
[`src/repo_bench/agent_runner.py`](src/repo_bench/agent_runner.py) so a bare
clone works standalone. Both call sites take an injected runner via a
`Protocol`, so any agent CLI can be swapped in — and the test suite uses that
seam to stay offline.

## License

Apache 2.0 — see [LICENSE](LICENSE).

# Benchmarks — versioned answer keys

Each subdirectory is one **answer key**: a filtered, ranked set of merged PRs
plus the snapshot SHA that pins the code a discovery method is allowed to see.
These are committed so the benchmark is reproducible from a bare clone — you
can inspect the exact PR set, re-grade your own findings against it, and check
the published scores without re-scraping GitHub.

What is *not* committed: the raw scrape (`prs.jsonl`, 5329 PRs) and the 624
per-PR diffs, ~32 MB together. Both are GitHub-rebuildable:

```bash
repo-bench aggregate   --start 2025-12-02 --end 2026-06-03
repo-bench fetch-diffs --bench-run-dir <run-dir>
```

`match` needs those diffs — it judges findings against the actual hunks — so
grading a new findings.json against a committed key means fetching the diffs
first (5–10 min with a `GITHUB_TOKEN`).

## `vllm-2025-12-02__2026-06-03`

| | |
|---|---|
| Target repo | [vllm-project/vllm](https://github.com/vllm-project/vllm) |
| Window | 2025-12-02 → 2026-06-03 |
| PRs merged in window | 5329 |
| **PRs in the answer key** | **624** (11.7%) |
| `view_id` | `8a6ca48d0d62` |
| Snapshot SHA | `a690fb5bd6773128fc82bf03f612156b387d5b61` |
| Filter rules | `not-bot,not-revert,not-chore,any-perf-signal-or-label,rank-spec-mag` |

| File | What it is |
|---|---|
| `view/prs.jsonl` | The answer key: 624 filtered PRs, ranked, one JSON object per line |
| `view/manifest.json` | Rule specs + `view_id`. Re-deriving with these rules reproduces the key exactly |
| `snapshot.json` | The pinned SHA + why it was chosen |
| `bench_spec.json` | Cross-module contract (SHA + workload signals + output naming) |
| `run_report.json` | Per-stage status and counts from the run that produced this key |
| `module_hit_map.md` | Which modules the 624 PRs concentrate in, vs. baseline repo churn |
| `workload_summary.md` | Aggregate model / feature / hardware signals across the key |
| `workload_portfolio.md` | Runnable serve + bench commands extracted from PR bodies |

### Caveat: this key used a 1-hour buffer

`buffer_hours` is **1** here, not the 24h default. The earliest PR in the key
(#29600, merged 2025-12-02T06:21:39Z) is only 1h28m newer than the snapshot
commit (#29243, 2025-12-02T04:53:28Z).

The buffer exists to stop a maintainer's rapid follow-up PR from leaking into
the snapshot — if two related PRs merge an hour apart, the snapshot can
already contain side effects of a change about to be scored. At 1h that
guard is thin for the earliest handful of PRs in the key. It does not affect
the scored results below, which all target `vllm/v1/kv_offload` and match
against PRs merged well after the window opened, but a fresh key should use
the default:

```bash
repo-bench run --start <s> --end <e> --rules <...>   # 24h buffer
```

### Results against this key

See [`examples/benchmark/`](../examples/benchmark/) for the six match reports
and the per-finding tables. Scored runs target the `vllm/v1/kv_offload`
module — 28 of the 624 PRs touch it.

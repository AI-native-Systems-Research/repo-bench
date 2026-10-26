# Module hit map — `bench-2025-12-02__2026-06-03__8a6ca48d0d62__20260609T070131Z`

- **ProjectTree**: `project_tree.json` (53 leaf modules; 49 after exclusions)
- **Filtered PRs (perf-relevant)**: 624
- **All PRs in window**: 5329
- **Window**: `2025-12-02__2026-06-03`
- **Snapshot SHA**: `a690fb5bd6773128fc82bf03f612156b387d5b61`
- **Excluded modules**: `tests`, `docs`, `tools`, `benchmarks`, `examples` (use `--exclude ''` to disable)

Each module's `path` is used as a directory prefix; a PR is counted once per module if it touches *any* file under that prefix. `perf_concentration_ratio` is `pct_filtered / pct_all` — values >1 mean the module is more perf-targeted than baseline repo churn would predict; <1 means the module gets touched a lot by general engineering work but perf PRs avoid it; ~1 means proportional.

## Top 30 modules by filtered-PR coverage

| Module | Path | Filtered | % filt | All | % all | Perf ratio |
|---|---|---:|---:|---:|---:|---:|
| `distributed.kv_transfer` | `vllm/distributed/kv_transfer` | 149 | 23.9% | 198 | 3.7% | 6.43× |
| `config` | `vllm/config` | 77 | 12.3% | 451 | 8.5% | 1.46× |
| `model_executor.layers.fused_moe` | `vllm/model_executor/layers/fused_moe` | 75 | 12.0% | 393 | 7.4% | 1.63× |
| `v1.worker` | `vllm/v1/worker` | 72 | 11.5% | 517 | 9.7% | 1.19× |
| `model_executor.models` | `vllm/model_executor/models` | 61 | 9.8% | 812 | 15.2% | 0.64× |
| `v1.attention` | `vllm/v1/attention` | 59 | 9.5% | 342 | 6.4% | 1.47× |
| `model_executor.layers.quantization` | `vllm/model_executor/layers/quantization` | 49 | 7.9% | 385 | 7.2% | 1.09× |
| `v1.core` | `vllm/v1/core` | 36 | 5.8% | 135 | 2.5% | 2.28× |
| `v1.engine` | `vllm/v1/engine` | 36 | 5.8% | 194 | 3.6% | 1.58× |
| `utils` | `vllm/utils` | 35 | 5.6% | 164 | 3.1% | 1.82× |
| `engine` | `vllm/engine` | 29 | 4.6% | 126 | 2.4% | 1.97× |
| `v1.kv_offload` | `vllm/v1/kv_offload` | 28 | 4.5% | 51 | 1.0% | 4.69× |
| `compilation` | `vllm/compilation` | 25 | 4.0% | 181 | 3.4% | 1.18× |
| `platforms` | `vllm/platforms` | 25 | 4.0% | 166 | 3.1% | 1.29× |
| `entrypoints.openai` | `vllm/entrypoints/openai` | 23 | 3.7% | 302 | 5.7% | 0.65× |
| `csrc.moe` | `csrc/moe` | 19 | 3.0% | 41 | 0.8% | 3.96× |
| `v1.spec_decode` | `vllm/v1/spec_decode` | 18 | 2.9% | 80 | 1.5% | 1.92× |
| `model_executor.layers.mamba` | `vllm/model_executor/layers/mamba` | 15 | 2.4% | 72 | 1.4% | 1.78× |
| `model_executor.model_loader` | `vllm/model_executor/model_loader` | 15 | 2.4% | 81 | 1.5% | 1.58× |
| `transformers_utils` | `vllm/transformers_utils` | 15 | 2.4% | 183 | 3.4% | 0.70× |
| `v1.sample` | `vllm/v1/sample` | 15 | 2.4% | 40 | 0.8% | 3.20× |
| `csrc.quantization` | `csrc/quantization` | 13 | 2.1% | 50 | 0.9% | 2.22× |
| `distributed.device_communicators` | `vllm/distributed/device_communicators` | 13 | 2.1% | 64 | 1.2% | 1.73× |
| `lora` | `vllm/lora` | 12 | 1.9% | 105 | 2.0% | 0.98× |
| `model_executor.layers.fla` | `vllm/model_executor/layers/fla` | 11 | 1.8% | 23 | 0.4% | 4.08× |
| `multimodal` | `vllm/multimodal` | 10 | 1.6% | 121 | 2.3% | 0.71× |
| `model_executor.warmup` | `vllm/model_executor/warmup` | 8 | 1.3% | 19 | 0.4% | 3.60× |
| `csrc.cpu` | `csrc/cpu` | 7 | 1.1% | 59 | 1.1% | 1.01× |
| `distributed.eplb` | `vllm/distributed/eplb` | 6 | 1.0% | 34 | 0.6% | 1.51× |
| `entrypoints.pooling` | `vllm/entrypoints/pooling` | 6 | 1.0% | 77 | 1.4% | 0.67× |

## Heatmap

Bar length = `% filtered` (share of perf PRs that touch the module). Bar color = `perf_concentration_ratio` — green = perf-targeted (>1), grey ≈ proportional, red = perf-avoided (<1). The **right-side number** is the ratio.

![module hit map](module_hit_map.svg)

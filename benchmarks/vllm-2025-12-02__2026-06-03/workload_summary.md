# Workload analysis — 624 PRs in view
- **112 of 624** PRs include an explicit `vllm serve` command in body (~ 18%)
- **106 of 624** PRs include a benchmark result table (~ 17%)

## Top models

| Item | Count | % of 624 |
|---|---:|---:|
| `deepseek-v` | 50 | 8.0% |
| `qwen-dense` | 36 | 5.8% |
| `llama-3` | 35 | 5.6% |
| `qwen3-moe` | 26 | 4.2% |
| `deepseek-r` | 23 | 3.7% |
| `gpt-oss` | 17 | 2.7% |
| `minimax-m` | 12 | 1.9% |
| `glm-4` | 9 | 1.4% |
| `eagle` | 8 | 1.3% |
| `whisper` | 6 | 1.0% |
| `medusa` | 2 | 0.3% |
| `mistral-7b` | 2 | 0.3% |
| `gemma` | 2 | 0.3% |
| `mixtral-8x` | 1 | 0.2% |

## Top features

| Item | Count | % of 624 |
|---|---:|---:|
| `fp8` | 124 | 19.9% |
| `kv_cache` | 121 | 19.4% |
| `attention` | 100 | 16.0% |
| `moe` | 87 | 13.9% |
| `prefix_cache` | 77 | 12.3% |
| `scheduler` | 54 | 8.7% |
| `offload` | 51 | 8.2% |
| `spec_decode` | 48 | 7.7% |
| `expert_parallel` | 43 | 6.9% |
| `bf16` | 38 | 6.1% |
| `mla` | 35 | 5.6% |
| `async_scheduling` | 28 | 4.5% |
| `cuda_graph` | 27 | 4.3% |
| `torch_compile` | 17 | 2.7% |
| `rmsnorm` | 13 | 2.1% |

## Top hardware mentions

| Item | Count | % of 624 |
|---|---:|---:|
| `nvidia-hopper` | 56 | 9.0% |
| `amd` | 47 | 7.5% |
| `nvidia-blackwell` | 39 | 6.2% |
| `sm_arch` | 12 | 1.9% |
| `nvidia-ampere` | 10 | 1.6% |
| `nvidia-l4` | 4 | 0.6% |
| `tpu` | 1 | 0.2% |

## Top file categories touched

| Item | Count | % of 624 |
|---|---:|---:|
| `distributed_comm` | 168 | 26.9% |
| `moe_kernel` | 76 | 12.2% |
| `attention` | 59 | 9.5% |
| `cuda_kernels` | 57 | 9.1% |
| `scheduler` | 54 | 8.7% |
| `quantization` | 48 | 7.7% |
| `kv_cache` | 36 | 5.8% |
| `engine_v1` | 35 | 5.6% |
| `torch_compile` | 25 | 4.0% |
| `platform` | 25 | 4.0% |
| `spec_decode` | 24 | 3.8% |
| `multimodal` | 11 | 1.8% |
| `lora` | 11 | 1.8% |
| `norm_rope` | 8 | 1.3% |
| `eplb` | 6 | 1.0% |

## Parallelism axes mentioned

| Item | Count | % of 624 |
|---|---:|---:|
| `tp` | 57 | 9.1% |
| `max_num_seqs` | 47 | 7.5% |
| `dp` | 9 | 1.4% |
| `pp` | 4 | 0.6% |

## Top model × feature co-occurrences

| Model + feature | PRs |
|---|---:|
| `deepseek-v|fp8` | 29 |
| `deepseek-v|kv_cache` | 21 |
| `deepseek-v|attention` | 18 |
| `qwen-dense|kv_cache` | 17 |
| `deepseek-v|expert_parallel` | 17 |
| `qwen3-moe|fp8` | 16 |
| `deepseek-v|prefix_cache` | 13 |
| `deepseek-v|moe` | 12 |
| `qwen3-moe|moe` | 12 |
| `deepseek-r|fp8` | 12 |
| `deepseek-v|mla` | 10 |
| `llama-3|prefix_cache` | 9 |
| `llama-3|fp8` | 9 |
| `llama-3|spec_decode` | 9 |
| `qwen-dense|attention` | 9 |
| `llama-3|kv_cache` | 9 |
| `qwen-dense|prefix_cache` | 9 |
| `minimax-m|fp8` | 9 |
| `gpt-oss|moe` | 8 |
| `deepseek-r|moe` | 8 |
| `minimax-m|moe` | 8 |
| `qwen3-moe|prefix_cache` | 7 |
| `qwen-dense|fp8` | 7 |
| `deepseek-r|kv_cache` | 7 |
| `deepseek-r|expert_parallel` | 7 |

## Suggested workload portfolio (greedy AND-cover)

Each entry is (model, feature). A PR is counted as covered ONLY if it mentions BOTH the model AND the feature. Greedy cover picks the highest-yield (model, feature) combo, marks those PRs covered, and repeats. Pairs covering fewer than 3 PRs are pruned as noise.

| # | Model | Feature | Total PRs at intersection | New covered | Cumulative share | Example PRs |
|---:|---|---|---:|---:|---:|---|
| 1 | `deepseek-v` | `fp8` | 29 | 29 | 4.6% | #24252, #27532, #29213, #29304, #29499 |
| 2 | `qwen-dense` | `kv_cache` | 17 | 15 | 7.1% | #24322, #29934, #30207, #33290, #34147 |
| 3 | `qwen3-moe` | `fp8` | 16 | 12 | 9.0% | #27883, #29470, #29512, #32618, #33173 |
| 4 | `deepseek-r` | `fp8` | 12 | 11 | 10.7% | #29354, #29795, #30014, #30729, #32619 |
| 5 | `llama-3` | `kv_cache` | 9 | 8 | 12.0% | #25954, #28454, #34931, #35270, #37160 |
| 6 | `llama-3` | `spec_decode` | 9 | 8 | 13.3% | #29821, #31739, #32642, #33612, #35158 |
| 7 | `qwen3-moe` | `moe` | 12 | 8 | 14.6% | #28284, #29600, #30897, #31832, #32520 |
| 8 | `gpt-oss` | `moe` | 8 | 7 | 15.7% | #29257, #30647, #36038, #37136, #37205 |


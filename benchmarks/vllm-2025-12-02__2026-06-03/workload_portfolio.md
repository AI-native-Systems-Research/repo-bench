### W1 — llama-3 + no-flags

**Covers 8 PRs.** Hardware: B200.

```bash
vllm serve nvidia/Llama-3.3-70B-Instruct-NVFP4
```

_Source PRs: #29025, #31739, #32520, #32642, #34299, #36029, #40900, #41043_

### W2 — deepseek-v + no-flags

**Covers 7 PRs.** Hardware: B200.

```bash
vllm serve nvidia/DeepSeek-V3.2-NVFP4 -tp 4

vllm bench serve --backend vllm --model nvidia/DeepSeek-V3.2-NVFP4 --input-len 131072 --output-len 2048 --num-prompts 1
```

_Source PRs: #32642, #33451, #33680, #34917, #35122, #36012, #37421_

### W3 — qwen-dense + no-flags

**Covers 5 PRs.**

```bash
vllm serve Qwen/Qwen3-32B --max-model-len 20000 --disable-uvicorn-access-log

vllm bench serve --model Qwen/Qwen3-32B --dataset-name hf --dataset-path philschmid/mt-bench --num-prompts 80 --max-concurrency (100|1) --temperature 0.0 --top-p 1.0 2>&1 > results/qwen3-32b-t0-run1.out &
```

_Source PRs: #24322, #30897, #31041, #34188, #36869_

### W4 — glm-4 + expert_parallel

**Covers 5 PRs.**

```bash
vllm serve zai-org/GLM-4.7-FP8 -tp 8 --port 9256 --enable-expert-parallel --max_num_seqs 128

vllm bench serve --model zai-org/GLM-4.7-FP8 --dataset-name random --host 127.0.0.1 --port 9256 --random-input-len 2 --random-output-len 128 --request-rate inf --num-prompts 128
```

_Source PRs: #31754, #31830, #32058, #32211, #32273_

### W5 — minimax-m + no-flags

**Covers 5 PRs.**

```bash
vllm serve MiniMaxAI/MiniMax-M2.5 --trust-remote-code --tensor-parallel-size 2
```

_Source PRs: #34924, #37695, #38993, #39141, #39547_

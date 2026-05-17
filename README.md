# Multi-Relational Memory Graph (MRMG)

An exploration of typed memory link structures for long-context dialogue retrieval, built on the [A-Mem](https://arxiv.org/pdf/2502.12110) framework.

## Topic

Original A-Mem stores all memory relations (temporal, semantic, causal) in a single undifferentiated link list. MRMG investigates whether **link type differentiation** improves retrieval — progressing from no typing → coarse two-type (temporal/logical) → fine-grained two-level four-type structure (temporal, entity, causality, elaboration), with category-aware multi-layer graph expansion strategies.

## Method

- **Two-level link hierarchy:** Temporal (session-based full-connection) vs. Logical (entity co-occurrence + LLM-judged causality/elaboration)
- **Category-aware retrieval:** 3-step process — semantic retrieval → typed multi-layer graph expansion → selective cross-encoder re-ranking (skipped for C2/C4 to preserve temporal/reasoning chains)
- **5 question types** with tailored strategies: C1 (entity expansion), C2 (temporal expansion), C3 (entity→causality→elaboration), C4 (temporal+entity→causality), C5 (no expansion, doubled initial recall)

## Test Commands

```bash
# Quick test 
python test_advanced.py

# Full test
python test_advanced.py

# Robust version (supports openai/vllm/ollama backends)
python test_advanced_robust.py --backend [your backend] --model [your model] \
    --dataset data/locomo10.json 

# Analyze results
python analyze_results.py <log_file>
```

## Results (1/10 LoCoMo)

| Scheme | Overall F1 |
|--------|-----------|
| Original A-Mem | 0.2712 |
| + Temporal/Logical (keyword) | 0.3121 |
| + Temporal/Logical (LLM) | 0.3205 |
| **MRMG (full)** | **0.3597** |

> Note: This is an exploratory study on link type differentiation. Results are vs. the A-Mem baseline only; not compared against MemGPT, GraphRAG, etc.

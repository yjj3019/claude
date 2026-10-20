# AI Infrastructure Domain Pack

## Focus Areas

- local LLM inference (memory bandwidth, context length, quantization)
- accelerator hardware (GPU, NPU, Apple Silicon, discrete accelerators)
- storage and networking for model weights and checkpoints
- MLOps / serving (batch vs streaming, observability, cost)
- power, cooling, and operational complexity
- evaluation and regression of model quality
- procurement and supply constraints

## Rules

- Distinguish peak capability (FLOPS, tokens/s) from sustained throughput under realistic workload and memory pressure.
- Include cost, power, cooling, memory capacity/bandwidth, storage, and operational complexity in infrastructure recommendations.
- Avoid hype. Mark unverified performance, pricing, or availability claims `[unverified]`.
- Specify model size, quantization, batch size, and hardware generation when discussing inference numbers.
- Prefer measured results or vendor primary sources over marketing claims.
- Note supply-chain or lead-time constraints when relevant to procurement.

## Evaluation Considerations

For local or on-prem inference claims, verify or state assumptions about:

- available memory (system + accelerator)
- memory bandwidth bottleneck
- context length and KV cache pressure
- quantization quality impact
- concurrent request behavior

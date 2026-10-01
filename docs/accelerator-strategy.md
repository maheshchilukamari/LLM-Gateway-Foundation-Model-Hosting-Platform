# Accelerator Strategy

Local development runs on CPU by default. Model providers should choose CUDA automatically when PyTorch reports that CUDA is available:

```python
device = "cuda" if torch.cuda.is_available() else "cpu"
```

Production accelerator topics:

- GPU memory limits constrain model size, batch size, and context length.
- Quantization can reduce memory pressure at possible quality or latency tradeoffs.
- Mixed precision can improve throughput on supported GPUs.
- Tensor and pipeline parallelism become relevant for larger models.
- GPU utilization, queue depth, and P95 latency should guide scaling decisions.

TPU execution is not implemented. TPU support would require provider-specific runtime integration and deployment design.


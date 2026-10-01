"""Resource monitoring abstraction."""


class ResourceMonitor:
    """Collect host resource usage for resource-aware routing."""

    def snapshot(self) -> dict[str, float]:
        try:
            import psutil

            return {
                "cpu_percent": float(psutil.cpu_percent(interval=None)),
                "memory_percent": float(psutil.virtual_memory().percent),
                "gpu_percent": 0.0,
                "gpu_memory_percent": 0.0,
            }
        except Exception:
            return {
                "cpu_percent": 0.0,
                "memory_percent": 0.0,
                "gpu_percent": 0.0,
                "gpu_memory_percent": 0.0,
            }


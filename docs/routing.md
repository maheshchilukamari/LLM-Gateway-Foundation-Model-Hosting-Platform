# Routing

The router will support these strategies:

- `lowest_latency`
- `lowest_cost`
- `highest_quality`
- `highest_throughput`
- `balanced`
- `resource_aware`
- `fallback`

The balanced strategy uses configurable weights from `configs/routing.yaml`:

```text
routing_score =
  quality_weight * normalized_quality
  - latency_weight * normalized_latency
  - cost_weight * normalized_cost
  + throughput_weight * normalized_throughput
```

Routers must consider model availability, health, task capability, context limits, estimated cost, throughput, and resource saturation. The implementation should avoid prompt text, user IDs, or other high-cardinality values in metrics labels.


# Service Level Objectives

These are target SLOs, not measured claims.

## SLIs

- Availability: successful requests divided by total valid requests.
- Gateway overhead latency: gateway processing time excluding provider inference.
- Error rate: failed valid requests divided by total valid requests.
- Cache dependency health: cache availability and latency.
- Model health: availability, recent failures, and latency trend.

## Example SLOs

- Gateway availability target: >= 99.9%.
- P95 gateway overhead target: < 100 ms excluding model inference.
- Request error rate target: < 1% under supported load.
- Cache availability should not determine gateway availability.

Load tests must be run before claiming measured performance.


# Testing and Load Testing

Run unit and integration tests:

```bash
pytest
```

Run lint:

```bash
ruff check .
```

Run a smoke benchmark against a running local server:

```bash
python scripts/benchmark.py
```

Run Locust:

```bash
locust -f locustfile.py --host http://localhost:8000
```

Do not publish benchmark numbers unless they were generated on the target machine and saved under `benchmarks/`.


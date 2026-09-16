# Performance Testing

## FastAPI Load Test

The API was load tested locally using Locust against the
Dockerized FastAPI service.

### Configuration

- Concurrent users: 20
- User spawn rate: 2 users/second
- Target: `http://127.0.0.1:8000`
- Endpoints:
  - `GET /`
  - `GET /health`

### Results

| Metric | Result |
|---|---:|
| Total Requests | 2,876 |
| Failed Requests | 0 |
| Failure Rate | 0% |
| Median Latency | 4 ms |
| Average Latency | 4.51 ms |
| 95th Percentile | 7 ms |
| 99th Percentile | 11 ms |
| Maximum Latency | 24 ms |
| Observed Throughput | ~11.8 requests/sec |

No HTTP failures occurred during the test.

The observed throughput is influenced by the intentional
Locust user wait time and should not be interpreted as the
maximum throughput of FastAPI.


## Contract Processing Benchmark

The complete asynchronous contract-analysis pipeline was
benchmarked using three sequential executions.

Each execution included:

1. Contract upload
2. Redis task queue
3. Celery processing
4. PDF text extraction
5. spaCy entity extraction
6. RoBERTa clause classification
7. Risk scoring
8. Pinecone vector indexing
9. Task completion

### Results

| Run | Queue Time | Processing Time | Total Time |
|---|---:|---:|---:|
| 1 | 0.124 s | 19.88 s | 20.00 s |
| 2 | 0.059 s | 6.08 s | 6.14 s |
| 3 | 0.026 s | 7.13 s | 7.16 s |

### Summary

- Successful runs: 3/3
- Average end-to-end latency: 11.10 seconds
- Fastest execution: 6.14 seconds
- Slowest execution: 20.00 seconds
- Warm-run average (runs 2 and 3): approximately 6.65 seconds

The first execution was significantly slower than subsequent
runs, consistent with cold-start and runtime/model warm-up
overhead.

All benchmark runs completed successfully.
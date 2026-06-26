# Benchmark Results

This document captures the latest local validation results for the inference runtime regression gate.

The project validates two paths:

1. A passing path where baseline and candidate runs use the same benchmark configuration.
2. A controlled failure path where the candidate run injects a 2.0 ms delay to produce a reproducible p95 latency regression.

## Regression Configuration

The regression gate compares candidate performance against baseline performance using the configured stage, metric, and threshold.

```json
{
  "stage": "end_to_end_ms",
  "metric": "p95_ms",
  "max_regression_percent": 10.0
}
```

A candidate run fails validation when its p95 end to end latency regresses by more than 10 percent compared to the baseline.

## Passing Gate

Baseline and candidate runs use the same benchmark configuration with no injected delay.

### Command

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_pass_gate.ps1
```

### Summary

| Metric      |     Baseline |    Candidate |  Change |
| ----------- | -----------: | -----------: | ------: |
| Throughput  | 319.91 req/s | 432.95 req/s | +35.33% |
| p50 latency |     2.601 ms |     2.022 ms | -22.26% |
| p95 latency |     5.548 ms |     3.726 ms | -32.83% |
| p99 latency |    10.078 ms |     4.069 ms | -59.62% |

### Gate Result

| Check                | Value         |
| -------------------- | ------------- |
| Regression stage     | end_to_end_ms |
| Regression metric    | p95_ms        |
| Regression threshold | 10.00%        |
| Observed change      | -32.83%       |
| Status               | PASS          |

### Output

```text
===== Running passing inference regression gate =====
Inference Runtime Benchmark
Device: cpu
Batch size: 16
Throughput: 319.91 req/s
p50: 2.601 ms
p95: 5.548 ms
p99: 10.078 ms
Saved: results\baseline.json

Inference Runtime Benchmark
Device: cpu
Batch size: 16
Throughput: 432.95 req/s
p50: 2.022 ms
p95: 3.726 ms
p99: 4.069 ms
Saved: results\candidate.json

Inference Runtime Regression Check
Stage: end_to_end_ms
Metric: p95_ms
Baseline: 5.548 ms
Candidate: 3.726 ms
Change: -32.83%
Threshold: 10.00%
Status: PASS

Validated benchmark result: results\baseline.json
Validated benchmark result: results\candidate.json
Smoke test passed.

PASS gate completed successfully.
```

## Controlled Failure Demo

The candidate run injects a controlled 2.0 ms delay to make the regression path reproducible.

This avoids relying on noisy CPU variance to demonstrate the failure path.

### Command

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_fail_demo.ps1
```

### Summary

| Metric      |     Baseline |    Candidate |   Change |
| ----------- | -----------: | -----------: | -------: |
| Throughput  | 419.76 req/s | 196.60 req/s |  -53.16% |
| p50 latency |     2.264 ms |     4.682 ms | +106.80% |
| p95 latency |     2.933 ms |     6.676 ms | +127.64% |
| p99 latency |     3.669 ms |    11.082 ms | +202.04% |

### Gate Result

| Check                | Value         |
| -------------------- | ------------- |
| Regression stage     | end_to_end_ms |
| Regression metric    | p95_ms        |
| Regression threshold | 10.00%        |
| Observed change      | +127.64%      |
| Status               | FAIL          |

### Output

```text
===== Running controlled inference regression failure demo =====
Inference Runtime Benchmark
Device: cpu
Batch size: 16
Throughput: 419.76 req/s
p50: 2.264 ms
p95: 2.933 ms
p99: 3.669 ms
Saved: results\baseline.json

Inference Runtime Benchmark
Device: cpu
Batch size: 16
Throughput: 196.60 req/s
p50: 4.682 ms
p95: 6.676 ms
p99: 11.082 ms
Saved: results\candidate.json

Inference Runtime Regression Check
Stage: end_to_end_ms
Metric: p95_ms
Baseline: 2.933 ms
Candidate: 6.676 ms
Change: 127.64%
Threshold: 10.00%
Status: FAIL

Validated benchmark result: results\baseline.json
Validated benchmark result: results\candidate.json
Smoke test passed.

Controlled failure demo failed as expected.
```

## What This Validates

The local checks validate that the project can:

1. Run baseline and candidate inference style benchmarks.
2. Capture p50, p95, and p99 latency.
3. Measure throughput.
4. Compare candidate performance against a baseline.
5. Fail validation when candidate p95 latency exceeds the configured threshold.
6. Validate benchmark result JSON structure with a smoke test.

## Notes

These results were collected from local CPU runs. Absolute latency values will vary by machine, CPU load, and scheduler behavior.

The important behavior is the validation flow:

1. The pass gate succeeds when candidate p95 latency stays within the configured threshold.
2. The controlled failure demo fails when a reproducible candidate delay pushes p95 latency beyond the threshold.

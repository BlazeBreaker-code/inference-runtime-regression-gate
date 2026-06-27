# Benchmark Results

This document captures the latest GitHub Actions validation results for the inference runtime regression gate.

The project validates two important paths:

1. A passing path where baseline and candidate runs use the same benchmark configuration.
2. A controlled regression detection path where the candidate run injects a 2.0 ms delay to produce a reproducible p95 latency regression.

## Regression Configuration

The regression gate compares candidate performance against baseline performance using the configured stage, metric, percent threshold, and absolute regression floor.

```json
{
  "stage": "end_to_end_ms",
  "metric": "p95_ms",
  "max_regression_percent": 10.0,
  "min_regression_ms": 1.0
}
```

A candidate run fails validation only when both conditions are true:

1. Candidate p95 latency regresses by more than 10 percent.
2. Candidate p95 latency increases by more than 1.0 ms.

This keeps the gate from failing on small noisy deltas while still catching meaningful regressions.

## Default Regression Gate

The default regression gate runs on push and pull request.

Baseline and candidate runs use the same benchmark configuration with no injected delay.

### Summary

| Metric      |     Baseline |    Candidate | Change |
| ----------- | -----------: | -----------: | -----: |
| Throughput  | 233.24 req/s | 219.38 req/s | -5.94% |
| p50 latency |     4.260 ms |     4.537 ms | +6.50% |
| p95 latency |     4.357 ms |     4.648 ms | +6.66% |
| p99 latency |     5.215 ms |     4.844 ms | -7.11% |

### Gate Result

| Check                    | Value         |
| ------------------------ | ------------- |
| Regression stage         | end_to_end_ms |
| Regression metric        | p95_ms        |
| Baseline p95             | 4.357 ms      |
| Candidate p95            | 4.648 ms      |
| Percent change           | +6.66%        |
| Absolute change          | +0.290 ms     |
| Percent threshold        | 10.00%        |
| Minimum regression floor | 1.000 ms      |
| Status                   | PASS          |

### Output

```text
Inference Runtime Regression Check
Stage: end_to_end_ms
Metric: p95_ms
Baseline: 4.357 ms
Candidate: 4.648 ms
Change: 6.66%
Absolute change: 0.290 ms
Percent threshold: 10.00%
Minimum regression floor: 1.000 ms
Status: PASS
```

## Manual Pass Gate

The manual pass gate validates the normal passing path.

### Summary

| Metric      |     Baseline |    Candidate | Change |
| ----------- | -----------: | -----------: | -----: |
| Throughput  | 234.11 req/s | 233.37 req/s | -0.32% |
| p50 latency |     4.260 ms |     4.260 ms | +0.00% |
| p95 latency |     4.362 ms |     4.384 ms | +0.49% |
| p99 latency |     4.444 ms |     4.730 ms | +6.44% |

### Gate Result

| Check                    | Value         |
| ------------------------ | ------------- |
| Regression stage         | end_to_end_ms |
| Regression metric        | p95_ms        |
| Baseline p95             | 4.362 ms      |
| Candidate p95            | 4.384 ms      |
| Percent change           | +0.49%        |
| Absolute change          | +0.021 ms     |
| Percent threshold        | 10.00%        |
| Minimum regression floor | 1.000 ms      |
| Status                   | PASS          |

### Output

```text
Inference Runtime Regression Check
Stage: end_to_end_ms
Metric: p95_ms
Baseline: 4.362 ms
Candidate: 4.384 ms
Change: 0.49%
Absolute change: 0.021 ms
Percent threshold: 10.00%
Minimum regression floor: 1.000 ms
Status: PASS
```

## Controlled Regression Detection Demo

The candidate run injects a controlled 2.0 ms delay to make the regression path reproducible.

The regression checker is expected to report FAIL. The workflow succeeds only if that failure is detected.

### Summary

| Metric      |     Baseline |    Candidate |  Change |
| ----------- | -----------: | -----------: | ------: |
| Throughput  | 231.46 req/s | 157.55 req/s | -31.93% |
| p50 latency |     4.227 ms |     6.337 ms | +49.92% |
| p95 latency |     5.257 ms |     6.516 ms | +23.95% |
| p99 latency |     5.334 ms |     6.676 ms | +25.16% |

### Gate Result

| Check                     | Value                                                            |
| ------------------------- | ---------------------------------------------------------------- |
| Regression stage          | end_to_end_ms                                                    |
| Regression metric         | p95_ms                                                           |
| Baseline p95              | 5.257 ms                                                         |
| Candidate p95             | 6.516 ms                                                         |
| Percent change            | +23.95%                                                          |
| Absolute change           | +1.259 ms                                                        |
| Percent threshold         | 10.00%                                                           |
| Minimum regression floor  | 1.000 ms                                                         |
| Regression checker status | FAIL                                                             |
| Workflow result           | PASS, because the controlled regression was detected as expected |

### Output

```text
Inference Runtime Regression Check
Stage: end_to_end_ms
Metric: p95_ms
Baseline: 5.257 ms
Candidate: 6.516 ms
Change: 23.95%
Absolute change: 1.259 ms
Percent threshold: 10.00%
Minimum regression floor: 1.000 ms
Status: FAIL
Controlled regression was detected as expected.
```

# Inference Runtime Regression Gate

A small CI validation project for inference-style workloads.

This project benchmarks baseline and candidate inference runs, captures p50, p95, and p99 latency, measures throughput, and fails validation when candidate p95 latency crosses a configured regression threshold.

The goal is to model a lightweight version of the kind of regression gate that can protect performance-sensitive inference releases.

## What It Measures

| Area | Metrics |
| ---- | ------- |
| End-to-end latency | p50, p95, p99, mean, min, max |
| Throughput | requests per second |
| Request stages | preprocessing, model execution, controlled delay, postprocessing, serialization |
| Regression check | baseline vs candidate p95 latency |
| Validation result | pass or fail based on configured threshold |

## Validation Modes

| Mode | Purpose | Expected Result |
| ---- | ------- | --------------- |
| Pass gate | Compares baseline and candidate runs with no injected delay | PASS |
| Controlled fail demo | Injects a controlled 2.0 ms candidate delay | FAIL |

The controlled fail demo makes the regression path reproducible instead of relying on noisy local CPU variance.

## Latest Local Results

### Passing Gate

| Metric | Baseline | Candidate | Change |
| ---- | ----: | ----: | ----: |
| Throughput | 319.91 req/s | 432.95 req/s | +35.33% |
| p50 latency | 2.601 ms | 2.022 ms | -22.26% |
| p95 latency | 5.548 ms | 3.726 ms | -32.83% |
| p99 latency | 10.078 ms | 4.069 ms | -59.62% |

Status: PASS

### Controlled Failure Demo

| Metric | Baseline | Candidate | Change |
| ---- | ----: | ----: | ----: |
| Throughput | 419.76 req/s | 196.60 req/s | -53.16% |
| p50 latency | 2.264 ms | 4.682 ms | +106.80% |
| p95 latency | 2.933 ms | 6.676 ms | +127.64% |
| p99 latency | 3.669 ms | 11.082 ms | +202.04% |

Configured threshold: 10% p95 latency regression  
Observed regression: 127.64%  
Status: FAIL

## Project Structure

```text
.github/workflows/
  regression-gate.yml
  regression-gate-fail-demo.yml
  regression-gate-pass.yml

benchmarks/
  inference_benchmark.py

configs/
  regression_config.json

docs/
  README_RESULTS.md

results/
  baseline.json
  candidate.json

scripts/
  compare_regression.py
  run_fail_demo.ps1
  run_local_checks.ps1
  run_pass_gate.ps1
  smoke_test.py
  summarize_results.py

src/
  synthetic_model.py
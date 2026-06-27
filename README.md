# Inference Runtime Regression Gate

A small CI validation project for inference-style workloads.

This project benchmarks baseline and candidate inference runs, captures p50, p95, and p99 latency, measures throughput, and fails validation when candidate p95 latency crosses a configured regression threshold.

The goal is to model a lightweight version of a performance regression gate that can protect latency-sensitive inference releases.

## What It Does

| Area               | What is measured                                                                |
| ------------------ | ------------------------------------------------------------------------------- |
| End-to-end latency | p50, p95, p99, mean, min, max                                                   |
| Throughput         | Requests per second                                                             |
| Request stages     | Preprocessing, model execution, controlled delay, postprocessing, serialization |
| Regression check   | Baseline vs candidate p95 latency                                               |
| Noise handling     | Percent threshold plus minimum absolute regression floor                        |
| Validation result  | Pass or fail based on configured thresholds                                     |

## Regression Policy

The gate compares candidate p95 latency against baseline p95 latency.

```json
{
  "stage": "end_to_end_ms",
  "metric": "p95_ms",
  "max_regression_percent": 10.0,
  "min_regression_ms": 1.0
}
```

A candidate run fails only when both conditions are true:

1. Candidate p95 latency regresses by more than 10 percent.
2. Candidate p95 latency increases by more than 1.0 ms.

This avoids failing CI on tiny noisy deltas from shared runners while still catching meaningful regressions.

## Validation Modes

| Mode                                 | Purpose                                                     | Expected result                                                                     |
| ------------------------------------ | ----------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| Default regression gate              | Compares baseline and candidate runs with no injected delay | PASS                                                                                |
| Pass gate                            | Manual passing-path validation                              | PASS                                                                                |
| Controlled regression detection demo | Injects a controlled 2.0 ms candidate delay                 | Regression checker reports FAIL, workflow succeeds because the failure was detected |

The controlled regression demo makes the failure path reproducible instead of relying on noisy local CPU variance.

## Latest GitHub Actions Results

### Default Regression Gate

| Metric      |     Baseline |    Candidate | Change |
| ----------- | -----------: | -----------: | -----: |
| Throughput  | 233.24 req/s | 219.38 req/s | -5.94% |
| p50 latency |     4.260 ms |     4.537 ms | +6.50% |
| p95 latency |     4.357 ms |     4.648 ms | +6.66% |
| p99 latency |     5.215 ms |     4.844 ms | -7.11% |

Absolute p95 change: 0.290 ms
Percent threshold: 10.00%
Minimum regression floor: 1.000 ms
Status: PASS

### Controlled Regression Detection Demo

| Metric      |     Baseline |    Candidate |  Change |
| ----------- | -----------: | -----------: | ------: |
| Throughput  | 231.46 req/s | 157.55 req/s | -31.93% |
| p50 latency |     4.227 ms |     6.337 ms | +49.92% |
| p95 latency |     5.257 ms |     6.516 ms | +23.95% |
| p99 latency |     5.334 ms |     6.676 ms | +25.16% |

Absolute p95 change: 1.259 ms
Percent threshold: 10.00%
Minimum regression floor: 1.000 ms
Regression checker status: FAIL
Workflow result: PASS, because the controlled regression was detected as expected

Detailed benchmark output is available in [docs/BENCHMARK_RESULTS.md](docs/BENCHMARK_RESULTS.md).

## Run Locally

Install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

Run the passing gate:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_pass_gate.ps1
```

Run the controlled regression detection demo:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_fail_demo.ps1
```

Run both paths:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_local_checks.ps1
```

## CI Workflows

The default GitHub Actions workflow runs the passing regression gate on push and pull request.

The controlled regression detection workflow is manually triggered. It injects a controlled candidate slowdown, expects the regression checker to report FAIL, and succeeds only when that failure is detected.

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
  BENCHMARK_RESULTS.md

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
```

$ErrorActionPreference = "Stop"

Write-Host "===== Running passing inference regression gate ====="

$env:PYTHONPATH = "."

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\baseline.json `
  --controlled-delay-ms 0

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\candidate.json `
  --controlled-delay-ms 0

python scripts\compare_regression.py `
  --baseline results\baseline.json `
  --candidate results\candidate.json

python scripts\smoke_test.py `
  --baseline results\baseline.json `
  --candidate results\candidate.json

Write-Host ""
Write-Host "PASS gate completed successfully."
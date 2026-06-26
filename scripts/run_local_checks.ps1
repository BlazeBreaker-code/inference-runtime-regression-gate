$ErrorActionPreference = "Stop"

Write-Host "===== Running passing regression gate ====="

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

Write-Host ""
Write-Host "PASS gate completed successfully."
Write-Host ""

Write-Host "===== Running controlled failure demo ====="

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\baseline.json `
  --controlled-delay-ms 0

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\candidate.json `
  --controlled-delay-ms 0.20

python scripts\compare_regression.py `
  --baseline results\baseline.json `
  --candidate results\candidate.json

if ($LASTEXITCODE -eq 0) {
    Write-Host "ERROR: Controlled failure demo unexpectedly passed."
    exit 1
}

Write-Host ""
Write-Host "Controlled failure demo failed as expected."
Write-Host "Local checks completed successfully."
exit 0
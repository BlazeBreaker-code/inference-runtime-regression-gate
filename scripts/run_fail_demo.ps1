$ErrorActionPreference = "Stop"

Write-Host "===== Running controlled inference regression failure demo ====="

$env:PYTHONPATH = "."

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\baseline.json `
  --controlled-delay-ms 0

python benchmarks\inference_benchmark.py `
  --device cpu `
  --output results\candidate.json `
  --controlled-delay-ms 2.0

$ErrorActionPreference = "Continue"

python scripts\compare_regression.py `
  --baseline results\baseline.json `
  --candidate results\candidate.json

$exitCode = $LASTEXITCODE
$ErrorActionPreference = "Stop"

if ($exitCode -eq 0) {
    Write-Host "ERROR: Controlled failure demo unexpectedly passed."
    exit 1
}

python scripts\smoke_test.py `
  --baseline results\baseline.json `
  --candidate results\candidate.json

Write-Host ""
Write-Host "Controlled failure demo failed as expected."
exit 0
# BID OWL Windows one-command local QA; use only from an authorized checkout.
# Synthetic fixtures/temp DBs only. No external API, customer data or deployment.
# Output JSON is kept locally under backend/qa_results/ (Git ignored).
param([switch]$Benchmark)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
  Write-Host 'BID OWL: measured full Python tests, synthetic smoke and JS syntax'
  python --version
  if ($LASTEXITCODE -ne 0) { throw 'Python 3.11+ unavailable' }
  if ($Benchmark) {
    Write-Host 'Optional extra: synthetic 10,000-bid local benchmark'
    python qa_runner.py --benchmark
  } else {
    python qa_runner.py
  }
  if ($LASTEXITCODE -ne 0) { throw 'BID OWL QA failed; inspect saved local JSON and console diagnostics' }
  Write-Host 'Actual invoked checks passed; inspect local qa_results JSON for counts and skipped checks.'
  Write-Host 'Not validated: native Windows Excel/PDF appearance, Chrome/Edge visual UX, real tenders.'
} finally {
  Pop-Location
}

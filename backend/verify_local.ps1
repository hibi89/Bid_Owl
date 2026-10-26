# BID OWL local Windows verification. Run ONLY on an authorized private checkout.
# This never modifies customer DBs: smoke_local.py uses synthetic fixture/temp files.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$start = Get-Date
Push-Location $PSScriptRoot
try {
  Write-Host 'BID OWL local QA: actual source checkout / all unittest cases'
  python --version
  if ($LASTEXITCODE -ne 0) { throw 'Python unavailable' }
  python -m unittest discover -s tests -v
  if ($LASTEXITCODE -ne 0) { throw 'Python unittest FAILED; stop without claiming PASS' }
  Write-Host 'BID OWL local QA: synthetic end-to-end smoke'
  python smoke_local.py
  if ($LASTEXITCODE -ne 0) { throw 'Synthetic E2E FAILED; stop without claiming PASS' }
  $node = Get-Command node -ErrorAction SilentlyContinue
  if ($null -ne $node) {
    node --check ui/ui.js
    if ($LASTEXITCODE -ne 0) { throw 'JavaScript syntax FAILED' }
  } else {
    Write-Warning 'Node not installed; JavaScript syntax CHECK SKIPPED (not PASS)'
  }
  $duration = (Get-Date) - $start
  Write-Host ('LOCAL_QA_COMPLETED: all invoked checks passed, elapsed {0:N1} sec' -f $duration.TotalSeconds)
  Write-Host 'Not checked: native Excel/PDF visual rendering, browser layout, real tender data or installation.'
} finally {
  Pop-Location
}

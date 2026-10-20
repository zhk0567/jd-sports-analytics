param([string]$Python = ".venv\Scripts\python.exe")
$ErrorActionPreference = "Stop"
$steps = @(
  "scripts/t2_generate_data.py",
  "scripts/t2_build_warehouse.py",
  "scripts/t2_train_models.py",
  "scripts/t2_generate_assets.py",
  "scripts/t2_generate_docs.py",
  "scripts/t2_validate.py"
)
foreach ($step in $steps) {
  Write-Host "==> $step"
  & $Python $step
  if ($LASTEXITCODE -ne 0) { throw "step failed: $step" }
}
Write-Host "pipeline finished: http://127.0.0.1:5000"

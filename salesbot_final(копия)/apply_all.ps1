$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

python --version | Out-Null

Write-Host "[run] autobuilder/merge_apply_all.py"
python ".\autobuilder\merge_apply_all.py"

Write-Host "`n[ok] Parts applied & merged. You can run: python -m uvicorn api.main:app --reload --port 8080"

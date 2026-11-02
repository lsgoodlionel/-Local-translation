param([string]$From = "en", [string]$To = "zh")
$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Venv = Join-Path $RepoRoot ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"
if (-not (Test-Path -LiteralPath $Python)) { python -m venv $Venv }
& $Python -m pip install --upgrade pip
& $Python -m pip install -r (Join-Path $RepoRoot "requirements.txt")
& $Python (Join-Path $RepoRoot "local-text-translation\scripts\install_model.py") --from $From --to $To
Write-Host "Ready. Translation runs locally with:"
Write-Host "  $Python local-text-translation\scripts\local_translate.py INPUT -o OUTPUT --from $From --to $To"


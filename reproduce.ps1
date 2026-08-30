$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

python -B "$Root\verification\verify_corank2_global.py"
python -B "$Root\verification\verify_corank2_global_independent.py"

$Paper = Join-Path $Root "paper"
$Build = Join-Path $Paper "build"
New-Item -ItemType Directory -Force -Path $Build | Out-Null
& pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=$Build (Join-Path $Paper "main.tex")
& pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=$Build (Join-Path $Paper "main.tex")
Copy-Item -Force (Join-Path $Build "main.pdf") (Join-Path $Paper "main.pdf")

python -B "$Root\tools\verify_hashes.py"
Write-Host "PASS_APPROVAL_CORE_SPARSE_DISAPPROVAL_RELEASE"

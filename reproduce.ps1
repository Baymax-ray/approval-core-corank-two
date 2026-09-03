$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Native {
    param(
        [Parameter(Mandatory = $true)][string]$Label,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    & $Command
    $exitCode = $LASTEXITCODE
    if ($exitCode -ne 0) {
        throw "$Label failed with exit code $exitCode"
    }
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path

Invoke-Native "primary exact verifier" {
    & python -B "$Root\verification\verify_corank2_global.py"
}
Invoke-Native "independent exact verifier" {
    & python -B "$Root\verification\verify_corank2_global_independent.py"
}

$pdfTeXOutput = & pdflatex --version
if ($LASTEXITCODE -ne 0) {
    throw "pdflatex version check failed with exit code $LASTEXITCODE"
}
$pdfTeXVersion = [string]($pdfTeXOutput | Select-Object -First 1)
$expectedPdfTeX = "pdfTeX 3.141592653-2.6-1.40.29 (TeX Live 2026)"
if (-not $pdfTeXVersion.Contains($expectedPdfTeX)) {
    throw "Byte-identical PDF replay requires $expectedPdfTeX; found $pdfTeXVersion"
}

$Paper = Join-Path $Root "paper"
$Build = Join-Path $Paper "build"
if (Test-Path -LiteralPath $Build) {
    Remove-Item -LiteralPath $Build -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $Build | Out-Null
$env:SOURCE_DATE_EPOCH = "1788048000"
$env:FORCE_SOURCE_DATE = "1"

Push-Location $Paper
try {
    Invoke-Native "pdflatex pass 1" {
        & pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
    }
    Invoke-Native "bibtex" {
        & bibtex build/main
    }
    Invoke-Native "pdflatex pass 2" {
        & pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
    }
    Invoke-Native "pdflatex pass 3" {
        & pdflatex -interaction=nonstopmode -halt-on-error -file-line-error -output-directory=build main.tex
    }
}
finally {
    Pop-Location
}

$releasePdf = Join-Path $Paper "main.pdf"
$builtPdf = Join-Path $Build "main.pdf"
if ((Get-FileHash $builtPdf).Hash -ne (Get-FileHash $releasePdf).Hash) {
    throw "Recompiled PDF differs from the release PDF"
}

Invoke-Native "SHA-256 manifest verification" {
    & python -B "$Root\tools\verify_hashes.py"
}
Write-Host "PASS_APPROVAL_CORE_SPARSE_DISAPPROVAL_RELEASE"

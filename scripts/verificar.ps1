param([switch]$ComNavegador)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $projectPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $projectPython)) { throw "Execute scripts/preparar.ps1 primeiro." }
    & $projectPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw "Dependencias inconsistentes." }
    & $projectPython -m ruff check .
    if ($LASTEXITCODE -ne 0) { throw "Falha na verificacao de codigo." }
    & $projectPython -m ruff format --check .
    if ($LASTEXITCODE -ne 0) { throw "Formatacao pendente: execute python -m ruff format . com o Python da .venv." }
    & $projectPython manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Falha na verificacao Django." }
    & $projectPython manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw "Migracoes pendentes." }
    & $projectPython manage.py test tests --verbosity 2
    if ($LASTEXITCODE -ne 0) { throw "Falha nos testes da base." }
    if ($ComNavegador) {
        & $projectPython manage.py test tests.browser_check tests.siat_browser_check tests.operador_browser_check tests.whatsapp_browser_check tests.desktop_browser_check tests.whatsapp_desktop_browser_check tests.siat_desktop_dialog_check tests.retorno_painel_browser_check tests.painel_resultado_browser_check --verbosity 2
        if ($LASTEXITCODE -ne 0) { throw "Falha no teste local com Chromium." }
    }
    Write-Host "Verificacao concluida. Estes testes nao comprovam o funcionamento das integracoes reais."
}
finally { Pop-Location }

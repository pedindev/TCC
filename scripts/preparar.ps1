param(
    [string]$Python = "py",
    [switch]$SemNavegador
)
$ErrorActionPreference = "Stop"
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $projectPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $projectPython)) {
        if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
            throw "Python nao encontrado. Instale Python 3.12 ou informe -Python com o caminho do executavel."
        }
        if ($Python -eq "py") { & $Python -3.12 -m venv .venv }
        else { & $Python -m venv .venv }
        if ($LASTEXITCODE -ne 0) { throw "Falha ao criar o ambiente virtual." }
    }
    & $projectPython -c "import sys; assert sys.version_info[:2] == (3, 12), 'Este ambiente foi preparado para Python 3.12.'"
    if ($LASTEXITCODE -ne 0) { throw "Versao de Python incompatível com o ambiente validado." }
    & $projectPython -m pip install --disable-pip-version-check --no-cache-dir -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw "Falha ao instalar dependencias. Verifique a conexao e tente novamente." }
    & $projectPython scripts/configurar_local.py
    if ($LASTEXITCODE -ne 0) { throw "Falha na configuracao local." }
    & $projectPython manage.py migrate --noinput
    if ($LASTEXITCODE -ne 0) { throw "Falha nas migracoes." }
    if (-not $SemNavegador) {
        $previousBrowserPath = $env:PLAYWRIGHT_BROWSERS_PATH
        try {
            $env:PLAYWRIGHT_BROWSERS_PATH = Join-Path $projectRoot ".local\browsers"
            & $projectPython -m playwright install chromium
            if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar Chromium. Execute preparar.ps1 novamente." }
        }
        finally { $env:PLAYWRIGHT_BROWSERS_PATH = $previousBrowserPath }
    }
    & $projectPython manage.py check
    if ($LASTEXITCODE -ne 0) { throw "A verificacao Django encontrou problemas." }
    Write-Host "Ambiente preparado. O painel local abre diretamente, sem criar conta."
    Write-Host "Depois execute .\scripts\verificar.ps1 e .\scripts\iniciar.ps1"
}
finally { Pop-Location }

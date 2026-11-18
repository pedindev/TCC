param([ValidateSet('preparacao', 'simulacao', 'navegador')][string]$Modo = 'navegador')
$ErrorActionPreference = "Stop"
if ($Modo) { $env:APP_MODE = $Modo }
$projectRoot = Split-Path -Parent $PSScriptRoot
Push-Location $projectRoot
try {
    $portaOcupada = $false
    $clientePainel = [System.Net.Sockets.TcpClient]::new()
    try { $clientePainel.Connect('127.0.0.1', 8000); $portaOcupada = $true } catch { }
    finally { $clientePainel.Dispose() }
    if ($portaOcupada) {
        throw 'Ja existe um painel na porta 8000. Pare o servidor antigo com Ctrl+C antes de iniciar esta versao.'
    }
    $projectPython = Join-Path $projectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $projectPython)) { throw "Execute scripts/preparar.ps1 primeiro." }
    & $projectPython manage.py check
    if ($LASTEXITCODE -ne 0) { throw "Corrija a configuracao antes de iniciar." }
    if ($Modo -eq 'navegador') {
        Write-Host 'O painel identifica o navegador em que foi aberto e verifica suas abas pelo Windows.'
        Write-Host 'Ao consultar, aguarde sem usar mouse ou teclado. O SIAT sera trazido para frente.'
        Write-Host 'Nenhum navegador ou site sera aberto automaticamente.'
        Write-Host 'Painel: http://127.0.0.1:8000/'
    }
    # --insecure serve apenas os arquivos estaticos com DEBUG=0. Uso exclusivo em loopback.
    # Sem autoreload: uma unica instancia do processo Django.
    & $projectPython manage.py runserver 127.0.0.1:8000 --noreload --insecure
    if ($LASTEXITCODE -ne 0) { throw "O servidor foi encerrado com erro. Confira se a porta 8000 esta livre." }
}
finally { Pop-Location }

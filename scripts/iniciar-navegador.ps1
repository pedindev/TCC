param([string]$Executavel = '')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
try {
    $conexao = Invoke-RestMethod -Uri 'http://127.0.0.1:9222/json/version' -TimeoutSec 2
    if ($conexao.webSocketDebuggerUrl) {
        Write-Host 'Reutilizando o navegador de atendimento aberto.'
        return
    }
} catch { }
if (-not $Executavel) {
    $opcoes = @(
        "$env:ProgramFiles\BraveSoftware\Brave-Browser\Application\brave.exe",
        "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
        "$env:LOCALAPPDATA\BraveSoftware\Brave-Browser\Application\brave.exe"
    )
    $Executavel = $opcoes | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
}
if (-not $Executavel -or -not (Test-Path -LiteralPath $Executavel)) {
    throw 'Informe o caminho do Chrome ou Brave em -Executavel.'
}
$perfil = Join-Path $projectRoot '.local\navegador-atendimento'
Write-Host 'Abrindo o painel no navegador de atendimento. Abra SIAT e WhatsApp pelos links do painel.'
Write-Host 'Este perfil guarda os cookies do navegador. Nao compartilhe a pasta .local.'
# Janela interativa solicitada por quem executa este script. Não copia perfis existentes.
$argumentos = @(
    '--remote-debugging-address=127.0.0.1',
    '--remote-debugging-port=9222',
    ('"--user-data-dir=' + $perfil + '"'),
    '--new-window',
    'http://127.0.0.1:8000/'
)
# A janela precisa ficar visível para o operador realizar os dois logins.
Start-Process -FilePath $Executavel -ArgumentList $argumentos -WindowStyle Normal
$prazo = (Get-Date).AddSeconds(15)
do {
    try {
        $conexao = Invoke-RestMethod -Uri 'http://127.0.0.1:9222/json/version' -TimeoutSec 1
        if ($conexao.webSocketDebuggerUrl) { return }
    } catch { }
    Start-Sleep -Milliseconds 250
} while ((Get-Date) -lt $prazo)
throw 'O navegador abriu, mas a conexao nao respondeu. Feche somente a janela de atendimento e inicie novamente.'

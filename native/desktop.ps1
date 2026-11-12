param([int]$ProcessoTeste = 0, [switch]$VerificarCompilacao)
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
[Console]::InputEncoding = $utf8
[Console]::OutputEncoding = $utf8
$OutputEncoding = $utf8
try {
    $assemblies = @('UIAutomationClient','UIAutomationTypes','WindowsBase','System.Windows.Forms') |
        ForEach-Object { [Reflection.Assembly]::LoadWithPartialName($_).Location }
    $assemblies += [System.Uri].Assembly.Location
    Add-Type -TypeDefinition (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Desktop.cs') -Raw -Encoding UTF8) -ReferencedAssemblies $assemblies
    [MvpDesktop]::ProcessoTeste = $ProcessoTeste
    if ($VerificarCompilacao) {
        foreach ($rotuloTeste in @('Digite uma mensagem','Digite uma mensagem para Contato ficticio','Digite uma mensagem: exemplo','Type a message to Fictional contact','Mensagem')) {
            if (-not [MvpDesktop]::RotuloCompositor($rotuloTeste)) { throw 'Rotulo valido recusado.' }
        }
        foreach ($rotuloTeste in @('Pesquisar mensagens','Mensagem de voz','Digite uma mensagemXYZ','Search','')) {
            if ([MvpDesktop]::RotuloCompositor($rotuloTeste)) { throw 'Rotulo indevido aceito.' }
        }
        Write-Output 'Compilacao e testes de rotulos OK'; exit 0
    }
    while ($null -ne ($linha = [Console]::ReadLine())) {
        $pedido = $null
        try {
            $pedido = $linha | ConvertFrom-Json
            $dados = [MvpDesktop]::Executar([string]$pedido.acao, [string]$pedido.referencia, [string]$pedido.valor, [long]$pedido.limite)
            $resposta = @{id=$pedido.id; dados=$dados}
        } catch {
            $resposta = @{id=$pedido.id; dados=@{resultado='falha'}}
        }
        [Console]::WriteLine(($resposta | ConvertTo-Json -Depth 6 -Compress))
        $pedido = $null; $linha = $null; $dados = $null; $resposta = $null
    }
} catch { if ($VerificarCompilacao) { Write-Error $_ }; exit 1 }

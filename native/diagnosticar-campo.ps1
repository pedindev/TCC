$ErrorActionPreference = 'Stop'
$assemblies = @('UIAutomationClient','UIAutomationTypes','WindowsBase','System.Windows.Forms') |
    ForEach-Object { [Reflection.Assembly]::LoadWithPartialName($_).Location }
$assemblies += [System.Uri].Assembly.Location
Add-Type -TypeDefinition (Get-Content -LiteralPath (Join-Path $PSScriptRoot 'Desktop.cs') -Raw -Encoding UTF8) -ReferencedAssemblies $assemblies
[MvpDesktop]::DiagnosticarCampoWhatsApp() | ConvertTo-Json -Depth 4 -Compress

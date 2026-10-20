param([string]$Datax = "datax.py")
$ErrorActionPreference = "Stop"
Get-ChildItem config/import/*.json | ForEach-Object {
  Write-Host "[DataX] $($_.FullName)"
  python $Datax $_.FullName
}

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$worldPath = "D:\Minecraft Worlds\saves\city1mansion ai"

$env:MINECRAFT_WORLD_PATH = $worldPath
Set-Location $projectRoot

Write-Host "Starting Minecraftia AI Civilization Simulator..."
Write-Host "World path: $worldPath"

python -m src.main

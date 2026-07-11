Param(
    [string]$WorldPath = $env:MINECRAFT_WORLD_PATH,
    [int]$Batch = 500,
    [double]$Pause = 0.25
)

if (-not $WorldPath) {
    $WorldPath = "D:\Minecraft Worlds\saves\city1mansion ai"
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Definition
Push-Location $root
try {
    if (Test-Path "..\.venv\Scripts\Activate.ps1") {
        & "..\.venv\Scripts\Activate.ps1"
    }
    python .\seed_population.py --world-path "$WorldPath" --batch $Batch --pause $Pause
} finally {
    Pop-Location
}

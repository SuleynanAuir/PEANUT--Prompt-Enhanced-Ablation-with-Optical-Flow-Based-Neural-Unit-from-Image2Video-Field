# Quick Visualization Script
param(
    [string]$ExperimentName = "exp1",
    [int[]]$FrameNumbers = @(1, 5, 10, 15, 20)
)

$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"
$ExperimentDir = Join-Path $ProjectRoot "experiment\$ExperimentName"
$ResultsDir = Join-Path $ExperimentDir "samwise_results"
$VisDir = Join-Path $ExperimentDir "visualizations"

if (-not (Test-Path $VisDir)) {
    New-Item -ItemType Directory -Force -Path $VisDir | Out-Null
}

Write-Host "Generating visualizations..." -ForegroundColor Cyan

# Find test directories
$testDirs = Get-ChildItem -Path $ResultsDir -Directory | Where-Object { 
    $_.Name -match "threshold_|model_|window_" 
}

if ($testDirs.Count -eq 0) {
    Write-Host "No test results found" -ForegroundColor Red
    exit 1
}

# Find source frames
$sourceFrames = Join-Path $ProjectRoot "SAMWISE\frames_alita1_test"
if (-not (Test-Path $sourceFrames)) {
    $sourceFrames = Join-Path $ProjectRoot "SAMWISE\demo_output\the_alita"
}

# Create config
$config = @{
    test_dirs = @($testDirs | ForEach-Object { $_.FullName })
    frame_numbers = $FrameNumbers
    output_dir = $VisDir
    source_frames_dir = $sourceFrames
} | ConvertTo-Json -Depth 10

$configPath = Join-Path $VisDir "config.json"
$Utf8NoBomEncoding = New-Object System.Text.UTF8Encoding $False
[System.IO.File]::WriteAllLines($configPath, $config, $Utf8NoBomEncoding)

# Run Python
$pythonScript = Join-Path $ProjectRoot "experiment\simple_visualize.py"
conda run -n e2fgvi-project python $pythonScript $configPath

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nVisualization complete!" -ForegroundColor Green
    Write-Host "Output: $VisDir" -ForegroundColor Yellow
    
    # Open first image
    $firstImg = Get-ChildItem -Path $VisDir -Filter "comparison_*.png" | Select-Object -First 1
    if ($firstImg) {
        Start-Process $firstImg.FullName
    }
}

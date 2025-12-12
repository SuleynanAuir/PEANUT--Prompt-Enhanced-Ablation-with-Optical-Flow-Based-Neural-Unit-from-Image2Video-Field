<#
.SYNOPSIS
    快速测试完整视频修复流水线
    
.DESCRIPTION
    一键运行 SAMWISE → E2FGVI → BasicVSR++ Restore → Denoise 全流程
    使用 the_way_of_water 或 Zoopic 视频进行测试
    
.PARAMETER VideoName
    测试视频名称（不含扩展名），默认 the_way_of_water
    
.PARAMETER UseCPU
    强制使用 CPU 运行 BasicVSR++（避免 GPU OOM）
    
.PARAMETER SegmentSize
    BasicVSR++ 分段处理大小（0=不分段），默认 6
    
.EXAMPLE
    .\RUN_PIPELINE_TEST.ps1
    .\RUN_PIPELINE_TEST.ps1 -VideoName Zoopic
    .\RUN_PIPELINE_TEST.ps1 -UseCPU -SegmentSize 4
#>

param(
    [string]$VideoName = "the_way_of_water",
    [switch]$UseCPU,
    [int]$SegmentSize = 6
)

$ErrorActionPreference = "Stop"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host " Complete Video Inpainting Pipeline Test" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Test video: $VideoName.mp4" -ForegroundColor Yellow
Write-Host "GPU mode: $(if ($UseCPU) { 'CPU forced' } else { 'GPU first (CPU fallback)' })" -ForegroundColor Yellow
Write-Host "Segment size: $SegmentSize frames" -ForegroundColor Yellow
Write-Host "========================================`n" -ForegroundColor Cyan

# Clean old outputs
Write-Host "Cleaning old outputs..." -ForegroundColor Gray
Remove-Item -Path "frames_package","mask_package","inpaint_package","restore_package","denoise_package","results" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "Cleaned old folders`n" -ForegroundColor Green

# Check prompt_list.json
$promptFile = "raw_prompt\prompt_list.json"
if (-not (Test-Path $promptFile)) {
    Write-Host "Error: prompt_list.json not found at $promptFile" -ForegroundColor Red
    Write-Host "Please create a JSON file with this format:" -ForegroundColor Yellow
    Write-Host '[' -ForegroundColor Gray
    Write-Host '  { "video_name": "the_way_of_water.mp4", "remove_prompt": "the man" },' -ForegroundColor Gray
    Write-Host '  { "video_name": "Zoopic.mp4", "remove_prompt": "the carrot" }' -ForegroundColor Gray
    Write-Host ']' -ForegroundColor Gray
    exit 1
}

# Check video file
$videoFile = "raw_video\$VideoName.mp4"
if (-not (Test-Path $videoFile)) {
    Write-Host "Error: video file not found: $videoFile" -ForegroundColor Red
    Write-Host "Available videos:" -ForegroundColor Yellow
    Get-ChildItem -Path "raw_video" -Filter *.mp4 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
    exit 1
}

# Run main pipeline
Write-Host "Starting pipeline...`n" -ForegroundColor Cyan
try {
    if ($UseCPU) {
        & ".\video_inpaint_pipeline_en.ps1" -SegmentSize $SegmentSize -ForceCPU
    } else {
        & ".\video_inpaint_pipeline_en.ps1" -SegmentSize $SegmentSize
    }
    
    Write-Host "`n========================================" -ForegroundColor Green
    Write-Host " Pipeline execution complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    
    # Show result statistics
    Write-Host "`nResult file statistics:" -ForegroundColor Cyan
    
    $resultDirs = @(
        @{Name="Mask Video"; Path="mask_package\${VideoName}_mask_video"},
        @{Name="Inpaint Video"; Path="inpaint_package\${VideoName}_inpaint_video"},
        @{Name="Restore Video"; Path="restore_package\${VideoName}_restore_video"},
        @{Name="Denoise Video"; Path="denoise_package\${VideoName}_denoise_video"},
        @{Name="Final Result"; Path="results\${VideoName}_result"}
    )
    
    foreach ($dir in $resultDirs) {
        if (Test-Path $dir.Path) {
            $files = Get-ChildItem -Path $dir.Path -File
            $totalSize = ($files | Measure-Object -Property Length -Sum).Sum / 1MB
            $sizeMB = "{0:N2}" -f $totalSize
            Write-Host "  $($dir.Name): $($files.Count) files, $sizeMB MB" -ForegroundColor Gray
            
            # List video files
            $videos = $files | Where-Object { $_.Extension -eq '.mp4' }
            foreach ($v in $videos) {
                $vsize = $v.Length / 1MB
                $vsizeMB = "{0:N2}" -f $vsize
                Write-Host "    -> $($v.Name) ($vsizeMB MB)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "  $($dir.Name): Not generated" -ForegroundColor Red
        }
    }
    
    # Quick preview command
    $finalVideo = "results\${VideoName}_result\${VideoName}_denoise.mp4"
    if (Test-Path $finalVideo) {
        Write-Host "`nFinal video location:" -ForegroundColor Cyan
        Write-Host "  $(Resolve-Path $finalVideo)" -ForegroundColor Green
        Write-Host "`nPlay command:" -ForegroundColor Cyan
        Write-Host "  Start-Process `"$finalVideo`"" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "`n========================================" -ForegroundColor Red
    Write-Host " Pipeline execution failed" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Yellow
    Write-Host "`nDebug suggestions:" -ForegroundColor Cyan
    Write-Host "  1. Check conda environments are activated" -ForegroundColor Gray
    Write-Host "  2. Check output directories for content" -ForegroundColor Gray
    Write-Host "  3. If GPU OOM, use -UseCPU parameter" -ForegroundColor Gray
    Write-Host "  4. Reduce -SegmentSize (e.g. 4 or 2)" -ForegroundColor Gray
    exit 1
}

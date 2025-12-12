<#
.SYNOPSIS
    批量处理多个视频的脚本
    
.DESCRIPTION
    支持批量处理多个视频文件，使用相同的处理参数
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$InputDir,
    
    [Parameter(Mandatory=$true)]
    [string]$TextPrompt,
    
    [string]$OutputDir = "batch_output",
    [string]$FilePattern = "*.mp4",
    
    [int]$NeighborStride = 3,
    [int]$MaxLoadFrames = 8,
    [string]$DenoiseMethod = "nlm",
    [int]$DenoiseStrength = 5
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PipelineScript = Join-Path $ScriptDir "video_inpaint_pipeline.ps1"

if (-not (Test-Path $PipelineScript)) {
    Write-Error "找不到主脚本: $PipelineScript"
    exit 1
}

if (-not (Test-Path $InputDir)) {
    Write-Error "输入目录不存在: $InputDir"
    exit 1
}

$Videos = Get-ChildItem -Path $InputDir -Filter $FilePattern

if ($Videos.Count -eq 0) {
    Write-Error "未找到符合条件的视频文件: $FilePattern"
    exit 1
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 批量处理视频" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "输入目录: $InputDir"
Write-Host "文件模式: $FilePattern"
Write-Host "找到视频: $($Videos.Count) 个"
Write-Host "文本提示: $TextPrompt"
Write-Host ""

$ProcessedCount = 0
$FailedCount = 0
$StartTime = Get-Date

foreach ($Video in $Videos) {
    $CurrentNum = $ProcessedCount + $FailedCount + 1
    
    Write-Host ""
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    Write-Host " [$CurrentNum/$($Videos.Count)] 处理: $($Video.Name)" -ForegroundColor Yellow
    Write-Host "----------------------------------------" -ForegroundColor Yellow
    
    try {
        & $PipelineScript `
            -InputVideo $Video.FullName `
            -TextPrompt $TextPrompt `
            -OutputDir $OutputDir `
            -NeighborStride $NeighborStride `
            -MaxLoadFrames $MaxLoadFrames `
            -DenoiseMethod $DenoiseMethod `
            -DenoiseStrength $DenoiseStrength `
            -ErrorAction Stop
        
        $ProcessedCount++
        Write-Host "✓ 完成: $($Video.Name)" -ForegroundColor Green
    }
    catch {
        $FailedCount++
        Write-Host "✗ 失败: $($Video.Name)" -ForegroundColor Red
        Write-Host "错误: $_" -ForegroundColor Red
        
        # 记录错误到日志文件
        $ErrorLog = Join-Path $OutputDir "errors.log"
        $ErrorMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') - $($Video.Name): $_"
        Add-Content -Path $ErrorLog -Value $ErrorMessage
    }
}

$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " 批量处理完成" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "总计视频: $($Videos.Count)"
Write-Host "成功处理: $ProcessedCount" -ForegroundColor Green
Write-Host "失败数量: $FailedCount" -ForegroundColor $(if ($FailedCount -eq 0) { "Green" } else { "Red" })
Write-Host "总耗时: $($Duration.ToString('hh\:mm\:ss'))"
Write-Host "输出目录: $OutputDir"
Write-Host ""

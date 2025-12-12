<#
.SYNOPSIS
    检查 SuperVideo-inpaint 环境配置
    
.DESCRIPTION
    验证所有必需的文件夹、Conda 环境和模型文件是否就绪
#>

$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " SuperVideo-inpaint 环境检查" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$allGood = $true

# 检查项目文件夹
Write-Host "检查项目文件夹..." -ForegroundColor Yellow
$requiredDirs = @(
    "SAMWISE",
    "E2FGVI_Project", 
    "BasicVSR_PlusPlus",
    "raw_video"
)

foreach ($dir in $requiredDirs) {
    $path = Join-Path $ProjectRoot $dir
    if (Test-Path $path) {
        Write-Host "  ✓ $dir" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $dir (未找到)" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""

# 检查主脚本
Write-Host "检查主脚本..." -ForegroundColor Yellow
$mainScript = Join-Path $ProjectRoot "video_inpaint_pipeline.ps1"
if (Test-Path $mainScript) {
    Write-Host "  ✓ video_inpaint_pipeline.ps1" -ForegroundColor Green
} else {
    Write-Host "  ✗ video_inpaint_pipeline.ps1 (未找到)" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# 检查 Conda 环境
Write-Host "检查 Conda 环境..." -ForegroundColor Yellow

$condaEnvs = @("samwise", "e2fgvi-project", "basicvsrpp-demo")

try {
    $envList = conda env list 2>&1 | Out-String
    
    foreach ($env in $condaEnvs) {
        if ($envList -match $env) {
            Write-Host "  ✓ $env" -ForegroundColor Green
        } else {
            Write-Host "  ✗ $env (未创建)" -ForegroundColor Red
            $allGood = $false
        }
    }
} catch {
    Write-Host "  ✗ 无法检查 Conda 环境 (Conda 未安装或未配置)" -ForegroundColor Red
    $allGood = $false
}

Write-Host ""

# 检查关键模型文件
Write-Host "检查模型文件..." -ForegroundColor Yellow

$e2fgviCheckpoint = Join-Path $ProjectRoot "E2FGVI_Project\release_model\E2FGVI-HQ-CVPR22.pth"
if (Test-Path $e2fgviCheckpoint) {
    Write-Host "  ✓ E2FGVI 模型" -ForegroundColor Green
} else {
    Write-Host "  ✗ E2FGVI 模型 (未找到)" -ForegroundColor Red
    Write-Host "    路径: $e2fgviCheckpoint" -ForegroundColor Gray
    $allGood = $false
}

$basicvsrCheckpoint = Join-Path $ProjectRoot "BasicVSR_PlusPlus\checkpoints\basicvsr_plusplus_reds4.pth"
if (Test-Path $basicvsrCheckpoint) {
    Write-Host "  ✓ BasicVSR++ 模型" -ForegroundColor Green
} else {
    Write-Host "  ✗ BasicVSR++ 模型 (未找到)" -ForegroundColor Red
    Write-Host "    路径: $basicvsrCheckpoint" -ForegroundColor Gray
    $allGood = $false
}

Write-Host ""

# 检查 raw_video 文件夹中的视频
Write-Host "检查输入视频..." -ForegroundColor Yellow
$rawVideoDir = Join-Path $ProjectRoot "raw_video"
$videos = Get-ChildItem -Path $rawVideoDir -Filter "*.mp4" -ErrorAction SilentlyContinue

if ($videos.Count -gt 0) {
    Write-Host "  ✓ 找到 $($videos.Count) 个视频文件" -ForegroundColor Green
    foreach ($video in $videos) {
        $sizeKB = [math]::Round($video.Length / 1KB, 2)
        Write-Host "    - $($video.Name) ($sizeKB KB)" -ForegroundColor Gray
    }
} else {
    Write-Host "  ⚠ raw_video 文件夹为空" -ForegroundColor Yellow
    Write-Host "    请将视频文件放入: $rawVideoDir" -ForegroundColor Gray
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host " ✓ 环境检查完成 - 一切就绪!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "您可以运行:" -ForegroundColor Cyan
    Write-Host "  .\video_inpaint_pipeline.ps1 -VideoPath `"your_video.mp4`" -TextPrompt `"the object`"" -ForegroundColor White
} else {
    Write-Host " ✗ 环境检查失败 - 请解决以上问题" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Cyan
}

Write-Host ""

<#
.SYNOPSIS
    视频帧提取和合成辅助工具
    
.DESCRIPTION
    提供视频帧提取、合成等辅助功能
#>

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet('extract', 'compose', 'info')]
    [string]$Action,
    
    [string]$InputPath,
    [string]$OutputPath,
    [int]$FPS = 30,
    [string]$Format = "png",
    [string]$Quality = "high"
)

# ============================================
# 提取视频帧
# ============================================
function Extract-VideoFrames {
    param(
        [string]$VideoPath,
        [string]$OutputDir,
        [int]$FPS
    )
    
    if (-not (Test-Path $VideoPath)) {
        Write-Error "视频文件不存在: $VideoPath"
        return
    }
    
    New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null
    
    Write-Host "正在提取视频帧..." -ForegroundColor Cyan
    Write-Host "输入: $VideoPath"
    Write-Host "输出: $OutputDir"
    Write-Host "FPS: $FPS"
    
    # 使用 ffmpeg 提取帧
    $ffmpegCmd = "ffmpeg -i `"$VideoPath`" -vf fps=$FPS `"$OutputDir\frame_%05d.png`""
    
    try {
        Invoke-Expression $ffmpegCmd
        
        $frameCount = (Get-ChildItem -Path $OutputDir -Filter "*.png").Count
        Write-Host "✓ 成功提取 $frameCount 帧" -ForegroundColor Green
    }
    catch {
        Write-Error "提取失败: $_"
    }
}

# ============================================
# 合成视频
# ============================================
function Compose-VideoFromFrames {
    param(
        [string]$FramesDir,
        [string]$OutputVideo,
        [int]$FPS,
        [string]$Quality
    )
    
    if (-not (Test-Path $FramesDir)) {
        Write-Error "帧目录不存在: $FramesDir"
        return
    }
    
    Write-Host "正在合成视频..." -ForegroundColor Cyan
    Write-Host "输入: $FramesDir"
    Write-Host "输出: $OutputVideo"
    Write-Host "FPS: $FPS"
    
    # 根据质量设置 CRF 值
    $crf = switch ($Quality) {
        "low" { 28 }
        "medium" { 23 }
        "high" { 18 }
        "best" { 15 }
        default { 23 }
    }
    
    # 查找帧文件的命名模式
    $firstFrame = Get-ChildItem -Path $FramesDir -Filter "*.png" | Select-Object -First 1
    if (-not $firstFrame) {
        Write-Error "未找到帧文件"
        return
    }
    
    # 使用 ffmpeg 合成视频
    $pattern = Join-Path $FramesDir "frame_%05d.png"
    $ffmpegCmd = "ffmpeg -framerate $FPS -i `"$pattern`" -c:v libx264 -crf $crf -pix_fmt yuv420p `"$OutputVideo`""
    
    try {
        Invoke-Expression $ffmpegCmd
        Write-Host "✓ 视频合成完成: $OutputVideo" -ForegroundColor Green
    }
    catch {
        Write-Error "合成失败: $_"
    }
}

# ============================================
# 获取视频信息
# ============================================
function Get-VideoInformation {
    param([string]$VideoPath)
    
    if (-not (Test-Path $VideoPath)) {
        Write-Error "视频文件不存在: $VideoPath"
        return
    }
    
    Write-Host "视频信息:" -ForegroundColor Cyan
    
    $ffprobeCmd = "ffprobe -v quiet -print_format json -show_format -show_streams `"$VideoPath`""
    
    try {
        $info = Invoke-Expression $ffprobeCmd | ConvertFrom-Json
        
        $videoStream = $info.streams | Where-Object { $_.codec_type -eq "video" } | Select-Object -First 1
        
        Write-Host "文件路径: $VideoPath"
        Write-Host "时长: $($info.format.duration) 秒"
        Write-Host "分辨率: $($videoStream.width)x$($videoStream.height)"
        Write-Host "FPS: $($videoStream.r_frame_rate)"
        Write-Host "编码: $($videoStream.codec_name)"
        Write-Host "比特率: $([math]::Round($info.format.bit_rate / 1000000, 2)) Mbps"
    }
    catch {
        Write-Error "获取信息失败: $_"
    }
}

# ============================================
# 主逻辑
# ============================================
switch ($Action) {
    'extract' {
        if (-not $InputPath -or -not $OutputPath) {
            Write-Error "extract 操作需要 -InputPath 和 -OutputPath 参数"
            exit 1
        }
        Extract-VideoFrames -VideoPath $InputPath -OutputDir $OutputPath -FPS $FPS
    }
    
    'compose' {
        if (-not $InputPath -or -not $OutputPath) {
            Write-Error "compose 操作需要 -InputPath 和 -OutputPath 参数"
            exit 1
        }
        Compose-VideoFromFrames -FramesDir $InputPath -OutputVideo $OutputPath -FPS $FPS -Quality $Quality
    }
    
    'info' {
        if (-not $InputPath) {
            Write-Error "info 操作需要 -InputPath 参数"
            exit 1
        }
        Get-VideoInformation -VideoPath $InputPath
    }
}

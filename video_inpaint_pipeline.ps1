# <#
# .SYNOPSIS
#     视频修复完整流程自动化脚本
    
# .DESCRIPTION
#     整合 SAMWISE (掩码生成) + E2FGVI (视频修复) + BasicVSR++ (视频增强/降噪)
    
# .PARAMETER InputVideo
#     输入视频路径
    
# .PARAMETER TextPrompt
#     文本提示词，用于 SAMWISE 识别目标物体
    
# .PARAMETER SkipMask
#     跳过掩码生成步骤（如果已有掩码）
    
# .PARAMETER SkipInpaint
#     跳过修复步骤（如果已修复）
    
# .PARAMETER SkipEnhance
#     跳过增强步骤
    
# .PARAMETER SkipDenoise
#     跳过降噪步骤
    
# .PARAMETER NeighborStride
#     E2FGVI 邻域步长 (默认: 3)
    
# .PARAMETER MaxLoadFrames
#     E2FGVI 最大加载帧数 (默认: 8)
    
# .PARAMETER DenoiseMethod
#     降噪方法 (nlm/bilateral/gaussian，默认: nlm)
    
# .PARAMETER DenoiseStrength
#     降噪强度 (1-10，默认: 5)
    
# .EXAMPLE
#     .\video_inpaint_pipeline.ps1 -InputVideo "assets/test.mp4" -TextPrompt "the person"
# #>

# param(
#     [Parameter(Mandatory=$true)]
#     [string]$VideoPath,
    
#     [Parameter(Mandatory=$true)]
#     [string]$TextPrompt,
    
#     [switch]$SkipMask,
#     [switch]$SkipInpaint,
#     [switch]$SkipEnhance,
#     [switch]$SkipDenoise,
    
#     [int]$NeighborStride = 3,
#     [int]$MaxLoadFrames = 8,
    
#     [string]$DenoiseMethod = "nlm",
#     [int]$DenoiseStrength = 5
# )

# # ============================================
# # 配置区域
# # ============================================
# # 项目根目录
# $ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"

# $Config = @{
#     # Conda 配置
#     CondaPath = "C:\Users\Aiur\miniconda3\Scripts\conda.exe"
    
#     # 项目路径
#     ProjectRoot = $ProjectRoot
#     SamwisePath = Join-Path $ProjectRoot "SAMWISE"
#     E2FGVIPath = Join-Path $ProjectRoot "E2FGVI_Project"
#     BasicVSRPath = Join-Path $ProjectRoot "BasicVSR_PlusPlus"
    
#     # 数据文件夹(固定结构)
#     RawVideoDir = Join-Path $ProjectRoot "raw_video"
#     Step1_FramesDir = Join-Path $ProjectRoot "step1_frames"
#     Step2_MasksDir = Join-Path $ProjectRoot "step2_masks"
#     Step3_InpaintedDir = Join-Path $ProjectRoot "step3_inpainted"
#     Step4_EnhancedDir = Join-Path $ProjectRoot "step4_enhanced"
#     ResultsDir = Join-Path $ProjectRoot "results"
    
#     # Conda 环境名称
#     SamwiseEnv = "samwise"
#     E2FGVIEnv = "e2fgvi-project"
#     BasicVSREnv = "basicvsrpp-demo"
    
#     # E2FGVI 模型配置
#     E2FGVIModel = "e2fgvi_hq"
#     E2FGVICheckpoint = "release_model\E2FGVI-HQ-CVPR22.pth"
    
#     # BasicVSR++ 配置
#     BasicVSRConfig = "configs\basicvsr_plusplus_reds4.py"
#     BasicVSRCheckpoint = "checkpoints\basicvsr_plusplus_reds4.pth"
# }

# # ============================================
# # 辅助函数
# # ============================================
# function Write-Step {
#     param([string]$Message)
#     Write-Host "`n========================================" -ForegroundColor Cyan
#     Write-Host " $Message" -ForegroundColor Cyan
#     Write-Host "========================================`n" -ForegroundColor Cyan
# }

# function Write-Success {
#     param([string]$Message)
#     Write-Host "✓ $Message" -ForegroundColor Green
# }

# function Write-Error-Custom {
#     param([string]$Message)
# # ============================================
# # 主流程
# # ============================================
# $ErrorActionPreference = "Stop"
# $StartTime = Get-Date

# # 构建完整的视频路径
# $InputVideo = Join-Path $Config.RawVideoDir $VideoPath

# # 验证输入
# if (-not (Test-PathExists $InputVideo "输入视频")) { 
#     Write-Error-Custom "视频文件不存在: $InputVideo"
#     Write-Host "请将视频文件放在: $($Config.RawVideoDir)" -ForegroundColor Yellow
#     exit 1 
# }

# # 创建固定的输出目录结构
# $FramesDir = $Config.Step1_FramesDir
# $MaskDir = $Config.Step2_MasksDir
# $InpaintDir = $Config.Step3_InpaintedDir
# $EnhanceDir = $Config.Step4_EnhancedDir
# $ResultsDir = $Config.ResultsDir

# # 清理并创建目录
# Write-Host "初始化工作目录..." -ForegroundColor Cyan
# @($FramesDir, $MaskDir, $InpaintDir, $EnhanceDir, $ResultsDir) | ForEach-Object {
#     if (Test-Path $_) {
#         Remove-Item -Path $_ -Recurse -Force
#         Write-Host "  清理: $_" -ForegroundColor Gray
#     }
#     New-Item -ItemType Directory -Force -Path $_ | Out-Null
#     Write-Host "  创建: $_" -ForegroundColor Gray
# }

# Write-Step "视频修复流程开始"
# Write-Host "输入视频: $InputVideo"
# Write-Host "文本提示: $TextPrompt"
# Write-Host "项目根目录: $($Config.ProjectRoot)"
# $FramesDir = Join-Path $WorkDir "01_frames"
# # ============================================
# # 步骤 1: SAMWISE - 生成掩码
# # ============================================
# if (-not $SkipMask) {
#     Write-Step "步骤 1/4: SAMWISE - 生成视频帧和掩码"
    
#     Push-Location $Config.SamwisePath
#     try {
#         $cmd = "conda activate $($Config.SamwiseEnv); python inference_demo.py --input_path `"$InputVideo`" --text_prompts `"$TextPrompt`""
#         Write-Host "执行命令: $cmd" -ForegroundColor Gray
        
#         Invoke-Expression $cmd
#         if ($LASTEXITCODE -ne 0) { throw "SAMWISE 执行失败" }
        
#         # 复制生成的帧和掩码到固定目录
#         $VideoBaseName = [System.IO.Path]::GetFileNameWithoutExtension($InputVideo)
#         $SamwiseFramesOutput = "frames_$VideoBaseName"
#         $SamwiseMaskOutput = "demo_output"
        
#         if (Test-Path $SamwiseFramesOutput) {
#             Write-Host "复制视频帧..." -ForegroundColor Gray
#             Copy-Item -Path "$SamwiseFramesOutput\*" -Destination $FramesDir -Recurse -Force
#             $frameCount = (Get-ChildItem -Path $FramesDir -Filter "*.jpg","*.png" -Recurse).Count
#             Write-Success "视频帧已保存: $FramesDir ($frameCount 帧)"
#         } else {
#             throw "未找到视频帧输出: $SamwiseFramesOutput"
#         }
        
#         if (Test-Path $SamwiseMaskOutput) {
#             Write-Host "复制掩码文件..." -ForegroundColor Gray
#             Copy-Item -Path "$SamwiseMaskOutput\*" -Destination $MaskDir -Recurse -Force
#             $maskCount = (Get-ChildItem -Path $MaskDir -Filter "*.jpg","*.png" -Recurse).Count
#             Write-Success "掩码已保存: $MaskDir ($maskCount 个掩码)"
#         } else {
#             throw "未找到掩码输出: $SamwiseMaskOutput"
#         }
        
#     } finally {
#         Pop-Location
#     }
# } else {
#     Write-Host "跳过掩码生成步骤" -ForegroundColor Yellow
# }       }
        
#         if (Test-Path $SamwiseMaskOutput) {
#             Copy-Item -Path "$SamwiseMaskOutput\*" -Destination $MaskDir -Recurse -Force
#             Write-Success "掩码已保存到: $MaskDir"
# # ============================================
# # 步骤 2: E2FGVI - 视频修复
# # ============================================
# if (-not $SkipInpaint) {
#     Write-Step "步骤 2/4: E2FGVI - 视频修复 (去除对象)"
    
#     Push-Location $Config.E2FGVIPath
#     try {
#         # 设置 CUDA 内存配置
#         $env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
        
#         $cmd = "conda activate $($Config.E2FGVIEnv); python test.py --model $($Config.E2FGVIModel) --video `"$FramesDir`" --mask `"$MaskDir`" --ckpt $($Config.E2FGVICheckpoint) --neighbor_stride $NeighborStride --max_load_frames $MaxLoadFrames"
#         Write-Host "执行命令: $cmd" -ForegroundColor Gray
#         Write-Host "参数: NeighborStride=$NeighborStride, MaxLoadFrames=$MaxLoadFrames" -ForegroundColor Gray
        
#         Invoke-Expression $cmd
#         if ($LASTEXITCODE -ne 0) { throw "E2FGVI 执行失败" }
        
#         # 复制修复结果到 step3_inpainted
#         $E2FGVIOutput = "results"  # E2FGVI 默认输出目录
#         if (Test-Path $E2FGVIOutput) {
#             Write-Host "复制修复结果..." -ForegroundColor Gray
#             Copy-Item -Path "$E2FGVIOutput\*" -Destination $InpaintDir -Recurse -Force
#             $inpaintCount = (Get-ChildItem -Path $InpaintDir -Filter "*.jpg","*.png" -Recurse).Count
#             Write-Success "修复结果已保存: $InpaintDir ($inpaintCount 帧)"
#         } else {
#             throw "未找到 E2FGVI 输出: $E2FGVIOutput"
#         }
        
#     } finally {
#         Pop-Location
#     }
# # ============================================
# # 步骤 3: BasicVSR++ - 视频增强
# # ============================================
# if (-not $SkipEnhance) {
#     Write-Step "步骤 3/4: BasicVSR++ - 视频质量增强"
    
#     Push-Location $Config.BasicVSRPath
#     try {
#         $cmd = "conda activate $($Config.BasicVSREnv); python demo/restoration_video_demo.py $($Config.BasicVSRConfig) $($Config.BasicVSRCheckpoint) `"$InpaintDir`" `"$EnhanceDir`""
#         Write-Host "执行命令: $cmd" -ForegroundColor Gray
        
#         Invoke-Expression $cmd
#         if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ 增强失败" }
        
#         $enhanceCount = (Get-ChildItem -Path $EnhanceDir -Filter "*.jpg","*.png" -Recurse).Count
#         Write-Success "增强结果已保存: $EnhanceDir ($enhanceCount 帧)"
        
#     } finally {
#         Pop-Location
#     }
# } else {
#     Write-Host "跳过视频增强步骤" -ForegroundColor Yellow
# }       $cmd = "conda activate $($Config.BasicVSREnv); python demo/restoration_video_demo.py $($Config.BasicVSRConfig) $($Config.BasicVSRCheckpoint) `"$InpaintDir`" `"$EnhanceDir`""
#         Write-Host "执行命令: $cmd"
        
#         Invoke-Expression $cmd
#         if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ 增强失败" }
        
#         Write-Success "增强结果已保存到: $EnhanceDir"
        
#     } finally {
#         Pop-Location
# # ============================================
# # 步骤 4: BasicVSR++ - 视频降噪并保存到 results
# # ============================================
# if (-not $SkipDenoise) {
#     Write-Step "步骤 4/4: BasicVSR++ - 视频降噪并输出最终结果"
    
#     Push-Location $Config.BasicVSRPath
#     try {
#         # 降噪并直接输出到 results 文件夹
#         $cmd = "conda activate $($Config.BasicVSREnv); python demo/denoise_results.py `"$EnhanceDir`" `"$ResultsDir`" --method $DenoiseMethod --strength $DenoiseStrength --preserve-details --create-video --speed 0.4"
#         Write-Host "执行命令: $cmd" -ForegroundColor Gray
#         Write-Host "降噪参数: Method=$DenoiseMethod, Strength=$DenoiseStrength" -ForegroundColor Gray
        
#         Invoke-Expression $cmd
#         if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ 降噪失败" }
        
#         $resultCount = (Get-ChildItem -Path $ResultsDir -Filter "*.jpg","*.png","*.mp4" -Recurse).Count
#         Write-Success "最终结果已保存: $ResultsDir ($resultCount 个文件)"
        
#     } finally {
#         Pop-Location
#     }
# } else {
#     Write-Host "跳过降噪步骤" -ForegroundColor Yellow
#     # 如果跳过降噪,将增强结果复制到 results
#     Write-Host "将增强结果复制到 results 文件夹..." -ForegroundColor Gray
#     Copy-Item -Path "$EnhanceDir\*" -Destination $ResultsDir -Recurse -Force
# # ============================================
# # 完成
# # ============================================
# $EndTime = Get-Date
# $Duration = $EndTime - $StartTime

# Write-Step "处理完成!"
# Write-Host "总耗时: $($Duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
# Write-Host ""
# Write-Host "========================================" -ForegroundColor Cyan
# Write-Host "文件夹结构 (SuperVideo-inpaint):" -ForegroundColor Cyan
# Write-Host "========================================" -ForegroundColor Cyan
# Write-Host "  raw_video/        输入视频"
# Write-Host "  ├─ step1_frames/     步骤1: 视频帧提取"
# Write-Host "  ├─ step2_masks/      步骤2: 掩码生成"
# Write-Host "  ├─ step3_inpainted/  步骤3: 视频修复"
# Write-Host "  ├─ step4_enhanced/   步骤4: 视频增强"
# Write-Host "  └─ results/          ✓ 最终结果 ✓" -ForegroundColor Green
# Write-Host ""
# Write-Host "最终结果位置: $ResultsDir" -ForegroundColor Green
# Write-Host ""

# # 显示结果文件列表
# $resultFiles = Get-ChildItem -Path $ResultsDir -File
# if ($resultFiles.Count -gt 0) {
#     Write-Host "生成的文件:" -ForegroundColor Cyan
#     foreach ($file in $resultFiles) {
#         $sizeKB = [math]::Round($file.Length / 1KB, 2)
#         Write-Host "  - $($file.Name) ($sizeKB KB)"
#     }
# }

# Write-Host ""
# Write-Success "所有流程执行完成!"r"
# Write-Host "`n文件结构:"
# Write-Host "  ├─ 01_frames/      (原始视频帧)"
# Write-Host "  ├─ 02_masks/       (生成的掩码)"
# Write-Host "  ├─ 03_inpainted/   (修复后的视频)"
# Write-Host "  ├─ 04_enhanced/    (增强后的视频)"
# Write-Host "  └─ 05_denoised/    (降噪后的最终结果)"
# Write-Host ""
# Write-Success "所有流程执行完成!"

<#
.SYNOPSIS
    Video Inpainting Pipeline - Automated Workflow
    
.DESCRIPTION
    Integrates SAMWISE (mask generation) + E2FGVI (video inpainting) + BasicVSR++ (enhancement/denoising)
    
.PARAMETER VideoPath
    Video filename in raw_video folder
    
.PARAMETER TextPrompt
    Text prompt for SAMWISE to identify target object
    
.PARAMETER SkipMask
    Skip mask generation step
    
.PARAMETER SkipInpaint
    Skip inpainting step
    
.PARAMETER SkipEnhance
    Skip enhancement step
    
.PARAMETER SkipDenoise
    Skip denoising step
    
.PARAMETER NeighborStride
    E2FGVI neighbor stride (default: 3)
    
.PARAMETER MaxLoadFrames
    E2FGVI max load frames (default: 8)
    
.PARAMETER DenoiseMethod
    Denoising method (nlm/bilateral/gaussian, default: nlm)
    
.PARAMETER DenoiseStrength
    Denoising strength (1-10, default: 5)
    
.PARAMETER OutputDir
    Custom output directory for results (default: results folder in project root)
    
.EXAMPLE
    .\video_inpaint_pipeline_en.ps1 -VideoPath "test.mp4" -TextPrompt "the person"
    
.EXAMPLE
    .\video_inpaint_pipeline_en.ps1 -VideoPath "test.mp4" -TextPrompt "the person" -OutputDir "C:\MyResults"
#>

param(
    [switch]$SkipMask,
    [switch]$SkipInpaint,
    [switch]$SkipEnhance,
    [switch]$SkipDenoise,
    
    [int]$NeighborStride = 3,
    [int]$MaxLoadFrames = 4,
    
    # Segment processing to reduce memory (0=disabled)
    [int]$SegmentSize = 0,

    # Force CPU for restoration to avoid GPU OOM
    [switch]$ForceCPU,
    
    # Max resolution (longer edge) to resize frames before processing (0=no resize, default: 720)
    [int]$MaxResolution = 720,
    
    # Frame extraction rate from video (fps, default: 10 means 10 frames per second)
    [int]$FrameExtractionFps = 10,
    
    # Video speed multiplier for output videos (default: 1.0, 2.0 = 2x speed)
    [float]$VideoSpeedMultiplier = 1.0,
    
    [string]$DenoiseMethod = "nlm",
    [int]$DenoiseStrength = 5,
    
    [string]$RawPromptPath = "raw_prompt\prompt_list.json",
    
    # Custom output directory (default: results folder in project root)
    [string]$OutputDir = ""
)

# ============================================
# Configuration
# ============================================
$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"

$Config = @{
    # Conda configuration
    CondaPath = "C:\Users\Aiur\miniconda3\Scripts\conda.exe"
    
    # Project paths
    ProjectRoot = $ProjectRoot
    SamwisePath = Join-Path $ProjectRoot "SAMWISE"
    E2FGVIPath = Join-Path $ProjectRoot "E2FGVI_Project\E2FGVI"
    BasicVSRPath = Join-Path $ProjectRoot "BasicVSR_PlusPlus"
    
    # Data folders (user-specified structure)
    RawVideoDir = Join-Path $ProjectRoot "raw_video"
    FramesPackageDir = Join-Path $ProjectRoot "frames_package"
    MaskPackageDir = Join-Path $ProjectRoot "mask_package"
    InpaintPackageDir = Join-Path $ProjectRoot "inpaint_package"
    RestorePackageDir = Join-Path $ProjectRoot "restore_package"
    DenoisePackageDir = Join-Path $ProjectRoot "denoise_package"
    ResultsDir = if ($OutputDir) { 
        if ([System.IO.Path]::IsPathRooted($OutputDir)) { 
            $OutputDir 
        } else { 
            Join-Path $ProjectRoot $OutputDir 
        }
    } else { 
        Join-Path $ProjectRoot "results" 
    }
    
    # Conda environment names
    SamwiseEnv = "samwise"
    E2FGVIEnv = "e2fgvi-project"
    BasicVSREnv = "basicvsrpp-demo"
    
    # E2FGVI model config
    E2FGVIModel = "e2fgvi_hq"
    E2FGVICheckpoint = "release_model\E2FGVI-HQ-CVPR22.pth"
    
    # BasicVSR++ config
    BasicVSRConfig = "configs\basicvsr_plusplus_reds4.py"
    BasicVSRCheckpoint = "checkpoints\basicvsr_plusplus_reds4.pth"
}

# ============================================
# Helper Functions
# ============================================
function Write-Step {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host " $Message" -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Test-PathExists {
    param([string]$Path, [string]$Description)
    if (-not (Test-Path $Path)) {
        Write-Host "[ERROR] $Description not found: $Path" -ForegroundColor Red
        return $false
    }
    return $true
}

function Write-Success {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Green
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "$Message" -ForegroundColor Red
}

function Resize-Frames {
    param(
        [string]$InputDir,
        [string]$OutputDir,
        [int]$MaxResolution
    )
    
    Write-Host "Resizing frames to max resolution: ${MaxResolution}px" -ForegroundColor Gray
    
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null }
    
    $frames = Get-ChildItem -Path $InputDir -Filter "*.png" -File | Sort-Object Name
    if ($frames.Count -eq 0) { $frames = Get-ChildItem -Path $InputDir -Filter "*.jpg" -File | Sort-Object Name }
    
    if ($frames.Count -eq 0) {
        Write-Host "  No frames found to resize" -ForegroundColor Yellow
        return $false
    }
    
    # Use Python with PIL/cv2 to resize (available in e2fgvi-project env)
    $resizeScript = @"
import os, sys
from PIL import Image
import glob

input_dir = r'$InputDir'
output_dir = r'$OutputDir'
max_res = $MaxResolution

frames = sorted(glob.glob(os.path.join(input_dir, '*.png')) + glob.glob(os.path.join(input_dir, '*.jpg')))
if not frames:
    sys.exit(1)

for f in frames:
    img = Image.open(f)
    w, h = img.size
    if max(w, h) > max_res:
        scale = max_res / max(w, h)
        new_w, new_h = int(w * scale), int(h * scale)
        # Ensure even dimensions (required by libx264)
        new_w = new_w if new_w % 2 == 0 else new_w + 1
        new_h = new_h if new_h % 2 == 0 else new_h + 1
        img = img.resize((new_w, new_h), Image.LANCZOS)
    out_path = os.path.join(output_dir, os.path.basename(f))
    img.save(out_path)
print(f'Resized {len(frames)} frames to {output_dir}')
"@
    
    $tempScript = Join-Path $env:TEMP "resize_frames.py"
    $resizeScript | Out-File -FilePath $tempScript -Encoding UTF8 -Force
    
    try {
        $cmd = "conda activate e2fgvi-project; python `"$tempScript`""
        Invoke-Expression $cmd
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  Frames resized successfully" -ForegroundColor Green
            return $true
        }
        return $false
    } catch {
        Write-Host "  Failed to resize frames: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    } finally {
        Remove-Item -Path $tempScript -Force -ErrorAction SilentlyContinue
    }
}

function Get-VideoDurationSeconds {
    param([string]$VideoPath)
    
    if (-not (Test-Path $VideoPath)) {
        return $null
    }
    
    try {
        # Try using ffprobe via e2fgvi-project conda env (ffmpeg is there)
        $output = conda run -n e2fgvi-project ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VideoPath" 2>$null
        if ($output) {
            return [float]$output
        }
    } catch {
        return $null
    }
    return $null
}

function Create-VideoFromFrames {
    param(
        [string]$FramesDir,
        [string]$OutputVideoPath,
        [int]$Fps = 10,
        [float]$SpeedMultiplier = 1.0,
        [float]$TargetDurationSeconds = $null
    )

    Write-Host "Creating video from frames: $OutputVideoPath (speed: ${SpeedMultiplier}x)" -ForegroundColor Gray
    
    # Collect frames (png preferred, fallback to jpg), sorted by name
    $frames = Get-ChildItem -Path $FramesDir -Filter "*.png" | Sort-Object Name
    if ($frames.Count -eq 0) {
        $frames = Get-ChildItem -Path $FramesDir -Filter "*.jpg" | Sort-Object Name
    }
    
    if ($frames.Count -eq 0) {
        Write-Host "  No frames found in $FramesDir" -ForegroundColor Yellow
        return $false
    }
    
    # Detect numeric start index from first frame filename
    $firstName = $frames[0].Name
    $useGlob = $true
    $startNumber = 1
    
    # Try to match pattern: prefix + digits + optional_suffix + extension
    # Examples: frame_00001.png, frame_00001_mask.png, img001.jpg
    if ($firstName -match '^(.*?)(\d+)(.*)(\.[A-Za-z]+)$') {
        $prefix = $Matches[1]
        $digits = $Matches[2]
        $suffix = $Matches[3]
        $ext = $Matches[4]
        $startNumber = [int]$digits
        $numDigits = $digits.Length
        
        # Build pattern: prefix%0Ndsuffix.ext
        $framePattern = Join-Path $FramesDir ("{0}%0{1}d{2}{3}" -f $prefix, $numDigits, $suffix, $ext)
        $useGlob = $false
    }
    
    # Build ffmpeg command using conda run (avoids shell activation issues)
    $ffmpegArgs = @('-y', '-framerate', "$Fps")
    if (-not $useGlob) {
        # Escape '%' for Windows cmd/conda-run (use '%%' in numeric patterns)
        $framePatternEsc = $framePattern -replace '%','%%'
        $ffmpegArgs += @('-start_number', "$startNumber", '-i', "$framePatternEsc")
    } else {
        $pattern = if ((Get-ChildItem -Path $FramesDir -Filter "*.png").Count -gt 0) { "*.png" } else { "*.jpg" }
        $ffmpegArgs += @('-pattern_type', 'glob', '-i', "$FramesDir\$pattern")
    }
    
    # Calculate output fps to match target duration (preserve video length regardless of frame count)
    $outputFps = $Fps  # default
    if ($TargetDurationSeconds -and $TargetDurationSeconds -gt 0) {
        # output_fps = frame_count / target_duration_seconds
        $frameCount = $frames.Count
        $outputFps = [math]::Max(1, [math]::Round($frameCount / $TargetDurationSeconds, 2))
        Write-Host "  Adjusting output fps: $frameCount frames / ${TargetDurationSeconds}s = ${outputFps}fps" -ForegroundColor Gray
    } else {
        # If no target duration, apply speed multiplier
        $outputFps = [math]::Max(1, [int]($Fps / $SpeedMultiplier))
    }
    
    # Use -vcodec to avoid PowerShell/conda parsing issues with '-c:v'
    $ffmpegArgs += @('-vcodec', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18', '-r', "$outputFps", "$OutputVideoPath")

    try {
        # Ensure output directory exists
        $outDir = Split-Path -Parent $OutputVideoPath
        if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Force -Path $outDir | Out-Null }

        # Run ffmpeg via conda run to guarantee environment
        $argList = @('run','-n','e2fgvi-project','ffmpeg') + $ffmpegArgs
        $proc = Start-Process -FilePath "conda" -ArgumentList $argList -NoNewWindow -Wait -PassThru -RedirectStandardError "$outDir\ffmpeg.err.log" -RedirectStandardOutput "$outDir\ffmpeg.out.log"

        # Wait a moment for file system to flush
        Start-Sleep -Milliseconds 500
        
        # Consider success if output file exists and has non-zero size
        if (Test-Path $OutputVideoPath) {
            $item = Get-Item $OutputVideoPath -ErrorAction SilentlyContinue
            if ($item -and $item.Length -gt 0) {
                $videoSize = [math]::Round($item.Length / 1MB, 3)
                Write-Host "  Video created: $OutputVideoPath ($videoSize MB)" -ForegroundColor Green
                return $true
            }
        }
        # If failed, check error log for actual errors (ignore informational output)
        $errLog = "$outDir\ffmpeg.err.log"
        if (Test-Path $errLog) {
            $errContent = Get-Content -Path $errLog -Raw
            if ($errContent -match "Error|failed|cannot|Unable") {
                $hint = ($errContent -split "`n" | Where-Object { $_ -match "Error|failed" } | Select-Object -First 1)
                Write-Host "  Failed to create video (hint: $hint)" -ForegroundColor Yellow
                return $false
            }
        }
        # No output file but no clear error either - retry once
        Write-Host "  Output file not found, retrying..." -ForegroundColor Yellow
        Start-Sleep -Seconds 1
        if (Test-Path $OutputVideoPath) {
            $item = Get-Item $OutputVideoPath -ErrorAction SilentlyContinue
            if ($item -and $item.Length -gt 0) {
                $videoSize = [math]::Round($item.Length / 1MB, 3)
                Write-Host "  Video created: $OutputVideoPath ($videoSize MB)" -ForegroundColor Green
                return $true
            }
        }
        Write-Host "  Failed to create video (output file missing)" -ForegroundColor Yellow
        return $false
    } catch {
        Write-Host "  Error creating video: $($_.Exception.Message)" -ForegroundColor Yellow
        return $false
    }
}

# ============================================
# Main Pipeline
# ============================================
$ErrorActionPreference = "Stop"
$StartTime = Get-Date

# Load prompt mapping JSON
$RawPromptFile = Join-Path $ProjectRoot $RawPromptPath
if (-not (Test-Path $RawPromptFile)) {
    Write-ErrorMsg "Prompt mapping JSON not found: $RawPromptFile"
    Write-Host "Expected JSON format: [ { \"video_name\": \"file.mp4\", \"remove_prompt\": \"text\" }, ... ]" -ForegroundColor Yellow
    exit 1
}
try { $PromptArray = Get-Content -Path $RawPromptFile -Raw | ConvertFrom-Json }
catch { Write-ErrorMsg "Failed to parse prompt JSON: $($_.Exception.Message)"; exit 1 }

# Build mapping: filename -> prompt
$PromptMap = @{}
foreach ($item in $PromptArray) {
    if ($item.video_name -and $item.remove_prompt) {
        $PromptMap[$item.video_name] = $item.remove_prompt
    }
}

# Enumerate all videos in raw_video
$RawVideos = Get-ChildItem -Path $Config.RawVideoDir -Filter *.mp4 -File | Sort-Object Name
if ($RawVideos.Count -eq 0) {
    Write-ErrorMsg "No mp4 videos found in: $($Config.RawVideoDir)"; exit 1
}

Write-Step "Video Inpainting Pipeline Started (batch mode)"
Write-Host "Project Root: $($Config.ProjectRoot)"
Write-Host "Raw Video Dir: $($Config.RawVideoDir)"
Write-Host "Prompt JSON: $RawPromptFile"

foreach ($vid in $RawVideos) {
    $VideoPath = $vid.FullName
    $VideoBaseName = [System.IO.Path]::GetFileNameWithoutExtension($vid.Name)
    $TextPrompt = $PromptMap[$vid.Name]
    if (-not $TextPrompt) {
        Write-Host "Skipping '$($vid.Name)': no prompt in JSON" -ForegroundColor Yellow
        continue
    }

    # Skip processing if results already exist for this exact video base name
    $ResultsDir = Join-Path $Config.ResultsDir "${VideoBaseName}_result"
    if (Test-Path $ResultsDir) {
        $existingResultFrames = Get-ChildItem -Path $ResultsDir -Include "*.png","*.jpg" -Recurse -File -ErrorAction SilentlyContinue
        if ($existingResultFrames -and $existingResultFrames.Count -gt 0) {
            # Check if source video is newer than results
            $videoModified = (Get-Item $VideoPath).LastWriteTime
            $resultModified = ($existingResultFrames | Sort-Object LastWriteTime -Descending | Select-Object -First 1).LastWriteTime
            
            if ($videoModified -le $resultModified) {
                $frameCount = $existingResultFrames.Count
                Write-Host "Skipping '$($vid.Name)': results already exist in '$ResultsDir' ($frameCount frames)" -ForegroundColor Green
                continue
            } else {
                Write-Host "Source video updated since last processing, re-processing '$($vid.Name)'..." -ForegroundColor Yellow
            }
        }
    }

    Write-Host ""; Write-Host "Processing: $($vid.Name) | Prompt: $TextPrompt" -ForegroundColor Cyan

    # Get original video duration for later use
    $OriginalVideoDuration = Get-VideoDurationSeconds -VideoPath $VideoPath
    if ($OriginalVideoDuration) {
        Write-Host "Original video duration: $([math]::Round($OriginalVideoDuration, 2))s" -ForegroundColor Gray
    }

    # Per-video output directories
    $FramesDir = Join-Path $Config.FramesPackageDir "${VideoBaseName}_frames"
    $MaskDir = Join-Path $Config.MaskPackageDir "${VideoBaseName}_mask"
    $InpaintDir = Join-Path $Config.InpaintPackageDir "${VideoBaseName}_inpaint"
    $RestoreDir = Join-Path $Config.RestorePackageDir "${VideoBaseName}_restore"
    $DenoiseDir = Join-Path $Config.DenoisePackageDir "${VideoBaseName}_denoise"
    # $ResultsDir already defined above for skip check

    # Clean and create directories
    Write-Host "Initializing workspace for $VideoBaseName..." -ForegroundColor Gray
    @($FramesDir, $MaskDir, $InpaintDir, $RestoreDir, $DenoiseDir) | ForEach-Object {
        if (Test-Path $_) { Remove-Item -Path $_ -Recurse -Force }
        New-Item -ItemType Directory -Force -Path $_ | Out-Null
    }

# ============================================
# Step 1: SAMWISE - Generate Masks
# ============================================
if (-not $SkipMask) {
    Write-Step "Step 1/4: SAMWISE - Extract Frames and Generate Masks"
    
    Push-Location $Config.SamwisePath
    try {
        $cmd = "conda activate $($Config.SamwiseEnv); python inference_demo.py --input_path `"$VideoPath`" --text_prompts `"$TextPrompt`" --fps $FrameExtractionFps"
        Write-Host "Running command: $cmd" -ForegroundColor Gray
        
        Invoke-Expression $cmd
        if ($LASTEXITCODE -ne 0) { throw "SAMWISE execution failed" }
        
        # SAMWISE 输出结构：
        # 1. frames_<video_name>/  - 提取的视频帧
        # 2. demo_output/<prompt>_binary_masks/  - 黑白掩码
        
        $SamwiseFramesOutput = "frames_$VideoBaseName"
        $PromptFolderName = $TextPrompt.Replace(' ', '_') + '_binary_masks'
        $SamwiseMaskOutput = Join-Path "demo_output" $PromptFolderName
        
        # Copy video frames
        if (Test-Path $SamwiseFramesOutput) {
            Write-Host "Copying video frames from $SamwiseFramesOutput..." -ForegroundColor Gray
            $sourceFrames = Get-ChildItem -Path $SamwiseFramesOutput -File -Include "*.jpg","*.png" -Recurse
            if ($sourceFrames.Count -gt 0) {
                Copy-Item -Path "$SamwiseFramesOutput\*" -Destination $FramesDir -Force
                $frameCount = (Get-ChildItem -Path $FramesDir -File -Include "*.jpg","*.png" -Recurse).Count
                Write-Success "Video frames saved: $FramesDir ($frameCount frames)"
            } else {
                throw "No frame files found in: $SamwiseFramesOutput"
            }
        } else {
            throw "Video frames output not found: $SamwiseFramesOutput"
        }
        
        # Copy binary masks (black/white masks)
        if (Test-Path $SamwiseMaskOutput) {
            Write-Host "Copying binary masks from $SamwiseMaskOutput..." -ForegroundColor Gray
            $sourceMasks = Get-ChildItem -Path $SamwiseMaskOutput -File -Include "*.jpg","*.png" -Recurse
            if ($sourceMasks.Count -gt 0) {
                Copy-Item -Path "$SamwiseMaskOutput\*" -Destination $MaskDir -Force
                $maskCount = (Get-ChildItem -Path $MaskDir -File -Include "*.jpg","*.png" -Recurse).Count
                Write-Success "Binary masks saved: $MaskDir ($maskCount masks)"
            } else {
                throw "No mask files found in: $SamwiseMaskOutput"
            }
        } else {
            throw "Binary mask output not found: $SamwiseMaskOutput`nExpected format: demo_output/<prompt>_binary_masks/"
        }
        
        # Generate mask video
        $MaskVideoDir = Join-Path (Split-Path $MaskDir -Parent) "${VideoBaseName}_mask_video"
        New-Item -ItemType Directory -Force -Path $MaskVideoDir | Out-Null
        $MaskVideoPath = Join-Path $MaskVideoDir "${VideoBaseName}_mask.mp4"
        if ($maskCount -gt 0) {
            Create-VideoFromFrames -FramesDir $MaskDir -OutputVideoPath $MaskVideoPath -Fps $FrameExtractionFps
        } else {
            Write-Host "Skipping mask video creation (no frames)" -ForegroundColor Yellow
        }
        
    } finally {
        Pop-Location
    }
} else {
    Write-Host "Skipping mask generation step" -ForegroundColor Yellow
}

# ============================================
# Step 1.5: Resize Frames (if MaxResolution > 0)
# ============================================
if ($MaxResolution -gt 0 -and -not $SkipMask) {
    Write-Step "Step 1.5/4: Resize Frames to Reduce Memory Usage"
    
    # Resize video frames
    $FramesDirResized = Join-Path $Config.FramesPackageDir "${VideoBaseName}_frames_resized"
    $resizeSuccess = Resize-Frames -InputDir $FramesDir -OutputDir $FramesDirResized -MaxResolution $MaxResolution
    if ($resizeSuccess) {
        # Replace original frames dir with resized version
        Remove-Item -Path $FramesDir -Recurse -Force -ErrorAction SilentlyContinue
        Move-Item -Path $FramesDirResized -Destination $FramesDir -Force
        Write-Success "Video frames resized and replaced"
    }
    
    # Resize masks to match
    $MaskDirResized = Join-Path $Config.MaskPackageDir "${VideoBaseName}_mask_resized"
    $resizeSuccess = Resize-Frames -InputDir $MaskDir -OutputDir $MaskDirResized -MaxResolution $MaxResolution
    if ($resizeSuccess) {
        # Replace original mask dir with resized version
        Remove-Item -Path $MaskDir -Recurse -Force -ErrorAction SilentlyContinue
        Move-Item -Path $MaskDirResized -Destination $MaskDir -Force
        Write-Success "Masks resized and replaced"
    }
}

# ============================================
# Step 2: E2FGVI - Video Inpainting
# ============================================
if (-not $SkipInpaint) {
    Write-Step "Step 2/4: E2FGVI - Video Inpainting (Remove Object)"
    
    Push-Location $Config.E2FGVIPath
    try {
        # Clean previous results directory to avoid contamination
        $E2FGVIResultsDir = "results"
        if (Test-Path $E2FGVIResultsDir) {
            Write-Host "Cleaning previous E2FGVI results..." -ForegroundColor Gray
            Remove-Item -Path $E2FGVIResultsDir -Recurse -Force
        }
        
        # Set CUDA memory config
        $env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
        
        $cmd = "conda activate $($Config.E2FGVIEnv); python test.py --model $($Config.E2FGVIModel) --video `"$FramesDir`" --mask `"$MaskDir`" --ckpt $($Config.E2FGVICheckpoint) --neighbor_stride $NeighborStride --max_load_frames $MaxLoadFrames --no-show"
        Write-Host "Running command: $cmd" -ForegroundColor Gray
        Write-Host "Parameters: NeighborStride=$NeighborStride, MaxLoadFrames=$MaxLoadFrames" -ForegroundColor Gray
        
        Invoke-Expression $cmd
        if ($LASTEXITCODE -ne 0) { throw "E2FGVI execution failed" }
        
        # Copy inpainting results - only the frames folder for current video
        # E2FGVI creates: results/<video_name>_frames/ folder with frame_00000.png, frame_00001.png, etc.
        $framesFolderName = "${VideoBaseName}_frames_frames"
        $E2FGVIFramesOutput = Join-Path $E2FGVIResultsDir $framesFolderName
        
        if (Test-Path $E2FGVIFramesOutput) {
            Write-Host "Copying inpainting results from $framesFolderName..." -ForegroundColor Gray
            Copy-Item -Path "$E2FGVIFramesOutput\*" -Destination $InpaintDir -Force
            $inpaintCount = (Get-ChildItem -Path $InpaintDir -Include "*.jpg","*.png").Count
            Write-Success "Inpainting results saved: $InpaintDir ($inpaintCount frames)"
        } else {
            throw "E2FGVI frames output not found: $E2FGVIFramesOutput"
        }
        
        # 生成修复后的视频
        $InpaintVideoDir = Join-Path (Split-Path $InpaintDir -Parent) "${VideoBaseName}_inpaint_video"
        New-Item -ItemType Directory -Force -Path $InpaintVideoDir | Out-Null
        $InpaintVideoPath = Join-Path $InpaintVideoDir "${VideoBaseName}_inpaint.mp4"
        Create-VideoFromFrames -FramesDir $InpaintDir -OutputVideoPath $InpaintVideoPath -Fps $FrameExtractionFps
        
    } finally {
        # Proactively free GPU memory after E2FGVI to leave room for restoration
        Write-Host "Clearing CUDA cache after E2FGVI..." -ForegroundColor Gray
        try {
            $clearCmd = "conda activate $($Config.E2FGVIEnv); python -c `"import torch; torch.cuda.empty_cache(); print('CUDA cache cleared')`""
            Invoke-Expression $clearCmd
        } catch {
            Write-Host "Warning: failed to clear CUDA cache: $($_.Exception.Message)" -ForegroundColor Yellow
        }
        Pop-Location
    }
} else {
    Write-Host "Skipping video inpainting step" -ForegroundColor Yellow
}

# ============================================
# Step 3: BasicVSR++ - Video Restoration
# ============================================
if (-not $SkipEnhance) {
    Write-Step "Step 3/4: BasicVSR++ - Video Restoration"
    
    # Set GPU memory config
    $env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
    $env:PYTHONPATH = $Config.BasicVSRPath
    
    # Step 3.1: Create intermediate video from inpaint frames (avoids frame numbering/missing issues)
    Write-Host "Creating intermediate video from inpaint frames..." -ForegroundColor Gray
    $InpaintVideoDir = Join-Path (Split-Path $InpaintDir -Parent) "${VideoBaseName}_inpaint_for_restore"
    New-Item -ItemType Directory -Force -Path $InpaintVideoDir | Out-Null
    $InpaintVideoPath = Join-Path $InpaintVideoDir "${VideoBaseName}_inpaint.mp4"
    
    $createVideoSuccess = Create-VideoFromFrames -FramesDir $InpaintDir -OutputVideoPath $InpaintVideoPath -Fps $FrameExtractionFps
    if (-not $createVideoSuccess) {
        throw "Failed to create intermediate inpaint video for restoration"
    }
    
    # Step 3.2: Run BasicVSR++ restoration using video input (GPU with fallback to CPU)
    Push-Location $Config.BasicVSRPath
    try {
        $maxSeqLen = if ($SegmentSize -gt 0) { $SegmentSize } else { 10 }
        $device = if ($ForceCPU) { "cpu" } else { "cuda:0" }
        
        $cmdRestore = "conda activate $($Config.BasicVSREnv); python demo/restoration_video_demo.py $($Config.BasicVSRConfig) $($Config.BasicVSRCheckpoint) `"$InpaintVideoPath`" `"$RestoreDir`" --device $device --fps 12 --max-seq-len $maxSeqLen"
        Write-Host "Running restoration: device=$device, max-seq-len=$maxSeqLen" -ForegroundColor Gray
        
        if ($ForceCPU) {
            Invoke-Expression $cmdRestore
            if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ restoration failed on CPU" }
        } else {
            try {
                Invoke-Expression $cmdRestore
                if ($LASTEXITCODE -ne 0) { throw "GPU run failed" }
            } catch {
                Write-Host "GPU restoration failed, retrying on CPU..." -ForegroundColor Yellow
                $cmdCpu = "conda activate $($Config.BasicVSREnv); python demo/restoration_video_demo.py $($Config.BasicVSRConfig) $($Config.BasicVSRCheckpoint) `"$InpaintVideoPath`" `"$RestoreDir`" --device cpu --fps 12 --max-seq-len $maxSeqLen"
                Invoke-Expression $cmdCpu
                if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ restoration failed on CPU" }
            }
        }
        
        $restoreCount = (Get-ChildItem -Path $RestoreDir -Include "*.jpg","*.png" -Recurse).Count
        Write-Success "Restoration results saved: $RestoreDir ($restoreCount frames)"
        
    } finally {
        Pop-Location
    }
    
    # Step 3.3: Create restored video for preview
    $RestoreVideoDir = Join-Path (Split-Path $RestoreDir -Parent) "${VideoBaseName}_restore_video"
    New-Item -ItemType Directory -Force -Path $RestoreVideoDir | Out-Null
    $RestoreVideoPath = Join-Path $RestoreVideoDir "${VideoBaseName}_restore.mp4"
    Create-VideoFromFrames -FramesDir $RestoreDir -OutputVideoPath $RestoreVideoPath -Fps $FrameExtractionFps
} else {
    Write-Host "Skipping video restoration step" -ForegroundColor Yellow
}

# ============================================
# Step 4: BasicVSR++ - Video Denoising
# ============================================
if (-not $SkipDenoise) {
    Write-Step "Step 4/4: BasicVSR++ - Video Denoising (denoise_results.py)"
    
    # Change to BasicVSR++ directory and run denoising; restrict method to supported set
    if (@('nlm','bilateral','gaussian','median','fast') -notcontains $DenoiseMethod) {
        Write-Host "Denoise method '$DenoiseMethod' is not supported. Falling back to 'nlm'." -ForegroundColor Yellow
        $DenoiseMethod = 'nlm'
    }
    $cmd = "cd `"$($Config.BasicVSRPath)`"; conda activate $($Config.BasicVSREnv); python demo/denoise_results.py `"$RestoreDir`" `"$DenoiseDir`" --method $DenoiseMethod --strength $DenoiseStrength --preserve-details --create-video --speed 0.4"
    Write-Host "Running command: $cmd" -ForegroundColor Gray
    Write-Host "Denoise params: Method=$DenoiseMethod, Strength=$DenoiseStrength" -ForegroundColor Gray
    
    Invoke-Expression $cmd
    if ($LASTEXITCODE -ne 0) { throw "BasicVSR++ denoising failed" }
    
    $denoiseCount = (Get-ChildItem -Path $DenoiseDir -Include "*.jpg","*.png","*.mp4" -Recurse).Count
    Write-Success "Denoising results saved: $DenoiseDir ($denoiseCount files)"
        
    # Create denoised video
    $DenoiseVideoDir = Join-Path (Split-Path $DenoiseDir -Parent) "${VideoBaseName}_denoise_video"
    New-Item -ItemType Directory -Force -Path $DenoiseVideoDir | Out-Null
    $DenoiseVideoPath = Join-Path $DenoiseVideoDir "${VideoBaseName}_denoise.mp4"
    Create-VideoFromFrames -FramesDir $DenoiseDir -OutputVideoPath $DenoiseVideoPath -Fps $FrameExtractionFps
    
    # Copy final results to results folder
    Write-Host "Copying final results to results folder..." -ForegroundColor Gray
    if (-not (Test-Path $ResultsDir)) { New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null }
    Copy-Item -Path "$DenoiseDir\*" -Destination $ResultsDir -Recurse -Force
    if (Test-Path $DenoiseVideoPath) { Copy-Item -Path $DenoiseVideoPath -Destination $ResultsDir -Force }
    $resultCount = (Get-ChildItem -Path $ResultsDir -Include "*.jpg","*.png","*.mp4" -Recurse).Count
    Write-Success "Final results saved: $ResultsDir ($resultCount files)"
} else {
    Write-Host "Skipping denoising step" -ForegroundColor Yellow
    # If skipping denoise, copy restoration results to results
    Write-Host "Copying restoration results to results folder..." -ForegroundColor Gray
    if (-not (Test-Path $ResultsDir)) { New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null }
    Copy-Item -Path "$RestoreDir\*" -Destination $ResultsDir -Recurse -Force
    Write-Success "Results saved to: $ResultsDir"
}

    # Display result file list per video
    $resultFiles = Get-ChildItem -Path $ResultsDir -File -ErrorAction SilentlyContinue
    if ($resultFiles -and $resultFiles.Count -gt 0) {
        Write-Host "Generated files for ${VideoBaseName}:" -ForegroundColor Cyan
        foreach ($file in $resultFiles) {
            $sizeKB = [math]::Round($file.Length / 1KB, 2)
            Write-Host "  - $($file.Name) ($sizeKB KB)"
        }
    }
}

# ============================================
# Completion
# ============================================
$EndTime = Get-Date
$Duration = $EndTime - $StartTime

Write-Step "Processing Complete!"
Write-Host "Total time: $($Duration.ToString('hh\:mm\:ss'))" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Folder Structure (SuperVideo-inpaint):" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  raw_video/                    Input videos"
Write-Host "  |- mask_package/              Step 1: Mask generation"
Write-Host "  |   |- <video>_mask/          Binary mask frames"
Write-Host "  |   \- <video>_mask_video/    Mask video (mp4)" -ForegroundColor Yellow
Write-Host "  |- frames_package/            Video frames extraction"
Write-Host "  |   \- <video>_frames/        Original video frames"
Write-Host "  |- inpaint_package/           Step 2: Video inpainting"
Write-Host "  |   |- <video>_inpaint/       Inpainted frames"
Write-Host "  |   \- <video>_inpaint_video/ Inpainted video (mp4)" -ForegroundColor Yellow
Write-Host "  |- restore_package/           Step 3: Video restoration"
Write-Host "  |   |- <video>_restore/       Restored frames"
Write-Host "  |   \- <video>_restore_video/ Restored video (mp4)" -ForegroundColor Yellow
Write-Host "  |- denoise_package/           Step 4: Video denoising"
Write-Host "  |   |- <video>_denoise/       Denoised frames"
Write-Host "  |   \- <video>_denoise_video/ Denoised video (mp4)" -ForegroundColor Yellow
Write-Host "  \- results/                   [FINAL RESULTS]" -ForegroundColor Green
Write-Host ""
Write-Host "Final results location: $($Config.ResultsDir)" -ForegroundColor Green
Write-Host ""
Write-Success "Batch pipeline completed successfully!"

# Return to project root directory
Set-Location -Path $Config.ProjectRoot
Write-Host "Returned to project root: $($Config.ProjectRoot)" -ForegroundColor Gray

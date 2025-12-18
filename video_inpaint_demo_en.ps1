<#
.SYNOPSIS
    Video Inpainting Demo Pipeline - Simplified Workflow for Demo Videos
    
.DESCRIPTION
    Processes videos from demo_video folder and saves results to demo_output folder.
    Integrates SAMWISE (mask generation) + E2FGVI (video inpainting) + BasicVSR++ (enhancement/denoising)
    
.PARAMETER VideoPath
    Video file path in demo_video folder (e.g., "alita1.mp4" or "demo_video\alita1.mp4")
    
.PARAMETER TextPrompt
    Text prompt for SAMWISE to identify the target object for removal
    
.PARAMETER SkipMask
    Skip mask generation step (use existing masks)
    
.PARAMETER SkipInpaint
    Skip inpainting step
    
.PARAMETER SkipEnhance
    Skip enhancement step
    
.PARAMETER SkipDenoise
    Skip denoising step
    
.PARAMETER NeighborStride
    E2FGVI neighbor stride parameter (default: 3, smaller = better quality but slower)
    
.PARAMETER MaxLoadFrames
    E2FGVI max frames to load at once (default: 4, reduce if GPU memory insufficient)
    
.PARAMETER MaxResolution
    Maximum resolution for frame processing - longer edge (default: 720, 0 = no resize)
    
.PARAMETER FrameExtractionFps
    Frame extraction rate from video in FPS (default: 10 frames per second)
    
.PARAMETER VideoSpeedMultiplier
    Output video speed multiplier (default: 1.0, 2.0 = 2x speed)
    
.PARAMETER DenoiseMethod
    Denoising method: nlm/bilateral/gaussian (default: nlm)
    
.PARAMETER DenoiseStrength
    Denoising strength level 1-10 (default: 5)
    
.PARAMETER ForceCPU
    Force CPU processing for restoration to avoid GPU memory issues
    
.PARAMETER SegmentSize
    Process frames in segments to reduce memory usage (0 = disabled, default: 0)
    
.EXAMPLE
    .\video_inpaint_demo.ps1 -VideoPath "alita1.mp4" -TextPrompt "the flying chains and its lips"
    
.EXAMPLE
    .\video_inpaint_demo.ps1 -VideoPath "demo_video\sample.mp4" -TextPrompt "the person" -MaxResolution 1080
    
.EXAMPLE
    .\video_inpaint_demo.ps1 -VideoPath "test.mp4" -TextPrompt "the object" -SkipEnhance -SkipDenoise
#>

param(
    [Parameter(Mandatory=$true)]
    [string]$VideoPath,
    
    [Parameter(Mandatory=$true)]
    [string]$TextPrompt,
    
    [switch]$SkipMask,
    [switch]$SkipInpaint,
    [switch]$SkipEnhance,
    [switch]$SkipDenoise,
    
    [int]$NeighborStride = 3,
    [int]$MaxLoadFrames = 4,
    [int]$SegmentSize = 0,
    [switch]$ForceCPU,
    [int]$MaxResolution = 720,
    [int]$FrameExtractionFps = 10,
    [float]$VideoSpeedMultiplier = 1.0,
    [string]$DenoiseMethod = "nlm",
    [int]$DenoiseStrength = 5
)

# ============================================
# Demo Configuration
# ============================================
$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"


# ===============================
# 修改输出目录为PEANUT主目录下的demo\demo_output
# ===============================
$PeanutRoot = "C:\Users\Aiur\PEANUT\PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit"
$Config = @{
    # Conda configuration
    CondaPath = "C:\Users\Aiur\miniconda3\Scripts\conda.exe"

    # Project paths
    ProjectRoot = $ProjectRoot
    SamwisePath = Join-Path $ProjectRoot "SAMWISE"
    E2FGVIPath = Join-Path $ProjectRoot "E2FGVI_Project\E2FGVI"
    BasicVSRPath = Join-Path $ProjectRoot "BasicVSR_PlusPlus"

    # Demo-specific folders
    DemoVideoDir = Join-Path $ProjectRoot "demo_video"
    DemoOutputDir = Join-Path $PeanutRoot "demo\demo_output"

    # Working directories (temporary processing)
    FramesPackageDir = Join-Path $ProjectRoot "frames_package"
    MaskPackageDir = Join-Path $ProjectRoot "mask_package"
    InpaintPackageDir = Join-Path $ProjectRoot "inpaint_package"
    RestorePackageDir = Join-Path $ProjectRoot "restore_package"
    DenoisePackageDir = Join-Path $ProjectRoot "denoise_package"

    # Conda environment names
    SamwiseEnv = "samwise"
    E2FGVIEnv = "e2fgvi-project"
    BasicVSREnv = "basicvsrpp-demo"

    # E2FGVI model configuration
    E2FGVIModel = "e2fgvi_hq"
    E2FGVICheckpoint = Join-Path $ProjectRoot "E2FGVI_Project\E2FGVI\release_model\E2FGVI-HQ-CVPR22.pth"

    # BasicVSR++ model configuration
    BasicVSRConfig = Join-Path $ProjectRoot "BasicVSR_PlusPlus\configs\basicvsr_plusplus_reds4.py"
    BasicVSRCheckpoint = Join-Path $ProjectRoot "BasicVSR_PlusPlus\checkpoints\basicvsr_plusplus_reds4.pth"
}

# ============================================
# Helper Functions
# ============================================

function Write-Step {
    param([string]$Message)
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host $Message -ForegroundColor Cyan
    Write-Host "========================================`n" -ForegroundColor Cyan
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Yellow
}

function Activate-CondaEnv {
    param([string]$EnvName)
    
    Write-Info "Activating conda environment: $EnvName"
    
    $condaHook = "C:\Users\Aiur\miniconda3\shell\condabin\conda-hook.ps1"
    if (Test-Path $condaHook) {
        & $condaHook
        conda activate $EnvName
        if ($LASTEXITCODE -eq 0) {
            Write-Success "Environment activated: $EnvName"
            return $true
        }
    }
    
    Write-Error-Custom "Failed to activate environment: $EnvName"
    return $false
}

function Resize-Frames {
    param(
        [string]$InputDir,
        [string]$OutputDir,
        [int]$MaxResolution
    )
    
    if ($MaxResolution -eq 0) {
        Write-Info "Frame resizing disabled (MaxResolution = 0)"
        return $true
    }
    
    if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null }
    
    $resizeScript = @"
import cv2
import os
from pathlib import Path

input_dir = r'$InputDir'
output_dir = r'$OutputDir'
max_res = $MaxResolution

for file in sorted(Path(input_dir).glob('*.png')):
    img = cv2.imread(str(file))
    h, w = img.shape[:2]
    
    if max(h, w) > max_res:
        if h > w:
            new_h = max_res
            new_w = int(w * max_res / h)
        else:
            new_w = max_res
            new_h = int(h * max_res / w)
        
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)
    
    cv2.imwrite(os.path.join(output_dir, file.name), img)

print(f'Resized frames saved to: {output_dir}')
"@
    
    # Activate e2fgvi-project environment (has cv2)
    $condaHook = "C:\Users\Aiur\miniconda3\shell\condabin\conda-hook.ps1"
    if (Test-Path $condaHook) {
        & $condaHook
        conda activate e2fgvi-project | Out-Null
    }
    $resizeScript | python
    return $LASTEXITCODE -eq 0
}

# ============================================
# Input Validation
# ============================================

# Parse video path - support both relative and full paths
$VideoFile = $null
if ($VideoPath -match "demo_video") {
    # If path contains "demo_video", extract filename
    $VideoFile = Split-Path $VideoPath -Leaf
} elseif (Test-Path $VideoPath) {
    # If it's a valid full path
    $VideoFile = Split-Path $VideoPath -Leaf
} else {
    # Assume it's just the filename
    $VideoFile = $VideoPath
}

$VideoFullPath = Join-Path $Config.DemoVideoDir $VideoFile

if (-not (Test-Path $VideoFullPath)) {
    Write-Error-Custom "Video file not found: $VideoFullPath"
    Write-Info "Please place your video in: $($Config.DemoVideoDir)"
    exit 1
}

$VideoBaseName = [System.IO.Path]::GetFileNameWithoutExtension($VideoFile)

Write-Step "VIDEO INPAINTING DEMO - STARTING"
Write-Info "Input Video: $VideoFullPath"
Write-Info "Text Prompt: $TextPrompt"
Write-Info "Output Directory: $($Config.DemoOutputDir)"

# Create output directory
$ResultsDir = Join-Path $Config.DemoOutputDir "${VideoBaseName}_result"
if (-not (Test-Path $ResultsDir)) {
    New-Item -ItemType Directory -Force -Path $ResultsDir | Out-Null
}

# ============================================
# STEP 1: Extract Frames
# ============================================

Write-Step "STEP 1: EXTRACTING FRAMES FROM VIDEO"

$FramesDir = Join-Path $Config.FramesPackageDir $VideoBaseName
if (-not (Test-Path $FramesDir)) { New-Item -ItemType Directory -Force -Path $FramesDir | Out-Null }

$extractScript = @"
import cv2
import os

video_path = r'$VideoFullPath'
output_dir = r'$FramesDir'
fps = $FrameExtractionFps

cap = cv2.VideoCapture(video_path)
video_fps = cap.get(cv2.CAP_PROP_FPS)
frame_interval = max(1, int(video_fps / fps))

frame_count = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    if frame_count % frame_interval == 0:
        cv2.imwrite(os.path.join(output_dir, f'{saved_count:05d}.png'), frame)
        saved_count += 1
    
    frame_count += 1

cap.release()
print(f'Extracted {saved_count} frames to: {output_dir}')
"@

# Activate e2fgvi-project environment which has cv2
Activate-CondaEnv $Config.E2FGVIEnv
$extractScript | python

if ($LASTEXITCODE -ne 0) {
    Write-Error-Custom "Frame extraction failed"
    exit 1
}

Write-Success "Frames extracted successfully"

# ============================================
# STEP 2: Generate Masks with SAMWISE
# ============================================

if (-not $SkipMask) {
    Write-Step "STEP 2: GENERATING MASKS WITH SAMWISE"
    
    Set-Location $Config.SamwisePath
    Activate-CondaEnv $Config.SamwiseEnv
    
    # SAMWISE creates folder based on text prompt only, not including video name
    $PromptFolderName = $TextPrompt -replace '[^\w\-]', '_'
    $SamwiseMaskOutput = "demo_output"
    
    Write-Info "Running SAMWISE mask generation..."
    Write-Info "Expected SAMWISE output folder: $PromptFolderName"
    python inference_demo.py `
        --input_path $FramesDir `
        --text_prompts $TextPrompt
    
    if ($LASTEXITCODE -ne 0) {
        Set-Location $ProjectRoot
        Write-Error-Custom "SAMWISE mask generation failed"
        exit 1
    }
    
    # Copy masks to mask package directory
    $MaskDir = Join-Path $Config.MaskPackageDir "${VideoBaseName}_mask"
    if (-not (Test-Path $MaskDir)) { New-Item -ItemType Directory -Force -Path $MaskDir | Out-Null }
    
    # Find binary masks folder - SAMWISE names it based on prompt only
    $samwiseDemoOutput = Join-Path $Config.SamwisePath $SamwiseMaskOutput
    $binaryMasksFolderName = "${PromptFolderName}_binary_masks"
    $binaryMasksPath = Join-Path $samwiseDemoOutput $binaryMasksFolderName
    
    if (Test-Path $binaryMasksPath) {
        Copy-Item -Path "$binaryMasksPath\*" -Destination $MaskDir -Force -Recurse
        Write-Success "Masks copied from: $binaryMasksPath"
    } else {
        Write-Warning "Binary masks not found at: $binaryMasksPath"
        Write-Info "Searching for any binary_masks folder..."
        $binaryMasksFolder = Get-ChildItem -Path $samwiseDemoOutput -Directory -Filter "*_binary_masks" | 
                             Where-Object { $_.Name -like "*$($TextPrompt -replace '[^\w\-]', '_')*" } | 
                             Select-Object -First 1
        if ($binaryMasksFolder) {
            Copy-Item -Path "$($binaryMasksFolder.FullName)\*" -Destination $MaskDir -Force -Recurse
            Write-Success "Masks copied from: $($binaryMasksFolder.FullName)"
        } else {
            Write-Error-Custom "Could not find binary masks for prompt: $TextPrompt"
        }
    }
    
    Write-Success "Masks generated and copied to: $MaskDir"
    Set-Location $ProjectRoot
} else {
    Write-Info "Skipping mask generation (using existing masks)"
    $MaskDir = Join-Path $Config.MaskPackageDir "${VideoBaseName}_mask"
}

# ============================================
# STEP 3: Resize Frames and Masks
# ============================================

Write-Step "STEP 3: RESIZING FRAMES AND MASKS"

$FramesDirResized = Join-Path $Config.FramesPackageDir "${VideoBaseName}_resized"
$MaskDirResized = Join-Path $Config.MaskPackageDir "${VideoBaseName}_mask_resized"

$resizeSuccess = Resize-Frames -InputDir $FramesDir -OutputDir $FramesDirResized -MaxResolution $MaxResolution
if (-not $resizeSuccess) {
    Write-Error-Custom "Frame resizing failed"
    exit 1
}

$resizeSuccess = Resize-Frames -InputDir $MaskDir -OutputDir $MaskDirResized -MaxResolution $MaxResolution
if (-not $resizeSuccess) {
    Write-Error-Custom "Mask resizing failed"
    exit 1
}

Write-Success "Frames and masks resized successfully"

# Verify frame and mask counts match
$frameCount = (Get-ChildItem -Path $FramesDirResized -Filter "*.png").Count
$maskCount = (Get-ChildItem -Path $MaskDirResized -Filter "*.png").Count

Write-Info "Frame count: $frameCount, Mask count: $maskCount"

if ($frameCount -ne $maskCount) {
    Write-Warning "Frame count ($frameCount) does not match mask count ($maskCount)"
    Write-Info "This may cause E2FGVI to fail. Consider regenerating masks or adjusting frame extraction."
    
    # Option: Skip to avoid error
    if ($maskCount -lt $frameCount) {
        Write-Error-Custom "Insufficient masks for frames. Please regenerate masks with -SkipMask:`$false"
        exit 1
    }
}

# ============================================
# STEP 4: Video Inpainting with E2FGVI
# ============================================

if (-not $SkipInpaint) {
    Write-Step "STEP 4: VIDEO INPAINTING WITH E2FGVI"
    
    Set-Location $Config.E2FGVIPath
    Activate-CondaEnv $Config.E2FGVIEnv
    
    $E2FGVIResultsDir = Join-Path $Config.InpaintPackageDir $VideoBaseName
    if (-not (Test-Path $E2FGVIResultsDir)) { 
        New-Item -ItemType Directory -Force -Path $E2FGVIResultsDir | Out-Null 
    }
    
    Write-Info "Running E2FGVI video inpainting..."
    
    # Set CUDA memory config
    $env:PYTORCH_CUDA_ALLOC_CONF = "expandable_segments:True"
    
    python test.py `
        --model $Config.E2FGVIModel `
        --video $FramesDirResized `
        --mask $MaskDirResized `
        --ckpt $Config.E2FGVICheckpoint `
        --neighbor_stride $NeighborStride `
        --max_load_frames $MaxLoadFrames `
        --no-show
    
    if ($LASTEXITCODE -ne 0) {
        Set-Location $ProjectRoot
        Write-Error-Custom "E2FGVI inpainting failed"
        exit 1
    }
    
    # Find and copy E2FGVI results
    $e2fgviOutput = Get-ChildItem -Path (Join-Path $Config.E2FGVIPath "results") -Directory | 
                    Sort-Object LastWriteTime -Descending | 
                    Select-Object -First 1
    
    if ($e2fgviOutput) {
        Copy-Item -Path "$($e2fgviOutput.FullName)\*" -Destination $E2FGVIResultsDir -Force -Recurse
        Write-Success "Inpainting completed: $E2FGVIResultsDir"
    }
    
    Set-Location $ProjectRoot
} else {
    Write-Info "Skipping inpainting step"
    $E2FGVIResultsDir = Join-Path $Config.InpaintPackageDir $VideoBaseName
}

# ============================================
# STEP 5: Enhancement with BasicVSR++
# ============================================

if (-not $SkipEnhance) {
    Write-Step "STEP 5: ENHANCEMENT WITH BASICVSR++"
    
    Set-Location $Config.BasicVSRPath
    Activate-CondaEnv $Config.BasicVSREnv
    
    $framesFolderName = (Get-ChildItem -Path $E2FGVIResultsDir -Directory | Select-Object -First 1).Name
    $E2FGVIFramesOutput = Join-Path $E2FGVIResultsDir $framesFolderName
    
    $RestoreDir = Join-Path $Config.RestorePackageDir $VideoBaseName
    if (-not (Test-Path $RestoreDir)) { 
        New-Item -ItemType Directory -Force -Path $RestoreDir | Out-Null 
    }
    
    Write-Info "Running BasicVSR++ enhancement..."
    
    $deviceArg = if ($ForceCPU) { "cpu" } else { "cuda:0" }
    
    python demo/restoration_video_demo.py `
        $Config.BasicVSRConfig `
        $Config.BasicVSRCheckpoint `
        $E2FGVIFramesOutput `
        $RestoreDir `
        --device $deviceArg `
        --fps $FrameExtractionFps `
        --max-seq-len 12
    
    if ($LASTEXITCODE -ne 0) {
        Set-Location $ProjectRoot
        Write-Error-Custom "BasicVSR++ enhancement failed"
        exit 1
    }
    
    Write-Success "Enhancement completed: $RestoreDir"
    Set-Location $ProjectRoot
} else {
    Write-Info "Skipping enhancement step"
}

# ============================================
# STEP 6: Denoising (Optional)
# ============================================

if (-not $SkipDenoise) {
    Write-Step "STEP 6: DENOISING"
    
    $DenoiseDir = Join-Path $Config.DenoisePackageDir $VideoBaseName
    if (-not (Test-Path $DenoiseDir)) { 
        New-Item -ItemType Directory -Force -Path $DenoiseDir | Out-Null 
    }
    
    $denoiseScript = @"
import cv2
import os
from pathlib import Path

input_dir = r'$RestoreDir'
output_dir = r'$DenoiseDir'
method = '$DenoiseMethod'
strength = $DenoiseStrength

for file in sorted(Path(input_dir).glob('*.png')):
    img = cv2.imread(str(file))
    
    if method == 'nlm':
        denoised = cv2.fastNlMeansDenoisingColored(img, None, strength, strength, 7, 21)
    elif method == 'bilateral':
        denoised = cv2.bilateralFilter(img, 9, strength * 15, strength * 15)
    elif method == 'gaussian':
        denoised = cv2.GaussianBlur(img, (5, 5), strength / 5)
    else:
        denoised = img
    
    cv2.imwrite(os.path.join(output_dir, file.name), denoised)

print(f'Denoising completed: {output_dir}')
"@
    
    # Activate e2fgvi-project environment (has cv2)
    Activate-CondaEnv $Config.E2FGVIEnv
    $denoiseScript | python
    
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Denoising completed: $DenoiseDir"
    } else {
        Write-Error-Custom "Denoising failed"
    }
} else {
    Write-Info "Skipping denoising step"
}

# ============================================
# STEP 7: Create Final Output Video
# ============================================

Write-Step "STEP 7: CREATING FINAL OUTPUT VIDEO"

$FinalFramesDir = if (-not $SkipDenoise) { $DenoiseDir } 
                  elseif (-not $SkipEnhance) { $RestoreDir }
                  else { $E2FGVIFramesOutput }

$OutputVideoPath = Join-Path $ResultsDir "${VideoBaseName}_final.mp4"

$createVideoScript = @"
import cv2
import os
from pathlib import Path

frames_dir = r'$FinalFramesDir'
output_video = r'$OutputVideoPath'
fps = $FrameExtractionFps * $VideoSpeedMultiplier

frames = sorted(Path(frames_dir).glob('*.png'))
if not frames:
    print('ERROR: No frames found')
    exit(1)

first_frame = cv2.imread(str(frames[0]))
height, width = first_frame.shape[:2]

fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter(output_video, fourcc, fps, (width, height))

for frame_path in frames:
    frame = cv2.imread(str(frame_path))
    out.write(frame)

out.release()
print(f'Video created: {output_video}')
"@

# Activate e2fgvi-project environment (has cv2)
Activate-CondaEnv $Config.E2FGVIEnv
$createVideoScript | python

if ($LASTEXITCODE -eq 0 -and (Test-Path $OutputVideoPath)) {
    Write-Success "Final video created: $OutputVideoPath"
} else {
    Write-Error-Custom "Failed to create final video"
    exit 1
}

# ============================================
# Summary
# ============================================

Write-Step "DEMO PIPELINE COMPLETED SUCCESSFULLY"

Write-Host "`nResults saved to:" -ForegroundColor Green
Write-Host "  Output Directory: $ResultsDir" -ForegroundColor Cyan
Write-Host "  Final Video: $OutputVideoPath" -ForegroundColor Cyan

Write-Host "`nProcessing Summary:" -ForegroundColor Yellow
Write-Host "  - Frames extracted: $FramesDir"
Write-Host "  - Masks generated: $MaskDir"
Write-Host "  - Inpainting: $E2FGVIResultsDir"
if (-not $SkipEnhance) { Write-Host "  - Enhancement: $RestoreDir" }
if (-not $SkipDenoise) { Write-Host "  - Denoising: $DenoiseDir" }

Write-Host "`nYou can find all results in: $($Config.DemoOutputDir)" -ForegroundColor Green

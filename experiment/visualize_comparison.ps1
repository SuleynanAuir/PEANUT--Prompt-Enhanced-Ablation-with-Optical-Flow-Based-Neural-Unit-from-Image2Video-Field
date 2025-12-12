<#
.SYNOPSIS
    Visual Comparison Generator for SAMWISE Experiments
    Creates side-by-side frame comparisons across different parameter configurations
    
.PARAMETER ExperimentName
    Name of the experiment to visualize
    
.PARAMETER FrameNumbers
    Specific frame numbers to compare (e.g., 1,10,20,30)
    
.PARAMETER OutputDir
    Output directory for comparison images
    
.EXAMPLE
    .\visualize_comparison.ps1 -ExperimentName "exp1" -FrameNumbers 1,10,20
#>

param(
    [string]$ExperimentName = "exp1",
    [int[]]$FrameNumbers = @(1, 5, 10, 15, 20),
    [string]$OutputDir = ""
)

$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"
$ExperimentRoot = Join-Path $ProjectRoot "experiment"
$ExperimentDir = Join-Path $ExperimentRoot $ExperimentName
$ResultsDir = Join-Path $ExperimentDir "samwise_results"
$VisualizationDir = if ($OutputDir) { $OutputDir } else { Join-Path $ExperimentDir "visualizations" }

# Create visualization directory
if (-not (Test-Path $VisualizationDir)) {
    New-Item -ItemType Directory -Force -Path $VisualizationDir | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SAMWISE Comparison Visualization" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Find all test result directories
$testDirs = Get-ChildItem -Path $ResultsDir -Directory | Where-Object { 
    $_.Name -match "threshold_|model_|window_" 
}

if ($testDirs.Count -eq 0) {
    Write-Host "No test results found in: $ResultsDir" -ForegroundColor Red
    exit 1
}

Write-Host "Found $($testDirs.Count) test configurations:" -ForegroundColor Green
$testDirs | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
Write-Host ""

# Create Python visualization script
$pythonScript = @"
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import glob

def create_comparison_grid(test_dirs, frame_num, output_path, source_frames_dir):
    """Create a grid comparing original frame with masks from different tests"""
    
    images = []
    labels = []
    
    # Load original frame
    original_path = os.path.join(source_frames_dir, f'frame_{frame_num:05d}.png')
    if os.path.exists(original_path):
        img = Image.open(original_path).convert('RGB')
        images.append(img)
        labels.append('Original Frame')
    else:
        print(f'Warning: Original frame not found: {original_path}')
        # Create placeholder
        if len(images) > 0:
            img = Image.new('RGB', images[0].size, color=(50, 50, 50))
        else:
            img = Image.new('RGB', (640, 480), color=(50, 50, 50))
        images.append(img)
        labels.append('Original (Missing)')
    
    # Load mask from each test
    for test_dir in test_dirs:
        test_name = os.path.basename(test_dir)
        
        # Find mask directory
        mask_dirs = glob.glob(os.path.join(test_dir, '*_binary_masks'))
        
        if mask_dirs:
            mask_path = os.path.join(mask_dirs[0], f'{frame_num:05d}.png')
            
            if os.path.exists(mask_path):
                mask_img = Image.open(mask_path).convert('RGB')
                images.append(mask_img)
                
                # Parse label from test name
                if 'threshold' in test_name:
                    threshold = test_name.split('_')[1]
                    labels.append(f'Threshold={threshold}')
                elif 'model' in test_name:
                    model = test_name.split('_')[1]
                    labels.append(f'Model={model}')
                elif 'window' in test_name:
                    window = test_name.split('_')[1]
                    labels.append(f'Window={window}')
                else:
                    labels.append(test_name)
            else:
                print(f'Warning: Mask not found: {mask_path}')
        else:
            print(f'Warning: No mask directory in {test_dir}')
    
    if len(images) == 0:
        print(f'Error: No images found for frame {frame_num}')
        return False
    
    # Calculate grid dimensions
    num_images = len(images)
    cols = min(4, num_images)
    rows = (num_images + cols - 1) // cols
    
    # Get image dimensions
    img_width, img_height = images[0].size
    label_height = 50
    padding = 10
    
    # Create grid
    grid_width = cols * img_width + (cols + 1) * padding
    grid_height = rows * (img_height + label_height) + (rows + 1) * padding
    
    grid = Image.new('RGB', (grid_width, grid_height), color=(240, 240, 240))
    draw = ImageDraw.Draw(grid)
    
    # Try to load font
    try:
        font = ImageFont.truetype('arial.ttf', 20)
        font_small = ImageFont.truetype('arial.ttf', 16)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    # Place images in grid
    for idx, (img, label) in enumerate(zip(images, labels)):
        row = idx // cols
        col = idx % cols
        
        x = col * (img_width + padding) + padding
        y = row * (img_height + label_height + padding) + padding
        
        # Paste image
        grid.paste(img, (x, y))
        
        # Draw label
        label_y = y + img_height + 5
        
        # Draw label background
        label_bbox = draw.textbbox((0, 0), label, font=font_small)
        label_width = label_bbox[2] - label_bbox[0]
        label_bg_x1 = x + (img_width - label_width) // 2 - 5
        label_bg_x2 = label_bg_x1 + label_width + 10
        label_bg_y1 = label_y - 2
        label_bg_y2 = label_y + 25
        
        draw.rectangle([label_bg_x1, label_bg_y1, label_bg_x2, label_bg_y2], 
                      fill=(255, 255, 255), outline=(100, 100, 100))
        
        # Draw text centered
        text_x = x + (img_width - label_width) // 2
        draw.text((text_x, label_y), label, fill=(0, 0, 0), font=font_small)
    
    # Add title
    title = f'Frame {frame_num:05d} - Comparison Across Configurations'
    title_bbox = draw.textbbox((0, 0), title, font=font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (grid_width - title_width) // 2
    draw.text((title_x, 5), title, fill=(0, 0, 0), font=font)
    
    # Save
    grid.save(output_path, quality=95)
    print(f'Created: {output_path}')
    return True

def create_montage(test_dirs, frame_numbers, output_dir, source_frames_dir):
    """Create comparison grids for multiple frames"""
    
    success_count = 0
    
    for frame_num in frame_numbers:
        output_path = os.path.join(output_dir, f'comparison_frame_{frame_num:05d}.png')
        
        if create_comparison_grid(test_dirs, frame_num, output_path, source_frames_dir):
            success_count += 1
    
    return success_count

# Main execution
if __name__ == '__main__':
    import json
    
    # Read parameters from command line
    config_json = sys.argv[1]
    
    with open(config_json, 'r') as f:
        config = json.load(f)
    
    test_dirs = config['test_dirs']
    frame_numbers = config['frame_numbers']
    output_dir = config['output_dir']
    source_frames_dir = config['source_frames_dir']
    
    print(f'Creating comparisons for {len(frame_numbers)} frames...')
    print(f'Test configurations: {len(test_dirs)}')
    print(f'Output directory: {output_dir}')
    print('')
    
    success = create_montage(test_dirs, frame_numbers, output_dir, source_frames_dir)
    
    print('')
    print(f'Successfully created {success} comparison images')
    
    sys.exit(0 if success > 0 else 1)
"@

$pythonScriptPath = Join-Path $VisualizationDir "create_comparison.py"
Set-Content -Path $pythonScriptPath -Value $pythonScript -Encoding UTF8

# Find source frames directory (from SAMWISE output)
$sourceFramesDir = ""
$firstTestDir = Get-ChildItem -Path $ResultsDir -Directory | Select-Object -First 1

if ($firstTestDir) {
    # Try to find frames in SAMWISE directory
    $videoBaseName = "alita1_test"  # Adjust based on actual video
    $samwiseFramesDir = Join-Path $ProjectRoot "SAMWISE\frames_$videoBaseName"
    
    if (Test-Path $samwiseFramesDir) {
        $sourceFramesDir = $samwiseFramesDir
    } else {
        # Try to find in experiment directory
        $expFramesDir = Join-Path $ExperimentRoot "exp_raw_video\frames"
        if (Test-Path $expFramesDir) {
            $sourceFramesDir = $expFramesDir
        }
    }
}

if (-not $sourceFramesDir -or -not (Test-Path $sourceFramesDir)) {
    Write-Host "Source frames directory not found. Extracting frames from video..." -ForegroundColor Yellow
    
    # Extract frames from video
    $videoPath = Join-Path $ExperimentRoot "exp_raw_video\alita1_test.mp4"
    $extractFramesDir = Join-Path $VisualizationDir "source_frames"
    
    if (-not (Test-Path $extractFramesDir)) {
        New-Item -ItemType Directory -Force -Path $extractFramesDir | Out-Null
    }
    
    Write-Host "Extracting frames from: $videoPath" -ForegroundColor Cyan
    
    # Use ffmpeg to extract frames
    $ffmpegCmd = "conda run -n e2fgvi-project ffmpeg -i `"$videoPath`" -vf fps=10 `"$extractFramesDir\frame_%05d.png`" -y"
    cmd /c $ffmpegCmd
    
    $sourceFramesDir = $extractFramesDir
}

Write-Host "Using source frames from: $sourceFramesDir" -ForegroundColor Green
Write-Host ""

# Create config JSON for Python script
$config = @{
    test_dirs = @($testDirs | ForEach-Object { $_.FullName })
    frame_numbers = $FrameNumbers
    output_dir = $VisualizationDir
    source_frames_dir = $sourceFramesDir
} | ConvertTo-Json -Depth 10

$configPath = Join-Path $VisualizationDir "comparison_config.json"
Set-Content -Path $configPath -Value $config -Encoding UTF8

# Run Python script
Write-Host "Generating comparison visualizations..." -ForegroundColor Cyan
Write-Host ""

try {
    $pythonCmd = "conda run -n e2fgvi-project python `"$pythonScriptPath`" `"$configPath`""
    cmd /c $pythonCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "Visualization Complete!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Output directory: $VisualizationDir" -ForegroundColor Yellow
        Write-Host ""
        
        # List generated files
        $comparisonFiles = Get-ChildItem -Path $VisualizationDir -Filter "comparison_*.png"
        Write-Host "Generated $($comparisonFiles.Count) comparison images:" -ForegroundColor Green
        $comparisonFiles | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor Gray }
        Write-Host ""
        
        # Open first image
        if ($comparisonFiles.Count -gt 0) {
            $firstImage = $comparisonFiles[0].FullName
            Write-Host "Opening first comparison..." -ForegroundColor Cyan
            Start-Process $firstImage
        }
        
        # Create index HTML
        $htmlIndex = @"
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>SAMWISE Comparison Gallery - $ExperimentName</title>
    <style>
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            margin: 0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 40px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
        }
        h2 {
            color: #764ba2;
            margin-top: 30px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 20px;
        }
        .gallery-item {
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            transition: transform 0.3s, box-shadow 0.3s;
            background: white;
        }
        .gallery-item:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.2);
        }
        .gallery-item img {
            width: 100%;
            display: block;
            cursor: pointer;
        }
        .gallery-item-caption {
            padding: 15px;
            background: #f8f9fa;
            text-align: center;
            font-weight: 600;
            color: #333;
        }
        .info-box {
            background: #e8f5e9;
            border-left: 4px solid #00c853;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }
        .info-box h3 {
            margin-top: 0;
            color: #00897b;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SAMWISE Experiment Comparison Gallery</h1>
        <p class="subtitle">Experiment: $ExperimentName | Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        
        <div class="info-box">
            <h3>How to Read These Comparisons</h3>
            <p><strong>Layout:</strong> Each image shows a side-by-side comparison of the original frame with masks generated using different parameter configurations.</p>
            <p><strong>Purpose:</strong> Visualize the impact of different hyperparameters (Threshold, Model, Window) on mask quality and coverage.</p>
            <p><strong>Tip:</strong> Click on any image to view it in full size.</p>
        </div>
        
        <h2>Frame Comparisons</h2>
        <div class="gallery">
"@

        foreach ($file in $comparisonFiles) {
            $htmlIndex += @"
            <div class="gallery-item">
                <img src="$($file.Name)" alt="$($file.BaseName)" onclick="window.open(this.src)">
                <div class="gallery-item-caption">$($file.BaseName -replace 'comparison_', '' -replace '_', ' ')</div>
            </div>
"@
        }

        $htmlIndex += @"
        </div>
    </div>
</body>
</html>
"@

        $htmlIndexPath = Join-Path $VisualizationDir "index.html"
        Set-Content -Path $htmlIndexPath -Value $htmlIndex -Encoding UTF8
        
        Write-Host "Gallery index created: $htmlIndexPath" -ForegroundColor Green
        Write-Host ""
        Write-Host "To view all comparisons, open:" -ForegroundColor Yellow
        Write-Host "  Start-Process `"$htmlIndexPath`"" -ForegroundColor Cyan
        Write-Host ""
        
    } else {
        Write-Host "Error: Visualization script failed" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

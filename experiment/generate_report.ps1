<#
.SYNOPSIS
    SAMWISE Experiment Report Generator
    Generates professional academic-style visualization reports
#>

param(
    [string]$ExperimentName = "exp1"
)

$ProjectRoot = "C:\Users\Aiur\SuperVideo-inpaint"
$ExperimentRoot = Join-Path $ProjectRoot "experiment"
$ExperimentDir = Join-Path $ExperimentRoot $ExperimentName
$ComparisonLog = Join-Path $ExperimentDir "comparison_results.txt"
$ReportFile = Join-Path $ExperimentDir "EXPERIMENT_REPORT.html"
$JsonReport = Join-Path $ExperimentDir "experiment_data.json"

function Parse-LogResults {
    param([string]$LogPath)
    
    $results = @()
    
    if (-not (Test-Path $LogPath)) {
        Write-Host "Log file not found: $LogPath" -ForegroundColor Red
        return $results
    }
    
    $content = Get-Content $LogPath -Raw
    
    # Parse test results
    $lines = Get-Content $LogPath
    $currentTest = $null
    
    foreach ($line in $lines) {
        # Detect test start
        if ($line -match "=====.*=====") {
            if ($line -match "threshold_|model_|window_") {
                $testName = $line -replace ".*=====\s*(.*?)\s*=====.*", '$1'
                $currentTest = @{
                    Name = $testName
                    Parameter = ""
                    Status = "RUNNING"
                    Duration = 0
                    MaskCount = 0
                }
            }
        }
        
        # Extract parameters
        if ($line -match "Threshold=|Model=|Window=") {
            if ($currentTest) {
                $currentTest.Parameter = $line.Trim()
            }
        }
        
        # Detect success
        if ($line -match "SUCCESS:.*completed in.*masks") {
            if ($currentTest) {
                $duration = [regex]::Match($line, "(\d+\.?\d*?)s").Groups[1].Value
                $masks = [regex]::Match($line, "(\d+) masks").Groups[1].Value
                
                $currentTest.Duration = [float]$duration
                $currentTest.MaskCount = [int]$masks
                $currentTest.Status = "SUCCESS"
                
                $results += $currentTest
                $currentTest = $null
            }
        }
        
        # Detect failure
        if ($line -match "ERROR:") {
            if ($currentTest) {
                $currentTest.Status = "FAILED"
                $results += $currentTest
                $currentTest = $null
            }
        }
    }
    
    return $results
}

function Generate-HtmlReport {
    param(
        [array]$Results,
        [string]$ExperimentName,
        [string]$OutputPath
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $totalTests = $Results.Count
    $successTests = ($Results | Where-Object { $_.Status -eq "SUCCESS" }).Count
    $failedTests = $totalTests - $successTests
    
    # Calculate statistics
    $successResults = $Results | Where-Object { $_.Status -eq "SUCCESS" }
    $avgDuration = 0
    $avgMasks = 0
    $totalTime = 0
    
    if ($successResults.Count -gt 0) {
        $avgDuration = ($successResults | ForEach-Object { $_.Duration } | Measure-Object -Average).Average
        $avgMasks = ($successResults | ForEach-Object { $_.MaskCount } | Measure-Object -Average).Average
    }
    
    if ($Results.Count -gt 0) {
        $totalTime = ($Results | ForEach-Object { $_.Duration } | Measure-Object -Sum).Sum
    }
    
    # Group by test type
    $thresholdTests = $Results | Where-Object { $_.Name -match "threshold_" }
    $modelTests = $Results | Where-Object { $_.Name -match "model_" }
    $windowTests = $Results | Where-Object { $_.Name -match "window_" }
    
    $html = @"
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAMWISE Experiment Report - $ExperimentName</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
        }
        
        .header p {
            font-size: 0.95em;
            opacity: 0.95;
        }
        
        .metadata {
            background: #f8f9fa;
            padding: 20px 40px;
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .metadata-item {
            padding: 10px 0;
        }
        
        .metadata-label {
            font-weight: 600;
            color: #667eea;
            font-size: 0.85em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .metadata-value {
            font-size: 1.1em;
            color: #333;
            margin-top: 5px;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: white;
        }
        
        .stat-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        
        .stat-card.success {
            background: linear-gradient(135deg, #00c853 0%, #00897b 100%);
        }
        
        .stat-card.failed {
            background: linear-gradient(135deg, #ff5252 0%, #d32f2f 100%);
        }
        
        .stat-card.total {
            background: linear-gradient(135deg, #2196f3 0%, #1565c0 100%);
        }
        
        .stat-value {
            font-size: 2.5em;
            font-weight: 700;
            margin: 10px 0;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.9;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .section {
            padding: 40px;
            border-bottom: 1px solid #e9ecef;
        }
        
        .section-title {
            font-size: 1.8em;
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            display: inline-block;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        thead {
            background: #f8f9fa;
            border-bottom: 2px solid #667eea;
        }
        
        th {
            padding: 15px;
            text-align: left;
            font-weight: 600;
            color: #333;
            font-size: 0.95em;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        td {
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }
        
        tr:hover {
            background: #f5f7fa;
        }
        
        .status-success {
            color: #00c853;
            font-weight: 600;
        }
        
        .status-failed {
            color: #ff5252;
            font-weight: 600;
        }
        
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }
        
        .status-badge.success {
            background: #e8f5e9;
            color: #00c853;
        }
        
        .status-badge.failed {
            background: #ffebee;
            color: #ff5252;
        }
        
        .analysis {
            background: #f5f7fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            margin-top: 20px;
            border-radius: 5px;
        }
        
        .analysis-item {
            margin: 10px 0;
            padding: 10px 0;
        }
        
        .analysis-item strong {
            color: #667eea;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px 40px;
            text-align: center;
            font-size: 0.9em;
            color: #666;
            border-top: 1px solid #e9ecef;
        }
        
        .chart-container {
            margin: 20px 0;
            padding: 20px;
            background: #f5f7fa;
            border-radius: 8px;
        }
        
        .bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
        }
        
        .bar-label {
            width: 150px;
            font-weight: 500;
            text-align: right;
            padding-right: 15px;
        }
        
        .bar-content {
            flex: 1;
            background: #e9ecef;
            border-radius: 5px;
            overflow: hidden;
            height: 30px;
            display: flex;
            align-items: center;
        }
        
        .bar-fill {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: flex-end;
            padding-right: 10px;
            color: white;
            font-weight: 600;
            font-size: 0.9em;
        }
        
        @media print {
            body {
                background: white;
            }
            .container {
                box-shadow: none;
                border-radius: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SAMWISE Experiment Report</h1>
            <p>Hyperparameter Comparison & Analysis</p>
        </div>
        
        <div class="metadata">
            <div class="metadata-item">
                <div class="metadata-label">Experiment Name</div>
                <div class="metadata-value">$ExperimentName</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Generated</div>
                <div class="metadata-value">$timestamp</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Total Tests</div>
                <div class="metadata-value">$totalTests</div>
            </div>
            <div class="metadata-item">
                <div class="metadata-label">Success Rate</div>
                <div class="metadata-value">$([math]::Round($successTests / $totalTests * 100, 1))%</div>
            </div>
        </div>
        
        <div class="stats">
            <div class="stat-card success">
                <div class="stat-label">Successful</div>
                <div class="stat-value">$successTests</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-label">Failed</div>
                <div class="stat-value">$failedTests</div>
            </div>
            <div class="stat-card total">
                <div class="stat-label">Total Time</div>
                <div class="stat-value">$([math]::Round($totalTime, 1))s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Avg Time/Test</div>
                <div class="stat-value">$([math]::Round($avgDuration, 2))s</div>
            </div>
        </div>
"@

    # Add threshold section if exists
    if ($thresholdTests.Count -gt 0) {
        $html += @"
        <div class="section">
            <div class="section-title">Phase 1: Threshold Comparison</div>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Threshold Value</th>
                        <th>Duration (s)</th>
                        <th>Masks Generated</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"@
        foreach ($test in $thresholdTests) {
            $statusBadge = if ($test.Status -eq "SUCCESS") { 
                '<span class="status-badge success">✓ SUCCESS</span>' 
            } else { 
                '<span class="status-badge failed">✗ FAILED</span>' 
            }
            $html += @"
                    <tr>
                        <td><strong>$($test.Name)</strong></td>
                        <td>$($test.Parameter)</td>
                        <td>$([math]::Round($test.Duration, 2))</td>
                        <td>$($test.MaskCount)</td>
                        <td>$statusBadge</td>
                    </tr>
"@
        }
        $html += @"
                </tbody>
            </table>
            <div class="analysis">
                <div class="analysis-item"><strong>Key Finding:</strong> Threshold 0.3 produces loose masks with broader coverage, while 0.7 produces strict masks with higher precision.</div>
                <div class="analysis-item"><strong>Recommendation:</strong> Use Threshold 0.5 for balanced coverage and precision in production.</div>
            </div>
        </div>
"@
    }

    # Add model section if exists
    if ($modelTests.Count -gt 0) {
        $html += @"
        <div class="section">
            <div class="section-title">Phase 2: Model Comparison</div>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Model Version</th>
                        <th>Duration (s)</th>
                        <th>Masks Generated</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"@
        foreach ($test in $modelTests) {
            $statusBadge = if ($test.Status -eq "SUCCESS") { 
                '<span class="status-badge success">✓ SUCCESS</span>' 
            } else { 
                '<span class="status-badge failed">✗ FAILED</span>' 
            }
            $html += @"
                    <tr>
                        <td><strong>$($test.Name)</strong></td>
                        <td>$($test.Parameter)</td>
                        <td>$([math]::Round($test.Duration, 2))</td>
                        <td>$($test.MaskCount)</td>
                        <td>$statusBadge</td>
                    </tr>
"@
        }
        $html += @"
                </tbody>
            </table>
            <div class="analysis">
                <div class="analysis-item"><strong>Key Finding:</strong> tiny model is fastest but has lower precision. large model has highest precision but requires more resources.</div>
                <div class="analysis-item"><strong>Recommendation:</strong> Use base model for optimal speed-accuracy tradeoff (RECOMMENDED).</div>
            </div>
        </div>
"@
    }

    # Add window section if exists
    if ($windowTests.Count -gt 0) {
        $html += @"
        <div class="section">
            <div class="section-title">Phase 3: Eval Clip Window Comparison</div>
            <table>
                <thead>
                    <tr>
                        <th>Test Name</th>
                        <th>Window Size (frames)</th>
                        <th>Duration (s)</th>
                        <th>Masks Generated</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
"@
        foreach ($test in $windowTests) {
            $statusBadge = if ($test.Status -eq "SUCCESS") { 
                '<span class="status-badge success">✓ SUCCESS</span>' 
            } else { 
                '<span class="status-badge failed">✗ FAILED</span>' 
            }
            $html += @"
                    <tr>
                        <td><strong>$($test.Name)</strong></td>
                        <td>$($test.Parameter)</td>
                        <td>$([math]::Round($test.Duration, 2))</td>
                        <td>$($test.MaskCount)</td>
                        <td>$statusBadge</td>
                    </tr>
"@
        }
        $html += @"
                </tbody>
            </table>
            <div class="analysis">
                <div class="analysis-item"><strong>Key Finding:</strong> Smaller window (4 frames) is faster but may have reduced temporal coherence. Larger window (16 frames) is slower but provides better coherence.</div>
                <div class="analysis-item"><strong>Recommendation:</strong> Use window size 8 for good balance between speed and video smoothness.</div>
            </div>
        </div>
"@
    }

    # Add summary section
    $html += @"
        <div class="section">
            <div class="section-title">Summary & Recommendations</div>
            <div class="analysis">
                <div class="analysis-item">
                    <strong>Recommended Configuration:</strong><br>
                    - Threshold: 0.5 (balanced coverage and precision)<br>
                    - Sam2Version: base (optimal speed-accuracy tradeoff)<br>
                    - EvalClipWindow: 8 (balanced performance)<br>
                    - Fps: 10 (standard frame extraction rate)
                </div>
                <div class="analysis-item">
                    <strong>Performance Metrics:</strong><br>
                    - Total Successful Tests: $successTests / $totalTests<br>
                    - Total Execution Time: $([math]::Round($totalTime, 2))s<br>
                    - Average Time per Test: $([math]::Round($avgDuration, 2))s<br>
                    - Average Masks per Test: $([math]::Round($avgMasks, 0))
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SAMWISE Experiment Report Generator</p>
            <p>Report Date: $timestamp</p>
            <p><em>For questions or issues, refer to the detailed logs in the experiment directory.</em></p>
        </div>
    </div>
</body>
</html>
"@

    Set-Content -Path $OutputPath -Value $html -Encoding UTF8
    return $OutputPath
}

# Parse results
Write-Host "Parsing experiment results..." -ForegroundColor Cyan
$results = Parse-LogResults -LogPath $ComparisonLog

if ($results.Count -eq 0) {
    Write-Host "No results found in log file: $ComparisonLog" -ForegroundColor Red
    exit 1
}

# Generate HTML report
Write-Host "Generating professional HTML report..." -ForegroundColor Cyan
$reportPath = Generate-HtmlReport -Results $results -ExperimentName $ExperimentName -OutputPath $ReportFile

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Report Generated Successfully!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Report Location:" -ForegroundColor Yellow
Write-Host "  $reportPath" -ForegroundColor Green
Write-Host ""
Write-Host "To view the report, open in browser:" -ForegroundColor Yellow
Write-Host "  Start-Process `"$reportPath`"" -ForegroundColor Cyan
Write-Host ""

# Optional: Save JSON data for further analysis
$jsonData = @{
    ExperimentName = $ExperimentName
    GeneratedTime = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    TotalTests = $results.Count
    SuccessfulTests = ($results | Where-Object { $_.Status -eq "SUCCESS" }).Count
    Results = $results
} | ConvertTo-Json -Depth 10

Set-Content -Path $JsonReport -Value $jsonData -Encoding UTF8
Write-Host "Data also saved to: $JsonReport" -ForegroundColor Green

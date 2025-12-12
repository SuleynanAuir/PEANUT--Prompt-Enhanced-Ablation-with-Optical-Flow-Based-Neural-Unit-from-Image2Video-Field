"""
Generate summary statistics and visualizations for mask evaluation metrics
"""

import os
import json
import sys
from pathlib import Path
from collections import defaultdict
import numpy as np


def load_metrics(metrics_dir):
    """Load all metrics JSON files from directory"""
    metrics_data = {}
    
    for json_file in Path(metrics_dir).rglob("metrics.json"):
        test_name = json_file.parent.name
        video_name = json_file.parent.parent.name
        
        if video_name not in metrics_data:
            metrics_data[video_name] = {}
        
        try:
            with open(json_file, 'r') as f:
                metrics_data[video_name][test_name] = json.load(f)
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
    
    return metrics_data


def generate_summary_table(metrics_data, output_file=None):
    """Generate markdown table with all metrics"""
    
    lines = ["# Mask Quality Evaluation Summary\n"]
    lines.append(f"Date: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    for video_name in sorted(metrics_data.keys()):
        lines.append(f"## Video: {video_name}\n\n")
        
        # Main metrics table
        lines.append("| Test Name | Quality Score | Coverage (%) | Temporal IoU | Edge Sharpness | Connectivity |\n")
        lines.append("|-----------|---------------|--------------|--------------|----------------|---------------|\n")
        
        video_metrics = metrics_data[video_name]
        for test_name in sorted(video_metrics.keys()):
            metrics = video_metrics[test_name]
            
            quality_score = metrics.get("quality_score", 0.0)
            coverage = metrics["coverage"]["mean"]
            temporal_iou = metrics["temporal"]["temporal_consistency"]
            edge_sharpness = metrics["edge_quality"]["edge_sharpness_mean"]
            num_comp = metrics["connectivity"]["num_components_mean"]
            
            lines.append(f"| {test_name} | {quality_score:.1f} | {coverage:.1f} | {temporal_iou:.3f} | {edge_sharpness:.3f} | {num_comp:.1f} |\n")
        
        lines.append("\n")
        
        # Detailed metrics table
        lines.append("### Detailed Metrics\n\n")
        lines.append("| Test Name | Coverage Mean±Std | Perimeter Ratio | Largest Component | Uniformity |\n")
        lines.append("|-----------|-------------------|-----------------|-------------------|------------|\n")
        
        for test_name in sorted(video_metrics.keys()):
            metrics = video_metrics[test_name]
            
            cov_mean = metrics["coverage"]["mean"]
            cov_std = metrics["coverage"]["std"]
            perim = metrics["edge_quality"]["perimeter_ratio_mean"]
            largest = metrics["connectivity"]["largest_ratio_mean"]
            uniform = metrics["connectivity"]["component_uniformity_mean"]
            
            lines.append(f"| {test_name} | {cov_mean:.1f}±{cov_std:.1f} | {perim:.3f} | {largest:.3f} | {uniform:.3f} |\n")
        
        lines.append("\n")
    
    summary_text = "".join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(summary_text)
        print(f"Summary saved to: {output_file}")
    
    return summary_text


def generate_csv_export(metrics_data, output_file=None):
    """Generate CSV for spreadsheet analysis"""
    
    import csv
    import io
    
    # Use StringIO to properly format CSV
    output = io.StringIO()
    writer = csv.writer(output, lineterminator='\n')
    
    # Write header
    writer.writerow(["Video", "TestName", "QualityScore", "Coverage_Mean", "Coverage_Std", 
                     "EdgeSharpness", "PerimeterRatio", "NumComponents", "LargestRatio", 
                     "Uniformity", "TemporalIoU", "FrameCount"])
    
    # Write data rows
    for video_name in sorted(metrics_data.keys()):
        for test_name in sorted(metrics_data[video_name].keys()):
            metrics = metrics_data[video_name][test_name]
            
            quality_score = metrics.get("quality_score", 0.0)
            cov_mean = metrics["coverage"]["mean"]
            cov_std = metrics["coverage"]["std"]
            edge_sharp = metrics["edge_quality"]["edge_sharpness_mean"]
            perim = metrics["edge_quality"]["perimeter_ratio_mean"]
            num_comp = metrics["connectivity"]["num_components_mean"]
            largest = metrics["connectivity"]["largest_ratio_mean"]
            uniform = metrics["connectivity"]["component_uniformity_mean"]
            temporal_iou = metrics["temporal"]["temporal_consistency"]
            frame_count = metrics["temporal"]["frame_count"]
            
            writer.writerow([video_name, test_name, f"{quality_score:.2f}", f"{cov_mean:.2f}", 
                           f"{cov_std:.2f}", f"{edge_sharp:.4f}", f"{perim:.4f}", 
                           f"{num_comp:.2f}", f"{largest:.4f}", f"{uniform:.4f}", 
                           f"{temporal_iou:.4f}", str(frame_count)])
    
    csv_text = output.getvalue()
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            f.write(csv_text)
        print(f"CSV exported to: {output_file}")
    
    return csv_text


def generate_comparison_report(metrics_data, output_file=None):
    """Generate detailed comparison report"""
    
    lines = ["# Mask Quality Comparison Report\n\n"]
    
    for video_name in sorted(metrics_data.keys()):
        lines.append(f"## {video_name}\n\n")
        
        video_metrics = metrics_data[video_name]
        
        # Find best and worst by score
        scores = {name: m.get("quality_score", 0) for name, m in video_metrics.items()}
        best_test = max(scores, key=scores.get)
        worst_test = min(scores, key=scores.get)
        
        lines.append(f"### Performance Summary\n")
        lines.append(f"- **Best**: {best_test} (Score: {scores[best_test]:.1f})\n")
        lines.append(f"- **Worst**: {worst_test} (Score: {scores[worst_test]:.1f})\n")
        lines.append(f"- **Average**: {np.mean(list(scores.values())):.1f}\n\n")
        
        # Coverage analysis
        lines.append(f"### Coverage Analysis\n")
        coverage_by_test = {name: m["coverage"]["mean"] for name, m in video_metrics.items()}
        min_cov_test = min(coverage_by_test, key=coverage_by_test.get)
        max_cov_test = max(coverage_by_test, key=coverage_by_test.get)
        lines.append(f"- Least masked: {min_cov_test} ({coverage_by_test[min_cov_test]:.1f}%)\n")
        lines.append(f"- Most masked: {max_cov_test} ({coverage_by_test[max_cov_test]:.1f}%)\n\n")
        
        # Temporal stability analysis
        lines.append(f"### Temporal Stability (IoU)\n")
        temporal_by_test = {name: m["temporal"]["temporal_consistency"] for name, m in video_metrics.items()}
        for test_name in sorted(temporal_by_test.keys()):
            iou = temporal_by_test[test_name]
            quality = "Excellent" if iou > 0.8 else "Good" if iou > 0.6 else "Fair" if iou > 0.4 else "Poor"
            lines.append(f"- {test_name}: {iou:.3f} ({quality})\n")
        lines.append("\n")
        
        # Edge quality analysis
        lines.append(f"### Edge Quality\n")
        for test_name in sorted(video_metrics.keys()):
            metrics = video_metrics[test_name]
            edge_sharp = metrics["edge_quality"]["edge_sharpness_mean"]
            perim = metrics["edge_quality"]["perimeter_ratio_mean"]
            lines.append(f"- {test_name}: Sharpness={edge_sharp:.3f}, Perimeter Ratio={perim:.3f}\n")
        lines.append("\n")
    
    report_text = "".join(lines)
    
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report_text)
        print(f"Report saved to: {output_file}")
    
    return report_text


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python generate_metrics_summary.py <experiment_dir>")
        sys.exit(1)
    
    exp_dir = sys.argv[1]
    
    if not os.path.isdir(exp_dir):
        print(f"Error: Directory not found: {exp_dir}")
        sys.exit(1)
    
    print(f"Loading metrics from: {exp_dir}")
    metrics_data = load_metrics(exp_dir)
    
    if not metrics_data:
        print("No metrics found!")
        sys.exit(1)
    
    # Generate outputs
    summary_file = os.path.join(exp_dir, "METRICS_SUMMARY.md")
    csv_file = os.path.join(exp_dir, "metrics_data.csv")
    report_file = os.path.join(exp_dir, "DETAILED_COMPARISON.md")
    
    print("\nGenerating summary...")
    generate_summary_table(metrics_data, summary_file)
    
    print("Generating CSV export...")
    generate_csv_export(metrics_data, csv_file)
    
    print("Generating detailed report...")
    generate_comparison_report(metrics_data, report_file)
    
    print("\nDone!")

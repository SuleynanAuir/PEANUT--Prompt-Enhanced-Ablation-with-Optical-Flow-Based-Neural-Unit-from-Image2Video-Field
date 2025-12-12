"""
Visualize mask quality metrics as charts and graphs
"""

import os
import json
import sys
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import numpy as np
from pathlib import Path

# Set Chinese font support
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def load_metrics_data(csv_path):
    """Load metrics from CSV file"""
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found: {csv_path}")
        return None
    
    df = pd.read_csv(csv_path)
    return df


def plot_quality_scores(df, output_dir, video_name):
    """Plot quality scores comparison"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    # Threshold comparison
    threshold_data = df[df['TestName'].str.contains('threshold')]
    if not threshold_data.empty:
        ax = axes[0]
        tests = threshold_data['TestName'].str.replace('threshold_', '').str.replace('_', '\n')
        scores = threshold_data['QualityScore']
        colors = ['#FF69B4', '#3CB371', '#4169E1']  # Pink, Green, Blue
        bars = ax.bar(tests, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
        ax.set_title('Threshold Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Model comparison
    model_data = df[df['TestName'].str.contains('model')]
    if not model_data.empty:
        ax = axes[1]
        tests = model_data['TestName'].str.replace('model_', '')
        scores = model_data['QualityScore']
        colors = ['#FF69B4', '#3CB371', '#4169E1']
        bars = ax.bar(tests, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
        ax.set_title('Model Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Window comparison
    window_data = df[df['TestName'].str.contains('window')]
    if not window_data.empty:
        ax = axes[2]
        tests = window_data['TestName'].str.replace('window_', '')
        scores = window_data['QualityScore']
        colors = ['#FF69B4', '#3CB371', '#4169E1']
        bars = ax.bar(tests, scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        ax.set_ylabel('Quality Score', fontsize=12, fontweight='bold')
        ax.set_title('Window Comparison', fontsize=14, fontweight='bold')
        ax.set_ylim(0, 100)
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_quality_scores.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_coverage_analysis(df, output_dir, video_name):
    """Plot coverage statistics"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    categories = [
        ('threshold', 'Threshold'),
        ('model', 'Model'),
        ('window', 'Window')
    ]
    
    for idx, (cat, title) in enumerate(categories):
        ax = axes[idx]
        cat_data = df[df['TestName'].str.contains(cat)]
        
        if not cat_data.empty:
            tests = cat_data['TestName'].str.replace(f'{cat}_', '').str.replace('_', '\n')
            means = cat_data['Coverage_Mean']
            stds = cat_data['Coverage_Std']
            colors = ['#FF69B4', '#3CB371', '#4169E1']
            
            bars = ax.bar(tests, means, yerr=stds, capsize=5, 
                         color=colors, alpha=0.8, edgecolor='black', linewidth=1.5,
                         error_kw={'linewidth': 2, 'ecolor': 'black'})
            
            ax.set_ylabel('Coverage (%)', fontsize=12, fontweight='bold')
            ax.set_title(f'{title} - Coverage', fontsize=14, fontweight='bold')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add value labels
            for bar, mean, std in zip(bars, means, stds):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{mean:.1f}±{std:.1f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_coverage.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_temporal_stability(df, output_dir, video_name):
    """Plot temporal stability (IoU)"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    categories = [
        ('threshold', 'Threshold'),
        ('model', 'Model'),
        ('window', 'Window')
    ]
    
    for idx, (cat, title) in enumerate(categories):
        ax = axes[idx]
        cat_data = df[df['TestName'].str.contains(cat)]
        
        if not cat_data.empty:
            tests = cat_data['TestName'].str.replace(f'{cat}_', '').str.replace('_', '\n')
            ious = cat_data['TemporalIoU']
            colors = ['#FF69B4', '#3CB371', '#4169E1']
            
            bars = ax.bar(tests, ious, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
            
            ax.set_ylabel('Temporal IoU', fontsize=12, fontweight='bold')
            ax.set_title(f'{title} - Temporal Stability', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 1.0)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Add stability zones
            ax.axhspan(0.8, 1.0, alpha=0.1, color='green', label='Excellent')
            ax.axhspan(0.6, 0.8, alpha=0.1, color='yellow', label='Good')
            ax.axhspan(0, 0.6, alpha=0.1, color='red', label='Fair')
            
            # Add value labels
            for bar, iou in zip(bars, ious):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{iou:.3f}', ha='center', va='bottom', fontweight='bold')
            
            if idx == 2:
                ax.legend(loc='upper right', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_temporal_stability.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_edge_quality(df, output_dir, video_name):
    """Plot edge quality metrics"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    categories = [
        ('threshold', 'Threshold'),
        ('model', 'Model'),
        ('window', 'Window')
    ]
    
    for idx, (cat, title) in enumerate(categories):
        ax = axes[idx]
        cat_data = df[df['TestName'].str.contains(cat)]
        
        if not cat_data.empty:
            tests = cat_data['TestName'].str.replace(f'{cat}_', '').str.replace('_', '\n')
            sharpness = cat_data['EdgeSharpness']
            perimeter = cat_data['PerimeterRatio']
            
            x = np.arange(len(tests))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, sharpness, width, label='Edge Sharpness',
                          color='#FF8C00', alpha=0.8, edgecolor='black', linewidth=1.5)
            bars2 = ax.bar(x + width/2, perimeter/10, width, label='Perimeter Ratio/10',
                          color='#9370DB', alpha=0.8, edgecolor='black', linewidth=1.5)
            
            ax.set_ylabel('Value', fontsize=12, fontweight='bold')
            ax.set_title(f'{title} - Edge Quality', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(tests)
            ax.legend(fontsize=9)
            ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_edge_quality.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_connectivity(df, output_dir, video_name):
    """Plot connectivity metrics"""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    categories = [
        ('threshold', 'Threshold'),
        ('model', 'Model'),
        ('window', 'Window')
    ]
    
    for idx, (cat, title) in enumerate(categories):
        ax = axes[idx]
        cat_data = df[df['TestName'].str.contains(cat)]
        
        if not cat_data.empty:
            tests = cat_data['TestName'].str.replace(f'{cat}_', '').str.replace('_', '\n')
            num_comp = cat_data['NumComponents']
            largest = cat_data['LargestRatio']
            
            x = np.arange(len(tests))
            width = 0.35
            
            bars1 = ax.bar(x - width/2, num_comp, width, label='Num Components',
                          color='#20B2AA', alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Create second y-axis for largest ratio
            ax2 = ax.twinx()
            bars2 = ax2.bar(x + width/2, largest, width, label='Largest Ratio',
                           color='#FF6347', alpha=0.8, edgecolor='black', linewidth=1.5)
            
            ax.set_ylabel('Number of Components', fontsize=11, fontweight='bold', color='#20B2AA')
            ax2.set_ylabel('Largest Component Ratio', fontsize=11, fontweight='bold', color='#FF6347')
            ax.set_title(f'{title} - Connectivity', fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(tests)
            ax2.set_ylim(0, 1.0)
            
            ax.tick_params(axis='y', labelcolor='#20B2AA')
            ax2.tick_params(axis='y', labelcolor='#FF6347')
            ax.grid(axis='y', alpha=0.3, linestyle='--')
            
            # Combine legends
            lines1, labels1 = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_connectivity.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def plot_radar_chart(df, output_dir, video_name):
    """Plot radar chart comparing all metrics"""
    # Normalize metrics to 0-1 scale
    categories = ['Quality\nScore', 'Coverage', 'Temporal\nIoU', 'Edge\nSharpness', 'Largest\nRatio']
    
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw=dict(projection='polar'))
    
    test_groups = [
        ('threshold', 'Threshold Comparison'),
        ('model', 'Model Comparison'),
        ('window', 'Window Comparison')
    ]
    
    for idx, (test_type, title) in enumerate(test_groups):
        ax = axes[idx]
        test_data = df[df['TestName'].str.contains(test_type)]
        
        if not test_data.empty:
            num_vars = len(categories)
            angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
            angles += angles[:1]
            
            ax.set_theta_offset(np.pi / 2)
            ax.set_theta_direction(-1)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories, fontsize=10)
            ax.set_ylim(0, 1)
            ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
            ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'], fontsize=8)
            ax.grid(True, linestyle='--', alpha=0.7)
            
            colors = ['#FF69B4', '#3CB371', '#4169E1']
            
            for test_idx, (_, row) in enumerate(test_data.iterrows()):
                values = [
                    row['QualityScore'] / 100,
                    min(row['Coverage_Mean'] / 20, 1.0),  # Cap at 20% for normalization
                    row['TemporalIoU'],
                    min(row['EdgeSharpness'] * 2, 1.0),
                    row['LargestRatio']
                ]
                values += values[:1]
                
                test_name = row['TestName'].replace(f'{test_type}_', '')
                ax.plot(angles, values, 'o-', linewidth=2, label=test_name, 
                       color=colors[test_idx % 3], markersize=6)
                ax.fill(angles, values, alpha=0.15, color=colors[test_idx % 3])
            
            ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
            ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=9)
    
    plt.tight_layout()
    output_path = os.path.join(output_dir, f'{video_name}_radar_comparison.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def create_summary_dashboard(df, output_dir, video_name):
    """Create a comprehensive summary dashboard"""
    fig = plt.figure(figsize=(20, 12))
    gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
    
    # 1. Quality Scores Overview
    ax1 = fig.add_subplot(gs[0, :])
    all_tests = df['TestName']
    all_scores = df['QualityScore']
    colors = ['#FF69B4' if 'threshold' in t else '#3CB371' if 'model' in t else '#4169E1' for t in all_tests]
    
    bars = ax1.barh(all_tests, all_scores, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax1.set_xlabel('Quality Score', fontsize=12, fontweight='bold')
    ax1.set_title('Overall Quality Scores Comparison', fontsize=16, fontweight='bold')
    ax1.set_xlim(0, 100)
    ax1.grid(axis='x', alpha=0.3, linestyle='--')
    
    for bar, score in zip(bars, all_scores):
        width = bar.get_width()
        ax1.text(width + 1, bar.get_y() + bar.get_height()/2,
                f'{score:.1f}', ha='left', va='center', fontweight='bold')
    
    # 2. Coverage vs Temporal IoU scatter
    ax2 = fig.add_subplot(gs[1, 0])
    threshold_data = df[df['TestName'].str.contains('threshold')]
    ax2.scatter(threshold_data['Coverage_Mean'], threshold_data['TemporalIoU'], 
               s=200, c='#FF69B4', alpha=0.6, edgecolors='black', linewidth=2)
    for _, row in threshold_data.iterrows():
        ax2.annotate(row['TestName'].replace('threshold_', ''), 
                    (row['Coverage_Mean'], row['TemporalIoU']),
                    fontsize=8, ha='center')
    ax2.set_xlabel('Coverage (%)', fontweight='bold')
    ax2.set_ylabel('Temporal IoU', fontweight='bold')
    ax2.set_title('Threshold: Coverage vs Stability', fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    # 3. Model comparison scatter
    ax3 = fig.add_subplot(gs[1, 1])
    model_data = df[df['TestName'].str.contains('model')]
    ax3.scatter(model_data['Coverage_Mean'], model_data['TemporalIoU'], 
               s=200, c='#3CB371', alpha=0.6, edgecolors='black', linewidth=2)
    for _, row in model_data.iterrows():
        ax3.annotate(row['TestName'].replace('model_', ''), 
                    (row['Coverage_Mean'], row['TemporalIoU']),
                    fontsize=8, ha='center')
    ax3.set_xlabel('Coverage (%)', fontweight='bold')
    ax3.set_ylabel('Temporal IoU', fontweight='bold')
    ax3.set_title('Model: Coverage vs Stability', fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 4. Window comparison scatter
    ax4 = fig.add_subplot(gs[1, 2])
    window_data = df[df['TestName'].str.contains('window')]
    ax4.scatter(window_data['Coverage_Mean'], window_data['TemporalIoU'], 
               s=200, c='#4169E1', alpha=0.6, edgecolors='black', linewidth=2)
    for _, row in window_data.iterrows():
        ax4.annotate(row['TestName'].replace('window_', ''), 
                    (row['Coverage_Mean'], row['TemporalIoU']),
                    fontsize=8, ha='center')
    ax4.set_xlabel('Coverage (%)', fontweight='bold')
    ax4.set_ylabel('Temporal IoU', fontweight='bold')
    ax4.set_title('Window: Coverage vs Stability', fontweight='bold')
    ax4.grid(True, alpha=0.3)
    
    # 5. Best configuration summary
    ax5 = fig.add_subplot(gs[2, :])
    ax5.axis('off')
    
    best_overall = df.loc[df['QualityScore'].idxmax()]
    best_coverage = df.loc[df['Coverage_Mean'].idxmax()]
    best_temporal = df.loc[df['TemporalIoU'].idxmax()]
    
    summary_text = f"""
    BEST CONFIGURATIONS:
    
    Highest Quality Score: {best_overall['TestName']} (Score: {best_overall['QualityScore']:.1f})
    Highest Coverage: {best_coverage['TestName']} (Coverage: {best_coverage['Coverage_Mean']:.1f}%)
    Best Temporal Stability: {best_temporal['TestName']} (IoU: {best_temporal['TemporalIoU']:.3f})
    
    RECOMMENDATIONS:
    • For highest quality: Use {best_overall['TestName'].replace('_', ' ')}
    • For maximum coverage: Use {best_coverage['TestName'].replace('_', ' ')}
    • For best stability: Use {best_temporal['TestName'].replace('_', ' ')}
    """
    
    ax5.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
            fontfamily='monospace', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    plt.suptitle(f'Mask Quality Analysis Dashboard - {video_name}', 
                fontsize=18, fontweight='bold', y=0.98)
    
    output_path = os.path.join(output_dir, f'{video_name}_dashboard.png')
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    plt.close()
    print(f"Saved: {output_path}")


def visualize_metrics(exp_dir):
    """Main function to generate all visualizations"""
    csv_path = os.path.join(exp_dir, "metrics_data.csv")
    
    if not os.path.exists(csv_path):
        print(f"Error: metrics_data.csv not found in {exp_dir}")
        return False
    
    # Load data
    df = load_metrics_data(csv_path)
    if df is None or df.empty:
        print("No data to visualize")
        return False
    
    # Create output directory
    viz_dir = os.path.join(exp_dir, "metrics_visualizations")
    os.makedirs(viz_dir, exist_ok=True)
    
    # Get unique videos
    if 'Video' in df.columns:
        videos = df['Video'].unique()
    else:
        videos = ['experiment']
    
    print(f"\nGenerating visualizations for {len(videos)} video(s)...")
    print("=" * 60)
    
    # Generate plots for each video
    for video_name in videos:
        if 'Video' in df.columns:
            video_df = df[df['Video'] == video_name]
        else:
            video_df = df
        
        print(f"\nProcessing: {video_name}")
        
        # Generate all plots
        plot_quality_scores(video_df, viz_dir, video_name)
        plot_coverage_analysis(video_df, viz_dir, video_name)
        plot_temporal_stability(video_df, viz_dir, video_name)
        plot_edge_quality(video_df, viz_dir, video_name)
        plot_connectivity(video_df, viz_dir, video_name)
        plot_radar_chart(video_df, viz_dir, video_name)
        create_summary_dashboard(video_df, viz_dir, video_name)
    
    print("=" * 60)
    print(f"\nAll visualizations saved to: {viz_dir}")
    print("\nGenerated files:")
    generated_count = 0
    for f in sorted(os.listdir(viz_dir)):
        if f.endswith('.png'):
            print(f"  - {f}")
            generated_count += 1
    print(f"\nTotal: {generated_count} PNG files generated")
    
    return True


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python visualize_metrics.py <experiment_dir>")
        sys.exit(1)
    
    exp_dir = sys.argv[1]
    
    if not os.path.isdir(exp_dir):
        print(f"Error: Directory not found: {exp_dir}")
        sys.exit(1)
    
    success = visualize_metrics(exp_dir)
    sys.exit(0 if success else 1)

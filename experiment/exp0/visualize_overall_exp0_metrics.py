#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP0 Overall Metrics Visualization (Academic Style)
Reads quality_metrics.csv and plots averaged metrics directly as specified.
"""

import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.dpi'] = 200
plt.rcParams['font.size'] = 11
plt.rcParams['axes.titlesize'] = 13
plt.rcParams['axes.labelsize'] = 11


def load_metrics_csv(csv_path: Path):
    """Load metrics from CSV and compute averages."""
    data = {
        'psnr_mean': [],
        'psnr_std': [],
        'ssim_mean': [],
        'ssim_std': [],
        'sharpness_mean': [],
        'blur_score_mean': [],
        'artifact_score_mean': [],
        'temporal_consistency': [],
    }
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in data.keys():
                data[key].append(float(row[key]))
    
    # Compute averages
    averages = {k: np.mean(v) for k, v in data.items()}
    return averages


def plot_overall(metrics, out_path: Path):
    """Plot overall metrics as horizontal bars in academic style."""
    
    # Order as specified
    order = [
        'psnr_mean',
        'psnr_std',
        'ssim_mean',
        'ssim_std',
        'sharpness_mean',
        'blur_score_mean',
        'artifact_score_mean',
        'temporal_consistency',
    ]
    
    labels = order
    values = [metrics[k] for k in order]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Colors: muted academic palette
    colors = ['#1f77b4', '#aec7e8', '#ff7f0e', '#ffbb78', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    
    bars = ax.barh(range(len(labels)), values, color=colors, edgecolor='black', alpha=0.85, linewidth=1.2)
    
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('Averaged Value', fontweight='bold')
    ax.set_title('EXP0 Overall Quality Metrics (LAMA4Video Assessment)', fontweight='bold', pad=15)
    ax.grid(axis='x', alpha=0.25, linestyle='--')
    
    # Add value labels
    for i, (bar, v) in enumerate(zip(bars, values)):
        ax.text(v + max(values) * 0.01, i, f"{v:.4f}", va='center', fontsize=9, fontweight='bold')
    
    # Clean spines
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    
    fig.tight_layout()
    fig.savefig(out_path, dpi=400, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out_path}")


def main():
    base = Path(__file__).resolve().parent
    csv_path = base / 'results' / 'metrics' / 'quality_metrics.csv'
    out_dir = base / 'results' / 'metrics'
    out_dir.mkdir(parents=True, exist_ok=True)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing CSV: {csv_path}")
    
    metrics = load_metrics_csv(csv_path)
    
    plot_overall(metrics, out_dir / 'overall_metrics_visualization.png')


if __name__ == '__main__':
    main()
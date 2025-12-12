#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP0 Quality Metrics Visualization
Reads exp0/results/metrics/quality_metrics.json and produces bar/heatmap
visualizations to highlight per-video quality gaps.
"""

import json
import sys
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.size'] = 10


def load_metrics(path: Path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def plot_metric_bars(metrics, out_path: Path):
    videos = sorted(metrics.keys())
    n = len(videos)

    psnr_mean = [metrics[v]['psnr_mean'] for v in videos]
    psnr_std = [metrics[v]['psnr_std'] for v in videos]
    ssim_mean = [metrics[v]['ssim_mean'] for v in videos]
    ssim_std = [metrics[v]['ssim_std'] for v in videos]
    sharp = [metrics[v]['sharpness_mean'] for v in videos]
    blur_inv = [100 - metrics[v]['blur_score_mean'] for v in videos]  # higher = better
    artifact_inv = [100 - metrics[v]['artifact_score_mean'] for v in videos]  # higher = better
    temporal_inv = [100 - metrics[v]['temporal_consistency'] for v in videos]  # higher = better

    fig, axes = plt.subplots(2, 4, figsize=(18, 8))
    fig.suptitle('EXP0 Quality Metrics (Per Video)', fontsize=14, fontweight='bold')

    def bar(ax, vals, title, ylabel=None, yerr=None):
        ax.bar(range(n), vals, color='teal', alpha=0.8, edgecolor='black', linewidth=1.2)
        if yerr is not None:
            ax.errorbar(range(n), vals, yerr=yerr, fmt='none', color='black', capsize=4, linewidth=1.5)
        ax.set_xticks(range(n))
        ax.set_xticklabels(videos, rotation=75, ha='right')
        ax.set_title(title, fontweight='bold')
        if ylabel:
            ax.set_ylabel(ylabel, fontweight='bold')
        ax.grid(axis='y', alpha=0.3)

    bar(axes[0, 0], psnr_mean, 'PSNR Mean (dB)', 'PSNR', yerr=psnr_std)
    bar(axes[0, 1], ssim_mean, 'SSIM Mean', 'SSIM', yerr=ssim_std)
    bar(axes[0, 2], sharp, 'Sharpness Score', 'Sharpness')
    bar(axes[0, 3], blur_inv, 'Blur Resistance (↑=better)', 'Score')
    bar(axes[1, 0], artifact_inv, 'Artifact Resistance (↑=better)', 'Score')
    bar(axes[1, 1], temporal_inv, 'Temporal Stability (↑=better)', 'Score')

    axes[1, 2].axis('off')
    axes[1, 3].axis('off')

    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def plot_heatmap(metrics, out_path: Path):
    videos = sorted(metrics.keys())
    # Metrics scaled to 0-100 for heatmap clarity
    data = []
    for v in videos:
        row = [
            min(100, metrics[v]['psnr_mean'] / 50 * 100),
            metrics[v]['ssim_mean'] * 100,
            metrics[v]['sharpness_mean'],
            100 - metrics[v]['blur_score_mean'],
            100 - metrics[v]['artifact_score_mean'],
            100 - metrics[v]['temporal_consistency'],
        ]
        data.append(row)

    data = np.array(data)
    labels = ['PSNR', 'SSIM', 'Sharpness', 'BlurRes', 'ArtifactRes', 'Temporal']

    fig, ax = plt.subplots(figsize=(10, max(6, len(videos) * 0.35)))
    im = ax.imshow(data, cmap='RdYlGn', aspect='auto', vmin=0, vmax=100)

    ax.set_xticks(np.arange(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_yticks(np.arange(len(videos)))
    ax.set_yticklabels(videos)
    ax.set_title('EXP0 Quality Metrics Heatmap (0-100 scaled)', fontweight='bold', pad=10)

    # Annotate values
    for i in range(len(videos)):
        for j in range(len(labels)):
            ax.text(j, i, f"{data[i, j]:.1f}", ha='center', va='center', color='black', fontsize=8)

    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label='Scaled Score (higher=better)')
    fig.tight_layout(rect=[0, 0, 1, 0.97])
    fig.savefig(out_path, dpi=300)
    plt.close(fig)


def main():
    base_dir = Path(__file__).resolve().parent
    metrics_path = base_dir / 'results' / 'metrics' / 'quality_metrics.json'
    out_dir = base_dir / 'results' / 'metrics'
    out_dir.mkdir(parents=True, exist_ok=True)

    if not metrics_path.exists():
        print(f"ERROR: metrics file not found: {metrics_path}")
        sys.exit(1)

    metrics = load_metrics(metrics_path)
    if not metrics:
        print("ERROR: metrics file is empty")
        sys.exit(1)

    print("Generating EXP0 visualizations...")
    plot_metric_bars(metrics, out_dir / 'exp0_metrics_overview.png')
    plot_heatmap(metrics, out_dir / 'exp0_metrics_heatmap.png')
    print("Saved:")
    print(f" - {out_dir / 'exp0_metrics_overview.png'}")
    print(f" - {out_dir / 'exp0_metrics_heatmap.png'}")


if __name__ == '__main__':
    main()

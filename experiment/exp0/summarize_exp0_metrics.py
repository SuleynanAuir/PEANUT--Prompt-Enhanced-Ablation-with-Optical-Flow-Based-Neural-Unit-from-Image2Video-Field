#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Summarize EXP0 quality metrics by averaging across all videos.
Inputs : exp0/results/metrics/quality_metrics.json
Outputs: exp0/results/metrics/overall_metrics_summary.csv/.txt
"""

import json
from pathlib import Path


def main():
    base = Path(__file__).resolve().parent
    metrics_path = base / "results" / "metrics" / "quality_metrics.json"
    out_dir = base / "results" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)

    if not metrics_path.exists():
        raise FileNotFoundError(f"Missing metrics file: {metrics_path}")

    with open(metrics_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not data:
        raise ValueError("Metrics file is empty")

    videos = list(data.keys())
    n = len(videos)

    # Aggregate means across videos
    def avg(key):
        return sum(data[v][key] for v in videos) / n

    psnr_mean_avg = avg("psnr_mean")
    psnr_std_avg = avg("psnr_std")
    ssim_mean_avg = avg("ssim_mean")
    ssim_std_avg = avg("ssim_std")
    sharpness_mean_avg = avg("sharpness_mean")
    blur_score_mean_avg = avg("blur_score_mean")
    artifact_score_mean_avg = avg("artifact_score_mean")
    temporal_consistency_avg = avg("temporal_consistency")

    blur_resistance_avg = 100 - blur_score_mean_avg
    artifact_resistance_avg = 100 - artifact_score_mean_avg
    temporal_stability_avg = 100 - temporal_consistency_avg

    ordered_metrics = [
        ("psnr_mean_avg", psnr_mean_avg, "dB", "higher-better"),
        ("psnr_std_avg", psnr_std_avg, "dB", "lower-better"),
        ("ssim_mean_avg", ssim_mean_avg, "0-1", "higher-better"),
        ("ssim_std_avg", ssim_std_avg, "0-1", "lower-better"),
        ("sharpness_mean_avg", sharpness_mean_avg, "0-100", "higher-better"),
        ("blur_score_mean_avg", blur_score_mean_avg, "0-100", "lower-better"),
        ("artifact_score_mean_avg", artifact_score_mean_avg, "0-100", "lower-better"),
        ("temporal_consistency_avg", temporal_consistency_avg, "0-100", "lower-better"),
        ("blur_resistance_avg", blur_resistance_avg, "0-100", "higher-better"),
        ("artifact_resistance_avg", artifact_resistance_avg, "0-100", "higher-better"),
        ("temporal_stability_avg", temporal_stability_avg, "0-100", "higher-better"),
    ]

    # CSV
    csv_path = out_dir / "overall_metrics_summary.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        f.write("metric,value,unit,preference\n")
        for name, val, unit, pref in ordered_metrics:
            f.write(f"{name},{val:.4f},{unit},{pref}\n")

    # TXT
    txt_path = out_dir / "overall_metrics_summary.txt"
    lines = ["EXP0 Overall Metrics (averaged across videos)", ""]
    for name, val, unit, pref in ordered_metrics:
        lines.append(f"{name}: {val:.4f} {unit} ({pref})")
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    print("Saved:")
    print(f" - {csv_path}")
    print(f" - {txt_path}")


if __name__ == "__main__":
    main()

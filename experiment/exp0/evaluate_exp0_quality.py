#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EXP0 Quality Metrics Evaluation
Matches original frames in `All_images` with outputs in `Video_output`,
computes PSNR/SSIM/Sharpness/Blur/Artifact/Temporal metrics, and writes
JSON/CSV/TXT reports under exp0/results.
"""

import os
import cv2
import json
import csv
import sys
import numpy as np
from pathlib import Path
from collections import defaultdict
from skimage.metrics import peak_signal_noise_ratio, structural_similarity


# -----------------------------
# Metric helpers
# -----------------------------
class QualityMetrics:
    """Calculate quality metrics for inpainting results."""

    @staticmethod
    def calculate_psnr(img1, img2):
        img1 = img1.astype(np.float32)
        img2 = img2.astype(np.float32)
        return peak_signal_noise_ratio(img1, img2, data_range=255.0)

    @staticmethod
    def calculate_ssim(img1, img2):
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY) if len(img1.shape) == 3 else img1
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_RGB2GRAY) if len(img2.shape) == 3 else img2
        return structural_similarity(img1_gray, img2_gray, data_range=255)

    @staticmethod
    def calculate_temporal_consistency(frames):
        if len(frames) < 2:
            return 0.0

        total_diff = 0.0
        for i in range(len(frames) - 1):
            diff = cv2.absdiff(frames[i], frames[i + 1])
            total_diff += np.mean(diff)

        avg_diff = total_diff / (len(frames) - 1)
        return min(100.0, avg_diff * 100.0 / 255.0)

    @staticmethod
    def calculate_sharpness(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        return min(100.0, sharpness / 100.0)

    @staticmethod
    def calculate_blur_score(img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY) if len(img.shape) == 3 else img
        f_transform = np.fft.fft2(gray)
        f_shift = np.fft.fftshift(f_transform)
        magnitude = np.abs(f_shift)

        h, w = magnitude.shape
        cy, cx = h // 2, w // 2
        high_freq = magnitude[cy // 2 : cy + cy // 2, cx // 2 : cx + cx // 2]
        high_freq_sum = np.sum(high_freq)
        total_sum = np.sum(magnitude)

        if total_sum == 0:
            return 50.0

        high_freq_ratio = high_freq_sum / total_sum
        blur_score = 100.0 - (high_freq_ratio * 100.0)
        return max(0.0, min(100.0, blur_score))

    @staticmethod
    def calculate_artifact_score(img):
        artifact_score = 0.0

        img_lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
        block_size = 8
        h, w = img.shape[:2]

        block_variance = []
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = img_lab[i : i + block_size, j : j + block_size]
                block_variance.append(np.var(block))

        if block_variance:
            variance_std = np.std(block_variance)
            blocking_score = min(50.0, variance_std / 10.0)
            artifact_score += blocking_score * 0.3

        img_hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        h_channel = img_hsv[:, :, 0]
        hue_grad = np.abs(np.gradient(h_channel.astype(float)))
        max_hue_change = np.percentile(hue_grad, 95)
        color_inconsistency = min(50.0, max_hue_change / 5.0)
        artifact_score += color_inconsistency * 0.3

        local_contrast = []
        for i in range(0, h - 16, 16):
            for j in range(0, w - 16, 16):
                patch = img[i : i + 16, j : j + 16]
                contrast = np.std(patch)
                local_contrast.append(contrast)

        if local_contrast:
            contrast_std = np.std(local_contrast)
            contrast_inconsistency = min(40.0, contrast_std)
            artifact_score += contrast_inconsistency * 0.4

        return min(100.0, artifact_score)


# -----------------------------
# IO helpers
# -----------------------------
def load_reference_frames(ref_dir: Path):
    """Load ground-truth frames grouped by video prefix."""
    videos = defaultdict(list)
    for file in sorted(ref_dir.glob("*_frame_*.png")):
        if file.name.endswith("_mask.png"):
            continue
        name_parts = file.name.split("_frame_")
        if len(name_parts) < 2:
            continue
        video = name_parts[0]
        frame_idx = int(name_parts[1].split('.')[0])
        img = cv2.cvtColor(cv2.imread(str(file)), cv2.COLOR_BGR2RGB)
        videos[video].append((frame_idx, img))

    # sort by frame index
    for vid in videos:
        videos[vid] = [img for _, img in sorted(videos[vid], key=lambda x: x[0])]
    return videos


def load_output_frames(video_name: str, out_dir: Path):
    """Load output frames by decoding mp4; fallback to extracted pngs if exist."""
    frames = []
    candidates = [
        out_dir / f"{video_name}.mp4",
        out_dir / video_name / f"{video_name}.mp4",
    ]

    video_path = None
    for cand in candidates:
        if cand.exists():
            video_path = cand
            break

    # If there are already extracted frames in subfolder, use them first
    frame_pattern = out_dir / video_name / f"{video_name}_frame_*.png"
    extracted = sorted([p for p in frame_pattern.parent.glob(frame_pattern.name) if not p.name.endswith("_mask.png")])
    if extracted:
        for file in extracted:
            img = cv2.cvtColor(cv2.imread(str(file)), cv2.COLOR_BGR2RGB)
            frames.append(img)
        return frames

    if video_path is None:
        return frames

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return frames

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame_rgb)
    cap.release()
    return frames


# -----------------------------
# Metrics aggregation
# -----------------------------
def evaluate_video(video_name, ref_frames, out_frames):
    n = min(len(ref_frames), len(out_frames))
    if n == 0:
        return None

    psnr_list, ssim_list = [], []
    sharp_list, blur_list, artifact_list = [], [], []

    processed_out_frames = []

    for i in range(n):
        ref = ref_frames[i]
        out = out_frames[i]

        if ref.shape[:2] != out.shape[:2]:
            out = cv2.resize(out, (ref.shape[1], ref.shape[0]), interpolation=cv2.INTER_LINEAR)

        psnr_list.append(QualityMetrics.calculate_psnr(ref, out))
        ssim_list.append(QualityMetrics.calculate_ssim(ref, out))
        sharp_list.append(QualityMetrics.calculate_sharpness(out))
        blur_list.append(QualityMetrics.calculate_blur_score(out))
        artifact_list.append(QualityMetrics.calculate_artifact_score(out))
        processed_out_frames.append(out)

    temporal = QualityMetrics.calculate_temporal_consistency(processed_out_frames)

    return {
        "frames_used": n,
        "psnr_mean": float(np.mean(psnr_list)),
        "psnr_std": float(np.std(psnr_list)),
        "ssim_mean": float(np.mean(ssim_list)),
        "ssim_std": float(np.std(ssim_list)),
        "sharpness_mean": float(np.mean(sharp_list)),
        "blur_score_mean": float(np.mean(blur_list)),
        "artifact_score_mean": float(np.mean(artifact_list)),
        "temporal_consistency": float(temporal),
    }


def save_json(metrics, path: Path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)


def save_csv(metrics, path: Path):
    headers = [
        "video",
        "frames_used",
        "psnr_mean",
        "psnr_std",
        "ssim_mean",
        "ssim_std",
        "sharpness_mean",
        "blur_score_mean",
        "artifact_score_mean",
        "temporal_consistency",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for video, data in metrics.items():
            writer.writerow([
                video,
                data["frames_used"],
                f"{data['psnr_mean']:.4f}",
                f"{data['psnr_std']:.4f}",
                f"{data['ssim_mean']:.4f}",
                f"{data['ssim_std']:.4f}",
                f"{data['sharpness_mean']:.4f}",
                f"{data['blur_score_mean']:.4f}",
                f"{data['artifact_score_mean']:.4f}",
                f"{data['temporal_consistency']:.4f}",
            ])


def save_summary(metrics, path: Path):
    lines = ["EXP0 Quality Metrics Summary\n"]
    for video, data in metrics.items():
        lines.append(f"Video: {video}")
        lines.append(f"  Frames: {data['frames_used']}")
        lines.append(f"  PSNR Mean/Std: {data['psnr_mean']:.2f} / {data['psnr_std']:.2f}")
        lines.append(f"  SSIM Mean/Std: {data['ssim_mean']:.4f} / {data['ssim_std']:.4f}")
        lines.append(f"  Sharpness: {data['sharpness_mean']:.2f}")
        lines.append(f"  Blur Score: {data['blur_score_mean']:.2f}")
        lines.append(f"  Artifact Score: {data['artifact_score_mean']:.2f}")
        lines.append(f"  Temporal Consistency: {data['temporal_consistency']:.2f}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


# -----------------------------
# Main
# -----------------------------
def main():
    base_dir = Path(__file__).resolve().parent
    ref_dir = base_dir / "All_images"
    out_dir = base_dir / "Video_output"
    result_dir = base_dir / "results" / "metrics"
    result_dir.mkdir(parents=True, exist_ok=True)

    print(f"Reference frames: {ref_dir}")
    print(f"Output videos:    {out_dir}")
    print(f"Results to:       {result_dir}\n")

    if not ref_dir.exists() or not out_dir.exists():
        print("ERROR: All_images or Video_output folder not found.")
        sys.exit(1)

    ref_videos = load_reference_frames(ref_dir)
    if not ref_videos:
        print("ERROR: No reference frames found.")
        sys.exit(1)

    metrics = {}
    for video, ref_frames in ref_videos.items():
        out_frames = load_output_frames(video, out_dir)
        if not out_frames:
            print(f"[WARN] No outputs found for {video}, skipping.")
            continue

        res = evaluate_video(video, ref_frames, out_frames)
        if res is None:
            print(f"[WARN] No paired frames for {video}, skipping.")
            continue

        metrics[video] = res
        print(f"[OK] {video}: frames={res['frames_used']} PSNR={res['psnr_mean']:.2f} SSIM={res['ssim_mean']:.4f}")

    if not metrics:
        print("ERROR: No metrics computed.")
        sys.exit(1)

    save_json(metrics, result_dir / "quality_metrics.json")
    save_csv(metrics, result_dir / "quality_metrics.csv")
    save_summary(metrics, result_dir / "quality_summary.txt")

    print("\nSaved:")
    print(f"  - {result_dir / 'quality_metrics.json'}")
    print(f"  - {result_dir / 'quality_metrics.csv'}")
    print(f"  - {result_dir / 'quality_summary.txt'}")


if __name__ == "__main__":
    main()

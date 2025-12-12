"""
Mask Quality Evaluation Metrics

Evaluates generated masks using multiple quantitative metrics:
- Coverage: Percentage of pixels that are masked
- Stability: Temporal consistency across frames
- Edge Quality: Boundary smoothness and precision
- Connectivity: Connected component analysis
"""

import os
import json
import numpy as np
from PIL import Image
from pathlib import Path
from scipy import ndimage
from collections import defaultdict
import cv2


def calculate_mask_coverage(mask_array):
    """Calculate percentage of masked pixels (foreground)"""
    if mask_array.size == 0:
        return 0.0
    total_pixels = mask_array.size
    masked_pixels = np.count_nonzero(mask_array)
    coverage = (masked_pixels / total_pixels) * 100
    return coverage


def calculate_edge_quality(mask_array):
    """
    Evaluate edge quality using:
    - Perimeter to area ratio (smoother = closer to 0)
    - Edge gradient smoothness
    """
    if np.count_nonzero(mask_array) == 0:
        return {"edge_sharpness": 0.0, "perimeter_ratio": 0.0}
    
    # Get edges using Canny
    mask_uint8 = (mask_array * 255).astype(np.uint8)
    edges = cv2.Canny(mask_uint8, 50, 150)
    
    # Edge sharpness: count of edge pixels / total boundary
    edge_pixels = np.count_nonzero(edges)
    masked_pixels = np.count_nonzero(mask_array)
    
    edge_sharpness = edge_pixels / max(masked_pixels, 1)
    
    # Perimeter analysis using contours
    contours, _ = cv2.findContours(mask_uint8, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        perimeter = sum(cv2.arcLength(c, True) for c in contours)
        area = masked_pixels
        perimeter_ratio = perimeter / (2 * np.sqrt(np.pi * area) + 1e-6)
    else:
        perimeter_ratio = 0.0
    
    return {
        "edge_sharpness": float(edge_sharpness),
        "perimeter_ratio": float(perimeter_ratio)
    }


def calculate_connectivity(mask_array):
    """
    Analyze connected components:
    - Number of components
    - Largest component ratio
    - Component uniformity
    """
    if np.count_nonzero(mask_array) == 0:
        return {
            "num_components": 0,
            "largest_ratio": 0.0,
            "component_uniformity": 0.0
        }
    
    # Label connected components
    labeled_array, num_features = ndimage.label(mask_array)
    
    total_masked = np.count_nonzero(mask_array)
    
    if num_features == 0:
        return {
            "num_components": 0,
            "largest_ratio": 0.0,
            "component_uniformity": 0.0
        }
    
    # Analyze component sizes
    component_sizes = np.bincount(labeled_array.flat)[1:]  # Skip background (0)
    
    if len(component_sizes) == 0:
        return {
            "num_components": 0,
            "largest_ratio": 0.0,
            "component_uniformity": 0.0
        }
    
    largest_ratio = np.max(component_sizes) / total_masked
    
    # Component uniformity: lower variance = more uniform
    if len(component_sizes) > 1:
        uniformity = 1.0 - (np.std(component_sizes) / np.mean(component_sizes))
        uniformity = max(0.0, min(1.0, uniformity))
    else:
        uniformity = 1.0
    
    return {
        "num_components": int(num_features),
        "largest_ratio": float(largest_ratio),
        "component_uniformity": float(uniformity)
    }


def calculate_temporal_stability(mask_dir, frame_numbers=None):
    """
    Calculate temporal consistency across frames:
    - Frame-to-frame intersection over union (IoU)
    - Mean absolute difference
    """
    mask_files = sorted(Path(mask_dir).glob("*_mask.png"))
    
    if len(mask_files) < 2:
        return {
            "avg_iou": 0.0,
            "avg_mse": 0.0,
            "temporal_consistency": 0.0
        }
    
    masks = []
    for mask_file in mask_files:
        mask = np.array(Image.open(mask_file).convert("L")) > 127
        masks.append(mask)
    
    # Calculate pairwise metrics
    ious = []
    mses = []
    
    for i in range(len(masks) - 1):
        m1 = masks[i].astype(np.float32)
        m2 = masks[i + 1].astype(np.float32)
        
        # IoU
        intersection = np.sum(m1 * m2)
        union = np.sum((m1 + m2) > 0)
        iou = intersection / (union + 1e-6)
        ious.append(iou)
        
        # MSE
        mse = np.mean((m1 - m2) ** 2)
        mses.append(mse)
    
    avg_iou = np.mean(ious) if ious else 0.0
    avg_mse = np.mean(mses) if mses else 0.0
    temporal_consistency = avg_iou  # Higher IoU = better consistency
    
    return {
        "avg_iou": float(avg_iou),
        "avg_mse": float(avg_mse),
        "temporal_consistency": float(temporal_consistency),
        "frame_count": len(masks)
    }


def evaluate_mask_set(mask_dir):
    """
    Comprehensively evaluate all masks in a directory
    Returns aggregated metrics
    """
    mask_files = sorted(Path(mask_dir).glob("*_mask.png"))
    
    if not mask_files:
        return None
    
    metrics = {
        "file_count": len(mask_files),
        "coverage": [],
        "edge_quality": {"edge_sharpness": [], "perimeter_ratio": []},
        "connectivity": {"num_components": [], "largest_ratio": [], "component_uniformity": []},
        "temporal": {}
    }
    
    # Process each frame
    for mask_file in mask_files:
        mask_array = np.array(Image.open(mask_file).convert("L")) > 127
        
        # Coverage
        coverage = calculate_mask_coverage(mask_array)
        metrics["coverage"].append(coverage)
        
        # Edge quality
        edge_metrics = calculate_edge_quality(mask_array)
        metrics["edge_quality"]["edge_sharpness"].append(edge_metrics["edge_sharpness"])
        metrics["edge_quality"]["perimeter_ratio"].append(edge_metrics["perimeter_ratio"])
        
        # Connectivity
        conn_metrics = calculate_connectivity(mask_array)
        metrics["connectivity"]["num_components"].append(conn_metrics["num_components"])
        metrics["connectivity"]["largest_ratio"].append(conn_metrics["largest_ratio"])
        metrics["connectivity"]["component_uniformity"].append(conn_metrics["component_uniformity"])
    
    # Temporal stability
    temporal_metrics = calculate_temporal_stability(mask_dir)
    metrics["temporal"] = temporal_metrics
    
    # Aggregate statistics
    aggregated = {
        "file_count": metrics["file_count"],
        "coverage": {
            "mean": float(np.mean(metrics["coverage"])),
            "std": float(np.std(metrics["coverage"])),
            "min": float(np.min(metrics["coverage"])),
            "max": float(np.max(metrics["coverage"]))
        },
        "edge_quality": {
            "edge_sharpness_mean": float(np.mean(metrics["edge_quality"]["edge_sharpness"])),
            "edge_sharpness_std": float(np.std(metrics["edge_quality"]["edge_sharpness"])),
            "perimeter_ratio_mean": float(np.mean(metrics["edge_quality"]["perimeter_ratio"])),
            "perimeter_ratio_std": float(np.std(metrics["edge_quality"]["perimeter_ratio"]))
        },
        "connectivity": {
            "num_components_mean": float(np.mean(metrics["connectivity"]["num_components"])),
            "num_components_max": float(np.max(metrics["connectivity"]["num_components"])),
            "largest_ratio_mean": float(np.mean(metrics["connectivity"]["largest_ratio"])),
            "component_uniformity_mean": float(np.mean(metrics["connectivity"]["component_uniformity"]))
        },
        "temporal": temporal_metrics
    }
    
    return aggregated


def score_mask_quality(metrics):
    """
    Generate overall quality score (0-100) based on metrics
    
    Scoring logic:
    - Coverage: 20-80% is ideal (not too sparse, not too dense)
    - Edge quality: Lower perimeter ratio is better (smoother)
    - Connectivity: Fewer components, high uniformity is better
    - Temporal stability: High IoU is better
    """
    if not metrics:
        return 0.0
    
    score = 0.0
    weight_total = 0.0
    
    # Coverage score (ideal 30-70%)
    cov_mean = metrics["coverage"]["mean"]
    if 20 <= cov_mean <= 80:
        cov_score = 100 * (1 - abs(cov_mean - 50) / 50)
    else:
        cov_score = max(0, 100 - abs(cov_mean - 50) / 2)
    score += cov_score * 0.25
    weight_total += 0.25
    
    # Edge quality score (lower perimeter ratio is better)
    perim_ratio = metrics["edge_quality"]["perimeter_ratio_mean"]
    edge_score = 100 * np.exp(-perim_ratio)  # Exponential decay
    score += edge_score * 0.25
    weight_total += 0.25
    
    # Connectivity score (prefer fewer components)
    num_comp = metrics["connectivity"]["num_components_mean"]
    largest_ratio = metrics["connectivity"]["largest_ratio_mean"]
    uniformity = metrics["connectivity"]["component_uniformity_mean"]
    
    comp_score = 50 * (1 / (1 + num_comp / 10)) + 50 * largest_ratio
    comp_score *= (0.5 + 0.5 * uniformity)
    score += comp_score * 0.25
    weight_total += 0.25
    
    # Temporal stability score
    temporal_score = metrics["temporal"]["temporal_consistency"] * 100
    score += temporal_score * 0.25
    weight_total += 0.25
    
    final_score = score / weight_total if weight_total > 0 else 0.0
    return max(0.0, min(100.0, final_score))


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python evaluate_masks.py <mask_directory> [output_json]")
        sys.exit(1)
    
    mask_dir = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.isdir(mask_dir):
        print(f"Error: Directory not found: {mask_dir}")
        sys.exit(1)
    
    print(f"Evaluating masks in: {mask_dir}")
    metrics = evaluate_mask_set(mask_dir)
    
    if metrics:
        quality_score = score_mask_quality(metrics)
        metrics["quality_score"] = quality_score
        
        print(json.dumps(metrics, indent=2))
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(metrics, f, indent=2)
            print(f"\nMetrics saved to: {output_file}")
    else:
        print("No masks found or error in evaluation")
        sys.exit(1)

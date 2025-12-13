#!/usr/bin/env python
"""
光流可视化脚本
将 .flo 文件转换为可视化图像，并将所有帧拼接成一张大图
"""

import numpy as np
import cv2
import os
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

def read_flo(filename):
    """
    读取 .flo 光流文件
    格式: magic(4) + width(4) + height(4) + flowdata(width*height*2*4)
    """
    with open(filename, 'rb') as f:
        magic = np.fromfile(f, np.uint8, count=4)
        w = np.fromfile(f, np.int32, count=1)[0]
        h = np.fromfile(f, np.int32, count=1)[0]
        
        data = np.fromfile(f, np.float32, count=2*w*h)
        flow = np.resize(data, (h, w, 2))
    
    return flow

def flow_to_color(flow, max_flow=None):
    """
    将光流转换为可视化的彩色图像
    使用 HSV 颜色空间：
    - Hue: 光流方向（0-360度）
    - Saturation: 动态调整（根据运动幅度）
    - Value: 光流大小
    
    颜色说明：
    - 红色: 向右运动
    - 绿色: 向下运动
    - 蓝色: 向左运动
    - 黄色: 向右下运动
    """
    h, w = flow.shape[:2]
    
    # 计算光流的大小和方向
    fx, fy = flow[:, :, 0], flow[:, :, 1]
    rad = np.sqrt(fx*fx + fy*fy)
    a = np.arctan2(-fy, -fx) / np.pi
    
    # 使用平方根来增强小运动的可见性
    if max_flow is None:
        max_flow = np.max(rad) + 1e-5
    
    # 正规化并应用非线性变换以增加亮度
    rad_normalized = rad / max_flow
    rad_normalized = np.sqrt(rad_normalized)  # 平方根增强亮度
    rad_normalized = np.clip(rad_normalized, 0, 1)
    
    # 创建 HSV 图像，增加 Saturation 来增强色彩饱和度
    img = np.zeros((h, w, 3), dtype=np.uint8)
    img[:, :, 0] = ((a + 1) / 2 * 180).astype(np.uint8)  # Hue (0-180 in OpenCV)
    img[:, :, 1] = (255 * np.sqrt(rad_normalized)).astype(np.uint8)  # Saturation (动态)
    img[:, :, 2] = (255 * rad_normalized).astype(np.uint8)   # Value
    
    # 转换为 BGR
    img = cv2.cvtColor(img, cv2.COLOR_HSV2BGR)
    
    # 应用对比度增强
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l_channel = lab[:, :, 0]
    l_channel = cv2.equalizeHist(l_channel) * 0.7 + l_channel * 0.3  # 轻微的直方图均衡化
    lab[:, :, 0] = l_channel
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    return img

def create_flow_legend(height=200, width=200):
    """
    创建光流色轮图例
    """
    center = (width // 2, height // 2)
    radius = min(height, width) // 2 - 10
    
    legend = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # 绘制色轮
    for angle in range(360):
        for r in range(radius):
            x = int(center[0] + r * np.cos(np.radians(angle)))
            y = int(center[1] - r * np.sin(np.radians(angle)))
            
            if 0 <= x < width and 0 <= y < height:
                # HSV 颜色
                h_val = int(angle * 180 / 360)  # OpenCV HSV H is 0-180
                s_val = 255
                v_val = 200
                hsv = np.uint8([[[h_val, s_val, v_val]]])
                bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)[0, 0]
                legend[y, x] = bgr
    
    # 添加标签
    cv2.putText(legend, 'Right', (center[0] + radius + 5, center[1] + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
    cv2.putText(legend, 'Down', (center[0] - 20, center[1] + radius + 15), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    cv2.putText(legend, 'Left', (center[0] - radius - 30, center[1] + 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)
    cv2.putText(legend, 'Up', (center[0] - 15, center[1] - radius - 5), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
    
    return legend

def visualize_flow_sequence(flow_dir_pattern, output_file, max_flow=None):
    """
    可视化一系列光流文件并拼接成一张大图
    
    Args:
        flow_dir_pattern: 光流文件的前缀或目录，如 './output_frames'
        output_file: 输出图像文件路径
        max_flow: 光流的最大值（用于颜色标准化）
    """
    
    # 查找所有 .flo 文件
    flo_files = sorted(Path('.').glob(f'{flow_dir_pattern}_*.flo'))
    
    if not flo_files:
        print(f"ERROR: No .flo files found matching pattern: {flow_dir_pattern}_*.flo")
        return
    
    print(f"Found {len(flo_files)} optical flow files")
    
    # 读取所有光流文件并转换为彩色图像
    flow_images = []
    max_rad = 0
    
    for i, flo_file in enumerate(flo_files):
        print(f"  Reading {flo_file.name}...", end=' ')
        try:
            flow = read_flo(str(flo_file))
            
            # 计算最大光流幅度（用于归一化）
            rad = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
            max_rad = max(max_rad, np.max(rad))
            
            flow_images.append(flow)
            print("✓")
        except Exception as e:
            print(f"ERROR: {e}")
    
    if not flow_images:
        print("ERROR: No flow images were successfully loaded")
        return
    
    print(f"\nMax optical flow magnitude: {max_rad:.2f}")
    
    # 转换为彩色图像
    color_images = []
    for i, flow in enumerate(flow_images):
        print(f"  Converting {i+1}/{len(flow_images)} to color...", end=' ')
        color_img = flow_to_color(flow, max_flow=max_rad)
        color_images.append(color_img)
        print("✓")
    
    # 计算拼接布局
    num_images = len(color_images)
    
    # 只显示前 24 帧
    num_images_to_show = min(24, num_images)
    color_images = color_images[:num_images_to_show]
    
    img_h, img_w = color_images[0].shape[:2]
    
    # 固定为6列，计算需要的行数
    cols = 6
    rows = int(np.ceil(num_images_to_show / cols))
    
    print(f"\nTiling layout: {rows} rows x {cols} columns")
    print(f"Displaying {num_images_to_show} frames (out of {num_images} total)")
    
    # 创建色轮图例
    legend = create_flow_legend(height=img_h, width=img_w)
    
    # 创建大图 - 只包含实际需要的行
    padding = 10
    text_height = 40  # 为标题留出空间
    
    # 计算实际需要的高度，不留多余空间
    # 标题 + 图例行 + (额外行数) * 行高
    actual_rows_needed = rows - 1  # 因为第一行包含图例
    canvas_h = text_height + padding + img_h + padding + actual_rows_needed * (img_h + padding)
    canvas_w = cols * img_w + (cols - 1) * padding
    canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 255
    
    # 添加标题文字
    title = "Optical Flow Visualization - Batman6"
    cv2.putText(canvas, title, (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    
    # 放置图例在第一行左侧
    legend_start_y = text_height + padding
    canvas[legend_start_y:legend_start_y+img_h, 0:img_w] = legend
    
    # 添加图例标签
    cv2.putText(canvas, "Color Wheel Legend", (10, legend_start_y + img_h + 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    
    # 放置光流图像
    idx = 0
    for row in range(rows):
        for col in range(cols):
            if idx >= num_images_to_show:
                break
            
            # 第一行的图像从第二列开始（第一列放图例）
            if row == 0:
                x = (col + 1) * (img_w + padding)
            else:
                x = col * (img_w + padding)
            
            y = legend_start_y + row * (img_h + padding)
            
            # 确保不超出边界
            if x + img_w <= canvas_w and y + img_h <= canvas_h:
                canvas[y:y+img_h, x:x+img_w] = color_images[idx]
                
                # 添加帧编号标签
                cv2.putText(canvas, f"Frame {idx}", (x + 5, y + 25), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            idx += 1
    
    # 保存结果
    print(f"\nSaving visualization to {output_file}...")
    cv2.imwrite(output_file, canvas)
    print(f"✓ Saved to {output_file}")
    print(f"  Image size: {canvas_w} x {canvas_h}")
    
    return canvas

def create_flow_video(flow_dir_pattern, output_video, fps=30):
    """
    从光流序列创建视频
    
    Args:
        flow_dir_pattern: 光流文件的前缀
        output_video: 输出视频文件路径
        fps: 视频帧率
    """
    
    # 查找所有 .flo 文件
    flo_files = sorted(Path('.').glob(f'{flow_dir_pattern}_*.flo'))
    
    if not flo_files:
        print(f"ERROR: No .flo files found matching pattern: {flow_dir_pattern}_*.flo")
        return
    
    print(f"Creating video from {len(flo_files)} frames...")
    
    # 读取第一帧以获取尺寸
    flow = read_flo(str(flo_files[0]))
    h, w = flow.shape[:2]
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_video, fourcc, fps, (w, h))
    
    max_rad = 0
    
    # 先计算最大光流幅度
    print("  Calculating max flow magnitude...", end=' ')
    for flo_file in flo_files:
        flow = read_flo(str(flo_file))
        rad = np.sqrt(flow[:, :, 0]**2 + flow[:, :, 1]**2)
        max_rad = max(max_rad, np.max(rad))
    print("✓")
    
    # 写入帧
    print("  Writing frames...", end=' ')
    for flo_file in flo_files:
        flow = read_flo(str(flo_file))
        color_img = flow_to_color(flow, max_flow=max_rad)
        out.write(color_img)
    print("✓")
    
    out.release()
    print(f"✓ Video saved to {output_video}")

if __name__ == '__main__':
    import sys
    
    # 默认参数
    flow_pattern = 'output_frames'
    output_dir = 'optical_flow_output'
    
    # 解析命令行参数
    if len(sys.argv) > 1:
        flow_pattern = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # 创建输出文件夹
    os.makedirs(output_dir, exist_ok=True)
    
    output_image = os.path.join(output_dir, 'optical_flow_visualization.png')
    output_video = os.path.join(output_dir, 'optical_flow_visualization.mp4')
    
    print("="*60)
    print("Optical Flow Visualization")
    print("="*60)
    print(f"Output directory: {output_dir}\n")
    
    # 可视化为拼接图
    canvas = visualize_flow_sequence(flow_pattern, output_image)
    
    print("\n" + "="*60)
    print("Creating video from optical flow sequence...")
    print("="*60)
    
    # 创建视频
    create_flow_video(flow_pattern, output_video, fps=10)
    
    print("\n✓ All visualizations complete!")
    print(f"  - Image: {output_image}")
    print(f"  - Video: {output_video}")

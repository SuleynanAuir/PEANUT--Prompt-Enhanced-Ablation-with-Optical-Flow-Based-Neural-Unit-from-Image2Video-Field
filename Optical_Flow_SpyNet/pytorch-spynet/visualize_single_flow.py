#!/usr/bin/env python
"""
单个光流文件的可视化脚本
"""

import numpy as np
import cv2
import os
from pathlib import Path

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
    """
    h, w = flow.shape[:2]
    
    # 计算光流的大小和方向
    fx, fy = flow[:, :, 0], flow[:, :, 1]
    rad = np.sqrt(fx*fx + fy*fy)
    a = np.arctan2(-fy, -fx) / np.pi
    
    # 使用平方根来增强小运动的可见性
    if max_flow is None:
        max_flow = np.max(rad) + 1e-5
    
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
    l_channel = cv2.equalizeHist(l_channel) * 0.7 + l_channel * 0.3
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
                h_val = int(angle * 180 / 360)
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

if __name__ == '__main__':
    import sys
    
    # 默认参数
    flo_file = 'optical_flow_output_2frames/batman6_output.flo'
    output_dir = 'optical_flow_output_2frames'
    
    if len(sys.argv) > 1:
        flo_file = sys.argv[1]
    if len(sys.argv) > 2:
        output_dir = sys.argv[2]
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(flo_file):
        print(f"ERROR: File not found: {flo_file}")
        sys.exit(1)
    
    print("="*60)
    print("Single Frame Pair Optical Flow Visualization")
    print("="*60)
    
    # 读取光流
    print(f"\nReading optical flow from: {flo_file}")
    flow = read_flo(flo_file)
    print(f"Flow shape: {flow.shape}")
    
    # 转换为彩色图像
    print("Converting to color visualization...")
    color_img = flow_to_color(flow)
    
    # 创建色轮图例
    legend = create_flow_legend(height=color_img.shape[0], width=color_img.shape[1])
    
    # 并排显示
    padding = 20
    canvas = np.ones((color_img.shape[0], color_img.shape[1] * 2 + padding, 3), dtype=np.uint8) * 255
    canvas[:, :color_img.shape[1]] = legend
    canvas[:, color_img.shape[1] + padding:] = color_img
    
    # 添加标题
    output_image = os.path.join(output_dir, 'optical_flow_single.png')
    
    # 添加标题行
    title_height = 50
    final_canvas = np.ones((color_img.shape[0] + title_height, canvas.shape[1], 3), dtype=np.uint8) * 255
    cv2.putText(final_canvas, "Optical Flow: Batman6 (Frame 0-1)", (20, 35), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)
    final_canvas[title_height:, :] = canvas
    
    # 保存结果
    print(f"\nSaving visualization to: {output_image}")
    cv2.imwrite(output_image, final_canvas)
    print(f"✓ Image size: {final_canvas.shape[1]} x {final_canvas.shape[0]}")
    
    print("\n✓ Visualization complete!")

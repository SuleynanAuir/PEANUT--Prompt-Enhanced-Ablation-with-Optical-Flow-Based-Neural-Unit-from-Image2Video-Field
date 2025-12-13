#!/usr/bin/env python
"""
示例：演示如何使用 frames_package 参数运行光流估计

这个脚本展示了如何：
1. 创建一个帧包（frames_package）
2. 使用 --frames-package 参数调用 run.py
"""

import numpy
import pickle
import os
from PIL import Image

def create_sample_frames_package():
    """
    创建一个示例帧包，包含多个帧
    每个帧是一个 numpy 数组，形状为 (height, width, 3)，值范围 0-255
    """
    # 从现有的示例图像加载帧
    frame_one = numpy.array(Image.open('./images/one.png'))
    frame_two = numpy.array(Image.open('./images/two.png'))
    
    # 创建帧包（可以包含更多帧）
    frames_package = numpy.array([frame_one, frame_two])
    
    return frames_package

def save_frames_package(frames_package, output_path):
    """
    将帧包保存为 pickle 文件
    """
    with open(output_path, 'wb') as f:
        pickle.dump(frames_package, f)
    print(f"✓ 帧包已保存到: {output_path}")

def save_frames_package_npy(frames_package, output_path):
    """
    将帧包保存为 numpy 格式
    """
    numpy.save(output_path, frames_package)
    print(f"✓ 帧包已保存到: {output_path}")

if __name__ == '__main__':
    # 创建示例帧包
    print("正在创建示例帧包...")
    frames_package = create_sample_frames_package()
    print(f"✓ 帧包已创建，包含 {len(frames_package)} 帧")
    print(f"  每帧的形状: {frames_package[0].shape}")
    
    # 保存为 pickle 格式
    pickle_path = './frames_package.pkl'
    save_frames_package(frames_package, pickle_path)
    
    # 保存为 npy 格式
    npy_path = './frames_package.npy'
    save_frames_package_npy(frames_package, npy_path)
    
    # 显示使用方法
    print("\n" + "="*50)
    print("使用方法:")
    print("="*50)
    print("\n方法 1: 使用 pickle 格式")
    print(f"  python run.py --frames-package {pickle_path} --out ./output_pickle")
    
    print("\n方法 2: 使用 numpy 格式")
    print(f"  python run.py --frames-package {npy_path} --out ./output_npy")
    
    print("\n使用示例:")
    print("  python run.py --model sintel-final --frames-package frames_package.pkl --out optical_flow")

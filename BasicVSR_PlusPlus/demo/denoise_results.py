# Copyright (c) OpenMMLab. All rights reserved.
"""
去噪模块 - 对视频超分结果进行去噪处理
支持多种去噪方法：
1. 非局部均值去噪 (Non-Local Means Denoising)
2. 双边滤波 (Bilateral Filter)
3. 高斯滤波 (Gaussian Blur)
4. 中值滤波 (Median Filter)
5. 快速去噪 (Fast Denoising)
"""

import argparse
import os
import glob
from pathlib import Path

import cv2
import numpy as np
from tqdm import tqdm


def parse_args():
    parser = argparse.ArgumentParser(description='视频结果去噪工具')
    parser.add_argument('input_dir', help='输入图像序列目录')
    parser.add_argument('output_dir', help='输出去噪后的目录')
    parser.add_argument(
        '--method',
        type=str,
        default='nlm',
        choices=['nlm', 'bilateral', 'gaussian', 'median', 'fast'],
        help='去噪方法: nlm(非局部均值), bilateral(双边滤波), '
             'gaussian(高斯滤波), median(中值滤波), fast(快速去噪)')
    parser.add_argument(
        '--strength',
        type=int,
        default=5,
        help='去噪强度 (1-20, 数值越大去噪越强，默认5)')
    parser.add_argument(
        '--preserve-details',
        action='store_true',
        help='保留更多细节 (使用更保守的去噪参数)')
    parser.add_argument(
        '--color-strength',
        type=int,
        default=None,
        help='彩色去噪强度 (仅用于nlm和fast方法)')
    parser.add_argument(
        '--create-video',
        action='store_true',
        help='同时创建视频文件')
    parser.add_argument(
        '--fps',
        type=int,
        default=30,
        help='输出视频的帧率 (默认30)')
    parser.add_argument(
        '--speed',
        type=float,
        default=1.0,
        help='视频播放速度倍数 (0.5=慢放2倍, 1.0=正常, 2.0=快放2倍)')
    args = parser.parse_args()
    return args


def denoise_nlm(img, h, h_color=None, preserve_details=False):
    """非局部均值去噪 - 质量最好但速度较慢"""
    if h_color is None:
        h_color = h
    
    if preserve_details:
        # 保留细节模式：使用较小的搜索窗口
        template_window_size = 5
        search_window_size = 15
    else:
        # 标准模式
        template_window_size = 7
        search_window_size = 21
    
    return cv2.fastNlMeansDenoisingColored(
        img,
        None,
        h=h,
        hColor=h_color,
        templateWindowSize=template_window_size,
        searchWindowSize=search_window_size
    )


def denoise_bilateral(img, d, sigma_color, sigma_space):
    """双边滤波 - 在去噪的同时保持边缘清晰"""
    return cv2.bilateralFilter(img, d, sigma_color, sigma_space)


def denoise_gaussian(img, kernel_size, sigma):
    """高斯滤波 - 简单快速的模糊去噪"""
    return cv2.GaussianBlur(img, (kernel_size, kernel_size), sigma)


def denoise_median(img, kernel_size):
    """中值滤波 - 对椒盐噪声效果好"""
    return cv2.medianBlur(img, kernel_size)


def denoise_fast(img, h, h_color=None):
    """快速去噪 - 速度快但质量略低于NLM"""
    if h_color is None:
        h_color = h
    return cv2.fastNlMeansDenoisingColored(
        img,
        None,
        h=h,
        hColor=h_color,
        templateWindowSize=5,
        searchWindowSize=11
    )


def denoise_image(img, method, strength, color_strength=None, preserve_details=False):
    """
    对单张图像进行去噪
    
    Args:
        img: 输入图像
        method: 去噪方法
        strength: 去噪强度
        color_strength: 彩色去噪强度
        preserve_details: 是否保留细节
    
    Returns:
        去噪后的图像
    """
    if method == 'nlm':
        # 非局部均值去噪
        h = strength
        h_color = color_strength if color_strength is not None else strength
        result = denoise_nlm(img, h, h_color, preserve_details)
    
    elif method == 'bilateral':
        # 双边滤波
        d = 9 if preserve_details else 15
        sigma_color = strength * 10
        sigma_space = strength * 10
        result = denoise_bilateral(img, d, sigma_color, sigma_space)
    
    elif method == 'gaussian':
        # 高斯滤波
        kernel_size = 3 + (strength // 5) * 2  # 确保是奇数
        kernel_size = min(kernel_size, 15)  # 最大15
        sigma = strength * 0.5
        result = denoise_gaussian(img, kernel_size, sigma)
    
    elif method == 'median':
        # 中值滤波
        kernel_size = 3 + (strength // 5) * 2  # 确保是奇数
        kernel_size = min(kernel_size, 13)  # 最大13
        if kernel_size % 2 == 0:
            kernel_size += 1
        result = denoise_median(img, kernel_size)
    
    elif method == 'fast':
        # 快速去噪
        h = strength
        h_color = color_strength if color_strength is not None else strength
        result = denoise_fast(img, h, h_color)
    
    else:
        raise ValueError(f"未知的去噪方法: {method}")
    
    return result


def get_image_files(input_dir):
    """获取目录中的所有图像文件"""
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif']
    image_files = []
    
    for ext in image_extensions:
        pattern = os.path.join(input_dir, f'*{ext}')
        image_files.extend(glob.glob(pattern, recursive=False))
    
    # 去重并排序
    image_files = sorted(list(set(image_files)))
    return image_files


def create_video_from_images(image_files, output_path, fps=30):
    """从图像序列创建视频"""
    if not image_files:
        print("没有找到图像文件")
        return
    
    # 读取第一张图像获取尺寸
    first_img = cv2.imread(image_files[0])
    if first_img is None:
        print(f"错误: 无法读取第一张图像 {image_files[0]}")
        return
    h, w = first_img.shape[:2]
    
    # 创建视频写入器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (w, h))
    
    if not video_writer.isOpened():
        print(f"错误: 无法创建视频文件 {output_path}")
        return
    
    print(f"正在创建视频: {output_path}")
    print(f"视频参数: {len(image_files)} 帧, {fps} fps, 分辨率 {w}x{h}")
    
    frames_written = 0
    for img_path in tqdm(image_files, desc="写入视频"):
        img = cv2.imread(img_path)
        if img is not None:
            video_writer.write(img)
            frames_written += 1
        else:
            print(f"警告: 无法读取图像 {img_path}")
    
    video_writer.release()
    print(f"视频已保存到: {output_path}")
    print(f"成功写入 {frames_written} 帧，视频时长: {frames_written/fps:.2f} 秒")


def main():
    args = parse_args()
    
    # 检查输入目录
    if not os.path.isdir(args.input_dir):
        print(f"错误: 输入目录不存在: {args.input_dir}")
        return
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 获取所有图像文件
    image_files = get_image_files(args.input_dir)
    
    if not image_files:
        print(f"错误: 在 {args.input_dir} 中没有找到图像文件")
        return
    
    print(f"找到 {len(image_files)} 张图像")
    print(f"去噪方法: {args.method}")
    print(f"去噪强度: {args.strength}")
    if args.preserve_details:
        print("模式: 保留细节")
    
    # 方法说明
    method_descriptions = {
        'nlm': '非局部均值去噪 (质量最好，速度较慢)',
        'bilateral': '双边滤波 (保持边缘，速度中等)',
        'gaussian': '高斯滤波 (简单快速)',
        'median': '中值滤波 (适合椒盐噪声)',
        'fast': '快速去噪 (速度快)'
    }
    print(f"方法说明: {method_descriptions.get(args.method, '未知')}")
    
    # 处理每张图像
    output_files = []
    for img_path in tqdm(image_files, desc="去噪处理"):
        # 读取图像
        img = cv2.imread(img_path)
        if img is None:
            print(f"警告: 无法读取图像 {img_path}")
            continue
        
        # 去噪
        denoised = denoise_image(
            img,
            args.method,
            args.strength,
            args.color_strength,
            args.preserve_details
        )
        
        # 保存
        filename = os.path.basename(img_path)
        output_path = os.path.join(args.output_dir, filename)
        cv2.imwrite(output_path, denoised)
        output_files.append(output_path)
    
    print(f"\n完成! 去噪后的图像已保存到: {args.output_dir}")
    print(f"处理了 {len(output_files)} 张图像")
    
    # 创建视频（如果需要）
    if args.create_video:
        video_name = os.path.basename(args.input_dir.rstrip('/\\')) + '_denoised.mp4'
        video_path = os.path.join(os.path.dirname(args.output_dir), video_name)
        # 重新扫描输出目录确保获取所有文件并正确排序
        denoised_files = get_image_files(args.output_dir)
        # 根据速度倍数调整帧率
        actual_fps = int(args.fps * args.speed)
        print(f"\n准备创建视频，共 {len(denoised_files)} 帧")
        print(f"原始帧率: {args.fps} fps, 速度倍数: {args.speed}x, 实际帧率: {actual_fps} fps")
        print(f"预计视频时长: {len(denoised_files)/actual_fps:.2f} 秒")
        create_video_from_images(denoised_files, video_path, actual_fps)
    
    # 显示推荐的参数范围
    print("\n参数建议:")
    print("  轻度去噪: --strength 3-5")
    print("  中度去噪: --strength 6-10")
    print("  强力去噪: --strength 11-15")
    print("  保留细节: 添加 --preserve-details 参数")
    print("  视频减速: --speed 0.5 (慢放2倍)")
    print("  视频加速: --speed 2.0 (快放2倍)")


if __name__ == '__main__':
    main()

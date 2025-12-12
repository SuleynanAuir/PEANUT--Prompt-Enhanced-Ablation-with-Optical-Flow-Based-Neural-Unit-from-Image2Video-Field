import sys
import cv2
import numpy as np
from pathlib import Path


def _read_all_frames(path: str):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频文件: {path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 0
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames, fps


def create_side_by_side_video(left_path: str, right_path: str, output_path: str,
                               border_color_left=(255, 65, 54), border_color_right=(0, 116, 217),
                               border_width=4):
    """
    创建左右并排对比视频，强制逐帧同步：长度取两者最短帧数，按索引线性对齐。
    """
    left_frames, fps_l = _read_all_frames(left_path)
    right_frames, fps_r = _read_all_frames(right_path)

    if not left_frames or not right_frames:
        raise RuntimeError("未读取到帧，请检查视频路径或编码")

    # 目标帧数与 fps
    target_frames = min(len(left_frames), len(right_frames))
    target_fps = max(1.0, min(fps_l or 30, fps_r or 30))

    # 采样索引（线性映射到最短长度）
    idx_l = np.linspace(0, len(left_frames) - 1, target_frames).round().astype(int)
    idx_r = np.linspace(0, len(right_frames) - 1, target_frames).round().astype(int)

    # 尺寸与缩放：统一高度 = 左侧首帧高度
    h_l, w_l = left_frames[0].shape[:2]
    h_r, w_r = right_frames[0].shape[:2]
    target_h = h_l
    w_r_scaled = int(w_r * target_h / h_r)

    gap = 20
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None

    print(f"[INFO] 开始合成视频... 目标帧数={target_frames}, fps={target_fps:.2f}")
    frame_count = 0

    for il, ir in zip(idx_l, idx_r):
        frame_l = left_frames[il]
        frame_r = right_frames[ir]

        frame_r_resized = cv2.resize(frame_r, (w_r_scaled, target_h))

        frame_l_bordered = cv2.copyMakeBorder(
            frame_l, border_width, border_width, border_width, border_width,
            cv2.BORDER_CONSTANT, value=border_color_left
        )
        frame_r_bordered = cv2.copyMakeBorder(
            frame_r_resized, border_width, border_width, border_width, border_width,
            cv2.BORDER_CONSTANT, value=border_color_right
        )

        l_h, l_w = frame_l_bordered.shape[:2]
        r_h, r_w = frame_r_bordered.shape[:2]
        canvas_h = max(l_h, r_h)
        canvas_w = l_w + gap + r_w
        canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 240

        canvas[:l_h, :l_w] = frame_l_bordered
        x_offset = l_w + gap
        canvas[:r_h, x_offset:x_offset + r_w] = frame_r_bordered

        if out is None:
            out = cv2.VideoWriter(output_path, fourcc, target_fps, (canvas.shape[1], canvas.shape[0]))

        out.write(canvas)
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"[INFO] 已处理 {frame_count} 帧...")

    if out:
        out.release()

    print(f"[OK] 合成完成: {output_path} ({frame_count} 帧, fps={target_fps:.2f})")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("用法: python tools/create_comparison_video.py <left_mp4> <right_mp4> <output_mp4>")
        sys.exit(1)
    
    left = sys.argv[1]
    right = sys.argv[2]
    output = sys.argv[3]
    
    create_side_by_side_video(left, right, output)

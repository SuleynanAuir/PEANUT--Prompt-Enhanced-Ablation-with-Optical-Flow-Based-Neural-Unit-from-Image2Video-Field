import sys
from pathlib import Path

import cv2
import numpy as np
import imageio.v3 as iio


def mp4_to_gif(src_mp4: Path, dst_gif: Path, fps: int = 12, scale: float = 0.5):
    if not src_mp4.exists():
        raise FileNotFoundError(f"源视频不存在: {src_mp4}")

    cap = cv2.VideoCapture(str(src_mp4))
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {src_mp4}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if scale and scale != 1.0:
            h, w = frame.shape[:2]
            new_w = max(1, int(w * scale))
            new_h = max(1, int(h * scale))
            frame = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frames.append(frame)

    cap.release()

    if not frames:
        raise RuntimeError("未能从视频读取到帧，请检查视频编码或路径。")

    dst_gif.parent.mkdir(parents=True, exist_ok=True)
    iio.imwrite(dst_gif, frames, plugin='pillow', duration=1.0 / fps, loop=0)
    print(f"[OK] GIF 已生成: {dst_gif} ({len(frames)} 帧, fps={fps}, scale={scale})")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("用法: python tools/mp4_to_gif.py <src_mp4> <dst_gif> [fps] [scale]")
        sys.exit(1)
    src = Path(sys.argv[1])
    dst = Path(sys.argv[2])
    fps = int(sys.argv[3]) if len(sys.argv) >= 4 else 12
    scale = float(sys.argv[4]) if len(sys.argv) >= 5 else 0.5
    mp4_to_gif(src, dst, fps=fps, scale=scale)

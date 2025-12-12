import sys
import cv2
import numpy as np


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


def create_triple_comparison(left_path: str, mid_path: str, right_path: str, output_path: str,
                             border_left=(54, 65, 255),   # BGR 红框
                             border_mid=(80, 80, 80),     # BGR 灰框（掩码）
                             border_right=(217, 116, 0),  # BGR 蓝框
                             border_width=4,
                             gap=20):
    left_frames, fps_l = _read_all_frames(left_path)
    mid_frames, fps_m = _read_all_frames(mid_path)
    right_frames, fps_r = _read_all_frames(right_path)

    if not left_frames or not mid_frames or not right_frames:
        raise RuntimeError("未读取到帧，请检查视频路径或编码")

    target_frames = min(len(left_frames), len(mid_frames), len(right_frames))
    target_fps = max(1.0, min(fps_l or 30, fps_m or 30, fps_r or 30))

    idx_l = np.linspace(0, len(left_frames) - 1, target_frames).round().astype(int)
    idx_m = np.linspace(0, len(mid_frames) - 1, target_frames).round().astype(int)
    idx_r = np.linspace(0, len(right_frames) - 1, target_frames).round().astype(int)

    # 基准高度取左侧首帧高度
    h_l, w_l = left_frames[0].shape[:2]
    h_m, w_m = mid_frames[0].shape[:2]
    h_r, w_r = right_frames[0].shape[:2]
    target_h = h_l
    w_m_scaled = int(w_m * target_h / h_m)
    w_r_scaled = int(w_r * target_h / h_r)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = None
    frame_count = 0
    print(f"[INFO] 开始三合一合成... 目标帧数={target_frames}, fps={target_fps:.2f}")

    for il, im, ir in zip(idx_l, idx_m, idx_r):
        fl = left_frames[il]
        fm = mid_frames[im]
        fr = right_frames[ir]

        fm = cv2.resize(fm, (w_m_scaled, target_h))
        fr = cv2.resize(fr, (w_r_scaled, target_h))

        fl_b = cv2.copyMakeBorder(fl, border_width, border_width, border_width, border_width,
                                  cv2.BORDER_CONSTANT, value=border_left)
        fm_b = cv2.copyMakeBorder(fm, border_width, border_width, border_width, border_width,
                                  cv2.BORDER_CONSTANT, value=border_mid)
        fr_b = cv2.copyMakeBorder(fr, border_width, border_width, border_width, border_width,
                                  cv2.BORDER_CONSTANT, value=border_right)

        l_h, l_w = fl_b.shape[:2]
        m_h, m_w = fm_b.shape[:2]
        r_h, r_w = fr_b.shape[:2]
        canvas_h = max(l_h, m_h, r_h)
        canvas_w = l_w + gap + m_w + gap + r_w
        canvas = np.ones((canvas_h, canvas_w, 3), dtype=np.uint8) * 240

        # 左、中、右依次放置
        x0 = 0
        canvas[:l_h, x0:x0 + l_w] = fl_b
        x1 = x0 + l_w + gap
        canvas[:m_h, x1:x1 + m_w] = fm_b
        x2 = x1 + m_w + gap
        canvas[:r_h, x2:x2 + r_w] = fr_b

        if out is None:
            out = cv2.VideoWriter(output_path, fourcc, target_fps, (canvas.shape[1], canvas.shape[0]))
        out.write(canvas)
        frame_count += 1
        if frame_count % 10 == 0:
            print(f"[INFO] 已处理 {frame_count} 帧...")

    if out:
        out.release()

    print(f"[OK] 三合一合成完成: {output_path} ({frame_count} 帧, fps={target_fps:.2f})")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("用法: python tools/create_triple_comparison_video.py <left_mp4> <mid_mp4> <right_mp4> <output_mp4>")
        sys.exit(1)
    left = sys.argv[1]
    mid = sys.argv[2]
    right = sys.argv[3]
    out = sys.argv[4]
    create_triple_comparison(left, mid, right, out)

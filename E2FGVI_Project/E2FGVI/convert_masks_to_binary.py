import os
import cv2
import argparse
import numpy as np


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def to_binary_mask(img, threshold: int):
    # If image has alpha channel, prefer it
    if img is None:
        raise ValueError("Image load failed")
    if img.shape[2] == 4:
        alpha = img[:, :, 3]
        base = alpha
    else:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        base = gray
    _, bw = cv2.threshold(base, threshold, 255, cv2.THRESH_BINARY)
    return bw


def post_process(mask, close_k: int, erode_k: int, dilate_k: int):
    res = mask
    if close_k > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (close_k, close_k))
        res = cv2.morphologyEx(res, cv2.MORPH_CLOSE, k)
    if erode_k > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (erode_k, erode_k))
        res = cv2.erode(res, k)
    if dilate_k > 0:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dilate_k, dilate_k))
        res = cv2.dilate(res, k)
    return res


def convert_dir(src_dir: str, dst_dir: str, threshold: int, close_k: int, erode_k: int, dilate_k: int):
    ensure_dir(dst_dir)
    files = sorted([f for f in os.listdir(src_dir) if f.lower().endswith((".png", ".jpg", ".jpeg"))])
    converted = 0
    for f in files:
        src_path = os.path.join(src_dir, f)
        img = cv2.imread(src_path, cv2.IMREAD_UNCHANGED)
        if img is None:
            print(f"Skip (load fail): {src_path}")
            continue
        bw = to_binary_mask(img, threshold)
        bw = post_process(bw, close_k, erode_k, dilate_k)
        # Force single channel output
        out_path = os.path.join(dst_dir, f.rsplit('.', 1)[0] + '.png')
        cv2.imwrite(out_path, bw)
        converted += 1
    return converted, len(files)


def main():
    parser = argparse.ArgumentParser(description="Convert colored/alpha masks to binary (black/white) PNG masks.")
    parser.add_argument("--src", required=True, help="Source mask directory (e.g. examples/the_horese_jumping_mask)")
    parser.add_argument("--dst", required=True, help="Destination directory for binary masks")
    parser.add_argument("--threshold", type=int, default=5, help="Pixel threshold (0-255) for foreground")
    parser.add_argument("--close-k", type=int, default=3, help="Kernel size for morphological closing (0 disable)")
    parser.add_argument("--erode-k", type=int, default=0, help="Kernel size for erosion (0 disable)")
    parser.add_argument("--dilate-k", type=int, default=0, help="Kernel size for dilation (0 disable)")
    args = parser.parse_args()

    converted, total = convert_dir(args.src, args.dst, args.threshold, args.close_k, args.erode_k, args.dilate_k)
    print(f"Converted {converted}/{total} masks to binary in {args.dst}")


if __name__ == "__main__":
    main()

import os
import sys
import json
from PIL import Image

# Explicit color map per category value
COLOR_MAP = {
    "threshold": {
        "0.3": (255, 105, 180),  # pink
        "0.5": (60, 179, 113),   # green
        "0.7": (65, 105, 225),   # blue
    },
    "model": {
        "tiny": (255, 105, 180),  # pink
        "base": (60, 179, 113),   # green
        "large": (65, 105, 225),  # blue
    },
    "window": {
        "4": (255, 105, 180),   # pink
        "8": (60, 179, 113),    # green
        "16": (65, 105, 225),   # blue
    },
}


def pick_color(category: str, value: str, idx: int):
    cmap = COLOR_MAP.get(category, {})
    if value in cmap:
        return cmap[value]
    # fallback by order
    fallback = list(cmap.values())
    if idx < len(fallback):
        return fallback[idx]
    return (255, 0, 0)


def extract_value(category: str, test_dir: str):
    name = os.path.basename(test_dir)
    parts = name.split("_")
    if category == "threshold" and len(parts) >= 2:
        return parts[1]
    if category == "model" and len(parts) >= 2:
        return parts[1]
    if category == "window" and len(parts) >= 2:
        # window_4 -> parts[1] = '4'
        return parts[1]
    return None


def find_mask(test_dir: str, frame_num: int):
    patterns = [
        f"frame_{frame_num:05d}_mask.png",
        f"{frame_num:05d}_mask.png",
        f"{frame_num:05d}.png",
    ]
    for root, dirs, files in os.walk(test_dir):
        for pat in patterns:
            candidate = os.path.join(root, pat)
            if os.path.exists(candidate):
                return candidate
    return None


def overlay_masks(config):
    test_dirs = config["test_dirs"]
    frame_numbers = config["frame_numbers"]
    output_dir = config["output_dir"]
    source_frames_dir = config["source_frames_dir"]
    category = config.get("category", "threshold")
    os.makedirs(output_dir, exist_ok=True)

    for frame_num in frame_numbers:
        # load original
        orig = None
        for pat in [f"frame_{frame_num:05d}.png", f"{frame_num:05d}.png", f"frame_{frame_num:05d}.jpg"]:
            p = os.path.join(source_frames_dir, pat)
            if os.path.exists(p):
                orig = Image.open(p).convert("RGBA")
                break
        if orig is None:
            print(f"Missing original frame {frame_num} in {source_frames_dir}")
            continue

        base = orig.copy()

        for idx, test_dir in enumerate(test_dirs):
            mask_path = find_mask(test_dir, frame_num)
            if not mask_path:
                print(f"Mask missing: frame {frame_num} in {test_dir}")
                continue
            mask = Image.open(mask_path).convert("L")
            value = extract_value(category, test_dir)
            color = pick_color(category, value, idx)
            # build overlay with alpha from mask
            overlay = Image.new("RGBA", base.size, color + (0,))
            # use mask as alpha scaled
            overlay.putalpha(mask)
            base = Image.alpha_composite(base, overlay)

        # save overlay image directly without legend
        out_path = os.path.join(output_dir, f"overlay_frame_{frame_num:05d}.png")
        base.convert("RGB").save(out_path, quality=95)
        print(f"Saved {out_path}")


if __name__ == "__main__":
    cfg_path = sys.argv[1]
    with open(cfg_path, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    overlay_masks(cfg)

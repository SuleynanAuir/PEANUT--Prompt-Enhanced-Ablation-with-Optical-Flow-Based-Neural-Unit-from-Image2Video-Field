import cv2
import numpy as np
import os
from PIL import Image

def check_mask_colors(mask_dir):
    """Check for non-binary color values in mask files"""
    files = sorted([f for f in os.listdir(mask_dir) if f.endswith('.png')])
    
    print(f"Checking {len(files)} mask files in {mask_dir}...\n")
    
    for i, fname in enumerate(files[:5]):  # Check first 5 files
        path = os.path.join(mask_dir, fname)
        
        # Read as color
        img_bgr = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        img_pil = Image.open(path)
        
        print(f"File: {fname}")
        print(f"  PIL mode: {img_pil.mode}")
        print(f"  OpenCV shape: {img_bgr.shape}")
        print(f"  OpenCV dtype: {img_bgr.dtype}")
        
        # Check unique values
        if len(img_bgr.shape) == 3:
            # Color image
            unique_colors = np.unique(img_bgr.reshape(-1, img_bgr.shape[2]), axis=0)
            print(f"  Unique colors (BGR): {unique_colors[:10]}")  # Show first 10
            
            # Check for orange/yellow
            for color in unique_colors:
                b, g, r = color[0], color[1], color[2]
                if r > 200 and g > 100 and b < 100:
                    print(f"  ⚠️ WARNING: Orange/yellow color found: BGR({b}, {g}, {r})")
        else:
            unique_vals = np.unique(img_bgr)
            print(f"  Unique grayscale values: {unique_vals}")
        
        # Convert to L and check
        m_l = np.array(img_pil.convert('L'))
        print(f"  After convert('L') unique: {np.unique(m_l)}")
        
        # Simulate test.py processing
        m_binary = np.array(m_l > 0).astype(np.uint8)
        print(f"  After (>0) binary unique: {np.unique(m_binary)}")
        
        print()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--mask_dir", required=True, help="Path to mask directory")
    args = parser.parse_args()
    
    check_mask_colors(args.mask_dir)

"""Extract frames from video for overlay visualization"""
import cv2
import os
import sys

def extract_frames(video_path, output_dir, fps=None):
    """Extract frames from video"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Cannot open video {video_path}")
        return False
    
    frame_count = 0
    saved_count = 0
    
    # Get video FPS
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Video FPS: {video_fps}")
    
    # Calculate frame interval if fps is specified
    if fps:
        frame_interval = int(video_fps / fps)
    else:
        frame_interval = 1
    
    print(f"Extracting every {frame_interval} frame(s)...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % frame_interval == 0:
            frame_num = saved_count + 1
            output_path = os.path.join(output_dir, f"frame_{frame_num:05d}.png")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            
            if saved_count % 10 == 0:
                print(f"Extracted {saved_count} frames...")
    
    cap.release()
    print(f"Done! Extracted {saved_count} frames from {frame_count} total frames")
    return True


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python extract_frames.py <video_path> <output_dir> [fps]")
        sys.exit(1)
    
    video_path = sys.argv[1]
    output_dir = sys.argv[2]
    fps = int(sys.argv[3]) if len(sys.argv) > 3 else None
    
    extract_frames(video_path, output_dir, fps)

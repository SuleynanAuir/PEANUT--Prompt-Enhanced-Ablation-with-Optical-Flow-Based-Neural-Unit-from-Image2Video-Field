# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import os
import glob

import cv2
import mmcv
import numpy as np
import torch
from tqdm import tqdm

from mmedit.apis import init_model, restoration_video_inference
from mmedit.core import tensor2img
from mmedit.utils import modify_args

VIDEO_EXTENSIONS = ('.mp4', '.mov')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.tif')


def parse_args():
    modify_args()
    parser = argparse.ArgumentParser(description='Restoration demo')
    parser.add_argument('config', help='test config file path')
    parser.add_argument('checkpoint', help='checkpoint file')
    parser.add_argument('input_dir', help='directory of the input video')
    parser.add_argument('output_dir', help='directory of the output video')
    parser.add_argument(
        '--start-idx',
        type=int,
        default=0,
        help='index corresponds to the first frame of the sequence')
    parser.add_argument(
        '--filename-tmpl',
        default='{:08d}.png',
        help='template of the file names')
    parser.add_argument(
        '--window-size',
        type=int,
        default=0,
        help='window size if sliding-window framework is used')
    parser.add_argument(
        '--max-seq-len',
        type=int,
        default=None,
        help='maximum sequence length if recurrent framework is used. '
             'Auto-set to 10 for CUDA to avoid OOM')
    parser.add_argument('--device', type=str, default='cuda:0', 
                        help='Device to use (e.g., "cuda:0" or "cpu")')
    parser.add_argument('--fps', type=int, default=30,
                        help='Frame rate for output video (default: 30)')
    parser.add_argument('--save-video', action='store_true',
                        help='Also save output as video file')
    args = parser.parse_args()
    
    # Auto-set max_seq_len for CUDA to avoid OOM
    if args.max_seq_len is None and args.device != 'cpu' and not args.device.startswith('cpu'):
        args.max_seq_len = 10  # Process 10 frames at a time for CUDA (conservative for 8GB GPU)
        print(f"Auto-setting max_seq_len to {args.max_seq_len} to avoid CUDA OOM")
    
    return args


def main():
    """ Demo for video restoration models.

    Note that we accept video as input/output, when 'input_dir'/'output_dir'
    is set to the path to the video. But using videos introduces video
    compression, which lowers the visual quality. If you want actual quality,
    please save them as separate images (.png).
    """

    args = parse_args()
    
    # Set CUDA memory management environment variable
    os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'expandable_segments:True'

    # Parse device string
    if args.device.startswith('cuda'):
        device = torch.device(args.device)
    elif args.device == 'cpu':
        device = torch.device('cpu')
    else:
        # Assume it's a CUDA device ID
        device = torch.device('cuda', int(args.device))

    # Auto-detect image files and adjust parameters
    if os.path.isdir(args.input_dir):
        # Get all image files in the directory (case-insensitive)
        image_files = []
        for ext in IMAGE_EXTENSIONS:
            # Use case-insensitive glob
            pattern = os.path.join(args.input_dir, f'*{ext}')
            image_files.extend(glob.glob(pattern))
        
        # Remove duplicates (in case file system is case-insensitive like Windows)
        image_files = list(set(image_files))
        
        if image_files:
            # Sort files by name
            image_files.sort()
            print(f"Found {len(image_files)} images in {args.input_dir}")
            
            # Detect filename pattern
            first_file = os.path.basename(image_files[0])
            file_ext = os.path.splitext(first_file)[1]
            
            # Try to detect numeric pattern
            import re
            # Match patterns like: 00000000.png, frame_0001.png, img001.jpg, etc.
            match = re.search(r'(\d+)', first_file)
            if match:
                # Get the number of digits
                num_str = match.group(1)
                num_digits = len(num_str)
                start_num = int(num_str)
                
                # Determine the template
                prefix = first_file[:match.start()]
                suffix = first_file[match.end():]
                args.filename_tmpl = f'{prefix}{{:0{num_digits}d}}{suffix}'
                args.start_idx = start_num
                
                print(f"Detected filename template: {args.filename_tmpl}")
                print(f"Starting index: {args.start_idx}")
            else:
                # No numeric pattern, use default
                print(f"Warning: Could not detect numeric pattern in filename '{first_file}'")
                print(f"Using default template: {args.filename_tmpl}")

    # Set CUDA memory optimization
    if device.type == 'cuda':
        torch.cuda.empty_cache()
        print(f"CUDA device: {torch.cuda.get_device_name(device)}")
        print(f"Total memory: {torch.cuda.get_device_properties(device).total_memory / 1024**3:.2f} GB")

    model = init_model(args.config, args.checkpoint, device=device)
    
    # Clear cache after model loading
    if device.type == 'cuda':
        torch.cuda.empty_cache()
        print(f"Memory allocated after model loading: {torch.cuda.memory_allocated(device) / 1024**3:.2f} GB")

    output = restoration_video_inference(model, args.input_dir,
                                         args.window_size, args.start_idx,
                                         args.filename_tmpl, args.max_seq_len)
    
    # Clear cache after inference
    if device.type == 'cuda':
        torch.cuda.empty_cache()

    file_extension = os.path.splitext(args.output_dir)[1]
    if file_extension in VIDEO_EXTENSIONS:  # save as video
        h, w = output.shape[-2:]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video_writer = cv2.VideoWriter(args.output_dir, fourcc, args.fps, (w, h))
        print(f"Saving {output.size(1)} frames to video...")
        for i in tqdm(range(0, output.size(1)), desc="Writing video"):
            img = tensor2img(output[:, i, :, :, :])
            video_writer.write(img.astype(np.uint8))
        cv2.destroyAllWindows()
        video_writer.release()
        print(f"Video saved to {args.output_dir}")
    else:
        os.makedirs(args.output_dir, exist_ok=True)
        print(f"Saving {output.size(1)} frames to {args.output_dir}...")
        for i in tqdm(range(args.start_idx, args.start_idx + output.size(1)), desc="Saving frames"):
            output_i = output[:, i - args.start_idx, :, :, :]
            output_i = tensor2img(output_i)
            save_path_i = f'{args.output_dir}/{args.filename_tmpl.format(i)}'
            mmcv.imwrite(output_i, save_path_i)
        print(f"Done! Results saved to {args.output_dir}")
        
        # Also save as video if requested
        if args.save_video:
            h, w = output.shape[-2:]
            video_name = os.path.basename(args.input_dir) + '_output.mp4'
            video_path = os.path.join('results', video_name)
            os.makedirs('results', exist_ok=True)
            
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(video_path, fourcc, args.fps, (w, h))
            print(f"Creating video at {args.fps} fps...")
            for i in tqdm(range(0, output.size(1)), desc="Writing video"):
                img = tensor2img(output[:, i, :, :, :])
                video_writer.write(img.astype(np.uint8))
            cv2.destroyAllWindows()
            video_writer.release()
            print(f"Video saved to {video_path}")


if __name__ == '__main__':
    main()

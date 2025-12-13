'''
Inference code for SAMWISE, on Ref-Youtube-VOS
Modified from DETR (https://github.com/facebookresearch/detr)
'''
import argparse
import random
import time
from pathlib import Path
import numpy as np
import torch
import util.misc as utils
import os
from PIL import Image
import torch.nn.functional as F
import json
from tqdm import tqdm
import sys
import subprocess
from pycocotools import mask as cocomask
from tools.colormap import colormap
import opts
from models.samwise import build_samwise
from util.misc import on_load_checkpoint
from tools.metrics import db_eval_boundary, db_eval_iou
from datasets.transform_utils import VideoEvalDataset
from torch.utils.data import DataLoader
from os.path import join
from datasets.transform_utils import vis_add_mask
from imageio_ffmpeg import get_ffmpeg_exe


# colormap
color_list = colormap()
color_list = color_list.astype('uint8').tolist()


def main(args):    
    # fix the seed for reproducibility
    seed = 0
    #utils.init_distributed_mode(args)
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    # save path
    input_path = args.input_path
    save_path_prefix = os.path.join('demo_output')
    os.makedirs(save_path_prefix, exist_ok=True)

    start_time = time.time()
    # model
    model = build_samwise(args)
    device = torch.device(args.device)
    model.to(device)

    if args.resume:
        checkpoint = torch.load(args.resume, map_location='cpu')
        if list(checkpoint['model'].keys())[0].startswith('module'):
            checkpoint['model'] = {k.replace('module.', ''): v for k, v in checkpoint['model'].items()}        
        checkpoint = on_load_checkpoint(model, checkpoint)
        model.load_state_dict(checkpoint['model'], strict=False)

    print('Start inference')
    inference(args, model, save_path_prefix, input_path, args.text_prompts, args.fps)

    end_time = time.time()
    total_time = end_time - start_time
    print("Total inference time: %.4f s" %(total_time))


def extract_frames_from_mp4(video_path, fps=10):
    extract_folder = 'frames_' + os.path.basename(video_path).split('.')[0]
    print(f'Extracting frames from .mp4 in {extract_folder} at {fps}fps with ffmpeg...')
    
    # 检查文件夹是否存在且包含帧
    needs_extraction = True
    if os.path.isdir(extract_folder):
        existing_frames = [f for f in os.listdir(extract_folder) if f.endswith('.png')]
        if existing_frames:
            print(f'{extract_folder} already exists with {len(existing_frames)} frames, using existing frames')
            needs_extraction = False
        else:
            print(f'{extract_folder} exists but is empty, re-extracting frames')
    
    if needs_extraction:
        os.makedirs(extract_folder, exist_ok=True)
        ffmpeg_bin = get_ffmpeg_exe()
        out_pattern = os.path.join(extract_folder, 'frame_%05d.png')
        
        # Use fps parameter for frame extraction rate
        cmd = [ffmpeg_bin, '-i', video_path, '-loglevel', 'error', '-vf', f'fps={fps}', out_pattern]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print('Something went wrong extracting frames with ffmpeg')
            if result.stderr:
                print(f'Error: {result.stderr}')
            sys.exit(result.returncode)
    
    frames_list=os.listdir(extract_folder)
    frames_list = sorted([os.path.splitext(frame)[0] for frame in frames_list if frame.endswith('.png')])

    return extract_folder, frames_list, '.png'


def compute_masks(model, text_prompt, frames_folder, frames_list, ext):
    all_pred_masks = []
    vd = VideoEvalDataset(frames_folder, frames_list, ext=ext)
    # Use a separate chunk size to control memory even if eval_clip_window is large
    chunk_size = getattr(args, "chunk_size", args.eval_clip_window)
    dl = DataLoader(vd, batch_size=chunk_size, num_workers=args.num_workers, shuffle=False)
    origin_w, origin_h = vd.origin_w, vd.origin_h
    # 3. for each clip
    for imgs, clip_frames_ids in tqdm(dl):
        clip_frames_ids = clip_frames_ids.tolist()
        imgs = imgs.to(args.device)  # [eval_clip_window, 3, h, w]
        img_h, img_w = imgs.shape[-2:]
        size = torch.as_tensor([int(img_h), int(img_w)]).to(args.device)
        target = {"size": size, 'frame_ids': clip_frames_ids}

        with torch.no_grad():
            outputs = model([imgs], [text_prompt], [target])

        pred_masks = outputs["pred_masks"]  # [t, q, h, w]
        pred_masks = pred_masks.unsqueeze(0)
        pred_masks = F.interpolate(pred_masks, size=(origin_h, origin_w), mode='bilinear', align_corners=False) 
        pred_masks = (pred_masks.sigmoid() > args.threshold)[0].cpu() 
        all_pred_masks.append(pred_masks)

    # store the video results
    all_pred_masks = torch.cat(all_pred_masks, dim=0).numpy()  # (video_len, h, w)

    return all_pred_masks

    
def inference(args, model, save_path_prefix, in_path, text_prompts, fps=10):
    # load data
    if os.path.isfile(in_path) and not args.image_level:
        frames_folder, frames_list, ext = extract_frames_from_mp4(in_path, fps)
    elif os.path.isfile(in_path) and args.image_level:
        fname, ext = os.path.splitext(in_path)
        frames_list = [os.path.basename(fname)]
        frames_folder = os.path.dirname(in_path)
    else:
        frames_folder = in_path
        frames_list = sorted(os.listdir(frames_folder))
        ext = os.path.splitext(frames_list[0])[1]
        frames_list = [os.path.splitext(frame)[0] for frame in frames_list if os.path.splitext(frame)[1] == ext]
        
    model.eval()
    print(f'Begin inference on {len(frames_list)} frames')
    # For each expression
    for i in range(len(text_prompts)):
        text_prompt = text_prompts[i]

        all_pred_masks = compute_masks(model, text_prompt, frames_folder, frames_list, ext)
            
        save_visualize_path_dir = join(save_path_prefix, text_prompt.replace(' ', '_'))
        os.makedirs(save_visualize_path_dir, exist_ok=True)
        
        # 创建二值掩码文件夹
        save_binary_mask_dir = join(save_path_prefix, text_prompt.replace(' ', '_') + '_binary_masks')
        os.makedirs(save_binary_mask_dir, exist_ok=True)
        
        print(f'Saving output to disk in {save_visualize_path_dir}')
        out_files_w_mask = []
        out_files_binary = []
        for t, frame in enumerate(frames_list):
            # original
            img_path = join(frames_folder, frame + ext)
            source_img = Image.open(img_path).convert('RGBA') # PIL image

            # draw mask
            source_img = vis_add_mask(source_img, all_pred_masks[t], color_list[i%len(color_list)])
            # save
            save_visualize_path = join(save_visualize_path_dir, frame + '.png')
            source_img.save(save_visualize_path)
            out_files_w_mask.append(save_visualize_path)
            
            # 保存二值掩码（黑白图）。为避免某些 MoviePy 版本不支持单通道，保存为三通道 RGB
            binary_mask = (all_pred_masks[t] * 255).astype(np.uint8)  # True->255(白色), False->0(黑色)
            rgb_mask = np.stack([binary_mask, binary_mask, binary_mask], axis=-1)  # (H,W,3)
            binary_mask_img = Image.fromarray(rgb_mask, mode='RGB')
            save_binary_mask_path = join(save_binary_mask_dir, frame + '_mask.png')
            binary_mask_img.save(save_binary_mask_path)
            out_files_binary.append(save_binary_mask_path)
        
        if not args.image_level:
            # Create the video clip from images
            try:
                from moviepy.editor import ImageSequenceClip
            except Exception:
                # fallback for environments packaging moviepy differently
                from moviepy import ImageSequenceClip
            clip = ImageSequenceClip(out_files_w_mask, fps=10)
            # Write the video file
            clip.write_videofile(join(save_path_prefix, text_prompt.replace(' ', '_')+'.mp4'), codec='libx264')

            # 生成二值掩码视频
            try:
                bin_clip = ImageSequenceClip(out_files_binary, fps=10)
                bin_video_path = join(save_path_prefix, text_prompt.replace(' ', '_') + '_mask.mp4')
                bin_clip.write_videofile(bin_video_path, codec='libx264', audio=False)
                print(f'Mask-only video ready at {bin_video_path}')
            except Exception as e:
                print(f'Failed to create binary mask video: {e}')

    print(f'Output masks and videos can be found in {save_path_prefix}')
    print(f'Binary masks (black/white) saved in folders ending with "_binary_masks"')
    print(f'Binary mask-only videos saved as <prompt>_mask.mp4')
    return 


def check_args(args):
    assert os.path.isfile(args.input_path) or os.path.isdir(args.input_path), f'The provided path {args.input_path} does not exist'
    args.image_level = False
    if os.path.isfile(args.input_path):
        ext = os.path.splitext(args.input_path)[1]
        assert ext in ['.jpg', '.png', '.mp4', '.jpeg'], f"Provided file extension should be one of ['.jpg', '.png', '.mp4']"
        if ext in ['.jpg', '.png', '.jpeg']: 
            args.image_level = True
            pretrained_model = 'pretrain/pretrained_model.pth'
            pretrained_model_link = 'https://drive.google.com/file/d/1gRGzARDjIisZ3PnCW77Y9TMM_SbV8aaa/view?usp=drive_link'
            print(f'Specified path is an image, using image-level configuration')

    if not args.image_level: # it's video inference
        # set default args
        args.HSA = True
        args.use_cme_head = False
        pretrained_model = 'pretrain/final_model_mevis.pth'
        pretrained_model_link = 'https://drive.google.com/file/d/1Molt2up2bP41ekeczXWQU-LWTskKJOV2/view?usp=sharing'
        print(f'Specified path is a video or folder with frames, using video-level configuration')
        
    if args.resume == '':
        args.resume = pretrained_model

    assert os.path.isfile(args.resume), f"You should download the model checkpoint first. Run 'cd pretrain &&  gdown --fuzzy {pretrained_model_link}"

    # Default chunk size follows eval_clip_window unless explicitly set smaller to save memory
    if not hasattr(args, 'chunk_size') or args.chunk_size is None:
        args.chunk_size = args.eval_clip_window


if __name__ == '__main__':
    if torch.cuda.get_device_properties(0).major >= 8:
        # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True

    parser = argparse.ArgumentParser('SAMWISE evaluation script', parents=[opts.get_args_parser()])
    parser.add_argument('--input_path', default=None, type=str, required=True, help='path to mp4 video or frames folder')
    parser.add_argument('--text_prompts', default=[''], type=str, required=True, nargs='+', help="List of referring expressions, separated by whitespace")
    parser.add_argument('--chunk_size', default=None, type=int, help='Override mini-batch size to reduce memory usage (default: eval_clip_window)')

    args = parser.parse_args()
    check_args(args)
    main(args)

# Copyright (c) OpenMMLab. All rights reserved.
import glob
import os.path as osp
import re
from functools import reduce

import mmcv
import numpy as np
import torch
from tqdm import tqdm

from mmedit.datasets.pipelines import Compose

VIDEO_EXTENSIONS = ('.mp4', '.mov')


def pad_sequence(data, window_size):
    padding = window_size // 2

    data = torch.cat([
        data[:, 1 + padding:1 + 2 * padding].flip(1), data,
        data[:, -1 - 2 * padding:-1 - padding].flip(1)
    ],
                     dim=1)

    return data


def restoration_video_inference(model,
                                img_dir,
                                window_size,
                                start_idx,
                                filename_tmpl,
                                max_seq_len=None):
    """Inference image with the model.

    Args:
        model (nn.Module): The loaded model.
        img_dir (str): Directory of the input video.
        window_size (int): The window size used in sliding-window framework.
            This value should be set according to the settings of the network.
            A value smaller than 0 means using recurrent framework.
        start_idx (int): The index corresponds to the first frame in the
            sequence.
        filename_tmpl (str): Template for file name.
        max_seq_len (int | None): The maximum sequence length that the model
            processes. If the sequence length is larger than this number,
            the sequence is split into multiple segments. If it is None,
            the entire sequence is processed at once.

    Returns:
        Tensor: The predicted restoration result.
    """

    device = next(model.parameters()).device  # model device

    # build the data pipeline
    if model.cfg.get('demo_pipeline', None):
        test_pipeline = model.cfg.demo_pipeline
    elif model.cfg.get('test_pipeline', None):
        test_pipeline = model.cfg.test_pipeline
    else:
        test_pipeline = model.cfg.val_pipeline

    # check if the input is a video
    file_extension = osp.splitext(img_dir)[1]
    if file_extension in VIDEO_EXTENSIONS:
        video_reader = mmcv.VideoReader(img_dir)
        # load the images
        data = dict(lq=[], lq_path=None, key=img_dir)
        for frame in video_reader:
            data['lq'].append(np.flip(frame, axis=2))

        # remove the data loading pipeline
        tmp_pipeline = []
        for pipeline in test_pipeline:
            if pipeline['type'] not in [
                    'GenerateSegmentIndices', 'LoadImageFromFileList'
            ]:
                tmp_pipeline.append(pipeline)
        test_pipeline = tmp_pipeline
    else:
        # the first element in the pipeline must be 'GenerateSegmentIndices'
        if test_pipeline[0]['type'] != 'GenerateSegmentIndices':
            raise TypeError('The first element in the pipeline must be '
                            f'"GenerateSegmentIndices", but got '
                            f'"{test_pipeline[0]["type"]}".')

        # specify start_idx and filename_tmpl
        test_pipeline[0]['start_idx'] = start_idx
        test_pipeline[0]['filename_tmpl'] = filename_tmpl

        # prepare data
        sequence_length = len(glob.glob(osp.join(img_dir, '*')))
        
        # Use dirname to get parent directory (handles Windows paths correctly)
        key = osp.basename(img_dir)
        lq_folder = osp.dirname(img_dir)
        
        # Debug: print the paths being used
        print(f"DEBUG - img_dir: {img_dir}")
        print(f"DEBUG - lq_folder: {lq_folder}")
        print(f"DEBUG - key: {key}")
        print(f"DEBUG - sequence_length: {sequence_length}")
            
        data = dict(
            lq_path=lq_folder,
            gt_path='',
            key=key,
            sequence_length=sequence_length)

    # compose the pipeline
    test_pipeline = Compose(test_pipeline)
    data = test_pipeline(data)

    # Robust shape handling: ensure 5D (n, t, c, h, w)
    lq = data['lq']
    if isinstance(lq, torch.Tensor):
        # Print debug shape information
        try:
            print(f"DEBUG - lq tensor shape before fix: {tuple(lq.shape)}")
        except Exception:
            pass

        if lq.dim() == 5:
            data = lq  # already (n, t, c, h, w)
        elif lq.dim() == 4:
            # (t, c, h, w) -> (n=1, t, c, h, w)
            data = lq.unsqueeze(0)
        elif lq.dim() == 3:
            # (c, h, w) -> (n=1, t=1, c, h, w)
            data = lq.unsqueeze(0).unsqueeze(0)
        else:
            raise ValueError(f"Unexpected lq tensor dims: {lq.dim()} (expected 3/4/5)")
    else:
        raise TypeError("Pipeline output 'lq' is not a torch.Tensor; check demo/test pipeline for FramesToTensor")

    # forward the model
    with torch.no_grad():
        if window_size > 0:  # sliding window framework
            data = pad_sequence(data, window_size)
            result = []
            total_frames = data.size(1) - 2 * (window_size // 2)
            print(f"Processing {total_frames} frames with sliding window (window_size={window_size})...")
            for i in tqdm(range(total_frames), desc="Processing frames"):
                data_i = data[:, i:i + window_size].to(device)
                result.append(model(lq=data_i, test_mode=True)['output'].cpu())
            result = torch.stack(result, dim=1)
        else:  # recurrent framework
            if max_seq_len is None:
                print(f"Processing {data.size(1)} frames in one pass...")
                result = model(
                    lq=data.to(device), test_mode=True)['output'].cpu()
            else:
                result = []
                num_segments = (data.size(1) + max_seq_len - 1) // max_seq_len
                print(f"Processing {data.size(1)} frames in {num_segments} segments (max_seq_len={max_seq_len})...")
                for i in tqdm(range(0, data.size(1), max_seq_len), desc="Processing segments", total=num_segments):
                    result.append(
                        model(
                            lq=data[:, i:i + max_seq_len].to(device),
                            test_mode=True)['output'].cpu())
                    # Clear CUDA cache after each segment
                    if device.type == 'cuda':
                        torch.cuda.empty_cache()
                result = torch.cat(result, dim=1)
    return result

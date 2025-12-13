#!/usr/bin/env python

import getopt
import math
import numpy
import PIL
import PIL.Image
import sys
import torch

##########################################################

torch.set_grad_enabled(False) # make sure to not compute gradients for computational performance

torch.backends.cudnn.enabled = True # make sure to use cudnn for computational performance

##########################################################

args_strModel = 'sintel-final' # 'sintel-final', or 'sintel-clean', or 'chairs-final', or 'chairs-clean', or 'kitti-final'
args_strOne = './images/one.png'
args_strTwo = './images/two.png'
args_strOut = './out.flo'
args_strFramesPackage = None
args_strOutputDir = None

for strOption, strArg in getopt.getopt(sys.argv[1:], '', [
    'model=',
    'one=',
    'two=',
    'out=',
    'frames-package=',
    'output-dir=',
])[0]:
    if strOption == '--model' and strArg != '': args_strModel = strArg # which model to use, see below
    if strOption == '--one' and strArg != '': args_strOne = strArg # path to the first frame
    if strOption == '--two' and strArg != '': args_strTwo = strArg # path to the second frame
    if strOption == '--out' and strArg != '': args_strOut = strArg # path to where the output should be stored
    if strOption == '--frames-package' and strArg != '': args_strFramesPackage = strArg # path to frames package
    if strOption == '--output-dir' and strArg != '': args_strOutputDir = strArg # output directory for results
# end

##########################################################

backwarp_tenGrid = {}

def backwarp(tenInput, tenFlow):
    if str(tenFlow.shape) not in backwarp_tenGrid:
        tenHor = torch.linspace(-1.0, 1.0, tenFlow.shape[3]).view(1, 1, 1, -1).repeat(1, 1, tenFlow.shape[2], 1)
        tenVer = torch.linspace(-1.0, 1.0, tenFlow.shape[2]).view(1, 1, -1, 1).repeat(1, 1, 1, tenFlow.shape[3])

        backwarp_tenGrid[str(tenFlow.shape)] = torch.cat([ tenHor, tenVer ], 1).to(tenFlow.device)
    # end

    tenFlow = torch.cat([ tenFlow[:, 0:1, :, :] * (2.0 / (tenInput.shape[3] - 1.0)), tenFlow[:, 1:2, :, :] * (2.0 / (tenInput.shape[2] - 1.0)) ], 1)

    return torch.nn.functional.grid_sample(input=tenInput, grid=(backwarp_tenGrid[str(tenFlow.shape)] + tenFlow).permute(0, 2, 3, 1), mode='bilinear', padding_mode='border', align_corners=True)
# end

##########################################################

class Network(torch.nn.Module):
    def __init__(self):
        super().__init__()

        class Preprocess(torch.nn.Module):
            def __init__(self):
                super().__init__()
            # end

            def forward(self, tenInput):
                tenInput = tenInput.flip([1])
                tenInput = tenInput - torch.tensor(data=[0.485, 0.456, 0.406], dtype=tenInput.dtype, device=tenInput.device).view(1, 3, 1, 1)
                tenInput = tenInput * torch.tensor(data=[1.0 / 0.229, 1.0 / 0.224, 1.0 / 0.225], dtype=tenInput.dtype, device=tenInput.device).view(1, 3, 1, 1)

                return tenInput
            # end
        # end

        class Basic(torch.nn.Module):
            def __init__(self, intLevel):
                super().__init__()

                self.netBasic = torch.nn.Sequential(
                    torch.nn.Conv2d(in_channels=8, out_channels=32, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=32, out_channels=64, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=64, out_channels=32, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=32, out_channels=16, kernel_size=7, stride=1, padding=3),
                    torch.nn.ReLU(inplace=False),
                    torch.nn.Conv2d(in_channels=16, out_channels=2, kernel_size=7, stride=1, padding=3)
                )
            # end

            def forward(self, tenInput):
                return self.netBasic(tenInput)
            # end
        # end

        self.netPreprocess = Preprocess()

        self.netBasic = torch.nn.ModuleList([ Basic(intLevel) for intLevel in range(6) ])

        self.load_state_dict({ strKey.replace('module', 'net'): tenWeight for strKey, tenWeight in torch.hub.load_state_dict_from_url(url='http://content.sniklaus.com/github/pytorch-spynet/network-' + args_strModel + '.pytorch', file_name='spynet-' + args_strModel).items() })
    # end

    def forward(self, tenOne, tenTwo):
        tenFlow = []

        tenOne = [ self.netPreprocess(tenOne) ]
        tenTwo = [ self.netPreprocess(tenTwo) ]

        for intLevel in range(5):
            if tenOne[0].shape[2] > 32 or tenOne[0].shape[3] > 32:
                tenOne.insert(0, torch.nn.functional.avg_pool2d(input=tenOne[0], kernel_size=2, stride=2, count_include_pad=False))
                tenTwo.insert(0, torch.nn.functional.avg_pool2d(input=tenTwo[0], kernel_size=2, stride=2, count_include_pad=False))
            # end
        # end

        tenFlow = tenOne[0].new_zeros([ tenOne[0].shape[0], 2, int(math.floor(tenOne[0].shape[2] / 2.0)), int(math.floor(tenOne[0].shape[3] / 2.0)) ])

        for intLevel in range(len(tenOne)):
            tenUpsampled = torch.nn.functional.interpolate(input=tenFlow, scale_factor=2, mode='bilinear', align_corners=True) * 2.0

            if tenUpsampled.shape[2] != tenOne[intLevel].shape[2]: tenUpsampled = torch.nn.functional.pad(input=tenUpsampled, pad=[ 0, 0, 0, 1 ], mode='replicate')
            if tenUpsampled.shape[3] != tenOne[intLevel].shape[3]: tenUpsampled = torch.nn.functional.pad(input=tenUpsampled, pad=[ 0, 1, 0, 0 ], mode='replicate')

            tenFlow = self.netBasic[intLevel](torch.cat([ tenOne[intLevel], backwarp(tenInput=tenTwo[intLevel], tenFlow=tenUpsampled), tenUpsampled ], 1)) + tenUpsampled
        # end

        return tenFlow
    # end
# end

netNetwork = None

##########################################################

def estimate(tenOne, tenTwo):
    global netNetwork

    if netNetwork is None:
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        netNetwork = Network().to(device).train(False)
    # end

    assert(tenOne.shape[1] == tenTwo.shape[1])
    assert(tenOne.shape[2] == tenTwo.shape[2])

    intWidth = tenOne.shape[2]
    intHeight = tenOne.shape[1]

    # Note: Model is trained for 1024x416, but can work with other sizes
    # Uncomment the assertions below if you want to enforce the trained size
    # assert(intWidth == 1024)
    # assert(intHeight == 416)

    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    tenPreprocessedOne = tenOne.to(device).view(1, 3, intHeight, intWidth)
    tenPreprocessedTwo = tenTwo.to(device).view(1, 3, intHeight, intWidth)

    intPreprocessedWidth = int(math.floor(math.ceil(intWidth / 32.0) * 32.0))
    intPreprocessedHeight = int(math.floor(math.ceil(intHeight / 32.0) * 32.0))

    tenPreprocessedOne = torch.nn.functional.interpolate(input=tenPreprocessedOne, size=(intPreprocessedHeight, intPreprocessedWidth), mode='bilinear', align_corners=False)
    tenPreprocessedTwo = torch.nn.functional.interpolate(input=tenPreprocessedTwo, size=(intPreprocessedHeight, intPreprocessedWidth), mode='bilinear', align_corners=False)

    tenFlow = torch.nn.functional.interpolate(input=netNetwork(tenPreprocessedOne, tenPreprocessedTwo), size=(intHeight, intWidth), mode='bilinear', align_corners=False)

    tenFlow[:, 0, :, :] *= float(intWidth) / float(intPreprocessedWidth)
    tenFlow[:, 1, :, :] *= float(intHeight) / float(intPreprocessedHeight)

    return tenFlow[0, :, :, :].cpu()
# end

##########################################################

if __name__ == '__main__':
    # 创建输出目录
    import os
    if args_strOutputDir is not None:
        os.makedirs(args_strOutputDir, exist_ok=True)
        output_prefix = os.path.join(args_strOutputDir, os.path.basename(args_strOut))
    else:
        output_prefix = args_strOut
    
    if args_strFramesPackage is not None:
        # Load from frames package (can be a folder, pickle file, or numpy file)
        import pickle
        import os
        from pathlib import Path
        
        frames_package = None
        
        # Check if it's a directory
        if os.path.isdir(args_strFramesPackage):
            # Load all image files from the directory
            frames_list = []
            image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
            
            # Get all image files sorted by name
            image_files = []
            for ext in image_extensions:
                image_files.extend(sorted(Path(args_strFramesPackage).glob(f'*{ext}')))
                image_files.extend(sorted(Path(args_strFramesPackage).glob(f'*{ext.upper()}')))
            
            # Remove duplicates and sort
            image_files = sorted(set(image_files))
            
            if not image_files:
                print(f"ERROR: No image files found in directory: {args_strFramesPackage}")
                sys.exit(1)
            
            print(f"Found {len(image_files)} frames in directory")
            
            for img_path in image_files:
                try:
                    img = PIL.Image.open(img_path)
                    frames_list.append(numpy.array(img))
                    print(f"  Loaded: {img_path.name}")
                except Exception as e:
                    print(f"  WARNING: Failed to load {img_path}: {e}")
            
            frames_package = numpy.array(frames_list)
            print(f"Loaded {len(frames_package)} frames from directory\n")
        
        elif args_strFramesPackage.endswith('.pkl') or args_strFramesPackage.endswith('.pickle'):
            # Load from pickle file
            with open(args_strFramesPackage, 'rb') as f:
                frames_package = pickle.load(f)
            print(f"Loaded {len(frames_package)} frames from pickle file\n")
        
        elif args_strFramesPackage.endswith('.npy'):
            # Load from numpy file
            frames_package = numpy.load(args_strFramesPackage)
            print(f"Loaded {len(frames_package)} frames from numpy file\n")
        
        else:
            print(f"ERROR: Unknown file format or path: {args_strFramesPackage}")
            sys.exit(1)
        
        # 只处理前两帧
        if len(frames_package) < 2:
            print(f"ERROR: Need at least 2 frames, but only got {len(frames_package)}")
            sys.exit(1)
        
        frame_one = frames_package[0]
        frame_two = frames_package[1]
        
        print(f"Processing frames 0 and 1 (out of {len(frames_package)} available frames)...")
        print(f"Frame 1 shape: {frame_one.shape}")
        print(f"Frame 2 shape: {frame_two.shape}\n")
        
        # Ensure frames are RGB
        if len(frame_one.shape) == 2:
            frame_one = numpy.stack([frame_one] * 3, axis=2)
        if len(frame_two.shape) == 2:
            frame_two = numpy.stack([frame_two] * 3, axis=2)
        
        # Convert to tensor
        tenOne = torch.FloatTensor(numpy.ascontiguousarray(frame_one[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenTwo = torch.FloatTensor(numpy.ascontiguousarray(frame_two[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        print(f"Estimating optical flow...")
        tenOutput = estimate(tenOne, tenTwo)

        # Save output
        output_file = output_prefix + '.flo'
        objOutput = open(output_file, 'wb')

        numpy.array([ 80, 73, 69, 72 ], numpy.uint8).tofile(objOutput)
        numpy.array([ tenOutput.shape[2], tenOutput.shape[1] ], numpy.int32).tofile(objOutput)
        numpy.array(tenOutput.numpy(force=True).transpose(1, 2, 0), numpy.float32).tofile(objOutput)

        objOutput.close()
        print(f"✓ Saved optical flow to {output_file}")
    else:
        # Use default two-image mode
        tenOne = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(PIL.Image.open(args_strOne))[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))
        tenTwo = torch.FloatTensor(numpy.ascontiguousarray(numpy.array(PIL.Image.open(args_strTwo))[:, :, ::-1].transpose(2, 0, 1).astype(numpy.float32) * (1.0 / 255.0)))

        tenOutput = estimate(tenOne, tenTwo)

        objOutput = open(output_prefix, 'wb')

        numpy.array([ 80, 73, 69, 72 ], numpy.uint8).tofile(objOutput)
        numpy.array([ tenOutput.shape[2], tenOutput.shape[1] ], numpy.int32).tofile(objOutput)
        numpy.array(tenOutput.numpy(force=True).transpose(1, 2, 0), numpy.float32).tofile(objOutput)

        objOutput.close()
# end
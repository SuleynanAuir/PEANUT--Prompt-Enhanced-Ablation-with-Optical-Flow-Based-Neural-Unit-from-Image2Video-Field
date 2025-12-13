# 使用自己的视频进行对象清除测试

## 概述

✅ **是的！** E2FGVI 项目完全支持使用自己的视频进行对象清除测试。

你需要准备：
1. 原始视频文件（MP4 格式）或视频帧序列
2. 对应的 mask（遮罩）文件，标记要清除的对象

---

## 快速开始

### 方式一：使用 MP4 视频文件

```powershell
conda activate e2fgvi-project
python test.py --model e2fgvi --video 你的视频.mp4 --mask 你的mask文件夹 --ckpt release_model\E2FGVI-CVPR22.pth
```

### 方式二：使用视频帧序列

```powershell
conda activate e2fgvi-project
python test.py --model e2fgvi --video 你的视频帧文件夹 --mask 你的mask文件夹 --ckpt release_model\E2FGVI-CVPR22.pth
```

---

## 详细准备步骤

### 步骤 1: 准备你的视频

**选项 A - 使用 MP4 视频**
- 直接使用你的 `.mp4` 视频文件
- 例如: `my_video.mp4`

**选项 B - 使用视频帧序列**
- 将视频拆分为单独的图片帧
- 文件命名格式: `00000.jpg`, `00001.jpg`, `00002.jpg`, ...
- 存放在一个文件夹中，例如: `my_video_frames/`

**拆分 MP4 为帧的方法（使用 ffmpeg）:**
```powershell
# 安装 ffmpeg (如果还没有)
# 下载: https://ffmpeg.org/download.html

# 拆分视频为帧
ffmpeg -i 你的视频.mp4 -qscale:v 2 output_frames/%05d.jpg
```

### 步骤 2: 创建 Mask（遮罩）

Mask 是用来标记视频中要清除的对象的黑白图像：
- **白色区域 (255)**: 要清除的对象
- **黑色区域 (0)**: 保留的背景

**Mask 文件要求:**
1. 每一帧对应一个 mask 图片
2. 文件命名与视频帧对应: `00000.png`, `00001.png`, `00002.png`, ...
3. 图片格式: PNG 或 JPG
4. 分辨率: 与原视频相同（程序会自动调整）

**创建 Mask 的工具推荐:**

**方法 1: 使用 LabelMe (推荐，免费)**
```powershell
# 安装 labelme
pip install labelme

# 启动标注工具
labelme
```
- 打开视频帧文件夹
- 使用多边形工具圈出要清除的对象
- 导出为二值化 mask

**方法 2: 使用 Photoshop / GIMP**
- 打开每一帧图片
- 使用选择工具选中要清除的区域
- 填充白色，背景保持黑色
- 保存为 PNG

**方法 3: 使用自动分割工具 (SAM - Segment Anything)**
```python
# 使用 Meta 的 SAM 模型自动生成 mask
# GitHub: https://github.com/facebookresearch/segment-anything
```

### 步骤 3: 组织文件结构

推荐的文件结构：

```
my_test/
├── my_video.mp4              # 你的原始视频（方式一）
或
├── my_video_frames/          # 视频帧文件夹（方式二）
│   ├── 00000.jpg
│   ├── 00001.jpg
│   └── ...
└── my_video_mask/            # Mask 文件夹（必需）
    ├── 00000.png
    ├── 00001.png
    └── ...
```

---

## 完整测试命令

### 使用标准模型（推荐，速度快）

```powershell
conda activate e2fgvi-project

# MP4 视频
python test.py --model e2fgvi --video my_test\my_video.mp4 --mask my_test\my_video_mask --ckpt release_model\E2FGVI-CVPR22.pth

# 视频帧序列
python test.py --model e2fgvi --video my_test\my_video_frames --mask my_test\my_video_mask --ckpt release_model\E2FGVI-CVPR22.pth
```

**输出位置**: `results/my_video_results.mp4`

### 使用高质量模型（质量更好，速度慢）

```powershell
conda activate e2fgvi-project

python test.py --model e2fgvi_hq --video my_test\my_video.mp4 --mask my_test\my_video_mask --ckpt release_model\E2FGVI-HQ-CVPR22.pth --set_size --width 1920 --height 1080
```

**参数说明:**
- `--set_size`: 启用自定义分辨率
- `--width 1920`: 输出视频宽度
- `--height 1080`: 输出视频高度

---

## 高级参数调整

### 调整邻域帧步长（影响质量和速度）

```powershell
python test.py --model e2fgvi --video my_video.mp4 --mask my_mask --ckpt release_model\E2FGVI-CVPR22.pth --neighbor_stride 5
```

**参数说明:**
- `--neighbor_stride 5`: 使用前后 5 帧作为参考（默认值）
- 值越大，速度越快，但质量可能下降
- 值越小，质量越好，但速度越慢

### 调整参考帧数量

```powershell
python test.py --model e2fgvi --video my_video.mp4 --mask my_mask --ckpt release_model\E2FGVI-CVPR22.pth --num_ref 10 --step 5
```

**参数说明:**
- `--num_ref 10`: 使用 10 个参考帧（默认 -1 表示自动）
- `--step 5`: 参考帧采样步长

### 调整输出视频帧率

```powershell
python test.py --model e2fgvi --video my_video.mp4 --mask my_mask --ckpt release_model\E2FGVI-CVPR22.pth --savefps 30
```

**参数说明:**
- `--savefps 30`: 输出视频帧率为 30fps（默认 24fps）

---

## 完整示例工作流

### 示例 1: 清除视频中的路人

**场景**: 旅游视频中有路人遮挡，想要清除

```powershell
# 1. 准备文件
# my_travel/
# ├── travel_video.mp4
# └── travel_mask/
#     ├── 00000.png  (手动标注路人位置为白色)
#     ├── 00001.png
#     └── ...

# 2. 激活环境
conda activate e2fgvi-project

# 3. 运行测试
python test.py --model e2fgvi --video my_travel\travel_video.mp4 --mask my_travel\travel_mask --ckpt release_model\E2FGVI-CVPR22.pth

# 4. 查看结果
# 输出在: results/travel_video_results.mp4
```

### 示例 2: 清除视频中的文字水印

**场景**: 视频右下角有固定位置的 logo

```powershell
# 1. 创建 mask (所有帧的 mask 都是相同的矩形白色区域)
# watermark_removal/
# ├── source_video.mp4
# └── logo_mask/
#     ├── 00000.png  (右下角白色矩形，其他黑色)
#     ├── 00001.png  (同样的 mask)
#     └── ...

# 2. 运行
conda activate e2fgvi-project
python test.py --model e2fgvi --video watermark_removal\source_video.mp4 --mask watermark_removal\logo_mask --ckpt release_model\E2FGVI-CVPR22.pth

# 3. 结果: results/source_video_results.mp4
```

### 示例 3: 高分辨率视频处理

**场景**: 处理 4K 或更高分辨率视频

```powershell
# 使用 HQ 模型
conda activate e2fgvi-project
python test.py --model e2fgvi_hq --video my_4k_video.mp4 --mask my_4k_mask --ckpt release_model\E2FGVI-HQ-CVPR22.pth --set_size --width 3840 --height 2160
```

---

## 快速创建简单 Mask 的 Python 脚本

如果你的对象在固定位置（如水印），可以用这个脚本快速生成 mask：

```python
# create_simple_mask.py
import cv2
import numpy as np
import os

def create_fixed_mask(video_path, output_folder, x, y, width, height):
    """
    为固定位置的对象创建 mask
    
    参数:
        video_path: 视频文件路径
        output_folder: mask 输出文件夹
        x, y: 要清除区域的左上角坐标
        width, height: 要清除区域的宽高
    """
    # 读取视频
    cap = cv2.VideoCapture(video_path)
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # 创建输出文件夹
    os.makedirs(output_folder, exist_ok=True)
    
    # 创建 mask 模板（全黑）
    mask_template = np.zeros((frame_height, frame_width), dtype=np.uint8)
    
    # 在指定区域填充白色
    mask_template[y:y+height, x:x+width] = 255
    
    # 为每一帧保存相同的 mask
    for i in range(frame_count):
        mask_path = os.path.join(output_folder, f"{i:05d}.png")
        cv2.imwrite(mask_path, mask_template)
    
    cap.release()
    print(f"创建了 {frame_count} 个 mask 文件在 {output_folder}")

# 使用示例：清除右下角 200x100 的水印
create_fixed_mask(
    video_path="my_video.mp4",
    output_folder="my_mask",
    x=1720,  # 距离左边的距离
    y=980,   # 距离上边的距离
    width=200,
    height=100
)
```

**运行脚本:**
```powershell
conda activate e2fgvi-project
python create_simple_mask.py
```

---

## 故障排查

### 问题 1: Mask 文件数量与视频帧数不匹配

**错误信息**: `IndexError: list index out of range`

**解决方案**:
- 确保 mask 文件夹中的图片数量等于视频帧数
- 使用 `ffmpeg` 检查视频帧数:
  ```powershell
  ffmpeg -i your_video.mp4 -vf "select='eq(n\,0)'" -f null -
  ```

### 问题 2: Mask 区域太大导致显存不足

**错误信息**: `CUDA out of memory`

**解决方案**:
1. 使用标准模型而非 HQ 模型
2. 降低视频分辨率:
   ```powershell
   ffmpeg -i input.mp4 -vf scale=720:-1 output_720p.mp4
   ```

### 问题 3: 输出视频质量不佳

**解决方案**:
1. 调整 `--neighbor_stride` 为更小的值（如 3）
2. 使用 HQ 模型
3. 确保 mask 边缘平滑（使用羽化效果）

---

## 完整命令参数参考

```powershell
python test.py [参数]
```

| 参数 | 必需 | 说明 | 示例 |
|------|------|------|------|
| `-v, --video` | ✅ | 输入视频路径（MP4 或帧文件夹） | `my_video.mp4` |
| `-m, --mask` | ✅ | Mask 文件夹路径 | `my_mask/` |
| `-c, --ckpt` | ✅ | 模型权重路径 | `release_model\E2FGVI-CVPR22.pth` |
| `--model` | ✅ | 模型类型 | `e2fgvi` 或 `e2fgvi_hq` |
| `--step` | ❌ | 参考帧采样步长 | `10` (默认) |
| `--num_ref` | ❌ | 参考帧数量 | `-1` (默认，自动) |
| `--neighbor_stride` | ❌ | 邻域帧步长 | `5` (默认) |
| `--savefps` | ❌ | 输出视频帧率 | `24` (默认) |
| `--set_size` | ❌ | 启用自定义分辨率 | 无值，添加即启用 |
| `--width` | ❌ | 输出宽度（需 `--set_size`） | `1920` |
| `--height` | ❌ | 输出高度（需 `--set_size`） | `1080` |

---

## 总结

✅ **E2FGVI 完全支持自定义视频测试**

**最简流程:**
1. 准备视频（MP4 或帧序列）
2. 创建 mask（标记要清除的对象）
3. 运行命令:
   ```powershell
   conda activate e2fgvi-project
   python test.py --model e2fgvi --video 你的视频 --mask 你的mask --ckpt release_model\E2FGVI-CVPR22.pth
   ```
4. 查看结果: `results/你的视频_results.mp4`

**推荐工作流:**
- 测试阶段: 使用标准模型 (`e2fgvi`)，速度快
- 最终输出: 使用 HQ 模型 (`e2fgvi_hq`)，质量更好

---

**最后更新**: 2025-12-02  
**相关文档**: 参考 `QUICK_START.md` 了解环境配置

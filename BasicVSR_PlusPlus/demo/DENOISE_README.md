# 视频结果去噪工具使用说明

## 功能介绍

这个去噪模块可以对视频超分辨率的结果进行后处理，去除可能存在的噪声，提升视觉质量。

## 支持的去噪方法

1. **nlm** (Non-Local Means) - 非局部均值去噪
   - 质量最好，能很好地保留细节
   - 速度较慢
   - 推荐用于最终输出

2. **bilateral** - 双边滤波
   - 在去噪的同时保持边缘清晰
   - 速度中等
   - 适合有明显边缘的内容

3. **gaussian** - 高斯滤波
   - 简单快速的模糊去噪
   - 速度最快
   - 适合快速预览

4. **median** - 中值滤波
   - 对椒盐噪声效果特别好
   - 速度快
   - 适合特定类型噪声

5. **fast** - 快速去噪
   - 速度快但质量略低于NLM
   - 平衡速度和质量
   - 适合批量处理

## 基本用法

### 1. 简单去噪（使用默认参数）
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised
```

### 2. 指定去噪方法
```bash
# 使用双边滤波
python demo/denoise_results.py results/horse_output results/horse_denoised --method bilateral

# 使用快速去噪
python demo/denoise_results.py results/horse_output results/horse_denoised --method fast
```

### 3. 调整去噪强度
```bash
# 轻度去噪（保留更多细节）
python demo/denoise_results.py results/horse_output results/horse_denoised --strength 3

# 中度去噪（推荐）
python demo/denoise_results.py results/horse_output results/horse_denoised --strength 7

# 强力去噪（去除更多噪声）
python demo/denoise_results.py results/horse_output results/horse_denoised --strength 12
```

### 4. 保留细节模式
```bash
# 在去噪的同时尽可能保留细节
python demo/denoise_results.py results/horse_output results/horse_denoised --preserve-details --strength 5
```

### 5. 同时生成视频
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised --create-video --fps 30
```

## 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `input_dir` | 输入图像序列目录（必需） | - |
| `output_dir` | 输出目录（必需） | - |
| `--method` | 去噪方法 (nlm/bilateral/gaussian/median/fast) | nlm |
| `--strength` | 去噪强度 (1-20) | 5 |
| `--preserve-details` | 保留更多细节 | False |
| `--color-strength` | 彩色去噪强度（仅nlm和fast） | 与strength相同 |
| `--create-video` | 同时创建视频文件 | False |
| `--fps` | 输出视频帧率 | 30 |

## 推荐配置

### 场景1: 轻微噪声，需要保留所有细节
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised \
    --method bilateral \
    --strength 3 \
    --preserve-details
```

### 场景2: 中等噪声，平衡去噪和细节（推荐）
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised \
    --method nlm \
    --strength 5
```

### 场景3: 较多噪声，优先去噪
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised \
    --method nlm \
    --strength 10
```

### 场景4: 快速处理大量数据
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised \
    --method fast \
    --strength 5
```

### 场景5: 完整流程（去噪并生成视频）
```bash
python demo/denoise_results.py results/horse_output results/horse_denoised \
    --method nlm \
    --strength 5 \
    --create-video \
    --fps 30
```

## 强度参数建议

- **1-5**: 轻度去噪，最大程度保留细节，适合高质量输入
- **6-10**: 中度去噪，平衡去噪效果和细节保留（推荐）
- **11-15**: 强力去噪，适合噪声较多的情况
- **16-20**: 极强去噪，可能会损失一些细节

## 处理流程示例

完整的超分+去噪工作流：

```bash
# 1. 运行超分辨率
python demo/restoration_video_demo.py \
    configs/basicvsr_plusplus_reds4.py \
    checkpoints/basicvsr_plusplus_reds4.pth \
    data/horse \
    results/horse_output

# 2. 对结果进行去噪
python demo/denoise_results.py \
    results/horse_output \
    results/horse_denoised \
    --method nlm \
    --strength 5 \
    --create-video
```

## 注意事项

1. 去噪强度越大，处理时间越长
2. NLM方法质量最好但速度最慢，建议先用fast方法测试参数
3. 不同内容可能需要不同的去噪强度，建议先小范围测试
4. `--preserve-details` 参数会使用更保守的去噪策略，适合细节丰富的内容
5. 输入必须是图像序列目录，不支持直接处理视频文件

## 性能参考

处理100帧1920x1080图像的大致时间（Intel i7 + 16GB RAM）：

- **gaussian**: ~5秒
- **median**: ~8秒
- **bilateral**: ~15秒
- **fast**: ~20秒
- **nlm**: ~60秒

实际时间会因硬件配置和图像尺寸而异。

# 🚀 SAMWISE 对比实验 - 快速开始

## 📋 说明

这个对比实验脚本可以在单个运行中自动执行多个参数组合的实验，生成完整的对比报告。

## 🎯 快速运行

### 方式 1: 仅对比阈值 (推荐首次运行)

```powershell
cd C:\Users\Aiur\SuperVideo-inpaint
& "C:\Users\Aiur\miniconda3\shell\condabin\conda-hook.ps1"
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1" -TestMode "threshold"
```

**执行内容**: 运行 3 个阈值对比 (0.3, 0.5, 0.7)  
**预期耗时**: 5-10 分钟  
**输出**: `experiment/exp1/` 目录

---

### 方式 2: 对比模型 (Model Variants)

```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1" -TestMode "model"
```

**执行内容**: 运行 3 个模型对比 (tiny, base, large)  
**预期耗时**: 10-15 分钟  
**注意**: large 模型需要更多显存

---

### 方式 3: 对比时间窗口 (Memory Optimization)

```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1" -TestMode "window"
```

**执行内容**: 运行 3 个窗口对比 (4, 8, 16 帧)  
**预期耗时**: 5-10 分钟

---

### 方式 4: 完整对比 (所有 3 个阶段)

```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1" -TestMode "all"
```

**执行内容**: 运行全部 9 个实验 (3×3 阶段)  
**预期耗时**: 30-45 分钟  
**结果**: 完整的三维对比分析

---

## 📊 输出结构

```
experiment/
└── exp1/
    ├── samwise_results/
    │   ├── threshold_0.3_loose/
    │   │   └── the_alita_binary_masks/  (掩码输出)
    │   ├── threshold_0.5_baseline/
    │   │   └── the_alita_binary_masks/
    │   ├── threshold_0.7_strict/
    │   │   └── the_alita_binary_masks/
    │   ├── model_tiny_fast/
    │   ├── model_base_balanced/
    │   ├── model_large_precise/
    │   ├── window_4_lowmem/
    │   ├── window_8_balanced/
    │   └── window_16_highquality/
    ├── comparison_results.txt           (详细日志)
    └── COMPARISON_SUMMARY.md            (对比报告)
```

---

## 📈 对比指标

| 参数 | 说明 | 影响 |
|------|------|------|
| **Threshold** | 掩码置信度阈值 (0.0-1.0) | ↑提高 = 更严格，↓降低 = 更宽松 |
| **Sam2Version** | SAM2 模型大小 | tiny(快) → base(均衡) → large(精准) |
| **EvalClipWindow** | 处理帧数窗口 | ↓减少 = 快速/低显存，↑增加 = 连贯性好 |

---

## 💡 推荐用法

### Step 1: 快速定位最优阈值
```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1_threshold" -TestMode "threshold"
```
📌 查看 `exp1_threshold/COMPARISON_SUMMARY.md` 选择最佳阈值

### Step 2: 对比模型大小
```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1_model" -TestMode "model"
```
📌 选择速度和精度的平衡点

### Step 3: 优化显存使用
```powershell
.\experiment\samwise_comparison_experiment.ps1 -ExperimentName "exp1_window" -TestMode "window"
```
📌 根据可用显存选择最大窗口大小

---

## 📝 查看结果

### 实时查看对比报告
```powershell
Get-Content C:\Users\Aiur\SuperVideo-inpaint\experiment\exp1\COMPARISON_SUMMARY.md
```

### 查看详细日志
```powershell
Get-Content C:\Users\Aiur\SuperVideo-inpaint\experiment\exp1\comparison_results.txt -Tail 50
```

### 列出所有输出
```powershell
Get-ChildItem -Recurse C:\Users\Aiur\SuperVideo-inpaint\experiment\exp1\samwise_results
```

---

## 🎬 实验案例

### 例 1: Alita 角色分割
```powershell
.\experiment\samwise_comparison_experiment.ps1 `
    -ExperimentName "exp1_alita" `
    -TestMode "threshold" `
    -VideoPath "experiment\exp_raw_video\alita1_test.mp4" `
    -TextPrompt "the alita"
```

### 例 2: 自定义对象 + 自定义名称
```powershell
.\experiment\samwise_comparison_experiment.ps1 `
    -ExperimentName "custom_exp" `
    -TestMode "all" `
    -VideoPath "experiment\exp_raw_video\custom_video.mp4" `
    -TextPrompt "the person wearing red"
```

---

## ⚠️ 故障排除

**问题**: 显存不足 (CUDA OOM)
- 使用 `tiny` 模型替代 `base`
- 降低 `EvalClipWindow` 为 4
- 使用更小的视频进行测试

**问题**: 输出目录为空
- 检查 `comparison_results.txt` 中的错误
- 验证视频文件存在: `experiment\exp_raw_video\alita1_test.mp4`
- 确保 SAMWISE 环境正确激活

**问题**: 速度太慢
- 使用 `TestMode="threshold"` 而不是 `"all"`
- 使用 `tiny` 模型
- 使用更小的视频进行测试

---

## ✨ 下一步

对比实验完成后：

1. ✓ 查看 `COMPARISON_SUMMARY.md` 获取总结
2. ✓ 选择最优参数组合
3. ✓ 应用到主管道:
   ```powershell
   .\video_inpaint_pipeline_en.ps1 -Threshold 0.5 -Sam2Version base -EvalClipWindow 8 -Fps 10
   ```


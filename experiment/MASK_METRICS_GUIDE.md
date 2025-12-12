# Mask 质量评估系统

## 概述

该系统提供了一套完整的 mask 质量量化指标，用于评估 SAMWISE 在不同参数下生成的 mask 质量。系统会在实验进行时自动评估，并生成详细的统计报告。

## 量化指标

### 1. Coverage（覆盖率）
**定义**：前景像素（mask = 1）占总像素的百分比

**含义**：
- 低覆盖率：目标物体检测不充分
- 高覆盖率：可能包含过多噪声或背景
- 理想范围：20-80%（根据具体任务调整）

**用途**：评估 mask 的疏密程度

**指标输出**：
```
"coverage": {
    "mean": 45.2,      # 平均覆盖率
    "std": 5.3,        # 标准差（一致性）
    "min": 38.1,       # 最小值
    "max": 52.7        # 最大值
}
```

### 2. Edge Quality（边界质量）
**定义**：评估 mask 边界的平滑度和精确性

**子指标**：
- **Edge Sharpness**：边缘清晰度（0-1，越高越清晰）
  - 低值：边界模糊、不清晰
  - 高值：边界清晰、干净

- **Perimeter Ratio**：周长比（越低越好）
  - 衡量边界的平滑度
  - 高值表示边界不规则、齿状

**用途**：评估边界检测的质量

**指标输出**：
```
"edge_quality": {
    "edge_sharpness_mean": 0.245,
    "edge_sharpness_std": 0.032,
    "perimeter_ratio_mean": 1.854,
    "perimeter_ratio_std": 0.126
}
```

### 3. Connectivity（连通性）
**定义**：分析 mask 中的连通分量特性

**子指标**：
- **Num Components**：连通分量数量
  - 1：单一完整目标
  - >1：目标被分割或有多个独立部分

- **Largest Ratio**：最大分量占比（0-1）
  - 接近1：单一主要目标
  - 接近0：分散的多个小分量

- **Component Uniformity**：分量均一性（0-1）
  - 高值：各分量大小相近
  - 低值：分量大小差异大

**用途**：评估 mask 的完整性和连续性

**指标输出**：
```
"connectivity": {
    "num_components_mean": 2.3,
    "num_components_max": 5,
    "largest_ratio_mean": 0.87,
    "component_uniformity_mean": 0.72
}
```

### 4. Temporal Stability（时间稳定性）
**定义**：相邻帧间 mask 的一致性

**子指标**：
- **Temporal IoU**：相邻帧 mask 的交并比（0-1）
  - 1.0：完全一致
  - 0.0：完全不同
  - >0.8：优秀的稳定性
  - 0.6-0.8：良好
  - <0.6：需要改进

- **MSE**：均方误差
  - 衡量像素级差异

**用途**：评估 mask 的时间连贯性

**指标输出**：
```
"temporal": {
    "avg_iou": 0.756,
    "avg_mse": 0.032,
    "temporal_consistency": 0.756,
    "frame_count": 200
}
```

### 5. Quality Score（综合质量评分）
**定义**：0-100 的综合评分，综合考虑所有指标

**计算权重**：
- Coverage（25%）：理想范围 20-80%
- Edge Quality（25%）：周长比越低越好
- Connectivity（25%）：分量数少、均一性高为佳
- Temporal Stability（25%）：IoU 越高越好

**解释**：
- 85-100：优秀
- 70-85：良好
- 50-70：中等
- <50：需要改进

## 输出文件

### 1. 单次实验 metrics
**位置**：`experiment/exp1/samwise_results/<video>/<test>/metrics.json`

**内容**：该单次实验的详细指标

```json
{
    "file_count": 200,
    "coverage": {
        "mean": 45.2,
        "std": 5.3,
        ...
    },
    "quality_score": 78.5
}
```

### 2. METRICS_SUMMARY.md
**位置**：`experiment/exp1/METRICS_SUMMARY.md`

**内容**：所有实验的汇总表格

| 格式 | 内容 |
|------|------|
| 简表 | Test Name, Quality Score, Coverage, Temporal IoU, Edge Sharpness, Connectivity |
| 详表 | Coverage Mean±Std, Perimeter Ratio, Largest Component, Uniformity |

### 3. metrics_data.csv
**位置**：`experiment/exp1/metrics_data.csv`

**内容**：所有指标导出为 CSV 格式

**用途**：在 Excel/Pandas 中进行进一步分析

**列**：
- Video
- TestName
- QualityScore
- Coverage_Mean, Coverage_Std
- EdgeSharpness
- PerimeterRatio
- NumComponents
- LargestRatio
- Uniformity
- TemporalIoU
- FrameCount

### 4. DETAILED_COMPARISON.md
**位置**：`experiment/exp1/DETAILED_COMPARISON.md`

**内容**：针对每个视频的详细对比分析

**包含**：
- 最佳/最差测试
- 覆盖率分析
- 时间稳定性排名
- 边界质量对比
- 连通性分析

## 使用方法

### 方式1：集成在实验脚本中（自动）

运行实验时会自动执行：

```powershell
conda activate samwise
Set-Location "C:\Users\Aiur\SuperVideo-inpaint"
.\experiment\samwise_comparison_exp.ps1 -ExperimentName "exp1" -TestMode "all" -ChunkSize 2
```

脚本会自动：
1. 运行 SAMWISE 推理
2. 对每个测试的 mask 进行评估
3. 生成 metrics.json
4. 汇总所有指标生成报告

### 方式2：手动评估单个 mask 目录

```powershell
conda activate e2fgvi-project
cd C:\Users\Aiur\SuperVideo-inpaint

# 评估单个目录的 mask
python experiment\evaluate_masks.py "path\to\mask\directory" "output\metrics.json"

# 或只输出到屏幕
python experiment\evaluate_masks.py "path\to\mask\directory"
```

### 方式3：生成汇总报告

```powershell
# 对整个实验目录生成汇总报告
python experiment\generate_metrics_summary.py experiment\exp1
```

会生成：
- METRICS_SUMMARY.md
- metrics_data.csv
- DETAILED_COMPARISON.md

## 指标解释示例

### 示例1：阈值 0.3 (loose)
```
Quality Score: 68.5 (中等)
Coverage: 52.3%±6.1 (较高，可能包含噪声)
Edge Sharpness: 0.284 (边界较清晰)
Temporal IoU: 0.712 (良好稳定性)
Num Components: 3.2 (可能分散)
```

**解释**：
- 阈值低导致覆盖率高
- 但可能包含更多伪正例
- 稳定性不错
- 但可能分散成多个分量

### 示例2：阈值 0.7 (strict)
```
Quality Score: 75.2 (良好)
Coverage: 38.1%±4.3 (较低，精确度高)
Edge Sharpness: 0.156 (边界清晰)
Temporal IoU: 0.823 (优秀稳定性)
Num Components: 1.1 (高度集中)
```

**解释**：
- 阈值高导致覆盖率低
- 但误检率低，精确度高
- 极佳的时间稳定性
- 目标高度集中

## 性能优化建议

基于指标值，您可以按以下逻辑选择最佳参数：

| 目标 | 推荐参数 |
|------|---------|
| **高精度** | 阈值=0.7, 模型=large, 窗口=16 |
| **均衡** | 阈值=0.5, 模型=base, 窗口=8 |
| **高速度** | 阈值=0.3, 模型=tiny, 窗口=4 |
| **稳定性** | 关注 Temporal IoU，选择>0.75 的配置 |
| **清晰边界** | 关注 Edge Sharpness，选择>0.25 的配置 |

## 常见问题

### Q: Quality Score 很低怎么办？
A: 检查以下几点：
1. Coverage 是否在合理范围（20-80%）
2. Temporal IoU 是否>0.6
3. 是否有过多的连通分量（>5个）
4. 尝试调整阈值参数

### Q: Coverage 很高但 Score 低？
A: 可能原因：
1. 阈值设置过低
2. Edge 质量差（周长比高）
3. 包含过多连通分量
4. 建议提高阈值

### Q: 时间稳定性差？
A: 可能原因：
1. 窗口大小过小
2. 模型不够大
3. 视频内容变化剧烈
4. 建议增加窗口大小或使用更大模型

## 高级用法

### 导出到 Excel 进行进一步分析

```python
import pandas as pd

df = pd.read_csv('experiment/exp1/metrics_data.csv')

# 按质量评分排序
best = df.sort_values('QualityScore', ascending=False)
print(best[['TestName', 'QualityScore', 'TemporalIoU', 'Coverage_Mean']])

# 统计分析
print(df.groupby('Video')[['QualityScore', 'TemporalIoU']].mean())
```

### 绘制对比图表

```python
import matplotlib.pyplot as plt

# 读取数据
df = pd.read_csv('experiment/exp1/metrics_data.csv')

# 按参数分组对比
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

# Threshold comparison
thresh = df[df['TestName'].str.contains('threshold')]
axes[0].plot(thresh['TestName'], thresh['QualityScore'], 'o-')
axes[0].set_title('Threshold Comparison')

# 类似处理 Model 和 Window
```

## 系统要求

- Python 3.7+
- numpy
- PIL (Pillow)
- scipy
- opencv-python (cv2)

所有依赖已在 evaluate_masks.py 中导入

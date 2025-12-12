# 快速启动脚本 - 放置您的视频到 raw_video 文件夹后运行

# 示例 1: 处理 raw_video 中的视频
.\video_inpaint_pipeline.ps1 -VideoPath "your_video.mp4" -TextPrompt "the object"

# 示例 2: 去除胡萝卜 (使用 SAMWISE 自带的测试视频)
.\video_inpaint_pipeline.ps1 -VideoPath "Zoopic.mp4" -TextPrompt "the carrot"

# 示例 3: 快速模式
.\video_inpaint_pipeline.ps1 -VideoPath "test.mp4" -TextPrompt "the person" -NeighborStride 5 -MaxLoadFrames 4

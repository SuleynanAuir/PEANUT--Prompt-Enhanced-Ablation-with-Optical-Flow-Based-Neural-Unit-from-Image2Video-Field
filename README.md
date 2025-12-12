<h1 style="text-align: center; font-size: 1.9em; margin-bottom: 15px;">
    PEANUT: Prompt-Enhanced Ablation with Optical Flow-Based Neural Unit for Spatio-Temporal Consistency & VSR++ Clarity from IMG2Video Field 馃挮 
</h1>

<div style="text-align: center; margin: 30px 0; display: flex; justify-content: center; gap: 20px; flex-wrap: wrap;">
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 8px 16px; border-radius: 20px; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4); font-weight: 500;">
    <span style="margin-right: 8px; font-size: 1.1em;">馃悕</span>
    <span>Python</span>
    <span style="margin-left: 8px; background-color: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 12px; font-weight: 600;">v3.8</span>
  </div>
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 8px 16px; border-radius: 20px; box-shadow: 0 4px 12px rgba(245, 87, 108, 0.4); font-weight: 500;">
    <span style="margin-right: 8px; font-size: 1.1em;">馃敟</span>
    <span>PyTorch</span>
    <span style="margin-left: 8px; background-color: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 12px; font-weight: 600;">v2.6.0+cu124</span>
  </div>
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 8px 16px; border-radius: 20px; box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4); font-weight: 500;">
    <span style="margin-right: 8px; font-size: 1.1em;">鈿?/span>
    <span>CUDA</span>
    <span style="margin-left: 8px; background-color: rgba(255,255,255,0.25); padding: 2px 8px; border-radius: 12px; font-weight: 600;">v12.4</span>
  </div>
</div>

<div style="text-align: center; margin: 15px 0; display: flex; justify-content: center; gap: 15px; flex-wrap: wrap;">
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); color: white; padding: 6px 14px; border-radius: 18px; box-shadow: 0 3px 10px rgba(250, 112, 154, 0.35); font-weight: 500; font-size: 0.9em;">
    <span style="margin-right: 6px;">馃幍</span>
    <span>TorchAudio</span>
    <span style="margin-left: 6px; background-color: rgba(255,255,255,0.25); padding: 1px 6px; border-radius: 10px; font-weight: 600;">v2.6.0+cu124</span>
  </div>
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 6px 14px; border-radius: 18px; box-shadow: 0 3px 10px rgba(168, 237, 234, 0.35); font-weight: 500; font-size: 0.9em;">
    <span style="margin-right: 6px;">馃柤锔?/span>
    <span>TorchVision</span>
    <span style="margin-left: 6px; background-color: rgba(255,255,255,0.4); padding: 1px 6px; border-radius: 10px; font-weight: 600;">v0.21.0+cu124</span>
  </div>
  <div style="display: inline-flex; align-items: center; background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; padding: 6px 14px; border-radius: 18px; box-shadow: 0 3px 10px rgba(252, 182, 159, 0.35); font-weight: 500; font-size: 0.9em;">
    <span style="margin-right: 6px;">馃幀</span>
    <span>imageio-ffmpeg</span>
    <span style="margin-left: 6px; background-color: rgba(255,255,255,0.4); padding: 1px 6px; border-radius: 10px; font-weight: 600;">v0.6.0</span>
  </div>
</div>



<ul style="list-style-type: none; padding-left: 0; margin-top: 15px;">
    <li style="margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #4CAF50; font-size: 1.2em;">馃懁</span> 
        <strong>Collaborators:</strong> Minghao Li (Aiur)
    </li>
    <li style="margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #4CAF50; font-size: 1.2em;">馃彨</span> 
        <strong>Affiliation:</strong> Beijing Normal University and Hong Kong Baptist University (BNBU)
    </li>
    <li style="margin-bottom: 10px; display: flex; align-items: center; gap: 10px;">
        <span style="color: #4CAF50; font-size: 1.2em;">馃摟</span> 
        <strong>Email:</strong> <code>t330034027@mail.uic.edu.cn</code>
    </li>
</ul>

### 馃樁鈥嶐煂笍 See Prompt-Guided Mask Generation in Different Scenarios

<div style="
    text-align: center; /* 灞呬腑鏁翠釜鍖哄潡鐨勫唴瀹?*/
    margin: 30px auto; 
    max-width: 2000px; /* 鎺у埗鏈€澶у搴?*/
    padding: 10px 0;
">
    <h3 style="
        color: #1b5e20; /* 鍖归厤娴佺▼鏉＄殑娣辩豢鑹蹭富棰?*/
        margin-bottom: 5px; /* 鍑忓皯鏍囬鍜屼笅闈㈢殑鍏冪礌涔嬮棿鐨勯棿璺?*/
        font-size: 1.4em;
        font-weight: 800; /* 鏋佽嚧鍔犵矖 */
        display: block; /* 纭繚鏍囬鍗犳嵁瀹屾暣瀹藉害 */
        padding: 5px 15px 5px 15px;
        letter-spacing: 0.5px; 
        text-transform: uppercase;
    ">
        馃幀 P-MASk Module in Different Scenarios
    </h3>
    <div style="display: inline-block; max-width: 100%; margin-top: 10px;">
        <div style="
            border-bottom: 3px solid #4caf50; 
            margin-bottom: 10px; /* 澧炲姞绾垮拰鍥剧墖涔嬮棿鐨勯棿璺?*/
            margin-top: 5px; /* 澧炲姞鏍囬鍜岀嚎涔嬮棿鐨勯棿璺?*/
        "></div>
        <img src="paper/graphs/preview_mask.png" alt="P-MASk Prompt Guided Mask Generation" style="
            display: block; /* 纭繚鍥剧墖鐙崰涓€琛?*/
            margin: 0 auto; /* 纭繚鍥剧墖鍦ㄥ叾鐖跺鍣ㄤ腑灞呬腑 */
            max-width: 100%; /* 纭繚鍥剧墖涓嶈秴杩囧鍣ㄥ搴?*/
            height: auto;
            border: 1px solid #ddd; /* 杞诲井杈规 */
            border-radius: 8px; /* 杞诲井鍦嗚 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 鎻愬崌瑙嗚鏁堟灉 */
        " title="P-MASk Prompt Guided Mask Generation">
    </div>
</div>

### 馃幀馃挮 Let's Enjoy Show with Specific Characteristics of Scene
<div style="
    text-align: center;
    padding: 20px 25px;
    margin: 25px auto;
    background: linear-gradient(135deg, #e8f5e9 0%, #ffffff 100%); /* 鏌斿拰娓愬彉鑳屾櫙 */
    border: 3px solid #4caf50; /* 绐佸嚭涓婚鑹茶竟妗?*/
    border-radius: 12px;
    box-shadow: 0 6px 15px rgba(76, 175, 80, 0.3); /* 缁胯壊闃村奖锛岀獊鍑烘牳蹇冩祦绋?*/
    font-size: 1.2em;
    font-weight: 600;
    color: #1b5e20; /* 娣辩豢鑹叉枃鏈?*/
    display: flex;
    justify-content: center;
    align-items: center;
">
    <span style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.8em;">馃</span> Initial Video
    </span>
    <span style="margin: 0 25px; color: #4caf50; font-size: 2.0em; font-weight: 300;">&rarr;</span>
    <span style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.8em;">馃樁鈥嶐煂笍</span> Prompt-Guided Mask
    </span>
    <span style="margin: 0 25px; color: #4caf50; font-size: 2.0em; font-weight: 300;">&rarr;</span>
    <span style="display: flex; align-items: center; gap: 8px;">
        <span style="font-size: 1.8em;">馃コ</span> Inpaint Video
    </span>
</div>

<div style="text-align:center; margin:0;">
  <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/alita1_result/alita1_triple_comparison.mp4" target="_blank" rel="noopener">
    <img src="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/alita1_result/alita1_triple_comparison.gif" alt="涓夊悎涓€骞舵帓瀵规瘮棰勮" style="width:95%; max-width:1400px; border:2px solid #ddd; border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.12);" />
  </a>
  <p style="margin:4px 0; color:#888; font-size:0.85em;">馃搾 Rapid and Continuous Movement 馃摋 Spanning Large Area 馃摃 Slow Motion 馃 Prompt:  flying chains apart from its tips<a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/alita1_result/alita1_triple_comparison.mp4" target="_blank" style="margin-left:8px; color:#0074d9; text-decoration:none;">馃攳 Check out Alita:Fight Angle 馃コ</a></p>
</div>

<!-- 鏇村绀轰緥锛堢珫鐩存帓鍒楋級 -->
<div style="text-align:center; margin:0;">
  <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/Zoopic_result/Zoopic_triple_comparison.mp4" target="_blank" rel="noopener">
    <img src="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/Zoopic_result/Zoopic_triple_comparison.gif" alt="Zoopic 涓夊悎涓€瀵规瘮棰勮" style="width:95%; max-width:1400px; border:2px solid #ddd; border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.12);" />
  </a>
  <p style="margin:4px 0; color:#888; font-size:0.85em;">馃搾 Semantic Understand 馃摋Screen Jump 馃摃 Background and Object Classify馃 the carrot 馃煱 馃 the thing held by rabbit 馃煱 馃 the thing clicked at 1st shot<a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/Zoopic_result/Zoopic_triple_comparison.mp4" target="_blank" style="margin-left:8px; color:#0074d9; text-decoration:none;">馃攳 Check out your Officer Judy !</a></p>
</div>

<div style="text-align:center; margin:0;">
  <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/dream3_result/dream3_triple_comparison.mp4" target="_blank" rel="noopener">
    <img src="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/dream3_result/dream3_triple_comparison.gif" alt="dream3 涓夊悎涓€瀵规瘮棰勮" style="width:95%; max-width:1400px; border:2px solid #ddd; border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.12);" />
  </a>
  <p style="margin:4px 0; color:#888; font-size:0.85em;">馃搾 Semantic Understand 馃摋 Slow Motion 馃摃 Background and Object Classify 馃 Prompt: the person setting on chair fell off <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/dream3_result/dream3_triple_comparison.mp4" target="_blank" style="margin-left:8px; color:#0074d9; text-decoration:none;">馃攳 Check out to Time Reversal !</a></p>
</div>

<div style="text-align:center; margin:0;">
  <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/batman6_result/batman6_triple_comparison.mp4" target="_blank" rel="noopener">
    <img src="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/batman6_result/batman6_triple_comparison.gif" alt="batman6 涓夊悎涓€瀵规瘮棰勮" style="width:95%; max-width:1400px; border:2px solid #ddd; border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.12);" />
  </a>
  <p style="margin:4px 0; color:#888; font-size:0.85em;">馃搾 Semantic Understand 馃摋Long-duration Movement 馃摃 Complex Background 馃 the person running out with yellow clothes 馃煱 馃 the person who runs faster<a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/batman6_result/batman6_triple_comparison.mp4" target="_blank" style="margin-left:8px; color:#0074d9; text-decoration:none;">馃攳 Check out to find whether he also fell off ?</a></p>
</div>

<div style="text-align:center; margin:0;">
  <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/space_travel1_result/space_travel1_triple_comparison.mp4" target="_blank" rel="noopener">
    <img src="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/space_travel1_result/space_travel1_triple_comparison.gif" alt="space_travel1 涓夊悎涓€瀵规瘮棰勮" style="width:95%; max-width:1400px; border:2px solid #ddd; border-radius:12px; box-shadow:0 8px 16px rgba(0,0,0,0.12);" />
  </a>
  <p style="margin:4px 0; color:#888; font-size:0.85em;">馃 Prompt: the girl who runs out of the house <a href="https://raw.githubusercontent.com/SuleynanAuir/PEANUT--Prompt-Enhanced-Ablation-with-Optical-Flow-Based-Neural-Unit-from-IMG2Video-Field/main/esults/space_travel1_result/space_travel1_triple_comparison.mp4" target="_blank" style="margin-left:8px; color:#0074d9; text-decoration:none;">馃攳 Check out Murphy, click !</a></p>
</div>


<!-- > *馃 Frame Processing and Detail Capture of Action Shots -->

<div style="
    text-align: center; /* 灞呬腑鏁翠釜鍖哄潡鐨勫唴瀹?*/
    margin: 30px auto; 
    max-width: 2000px; /* 鎺у埗鏈€澶у搴?*/
    padding: 10px 0;
">
    <h3 style="
        color: #1b5e20; /* 鍖归厤娴佺▼鏉＄殑娣辩豢鑹蹭富棰?*/
        margin-bottom: 5px; /* 鍑忓皯鏍囬鍜屼笅闈㈢殑鍏冪礌涔嬮棿鐨勯棿璺?*/
        font-size: 1.4em;
        font-weight: 800; /* 鏋佽嚧鍔犵矖 */
        display: block; /* 纭繚鏍囬鍗犳嵁瀹屾暣瀹藉害 */
        padding: 5px 15px 5px 15px;
        letter-spacing: 0.5px; 
        text-transform: uppercase;
    ">
        馃 Frame Processing and Detail Capture of Shots
    </h3>
    <div style="display: inline-block; max-width: 100%; margin-top: 10px;">
        <div style="
            border-bottom: 3px solid #4caf50; 
            margin-bottom: 10px; /* 澧炲姞绾垮拰鍥剧墖涔嬮棿鐨勯棿璺?*/
            margin-top: 5px; /* 澧炲姞鏍囬鍜岀嚎涔嬮棿鐨勯棿璺?*/
        "></div>
        <img src="paper/graphs/preview1.png" alt="P-MASk Prompt Guided Mask Generation" style="
            display: block; /* 纭繚鍥剧墖鐙崰涓€琛?*/
            margin: 0 auto; /* 纭繚鍥剧墖鍦ㄥ叾鐖跺鍣ㄤ腑灞呬腑 */
            max-width: 100%; /* 纭繚鍥剧墖涓嶈秴杩囧鍣ㄥ搴?*/
            height: auto;
            border: 1px solid #ddd; /* 杞诲井杈规 */
            border-radius: 8px; /* 杞诲井鍦嗚 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 鎻愬崌瑙嗚鏁堟灉 */
        " title="P-MASk Prompt Guided Mask Generation">
    </div>
</div>


<!-- ![](paper/graphs/preview1.png "P-MASk Prompt Guided Mask Generation") -->

###  馃搨 1. Folder Structure

```
SuperVideo-inpaint/
鈹溾攢鈹€ raw_video/              # patch processing raw video input
鈹溾攢鈹€ results/                # patch processing inpaint result (IMG/GIF)
鈹溾攢鈹€ demo_video/             # single processing demo video input
鈹溾攢鈹€ demo_output/            # single processing demo video output
鈹?
鈹溾攢鈹€ frames_package/         # temp: video2frames (fps/extract-rate settings)
鈹溾攢鈹€ mask_package/           # temp: mask generation based on frame_package with P-MASk processed
鈹溾攢鈹€ inpaint_package/        # temp: NOF-Eraser output storage
鈹溾攢鈹€ restore_package/        # temp: UR-Net output storage
鈹溾攢鈹€ denoise_package/        # temp: nlm denoise processed 
鈹?
鈹溾攢鈹€ experiment/             # exp & eval metrics
鈹?  鈹斺攢鈹€ exp0/               # the fail of Big-LaMa implemented in video inpaint
鈹?  鈹斺攢鈹€ exp1/               # P-MASk Hyperparameters: model-size / clip-window / step
鈹?  鈹斺攢鈹€ exp2/               # NOF-Eraser Hyperparameters: neighbors / step


鈹?
鈹溾攢鈹€ SAMWISE/                # project 1 P-MASk: prompt guied mask generation for each sampled frames 
鈹溾攢鈹€ E2FGVI_Project/         # project 2 NOF-Eraser: flow-based video inpaint
鈹溾攢鈹€ BasicVSR_PlusPlus/      # project 3 UR-Net & Denoise Block for video clearity
鈹?
鈹溾攢鈹€ video_inpaint_pipeline_en.ps1  # 猸愷煉?main function to patch process
鈹斺攢鈹€ video_inpaint_demo.ps1         # 猸?demo single process
```

### 馃殌 2. Quick Start (Demo + Patch)

#### 2.1 Method 1: Demo Script 

Single Video for the whoe processing pipeline.

```powershell
# video to ur demo_video package
Copy-Item "your_video.mp4" -Destination "demo_video\"
# run
.\video_inpaint_demo.ps1 -VideoPath "your_video.mp4" -TextPrompt "the object to remove"
# model saved in: demo_output\your_video_result\
```

**Advantage**:
- 鉁?Automatically creates a separate output folder

- 鉁?Retains all intermediate results (frames, masks, repairs, enhancements)

- 鉁?Suitable for single video testing and debugging

- 鉁?Supports custom resolution, FPS, and other parameters

#### 2.2 Method 2: Batch Processing Pipeline 馃摎

batch processing in `raw_video` package video

- basic pipeline version (all)
```powershell
# put video into ur raw_video package
Copy-Item "video.mp4" -Destination "raw_video\"
# bathc processing pipeline
.\video_inpaint_pipeline_en.ps1 -VideoPath "raw_video\video.mp4" -TextPrompt "the object"
# results saved in results package
```

- advanced pipeline version
```powershell
# skip certain steps
.\video_inpaint_pipeline_en.ps1 `
    -VideoPath "raw_video\video.mp4" `
    -TextPrompt "object" `
    -SkipMask `
    -SkipInpaint
```

**Advantage**:
- 鉁?Supports specifying the output directory (-OutputDir)

- 鉁?Automatically cleans up intermediate files

- 鉁?Suitable for batch processing of multiple videos

### 3. 馃摑 Use Demo

#### 3.1 Demo 1: Demo Basic Usage  
```powershell
.\video_inpaint_demo.ps1 -VideoPath "alita1.mp4" -TextPrompt "the flying chains and its lips"
```

#### 3.2 Demo 2: Custom Resolution and FPS
- max resolution (default 1080)
- fps (default 30)

```powershell
.\video_inpaint_demo.ps1 `
    -VideoPath "batman1.mp4" `
    -TextPrompt "the person walking on the left" `
    -MaxResolution 1080 ` 
    -FrameExtractionFps 30
```

#### 3.3 Demo 3: Fast Mode (CPU mode, Skip enhancements 鉂?
```powershell
.\video_inpaint_demo.ps1 `
    -VideoPath "test.mp4" `
    -TextPrompt "the watermark" `
    -SkipEnhance `
    -ForceCPU
```

#### 3.4 Demo 4: High Quality Mode (Slower GPU mode, All pipeline 鉁?

- maximum settings with All Settings Pipeline
 
```powershell
.\video_inpaint_demo.ps1 `
    -VideoPath "video.mp4" `
    -TextPrompt "the logo" `
    -NeighborStride 2 `
    -MaxLoadFrames 12 `
    -DenoiseStrength 7
```


### 鈿欙笍 4. Parameter Description

#### 4.1 Demo Script (video_inpaint_demo_en.ps1)

| Parameters | Necessity | Default | Statement |
| :--- | :---: | :---: | :--- |
| `-VideoPath` | <span style="color: green; font-weight: bold;">&#x2713;</span> | - | demo\_video the path od video |
| `-TextPrompt` | <span style="color: green; font-weight: bold;">&#x2713;</span> | - | the removed object in natural language|
| `-MaxResolution` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 720 | max resolution锛宭imit frames' height /width |
| `-FrameExtractionFps` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 30 | Frame Extractions FPS |
| `-NeighborStride` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 3 | Neighborhood step size (1-10, smaller values 鈥嬧€媟esult in better quality but slower speed) |
| `-MaxLoadFrames` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 8 | Maximum number of frames loaded (affects memory usage and quality) |
| `-DenoiseStrength` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 5 | Noise reduction intensity (1-10) |
| `-SkipMask` | <span style="color: red; font-weight: bold;">&#x2717;</span> | <span style="color: red; font-weight: bold;">&#x2717;</span> | Skip P-MASk Processing |
| `-SkipInpaint` | <span style="color: red; font-weight: bold;">&#x2717;</span> | <span style="color: red; font-weight: bold;">&#x2717;</span> | Skip NOF-Eraser Video Inpainting |
| `-SkipEnhance` | <span style="color: red; font-weight: bold;">&#x2717;</span> | <span style="color: red; font-weight: bold;">&#x2717;</span> | Skip UR-Net Video Enhancement |
| `-SkipDenoise` | <span style="color: red; font-weight: bold;">&#x2717;</span> | <span style="color: red; font-weight: bold;">&#x2717;</span> | Skip Denoise |
| `-ForceCPU` | <span style="color: red; font-weight: bold;">&#x2717;</span> | <span style="color: red; font-weight: bold;">&#x2717;</span> | Force CPU锛圔asicVSR++锛墊

#### 4.2 Batch Processing (video_inpaint_pipeline_en.ps1)

| Parameters | Necessity | Default | Statement |
| :--- | :---: | :---: | :--- |
| `-VideoPath` | <span style="color: green; font-weight: bold;">&#x2713;</span> | - | Video file path (supports relative and absolute paths) |
| `-TextPrompt` | <span style="color: green; font-weight: bold;">&#x2713;</span> | - | Description of the object to be removed (English) |
| `-OutputDir` | <span style="color: red; font-weight: bold;">&#x2717;</span> | "results" | Output directory (relative or absolute path) |
| `-NeighborStride` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 3 | Neighbor stride |
| `-MaxLoadFrames` | <span style="color: red; font-weight: bold;">&#x2717;</span> | 8 | Maximum number of frames to load |
| `-OtherParams` | <span style="color: red; font-weight: bold;">&#x2717;</span> | - | Similar to the demonstration script |

<!-- ## 馃幆 Processing Flow

<div style="
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    background-color: #f9f9f9; 
    padding: 20px; 
    border-radius: 10px; 
    border: 1px solid #eee;
">
    
#### 馃摜 Input
<div style="background-color: #e0f7fa; padding: 5px 15px; border-radius: 5px; margin: 5px 0; font-weight: bold; border: 1px dashed #00bcd4;">
    `Input Video` (`demo_video/` or `raw_video/`)
</div>

<div style="background-color: #d7f3c1ff; padding: 5px 15px; border-radius: 5px; margin: 5px 0; font-weight: bold; border: 1px dashed #00bcd4;">
    `Prompt Configs` (`raw_prompt/prompt_list`)
</div>

猬囷笍

#### 1锔忊儯 **STEP1 Frame Extraction: fos and Frame Resolution**
  * **Method:** Extract video frames using OpenCV
  * **鉃★笍 Output:** `frames_package/` <span style="font-size: 0.9em; color: #b80f0fff;">(PNG Format Frames)</span>

猬囷笍

#### 2锔忊儯 **STEP2 Mask Generation: P-MASk Module**
* **Method:** Generate object masks based on text prompt
* **鉃★笍 Output:** `mask_package/` <span style="font-size: 0.9em; color: #281cd5ff;">(Binary-Value Masks)</span>

猬囷笍

#### 3锔忊儯 **STEP3 Frame and Mask Resizing: Speedup 馃挮**
* **Method:** Adjust to specified resolution
* **鉃★笍 Output:** `*_resized` folder

猬囷笍

#### 4锔忊儯 **STEP4 Video Inpainting: NOF-Eraser**
* **Method:** Remove masked objects (E2FGVI-based)
* **鉃★笍 Output:** `inpaint_package/` <span style="font-size: 0.9em; color: #12d12cff;">(Inpainted Frames)</span>

猬囷笍

#### 5锔忊儯 **STEP5 Quality Enhancement: UR-Net with BasicVSR++**
* **Method:** Improve video quality and clarity
* **鉃★笍 Output:** `restore_package/` <span style="font-size: 0.9em; color: #c61b79ff;">(Enhanced Frames)</span>

猬囷笍

#### 6锔忊儯 **STEP 6 Denoising Module: nlm denoise**
* **Method:** Apply NLM/Bilateral/Gaussian denoising
* **鉃★笍 Output:** `denoise_package/` <span style="font-size: 0.9em; color: #5846a5ff;">(Denoised Frames)</span>

猬囷笍

#### 7锔忊儯 **STEP7 Video Generation**
* **Method:** Create final video from frame sequence

猬囷笍
<div style="margin-top: 15px; padding: 10px 20px; border-radius: 8px; background-color: #e8f5e9; border: 2px solid #4caf50;">
    鉁?**Output:** <span style="font-weight: bold;">`demo_output/` or `results/`</span>
</div>

</div> -->

### 馃殌 5. PEANUT Video Processing Architecture

<div style="
    display: flex; 
    flex-direction: column; 
    align-items: center; 
    background-color: #ffffff; /* 绾櫧鑳屾櫙 */
    padding: 30px 15px; 
    border-radius: 15px; /* 鏇村渾娑︾殑杈硅 */
    box-shadow: 0 15px 30px rgba(0,0,0,0.15); /* 鏇存繁鐨勯槾褰憋紝绐佸嚭涓讳綋 */
    margin: 20px 0;
">
    
<h4 style="color: #00796b; margin-bottom: 8px; border-bottom: 2px solid #00796b; padding-bottom: 3px;">馃摜 INPUT DATA / CONFIGS</h4>
<div style="
    display: flex; 
    flex-direction: column; /* 鍏抽敭淇敼锛氬皢鍏冪礌鍨傜洿鍫嗗彔 */
    align-items: center;    /* 鍏抽敭淇敼锛氬皢鍏冪礌娌夸氦鍙夎酱锛堟按骞虫柟鍚戯級灞呬腑 */
    gap: 15px;              /* 璋冩暣鍏冪礌闂寸殑鍨傜洿闂磋窛 */
    width: 100%;
    margin: 10px 0;
">
    <div style="background-color: #e0f7fa; padding: 10px 25px; border-radius: 8px; font-weight: bold; border: 2px solid #00bcd4; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        `Input Video` (`demo_video/` or `raw_video/`)
    </div>
    <div style="background-color: #fffde7; padding: 10px 25px; border-radius: 8px; font-weight: bold; border: 2px solid #ff9800; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">
        `Prompt Configs` (`raw_prompt/prompt_list`)
    </div>
</div>

<div style="width: 4px; height: 35px; background-color: #b3e5fc; margin: 15px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 20px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #e8eaf6; border-left: 6px solid #5c6bc0; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #5c6bc0;">1锔忊儯 馃帪锔?STEP 1: Frame Extraction (FPS & Resolution)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Extract video frames using OpenCV</li>
        <li>鉃★笍 Output: `frames_package/` <span style="font-size: 0.9em; color: #b80f0fff; font-weight: bold;">(PNG Format Frames)</span></li>
    </ul>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #e3f4fd; border-left: 6px solid #29b6f6; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #29b6f6;">2锔忊儯 鉁傦笍 STEP 2: Mask Generation (P-MASk Module)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Generate object masks based on text prompt</li>
        <li>鉃★笍 Output: `mask_package/` <span style="font-size: 0.9em; color: #281cd5ff; font-weight: bold;">(Binary-Value Masks)</span></li>
    </ul>
</div>

<div style="
    text-align: center; /* 灞呬腑鏁翠釜鍖哄潡鐨勫唴瀹?*/
    margin: 30px auto; 
    max-width: 2000px; /* 鎺у埗鏈€澶у搴?*/
    padding: 10px 0;
">
    <h3 style="
        color: #1b5e20; /* 鍖归厤娴佺▼鏉＄殑娣辩豢鑹蹭富棰?*/
        margin-bottom: 5px; /* 鍑忓皯鏍囬鍜屼笅闈㈢殑鍏冪礌涔嬮棿鐨勯棿璺?*/
        font-size: 1.4em;
        font-weight: 800; /* 鏋佽嚧鍔犵矖 */
        display: block; /* 纭繚鏍囬鍗犳嵁瀹屾暣瀹藉害 */
        padding: 5px 15px 5px 15px;
        letter-spacing: 0.5px; 
        text-transform: uppercase;
    ">
        鈿欙笍 P-MASk Module Architecture
    </h3>
    <div style="display: inline-block; max-width: 100%; margin-top: 10px;">
        <div style="
            border-bottom: 3px solid #4caf50; 
            margin-bottom: 10px; /* 澧炲姞绾垮拰鍥剧墖涔嬮棿鐨勯棿璺?*/
            margin-top: 5px; /* 澧炲姞鏍囬鍜岀嚎涔嬮棿鐨勯棿璺?*/
        "></div>
        <img src="paper/graphs/P_MASk_Structure.png" alt="P-MASk Prompt Guided Mask Generation" style="
            display: block; /* 纭繚鍥剧墖鐙崰涓€琛?*/
            margin: 0 auto; /* 纭繚鍥剧墖鍦ㄥ叾鐖跺鍣ㄤ腑灞呬腑 */
            max-width: 100%; /* 纭繚鍥剧墖涓嶈秴杩囧鍣ㄥ搴?*/
            height: auto;
            border: 1px solid #ddd; /* 杞诲井杈规 */
            border-radius: 8px; /* 杞诲井鍦嗚 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 鎻愬崌瑙嗚鏁堟灉 */
        " title="P-MASk Prompt Guided Mask Generation">
    </div>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #fbe9e7; border-left: 6px solid #ff7043; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #ff7043;">3锔忊儯 鈿?STEP 3: Resizing (Frame & Mask Speedup 馃挮)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Adjust to specified resolution</li>
        <li>鉃★笍 Output: `*_resized` folder</li>
    </ul>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 20px; background: #e0f2f1; border: 4px solid #009688; border-radius: 12px; box-shadow: 0 8px 15px rgba(0, 150, 136, 0.3);">
    <h4 style="margin: 0 0 5px 0; color: #009688;">4锔忊儯 馃獎 STEP 4: Video Inpainting (NOF-Eraser CORE)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 1em; font-weight: 500; line-height: 1.6;">
        <li>Method: Remove masked objects (E2FGVI-based)</li>
        <li>鉃★笍 Output: `inpaint_package/` <span style="font-size: 0.9em; color: #12d12cff; font-weight: bold;">(Inpainted Frames)</span></li>
    </ul>
</div>

<div style="
    text-align: center; /* 灞呬腑鏁翠釜鍖哄潡鐨勫唴瀹?*/
    margin: 30px auto; 
    max-width: 2000px; /* 鎺у埗鏈€澶у搴?*/
    padding: 10px 0;
">
    <h3 style="
        color: #1b5e20; /* 鍖归厤娴佺▼鏉＄殑娣辩豢鑹蹭富棰?*/
        margin-bottom: 5px; /* 鍑忓皯鏍囬鍜屼笅闈㈢殑鍏冪礌涔嬮棿鐨勯棿璺?*/
        font-size: 1.4em;
        font-weight: 800; /* 鏋佽嚧鍔犵矖 */
        display: block; /* 纭繚鏍囬鍗犳嵁瀹屾暣瀹藉害 */
        padding: 5px 15px 5px 15px;
        letter-spacing: 0.5px; 
        text-transform: uppercase;
    ">
        鈿欙笍 NOF-Eraser Module Architecture
    </h3>
    <div style="display: inline-block; max-width: 100%; margin-top: 10px;">
        <div style="
            border-bottom: 3px solid #4caf50; 
            margin-bottom: 10px; /* 澧炲姞绾垮拰鍥剧墖涔嬮棿鐨勯棿璺?*/
            margin-top: 5px; /* 澧炲姞鏍囬鍜岀嚎涔嬮棿鐨勯棿璺?*/
        "></div>
        <img src="paper/graphs/NOF_FULL.png" alt="P-MASk Prompt Guided Mask Generation" style="
            display: block; /* 纭繚鍥剧墖鐙崰涓€琛?*/
            margin: 0 auto; /* 纭繚鍥剧墖鍦ㄥ叾鐖跺鍣ㄤ腑灞呬腑 */
            max-width: 100%; /* 纭繚鍥剧墖涓嶈秴杩囧鍣ㄥ搴?*/
            height: auto;
            border: 1px solid #ddd; /* 杞诲井杈规 */
            border-radius: 8px; /* 杞诲井鍦嗚 */
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1); /* 鎻愬崌瑙嗚鏁堟灉 */
        " title="P-MASk Prompt Guided Mask Generation">
    </div>
</div>


<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #f3e5f5; border-left: 6px solid #ab47bc; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #ab47bc;">5锔忊儯 馃専 STEP 5: Quality Enhancement (UR-Net with BasicVSR++ Algorithm)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Improve video quality and clarity</li>
        <li>鉃★笍 Output: `restore_package/` <span style="font-size: 0.9em; color: #c61b79ff; font-weight: bold;">(Enhanced Frames)</span></li>
    </ul>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #e0f7fa; border-left: 6px solid #039be5; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #039be5;">6锔忊儯 馃Ъ STEP 6: Denoising Module (NLM Denoise)</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Apply NLM/Bilateral/Gaussian denoising</li>
        <li>鉃★笍 Output: `denoise_package/` <span style="font-size: 0.9em; color: #5846a5ff; font-weight: bold;">(Denoised Frames)</span></li>
    </ul>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #3f51b5; margin: 0 auto 15px auto;"></div>

<div style="width: 95%; max-width: 550px; padding: 15px; background: #e6f0e6; border-left: 6px solid #66bb6a; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
    <h4 style="margin: 0 0 5px 0; color: #66bb6a;">7锔忊儯 馃帴 STEP 7: Video Generation</h4>
    <ul style="list-style: none; padding-left: 15px; margin: 0; font-size: 0.9em; line-height: 1.5;">
        <li>Method: Create final video from frame sequence</li>
    </ul>
</div>

<div style="width: 4px; height: 25px; background-color: #b3e5fc; margin: 10px auto 0 auto; border-radius: 2px;"></div>
<div style="width: 0; height: 0; border-left: 8px solid transparent; border-right: 8px solid transparent; border-top: 12px solid #4caf50; margin: 0 auto 15px auto;"></div>


<div style="width: 95%; max-width: 550px; margin-top: 15px; padding: 20px; border-radius: 12px; background-color: #e8f5e9; border: 3px solid #4caf50; box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3);">
    <h4 style="margin: 0; color: #4caf50;">鉁?FINAL OUTPUT</h4>
    <span style="font-weight: bold; font-size: 1.2em;">`demo_output/` or `results/`</span>
</div>

</div>

### 馃挕 6. Performance Recommendations

#### 6.1 Quick Mode (Low Quality & Fast馃弮鈥嶁檪锔忊€嶁灐锔?
```powershell
-NeighborStride 5 -MaxLoadFrames 4 -DenoiseStrength 3
```

#### 6.2 Balanced Mode (Recommended馃コ)
```powershell
-NeighborStride 3 -MaxLoadFrames 8 -DenoiseStrength 5
```

#### 6.3 Quality Mode (High Quality & Slow Speed馃檱鈥嶁檧锔?
```powershell
-NeighborStride 2 -MaxLoadFrames 12 -DenoiseStrength 7
```

### 鈿狅笍 7. Important Operating Notes

> Please follow these guidelines before running the processing script to ensure optimal performance and results.

<div style="margin-top: 15px;">
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 12px; padding: 10px; border-left: 4px solid #007bff; background-color: #f7f9fc; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        馃憠 1. Video Path Restriction
        <p style="margin: 5px 0 0 15px; font-size: 0.95em;">
            You only need to provide the **filename** (e.g., `alita1.mp4`). The video file **must** be placed inside the <code style="background-color: #ffe0b2; padding: 2px 4px; border-radius: 3px;">raw_video/</code> folder.
        </p>
    </li>
    <li style="margin-bottom: 12px; padding: 10px; border-left: 4px solid #28a745; background-color: #f7fcf7; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        馃棧锔?2. Text Prompt Language
        <p style="margin: 5px 0 0 15px; font-size: 0.95em;">
            The object to be removed must be described using **English text prompts** (e.g., "the person", "the car", "the traffic sign").
        </p>
    </li>
    <li style="margin-bottom: 12px; padding: 10px; border-left: 4px solid #ffc107; background-color: #fffdf7; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        馃捑 3. Memory Usage (VRAM)
        <p style="margin: 5px 0 0 15px; font-size: 0.95em;">
            If you encounter **Out-of-Memory (OOM) errors**, please try reducing the value of the <code style="background-color: #ffe0b2; padding: 2px 4px; border-radius: 3px;">MaxLoadFrames</code> parameter.
        </p>
    </li>
    <li style="margin-bottom: 12px; padding: 10px; border-left: 4px solid #dc3545; background-color: #fcf7f7; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        鈴憋笍 4. Processing Time Estimate
        <p style="margin: 5px 0 0 15px; font-size: 0.95em;">
            Processing time depends on video length and parameter settings. A 10-second video typically requires **5 to 20 minutes** for full pipeline execution.
        </p>
    </li>
    <li style="margin-bottom: 12px; padding: 10px; border-left: 4px solid #6c757d; background-color: #fcfcfc; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
        馃Ч 5. Clean Run Policy
        <p style="margin: 5px 0 0 15px; font-size: 0.95em;">
            Each new script run will **clear all previous intermediate results** (e.g., frames, masks) to maintain a clean directory structure.
        </p>
    </li>
</ul>
</div>

***

### 馃洜锔?8. Environment Requirements

<div style="
    padding: 20px; 
    border: 1px solid #ddd; 
    border-radius: 10px; 
    background-color: #f8f8f8; 
    box-shadow: 0 4px 8px rgba(0,0,0,0.05);
">
    
#### 馃枼锔?8.1 **Operating System**
<div style="
    background-color: #e6f7ff; 
    padding: 8px 15px; 
    border-radius: 6px; 
    font-weight: bold; 
    border-left: 5px solid #1890ff;
    margin-top: 10px;
">
    Windows | CUDA: 12.7 | PyTorch Version: 2.6.0+cu124
CUDA Available: True
CUDA Version: 12.4 
</div>

#### 馃И 8.2 **Conda Environments (Dependencies)**

<p style="font-size: 0.9em; color: #555;">
    The processing pipeline requires three dedicated Conda environments for different components:
</p>

<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #bae0ff; background-color: #e6f7ff; border-radius: 6px;">
        <span style="font-weight: bold; color: #1890ff;">Conda Environment:</span> <code>samwise</code>
        <p style="margin: 5px 0 0 15px; font-size: 0.9em; color: #333;">
            <span style="font-weight: bold; color: #52c41a;">&rarr; Function:</span> Mask Generation (SAMWISE Project)
        </p>
    </li>
    <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #fff1b8; background-color: #fffbe6; border-radius: 6px;">
        <span style="font-weight: bold; color: #faad14;">Conda Environment:</span> <code>e2fgvi-project</code>
        <p style="margin: 5px 0 0 15px; font-size: 0.9em; color: #333;">
            <span style="font-weight: bold; color: #52c41a;">&rarr; Function:</span> Video Inpainting (E2FGVI Project)
        </p>
    </li>
    <li style="margin-bottom: 10px; padding: 10px; border: 1px solid #ffccc7; background-color: #fff1f0; border-radius: 6px;">
        <span style="font-weight: bold; color: #f5222d;">Conda Environment:</span> <code>basicvsrpp-demo</code>
        <p style="margin: 5px 0 0 15px; font-size: 0.9em; color: #333;">
            <span style="font-weight: bold; color: #52c41a;">&rarr; Function:</span> Quality Enhancement (BasicVSR++ Project)
        </p>
    </li>
</ul>

</div>



### 馃幀 9. Video Content Inpainting Workflow Examples

The following provides two structured workflows using PowerShell for a hypothetical video inpainting project (assumed to be `SuperVideo-inpaint`).

#### I. Demonstration Script Workflow: Rapid Single-Video Testing鉁?

This workflow is optimized for quickly verifying the project setup, the performance of the **segmentation model** (Mask Generation), and the final **inpainting quality** on a single test video.

| Step | Command (PowerShell) | Purpose & Technical Explanation |
| :--- | :--- | :--- |
| **1. Navigate to Project Root Path** | `cd C:\Users\Aiur\SuperVideo-inpaint` | Change directory to the repository's root, ensuring correct path resolution for all dependencies and scripts. |
| **2. Data Ingestion** | `Copy-Item "D:\alita1.mp4" -Destination "demo_video\"` | Ingest the source video into the designated input folder (`demo_video/`) for the demonstration environment. |
| **3. Core Execution** | `.\video_inpaint_demo.ps1 -VideoPath "alita1.mp4" -TextPrompt "the flying chains and its lips"` | Executes the primary pipeline: 1. **Frame Extraction**. 2. **Prompt-based Segmentation/Mask Generation** (e.g., using SAM or RITM). 3. **Video Inpainting** (e.g., using a Flow-based or RNN model). |
| **4. Final Output Review** | `explorer demo_output\alita1_result` | Quickly opens the directory containing the processed, high-quality output video (`alita1_result.mp4`). |

> #### 馃敩 Intermediate Results Analysis (Debugging Phase)
> For professional debugging and **Quantitative Evaluation** of the model's performance (e.g., checking Mask IoU or Inpainting Consistency), these folders are crucial: 
>
> * `explorer frames_package\alita1`: Review the original **frame sequence**.
> * `explorer mask_package\alita1_mask`: Examine the generated **temporal mask sequence**, which defines the target region for removal.
> * `explorer inpaint_package\alita1`: Analyze the per-frame **inpainting results** before final video composition/post-processing.

---

#### II. Batch Pipeline Workflow: Large-Scale Processing and Data Engineering鉁?

This workflow is designed for running multiple jobs, facilitating large-scale **data science experiments** and providing control over output organization.

| Step | Command (PowerShell) | Purpose & Technical Explanation |
| :--- | :--- | :--- |
| **1. Bulk Data Preparation** | `Copy-Item "D:\videos\*.mp4" -Destination "raw_video\"` | Standardizes input by copying a batch of raw videos into the designated processing queue folder (`raw_video/`). |
| **2. Sequential Processing (Job 1)** | `.\video_inpaint_pipeline_en.ps1 -VideoPath "raw_video\video1.mp4" -TextPrompt "the person"` | Initiates the pipeline to remove the target object ("the person") from `video1.mp4`. |
| **3. Sequential Processing (Job 2)** | `.\video_inpaint_pipeline_en.ps1 -VideoPath "raw_video\video2.mp4" -TextPrompt "the car"` | Initiates the pipeline to remove the target object ("the car") from `video2.mp4`. |

> ### 鈿欙笍 10. Custom Output Directory for Experiment Tracking
> The `-OutputDir` parameter is vital for **Mathematical Modeling/Experimentation**, allowing results from different models or parameter configurations to be isolated for comparison and analysis.
>
> ```powershell
> .\video_inpaint_pipeline_en.ps1 `
>     -VideoPath "raw_video\video3.mp4" `
>     -TextPrompt "the logo" `
>     -OutputDir "custom_output\LogoRemoval_ExperimentA"
> ```

### 馃搳 11. Quality Assessment & Metric Evaluation Workflow

This section outlines the workflow for running **EXP0**, a controlled experiment designed to rigorously evaluate the inpainting quality of the **LAMA4Video** model against established metrics.

| Step | Command (PowerShell) | Purpose & Technical Explanation |
| :--- | :--- | :--- |
| **1. Change Directory** | `cd experiment\exp0` | Navigate to the specific experiment directory to ensure the evaluation scripts can locate the necessary ground truth data and model outputs. |
| **2. Environment Activation** | `conda activate e2fgvi-project` | **Crucial Step:** Activate the designated Anaconda/Conda environment. This environment must contain all dependencies (e.g., PyTorch, NumPy, scikit-image) required by the `e2fgvi-project` for complex metric calculations. |
| **3. Execute Evaluation** | `python evaluate_exp0_quality.py` | Run the script to compute raw quantitative metrics by comparing the LAMA4Video output with the ground truth (GT) frames. This generates the primary data for analysis. |
| **4. Generate Visual Reports** | `python visualize_exp0_quality.py` | Creates detailed, per-video visualizations (e.g., charts, plots) for metric trends over time or frame sequence. |
| **5. Generate Overall Summary** | `python visualize_overall_exp0_metrics.py` | Generates aggregated reports (e.g., bar charts, box plots) summarizing the **mean** and **variance** of metrics across the entire dataset. |
| **6. Review Results** | `explorer results\metrics` | Opens the output directory containing the generated CSV/JSON metric files and the final visualization plots (e.g., PNG, SVG). |

#### 馃搱 Core Evaluation Metrics

The experiment focuses on both traditional signal processing metrics and specialized metrics for video consistency:

| Metric Name (Full) | Acronym | Domain & Relevance |
| :--- | :--- | :--- |
| **Peak Signal-to-Noise Ratio** | PSNR | Measures absolute reconstruction fidelity based on Mean Squared Error (MSE). Higher is better. |
| **Structural Similarity Index Measure** | SSIM | Assesses perceptual similarity based on luminance, contrast, and structure, aligning more closely with human vision. |
| **Sharpness Score** | - | Measures the clarity of edges and fine details in the output frames (e.g., using Laplace filter variance). |
| **Blur Score** | - | Quantifies the inverse of sharpness, indicating lack of detail and over-smoothing. Lower is better. |
| **Artifact Score** | - | Specialized metric to detect common inpainting defects like checkerboard patterns or color bleeding. Lower is better. |
| **Temporal Consistency** | - | **Critical for Video Inpainting.** Evaluates frame-to-frame smoothness and stability of the repaired region, often via optical flow or difference mapping. |

Would you like me to discuss the underlying mathematical formulations for any of these metrics, such as the equation for SSIM or how Optical Flow is integrated into Temporal Consistency?

### 馃摓 12. Troubleshooting Guide

<div style="
    display: flex;
    flex-direction: column;
    gap: 20px;
    padding: 25px;
    background-color: #f7f7f7; 
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
">

<div style="padding: 15px; border-left: 5px solid #ff4d4f; background-color: #fff1f0; border-radius: 8px;">
    <h4 style="margin-top: 0; color: #ff4d4f;">鉂?Issue 1: Video File Not Found</h4>
    <p style="margin-bottom: 5px; font-weight: bold;">馃挕 Solution:</p>
    <ul style="margin: 0; padding-left: 20px; font-size: 0.95em;">
        <li>Demo Script: Ensure the video is placed in the <code>demo_video/</code> folder.</li>
        <li>Batch Script: Use the full path or correct relative path (e.g., <code>raw_video\video.mp4</code>).</li>
    </ul>
</div>

<div style="padding: 15px; border-left: 5px solid #1890ff; background-color: #e6f7ff; border-radius: 8px;">
    <h4 style="margin-top: 0; color: #1890ff;">馃悕 Issue 2: ModuleNotFoundError (cv2, PIL, etc.)</h4>
    <p style="margin-bottom: 5px; font-weight: bold;">馃挕 Solution:</p>
    <p style="margin: 0; font-size: 0.95em;">The script is designed to automatically activate the correct Conda environment. Ensure all three required environments are properly installed:</p>
    <pre style="background-color: #262626; color: #f0f0f0; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 0.9em;">conda env list  # Check your environments</pre>
</div>

<div style="padding: 15px; border-left: 5px solid #faad14; background-color: #fffbe6; border-radius: 8px;">
    <h4 style="margin-top: 0; color: #faad14;">馃捑 Issue 3: CUDA Out of Memory (OOM)</h4>
    <p style="margin-bottom: 5px; font-weight: bold;">馃挕 Solution:</p>
    <p style="margin: 0; font-size: 0.95em;">Reduce VRAM consumption by decreasing these parameters:</p>
    <pre style="background-color: #262626; color: #f0f0f0; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 0.9em;">-NeighborStride 5 -MaxLoadFrames 4</pre>
</div>

<div style="padding: 15px; border-left: 5px solid #eb2f96; background-color: #fff0f6; border-radius: 8px;">
    <h4 style="margin-top: 0; color: #eb2f96;">馃毇 Issue 4: Mask Count Mismatch (IndexError)</h4>
    <p style="margin-bottom: 5px; font-weight: bold;">Symptom:</p>
    <pre style="background-color: #f7f7f7; color: #eb2f96; padding: 5px; border-radius: 3px; font-size: 0.9em;">IndexError: index X is out of bounds</pre>
    <p style="margin-bottom: 5px; font-weight: bold;">馃挕 Solution: Re-generate Masks</p>
    <p style="margin: 0; font-size: 0.95em;">Clear old intermediate data before re-running:</p>
    <pre style="background-color: #262626; color: #f0f0f0; padding: 8px; border-radius: 4px; margin-top: 8px; font-size: 0.9em;"># Clear old data
Remove-Item "frames_package\video*" -Recurse -Force
Remove-Item "mask_package\video*" -Recurse -Force
.\video_inpaint_demo.ps1 -VideoPath "video.mp4" -TextPrompt "object"</pre>
</div>

<div style="padding: 15px; border-left: 5px solid #52c41a; background-color: #f6ffed; border-radius: 8px;">
    <h4 style="margin-top: 0; color: #52c41a;">鉁?Issue 5: SAMWISE Output Path Error</h4>
    <p style="margin-bottom: 5px; font-weight: bold;">Symptom:</p>
    <pre style="background-color: #f7f7f7; color: #52c41a; padding: 5px; border-radius: 3px; font-size: 0.9em;">Binary masks not found</pre>
    <p style="margin-bottom: 5px; font-weight: bold;">馃挕 Solution:</p>
    <p style="margin: 0; font-size: 0.95em;">This issue includes an automatic fix in the script. Ensure you are using the latest version of <code>video_inpaint_demo.ps1</code>.</p>
</div>

</div>


### 馃攧 13. Version History

<div style="
    display: flex;
    flex-direction: column;
    gap: 15px;
    padding: 25px;
    background-color: #f0f8ff; /* Light blue background for history */
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.1);
">

### 馃煝 v3.0 (2025-12-5)
<ul style="list-style: none; padding-left: 15px; margin: 0;">
    <li style="margin-bottom: 5px;">鉁?Feature: Added the <code>video_inpaint_demo.ps1</code> demonstration script.</li>
    <li style="margin-bottom: 5px;">鉁?Feature: Introduced the EXP0 Quality Assessment System.</li>
    <li style="margin-bottom: 5px;">馃悰 Fix: Resolved automatic Conda environment activation issues.</li>
    <li style="margin-bottom: 5px;">馃悰 Fix: Fixed SAMWISE path detection problems.</li>
    <li style="margin-bottom: 5px;">馃悰 Fix: Fixed frame/mask count validation logic.</li>
    <li style="margin-bottom: 5px;">鈿欙笍 Update: <code>video_inpaint_pipeline_en.ps1</code> now includes the <code>-OutputDir</code> parameter.</li>
</ul>

### 馃煛 v2.0 (2025-11-14)
<ul style="list-style: none; padding-left: 15px; margin: 0;">
    <li style="margin-bottom: 5px;">Initial Release.</li>
</ul>

<hr style="border-top: 1px dashed #ccc;">

<p style="font-weight: bold; font-size: 1.1em; color: #007bff;">
    Current Version: 3.0
</p>

</div>

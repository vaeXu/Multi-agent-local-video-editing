# 创作链路留痕（版权/审核材料）

- 作品：代签 EP01
- 生成时间：2026-11-12T20:21:29+08:00
- 制作方式：本地流水线，素材与中间产物均未上传第三方服务
- 可见 AI 提示标识：AI 辅助制作（片头画面 + MP4 comment 元数据）

## 逐环节记录

### 00_previs 导演台预演与质量门（导演 Agent）
- 结果：pass · 12 镜预演 / 集长 73.0s / 运动预算 固定4镜；质量门 20通过 0待确认 0不通过；生产任务 12 镜待明确确认（指纹 c69345c89071）
- 产物：`output/00_previs/previs.md`（导演台预演表）
- 产物：`output/00_previs/previs.json`（预演数据（轴线/运动预算/时间线））
- 产物：`output/00_previs/production_preview.md`（生产预览（未确认不产生费用））
- 产物：`output/00_previs/production_jobs.json`（生产任务与指纹）
- 产物：`output/00_previs/director_gates.json`（20 条确定性质量门结果）
- 产物：`output/00_creator_docs/剧本.md`（创作文档 · 剧本.md）
- 产物：`output/00_creator_docs/视觉设定.md`（创作文档 · 视觉设定.md）
- 产物：`output/00_creator_docs/分镜.md`（创作文档 · 分镜.md）
- 产物：`output/00_creator_docs/视频提示词.md`（创作文档 · 视频提示词.md）
- 产物：`output/00_creator_docs/剪辑单.md`（创作文档 · 剪辑单.md）
- 命令/处理：director.build_creator_docs() → 五份创作文档（含连续性锁与 REF 槽位）
- 命令/处理：director.previsualize() → 整组镜头时间线 / 轴线 / 运动预算
- 命令/处理：director.production_preview() → 只出预览与指纹，绝不调用生成接口
- 命令/处理：director.run_gates() → 20 条纯字符串/数值门，不调模型

### 01_script 剧本与合规预审（制片 Agent）
- 结果：pass · 12 镜 / 73.0s；前3秒钩子已配置；题材红线扫描 0 项命中；超长台词 0 条
- 产物：`output/01_script/script.md`（人可读剧本）
- 产物：`output/01_script/storyboard.json`（结构化分镜）
- 产物：`output/01_script/precheck.json`（合规预审记录）
- 命令/处理：copy script.md / storyboard.json → output/01_script/
- 命令/处理：题材红线关键词扫描 + 台词长度 + 画风锁定校验

### 02_characters 角色资产与一致性锁定（美术 Agent）
- 结果：pass · 2 个角色；锚点最少 4 条；本机音色全部可用 True
- 产物：`output/02_characters/characters.json`（角色卡）
- 产物：`output/02_characters/consistency_report.json`（一致性报告）
- 产物：`output/02_characters/character_sheets/1_林昭.png`（林昭 定妆卡）
- 产物：`output/02_characters/character_sheets/2_苏晴.png`（苏晴 定妆卡）
- 命令/处理：say -v ? 校验本机音色
- 命令/处理：逐角色生成定妆卡 PNG 与一致性报告

### 03_frames 真人帧 → 漫画化转绘（转绘 Agent）
- 结果：pass · 12 帧 1080×1920；6 张真人源帧转绘 + 6 张同风格派生；水印已本地裁切；跨镜亮度向中位数 71.78 拉近 70%
- 产物：`output/03_frames/frame_sources.csv`（逐镜来源与处理链）
- 产物：`output/03_frames/frame_manifest.json`（帧清单（JSON））
- 产物：`output/03_frames/luma_match.json`（跨镜接镜亮度匹配（70%））
- 产物：`output/02_characters/style_base/`（统一风格底图目录）
- 产物：`output/03_frames/S01.png`（S01 转绘帧）
- 产物：`output/03_frames/S02.png`（S02 转绘帧）
- 产物：`output/03_frames/S03.png`（S03 转绘帧）
- 产物：`output/03_frames/S04.png`（S04 转绘帧）
- 产物：`output/03_frames/S05.png`（S05 转绘帧）
- 产物：`output/03_frames/S06.png`（S06 转绘帧）
- 产物：`output/03_frames/S07.png`（S07 转绘帧）
- 产物：`output/03_frames/S08.png`（S08 转绘帧）
- 产物：`output/03_frames/S09.png`（S09 转绘帧）
- 产物：`output/03_frames/S10.png`（S10 转绘帧）
- 产物：`output/03_frames/S11.png`（S11 转绘帧）
- 产物：`output/03_frames/S12.png`（S12 转绘帧）
- 命令/处理：去水印裁切 → 9:16 居中裁切 → 双边滤波/色阶量化/自适应描线/网点/统一冷调LUT/暗角
- 命令/处理：按 DERIVE_MAP 派生不同景别，逐镜写入 frame_sources.csv
- 命令/处理：match_shot_luma(strength=0.7)：增益限 0.6–1.6，消除硬切亮度跳变

### 04_clips 逐镜生产（真视频/视差）（动画 Agent）
- 结果：pass · 12/12 镜头；真动态视频 1 镜（逐帧本地转绘、去模型水印、对齐全片 LUT） / 本地多层视差 11 镜；逐句字幕时段 + 插入镜闪白 + 片头 AI 标识 + 末镜淡出
- 产物：`output/04_clips/clip_render_log.json`（逐镜生产日志（含通道与来源））
- 产物：`output/04_clips/channel_map.json`（逐镜通道映射）
- 产物：`output/04_clips/S01.mp4`（S01 镜头片段 · generated_video）
- 产物：`output/04_clips/S02.mp4`（S02 镜头片段 · unchanged）
- 产物：`output/04_clips/S03.mp4`（S03 镜头片段 · unchanged）
- 产物：`output/04_clips/S04.mp4`（S04 镜头片段 · unchanged）
- 产物：`output/04_clips/S05.mp4`（S05 镜头片段 · unchanged）
- 产物：`output/04_clips/S06.mp4`（S06 镜头片段 · unchanged）
- 产物：`output/04_clips/S07.mp4`（S07 镜头片段 · unchanged）
- 产物：`output/04_clips/S08.mp4`（S08 镜头片段 · unchanged）
- 产物：`output/04_clips/S09.mp4`（S09 镜头片段 · unchanged）
- 产物：`output/04_clips/S10.mp4`（S10 镜头片段 · unchanged）
- 产物：`output/04_clips/S11.mp4`（S11 镜头片段 · unchanged）
- 产物：`output/04_clips/S12.mp4`（S12 镜头片段 · unchanged）
- 命令/处理：真视频通道：ffmpeg -i generated_video/<Sxx>.mp4 -filter_complex scale/crop/fps/tpad/trim,drawtext -an ...
- 命令/处理：视差通道：ffmpeg -loop 1 -i <frame>.png -loop 1 -i light_overlay.png -filter_complex zoompan,eq,noise,vignette,overlay,drawtext ...
- 命令/处理：片段重拍：替换 input/<项目>/generated_video/<Sxx>.mp4 后执行 --retake Sxx

### 05_audio 本地配音 / BGM / 音效（声音 Agent）
- 结果：pass · 12 段离线配音 + 音效；全片人声轨 73.0s，最大音画漂移 0.0s；BGM 73.0s 本地合成
- 产物：`output/05_audio/audio_sync.json`（音画同步时间轴）
- 产物：`output/05_audio/voice_track.wav`（全片人声轨）
- 产物：`output/05_audio/bgm.wav`（全片氛围 BGM）
- 产物：`output/05_audio/S01.wav`（S01 混音）
- 产物：`output/05_audio/S02.wav`（S02 混音）
- 产物：`output/05_audio/S03.wav`（S03 混音）
- 产物：`output/05_audio/S04.wav`（S04 混音）
- 产物：`output/05_audio/S05.wav`（S05 混音）
- 产物：`output/05_audio/S06.wav`（S06 混音）
- 产物：`output/05_audio/S07.wav`（S07 混音）
- 产物：`output/05_audio/S08.wav`（S08 混音）
- 产物：`output/05_audio/S09.wav`（S09 混音）
- 产物：`output/05_audio/S10.wav`（S10 混音）
- 产物：`output/05_audio/S11.wav`（S11 混音）
- 产物：`output/05_audio/S12.wav`（S12 混音）
- 命令/处理：say -v <voice> -r 165 -o <shot>.aiff '<台词>'  →  ffmpeg 转 44100Hz 双声道
- 命令/处理：numpy 合成音效/BGM → 按 duration_s 拼接 voice_track.wav

### 06_final 字幕 / 合成 / 导出（剪辑 Agent）
- 结果：pass · 成片 EP01.mp4：1080×1920 / h264 / 73.0s / AAC 44100Hz；封面 1200x1600
- 产物：`output/06_final/EP01.mp4`（★ 最终成片）
- 产物：`output/06_final/cover.png`（封面（带描边剧名））
- 产物：`output/06_final/剪辑单.md`（剪辑单（逐镜入出点 + 实测回填））
- 产物：`output/06_final/EP01.srt`（字幕时间轴）
- 产物：`output/06_final/ai_label_notice.txt`（AI 标识留痕）
- 产物：`output/06_final/export_probe.json`（导出参数实测）
- 命令/处理：ffmpeg -f concat -safe 0 -i concat_list.txt -c copy _concat.mp4
- 命令/处理：ffmpeg -i _concat.mp4 -i voice_track.wav -i bgm.wav -filter_complex amix -c:v copy -c:a aac -ar 44100 -ac 2 -metadata comment='AI 辅助制作' EP01.mp4

# 时象助手 · 本地真人漫剧制作 Agent

把「基础材料」变成符合红果短剧上架口径的竖屏真人漫剧成片。全流程在本机跑完，素材不出本机，**每个环节的产物、每条验收规则的实测值、每个镜头的来源都能随时打开核对**。

> 本次交付的是跑通全流程的 demo：一集 73 秒 / 12 镜《代签·签字页》，含成片、封面、逐条验收报告和可交互查验台。

---

## 0. v2 更新：小云雀模式 × drama-skills / shuohao-skills 拼装

v1 的画质瓶颈是**静帧 + Ken Burns 假动**：人物不动、没有表演、6 张源帧派生出 12 镜、硬切忽明忽暗。
v2 按「小云雀短剧 Agent」的四层工作流重做，并把两个开源技能包的确定性机制拼了进来：

| 层 | 落地 | 来源 |
|---|---|---|
| 资产锁定 | `input/<项目>/director.json`：风格锚、4 把连续性锁、场景轴线与工作侧 | 小云雀资产画布 / drama-skills 连续性锁 |
| 导演台预演 | `output/00_previs/previs.md`：12 镜时间线、景别/机位、越轴检查、运动预算 | 小云雀 3D 导演台 / shuohao-skills staging |
| 五份创作文档 | `output/00_creator_docs/`：剧本 / 视觉设定 / 分镜 / 视频提示词 / 剪辑单，SHOT↔MOTION↔CUT 一一对应 | drama-skills |
| 20 条确定性门 | `src/director.py`：时长逐字传播、锁面传播、REF 槽位、对白 4.1 字/秒发声窗口、生产前指纹确认 | drama-skills + shuohao-skills（脚本判定，不靠模型自觉） |
| **逐镜真视频** | `providers.motion = generated_video + local_parallax`：WorkBuddy 的 VideoGen 逐镜图生视频，落到 `input/<项目>/generated_video/Sxx.mp4`，流水线自动检测优先采用 | 小云雀逐镜生成 |
| 逐镜质检 / 重拍 | `output/07_reports/shot_qc.json`：帧间运动量、黑边、字幕、跨镜重复、接镜亮度跳变、音画漂移；`--retake Sxx` 只重拍一镜 | 小云雀片段重拍 + drama-skills 剪辑质检 |
| 接镜匹配 | `providers.match_shot_luma()`：每帧亮度向全片中位数拉近 70%（增益限 0.6–1.6） | drama-skills `SHOT_MATCH_STRENGTH=0.7` |

**实测改进**：接镜亮度最大跳变 58.39 → 11.15，逐镜质检 `6 warn / 6 pass` → `12 pass / 0 warn`，
重拍清单清空；镜头层从单一 zoompan 升级为多层视差 + 可移动前景光带 + 明暗呼吸 + 颗粒 + 暗角 +
逐句字幕时段 + 插入镜闪白 + 末镜淡出；字幕按 12 字自动折行。

> **诚实边界**：本地 `local_parallax` 通道再怎么做也**不是真表演**，画质上限由「有没有真视频片段」决定。
> 真视频通道需要调用 WorkBuddy 的图生视频工具（5 秒约 50–100 积分），必须经生产预览 + 明确确认。
> **本次交付的 demo 为「先试 1 镜」档**：仅 S01 调用了一次图生视频（约 50–100 积分），
> 其余 11 镜为零积分的本地视差通道。查验台与逐镜质检都如实标注每镜通道，绝不把静帧混报成真视频。

### 0.1 S01 真视频试片：实测发现与自动处理

| 实测 | 处理 |
|---|---|
| 模型 `minimax-video-h3` 不允许「首帧 + reference_images」同时用 | 首帧优先，去掉参考图；角色一致性由冻结关键帧与连续性锁文本承担 |
| 模型强制自带音轨，不能 `enable_audio=false` | 不传该参数，`make_clip` 用 `-an` 只取画面，对白仍由本地 TTS 统一合成 |
| 输出 768×1344 / 24fps / 6.58s，非交付规格 | 流水线 `scale/crop/fps/tpad/trim` 规整到 1080×1920@30fps 并裁到 6s |
| 输出带左上角「AI生成」第三方水印 | `comicify_video()` 顶部裁 7.5% 去除；片头保留项目自己的「AI 辅助制作」标识 |
| **输出是真人实拍质感，与全片漫画风不一致** | 逐帧送进与其余镜头完全相同的 `comicify()` LUT，统一平涂/描线/网点/冷青灰，并对齐全片亮度中位数（70% 接镜匹配）。约 15 秒 / 6 秒片段，全程本地、零额外费用 |

试片结果：S01 帧间运动量 **8.92**（本地镜 1.86–5.49），是真正的镜头推进与人物抬头；
抽帧复核画风与 S02 连贯、无水印、无黑边、手部五官正常。
证据：`output/00_previs/production_preview_S01.md`（单镜预览与确认）、
`output/04_clips/clip_render_log.json` 的 `comicify` 字段、
`output/07_reports/v2_preview/gen_S01_*.png`（原片）与 `comic_S01_*.png`（转绘后）对比。

> 生成模型自行把 S01 从「过肩手部拍纸」演到了「人物侧脸」，与分镜的「唯一动作」有偏差。
> 这正是**逐镜人工验收**存在的意义：脚本只测客观指标，动作是否符合导演意图由人看片段决定，
> 不满意就替换 `input/demo/generated_video/S01.mp4` 后跑 `--retake S01 --from 04_clips`。

**WorkBuddy 技能包**：已安装到 `~/.workbuddy/skills/shixiang-director/`，在对话里说
「时象助手 / 真人漫剧 / 小云雀模式 / 重拍某镜」即可由 WorkBuddy 驱动整条流程。
参考实现源码在 `vendor/drama-skills/` 与 `vendor/shuohao-skills/`（只读，不 import、不绑定供应商）。

```bash
# 零费用导演台（不调任何模型）
python3 src/director.py --action prepare     # 五份文档 + 预演 + 生产预览
python3 src/director.py --action check       # 20 条门
# 人阅读 output/00_previs/production_preview.md 并确认后
python3 src/director.py --action confirm --token "CONFIRM <job_id> <fp前12位>"
# WorkBuddy 逐镜生成 → 重命名为 Sxx.mp4 → 跑流水线
python3 src/pipeline.py --input input/demo --auto-approve
# 只重拍一镜
python3 src/pipeline.py --input input/demo --retake S05 --from 04_clips
```

---

## 1. 三条设计原则

| 原则 | 落地方式 |
|---|---|
| **本地优先** | 转绘用 OpenCV、动效/合成/字幕用本地 ffmpeg、配音用 macOS 离线 `say`、BGM/音效用 numpy 合成。素材、中间产物、成片全在 `output/`，不上传第三方。 |
| **可查验** | 每环节写「产物文件 + 结构化记录」，`output/status.json` 是唯一数据源。32 条红果规则逐条给出 `期望 / 实测 / 证据路径 / 依据来源 / 人工核验方式 / 修复建议`。 |
| **人可随时介入** | 5 道人工确认门。默认模式跑到门就暂停，等人查验；`output/gates.json` 里写 `approved` 或 `rejected` + 意见即可放行/打回，再用 `--from` 重跑该环节。 |

**关于"符合"的诚实口径**：画面级、法律效力级判定（画风一致性、参考图授权、AIGC 隐式标识、音画口型等）机器不能替人下结论，一律标 `warn / 需人工核验`，**不写死通过**。所以综合状态通常是 `WARN`，这不是缺陷，而是把"哪些已经机检通过、哪些必须人看"分得清清楚楚。

---

## 2. 快速开始

```bash
cd /Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent

# 无人值守跑通全流程（人工门自动通过，但会标注"仍需人工复核"）
python3 src/pipeline.py --input input/demo --auto-approve

# 人机协同：在每道门暂停，等人查验后继续
python3 src/pipeline.py --input input/demo
#   编辑 output/gates.json 把 G1 改成 approved
python3 src/pipeline.py --from 01_script

# 只重跑某一环节（例如换了新的真人参考帧）
python3 src/pipeline.py --only 03_frames
```

依赖：Python 3.10+、`opencv-python`、`numpy`、`Pillow`、ffmpeg（本机无系统 ffmpeg 时自动用 `imageio-ffmpeg` 静态二进制）、macOS `say`。首次运行会自动把系统中文字体复制到 `config/font.ttc`。

**打开查验台**：直接双击 `console/index.html` 即可。流水线每完成一个环节都会同步写 `console/data.js`（本机真实数据快照，`<script src>` 不受 `file://` 的跨域限制），所以双击打开看到的就是真实进度与真实证据，不是演示假数据。

需要读取最新状态或启用自动轮询时，起个本地服务：

```bash
python3 -m http.server 8000
# 浏览器打开 http://localhost:8000/console/
```

---

## 3. 换成你自己的基础材料

把新材料放进 `input/<你的项目名>/`，保持三个文件（格式见 `SPEC.md` 第 2 节）：

```
input/我的剧/
├── script.md          人可读剧本
├── characters.json    角色卡（每个角色 ≥3 条刚性锚点 + 本机可用音色）
├── storyboard.json    分镜（镜号/时长/景别/运镜/画面提示词/台词/字幕/音效）
└── frames/            真人实拍参考帧，命名 S01.jpg、S02.jpg …（可选）
```

```bash
python3 src/pipeline.py --input input/我的剧
```

- `frames/` 里**缺哪镜就自动用本地程序化渲染兜底**，不会中断，但会在 `frame_sources.csv` 里如实标注该镜无真人源帧。
- 来源帧自带水印时，本地转绘会裁掉底部 8.5%（`config/project.json` 可调），并在证据链里记录。
- 想换音色：`say -v '?' | grep zh_CN` 查本机可用音色，改 `characters.json` 的 `voice`。
- 想调画风：改 `config/project.json` 的 `comicify`（色阶数、描线强度、饱和度、冷调 LUT、网点、暗角），然后 `--only 03_frames`。

---

## 4. 验收标准怎么来的

`config/hongguo_rules.json` 共 **32 条**，由规范官 Agent 联网调研后编码，四类：技术规格 12 / 内容合规 10 / 版权留痕 5 / 音画质量 5。每条带来源名称与链接，并区分「硬规-法规」「平台公告」「硬规-上传口径」「行业建议」「风险自查」。

调研中做了几处纠正，避免把网传说法当成官方标准：

- 网传「3 类禁拍 13 类受限」清单，红果 2026-06 已向媒体否认发布过该标准，已降级为风险自查；内容硬规改用广电总局令第 16 号 §25。
- AI 标识的法规措辞是**每集明显位置**加提示标识（§34）+ 网信办《标识办法》显式/隐式双标识；"片头标 AI 辅助制作"只是平台执行口径。
- 「首次投稿总时长 >20 分钟」仅见第三方资料、未见官方确认，已标存疑；官方只确认连载首次上传 ≥3 集。
- 封面 `350×500` 与版权中台 `3:4 建议 1200×1600` 两个口径冲突，已并列标注。

`src/compliance.py` 用 `ffmpeg -i` 的 stderr 正则实测成片参数（本机无 ffprobe），逐条计算，单条异常隔离不中断。

---

## 5. 多 Agent 分工

| 角色 | 交付 |
|---|---|
| 制片 / 编剧 Agent | 示例剧本、角色卡、12 镜结构化分镜（前 3 秒钩子、结尾悬念、台词 ≤24 字） |
| 规范官 Agent | 32 条红果规则集 + 21 个检查器 + 合规执行器与评分 |
| 查验台工程师 Agent | `console/index.html`：总览 / 7 段时间线 / 规则明细 / 镜头墙 / 人工门 / 离线容错 |
| 集成方（主线） | `SPEC.md` 数据契约、`providers.py` 能力层、`gates.py` 人工门、`pipeline.py` 七段流水线、成片与报告 |

七段流水线：`01_script` 剧本预审 → `02_characters` 角色锁定 → `03_frames` 真人转绘 → `04_clips` 微动效+烧字幕 → `05_audio` 离线配音/BGM/音效 → `06_final` 拼接导出+封面 → `07_reports` 逐条验收。

---

## 6. 本机适配与升级路径

本机是 **Apple M5 / arm64，无 NVIDIA CUDA**，跑不了 ComfyUI + SDXL 那套，因此默认用轻量本地实现。能力层在 `providers.py` 里是可插拔的，换实现不动流水线：

| 能力 | 当前（本机） | 有 N 卡 / 追求商用画质时 |
|---|---|---|
| 真人转绘 | OpenCV 双边滤波+色阶量化+自适应描线+网点+统一 LUT | `comfyui_v2v`：ControlNet lineart / IP-Adapter FaceID 锁五官 |
| 动态化 | ffmpeg `zoompan` 缓推缓拉 | AnimateDiff / Wan2.2 图生视频、Wav2Lip 对口型 |
| 配音 | macOS `say` 离线中文 | Qwen3-TTS / CosyVoice 本地服务，多情绪多角色 |
| 角色一致性 | 统一风格底图 + 逐镜刚性锚点描述 + 同一 LUT | LoRA 角色 + StoryDiffusion 时序连贯约束 |
| 音乐音效 | numpy 本地合成，无版权风险 | 授权素材库 / AI 音效生成 |

---

## 7. 正式投稿前必须处理（demo 的已知限制）

1. **替换示例素材**：`input/demo/frames/` 是本地图像生成模型产出的演示参考帧，仅用于跑通流程；授权状态见 `output/07_reports/asset_licenses.csv`。正式投稿请换成自有实拍或已授权素材，并留存授权凭证。
2. **画面复用**：示例只有 6 张真人源帧，另 6 镜由同一风格底图派生不同景别（逐镜来源见 `output/03_frames/frame_sources.csv`）。真实项目应每镜独立给源帧。
3. **人工核验项**：报告里标 `warn` 的条目要人逐条看过再勾，尤其是画风一致性、无水印黑边、音画口型、AIGC 隐式标识、参考图授权。
4. **签署声明**：`output/07_reports/originality_declaration.md` 是模板，需填写作者信息并签字。
5. **字体商用授权**：`config/font.ttc` 来自 macOS 系统字体，正式商用请核对字体授权或更换为可商用字体。
6. **集数**：连载首次上传至少 3 集；本 demo 只做了第 1 集。
7. **审核留痕**：投稿时把 `output/07_reports/` 整目录（创作链路、生成参数、素材台账、工程文件）一起提交。

---

## 8. 目录速查

```
config/project.json              制作参数（画幅/帧率/码率/音色/转绘参数）
config/hongguo_rules.json        32 条红果验收规则
input/demo/                     示例基础材料（替换这里）
output/status.json              ★ 查验台数据源
output/01_script/               剧本、分镜、合规预审记录
output/02_characters/           角色卡、一致性报告、统一风格底图
output/03_frames/               12 张转绘帧 + frame_sources.csv 来源台账
output/04_clips/                12 个镜头片段 + 渲染日志
output/05_audio/                逐镜配音、全片人声轨、BGM、audio_sync.json
output/06_final/                ★ EP01.mp4、cover.png、字幕、AI 标识留痕
output/07_reports/              ★ 验收报告、创作链路、参数、素材台账、原创声明
output/gates.json               人工确认门（可编辑）
console/index.html              ★ 查验台
SPEC.md                         全系统数据契约
```
# Multi-agent-local-video-editing
# Multi-agent-local-video-editing
# Multi-agent-local-video-editing

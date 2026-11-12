# 时象助手 · 本地真人漫剧制作 Agent — 系统契约 v1.0

> 目标：把"基础材料"变成符合红果短剧上架规范的竖屏真人漫剧成片，全过程**本地运行、逐环节留痕、人可随时查验并介入**。
> 本文件是所有协作 Agent 的唯一数据契约，任何产出不得擅自改字段。

## 0. 不可妥协的三条原则

1. **本地优先**：素材、中间产物、成片全部落在本机 `output/`；不上传第三方服务。能力层可插拔，默认使用本机无需 GPU 的实现。
2. **可查验**：流水线的每个 stage 都必须写出「产物文件 + 结构化检查记录」；任何一条不符合红果规则，都能定位到**具体镜头 / 具体文件 / 具体规则 / 具体实测值**。
3. **人可随时介入**：设置人工确认门（Human Gate）。默认模式在 gate 处暂停等人确认；`--auto-approve` 仅供无人值守演示。人可驳回任一环节并附意见，流水线据此重跑该环节。

## 1. 目录结构

```
shixiang-agent/
├── SPEC.md                     # 本契约
├── README.md                   # 使用说明（集成方产出）
├── config/
│   ├── project.json            # 制作参数（画幅/帧率/编码/TTS 音色）
│   └── hongguo_rules.json      # 红果验收规则集（规范官产出）
├── input/
│   └── demo/                   # 示例基础材料（替换此目录即可换素材）
│       ├── script.md
│       ├── characters.json
│       ├── storyboard.json
│       └── frames/             # 真人原始帧（可选，缺省由本地渲染生成）
├── src/
│   ├── pipeline.py             # 主流水线（集成方）
│   ├── providers.py            # 可插拔能力层（集成方）
│   ├── compliance.py           # 规则执行器（规范官）
│   └── gates.py                # 人工确认门（集成方）
├── output/
│   ├── status.json             # ★ 查验台唯一数据源（流水线生成）
│   ├── 01_script/  02_characters/  03_frames/  04_clips/
│   ├── 05_audio/   06_final/       07_reports/
└── console/
    └── index.html              # 查验台（查验台工程师产出，纯前端、双击可开）
```

## 2. 输入契约

### 2.1 `input/<项目名>/storyboard.json`（必需）

```json
{
  "episode": {
    "id": "EP01",
    "title": "剧名",
    "duration_target_s": 75,
    "genre": "都市悬疑",
    "logline": "一句话梗概",
    "hook_3s": "前3秒冲突"
  },
  "style": {
    "name": "写实国漫 · 电影感",
    "prompt_prefix": "统一画风前缀",
    "negative_prompt": "畸形手,变形五官,模糊,水印"
  },
  "shots": [
    {
      "id": "S01",
      "duration_s": 5.0,
      "shot_size": "特写",
      "camera": "缓推",
      "characters": ["林昭"],
      "visual_prompt": "画面描述，用于生成/检索真人原帧",
      "dialogue": { "speaker": "林昭", "text": "台词", "emotion": "压低声音" },
      "sfx": ["心跳声"],
      "subtitle": "字幕文本（可与台词一致）",
      "source_frame": "frames/S01.jpg"
    }
  ]
}
```

字段约束：`shots[].id` 唯一且形如 `S\d{2}`；`duration_s` 3~8；整集镜头数 ≥ 8；`dialogue.text` 单句 ≤ 24 字（红果漫剧台词宜短）。
`source_frame` 指向相对 `input/<项目名>/` 的路径；文件不存在时流水线走本地程序化渲染，不报错。

### 2.2 `characters.json`

```json
{ "characters": [
  { "name": "林昭", "role": "男主", "voice": "Eddy",
    "appearance": "黑色短发,锐利眼神,深灰风衣",
    "identity_anchors": ["左眉一道细疤", "银色耳钉", "深灰风衣立领"],
    "reference_images": [] }
] }
```

`identity_anchors` 至少 3 条，用于跨镜角色一致性校验（红果对"角色变脸/跨剧撞脸"有硬性驳回）。
`voice` 必须是本机 `say -v '?'` 中存在的音色名。

### 2.3 `script.md`
人可读剧本，含场景、人物、动作、台词；流水线会原样归档到 `output/01_script/`。

## 3. 输出契约

### 3.1 `output/status.json` ★（查验台唯一数据源，集成方生成）

```json
{
  "schema_version": "1.0",
  "project": "时象助手 · 本地真人漫剧制作 Agent",
  "episode_title": "剧名",
  "run_id": "20261112-183500",
  "generated_at": "2026-11-12T18:35:00+08:00",
  "mode": "demo",
  "overall": {
    "status": "PASS",
    "score": 94,
    "total": 26, "passed": 24, "warned": 2, "failed": 0,
    "blocker_failed": 0
  },
  "stages": [
    {
      "id": "01_script", "name": "剧本与合规预审", "owner": "制片 Agent",
      "status": "pass", "duration_s": 1.2, "summary": "12 镜，总时长 72s",
      "artifacts": [
        { "label": "分镜脚本", "path": "output/01_script/storyboard.json", "type": "json" }
      ],
      "checks": ["C01", "C02"],
      "gate": { "id": "G1", "status": "approved", "note": "", "reviewer": "人工" }
    }
  ],
  "checks": [
    {
      "id": "C01", "rule_id": "HG-TECH-01", "stage": "06_final",
      "name": "竖屏画幅 1080×1920", "category": "技术规格",
      "severity": "blocker", "status": "pass",
      "expected": "1080x1920", "actual": "1080x1920",
      "evidence": "output/06_final/EP01.mp4",
      "source": "红果短剧漫剧上传规范",
      "how_to_verify": "双击成片查看，或 ffmpeg -i 查看 Stream 信息",
      "fix_hint": "在 config/project.json 调整 width/height 后重跑 06_final"
    }
  ],
  "shots": [
    {
      "id": "S01", "duration_s": 5.0, "status": "pass",
      "frame": "output/03_frames/S01.png",
      "clip": "output/04_clips/S01.mp4",
      "audio": "output/05_audio/S01.aiff",
      "subtitle": "字幕文本", "issues": []
    }
  ],
  "human_gates": [
    { "id": "G1", "stage": "01_script", "name": "剧本与分镜确认",
      "status": "approved", "note": "", "how_to_verify": "打开 output/01_script/script.md",
      "reject_action": "修改 input/demo/storyboard.json 后执行 pipeline.py --from 01_script" }
  ],
  "final_video": "output/06_final/EP01.mp4",
  "report_md": "output/07_reports/compliance_report.md"
}
```

枚举：`status` ∈ `pass|warn|fail|skipped`；`severity` ∈ `blocker|major|minor`；
`gate.status` ∈ `approved|pending|rejected`。
**所有 path 均为相对项目根目录的相对路径**，查验台优先用 `fetch()` 读取；为兼容 `file://`，流水线每次写 status.json 时**同步写 `console/data.js`**（本机真实数据快照，`<script src>` 不受 CORS 限制），查验台在 fetch 失败时优先载入该真实快照并标注「本机快照」，同时保留「选择 status.json 文件」手动载入能力；内嵌演示数据仅在快照也不存在时作最后兜底，且必须显著标注「非真实产物，不能作为验收依据」。

### 3.2 `config/hongguo_rules.json`（规范官产出）

```json
{
  "version": "2026-11",
  "source_notes": "红果短剧/抖音集团短剧版权中心 漫剧上架与审核要求（公开资料整理，非官方合同附件）",
  "rules": [
    {
      "id": "HG-TECH-01", "category": "技术规格", "name": "竖屏 9:16 1080×1920",
      "severity": "blocker", "expected": "1080x1920",
      "check": "video_resolution",
      "source": "...来源名称与链接...",
      "how_to_verify": "人工核验方式",
      "fix_hint": "不合规时怎么改"
    }
  ]
}
```

`check` 必须是 `src/compliance.py` 中实现过的检查器 key，未实现的标 `manual`。
规则须覆盖：技术规格（画幅/编码/帧率/码率/音频/时长/容器）、内容合规（题材红线/AI 标识/角色一致性/画风统一）、版权留痕（创作链路截图/原创声明/参考图授权记录）、音画质量（音画同步/字幕/无水印黑边）。

### 3.3 `src/compliance.py` 接口（规范官产出）

```python
def run(project_root: str, status: dict) -> dict:
    """读取 config/hongguo_rules.json 与 output/status.json，逐条执行规则，
    就地补全 status['checks']、status['overall']，返回 status。
    不得抛异常到流水线；单条规则失败记为 fail 并写明原因。"""
```

同时提供 `check_video(video_path, ffmpeg_bin) -> dict`，返回
`{width,height,codec,fps,bitrate_kbps,audio_codec,sample_rate,channels,duration_s,container}`。

## 4. 流水线 Stage 与人工门

| stage | 名称 | 负责 Agent | 主要产物 | 门 |
|---|---|---|---|---|
| 01_script | 剧本与合规预审 | 制片 | script.md / storyboard.json / 预审记录 | G1 |
| 02_characters | 角色资产与一致性锁定 | 美术 | character_sheets/ / 角色卡 / 一致性报告 | G2 |
| 03_frames | 真人帧 → 漫画化转绘 | 转绘 | 每镜 PNG 1080×1920 | G3 |
| 04_clips | 微动效镜头生成 | 动画 | 每镜 MP4 | — |
| 05_audio | 本地配音/BGM/音效 | 声音 | 每镜 AIFF + 总轨 | G4 |
| 06_final | 字幕/合成/导出 | 剪辑 | EP01.mp4 | — |
| 07_reports | 逐条验收 + 报告 | 质检 | compliance_report.md / status.json | G5 终审 |

门语义：`pending` → 流水线暂停；`approved` → 继续；`rejected` → 该 stage 重跑。
`--auto-approve` 时所有门自动置 `approved` 并在 note 标注「演示模式自动通过，仍需人工复核」。

## 5. 能力层（providers.py）可插拔约定

同一能力多种实现，按 `config/project.json` 的 `providers` 选择；缺失时自动降级并**在 status 中记录降级原因**（不得静默）。

| 能力 | 默认实现（本机 Apple M5 / 无 CUDA） | 可选实现 |
|---|---|---|
| 画面生成 | `procedural`：本地 PIL/OpenCV 程序化绘制 + 真人帧漫画化滤镜 | `imagegen`（离线生成的素材落盘）、`comfyui`（NVIDIA + SDXL/IP-Adapter/ControlNet） |
| 真人转绘 | 本地 `comicify`：双边滤波 + 色阶量化 + 边缘描线 + 网点 + 调色 | `comfyui_v2v` / `controlnet_lineart` |
| 动态化 | `kenburns`：ffmpeg zoompan 缓推/缓拉 + 轻微呼吸 | AnimateDiff / Wan2.2 / 图生视频 |
| 配音 | `macos_say`：本机 `say -v <音色>`，纯离线 | Qwen3-TTS / CosyVoice 本地服务 |
| 音乐音效 | `local_synth`：ffmpeg lavfi / numpy 合成 | 授权素材库 |
| 字幕 | `drawtext` 烧字幕（本地字体） | 剪映工程 |

**真人漫剧定义**：以真人实拍/真人参考帧为源，经本地漫画化转绘形成统一国漫风格，再叠加微动效、配音、字幕、音效做成竖屏短剧；不是纯文生图漫剧，也不是真人实拍原片。

## 6. 红果硬指标基线（规范官需核实并细化，集成方用于 config/project.json）

- 画幅 9:16，1080×1920；MP4 / H.264；帧率 25 或 30fps
- 音频 AAC，44100Hz，双声道；视频码率建议 8~12Mbps（不低于 4Mbps）
- 单集 60~120s 为佳（上传口径 1~5 分钟）；首次投稿至少 3 集、总时长 > 20 分钟
- 无水印、无黑边、无 alpha 通道、分辨率非奇数
- 片头标注「AI 辅助制作」；内嵌字幕（白字黑描边，思源黑体/微软雅黑级别）
- 创作链路留痕：剧本记录、分镜 JSON、生成参数、工程文件、参考图授权状态
- 内容红线：灵异迷信、猎奇、超自然金手指、以暴制暴、畸形婚恋等受限题材
- 角色五官跨镜一致、全剧画风统一；跨剧角色面部相似度过高会被驳回

---

## 7. v2 契约增量（小云雀模式 × 开源技能拼装）

以下为 v2 新增，**不改动第 1–3 节已有字段**，旧材料可直接继续跑。

### 7.1 新增输入 `input/<项目>/director.json`

| 字段 | 说明 |
|---|---|
| `mode` | `xiaoyunque` |
| `style_anchor` | `name` / `surface`（提示词语种最小短语）/ `surface_en` / `palette` / `negative` |
| `continuity_locks[]` | `id` / `name` / `surface` / `surface_en` / `scope`（生效镜号数组）/ `reason` |
| `scene_geometry` | `axis` / `camera_working_side` / `note` |
| `shots[]` | `id` / `purpose` / `start` / `action` / `end` / `screen_direction` / `axis_side` / `motion_intensity` / `camera_move_pct` / `subtitle_window_s` / `video_prompt` / `references[]` / 可选 `axis_transition` |
| `references[]` | `slot`（REF-*）/ `order`（1..N 连续）/ `path`（项目内真实文件）/ `name` / `purpose`（9 值闭集）/ `controls` / `must_not`（与控制域互斥） |

### 7.2 新增输入 `input/<项目>/generated_video/Sxx.mp4`

可选。存在即由 `04_clips` 采用真视频通道；缺失或小于 10KB 时自动回落本地视差通道。
逐镜通道来源写入 `output/04_clips/channel_map.json` 与 `clip_render_log.json`，可随时查验，绝不混报。

**真视频必须经本地转绘层**：`config.comicify_generated_video=true` 时，
`providers.comicify_video()` 逐帧执行「顶部裁 `generated_video_watermark_crop_top_ratio`（默认 0.075）
去模型水印 → 9:16 居中 → 与其余镜头相同的 `comicify()` LUT → 对齐全片亮度中位数」，
产出 `output/04_clips/_comic_<Sxx>.mp4` 再进合成。原因是图生视频模型实测输出真人实拍质感
且自带「AI生成」水印，直接拼接会造成画风断裂与第三方水印，两者都是红果驳回项。
`clip_render_log.json` 的 `comicify` 字段记录帧数、fps、裁切比例、亮度增益与执行结果。

单镜试片另产出 `output/00_previs/production_preview_S01.md`、
`production_jobs_S01.json`，并在 `confirmation.json.executions[]` 追加本次投产范围与依据。

### 7.3 `status.json` 新增字段

| 字段 | 结构 | 用途 |
|---|---|---|
| `director_gates` | `{summary:{status,score,total,passed,warned,failed,blocker_failed}, gates:[{id,name,level,status,actual,expected,evidence,fix_hint}]}` | 20 条确定性质量门 |
| `previs` | `{path,shot_count,total_duration_s,avg_shot_s,motion_budget,production_jobs,fingerprint}` | 导演台预演摘要 |
| `shot_qc` | `{summary:{pass,warn,fail,generated_video_shots,local_parallax_shots,retake_list}, shots:[{shot_id,channel,status,metrics,issues,retake_hint,evidence,how_to_verify}]}` | 逐镜质检与重拍清单 |
| `notes[]` | 字符串数组 | 演示模式代写确认等需明示的例外 |

`stages[]` 由 7 个增至 **8 个**，新增 `00_previs`（导演 Agent，无人工门）；
`04_clips` 更名为「逐镜生产（真视频/视差）」，`07_reports` 更名为「逐镜质检 + 逐条验收」。

### 7.4 新增产物

```
output/00_creator_docs/  剧本.md 视觉设定.md 分镜.md 视频提示词.md 剪辑单.md
output/00_previs/        previs.md previs.json production_preview.md
                         production_jobs.json director_gates.json CONFIRM
output/03_frames/        luma_match.json（跨镜接镜亮度匹配 70%）
output/04_clips/         channel_map.json（逐镜真视频/本地视差来源）
output/06_final/         剪辑单.md（含成片实测回填）
output/07_reports/       shot_qc.json qc_frames/（逐镜抽帧证据）
```

### 7.5 生产四步硬闸门

`prepare`（只出预览与指纹，绝不调模型）→ `preview`（把任务数/积分/提示词/参考/输出报给人）
→ `confirm`（`CONFIRM <job_id> <fingerprint[:12]>` 精确令牌）→ `run`（才允许调用生成接口）。
指纹由 prompt/参考/参数/输出共同哈希，任一变化旧确认失效。
`--auto-approve` 只在演示模式代写确认，并在 `notes` 留痕，不冒充人工签署。

### 7.6 命令增量

```
python3 src/director.py --action prepare|check|confirm [--token ...]
python3 src/pipeline.py --confirm [--token ...]
python3 src/pipeline.py --retake S05,S09 --from 04_clips
python3 ~/.workbuddy/skills/shixiang-director/scripts/check_project.py --gates
```

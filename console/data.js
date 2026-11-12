/* 由 pipeline.py 自动生成：本机真实查验数据快照，勿手工编辑 */
window.__SHIXIANG_STATUS__ = {
  "schema_version": "1.0",
  "project": "时象助手 · 本地真人漫剧制作 Agent",
  "episode_title": "代签",
  "episode_id": "EP01",
  "run_id": "20261112-202104",
  "generated_at": "2026-11-12T20:21:32+08:00",
  "mode": "demo",
  "ffmpeg_bin": "/Users/xujiahua/.local/lib/python3.13/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v9.0",
  "input_dir": "input/demo",
  "config": {
    "width": 1080,
    "height": 1920,
    "fps": 30,
    "providers": {
      "frame": "local_comicify",
      "motion": "generated_video+local_parallax",
      "tts": "macos_say",
      "music": "local_synth",
      "subtitle": "drawtext"
    }
  },
  "overall": {
    "status": "WARN",
    "score": 75,
    "total": 32,
    "passed": 16,
    "warned": 16,
    "failed": 0,
    "blocker_failed": 0
  },
  "stages": [
    {
      "id": "00_previs",
      "name": "导演台预演与质量门",
      "owner": "导演 Agent",
      "status": "pass",
      "duration_s": 0.13,
      "summary": "12 镜预演 / 集长 73.0s / 运动预算 固定4镜；质量门 20通过 0待确认 0不通过；生产任务 12 镜待明确确认（指纹 c69345c89071）",
      "artifacts": [
        {
          "label": "导演台预演表",
          "path": "output/00_previs/previs.md",
          "type": "text"
        },
        {
          "label": "预演数据（轴线/运动预算/时间线）",
          "path": "output/00_previs/previs.json",
          "type": "json"
        },
        {
          "label": "生产预览（未确认不产生费用）",
          "path": "output/00_previs/production_preview.md",
          "type": "text"
        },
        {
          "label": "生产任务与指纹",
          "path": "output/00_previs/production_jobs.json",
          "type": "json"
        },
        {
          "label": "20 条确定性质量门结果",
          "path": "output/00_previs/director_gates.json",
          "type": "json"
        },
        {
          "label": "创作文档 · 剧本.md",
          "path": "output/00_creator_docs/剧本.md",
          "type": "text"
        },
        {
          "label": "创作文档 · 视觉设定.md",
          "path": "output/00_creator_docs/视觉设定.md",
          "type": "text"
        },
        {
          "label": "创作文档 · 分镜.md",
          "path": "output/00_creator_docs/分镜.md",
          "type": "text"
        },
        {
          "label": "创作文档 · 视频提示词.md",
          "path": "output/00_creator_docs/视频提示词.md",
          "type": "text"
        },
        {
          "label": "创作文档 · 剪辑单.md",
          "path": "output/00_creator_docs/剪辑单.md",
          "type": "text"
        }
      ],
      "checks": [],
      "commands": [
        "director.build_creator_docs() → 五份创作文档（含连续性锁与 REF 槽位）",
        "director.previsualize() → 整组镜头时间线 / 轴线 / 运动预算",
        "director.production_preview() → 只出预览与指纹，绝不调用生成接口",
        "director.run_gates() → 20 条纯字符串/数值门，不调模型"
      ]
    },
    {
      "id": "01_script",
      "name": "剧本与合规预审",
      "owner": "制片 Agent",
      "status": "pass",
      "duration_s": 0.03,
      "summary": "12 镜 / 73.0s；前3秒钩子已配置；题材红线扫描 0 项命中；超长台词 0 条",
      "artifacts": [
        {
          "label": "人可读剧本",
          "path": "output/01_script/script.md",
          "type": "text"
        },
        {
          "label": "结构化分镜",
          "path": "output/01_script/storyboard.json",
          "type": "json"
        },
        {
          "label": "合规预审记录",
          "path": "output/01_script/precheck.json",
          "type": "json"
        }
      ],
      "checks": [
        "C14",
        "C15",
        "C16",
        "C20",
        "C21",
        "C22"
      ],
      "commands": [
        "copy script.md / storyboard.json → output/01_script/",
        "题材红线关键词扫描 + 台词长度 + 画风锁定校验"
      ],
      "gate": {
        "id": "G1",
        "status": "approved",
        "note": "演示模式自动通过，仍需人工复核",
        "reviewer": "auto-approve（待人工复核）"
      }
    },
    {
      "id": "02_characters",
      "name": "角色资产与一致性锁定",
      "owner": "美术 Agent",
      "status": "pass",
      "duration_s": 0.5,
      "summary": "2 个角色；锚点最少 4 条；本机音色全部可用 True",
      "artifacts": [
        {
          "label": "角色卡",
          "path": "output/02_characters/characters.json",
          "type": "json"
        },
        {
          "label": "一致性报告",
          "path": "output/02_characters/consistency_report.json",
          "type": "json"
        },
        {
          "label": "林昭 定妆卡",
          "path": "output/02_characters/character_sheets/1_林昭.png",
          "type": "image"
        },
        {
          "label": "苏晴 定妆卡",
          "path": "output/02_characters/character_sheets/2_苏晴.png",
          "type": "image"
        }
      ],
      "checks": [
        "C17",
        "C19"
      ],
      "commands": [
        "say -v ? 校验本机音色",
        "逐角色生成定妆卡 PNG 与一致性报告"
      ],
      "gate": {
        "id": "G2",
        "status": "approved",
        "note": "演示模式自动通过，仍需人工复核",
        "reviewer": "auto-approve（待人工复核）"
      }
    },
    {
      "id": "03_frames",
      "name": "真人帧 → 漫画化转绘",
      "owner": "转绘 Agent",
      "status": "pass",
      "duration_s": 6.93,
      "summary": "12 帧 1080×1920；6 张真人源帧转绘 + 6 张同风格派生；水印已本地裁切；跨镜亮度向中位数 71.78 拉近 70%",
      "artifacts": [
        {
          "label": "逐镜来源与处理链",
          "path": "output/03_frames/frame_sources.csv",
          "type": "csv"
        },
        {
          "label": "帧清单（JSON）",
          "path": "output/03_frames/frame_manifest.json",
          "type": "json"
        },
        {
          "label": "跨镜接镜亮度匹配（70%）",
          "path": "output/03_frames/luma_match.json",
          "type": "json"
        },
        {
          "label": "统一风格底图目录",
          "path": "output/02_characters/style_base/",
          "type": "dir"
        },
        {
          "label": "S01 转绘帧",
          "path": "output/03_frames/S01.png",
          "type": "image"
        },
        {
          "label": "S02 转绘帧",
          "path": "output/03_frames/S02.png",
          "type": "image"
        },
        {
          "label": "S03 转绘帧",
          "path": "output/03_frames/S03.png",
          "type": "image"
        },
        {
          "label": "S04 转绘帧",
          "path": "output/03_frames/S04.png",
          "type": "image"
        },
        {
          "label": "S05 转绘帧",
          "path": "output/03_frames/S05.png",
          "type": "image"
        },
        {
          "label": "S06 转绘帧",
          "path": "output/03_frames/S06.png",
          "type": "image"
        },
        {
          "label": "S07 转绘帧",
          "path": "output/03_frames/S07.png",
          "type": "image"
        },
        {
          "label": "S08 转绘帧",
          "path": "output/03_frames/S08.png",
          "type": "image"
        },
        {
          "label": "S09 转绘帧",
          "path": "output/03_frames/S09.png",
          "type": "image"
        },
        {
          "label": "S10 转绘帧",
          "path": "output/03_frames/S10.png",
          "type": "image"
        },
        {
          "label": "S11 转绘帧",
          "path": "output/03_frames/S11.png",
          "type": "image"
        },
        {
          "label": "S12 转绘帧",
          "path": "output/03_frames/S12.png",
          "type": "image"
        }
      ],
      "checks": [
        "C18",
        "C29",
        "C30"
      ],
      "commands": [
        "去水印裁切 → 9:16 居中裁切 → 双边滤波/色阶量化/自适应描线/网点/统一冷调LUT/暗角",
        "按 DERIVE_MAP 派生不同景别，逐镜写入 frame_sources.csv",
        "match_shot_luma(strength=0.7)：增益限 0.6–1.6，消除硬切亮度跳变"
      ],
      "gate": {
        "id": "G3",
        "status": "approved",
        "note": "演示模式自动通过，仍需人工复核",
        "reviewer": "auto-approve（待人工复核）"
      }
    },
    {
      "id": "04_clips",
      "name": "逐镜生产（真视频/视差）",
      "owner": "动画 Agent",
      "status": "pass",
      "duration_s": 16.32,
      "summary": "12/12 镜头；真动态视频 1 镜（逐帧本地转绘、去模型水印、对齐全片 LUT） / 本地多层视差 11 镜；逐句字幕时段 + 插入镜闪白 + 片头 AI 标识 + 末镜淡出",
      "artifacts": [
        {
          "label": "逐镜生产日志（含通道与来源）",
          "path": "output/04_clips/clip_render_log.json",
          "type": "json"
        },
        {
          "label": "逐镜通道映射",
          "path": "output/04_clips/channel_map.json",
          "type": "json"
        },
        {
          "label": "S01 镜头片段 · generated_video",
          "path": "output/04_clips/S01.mp4",
          "type": "video"
        },
        {
          "label": "S02 镜头片段 · unchanged",
          "path": "output/04_clips/S02.mp4",
          "type": "video"
        },
        {
          "label": "S03 镜头片段 · unchanged",
          "path": "output/04_clips/S03.mp4",
          "type": "video"
        },
        {
          "label": "S04 镜头片段 · unchanged",
          "path": "output/04_clips/S04.mp4",
          "type": "video"
        },
        {
          "label": "S05 镜头片段 · unchanged",
          "path": "output/04_clips/S05.mp4",
          "type": "video"
        },
        {
          "label": "S06 镜头片段 · unchanged",
          "path": "output/04_clips/S06.mp4",
          "type": "video"
        },
        {
          "label": "S07 镜头片段 · unchanged",
          "path": "output/04_clips/S07.mp4",
          "type": "video"
        },
        {
          "label": "S08 镜头片段 · unchanged",
          "path": "output/04_clips/S08.mp4",
          "type": "video"
        },
        {
          "label": "S09 镜头片段 · unchanged",
          "path": "output/04_clips/S09.mp4",
          "type": "video"
        },
        {
          "label": "S10 镜头片段 · unchanged",
          "path": "output/04_clips/S10.mp4",
          "type": "video"
        },
        {
          "label": "S11 镜头片段 · unchanged",
          "path": "output/04_clips/S11.mp4",
          "type": "video"
        },
        {
          "label": "S12 镜头片段 · unchanged",
          "path": "output/04_clips/S12.mp4",
          "type": "video"
        }
      ],
      "checks": [],
      "commands": [
        "真视频通道：ffmpeg -i generated_video/<Sxx>.mp4 -filter_complex scale/crop/fps/tpad/trim,drawtext -an ...",
        "视差通道：ffmpeg -loop 1 -i <frame>.png -loop 1 -i light_overlay.png -filter_complex zoompan,eq,noise,vignette,overlay,drawtext ...",
        "片段重拍：替换 input/<项目>/generated_video/<Sxx>.mp4 后执行 --retake Sxx"
      ]
    },
    {
      "id": "05_audio",
      "name": "本地配音 / BGM / 音效",
      "owner": "声音 Agent",
      "status": "pass",
      "duration_s": 5.62,
      "summary": "12 段离线配音 + 音效；全片人声轨 73.0s，最大音画漂移 0.0s；BGM 73.0s 本地合成",
      "artifacts": [
        {
          "label": "音画同步时间轴",
          "path": "output/05_audio/audio_sync.json",
          "type": "json"
        },
        {
          "label": "全片人声轨",
          "path": "output/05_audio/voice_track.wav",
          "type": "audio"
        },
        {
          "label": "全片氛围 BGM",
          "path": "output/05_audio/bgm.wav",
          "type": "audio"
        },
        {
          "label": "S01 混音",
          "path": "output/05_audio/S01.wav",
          "type": "audio"
        },
        {
          "label": "S02 混音",
          "path": "output/05_audio/S02.wav",
          "type": "audio"
        },
        {
          "label": "S03 混音",
          "path": "output/05_audio/S03.wav",
          "type": "audio"
        },
        {
          "label": "S04 混音",
          "path": "output/05_audio/S04.wav",
          "type": "audio"
        },
        {
          "label": "S05 混音",
          "path": "output/05_audio/S05.wav",
          "type": "audio"
        },
        {
          "label": "S06 混音",
          "path": "output/05_audio/S06.wav",
          "type": "audio"
        },
        {
          "label": "S07 混音",
          "path": "output/05_audio/S07.wav",
          "type": "audio"
        },
        {
          "label": "S08 混音",
          "path": "output/05_audio/S08.wav",
          "type": "audio"
        },
        {
          "label": "S09 混音",
          "path": "output/05_audio/S09.wav",
          "type": "audio"
        },
        {
          "label": "S10 混音",
          "path": "output/05_audio/S10.wav",
          "type": "audio"
        },
        {
          "label": "S11 混音",
          "path": "output/05_audio/S11.wav",
          "type": "audio"
        },
        {
          "label": "S12 混音",
          "path": "output/05_audio/S12.wav",
          "type": "audio"
        }
      ],
      "checks": [
        "C12",
        "C28",
        "C31"
      ],
      "commands": [
        "say -v <voice> -r 165 -o <shot>.aiff '<台词>'  →  ffmpeg 转 44100Hz 双声道",
        "numpy 合成音效/BGM → 按 duration_s 拼接 voice_track.wav"
      ],
      "gate": {
        "id": "G4",
        "status": "approved",
        "note": "演示模式自动通过，仍需人工复核",
        "reviewer": "auto-approve（待人工复核）"
      }
    },
    {
      "id": "06_final",
      "name": "字幕 / 合成 / 导出",
      "owner": "剪辑 Agent",
      "status": "pass",
      "duration_s": 2.08,
      "summary": "成片 EP01.mp4：1080×1920 / h264 / 73.0s / AAC 44100Hz；封面 1200x1600",
      "artifacts": [
        {
          "label": "★ 最终成片",
          "path": "output/06_final/EP01.mp4",
          "type": "video"
        },
        {
          "label": "封面（带描边剧名）",
          "path": "output/06_final/cover.png",
          "type": "image"
        },
        {
          "label": "剪辑单（逐镜入出点 + 实测回填）",
          "path": "output/06_final/剪辑单.md",
          "type": "text"
        },
        {
          "label": "字幕时间轴",
          "path": "output/06_final/EP01.srt",
          "type": "text"
        },
        {
          "label": "AI 标识留痕",
          "path": "output/06_final/ai_label_notice.txt",
          "type": "text"
        },
        {
          "label": "导出参数实测",
          "path": "output/06_final/export_probe.json",
          "type": "json"
        }
      ],
      "checks": [
        "C01",
        "C02",
        "C03",
        "C04",
        "C05",
        "C06",
        "C07",
        "C08",
        "C09",
        "C10",
        "C11",
        "C32"
      ],
      "commands": [
        "ffmpeg -f concat -safe 0 -i concat_list.txt -c copy _concat.mp4",
        "ffmpeg -i _concat.mp4 -i voice_track.wav -i bgm.wav -filter_complex amix -c:v copy -c:a aac -ar 44100 -ac 2 -metadata comment='AI 辅助制作' EP01.mp4"
      ]
    },
    {
      "id": "07_reports",
      "name": "逐镜质检 + 逐条验收",
      "owner": "质检 Agent",
      "status": "pass",
      "duration_s": 3.0,
      "summary": "32 条规则：通过 16 / 需人工核验 16 / 不通过 0；逐镜质检 12 镜（真视频 1 镜）；综合 WARN 75分",
      "artifacts": [
        {
          "label": "★ 验收报告（含质量门与逐镜质检）",
          "path": "output/07_reports/compliance_report.md",
          "type": "text"
        },
        {
          "label": "★ 查验台数据源",
          "path": "output/status.json",
          "type": "json"
        },
        {
          "label": "逐镜质检与重拍清单",
          "path": "output/07_reports/shot_qc.json",
          "type": "json"
        },
        {
          "label": "逐镜抽帧证据目录",
          "path": "output/07_reports/qc_frames/",
          "type": "dir"
        },
        {
          "label": "导演台质量门",
          "path": "output/00_previs/director_gates.json",
          "type": "json"
        },
        {
          "label": "导演台预演表",
          "path": "output/00_previs/previs.md",
          "type": "text"
        },
        {
          "label": "生产预览与指纹",
          "path": "output/00_previs/production_preview.md",
          "type": "text"
        },
        {
          "label": "创作链路留痕",
          "path": "output/07_reports/creation_chain.md",
          "type": "text"
        },
        {
          "label": "生成参数",
          "path": "output/07_reports/generation_params.json",
          "type": "json"
        },
        {
          "label": "素材授权台账",
          "path": "output/07_reports/asset_licenses.csv",
          "type": "csv"
        },
        {
          "label": "原创声明模板",
          "path": "output/07_reports/originality_declaration.md",
          "type": "text"
        },
        {
          "label": "人工确认门",
          "path": "output/gates.json",
          "type": "json"
        }
      ],
      "checks": [],
      "commands": [
        "compliance.run()：ffmpeg -i 解析成片 + 读取素材/归档，逐条执行 32 条规则",
        "quality.qc_all()：逐镜抽帧测量运动量/黑边/字幕/重复度/接镜跳变/音画漂移",
        "生成合规报告、逐镜重拍清单与人工核验清单"
      ],
      "gate": {
        "id": "G5",
        "status": "approved",
        "note": "演示模式自动通过，仍需人工复核",
        "reviewer": "auto-approve（待人工复核）"
      }
    }
  ],
  "checks": [
    {
      "id": "C01",
      "rule_id": "HG-TECH-01",
      "stage": "06_final",
      "name": "竖屏 9:16 分辨率 1080×1920",
      "category": "技术规格",
      "severity": "blocker",
      "status": "pass",
      "expected": "1080x1920（宽×高，9:16 竖屏）",
      "actual": "1080x1920（期望 1080x1920）",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 阿里云开发者社区《8G显卡本地部署AI漫剧流水线》| https://developer.aliyun.com/article/1774060；[实1] 润灭网《自制AI短剧怎么上传红果》| https://www.runmie.com/44742.html。注：官方创作者中心未见逐像素公开条文，1080×1920 为全来源一致口径",
      "how_to_verify": "ffmpeg -i 查看 Video 流中的 1080x1920；再双击成片确认竖屏且画面未拉伸",
      "fix_hint": "在 config/project.json 把 width/height 改为 1080/1920 后重跑 06_final"
    },
    {
      "id": "C02",
      "rule_id": "HG-TECH-02",
      "stage": "06_final",
      "name": "视频编码 H.264/AVC",
      "category": "技术规格",
      "severity": "blocker",
      "status": "pass",
      "expected": "h264",
      "actual": "视频编码=h264",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实1] 润灭网 MP4/H.264 | https://www.runmie.com/44742.html；[实6] 阿里云开发者社区 | https://developer.aliyun.com/article/1774060",
      "how_to_verify": "ffmpeg -i 查看 Video: h264；用播放器确认可正常解码",
      "fix_hint": "导出时指定 -c:v libx264，重跑 06_final"
    },
    {
      "id": "C03",
      "rule_id": "HG-TECH-03",
      "stage": "06_final",
      "name": "帧率 25 或 30fps（不低于 25）",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "25 或 30 fps（>=25）",
      "actual": "帧率=30 fps",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实1] 帧率不低于 25fps | https://www.runmie.com/44742.html；[实2] 夜雨聆风 25/30fps | https://e.yeyulingfeng.com/a/481272.html；[行业建议][实7] CSDN 30fps | https://blog.csdn.net/weixin_42526415/article/details/170391953",
      "how_to_verify": "ffmpeg -i 查看 Video 流的 '30 fps' / '25 fps' 字段，并确认全片未混帧",
      "fix_hint": "统一按 30fps（或 25fps）渲染，修改 config/project.json 的 fps 后重跑 04_clips/06_final"
    },
    {
      "id": "C04",
      "rule_id": "HG-TECH-04",
      "stage": "06_final",
      "name": "视频码率不低于 4Mbps（建议 8~12Mbps）",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": ">=4000 kb/s（建议 8000~12000 kb/s）",
      "actual": "码率=9180 kb/s（下限 4000）",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规下限·上传口径][实1] 码率不低于 4Mbps | https://www.runmie.com/44742.html；[行业建议][实7] CSDN 8-12Mbps | https://blog.csdn.net/weixin_42526415/article/details/170391953；[实11] 星宇智算 1080P 8-12Mbps 行业通用 | https://www.starverse-ai.com/guide?p=9718",
      "how_to_verify": "ffmpeg -i 查看 Duration 行的 'bitrate: N kb/s'；低于 8000 时人工评估是否有明显压缩块",
      "fix_hint": "把导出 -b:v 提到 8M~12M，重跑 06_final"
    },
    {
      "id": "C05",
      "rule_id": "HG-TECH-05",
      "stage": "06_final",
      "name": "容器格式 MP4",
      "category": "技术规格",
      "severity": "blocker",
      "status": "pass",
      "expected": "mp4",
      "actual": "容器=mp4",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实1] 润灭网 MP4 | https://www.runmie.com/44742.html；[实6] 阿里云开发者社区 mp4 | https://developer.aliyun.com/article/1774060；[实2] 夜雨聆风 MP4(H.264) | https://e.yeyulingfeng.com/a/481272.html",
      "how_to_verify": "ffmpeg -i 首行 Input #0, mov,mp4,... 且文件扩展名为 .mp4",
      "fix_hint": "重新封装为 MP4（-f mp4 / 改扩展名），重跑 06_final"
    },
    {
      "id": "C06",
      "rule_id": "HG-TECH-06",
      "stage": "06_final",
      "name": "单集时长 60~120s（上传口径 1~5 分钟）",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "60~120 s（平台上传口径 60~300 s）",
      "actual": "时长=73.00 s（期望 60~120s，上传口径 60~300s）；落在 60~120s 为佳区间",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[行业建议][实6] 单集 60~120s | https://developer.aliyun.com/article/1774060；[硬规-上传口径][实1] 单集 1~5 分钟 | https://www.runmie.com/44742.html；[官5] 版权中台保底合作单集 1-3 分钟 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895",
      "how_to_verify": "ffmpeg -i 查看 Duration；并核对 storyboard.json 的 episode.duration_target_s 与实测是否一致",
      "fix_hint": "增删镜头或调整每镜 duration_s，把整集控制在 60~120s 后重跑 06_final"
    },
    {
      "id": "C07",
      "rule_id": "HG-TECH-07",
      "stage": "06_final",
      "name": "无 alpha 通道",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "无 alpha（像素格式如 yuv420p）",
      "actual": "像素格式=yuv420p；无 alpha 通道",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 禁止带 alpha 通道 | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6",
      "how_to_verify": "ffmpeg -i 查看 Video 流像素格式，出现 yuva/rgba/argb/bgra/gbrap 即为带 alpha",
      "fix_hint": "导出前加 -pix_fmt yuv420p，重跑 06_final"
    },
    {
      "id": "C08",
      "rule_id": "HG-TECH-08",
      "stage": "06_final",
      "name": "分辨率宽高均为偶数（非奇数）",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "width/height 均为偶数",
      "actual": "1080x1920（均为偶数）",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 禁止奇尺寸分辨率 | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6",
      "how_to_verify": "ffmpeg -i 读取宽高，检查 width%2==0 且 height%2==0",
      "fix_hint": "把输出尺寸修正为偶数（1080×1920）后重跑 06_final"
    },
    {
      "id": "C09",
      "rule_id": "HG-TECH-09",
      "stage": "06_final",
      "name": "音频编码 AAC",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "aac",
      "actual": "音频编码=aac",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 音频 AAC | https://developer.aliyun.com/article/1774060；[实2] 夜雨聆风 AAC | https://e.yeyulingfeng.com/a/481272.html；[项目契约] SPEC §6",
      "how_to_verify": "ffmpeg -i 查看 Audio: aac",
      "fix_hint": "配音/混音导出时指定 -c:a aac，重跑 05_audio/06_final"
    },
    {
      "id": "C10",
      "rule_id": "HG-TECH-10",
      "stage": "06_final",
      "name": "音频采样率 44100Hz",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "44100 Hz",
      "actual": "采样率=44100 Hz",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 44100Hz | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6",
      "how_to_verify": "ffmpeg -i 查看 Audio 流的 44100 Hz 字段",
      "fix_hint": "TTS/合成时指定 -ar 44100，重跑 05_audio"
    },
    {
      "id": "C11",
      "rule_id": "HG-TECH-11",
      "stage": "06_final",
      "name": "音频双声道（stereo）",
      "category": "技术规格",
      "severity": "major",
      "status": "pass",
      "expected": "2 声道 / stereo",
      "actual": "声道数=2（stereo）",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 双声道 | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6",
      "how_to_verify": "ffmpeg -i 查看 Audio 流为 stereo 而非 mono",
      "fix_hint": "混音时指定 -ac 2，重跑 05_audio"
    },
    {
      "id": "C12",
      "rule_id": "HG-TECH-12",
      "stage": "06_final",
      "name": "连载首次投稿 ≥3 集（总时长门槛待核）",
      "category": "技术规格",
      "severity": "minor",
      "status": "warn",
      "expected": "连载作品首次上传 >=3 集",
      "actual": "需人工核验：登录短剧创作者中心核对本批次投稿集数；「总时长>20分钟」仅见第三方实操文，须向对接商务或后台当前提示核实",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[平台合作口径][官5] 抖音集团短剧版权中台《成品漫剧业务介绍及合作指引》连载作品首次上传至少≥3集 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[存疑·非官方][实1] 称 2026-06 起总时长>20分钟、保底精品总时长≥120分钟系不同模式口径，未见官方统一确认 | https://www.runmie.com/44742.html",
      "how_to_verify": "登录短剧创作者中心核对本批次投稿集数；「总时长>20分钟」仅见第三方实操文，须向对接商务或后台当前提示核实",
      "fix_hint": "补齐至少 3 集成片再提交；总时长门槛以平台后台当前口径为准，勿按网传数字硬凑"
    },
    {
      "id": "C13",
      "rule_id": "HG-CONT-01",
      "stage": "01_script",
      "name": "每集明显位置添加 AI 提示标识（含片头「AI辅助制作」）",
      "category": "内容合规",
      "severity": "blocker",
      "status": "warn",
      "expected": "每集片头/明显位置可见 AI 提示标识；片头、封面、简介同步标注；文件元数据含隐式 AIGC 标识",
      "actual": "需人工核验：每集片头/明显位置的可见 AI 提示标识、封面与简介同步标注、文件元数据隐式 AIGC 标识是否齐全且未被隐藏；本地文本线索命中 4 处：output/07_reports/compliance_report.md(AI 辅助制作)；output/07_reports/creation_chain.md(AI 辅助制作)；output/07_reports/originality_declaration.md(AIGC)；output/06_final/ai_label_notice.txt(AI 辅助制作)。ffmpeg -i 无法读取画面文字与自定义元数据",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-法规][官1] 广电总局令第16号《微短剧发展管理办法》第三十四条：每集明显位置添加提示标识 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[官2]《人工智能生成合成内容标识办法》显式+隐式标识 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm；[平台执行·媒体报道][实9] 红果 2026-08-03 起要求每集片头标注「AI辅助制作」| https://www.toutiao.com/a7701912782408614440；[权1] 人民网 苔花统一标识 | https://sc.people.com.cn/n2/2026/0903/c345167-41685601.html",
      "how_to_verify": "逐集播放片头 3 秒确认可见「AI辅助制作」/苔花标识；核对封面与简介同步标注；用专门工具读取文件元数据 AIGC 隐式标识。注意法规原文为「每集明显位置」，非仅片头一次",
      "fix_hint": "在 06_final 片头叠加 AI 标识字幕层（每集都加，不得用透明度/边缘裁剪隐藏），并保留导出元数据，重跑导出"
    },
    {
      "id": "C14",
      "rule_id": "HG-CONT-02",
      "stage": "01_script",
      "name": "不含《微短剧发展管理办法》第二十五条禁止内容",
      "category": "内容合规",
      "severity": "blocker",
      "status": "warn",
      "expected": "无第二十五条 11 项禁止内容：邪教迷信、拜金主义、淫秽赌博吸毒、渲染暴力恐怖/教唆犯罪、危害未成年人、侮辱诽谤散布隐私、破坏民族团结等",
      "actual": "需人工核验：人工通读 script.md 与 storyboard.json 的全部台词、画面描述、剧名，逐项对照第二十五条 11 款；本地无语义审核能力",
      "evidence": "input/demo/storyboard.json",
      "source": "[硬规-法规][官1] 国家广播电视总局令第16号 第二十五条（全文 11 款）| https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html",
      "how_to_verify": "人工通读 script.md 与 storyboard.json 的全部台词、画面描述、剧名，逐项对照第二十五条 11 款；本地无语义审核能力",
      "fix_hint": "删除/改写命中条款的桥段与台词，从 01_script 起重跑受影响环节"
    },
    {
      "id": "C15",
      "rule_id": "HG-CONT-03",
      "stage": "01_script",
      "name": "受限题材自查（仅作风险提示，非平台硬规）",
      "category": "内容合规",
      "severity": "major",
      "status": "warn",
      "expected": "规避灵异迷信/猎奇/超自然金手指/以暴制暴/畸形婚恋等方向（风险自查项）",
      "actual": "需人工核验：人工核对题材方向。★该「3类禁拍13类受限」清单已被红果官方明确否认发布，绝不可当作官方硬规引用；只按 [官1]§25 与广电专项治理方向做风险自查",
      "evidence": "input/demo/storyboard.json",
      "source": "[存疑·非官方][权6] 环球网科技《红果3类短剧禁拍13类受限》| https://new.qq.com/rain/a/20260606A031QE00；★[官方辟谣][权5] 新京报/腾讯网《红果短剧回应：从未发布过类似审核标准》(2026-06-06) | https://new.qq.com/rain/a/20260606A082OE00；[监管方向][权4] 广电总局 2026-06-01 专项治理 8 类重点问题 | https://www.zhitongcaijing.com/content/detail/1522062.html；[实3] 夜雨聆风备案避坑指南 | https://e.yeyulingfeng.com/a/478803.html",
      "how_to_verify": "人工核对题材方向。★该「3类禁拍13类受限」清单已被红果官方明确否认发布，绝不可当作官方硬规引用；只按 [官1]§25 与广电专项治理方向做风险自查",
      "fix_hint": "若命中高危方向，把超自然能力改为可解释的专业本领、以暴制暴改为交由公安依法处置，重跑 01_script"
    },
    {
      "id": "C16",
      "rule_id": "HG-CONT-04",
      "stage": "01_script",
      "name": "角色身份锚点 ≥3 条（跨镜五官一致的数据基础）",
      "category": "内容合规",
      "severity": "major",
      "status": "pass",
      "expected": "每个角色 identity_anchors >= 3 条",
      "actual": "2 个角色 / 共 8 条锚点；每角色均 >=3 条",
      "evidence": "input/demo/characters.json",
      "source": "[项目契约] SPEC §2.2；[平台公告][官6] 红果《关于规范AI剧角色创作的公告》：同剧各角色须有清晰形象区分度 | https://www.nfnews.com/content/voAp8L5Y6R.html",
      "how_to_verify": "打开 characters.json 逐角色数 identity_anchors 条数；并人工抽查 output/03_frames 中同名角色跨镜五官是否一致（本项仅自动校验锚点数量）",
      "fix_hint": "为不足 3 条锚点的角色补足，重跑 02_characters/03_frames"
    },
    {
      "id": "C17",
      "rule_id": "HG-CONT-05",
      "stage": "01_script",
      "name": "跨剧/跨角色不复用高度近似 AI 脸",
      "category": "内容合规",
      "severity": "major",
      "status": "warn",
      "expected": "不与平台已有剧集角色面部高度相似；同剧各角色形象有清晰区分度",
      "actual": "需人工核验：人工用平台人脸相似度预检工具做跨剧比对，并逐帧比对本地角色主视觉；本地无跨剧人脸库，无法自动判定",
      "evidence": "input/demo/storyboard.json",
      "source": "[平台公告][官6] 南方+ 红果治理「高频AI脸」| https://www.nfnews.com/content/voAp8L5Y6R.html；[官7] 中国新闻出版广电报 2026-10-27 公告「多人同脸」「跨剧撞脸」| https://epaper.chinaxwcb.com/epaper/2026-11/04/content_99886689.html；[权2] 澎湃新闻 | https://m.thepaper.cn/newsDetail_forward_34388675；[权3] 百度百科 AI短剧词条（2026-08 公告）| https://baike.baidu.com/item/AI微短剧/67248821；[实9] 平台人脸相似度比对系统 | https://www.toutiao.com/a7701912782408614440",
      "how_to_verify": "人工用平台人脸相似度预检工具做跨剧比对，并逐帧比对本地角色主视觉；本地无跨剧人脸库，无法自动判定",
      "fix_hint": "为每个角色单独调参渲染，建立差异化「视觉指纹」（骨相五官+服饰造型），重跑 02_characters/03_frames"
    },
    {
      "id": "C18",
      "rule_id": "HG-CONT-06",
      "stage": "01_script",
      "name": "全剧画风统一",
      "category": "内容合规",
      "severity": "major",
      "status": "warn",
      "expected": "全剧统一 style.name / prompt_prefix，镜头无风格漂移",
      "actual": "需人工核验：全剧画风/线条/色温一致性与五官稳定性；数据层：style.name=写实国漫 · 都市冷调电影感，prompt_prefix=已配置，negative_prompt=已配置，帧 12 / 镜 12",
      "evidence": "input/demo/storyboard.json",
      "source": "[平台执行·行业整理][实10] 红果公告要求全剧画风统一 | https://www.toutiao.com/a7706135472770155050；[官7] 中国新闻出版广电报：治理剧情结构/视听表达要素同质化与低质 | https://epaper.chinaxwcb.com/epaper/2026-11/04/content_99886689.html；[项目契约] SPEC §2.1/§6",
      "how_to_verify": "人工连续播放全片检查画风、色温、线条风格是否一致；并核对所有镜头共用同一 prompt_prefix 与 negative_prompt（本项仅自动校验配置与帧齐备性）",
      "fix_hint": "统一 style.prompt_prefix / negative_prompt，剔除风格异常镜头后重跑 03_frames"
    },
    {
      "id": "C19",
      "rule_id": "HG-CONT-07",
      "stage": "01_script",
      "name": "单句台词 ≤24 字",
      "category": "内容合规",
      "severity": "minor",
      "status": "pass",
      "expected": "每个 shot 的 dialogue.text 长度 <= 24 字",
      "actual": "检查 12 条非空台词（<=24 字）；全部合规",
      "evidence": "input/demo/storyboard.json",
      "source": "[项目契约] SPEC §2.1（红果漫剧台词宜短）；[行业建议][实6] 对话密集、单镜头叙事简短 | https://developer.aliyun.com/article/1774060",
      "how_to_verify": "检查 storyboard.json 所有 dialogue.text 字数；并人工听配音断句是否自然",
      "fix_hint": "拆句或精简超长台词，重跑 01_script/05_audio"
    },
    {
      "id": "C20",
      "rule_id": "HG-CONT-08",
      "stage": "01_script",
      "name": "片头信息标注（剧名/许可证号/批准文件编号/节目编号）",
      "category": "内容合规",
      "severity": "major",
      "status": "warn",
      "expected": "片头明显位置标注剧名，并按剧目类别标注许可证号/批准文件编号/节目编号",
      "actual": "需人工核验：人工查看每集片头；三类剧须有平台节目编号，一/二类须有发行许可证号或批准文件编号；投资额≥30万或特殊题材须先走广电备案",
      "evidence": "input/demo/storyboard.json",
      "source": "[硬规-法规][官1]《微短剧发展管理办法》第二十七条（片头明显位置标注剧名、许可证号、批准文件编号、节目编号）、第十七条/第三十三条（三类由平台审核并标注节目编号）| https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[权1] 人民网 微短剧统一标识与备案号 | https://sc.people.com.cn/n2/2026/0903/c345167-41685601.html",
      "how_to_verify": "人工查看每集片头；三类剧须有平台节目编号，一/二类须有发行许可证号或批准文件编号；投资额≥30万或特殊题材须先走广电备案",
      "fix_hint": "在片头模板加入剧名与编号占位，取得编号后回填，重跑 06_final；编号未取得前不得上架"
    },
    {
      "id": "C21",
      "rule_id": "HG-CONT-09",
      "stage": "01_script",
      "name": "整集镜头数 ≥8",
      "category": "内容合规",
      "severity": "minor",
      "status": "pass",
      "expected": "storyboard.shots 数量 >= 8 且 shot id 唯一、形如 S\\d{2}",
      "actual": "镜头数=12（>=8）；id 唯一=True；id 符合 S\\d{2}=True",
      "evidence": "input/demo/storyboard.json",
      "source": "[项目契约] SPEC §2.1（整集镜头数 ≥ 8）；[行业建议][实6] 拆成 5~8s 单镜头片段渲染 | https://developer.aliyun.com/article/1774060",
      "how_to_verify": "检查 storyboard.json 的 shots 数组长度与 id 唯一性/格式；并核对成片实际切镜数",
      "fix_hint": "拆分或补足镜头到 ≥8，重跑 01_script 起的各环节"
    },
    {
      "id": "C22",
      "rule_id": "HG-CONT-10",
      "stage": "01_script",
      "name": "单镜时长 3~8s",
      "category": "内容合规",
      "severity": "minor",
      "status": "pass",
      "expected": "每个 shot 的 duration_s 在 3~8 之间",
      "actual": "共 12 镜；全部在 3~8s",
      "evidence": "input/demo/storyboard.json",
      "source": "[项目契约] SPEC §2.1（duration_s 3~8）；[行业建议][实7] 单个镜头不要停太久 | https://blog.csdn.net/weixin_42526415/article/details/170391953",
      "how_to_verify": "检查 storyboard.json 每个 shot 的 duration_s；并人工确认成片节奏无过长静止镜头",
      "fix_hint": "调整超范围镜头的 duration_s 后重跑 04_clips/06_final"
    },
    {
      "id": "C23",
      "rule_id": "HG-RIGHT-01",
      "stage": "07_reports",
      "name": "创作链路归档完整（剧本/分镜/角色卡/参数/报告）",
      "category": "版权留痕",
      "severity": "major",
      "status": "pass",
      "expected": "output/01_script/script.md、output/01_script/storyboard.json、output/02_characters/characters.json、config/project.json、output/07_reports/compliance_report.md 齐备",
      "actual": "5/5 项归档文件齐备（output/01_script/script.md, output/01_script/storyboard.json, output/02_characters/characters.json, config/project.json, output/07_reports/compliance_report.md）；内容完整性按 how_to_verify 人工核验",
      "evidence": "output/",
      "source": "[平台要求][官5] 抖音集团短剧版权中台合作指引（先上传过审、再签约确权）| http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[实5] 短剧自习室周报 2026-06-12 工程文件截图/承诺函公告 | https://duanju007.com/?p=27372；[硬规-法规][官1] 第十条 尊重原创保护著作权、第三十二条 内容安全全流程责任追溯 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[项目契约] SPEC §0/§6",
      "how_to_verify": "逐项打开归档文件，确认含完整剧本、分镜 JSON、生成参数、工程文件且与成片版本一致；本项仅自动校验文件存在性",
      "fix_hint": "补齐缺失归档文件，从对应 stage 重跑并确认产物落盘"
    },
    {
      "id": "C24",
      "rule_id": "HG-RIGHT-02",
      "stage": "07_reports",
      "name": "剪辑工程文件截图（创作链路截图）",
      "category": "版权留痕",
      "severity": "major",
      "status": "warn",
      "expected": "≥4 张不同段落的工程文件截图，含短剧画面、合理分轨与剪辑点，可见项目名",
      "actual": "需人工核验：人工打开截图文件夹，核对连续时间段、项目名可见、未打码、≥4 张且与成片对应",
      "evidence": "output/07_reports/",
      "source": "[平台要求][实4] 引《短剧版权证明文件提交指南》：至少 4 张不同段落展示图片，含短剧画面及合理分轨和剪辑点 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[实5] 2026-06-12 起工程文件截图为多渠道分发必要条件 | https://duanju007.com/?p=27372；[实1] 剧本创作记录/剪映工程/即梦或 Liblib 生成截图 | https://www.runmie.com/44742.html",
      "how_to_verify": "人工打开截图文件夹，核对连续时间段、项目名可见、未打码、≥4 张且与成片对应",
      "fix_hint": "在剪辑软件中拉动时间轴连续截图，归入 output/07_reports/ 后随片重新提交"
    },
    {
      "id": "C25",
      "rule_id": "HG-RIGHT-03",
      "stage": "07_reports",
      "name": "不侵权承诺函 / 原创声明",
      "category": "版权留痕",
      "severity": "blocker",
      "status": "warn",
      "expected": "按平台最新模板填写并签署《不侵权承诺函》/原创声明，拍照上传后台",
      "actual": "需人工核验：人工核对承诺函为后台最新模板版本、签署主体与账号认证一致、已拍照上传；法律效力无法自动判定",
      "evidence": "output/07_reports/",
      "source": "[平台要求][实4] 平台给模板，必填必拍照上传，签后对版权负责 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[实2] 上传版权证明文件：创作链路截图、不侵权承诺函 | https://e.yeyulingfeng.com/a/481272.html；[实5] 2026-06-12 更新《承诺函》模板 | https://duanju007.com/?p=27372；[实3] 原创声明函/AI 工具商用授权 | https://e.yeyulingfeng.com/a/478803.html",
      "how_to_verify": "人工核对承诺函为后台最新模板版本、签署主体与账号认证一致、已拍照上传；法律效力无法自动判定",
      "fix_hint": "从创作者中心后台下载最新模板，填写签署后重新上传"
    },
    {
      "id": "C26",
      "rule_id": "HG-RIGHT-04",
      "stage": "07_reports",
      "name": "参考图 / 角色肖像 / 字体音效授权状态可追溯",
      "category": "版权留痕",
      "severity": "major",
      "status": "warn",
      "expected": "characters.json 的 reference_images 与所用素材均有授权状态记录；AI 工具商用授权条款留存",
      "actual": "需人工核验：人工逐项核对参考图、真人肖像、字体、音效、配音模型、AI 工具的授权凭证与商用范围；授权状态需写入 characters.json 与授权台账",
      "evidence": "output/07_reports/",
      "source": "[平台要求][实4] AI 生成需提供平台用户协议版权归属条款截图，改编须有正式授权 | http://mp.weixin.qq.com/s?__biz=Mzk0NTYwNTAyMg==&mid=2247492686&idx=1&sn=7a9058ee9cfbdf7df752522146bf64da；[官5] 非取得合法授权严禁蹭 IP 名称、版权归属清晰 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[权3] 2026-09-02「融像」「融声」座谈会：须取得权利人明确授权 | https://baike.baidu.com/item/AI微短剧/67248821；[实8] 五证合一（角色肖像模型合规来源证明、全商业字体音效授权）| https://www.tahou.com/article/221745076397698053",
      "how_to_verify": "人工逐项核对参考图、真人肖像、字体、音效、配音模型、AI 工具的授权凭证与商用范围；授权状态需写入 characters.json 与授权台账",
      "fix_hint": "补齐授权凭证，把授权状态写入 characters.json 并在 output/07_reports/ 建立授权台账"
    },
    {
      "id": "C27",
      "rule_id": "HG-RIGHT-05",
      "stage": "07_reports",
      "name": "AI 隐式标识 / 元数据溯源留痕",
      "category": "版权留痕",
      "severity": "major",
      "status": "warn",
      "expected": "成片文件元数据含 AIGC 隐式标识（生成服务/传播平台/唯一编号），且未被删除篡改",
      "actual": "需人工核验：人工用平台/专门工具读取文件元数据中的 AIGC 字段；ffmpeg -i 不展示自定义元数据，本检查器无法自动判定",
      "evidence": "output/07_reports/",
      "source": "[硬规-法规][官2]《人工智能生成合成内容标识办法》：文件元数据添加隐式标识、不得恶意删除篡改隐匿 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm；[官3] 中国政府网解读 | https://www.gov.cn/zhengce/202503/content_7014281.htm；[官1] 第16号令第三十四条 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html；[实12] 中国经济网 元数据字段名含 AIGC 标识符号 | https://www.ce.cn/cysc//newmain/yc/jsxw/202510/t20251024_2535313.shtml",
      "how_to_verify": "人工用平台/专门工具读取文件元数据中的 AIGC 字段；ffmpeg -i 不展示自定义元数据，本检查器无法自动判定",
      "fix_hint": "导出时保留 AIGC 元数据，禁止二次转码丢失；必要时用平台标识工具补写"
    },
    {
      "id": "C28",
      "rule_id": "HG-AV-01",
      "stage": "06_final",
      "name": "内嵌烧录字幕（白字黑描边）",
      "category": "音画质量",
      "severity": "major",
      "status": "warn",
      "expected": "字幕烧录进画面（非外挂软字幕），白字黑描边、字体清晰可读",
      "actual": "需人工核验：字幕是否烧录进画面、白字黑描边、字体清晰且不遮挡人脸；数据层：12/12 镜头有字幕文本；未检出独立软字幕流",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实6] 内嵌字幕 | https://developer.aliyun.com/article/1774060；[项目契约] SPEC §6（白字黑描边，思源黑体/微软雅黑级别）；[官1] 第二十六条 剧名台词字幕须符合国家通用语言文字规范 | https://www.nrta.gov.cn/art/2026/7/31/art_1588_73827.html",
      "how_to_verify": "人工逐镜播放确认字幕已烧录进画面、描边清晰、不遮挡人脸；本项仅自动校验 storyboard 字幕文本齐备与是否存在独立软字幕流",
      "fix_hint": "用 drawtext 烧录字幕（白字+黑描边），重跑 06_final"
    },
    {
      "id": "C29",
      "rule_id": "HG-AV-02",
      "stage": "06_final",
      "name": "无第三方水印 / AI 工具水印，且 AI 标识不得刻意隐藏",
      "category": "音画质量",
      "severity": "blocker",
      "status": "warn",
      "expected": "画面无水印；不得用颜色/透明度/边缘裁剪隐藏 AI 标识",
      "actual": "需人工核验：人工全片逐段查看四角与边缘，确认无工具/平台水印、无遮挡式隐藏标识；水印无法从流信息自动判定",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实1] 无水印无黑边 | https://www.runmie.com/44742.html；[实8] 严禁利用文字颜色、透明度或边缘裁剪刻意隐藏 AI 水印 | https://www.tahou.com/article/221745076397698053；[官2] 不得恶意删除、篡改、伪造、隐匿生成合成内容标识 | https://www.cac.gov.cn/2025-03/14/c_1743654685899683.htm",
      "how_to_verify": "人工全片逐段查看四角与边缘，确认无工具/平台水印、无遮挡式隐藏标识；水印无法从流信息自动判定",
      "fix_hint": "改用有商用授权的生成与剪辑工具，去除素材水印后重跑 03_frames/06_final"
    },
    {
      "id": "C30",
      "rule_id": "HG-AV-03",
      "stage": "06_final",
      "name": "无黑边 / 无拉伸变形",
      "category": "音画质量",
      "severity": "major",
      "status": "warn",
      "expected": "画面满屏 9:16，无上下/左右黑边，人物无拉伸变形",
      "actual": "需人工核验：人工播放确认画面铺满、无黑边；并核对 03_frames 合成时 scale/pad 参数与 1080×1920 一致",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[硬规-上传口径][实1] 无水印无黑边 | https://www.runmie.com/44742.html；[官5] 书壳封面不能拉伸、人物不得拉伸变形（同一审核口径延伸至正片）| http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895",
      "how_to_verify": "人工播放确认画面铺满、无黑边；并核对 03_frames 合成时 scale/pad 参数与 1080×1920 一致",
      "fix_hint": "统一按 1080×1920 居中裁剪/填充，重跑 03_frames/06_final"
    },
    {
      "id": "C31",
      "rule_id": "HG-AV-04",
      "stage": "06_final",
      "name": "音画同步 / 口型同步",
      "category": "音画质量",
      "severity": "major",
      "status": "warn",
      "expected": "配音、音效、字幕与画面时间轴对齐，口型基本吻合，非全程怼脸单一特写",
      "actual": "需人工核验：人工全片播放核对音画与口型、景别分布；本地无自动音画/口型比对能力",
      "evidence": "output/06_final/EP01.mp4",
      "source": "[平台执行·行业整理][实10] 红果公告要求口型同步、别全程怼脸 | https://www.toutiao.com/a7706135472770155050；[项目契约] SPEC §5（05_audio 配音 / 06_final 合成）",
      "how_to_verify": "人工全片播放核对音画与口型、景别分布；本地无自动音画/口型比对能力",
      "fix_hint": "调整 05_audio 时间轴与 06_final 合成偏移，重跑 05_audio/06_final"
    },
    {
      "id": "C32",
      "rule_id": "HG-AV-05",
      "stage": "06_final",
      "name": "封面规格（比例 + 描边剧名）",
      "category": "音画质量",
      "severity": "major",
      "status": "warn",
      "expected": "封面 3:4（建议 1200×1600，1~5MB）或按投稿入口要求 350×500；带描边剧名、无拉伸（两来源口径不一致，以后台当前提示为准）",
      "actual": "需人工核验：封面描边剧名、无拉伸变形、比例符合后台当前口径（版权中台 3:4 建议 1200×1600；另有 350×500 实操口径，二者不一致）；实测 1200x1600（约 3:4），1.00 MB",
      "evidence": "output/06_final/cover.png",
      "source": "[平台合作口径][官5] 版权中台：动态漫书壳封面必须 3:4、1-5MB、建议 1200×1600、不得拉伸变形 | http://mp.weixin.qq.com/s?__biz=MzkxMTQ5MjkzMA==&mid=2247496815&idx=4&sn=21039388f1dad31de03064f18a458895；[创作者实操][实1] 封面 350×500 且必须带描边剧名，否则驳回 | https://www.runmie.com/44742.html。★两者比例口径不一致，已标注差异",
      "how_to_verify": "人工打开封面确认比例、描边剧名、无拉伸，并核对文件大小；本项仅自动读取封面图片像素尺寸",
      "fix_hint": "按后台当前要求重做封面，剧名加描边，另存到投稿目录；不同季不得复用同一张封面"
    }
  ],
  "shots": [
    {
      "id": "S01",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S01.png",
      "clip": "output/04_clips/S01.mp4",
      "audio": "output/05_audio/S01.wav",
      "subtitle": "不是我签的，是你代签的。",
      "issues": []
    },
    {
      "id": "S02",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S02.png",
      "clip": "output/04_clips/S02.mp4",
      "audio": "output/05_audio/S02.wav",
      "subtitle": "会议室有监控，调出来。",
      "issues": []
    },
    {
      "id": "S03",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S03.png",
      "clip": "output/04_clips/S03.mp4",
      "audio": "output/05_audio/S03.wav",
      "subtitle": "昨晚九点，只有你进过。",
      "issues": []
    },
    {
      "id": "S04",
      "duration_s": 7.0,
      "status": "pass",
      "frame": "output/03_frames/S04.png",
      "clip": "output/04_clips/S04.mp4",
      "audio": "output/05_audio/S04.wav",
      "subtitle": "九点零七，灯是灭的。",
      "issues": []
    },
    {
      "id": "S05",
      "duration_s": 5.0,
      "status": "pass",
      "frame": "output/03_frames/S05.png",
      "clip": "output/04_clips/S05.mp4",
      "audio": "output/05_audio/S05.wav",
      "subtitle": "纸下面，还有一层压痕。",
      "issues": []
    },
    {
      "id": "S06",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S06.png",
      "clip": "output/04_clips/S06.mp4",
      "audio": "output/05_audio/S06.wav",
      "subtitle": "压痕……什么意思？",
      "issues": []
    },
    {
      "id": "S07",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S07.png",
      "clip": "output/04_clips/S07.mp4",
      "audio": "output/05_audio/S07.wav",
      "subtitle": "有人照着，描过一遍。",
      "issues": []
    },
    {
      "id": "S08",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S08.png",
      "clip": "output/04_clips/S08.mp4",
      "audio": "output/05_audio/S08.wav",
      "subtitle": "谁？",
      "issues": []
    },
    {
      "id": "S09",
      "duration_s": 7.0,
      "status": "pass",
      "frame": "output/03_frames/S09.png",
      "clip": "output/04_clips/S09.mp4",
      "audio": "output/05_audio/S09.wav",
      "subtitle": "章号，不在这层楼。",
      "issues": []
    },
    {
      "id": "S10",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S10.png",
      "clip": "output/04_clips/S10.mp4",
      "audio": "output/05_audio/S10.wav",
      "subtitle": "这文件……是塞给我的。",
      "issues": []
    },
    {
      "id": "S11",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S11.png",
      "clip": "output/04_clips/S11.mp4",
      "audio": "output/05_audio/S11.wav",
      "subtitle": "我不是来被审的。",
      "issues": []
    },
    {
      "id": "S12",
      "duration_s": 6.0,
      "status": "pass",
      "frame": "output/03_frames/S12.png",
      "clip": "output/04_clips/S12.mp4",
      "audio": "output/05_audio/S12.wav",
      "subtitle": "这页，只是第一份。",
      "issues": []
    }
  ],
  "human_gates": [
    {
      "id": "G1",
      "stage": "01_script",
      "name": "剧本与分镜确认",
      "how_to_verify": "打开 output/01_script/script.md 与 storyboard.json，核对钩子、题材红线、台词长度与镜头时长",
      "reject_action": "修改 input/<项目名>/storyboard.json 后执行 pipeline.py --from 01_script",
      "status": "approved",
      "note": "演示模式自动通过，仍需人工复核",
      "reviewer": "auto-approve（待人工复核）",
      "decided_at": "2026-11-12T19:13:05+08:00"
    },
    {
      "id": "G2",
      "stage": "02_characters",
      "name": "角色定妆与一致性锁定",
      "how_to_verify": "打开 output/02_characters/character_sheets/ 逐张核对五官与 3 条以上刚性锚点、音色分配",
      "reject_action": "修改 input/<项目名>/characters.json 后执行 pipeline.py --from 02_characters",
      "status": "approved",
      "note": "演示模式自动通过，仍需人工复核",
      "reviewer": "auto-approve（待人工复核）",
      "decided_at": "2026-11-12T19:13:05+08:00"
    },
    {
      "id": "G3",
      "stage": "03_frames",
      "name": "真人转绘帧验收",
      "how_to_verify": "打开 output/03_frames/*.png 与 frame_sources.csv，核对画风统一、无水印、无黑边、每镜来源",
      "reject_action": "替换 input/<项目名>/frames/ 或调整 config/project.json 的 comicify 参数后 --from 03_frames",
      "status": "approved",
      "note": "演示模式自动通过，仍需人工复核",
      "reviewer": "auto-approve（待人工复核）",
      "decided_at": "2026-11-12T19:13:10+08:00"
    },
    {
      "id": "G4",
      "stage": "05_audio",
      "name": "配音与音画同步预检",
      "how_to_verify": "试听 output/05_audio/S*.wav，核对 audio_sync.json 中每镜音轨长度与镜头时长一致",
      "reject_action": "调整 characters.json 的 voice 或 tts_rate 后 --from 05_audio",
      "status": "approved",
      "note": "演示模式自动通过，仍需人工复核",
      "reviewer": "auto-approve（待人工复核）",
      "decided_at": "2026-11-12T19:13:28+08:00"
    },
    {
      "id": "G5",
      "stage": "07_reports",
      "name": "成片终审（人工）",
      "how_to_verify": "播放 output/06_final/EP01.mp4；打开 console/index.html 逐条核对现场无法自动判定的规则（标 warn 项）",
      "reject_action": "按合规报告 fix_hint 修改后 --from 对应环节；确认通过请把 G5 置为 approved",
      "status": "approved",
      "note": "演示模式自动通过，仍需人工复核",
      "reviewer": "auto-approve（待人工复核）",
      "decided_at": "2026-11-12T19:15:21+08:00"
    }
  ],
  "final_video": "output/06_final/EP01.mp4",
  "cover": "output/06_final/cover.png",
  "report_md": "output/07_reports/compliance_report.md",
  "notes": [],
  "director_gates": {
    "summary": {
      "total": 20,
      "passed": 20,
      "warned": 0,
      "failed": 0,
      "blocker_failed": 0,
      "status": "PASS",
      "score": 100.0
    },
    "gates": [
      {
        "id": "D01",
        "name": "五份创作文档齐全",
        "level": "blocker",
        "status": "pass",
        "actual": "齐备 5/5",
        "expected": "5/5 全部存在",
        "evidence": "output/00_creator_docs/",
        "fix_hint": "运行 stage_00_previs 生成缺失文档"
      },
      {
        "id": "D02",
        "name": "SHOT↔MOTION↔CUT 一一对应",
        "level": "blocker",
        "status": "pass",
        "actual": "SHOT 12 / MOTION 12 / CUT 12 / 分镜 12",
        "expected": "四者数量与镜号集合完全一致",
        "evidence": "output/00_creator_docs/{分镜,视频提示词,剪辑单}.md",
        "fix_hint": "检查是否有镜头漏写视频提示词或剪辑单；ID 必须逐个对应"
      },
      {
        "id": "D03",
        "name": "分镜/视频提示词/剪辑单时长逐字一致",
        "level": "blocker",
        "status": "pass",
        "actual": "漂移镜 无；剪辑单时长条目 12",
        "expected": "全部相等，容差 0.005s",
        "evidence": "output/00_creator_docs/",
        "fix_hint": "视频提示词只能原样照抄已接受的镜头时长，不得另估"
      },
      {
        "id": "D04",
        "name": "集长等于可见镜头时长之和",
        "level": "blocker",
        "status": "pass",
        "actual": "镜头合计 73.00s / 目标 73s",
        "expected": "差值 ≤0.05s",
        "evidence": "input/demo/storyboard.json",
        "fix_hint": "调整末镜时长或修正目标集长，禁止用变速凑数"
      },
      {
        "id": "D05",
        "name": "对白发声窗口预算（4.1 字/秒）",
        "level": "blocker",
        "status": "pass",
        "actual": "超载镜 无；最紧窗口占用 52%",
        "expected": "台词时长 ≤ 镜长 −0.35s −0.4s",
        "evidence": "output/00_creator_docs/分镜.md → 声音",
        "fix_hint": "先删装饰动作 → 并行 → 回上游拆镜/精简台词；禁止加快语速"
      },
      {
        "id": "D06",
        "name": "字幕与台词逐字对齐且能在剧本中找到原文",
        "level": "blocker",
        "status": "pass",
        "actual": "偏离镜 无",
        "expected": "subtitle == dialogue.text 且为剧本子串",
        "evidence": "input/demo/script.md",
        "fix_hint": "字幕只能逐字照抄剧本，不得改写或增删标点"
      },
      {
        "id": "D07",
        "name": "连续性锁锁面原样传播到生效镜头",
        "level": "blocker",
        "status": "pass",
        "actual": "缺失 无；锁 4 把",
        "expected": "生效范围内每条视频提示词必须含锁面",
        "evidence": "output/00_creator_docs/视觉设定.md → 连续性锁",
        "fix_hint": "把锁面短语原样写进该镜视频提示词；锁面不得含动作、剧情或否定词"
      },
      {
        "id": "D08",
        "name": "REF 槽位顺序/用途/控制域/文件真实性",
        "level": "blocker",
        "status": "pass",
        "actual": "问题 0；12 张起始帧",
        "expected": "顺序 1..N 连续、用途在闭集、控制域互斥、真实文件存在",
        "evidence": "output/00_creator_docs/分镜.md → 输入参考图",
        "fix_hint": "PLAN-* 只是挂图计划，投产前必须换成项目内真实 REF-* 文件"
      },
      {
        "id": "D09",
        "name": "相邻镜景别/角度/人物关系至少改变一项",
        "level": "craft",
        "status": "pass",
        "actual": "重复相邻 无",
        "expected": "不允许同景别同机位同关系连续两镜",
        "evidence": "input/demo/storyboard.json",
        "fix_hint": "并镜或改景别/机位；同景别重复须贡献反应或细节"
      },
      {
        "id": "D10",
        "name": "正反打不越轴，越轴须声明过渡",
        "level": "craft",
        "status": "pass",
        "actual": "未声明越轴 无",
        "expected": "工作侧一致；换侧须写镜内穿轴/中性过渡镜/全景重建",
        "evidence": "output/00_creator_docs/分镜.md → 场景站位",
        "fix_hint": "补写越轴过渡方式并声明新工作侧，或把该镜改回 A 侧"
      },
      {
        "id": "D11",
        "name": "运镜幅度 ≤30% 且速率 0.1–10%/秒",
        "level": "craft",
        "status": "pass",
        "actual": "越界 无",
        "expected": "单段累计 ≤30%，速率在 0.1–10%/s",
        "evidence": "output/00_creator_docs/剪辑单.md → 运镜",
        "fix_hint": "放慢或缩短该段；过高动态是 AI 视频人物变形的首要原因"
      },
      {
        "id": "D12",
        "name": "每镜单一戏剧目的且不重复",
        "level": "craft",
        "status": "pass",
        "actual": "唯一目的 12/12",
        "expected": "每镜一个可验收目的，不写「展示人物说话」这类空泛描述",
        "evidence": "input/demo/director.json → purpose",
        "fix_hint": "合并目的重复的镜头，或改写为具体戏剧作用"
      },
      {
        "id": "D13",
        "name": "起点→唯一动作→终点三态完整",
        "level": "blocker",
        "status": "pass",
        "actual": "缺失 无",
        "expected": "每镜三态齐全且互不重复",
        "evidence": "input/demo/director.json",
        "fix_hint": "冻结关键帧只写起点可见内容；终点另写，不写成动作链"
      },
      {
        "id": "D14",
        "name": "前 3 秒强冲突钩子",
        "level": "craft",
        "status": "pass",
        "actual": "前 3 秒抛出代签指控，把冲突直接摆上桌",
        "expected": "第一镜直接抛冲突台词或画面",
        "evidence": "input/demo/director.json S01",
        "fix_hint": "把最强冲突前置到 0–3 秒，不要铺垫环境"
      },
      {
        "id": "D15",
        "name": "集尾留悬念引导下一集",
        "level": "craft",
        "status": "pass",
        "actual": "留悬念引导下一集，机位穿轴重建空间 / 这页，只是第一份。",
        "expected": "末镜目的或台词含追更钩子",
        "evidence": "input/demo/director.json 末镜",
        "fix_hint": "把未解信息留到末镜，台词指向后续而非收束剧情"
      },
      {
        "id": "D16",
        "name": "付费生产前预览 + 指纹明确确认",
        "level": "blocker",
        "status": "pass",
        "actual": "job=JOB-C69345C8 fp=c69345c89071 任务=12；确认=有效",
        "expected": "prepare → 展示预览 → CONFIRM <job_id> <fingerprint[:12]> → run",
        "evidence": "output/00_previs/production_jobs.json / CONFIRM",
        "fix_hint": "任何 prompt/参考/参数/输出变化都会使旧确认失效，须重新预览确认"
      },
      {
        "id": "D17",
        "name": "画幅帧率一致且宽高为偶数",
        "level": "blocker",
        "status": "pass",
        "actual": "1080×1920 @ 30fps",
        "expected": "9:16 1080×1920，宽高偶数（yuv420p）",
        "evidence": "config/project.json / output/00_creator_docs/剪辑单.md",
        "fix_hint": "奇数边在 4:2:0 编码下会失败，改回偶数尺寸"
      },
      {
        "id": "D18",
        "name": "对白镜 ≥1.2s、静帧段 ≥0.50s",
        "level": "craft",
        "status": "pass",
        "actual": "过短镜 无；最短 5.00s",
        "expected": "对白镜 ≥1.20s",
        "evidence": "input/demo/storyboard.json",
        "fix_hint": "延长镜头或并入相邻镜"
      },
      {
        "id": "D19",
        "name": "同框说话人绑定（不说话正脸须闭嘴）",
        "level": "craft",
        "status": "pass",
        "actual": "需人工复核镜 无",
        "expected": "台词紧跟主动作；同框其他正脸明写闭嘴",
        "evidence": "output/00_creator_docs/视频提示词.md",
        "fix_hint": "双人镜在负面约束里写『不让两人同时张嘴』，避免口型落到更显眼的正脸"
      },
      {
        "id": "D20",
        "name": "剪辑单出点−入点==时长",
        "level": "blocker",
        "status": "pass",
        "actual": "记录 12 段，算术异常 0",
        "expected": "每段 |出−入−时长| ≤0.005s 且入点非负",
        "evidence": "output/00_creator_docs/剪辑单.md",
        "fix_hint": "修正入出点或时长，不得写时间码/帧号"
      }
    ],
    "source": "drama-skills / shuohao-skills 确定性门 + 小云雀预演规则",
    "note": "所有门均为纯字符串/数值比较，不调用模型、不产生费用；craft 级为创作建议，不作为阻断"
  },
  "shot_qc": {
    "summary": {
      "total": 12,
      "pass": 12,
      "warn": 0,
      "fail": 0,
      "generated_video_shots": 1,
      "local_parallax_shots": 11,
      "retake_list": [],
      "note": "画面级「像不像同一个人 / 动作是否好看」不由脚本下结论，见人工确认门"
    },
    "shots": [
      {
        "shot_id": "S01",
        "channel": "generated_video",
        "status": "pass",
        "metrics": {
          "motion": 8.921,
          "motion_peak": 11.571,
          "luma": 61.98,
          "black_bars": false,
          "subtitle_pixels": 339,
          "repeat_corr_with_prev": null,
          "luma_jump_with_prev": null,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S01_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S02",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 5.493,
          "motion_peak": 5.687,
          "luma": 50.48,
          "black_bars": false,
          "subtitle_pixels": 298,
          "repeat_corr_with_prev": 0.6725,
          "luma_jump_with_prev": 11.5,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S02_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S03",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 1.859,
          "motion_peak": 2.007,
          "luma": 50.45,
          "black_bars": false,
          "subtitle_pixels": 289,
          "repeat_corr_with_prev": 0.9045,
          "luma_jump_with_prev": 0.03,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S03_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S04",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 4.75,
          "motion_peak": 5.059,
          "luma": 51.85,
          "black_bars": false,
          "subtitle_pixels": 249,
          "repeat_corr_with_prev": 0.9186,
          "luma_jump_with_prev": 1.4,
          "duration_actual_s": 7.0,
          "duration_expected_s": 7.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S04_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S05",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 1.156,
          "motion_peak": 1.233,
          "luma": 62.72,
          "black_bars": false,
          "subtitle_pixels": 301,
          "repeat_corr_with_prev": 0.6587,
          "luma_jump_with_prev": 10.87,
          "duration_actual_s": 5.0,
          "duration_expected_s": 5.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S05_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S06",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 4.445,
          "motion_peak": 6.016,
          "luma": 51.57,
          "black_bars": false,
          "subtitle_pixels": 206,
          "repeat_corr_with_prev": 0.8157,
          "luma_jump_with_prev": 11.15,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S06_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S07",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 2.007,
          "motion_peak": 2.995,
          "luma": 61.07,
          "black_bars": false,
          "subtitle_pixels": 235,
          "repeat_corr_with_prev": 0.7946,
          "luma_jump_with_prev": 9.5,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S07_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S08",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 1.325,
          "motion_peak": 1.442,
          "luma": 55.55,
          "black_bars": false,
          "subtitle_pixels": 53,
          "repeat_corr_with_prev": 0.8224,
          "luma_jump_with_prev": 5.52,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S08_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S09",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 5.531,
          "motion_peak": 6.052,
          "luma": 58.69,
          "black_bars": false,
          "subtitle_pixels": 258,
          "repeat_corr_with_prev": 0.8344,
          "luma_jump_with_prev": 3.14,
          "duration_actual_s": 7.0,
          "duration_expected_s": 7.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S09_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S10",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 6.0,
          "motion_peak": 6.107,
          "luma": 49.89,
          "black_bars": false,
          "subtitle_pixels": 301,
          "repeat_corr_with_prev": 0.8167,
          "luma_jump_with_prev": 8.8,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S10_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S11",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 11.128,
          "motion_peak": 11.174,
          "luma": 53.35,
          "black_bars": false,
          "subtitle_pixels": 269,
          "repeat_corr_with_prev": 0.8782,
          "luma_jump_with_prev": 3.46,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S11_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      },
      {
        "shot_id": "S12",
        "channel": "local_parallax",
        "status": "pass",
        "metrics": {
          "motion": 4.597,
          "motion_peak": 4.929,
          "luma": 58.54,
          "black_bars": false,
          "subtitle_pixels": 223,
          "repeat_corr_with_prev": 0.7483,
          "luma_jump_with_prev": 5.19,
          "duration_actual_s": 6.0,
          "duration_expected_s": 6.0,
          "audio_drift_s": 0.0
        },
        "issues": [],
        "retake_hint": "无需返工",
        "evidence": "output/07_reports/qc_frames/S12_01.png",
        "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置"
      }
    ],
    "thresholds": {
      "motion_min": 0.35,
      "strong_motion": 3.0,
      "repeat_hist_corr": 0.965,
      "cut_jump_notice": 20.0
    }
  },
  "previs": {
    "path": "output/00_previs/previs.json",
    "shot_count": 12,
    "total_duration_s": 73.0,
    "avg_shot_s": 6.08,
    "motion_budget": {
      "fixed_shots": 4,
      "moving_shots": 8,
      "max_move_pct": 18,
      "avg_move_pct": 4.83,
      "medium_dynamic_shots": 1,
      "note": "低动态为主、单镜中动态作高潮；这是小云雀降低抽卡率的核心预演约束"
    },
    "production_jobs": 12,
    "fingerprint": "c69345c89071b2e7f239ec92cef9c76d74d21d1b8a53be8d8907a09642551e01"
  }
};
window.__SHIXIANG_SNAPSHOT_AT__ = "2026-11-12T20:21:32+08:00";

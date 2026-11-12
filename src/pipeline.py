#!/usr/bin/env python3
"""时象助手 · 本地真人漫剧制作 Agent —— 主流水线

用法：
    python3 src/pipeline.py --input input/demo --auto-approve     # 无人值守跑通 demo
    python3 src/pipeline.py --input input/demo                    # 在每个人工门处暂停，等人查验
    python3 src/pipeline.py --from 03_frames                      # 从某环节重跑（人工驳回后）
    python3 src/pipeline.py --only 03_frames                      # 只重跑某一环节

每条命令即时把状态写入 output/status.json；打开 console/index.html 可随时查验。
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import providers as P          # noqa: E402
import gates as G              # noqa: E402
import compliance              # noqa: E402
import director as D           # noqa: E402
import quality as Q            # noqa: E402

STAGES = [
    {"id": "00_previs",      "name": "导演台预演与质量门",   "owner": "导演 Agent", "gate": None},
    {"id": "01_script",      "name": "剧本与合规预审",       "owner": "制片 Agent", "gate": "G1"},
    {"id": "02_characters",  "name": "角色资产与一致性锁定", "owner": "美术 Agent", "gate": "G2"},
    {"id": "03_frames",      "name": "真人帧 → 漫画化转绘",  "owner": "转绘 Agent", "gate": "G3"},
    {"id": "04_clips",       "name": "逐镜生产（真视频/视差）", "owner": "动画 Agent", "gate": None},
    {"id": "05_audio",       "name": "本地配音 / BGM / 音效", "owner": "声音 Agent", "gate": "G4"},
    {"id": "06_final",       "name": "字幕 / 合成 / 导出",   "owner": "剪辑 Agent", "gate": None},
    {"id": "07_reports",     "name": "逐镜质检 + 逐条验收",  "owner": "质检 Agent", "gate": "G5"},
]

RED_FLAG_WORDS = ("灵异", "鬼神", "超自然", "血腥", "缅北", "以暴制暴", "畸形婚恋", "封建迷信")


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def dump(root: Path, status: dict) -> None:
    p = root / "output/status.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(status, ensure_ascii=False, indent=2)
    p.write_text(payload, encoding="utf-8")
    # 同步写一份 JS 快照：<script src> 不受 file:// 的 CORS 限制，
    # 因此双击 console/index.html 也能立刻看到本机真实数据（含跑到一半的进度）。
    djs = root / "console/data.js"
    djs.parent.mkdir(parents=True, exist_ok=True)
    djs.write_text(
        "/* 由 pipeline.py 自动生成：本机真实查验数据快照，勿手工编辑 */\n"
        "window.__SHIXIANG_STATUS__ = " + payload + ";\n"
        "window.__SHIXIANG_SNAPSHOT_AT__ = " + json.dumps(now()) + ";\n",
        encoding="utf-8")


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def art(label: str, rel: str, kind: str = "file") -> dict:
    return {"label": label, "path": rel, "type": kind}


def base_status(cfg: dict, sb: dict, args) -> dict:
    return {
        "schema_version": "1.0",
        "project": "时象助手 · 本地真人漫剧制作 Agent",
        "episode_title": sb["episode"]["title"],
        "episode_id": sb["episode"]["id"],
        "run_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "generated_at": now(),
        "mode": "demo" if args.auto_approve else "human-in-the-loop",
        "ffmpeg_bin": P.get_ffmpeg(),
        "input_dir": args.input,
        "config": {"width": cfg["width"], "height": cfg["height"], "fps": cfg["fps"],
                   "providers": cfg["providers"]},
        "overall": {"status": "WARN", "score": 0, "total": 0, "passed": 0,
                    "warned": 0, "failed": 0, "blocker_failed": 0},
        "stages": [], "checks": [], "shots": [], "human_gates": G.all_gates(ROOT),
        "final_video": "", "cover": "", "report_md": "output/07_reports/compliance_report.md",
        "notes": [],
    }


# ---------------------------------------------------------------------------
# 各环节
# ---------------------------------------------------------------------------


def stage_00_previs(ctx) -> dict:
    """导演台：五份创作文档 → 整组镜头预演 → 生产预览/指纹确认 → 20 条确定性门。

    对应小云雀「资产锁定 + 导演台预演」，以及 drama-skills / shuohao-skills 的
    「脚本判定质量门 + 生产前明确确认」。此环节不调任何模型、零费用。
    """
    root, cfg, sb, ch, inp = ctx["root"], ctx["cfg"], ctx["sb"], ctx["characters"], ctx["input"]
    dr = ctx.get("director")
    if not dr:
        return {"status": "warn",
                "summary": "输入目录缺少 director.json，跳过导演台；将退化为 v1 静帧流程",
                "artifacts": [], "commands": []}
    script = (inp / "script.md").read_text(encoding="utf-8")
    docs = D.build_creator_docs(root, sb, ch, dr, script, cfg)
    previs = D.previsualize(root, sb, dr, cfg)
    jobs = D.production_preview(root, sb, dr, cfg)

    # 四步硬闸门：prepare → 预览 → CONFIRM → run。
    # --auto-approve 是演示模式，由流水线代写并明确标注，不冒充人工确认。
    args = ctx["args"]
    confirmed = (root / "output/00_previs/CONFIRM").is_file()
    if args.auto_approve and not confirmed:
        token = f"CONFIRM {jobs['job_id']} {jobs['fingerprint'][:12]}"
        D.confirm(root, token)
        ctx["status"].setdefault("notes", []).append(
            "演示模式：D16 生产确认门由流水线代写 CONFIRM 令牌；正式投产须由人阅读 "
            "output/00_previs/production_preview.md 后自行确认（或用 --confirm 提交令牌）。")
    elif args.confirm:
        r = D.confirm(root, args.confirm if args.confirm != "auto" else
                      f"CONFIRM {jobs['job_id']} {jobs['fingerprint'][:12]}")
        if not r["ok"]:
            return {"status": "fail", "summary": "生产确认失败：" + r["reason"],
                    "artifacts": [], "commands": []}
    gates = D.run_gates(root, sb, ch, dr, script, cfg)
    ctx["status"]["director_gates"] = gates
    ctx["status"]["previs"] = {
        "path": "output/00_previs/previs.json",
        "shot_count": previs["shot_count"], "total_duration_s": previs["total_duration_s"],
        "avg_shot_s": previs["avg_shot_s"],
        "motion_budget": previs["motion_budget"],
        "production_jobs": jobs["count"],
        "fingerprint": jobs["fingerprint"],
    }
    arts = [art("导演台预演表", "output/00_previs/previs.md", "text"),
            art("预演数据（轴线/运动预算/时间线）", "output/00_previs/previs.json", "json"),
            art("生产预览（未确认不产生费用）", "output/00_previs/production_preview.md", "text"),
            art("生产任务与指纹", "output/00_previs/production_jobs.json", "json"),
            art("20 条确定性质量门结果", "output/00_previs/director_gates.json", "json")]
    arts += [art(f"创作文档 · {d}", f"output/00_creator_docs/{d}", "text") for d in D.DOCS]
    s = gates["summary"]
    return {
        "status": "fail" if s["blocker_failed"] else ("warn" if s["failed"] or s["warned"] else "pass"),
        "summary": (f"{previs['shot_count']} 镜预演 / 集长 {previs['total_duration_s']}s / "
                    f"运动预算 固定{previs['motion_budget']['fixed_shots']}镜；"
                    f"质量门 {s['passed']}通过 {s['warned']}待确认 {s['failed']}不通过；"
                    f"生产任务 {jobs['count']} 镜待明确确认（指纹 {jobs['fingerprint'][:12]}）"),
        "artifacts": arts,
        "commands": ["director.build_creator_docs() → 五份创作文档（含连续性锁与 REF 槽位）",
                     "director.previsualize() → 整组镜头时间线 / 轴线 / 运动预算",
                     "director.production_preview() → 只出预览与指纹，绝不调用生成接口",
                     "director.run_gates() → 20 条纯字符串/数值门，不调模型"],
    }


def stage_01_script(ctx) -> dict:
    root, cfg, sb, inp = ctx["root"], ctx["cfg"], ctx["sb"], ctx["input"]
    dst = root / "output/01_script"
    dst.mkdir(parents=True, exist_ok=True)
    shutil.copy2(inp / "script.md", dst / "script.md")
    shutil.copy2(inp / "storyboard.json", dst / "storyboard.json")
    shots = sb["shots"]
    total = round(sum(float(s["duration_s"]) for s in shots), 2)
    # 只扫剧本正文、梗概、钩子、台词与画面描述；
    # style.negative_prompt 里本来就写着"灵异/血腥"等排除词，不能算作题材命中
    scan_text = "\n".join(
        [(inp / "script.md").read_text(encoding="utf-8"),
         sb["episode"].get("logline", ""), sb["episode"].get("hook_3s", "")]
        + [s.get("visual_prompt", "") + " " + s.get("dialogue", {}).get("text", "")
           + " " + s.get("subtitle", "") for s in shots]
    )
    flags = [w for w in RED_FLAG_WORDS if w in scan_text]
    long_lines = [s["id"] for s in shots if len(s.get("dialogue", {}).get("text", "")) > 24]
    pre = {
        "shot_count": len(shots), "total_duration_s": total,
        "hook_3s": sb["episode"].get("hook_3s", ""),
        "hook_ok": bool(sb["episode"].get("hook_3s")),
        "red_flag_words": flags, "red_flag_pass": not flags,
        "dialogue_over_24_chars": long_lines,
        "style_locked": all(k in sb.get("style", {}) for k in ("name", "prompt_prefix", "negative_prompt")),
        "checked_at": now(),
    }
    dump_json(dst / "precheck.json", pre)
    return {
        "status": "pass" if not flags and not long_lines else "warn",
        "summary": f"{len(shots)} 镜 / {total}s；前3秒钩子已配置；题材红线扫描 {len(flags)} 项命中；超长台词 {len(long_lines)} 条",
        "artifacts": [art("人可读剧本", "output/01_script/script.md", "text"),
                      art("结构化分镜", "output/01_script/storyboard.json", "json"),
                      art("合规预审记录", "output/01_script/precheck.json", "json")],
        "commands": ["copy script.md / storyboard.json → output/01_script/",
                     "题材红线关键词扫描 + 台词长度 + 画风锁定校验"],
    }


def stage_02_characters(ctx) -> dict:
    from PIL import Image, ImageDraw, ImageFont
    root, cfg, sb, inp = ctx["root"], ctx["cfg"], ctx["sb"], ctx["input"]
    ch = ctx["characters"]
    dst = root / "output/02_characters"
    (dst / "character_sheets").mkdir(parents=True, exist_ok=True)
    shutil.copy2(inp / "characters.json", dst / "characters.json")
    font_path = root / cfg["font_local"]
    try:
        f_big = ImageFont.truetype(str(font_path), 62)
        f_mid = ImageFont.truetype(str(font_path), 34)
    except Exception:
        f_big = f_mid = ImageFont.load_default()

    voices = set()
    import subprocess
    try:
        out = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, timeout=20).stdout
        voices = {line.split()[0] for line in out.splitlines() if line.strip()}
    except Exception:
        pass

    report = {"checked_at": now(), "characters": [], "all_voice_available": True,
              "anchor_min_required": 3}
    for i, c in enumerate(ch["characters"]):
        anchors = c.get("identity_anchors", [])
        appear = sum(1 for s in sb["shots"] if c["name"] in s.get("characters", []))
        voice_ok = (not voices) or c["voice"] in voices
        report["all_voice_available"] &= bool(voice_ok)
        report["characters"].append({
            "name": c["name"], "role": c["role"], "voice": c["voice"],
            "voice_available": bool(voice_ok), "anchor_count": len(anchors),
            "anchors": anchors, "shots_appeared": appear,
            "consistency_strategy": "统一风格底图 + 逐镜刚性锚点描述 + 同一 LUT，跨镜不重新抽卡",
        })
        img = Image.new("RGB", (900, 1200), (236, 240, 243))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 900, 14), fill=(38, 52, 62))
        d.text((60, 70), c["name"], font=f_big, fill=(24, 32, 40))
        d.text((60, 165), f"{c['role']}  ·  音色 {c['voice']}", font=f_mid, fill=(80, 94, 104))
        d.text((60, 260), c.get("appearance", ""), font=f_mid, fill=(40, 50, 58))
        d.line((60, 340, 840, 340), fill=(170, 182, 190), width=2)
        d.text((60, 380), "刚性身份锚点（跨镜锁定）", font=f_mid, fill=(24, 32, 40))
        for j, a in enumerate(anchors):
            d.text((80, 450 + j * 72), f"{j + 1}. {a}", font=f_mid, fill=(44, 58, 68))
        d.text((60, 1000), f"出场镜头 {appear}  ·  配音可用 {'是' if voice_ok else '否'}",
               font=f_mid, fill=(80, 94, 104))
        d.text((60, 1080), f"画风：{sb['style']['name']}", font=f_mid, fill=(80, 94, 104))
        img.save(dst / "character_sheets" / f"{i + 1}_{c['name']}.png")
    dump_json(dst / "consistency_report.json", report)
    arts = [art("角色卡", "output/02_characters/characters.json", "json"),
            art("一致性报告", "output/02_characters/consistency_report.json", "json")]
    arts += [art(f"{c['name']} 定妆卡", f"output/02_characters/character_sheets/{i+1}_{c['name']}.png", "image")
             for i, c in enumerate(ch["characters"])]
    return {
        "status": "pass" if report["all_voice_available"] else "warn",
        "summary": f"{len(ch['characters'])} 个角色；锚点最少 {min(len(c.get('identity_anchors',[])) for c in ch['characters'])} 条；本机音色全部可用 {report['all_voice_available']}",
        "artifacts": arts,
        "commands": ["say -v ? 校验本机音色", "逐角色生成定妆卡 PNG 与一致性报告"],
    }


def stage_03_frames(ctx) -> dict:
    root, cfg, sb, inp = ctx["root"], ctx["cfg"], ctx["sb"], ctx["input"]
    recs = P.build_frames(root, inp, sb, cfg)
    # 同时把风格底图归档到 02，便于人工核对"是否全剧同一套 LUT"
    basedir = root / "output/02_characters/style_base"
    basedir.mkdir(parents=True, exist_ok=True)
    import cv2
    for src in sorted((inp / "frames").glob("*.jpg")) + sorted((inp / "frames").glob("*.png")):
        raw = cv2.imread(str(src), cv2.IMREAD_COLOR)
        if raw is None:
            continue
        cv2.imwrite(str(basedir / f"{src.stem}.png"),
                    P.comicify(P._fit_vertical(raw, cfg, True), cfg))
    dump_json(root / "output/03_frames/frame_manifest.json", recs)
    luma = P.match_shot_luma(root, sb, cfg, strength=0.7)
    dump_json(root / "output/03_frames/luma_match.json", luma)
    n_direct = sum(1 for r in recs if r["source_kind"] == "真人参考帧转绘")
    arts = [art("逐镜来源与处理链", "output/03_frames/frame_sources.csv", "csv"),
            art("帧清单（JSON）", "output/03_frames/frame_manifest.json", "json"),
            art("跨镜接镜亮度匹配（70%）", "output/03_frames/luma_match.json", "json"),
            art("统一风格底图目录", "output/02_characters/style_base/", "dir")]
    arts += [art(f"{r['shot_id']} 转绘帧", r["frame"], "image") for r in recs]
    return {
        "status": "pass",
        "summary": (f"{len(recs)} 帧 {cfg['width']}×{cfg['height']}；{n_direct} 张真人源帧转绘 + "
                    f"{len(recs)-n_direct} 张同风格派生；水印已本地裁切；"
                    f"跨镜亮度向中位数 {luma.get('target_luma')} 拉近 70%"),
        "artifacts": arts,
        "commands": ["去水印裁切 → 9:16 居中裁切 → 双边滤波/色阶量化/自适应描线/网点/统一冷调LUT/暗角",
                     "按 DERIVE_MAP 派生不同景别，逐镜写入 frame_sources.csv",
                     "match_shot_luma(strength=0.7)：增益限 0.6–1.6，消除硬切亮度跳变"],
        "frame_records": recs,
    }


def stage_04_clips(ctx) -> dict:
    """逐镜生产：WorkBuddy 生成的真动态视频优先，缺镜用本地多层视差兜底。

    这一层就是「小云雀模式」的逐镜生成 + 片段重拍边界：
    某一镜有问题只需替换 input/<项目>/generated_video/<Sxx>.mp4，
    再跑 --retake Sxx 即可，不会推翻整集。
    """
    root, cfg, sb = ctx["root"], ctx["cfg"], ctx["sb"]
    ff, font = ctx["ffmpeg"], ctx["font"]
    outdir = root / "output/04_clips"
    outdir.mkdir(parents=True, exist_ok=True)
    gen_dir = ctx["input"] / "generated_video"
    dmap = {d["id"]: d for d in ctx.get("director", {}).get("shots", [])}
    retake = ctx["args"].retake
    log = []
    for i, shot in enumerate(sb["shots"]):
        sid = shot["id"]
        out = outdir / f"{sid}.mp4"
        src = gen_dir / f"{sid}.mp4"
        if retake and sid not in retake and out.is_file():
            log.append({"shot_id": sid, "ok": True, "motion": "沿用上次结果",
                        "channel": "unchanged", "source_video": "",
                        "duration_s": shot["duration_s"], "stderr": ""})
            continue
        r = P.make_clip(shot, root / f"output/03_frames/{sid}.png", out,
                        root, cfg, ff, font, is_first=(i == 0),
                        source_video=src if src.is_file() else None,
                        dshot=dmap.get(sid), is_last=(i == len(sb["shots"]) - 1))
        log.append({"shot_id": sid, "ok": r["ok"], "motion": r["motion"],
                    "channel": r["channel"], "source_video": r["source_video"],
                    "comicify": r.get("comicify", {}),
                    "duration_s": shot["duration_s"],
                    "stderr": r["stderr"] if not r["ok"] else "", "cmd": r["cmd"]})
    dump_json(outdir / "clip_render_log.json", log)
    channels = {x["shot_id"]: x["channel"] for x in log if x["channel"] != "unchanged"}
    # 沿用上次结果时，从旧 channel_map 补齐
    cm_path = outdir / "channel_map.json"
    if cm_path.is_file():
        old = json.loads(cm_path.read_text(encoding="utf-8"))
        for k, v in old.items():
            channels.setdefault(k, v)
    dump_json(cm_path, channels)
    ctx["channel_map"] = channels
    n_gen = sum(1 for v in channels.values() if v == "generated_video")
    ok = all(x["ok"] for x in log)
    return {
        "status": "pass" if ok else "fail",
        "summary": (f"{sum(x['ok'] for x in log)}/{len(log)} 镜头；"
                    f"真动态视频 {n_gen} 镜（逐帧本地转绘、去模型水印、对齐全片 LUT）"
                    f" / 本地多层视差 {len(channels)-n_gen} 镜；"
                    f"逐句字幕时段 + 插入镜闪白 + 片头 AI 标识 + 末镜淡出"),
        "artifacts": [art("逐镜生产日志（含通道与来源）", "output/04_clips/clip_render_log.json", "json"),
                      art("逐镜通道映射", "output/04_clips/channel_map.json", "json")]
                     + [art(f"{x['shot_id']} 镜头片段 · {x['channel']}",
                            f"output/04_clips/{x['shot_id']}.mp4", "video") for x in log],
        "commands": ["真视频通道：ffmpeg -i generated_video/<Sxx>.mp4 -filter_complex scale/crop/fps/tpad/trim,drawtext -an ...",
                     "视差通道：ffmpeg -loop 1 -i <frame>.png -loop 1 -i light_overlay.png "
                     "-filter_complex zoompan,eq,noise,vignette,overlay,drawtext ...",
                     "片段重拍：替换 input/<项目>/generated_video/<Sxx>.mp4 后执行 --retake Sxx"],
        "clip_log": log,
    }


def stage_05_audio(ctx) -> dict:
    root, cfg, sb = ctx["root"], ctx["cfg"], ctx["sb"]
    ff = ctx["ffmpeg"]
    ch = ctx["characters"]
    vmap = {c["name"]: c["voice"] for c in ch["characters"]}
    outdir = root / "output/05_audio"
    outdir.mkdir(parents=True, exist_ok=True)
    per_shot, voice_log = [], []
    for shot in sb["shots"]:
        sid = shot["id"]
        text = shot["dialogue"]["text"]
        voice = vmap.get(shot["dialogue"]["speaker"], "Eddy")
        raw = outdir / f"{sid}_voice.wav"
        v = P.synth_voice(text, voice, raw, root, cfg, ff)
        mixed = outdir / f"{sid}.wav"
        m = P.mix_shot_audio(raw, shot.get("sfx", []), float(shot["duration_s"]), mixed, cfg)
        per_shot.append(mixed)
        voice_log.append({"shot_id": sid, "speaker": shot["dialogue"]["speaker"],
                          "text": text, "voice": v["voice"], "tts_duration_s": v["duration_s"],
                          "shot_duration_s": shot["duration_s"], "mix": m})
    total = float(sum(float(s["duration_s"]) for s in sb["shots"]))
    track = P.build_voice_track(sb["shots"], per_shot, outdir / "voice_track.wav", cfg)
    bgm = P.synth_bgm(total, outdir / "bgm.wav", cfg)
    dump_json(outdir / "audio_sync.json", {"per_shot": voice_log,
                                           "voice_track": track, "bgm": bgm,
                                           "sync_method": "每镜音轨长度强制等于 duration_s，首尾相接后与 concat 视频时间轴逐帧对齐"})
    over = [x["shot_id"] for x in voice_log if x["tts_duration_s"] + 0.25 > float(x["shot_duration_s"])]
    return {
        "status": "warn" if over else "pass",
        "summary": f"{len(voice_log)} 段离线配音 + 音效；全片人声轨 {track['duration_s']}s，最大音画漂移 {track['max_drift_s']}s；BGM {bgm['duration_s']}s 本地合成",
        "artifacts": [art("音画同步时间轴", "output/05_audio/audio_sync.json", "json"),
                      art("全片人声轨", "output/05_audio/voice_track.wav", "audio"),
                      art("全片氛围 BGM", "output/05_audio/bgm.wav", "audio")]
                     + [art(f"{x['shot_id']} 混音", f"output/05_audio/{x['shot_id']}.wav", "audio")
                        for x in voice_log],
        "commands": ["say -v <voice> -r 165 -o <shot>.aiff '<台词>'  →  ffmpeg 转 44100Hz 双声道",
                     "numpy 合成音效/BGM → 按 duration_s 拼接 voice_track.wav"],
        "audio_log": voice_log, "track": track, "bgm": bgm, "total": total,
        "overlong": over,
    }


def stage_06_final(ctx) -> dict:
    root, cfg, sb = ctx["root"], ctx["cfg"], ctx["sb"]
    ff = ctx["ffmpeg"]
    clips = [root / f"output/04_clips/{s['id']}.mp4" for s in sb["shots"]]
    total = float(sum(float(s["duration_s"]) for s in sb["shots"]))
    final = root / "output/06_final/EP01.mp4"
    final.parent.mkdir(parents=True, exist_ok=True)
    res = P.concat_and_mux(clips, root / "output/05_audio/voice_track.wav",
                           root / "output/05_audio/bgm.wav", final,
                           root, cfg, ff, total)
    cover = P.make_cover(root / f"output/03_frames/{sb['shots'][0]['id']}.png",
                         sb["episode"]["title"], root / "output/06_final/cover.png",
                         root, cfg)
    # 字幕时间轴留档（画面字幕已在 04 阶段烧录）
    srt, t = [], 0.0
    for i, s in enumerate(sb["shots"], 1):
        d = float(s["duration_s"])
        srt.append(f"{i}\n{_srt(t)} --> {_srt(t+d-0.25)}\n{s['subtitle']}\n")
        t += d
    (final.parent / "EP01.srt").write_text("\n".join(srt), encoding="utf-8")
    (final.parent / "ai_label_notice.txt").write_text(
        f"{cfg['ai_label']}\n本片第一集前 {cfg['ai_label_seconds']}s 画面右上角有可见提示标识，"
        "MP4 comment 元数据亦写入相同标识。\n", encoding="utf-8")
    dump_json(final.parent / "export_probe.json", res.get("probe", {}))
    # 剪辑单回填成片实测（drama-skills short-drama-edit 交付闭环）
    src_edit = root / "output/00_creator_docs/剪辑单.md"
    if src_edit.is_file():
        pr0 = res.get("probe", {})
        back = ("\n\n## 成片实测回填\n"
                f"- 实际成片：`output/06_final/EP01.mp4`\n"
                f"- 实测画幅：{pr0.get('width')}×{pr0.get('height')} @ {pr0.get('fps')}fps\n"
                f"- 实测时长：{pr0.get('duration_s')}s / 目标 {total:.2f}s\n"
                f"- 视频编码：{pr0.get('codec')} / {pr0.get('bitrate_kbps')} kb/s\n"
                f"- 音频：{pr0.get('audio_codec')} {pr0.get('sample_rate')}Hz "
                f"{pr0.get('channels')}ch\n"
                f"- 交付响度：目标 {cfg.get('target_lufs', -16)} LUFS（末级 loudnorm 归一）；"
                "复核命令 `ffmpeg -i EP01.mp4 -af volumedetect -f null -`\n"
                "- 逐镜入出点、取舍理由与字幕原文见上文 CUT 记录；"
                "未采用镜头逐镜写明理由（本片为「无」）\n")
        (final.parent / "剪辑单.md").write_text(
            src_edit.read_text(encoding="utf-8") + back, encoding="utf-8")
    pr = res.get("probe", {})
    summary = (f"成片 EP01.mp4：{pr.get('width')}×{pr.get('height')} / "
               f"{pr.get('codec')} / {pr.get('duration_s')}s / "
               f"AAC {pr.get('sample_rate')}Hz；封面 {cover['size']}")
    if not res["ok"]:
        summary += "；合成失败：" + (res.get("stderr", "") or "未知错误")[:300]
    return {
        "status": "pass" if res["ok"] and pr.get("width") else "fail",
        "summary": summary,
        "artifacts": [art("★ 最终成片", "output/06_final/EP01.mp4", "video"),
                      art("封面（带描边剧名）", "output/06_final/cover.png", "image"),
                      art("剪辑单（逐镜入出点 + 实测回填）", "output/06_final/剪辑单.md", "text"),
                      art("字幕时间轴", "output/06_final/EP01.srt", "text"),
                      art("AI 标识留痕", "output/06_final/ai_label_notice.txt", "text"),
                      art("导出参数实测", "output/06_final/export_probe.json", "json")],
        "commands": ["ffmpeg -f concat -safe 0 -i concat_list.txt -c copy _concat.mp4",
                     "ffmpeg -i _concat.mp4 -i voice_track.wav -i bgm.wav -filter_complex amix -c:v copy -c:a aac -ar 44100 -ac 2 -metadata comment='AI 辅助制作' EP01.mp4"],
        "probe": res.get("probe", {}), "cover": cover, "stderr": res.get("stderr", ""),
    }


def _srt(sec: float) -> str:
    h = int(sec // 3600); m = int(sec % 3600 // 60); s = sec % 60
    return f"{h:02d}:{m:02d}:{int(s):02d},{int((s % 1) * 1000):03d}"


# ---------------------------------------------------------------------------
# 归档与报告
# ---------------------------------------------------------------------------


def write_archive(ctx) -> None:
    """创作链路留痕：红果审核要求的剧本记录 / 生成参数 / 工程文件 / 参考图授权状态。"""
    root, cfg, sb = ctx["root"], ctx["cfg"], ctx["sb"]
    rep = root / "output/07_reports"
    rep.mkdir(parents=True, exist_ok=True)
    lines = ["# 创作链路留痕（版权/审核材料）", "",
             f"- 作品：{sb['episode']['title']} {sb['episode']['id']}",
             f"- 生成时间：{now()}",
             f"- 制作方式：本地流水线，素材与中间产物均未上传第三方服务",
             f"- 可见 AI 提示标识：{cfg['ai_label']}（片头画面 + MP4 comment 元数据）", "",
             "## 逐环节记录", ""]
    for st in ctx["status"]["stages"]:
        lines += [f"### {st['id']} {st['name']}（{st['owner']}）",
                  f"- 结果：{st['status']} · {st.get('summary','')}"]
        for a in st.get("artifacts", []):
            lines.append(f"- 产物：`{a['path']}`（{a['label']}）")
        for c in st.get("commands", []):
            lines.append(f"- 命令/处理：{c}")
        lines.append("")
    (rep / "creation_chain.md").write_text("\n".join(lines), encoding="utf-8")
    dump_json(rep / "generation_params.json", {
        "project_config": cfg, "storyboard": sb, "characters": ctx["characters"],
        "ffmpeg": ctx["ffmpeg"], "generated_at": now(),
    })
    with (rep / "asset_licenses.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.writer(fh)
        wr.writerow(["素材", "路径", "来源", "授权状态", "投稿可用性"])
        for p in sorted((ctx["input"] / "frames").glob("*.jpg")):
            wr.writerow([p.name, f"input/{ctx['args'].input.split('/')[-1]}/frames/{p.name}",
                         "本地图像生成模型产出的示例参考帧",
                         "示例素材，仅用于流程演示；无第三方版权主张",
                         "正式投稿前必须替换为自有实拍或已授权素材"])
        wr.writerow(["BGM", "output/05_audio/bgm.wav", "numpy 算法本地合成",
                     "自有，无第三方素材", "可用"])
        wr.writerow(["音效", "output/05_audio/*.wav", "numpy 算法本地合成",
                     "自有，无第三方素材", "可用"])
        wr.writerow(["字体", cfg["font_local"], "macOS 系统字体，本地复制",
                     "系统随附；正式商用请核对字体授权", "需人工确认"])
    (rep / "originality_declaration.md").write_text(
        f"# 原创声明 / 不侵权承诺（模板）\n\n"
        f"作品《{sb['episode']['title']}》{sb['episode']['id']} 的剧本、分镜、角色设定、画面、配音与音乐由本人创作或由本地 AI 工具辅助生成，"
        "未侵犯第三方著作权、肖像权、名誉权及其他合法权益。\n\n"
        "- 参考图来源与授权状态见 asset_licenses.csv\n"
        "- 创作链路见 creation_chain.md，生成参数见 generation_params.json\n"
        "- 画面含可见 AI 提示标识，文件元数据含隐式 AIGC 标识\n\n"
        "> **待人工签署**：投稿前请填写作者姓名、身份证号、日期并签字；本文件为模板，不代表已完成签署。\n",
        encoding="utf-8")
    (rep / "ai_label_notice.txt").write_text(
        f"{cfg['ai_label']}｜每集片头明显位置可见标识 + AIGC 隐式元数据标识。\n", encoding="utf-8")
    # 初版报告：让归档完整性检查能看到该文件；07 阶段末会用完整版覆盖
    (rep / "compliance_report.md").write_text(
        f"# {sb['episode']['title']} 红果短剧验收报告\n\n生成中，请稍候刷新……\n\n{cfg['ai_label']}\n",
        encoding="utf-8")


def stage_07_reports(ctx) -> dict:
    root, sb = ctx["root"], ctx["sb"]
    write_archive(ctx)
    status = compliance.run(str(root), ctx["status"])
    ctx["status"] = status
    # 逐镜质检（客观测量，不下「像不像」的结论）
    cm = ctx.get("channel_map")
    cm_path = root / "output/04_clips/channel_map.json"
    if not cm and cm_path.is_file():
        try:
            cm = json.loads(cm_path.read_text(encoding="utf-8"))
        except Exception:
            cm = {}
    sync_path = root / "output/05_audio/audio_sync.json"
    sync = json.loads(sync_path.read_text(encoding="utf-8")) if sync_path.is_file() else None
    qc = Q.qc_all(root, sb, ctx["cfg"], ctx["ffmpeg"], cm or {}, sync)
    status["shot_qc"] = qc
    gd_path = root / "output/00_previs/director_gates.json"
    if not status.get("director_gates") and gd_path.is_file():
        status["director_gates"] = json.loads(gd_path.read_text(encoding="utf-8"))
    pv_path = root / "output/00_previs/previs.json"
    if not status.get("previs") and pv_path.is_file():
        pv = json.loads(pv_path.read_text(encoding="utf-8"))
        jp = root / "output/00_previs/production_jobs.json"
        jb = json.loads(jp.read_text(encoding="utf-8")) if jp.is_file() else {}
        status["previs"] = {"path": "output/00_previs/previs.json",
                            "shot_count": pv["shot_count"],
                            "total_duration_s": pv["total_duration_s"],
                            "avg_shot_s": pv["avg_shot_s"],
                            "motion_budget": pv["motion_budget"],
                            "production_jobs": jb.get("count", 0),
                            "fingerprint": jb.get("fingerprint", "")}
    # 把 32 条规则关联到具体环节，便于从时间线跳转查验
    by_stage = {}
    for c in status["checks"]:
        rid = c.get("rule_id", "")
        if rid.startswith("HG-RIGHT") or rid == "HG-CONT-01":
            key = "07_reports"
        elif rid in ("HG-CONT-05", "HG-CONT-07"):
            key = "02_characters"
        elif rid in ("HG-CONT-06", "HG-AV-02", "HG-AV-03"):
            key = "03_frames"
        elif rid in ("HG-AV-04", "HG-AV-01", "HG-TECH-12"):
            key = "05_audio"
        elif rid.startswith("HG-TECH") or rid == "HG-AV-05":
            key = "06_final"
        else:
            key = "01_script"
        by_stage.setdefault(key, []).append(c["id"])
    for st in status["stages"]:
        st["checks"] = by_stage.get(st["id"], [])

    o = status["overall"]
    lines = [
        f"# 《{sb['episode']['title']}》{sb['episode']['id']} · 红果短剧验收报告", "",
        f"- 生成时间：{status['generated_at']}",
        f"- 成片：`{status.get('final_video','')}`",
        f"- 综合状态：**{o['status']}**，符合度 **{o['score']}/100**",
        f"- 规则合计 {o['total']} 条：通过 {o['passed']} / 需人工核验 {o['warned']} / 不通过 {o['failed']}（blocker 不通过 {o['blocker_failed']}）", "",
        "> 说明：标 `warn` 的项目多为画面级、法律效力级判定（如画风一致性、参考图授权、AIGC 隐式标识），"
        "机器无法替代人工结论，因此**不写死通过**，逐条列出人工核验方式。打开 `console/index.html` 可边看边勾。",
        "", "## 逐条验收结果", "",
        "| 规则 | 类别 | 级别 | 状态 | 期望 | 实测 | 证据 |",
        "|---|---|---|---|---|---|---|",
    ]
    for c in status["checks"]:
        actual = str(c.get("actual", "")).replace("|", "／").replace("\n", " ")[:220]
        lines.append(f"| {c['rule_id']} {c['name']} | {c['category']} | {c['severity']} | "
                     f"{c['status']} | {str(c.get('expected',''))[:60]} | {actual} | `{c.get('evidence','')}` |")
    lines += ["", "## 需人工核验项与核验方式", ""]
    for c in status["checks"]:
        if c["status"] == "warn":
            lines += [f"### {c['rule_id']} {c['name']}",
                      f"- 依据：{c.get('source','')}",
                      f"- 核验方式：{c.get('how_to_verify','')}",
                      f"- 实测线索：{c.get('actual','')}",
                      f"- 不合规时：{c.get('fix_hint','')}", ""]
    gd = status.get("director_gates", {}).get("summary", {})
    qs = qc["summary"]
    lines += ["", "## 小云雀导演台 · 确定性质量门", "",
              f"- 结果：{gd.get('status','—')} {gd.get('score','—')}/100；"
              f"{gd.get('total',0)} 门中通过 {gd.get('passed',0)} / 待确认 {gd.get('warned',0)} / 不通过 {gd.get('failed',0)}",
              "- 明细：`output/00_previs/director_gates.json`；预演：`output/00_previs/previs.md`",
              "- 生产预览与指纹：`output/00_previs/production_preview.md`（未确认不产生费用）", "",
              "| 门 | 名称 | 级别 | 状态 | 实测 |", "|---|---|---|---|---|"]
    for g in status.get("director_gates", {}).get("gates", []):
        lines.append(f"| {g['id']} | {g['name']} | {g['level']} | {g['status']} | "
                     f"{str(g['actual'])[:110].replace('|','／')} |")
    lines += ["", "## 逐镜质检与重拍清单", "",
              f"- 合计 {qs['total']} 镜：通过 {qs['pass']} / 提示 {qs['warn']} / 不通过 {qs['fail']}",
              f"- 真动态视频 {qs['generated_video_shots']} 镜 / 本地视差 {qs['local_parallax_shots']} 镜",
              f"- 建议重拍：`{', '.join(qs['retake_list']) or '无'}`",
              "- 逐镜测量：帧间运动量、黑边、字幕高亮像素、跨镜重复度、接镜亮度跳变、时长与音画漂移",
              "- 明细：`output/07_reports/shot_qc.json`；抽帧证据：`output/07_reports/qc_frames/`",
              "- 重拍方式：替换 `input/<项目>/generated_video/<Sxx>.mp4` 后执行 "
              "`python3 src/pipeline.py --input input/demo --retake Sxx --from 04_clips`", "",
              "| 镜 | 通道 | 状态 | 运动量 | 问题 | 建议 |", "|---|---|---|---|---|---|"]
    for r in qc["shots"]:
        m = r.get("metrics", {})
        lines.append(f"| {r['shot_id']} | {r['channel']} | {r['status']} | "
                     f"{m.get('motion','—')} | {'；'.join(r.get('issues',[]))[:90] or '—'} | "
                     f"{str(r.get('retake_hint',''))[:80]} |")
    lines += ["## 人工确认门", ""]
    for g in status["human_gates"]:
        lines.append(f"- {g['id']} {g['name']}：**{g['status']}** {g.get('note','')}")
    lines += ["", "## 创作链路与版权留痕", "",
              "- `output/07_reports/creation_chain.md`：逐环节输入/命令/产物",
              "- `output/07_reports/generation_params.json`：全部生成参数",
              "- `output/07_reports/asset_licenses.csv`：参考图来源与授权状态",
              "- `output/07_reports/originality_declaration.md`：原创声明模板（待人工签署）", "",
              f"本片标识：{ctx['cfg']['ai_label']}", ""]
    (root / "output/07_reports/compliance_report.md").write_text("\n".join(lines), encoding="utf-8")
    return {
        "status": "pass" if o["failed"] == 0 else "fail",
        "summary": (f"32 条规则：通过 {o['passed']} / 需人工核验 {o['warned']} / 不通过 {o['failed']}；"
                    f"逐镜质检 {qc['summary']['total']} 镜（真视频 {qc['summary']['generated_video_shots']} 镜）；"
                    f"综合 {o['status']} {o['score']}分"),
        "artifacts": [art("★ 验收报告（含质量门与逐镜质检）", "output/07_reports/compliance_report.md", "text"),
                      art("★ 查验台数据源", "output/status.json", "json"),
                      art("逐镜质检与重拍清单", "output/07_reports/shot_qc.json", "json"),
                      art("逐镜抽帧证据目录", "output/07_reports/qc_frames/", "dir"),
                      art("导演台质量门", "output/00_previs/director_gates.json", "json"),
                      art("导演台预演表", "output/00_previs/previs.md", "text"),
                      art("生产预览与指纹", "output/00_previs/production_preview.md", "text"),
                      art("创作链路留痕", "output/07_reports/creation_chain.md", "text"),
                      art("生成参数", "output/07_reports/generation_params.json", "json"),
                      art("素材授权台账", "output/07_reports/asset_licenses.csv", "csv"),
                      art("原创声明模板", "output/07_reports/originality_declaration.md", "text"),
                      art("人工确认门", "output/gates.json", "json")],
        "commands": ["compliance.run()：ffmpeg -i 解析成片 + 读取素材/归档，逐条执行 32 条规则",
                     "quality.qc_all()：逐镜抽帧测量运动量/黑边/字幕/重复度/接镜跳变/音画漂移",
                     "生成合规报告、逐镜重拍清单与人工核验清单"],
    }


STAGE_FUNCS = {
    "00_previs": stage_00_previs,
    "01_script": stage_01_script, "02_characters": stage_02_characters,
    "03_frames": stage_03_frames, "04_clips": stage_04_clips,
    "05_audio": stage_05_audio, "06_final": stage_06_final,
    "07_reports": stage_07_reports,
}


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser(description="时象助手 · 本地真人漫剧制作 Agent")
    ap.add_argument("--input", default="input/demo", help="基础材料目录（相对项目根）")
    ap.add_argument("--auto-approve", action="store_true", help="演示模式：人工门自动通过并标注仍需复核")
    ap.add_argument("--from", dest="from_stage", default="", help="从指定环节开始重跑")
    ap.add_argument("--only", default="", help="只重跑指定环节")
    ap.add_argument("--confirm", nargs="?", const="auto", default="",
                    help="提交生产确认令牌；给 auto 则用当前预览指纹自动生成")
    ap.add_argument("--retake", default="", help="只重拍指定镜，逗号分隔，如 S05,S09")
    args = ap.parse_args()
    args.retake = {x.strip() for x in args.retake.split(",") if x.strip()}
    root = ROOT
    inp = (root / args.input).resolve()
    cfg = json.loads((root / "config/project.json").read_text(encoding="utf-8"))
    sb = json.loads((inp / "storyboard.json").read_text(encoding="utf-8"))
    characters = json.loads((inp / "characters.json").read_text(encoding="utf-8"))
    dp = inp / "director.json"
    dr = json.loads(dp.read_text(encoding="utf-8")) if dp.is_file() else None
    ff = P.get_ffmpeg()
    font = P.prepare_font(root, cfg)
    if not font:
        print("[FATAL] 未找到可用中文字体", file=sys.stderr)
        return 2
    for d in ("00_previs", "00_creator_docs", "01_script", "02_characters",
              "03_frames", "04_clips", "05_audio", "06_final", "07_reports"):
        (root / "output" / d).mkdir(parents=True, exist_ok=True)

    prev = {}
    sp = root / "output/status.json"
    if sp.is_file():
        try:
            prev = json.loads(sp.read_text(encoding="utf-8"))
        except Exception:
            prev = {}
    status = base_status(cfg, sb, args)
    if args.from_stage or args.only:
        status["stages"] = list(prev.get("stages", []))
        status["shots"] = list(prev.get("shots", []))
        status["final_video"] = prev.get("final_video", "")
        status["cover"] = prev.get("cover", "")
    status["ffmpeg_bin"] = ff

    ctx = {"root": root, "cfg": cfg, "sb": sb, "characters": characters,
           "input": inp, "ffmpeg": ff, "font": font, "args": args,
           "director": dr, "status": status}
    # --from 断点续跑时把导演台与质检数据一并带回，查验台不会缺面板
    for key, rel in (("director_gates", "output/00_previs/director_gates.json"),
                     ("shot_qc", "output/07_reports/shot_qc.json")):
        p = root / rel
        if (args.from_stage or args.only) and p.is_file():
            try:
                status[key] = json.loads(p.read_text(encoding="utf-8"))
            except Exception:
                pass

    shots_map = {s["id"]: dict(s) for s in sb["shots"]}
    if not status["shots"]:
        for s in sb["shots"]:
            status["shots"].append({
                "id": s["id"], "duration_s": float(s["duration_s"]), "status": "pending",
                "frame": "", "clip": "", "audio": "", "subtitle": s.get("subtitle", ""),
                "issues": [],
            })

    start_idx = 0
    if args.from_stage:
        start_idx = next((i for i, s in enumerate(STAGES) if s["id"] == args.from_stage), 0)
    dump(root, status)

    print(f"=== 时象助手 · {sb['episode']['title']} {sb['episode']['id']} ===")
    print(f"ffmpeg: {ff}\n")

    for i, st in enumerate(STAGES):
        if args.only and st["id"] != args.only:
            continue
        if not args.only and i < start_idx:
            print(f"[skip ] {st['id']} {st['name']}（沿用上次记录）")
            continue
        # 移除旧记录，避免重复
        status["stages"] = [x for x in status["stages"] if x["id"] != st["id"]]
        t0 = time.time()
        print(f"[run  ] {st['id']} {st['name']} ...", flush=True)
        try:
            res = STAGE_FUNCS[st["id"]](ctx)
        except Exception as exc:
            import traceback
            traceback.print_exc()
            res = {"status": "fail", "summary": f"环节异常：{type(exc).__name__}: {exc}",
                   "artifacts": [], "commands": []}
        rec = {"id": st["id"], "name": st["name"], "owner": st["owner"],
               "status": res.get("status", "warn"), "duration_s": round(time.time() - t0, 2),
               "summary": res.get("summary", ""),
               "artifacts": res.get("artifacts", []), "checks": [],
               "commands": res.get("commands", [])}
        # 把产物回填到镜头级状态，供查验台逐镜查看
        if st["id"] == "03_frames":
            for r in res.get("frame_records", []):
                _shot(status, r["shot_id"])["frame"] = r["frame"]
        elif st["id"] == "04_clips":
            for x in res.get("clip_log", []):
                s = _shot(status, x["shot_id"])
                s["clip"] = f"output/04_clips/{x['shot_id']}.mp4"
                s["status"] = "pass" if x["ok"] else "fail"
                if not x["ok"]:
                    s["issues"].append("镜头渲染失败：" + x["stderr"][:120])
        elif st["id"] == "05_audio":
            for x in res.get("audio_log", []):
                s = _shot(status, x["shot_id"])
                s["audio"] = f"output/05_audio/{x['shot_id']}.wav"
                if x["shot_id"] in res.get("overlong", []):
                    s["issues"].append("配音超出镜头时长，需调整 tts_rate 或延长镜头")
        elif st["id"] == "06_final":
            status["final_video"] = "output/06_final/EP01.mp4"
            status["cover"] = "output/06_final/cover.png"
        elif st["id"] == "07_reports":
            status = ctx["status"]          # compliance.run 已就地补全 checks/overall

        if st["gate"]:
            gate = G.resolve(root, st["gate"], args.auto_approve)
            rec["gate"] = {k: gate.get(k, "") for k in ("id", "status", "note", "reviewer")}
        status["stages"].append(rec)
        status["human_gates"] = G.all_gates(root)
        status["generated_at"] = now()
        # 按 SPEC 顺序排列
        order = {s["id"]: n for n, s in enumerate(STAGES)}
        status["stages"].sort(key=lambda x: order.get(x["id"], 99))
        dump(root, status)
        print(f"        {rec['status']}  {rec['summary']}")

        if st["gate"] and rec["gate"]["status"] != "approved":
            print(G.pending_hint(root, gate))
            return 3
        if rec["status"] == "fail":
            print(f"\n[STOP] {st['id']} 未通过，已保留现场。修复后执行 --from {st['id']}")
            return 4

    o = status["overall"]
    print("\n=== 完成 ===")
    print(f"成片：{status.get('final_video') or '（未生成）'}")
    print(f"验收：{o['status']} {o['score']}/100  通过 {o['passed']} / 需人工核验 {o['warned']} / 不通过 {o['failed']}")
    print("查验台：console/index.html（双击打开；或 python3 -m http.server 8000 后访问 /console/）")
    return 0 if o["failed"] == 0 else 5


def _shot(status: dict, sid: str) -> dict:
    for s in status["shots"]:
        if s["id"] == sid:
            return s
    s = {"id": sid, "status": "pending", "frame": "", "clip": "", "audio": "",
         "subtitle": "", "issues": []}
    status["shots"].append(s)
    return s


if __name__ == "__main__":
    raise SystemExit(main())

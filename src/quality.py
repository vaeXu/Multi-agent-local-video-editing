#!/usr/bin/env python3
"""时象助手 v2 · 逐镜质检（小云雀「逐镜验收 + 片段重拍」）

全部为客观测量：帧间运动量、黑边、接镜亮度跳变、跨镜画面重复度、
字幕可读性、时长与音画漂移。脚本只回报事实与修复建议，
「像不像同一个人」「动作是否好看」仍留给人工门，不伪造成机器判定。
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import cv2
import numpy as np

# drama-skills edit_tool.py 的复核指引阈值
CUT_LEVEL_NOTICE_DB = 10.0
CUT_JUMP_NOTICE = 20.0
MOTION_MIN = 0.35          # 画面平均帧间差（0–255 灰阶）下限，低于此视为「几乎静止」
STRONG_MOTION = 3.0        # 真视频通常高于此
REPEAT_HIST_CORR = 0.965   # 相邻镜直方图相关高于此判为画面重复


def dump_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _extract(video: Path, outdir: Path, sid: str, ff: str, root) -> list[Path]:
    """每秒抽 1 帧、缩放后落盘，供客观测量。

    刻意不删除旧抽帧：批量删除会触发本机文件保护，也会让证据链断掉。
    ffmpeg -y 覆盖同名文件，再用「本轮写入时间」筛出本次产物。
    """
    import subprocess
    import time
    outdir.mkdir(parents=True, exist_ok=True)
    started = time.time() - 1.0
    pattern = str(outdir.relative_to(root) / f"{sid}_%02d.png")
    src = str(video.relative_to(root)) if str(video).startswith(str(root)) else str(video)
    cmd = [ff, "-y", "-hide_banner", "-loglevel", "error", "-i", src,
           "-vf", "fps=1,scale=270:480", "-frames:v", "7", pattern]
    subprocess.run(cmd, cwd=root, capture_output=True, timeout=180)
    return [p for p in sorted(outdir.glob(f"{sid}_*.png"))
            if p.stat().st_mtime >= started]


def _measure(frames: list[Path]) -> dict:
    imgs = [cv2.imread(str(p), cv2.IMREAD_COLOR) for p in frames]
    imgs = [i for i in imgs if i is not None]
    if not imgs:
        return {"frames": 0, "motion": 0.0, "luma": 0.0, "black_bars": None,
                "subtitle_pixels": 0, "hist": None}
    greys = [cv2.cvtColor(i, cv2.COLOR_BGR2GRAY) for i in imgs]
    diffs = [float(np.abs(a.astype(np.float32) - b.astype(np.float32)).mean())
             for a, b in zip(greys, greys[1:])]
    first = greys[0]
    h, w = first.shape
    edge = np.concatenate([first[:int(h * .03)].ravel(), first[-int(h * .03):].ravel(),
                           first[:, :int(w * .03)].ravel(), first[:, -int(w * .03):].ravel()])
    black_bars = bool(edge.mean() < 12 and edge.std() < 3)
    # 字幕区（底部 12%–22%）的高亮像素占比
    sub = greys[len(greys) // 2][int(h * .78):int(h * .90)]
    subtitle_pixels = int((sub > 205).sum())
    hist = cv2.calcHist([imgs[0]], [0, 1], None, [32, 32], [0, 256, 0, 256])
    cv2.normalize(hist, hist)
    return {"frames": len(imgs), "motion": round(float(np.mean(diffs)) if diffs else 0.0, 3),
            "motion_peak": round(max(diffs), 3) if diffs else 0.0,
            "luma": round(float(first.mean()), 2), "black_bars": black_bars,
            "subtitle_pixels": subtitle_pixels, "hist": hist}


def qc_all(root: Path, sb: dict, cfg: dict, ff: str,
           channel_map: dict[str, str], audio_sync: dict | None = None) -> dict:
    tmp = root / "output/07_reports/qc_frames"
    rows, prev = [], None
    retake = []
    for i, shot in enumerate(sb["shots"]):
        sid = shot["id"]
        video = root / f"output/04_clips/{sid}.mp4"
        channel = channel_map.get(sid, "local_parallax")
        issues, hints = [], []
        if not video.is_file():
            rows.append({"shot_id": sid, "channel": channel, "status": "fail",
                         "metrics": {}, "issues": ["镜头片段缺失"],
                         "retake_hint": "重跑 04_clips，或检查 ffmpeg 渲染日志"})
            retake.append(sid)
            continue
        frames = _extract(video, tmp, sid, ff, root)
        m = _measure(frames)
        # 1) 动态量
        if m["motion"] < MOTION_MIN:
            issues.append(f"画面几乎静止（帧间差 {m['motion']}）")
            hints.append("换用图生视频真动态，或加大导演台运镜幅度")
        if channel == "generated_video" and m["motion"] < STRONG_MOTION:
            issues.append(f"真视频通道但运动量偏低（{m['motion']} < {STRONG_MOTION}）")
            hints.append("检查是否误用了静帧或生成结果定格，必要时重拍该镜")
        # 2) 黑边 / 拉伸
        if m["black_bars"]:
            issues.append("检测到疑似黑边")
            hints.append("检查源素材画幅，重新做 9:16 居中裁切")
        # 3) 字幕可读性（阈值随台词字数缩放，避免「谁？」这类两字字幕被误报）
        chars = len(re.sub(r"[\s\W_]+", "", shot.get("subtitle", "")))
        need_px = max(45, 14 * chars)
        if m["subtitle_pixels"] < need_px and shot.get("subtitle"):
            issues.append(f"字幕区高亮像素偏少（{m['subtitle_pixels']} < {need_px}），可能未烧录或不可读")
            hints.append("检查 drawtext 字体路径与字幕时间窗")
        # 4) 跨镜重复
        repeat_corr = None
        if prev and prev.get("hist") is not None and m.get("hist") is not None:
            repeat_corr = round(float(cv2.compareHist(prev["hist"], m["hist"],
                                                      cv2.HISTCMP_CORREL)), 4)
            if repeat_corr > REPEAT_HIST_CORR and channel == "local_parallax":
                issues.append(f"与上一镜画面高度重复（直方图相关 {repeat_corr}）")
                hints.append("为该镜补一张独立真人源帧，不要从同图裁切派生")
        # 5) 接镜亮度跳变
        jump = None
        if prev:
            jump = round(abs(m["luma"] - prev["luma"]), 2)
            if jump > CUT_JUMP_NOTICE:
                issues.append(f"接镜亮度跳变 {jump} > {CUT_JUMP_NOTICE}，请回看切点")
                hints.append("统一 LUT 或在该镜写入接镜匹配")
        # 6) 时长与音画漂移
        expected = float(shot["duration_s"])
        probe = {}
        try:
            import providers as P
            probe = P.probe(video, ff)
        except Exception:
            pass
        actual = float(probe.get("duration_s") or 0)
        if actual and abs(actual - expected) > 0.12:
            issues.append(f"片段时长 {actual:.2f}s 与分镜 {expected:.2f}s 不符")
            hints.append("检查 trim/tpad 与 -t 参数")
        drift = 0.0
        if audio_sync:
            for x in audio_sync.get("voice_track", {}).get("timeline", []):
                if x.get("shot_id") == sid:
                    drift = abs(x.get("end_s", 0) - x.get("start_s", 0) - expected)
        if drift > 0.05:
            issues.append(f"音画漂移 {drift:.3f}s")
            hints.append("重跑 05_audio 让每镜音轨长度强制等于 duration_s")

        status = "fail" if any("缺失" in x or "不符" in x for x in issues) else (
            "warn" if issues else "pass")
        if status != "pass":
            retake.append(sid)
        rows.append({
            "shot_id": sid, "channel": channel, "status": status,
            "metrics": {"motion": m["motion"], "motion_peak": m.get("motion_peak", 0),
                        "luma": m["luma"], "black_bars": m["black_bars"],
                        "subtitle_pixels": m["subtitle_pixels"],
                        "repeat_corr_with_prev": repeat_corr,
                        "luma_jump_with_prev": jump,
                        "duration_actual_s": actual, "duration_expected_s": expected,
                        "audio_drift_s": round(drift, 4)},
            "issues": issues, "retake_hint": "；".join(hints) or "无需返工",
            "evidence": f"output/07_reports/qc_frames/{sid}_01.png",
            "how_to_verify": "打开该镜片段与抽帧，逐项复核动作可读性、角色一致性、字幕位置",
        })
        prev = m

    generated = sum(1 for r in rows if r["channel"] == "generated_video")
    summary = {
        "total": len(rows),
        "pass": sum(1 for r in rows if r["status"] == "pass"),
        "warn": sum(1 for r in rows if r["status"] == "warn"),
        "fail": sum(1 for r in rows if r["status"] == "fail"),
        "generated_video_shots": generated,
        "local_parallax_shots": len(rows) - generated,
        "retake_list": retake,
        "note": "画面级「像不像同一个人 / 动作是否好看」不由脚本下结论，见人工确认门",
    }
    res = {"summary": summary, "shots": rows,
           "thresholds": {"motion_min": MOTION_MIN, "strong_motion": STRONG_MOTION,
                          "repeat_hist_corr": REPEAT_HIST_CORR,
                          "cut_jump_notice": CUT_JUMP_NOTICE}}
    dump_json(root / "output/07_reports/shot_qc.json", res)
    return res

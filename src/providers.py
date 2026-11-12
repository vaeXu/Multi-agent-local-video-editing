"""时象助手 · 本地能力层（providers）

全部能力在本机完成：OpenCV 漫画化转绘、ffmpeg 微动效与合成、macOS 离线中文 TTS、
numpy 合成 BGM/音效。不上传任何素材。所有 ffmpeg 调用以项目根为 cwd 并使用相对路径，
以规避中文目录在 filter 表达式中的转义问题。

有 NVIDIA GPU 时可把 local_comicify / kenburns / macos_say 替换为
comfyui_v2v / AnimateDiff / Qwen3-TTS，接口保持不变。
"""

from __future__ import annotations

import csv
import json
import math
import os
import shutil
import subprocess
import wave
from pathlib import Path

import cv2
import numpy as np

# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------


def get_ffmpeg() -> str:
    """优先系统 ffmpeg，回退到 imageio-ffmpeg 自带的静态二进制。"""
    if shutil.which("ffmpeg"):
        return "ffmpeg"
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception as exc:
        raise RuntimeError("未找到 ffmpeg，请执行 pip install imageio-ffmpeg") from exc


def run(cmd: list[str], root: Path, timeout: int = 600) -> subprocess.CompletedProcess:
    """以项目根为 cwd 执行命令；返回 CompletedProcess，不因非零码抛异常。"""
    return subprocess.run(
        [str(x) for x in cmd], cwd=str(root), capture_output=True,
        text=True, timeout=timeout,
    )


def prepare_font(root: Path, cfg: dict) -> str:
    """把系统字体复制到无空格的相对路径，供 drawtext 使用。"""
    local = cfg.get("font_local", "config/font.ttc")
    dst = root / local
    if dst.is_file() and dst.stat().st_size > 1000:
        return local
    dst.parent.mkdir(parents=True, exist_ok=True)
    src = Path(cfg.get("font_source", ""))
    if not src.is_file():
        for cand in Path("/System/Library/Fonts").glob("*.ttc"):
            src = cand
            break
    if src.is_file():
        # 系统字体带受保护 flags，copy2 的 copystat 会触发 chflags 权限错误；只复制字节
        dst.write_bytes(src.read_bytes())
    return local if dst.is_file() else ""


def wav_write(path: Path, data: np.ndarray, rate: int = 44100) -> None:
    """写 16bit PCM 双声道 wav。data: (n,2) float32，范围 -1~1。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    arr = np.clip(data, -1.0, 1.0)
    pcm = (arr * 32767.0).astype("<i2")
    with wave.open(str(path), "wb") as fh:
        fh.setnchannels(2)
        fh.setsampwidth(2)
        fh.setframerate(rate)
        fh.writeframes(pcm.tobytes())


def wav_read(path: Path) -> tuple[np.ndarray, int]:
    with wave.open(str(path), "rb") as fh:
        rate = fh.getframerate()
        ch = fh.getnchannels()
        raw = fh.readframes(fh.getnframes())
    arr = np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32767.0
    if ch == 1:
        arr = np.repeat(arr[:, None], 2, axis=1)
    else:
        arr = arr.reshape(-1, ch)[:, :2]
    return arr, rate


def probe(video: Path, ffmpeg_bin: str) -> dict:
    """无 ffprobe，解析 ffmpeg -i 的 stderr。"""
    import re
    p = subprocess.run([ffmpeg_bin, "-hide_banner", "-i", str(video)],
                       capture_output=True, text=True, timeout=90)
    s = (p.stderr or "") + (p.stdout or "")
    out = {}
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", s)
    if m:
        out["duration_s"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    m = re.search(r"(\d{2,5})x(\d{2,5})", s)
    if m:
        out["width"], out["height"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"Video:\s*([A-Za-z0-9_]+)", s)
    if m:
        out["codec"] = m.group(1).lower()
    m = re.search(r"Audio:\s*([A-Za-z0-9_]+)", s)
    if m:
        out["audio_codec"] = m.group(1).lower()
    m = re.search(r"(\d+)\s*Hz", s)
    if m:
        out["sample_rate"] = int(m.group(1))
    return out


# ---------------------------------------------------------------------------
# 画面：真人帧 → 漫画化转绘（含去水印裁切、统一画风 LUT）
# ---------------------------------------------------------------------------


# 示例素材只有 6 张真人参考帧；其余镜头由同一风格底图派生不同构图，
# 每一镜的真实来源会写入 output/03_frames/frame_sources.csv 供人工查验。
DERIVE_MAP = {
    "S01": ("S01", "center", 1.00, "none"),
    "S02": ("S02", "upper", 1.06, "none"),
    "S03": ("S03", "center", 1.00, "none"),
    "S04": ("S02", "upper", 1.24, "none"),
    "S05": ("S05", "center", 1.00, "none"),
    "S06": ("S03", "upper", 1.20, "flip"),
    "S07": ("S07", "center", 1.00, "none"),
    "S08": ("S01", "center", 1.00, "flip"),
    "S09": ("S05", "lower", 1.28, "none"),
    "S10": ("S03", "upper", 1.12, "none"),
    "S11": ("S11", "center", 1.00, "none"),
    "S12": ("S07", "lower", 1.10, "dark"),
}


def _fit_vertical(bgr: np.ndarray, cfg: dict, crop_watermark: bool = True,
                  crop_top_ratio: float = 0.0) -> np.ndarray:
    """裁掉来源帧自带水印，按 9:16 居中裁切并缩放到 1080×1920。

    crop_watermark    裁底部（ImageGen 水印在右下）
    crop_top_ratio    裁顶部（VideoGen 水印在左上），两者可独立使用
    """
    h, w = bgr.shape[:2]
    if crop_top_ratio > 0:
        bgr = bgr[int(h * crop_top_ratio):, :]
        h, w = bgr.shape[:2]
    if crop_watermark:
        keep = int(h * (1 - cfg["comicify"]["watermark_crop_bottom_ratio"]))
        bgr = bgr[:keep, :]
        h, w = bgr.shape[:2]
    target_ratio = cfg["width"] / cfg["height"]
    if w / h > target_ratio:          # 太宽 → 左右裁
        nw = int(round(h * target_ratio))
        x0 = (w - nw) // 2
        bgr = bgr[:, x0:x0 + nw]
    else:                              # 太高 → 上下裁
        nh = int(round(w / target_ratio))
        y0 = max(0, (h - nh) // 3)
        bgr = bgr[y0:y0 + nh, :]
    return cv2.resize(bgr, (cfg["width"], cfg["height"]), interpolation=cv2.INTER_AREA)


def comicify(bgr: np.ndarray, cfg: dict) -> np.ndarray:
    """本地真人转绘：双边滤波 → 色阶量化 → 自适应描线 → 网点 → 统一冷调 LUT → 暗角。"""
    p = cfg["comicify"]
    d, sig = p["bilateral_d"], p["bilateral_sigma"]
    smooth = cv2.bilateralFilter(bgr, d, sig, sig)
    smooth = cv2.bilateralFilter(smooth, d, sig, sig)

    # 色阶量化（漫画的平涂感）
    step = 256.0 / int(p["levels"])
    quant = (np.floor(smooth.astype(np.float32) / step) * step + step / 2)
    quant = np.clip(quant, 0, 255)

    # 描线：自适应阈值取暗部边缘，压暗到接近墨色
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY,
        int(p["edge_block"]), 3,
    )
    ink = (edges < 128).astype(np.float32)[:, :, None]
    ink = cv2.GaussianBlur(ink, (3, 3), 0)
    if ink.ndim == 2:                 # OpenCV 会 squeeze 单通道
        ink = ink[:, :, None]
    out = quant * (1.0 - float(p["edge_strength"]) * ink)

    # 半调网点：在暗部叠一层细密网点
    h, w = out.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dots = (((np.sin(xx * 0.14) * np.sin(yy * 0.14)) + 1) * 0.5) ** 6
    lum = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    shadow = 1.0 - lum.astype(np.float32) / 255.0
    out -= (dots * shadow * float(p["halftone_strength"]) * 255)[:, :, None]

    out = np.clip(out, 0, 255).astype(np.uint8)

    # 统一冷调 LUT + 降饱和（全剧共用同一组参数，保证画风不跳变）
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= float(p["saturation"])
    out = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    tint = np.array(p["cool_tint"], dtype=np.float32)  # B,G,R
    out = np.clip(out.astype(np.float32) * tint[::-1][None, None, :], 0, 255)

    # 暗角
    cy, cx = h / 2, w / 2
    Y, X = np.ogrid[:h, :w]
    r = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2) / math.sqrt(2)
    vig = 1.0 - float(p["vignette"]) * np.clip(r, 0, 1) ** 2
    out *= vig[:, :, None]
    return np.clip(out, 0, 255).astype(np.uint8)


def derive(base: np.ndarray, anchor: str, zoom: float, effect: str) -> np.ndarray:
    """由统一风格底图派生不同景别/机位，保持画风与五官一致。"""
    h, w = base.shape[:2]
    zoom = max(1.0, float(zoom))
    cw, ch = int(w / zoom), int(h / zoom)
    x0 = (w - cw) // 2
    ymap = {"upper": 0.10, "center": 0.5, "lower": 0.90}
    y0 = int(max(0, min(h - ch, (h - ch) * ymap.get(anchor, 0.5))))
    img = base[y0:y0 + ch, x0:x0 + cw]
    img = cv2.resize(img, (w, h), interpolation=cv2.INTER_LINEAR)
    if effect == "flip":
        img = cv2.flip(img, 1)
    elif effect == "dark":
        img = np.clip(img.astype(np.float32) * 0.78, 0, 255).astype(np.uint8)
    return img


def build_frames(root: Path, input_dir: Path, storyboard: dict, cfg: dict) -> list[dict]:
    """生成全部镜头的 1080×1920 转绘帧，返回逐镜来源记录。"""
    outdir = root / "output/03_frames"
    outdir.mkdir(parents=True, exist_ok=True)
    frames_dir = input_dir / "frames"

    # 先对所有可用的真人参考帧做一次统一转绘，得到风格底图
    bases: dict[str, np.ndarray] = {}
    for jpg in sorted(frames_dir.glob("*.jpg")) + sorted(frames_dir.glob("*.png")):
        raw = cv2.imread(str(jpg), cv2.IMREAD_COLOR)
        if raw is None:
            continue
        fitted = _fit_vertical(raw, cfg, crop_watermark=True)
        bases[jpg.stem] = comicify(fitted, cfg)

    records = []
    for shot in storyboard["shots"]:
        sid = shot["id"]
        src_key, anchor, zoom, effect = DERIVE_MAP.get(sid, (sid, "center", 1.0, "none"))
        if src_key in bases:
            img = derive(bases[src_key], anchor, zoom, effect)
            kind = "真人参考帧转绘" if src_key == sid else "同风格底图派生"
            source = f"frames/{src_key}.jpg"
        else:
            img = _procedural_frame(shot, cfg)
            kind = "本地程序化渲染（无真人源帧）"
            source = "—"
        dst = outdir / f"{sid}.png"
        cv2.imwrite(str(dst), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        records.append({
            "shot_id": sid, "frame": f"output/03_frames/{sid}.png",
            "source_kind": kind, "source_frame": source,
            "transform": f"去水印裁切 → 9:16 → 统一LUT转绘 → {anchor}/{zoom}/{effect}",
            "resolution": f"{cfg['width']}x{cfg['height']}",
        })

    with (outdir / "frame_sources.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        wr.writeheader()
        wr.writerows(records)
    return records


def match_shot_luma(root: Path, sb: dict, cfg: dict, strength: float = 0.7) -> dict:
    """跨镜接镜匹配：把每帧平均亮度向全片中位数拉近 70%。

    来自 drama-skills edit_tool.py 的 SHOT_MATCH_STRENGTH=0.7 / 增益限 (0.6, 1.6)。
    真人源帧明暗不一（纸面特写亮、人物特写暗）会造成硬切时亮度跳变，
    逐镜质检会把它量出来；这里在转绘层就消掉，而不是靠剪辑时补救。
    """
    frames = [root / f"output/03_frames/{s['id']}.png" for s in sb["shots"]]
    imgs = [(p, cv2.imread(str(p), cv2.IMREAD_COLOR)) for p in frames]
    imgs = [(p, im) for p, im in imgs if im is not None]
    if not imgs:
        return {"applied": False, "reason": "未找到转绘帧"}
    lumas = [float(cv2.cvtColor(im, cv2.COLOR_BGR2GRAY).mean()) for _, im in imgs]
    target = float(np.median(lumas))
    rows = []
    for (p, im), before in zip(imgs, lumas):
        gain = float(np.clip((target / max(before, 1.0)) ** strength, 0.6, 1.6))
        out = np.clip(im.astype(np.float32) * gain, 0, 255).astype(np.uint8)
        cv2.imwrite(str(p), out, [cv2.IMWRITE_PNG_COMPRESSION, 6])
        after = float(cv2.cvtColor(out, cv2.COLOR_BGR2GRAY).mean())
        rows.append({"shot_id": p.stem, "luma_before": round(before, 2),
                     "gain": round(gain, 4), "luma_after": round(after, 2)})
    return {"applied": True, "target_luma": round(target, 2),
            "strength": strength, "gain_limits": [0.6, 1.6], "shots": rows,
            "source": "drama-skills edit_tool.py SHOT_MATCH_STRENGTH=0.7"}


def _procedural_frame(shot: dict, cfg: dict) -> np.ndarray:
    """无真人源帧时的本地兜底：程序化冷调渐变 + 构图色块 + 镜号。"""
    w, h = cfg["width"], cfg["height"]
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    top = np.array([38, 46, 52], np.float32)
    bot = np.array([16, 22, 28], np.float32)
    grad = top[None, None, :] * (1 - y[:, :, None]) + bot[None, None, :] * y[:, :, None]
    img = np.repeat(grad, w, axis=1)
    cv2.rectangle(img, (90, 520), (w - 90, 1320), (58, 66, 72), -1)
    cv2.rectangle(img, (90, 520), (w - 90, 1320), (150, 165, 172), 3)
    cv2.putText(img, shot["id"], (130, 1000), cv2.FONT_HERSHEY_SIMPLEX,
                2.2, (200, 210, 215), 4, cv2.LINE_AA)
    return np.clip(img, 0, 255).astype(np.uint8)


# ---------------------------------------------------------------------------
# 声音：本地 TTS / 音效 / BGM
# ---------------------------------------------------------------------------


def synth_voice(text: str, voice: str, out_wav: Path, root: Path,
                cfg: dict, ffmpeg_bin: str) -> dict:
    """macOS 内置离线中文 TTS → 44100Hz 双声道 wav。"""
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    aiff = out_wav.with_suffix(".aiff")
    r = run(["say", "-v", voice, "-r", str(cfg["tts_rate"]), "-o", str(aiff), text], root)
    if r.returncode != 0 or not aiff.is_file():
        # 音色不可用则退回系统默认中文音色
        r = run(["say", "-v", "Tingting", "-r", str(cfg["tts_rate"]),
                 "-o", str(aiff), text], root)
        voice = "Tingting(fallback)"
    conv = run([ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(aiff), "-ar", str(cfg["sample_rate"]),
                "-ac", str(cfg["channels"]), str(out_wav)], root)
    data, rate = wav_read(out_wav) if out_wav.is_file() else (np.zeros((1, 2), np.float32), 44100)
    return {"voice": voice, "wav": str(out_wav), "duration_s": round(len(data) / rate, 3),
            "engine": "macos_say (offline)", "ok": conv.returncode == 0}


def _tone(freq: float, n: int, rate: int, decay: float = 0.0) -> np.ndarray:
    t = np.arange(n, dtype=np.float32) / rate
    env = np.exp(-decay * t) if decay else np.ones(n, np.float32)
    return (np.sin(2 * np.pi * freq * t) * env).astype(np.float32)


def _sfx_signal(name: str, rate: int) -> np.ndarray:
    rng = np.random.default_rng(abs(hash(name)) % (2 ** 31))
    n = int(rate * 0.5)
    if any(k in name for k in ("心跳", "呼吸")):
        a = np.zeros(int(rate * 1.3), np.float32)
        for st in (0, int(rate * 0.42)):
            seg = _tone(58, int(rate * 0.20), rate, 16) * 0.85
            a[st:st + len(seg)] += seg
        return a
    if "震动" in name:
        return (_tone(46, int(rate * 0.45), rate, 3) * 0.5
                * (np.sign(np.sin(2 * np.pi * 18 * np.arange(int(rate * 0.45)) / rate)) * 0.5 + 0.5))
    if any(k in name for k in ("纸", "翻")):
        return rng.normal(0, 0.22, int(rate * 0.32)).astype(np.float32) * np.exp(
            -8 * np.arange(int(rate * 0.32)) / rate)
    if any(k in name for k in ("门", "拍桌", "叩桌", "椅子", "皮夹", "扫码")):
        return (_tone(120, n, rate, 22) + rng.normal(0, 0.12, n)).astype(np.float32) * 0.6
    if any(k in name for k in ("窗帘", "空调")):
        return rng.normal(0, 0.05, int(rate * 0.9)).astype(np.float32)
    return rng.normal(0, 0.10, int(rate * 0.25)).astype(np.float32) * 0.5


def mix_shot_audio(voice_wav: Path, sfx_names: list[str], duration_s: float,
                   out_wav: Path, cfg: dict) -> dict:
    """把配音与音效按镜头时长混成一条双声道轨，保证音画严格等长。"""
    rate = cfg["sample_rate"]
    total = int(round(duration_s * rate))
    track = np.zeros((total, 2), np.float32)
    voice, vr = wav_read(voice_wav) if voice_wav.is_file() else (np.zeros((1, 2), np.float32), rate)
    start = int(0.25 * rate)
    end = min(total, start + len(voice))
    if end > start:
        track[start:end] += voice[:end - start] * cfg["voice_gain"]
    sfx_log = []
    for i, name in enumerate(sfx_names or []):
        sig = _sfx_signal(name, rate)
        pos = int((0.05 + 0.55 * i) * rate)
        pos = min(pos, max(0, total - len(sig)))
        track[pos:pos + len(sig), 0] += sig * cfg["sfx_gain"]
        track[pos:pos + len(sig), 1] += sig * cfg["sfx_gain"]
        sfx_log.append({"name": name, "at_s": round(pos / rate, 2)})
    peak = float(np.max(np.abs(track))) or 1.0
    if peak > 0.98:
        track *= 0.98 / peak
    wav_write(out_wav, track, rate)
    return {"duration_s": duration_s, "voice_offset_s": 0.25,
            "voice_len_s": round(len(voice) / vr, 3), "sfx": sfx_log,
            "peak": round(min(peak, 0.98), 3)}


def synth_bgm(duration_s: float, out_wav: Path, cfg: dict) -> dict:
    """本地合成低沉悬疑氛围垫音，避免第三方素材版权风险。"""
    rate = cfg["sample_rate"]
    n = int(duration_s * rate)
    t = np.arange(n, dtype=np.float32) / rate
    pad = np.zeros(n, np.float32)
    for f, amp in ((55.0, 0.34), (82.41, 0.20), (110.0, 0.13), (164.81, 0.07)):
        lfo = 0.75 + 0.25 * np.sin(2 * np.pi * (0.045 + f / 8000.0) * t)
        pad += (np.sin(2 * np.pi * f * t) * lfo * amp).astype(np.float32)
    rng = np.random.default_rng(7)
    air = rng.normal(0, 0.012, n).astype(np.float32)
    filt = np.convolve(air, np.ones(64, np.float32) / 64, mode="same")
    mono = (pad + filt) * 0.5
    fade = np.clip(np.minimum(t / 1.5, (duration_s - t) / 2.0), 0, 1)
    mono *= fade
    stereo = np.stack([mono, mono * 0.97 + np.roll(mono, 220) * 0.03], axis=1)
    wav_write(out_wav, stereo, rate)
    return {"duration_s": round(duration_s, 2), "engine": "numpy local synth",
           "license": "算法合成，无第三方素材"}


# ---------------------------------------------------------------------------
# 视频：微动效 + 烧录字幕 + 拼接 + 混音 + 封面
# ---------------------------------------------------------------------------


def comicify_video(src: Path, dst: Path, cfg: dict, ffmpeg_bin: str,
                   root: Path) -> dict:
    """把 WorkBuddy 生成的真视频逐帧纳入本地漫画化转绘层。

    解决两件事：
      1) 图生视频模型往往输出真人实拍质感，与全片漫画风不统一（红果驳回项）；
      2) 模型自带左上角「AI生成」水印，平台要求无第三方水印。
    逐帧做「顶部裁切去水印 → 9:16 居中 → 与其余镜头完全相同的 comicify LUT」，
    因此保留的是**真实动态表演**，统一的是**画风与光色**，且全程本地、零额外费用。
    """
    import subprocess
    cap = cv2.VideoCapture(str(src))
    if not cap.isOpened():
        return {"ok": False, "reason": "无法解码源视频"}
    src_fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    out_fps = max(1, int(round(src_fps)))
    W, H = cfg["width"], cfg["height"]
    top = float(cfg.get("generated_video_watermark_crop_top_ratio", 0.075))

    # 与全片接镜亮度目标对齐（stage_03 的 match_shot_luma 结果）
    gain = 1.0
    lp = root / "output/03_frames/luma_match.json"
    if lp.is_file():
        import json
        target = float(json.loads(lp.read_text(encoding="utf-8")).get("target_luma") or 0)
        samples = []
        for _ in range(6):
            ok, f = cap.read()
            if not ok:
                break
            fit = _fit_vertical(f, cfg, False, top)
            samples.append(float(cv2.cvtColor(comicify(fit, cfg), cv2.COLOR_BGR2GRAY).mean()))
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        if target > 0 and samples:
            m = float(np.mean(samples))
            gain = float(np.clip((target / max(m, 1.0)) ** 0.7, 0.6, 1.6))

    dst.parent.mkdir(parents=True, exist_ok=True)
    rel = str(dst.relative_to(root)) if str(dst).startswith(str(root)) else str(dst)
    cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}",
           "-r", str(out_fps), "-i", "-", "-an",
           "-c:v", cfg["video_codec"], "-preset", "veryfast",
           "-b:v", cfg["video_bitrate"], "-pix_fmt", cfg["pix_fmt"],
           "-movflags", "+faststart", rel]
    proc = subprocess.Popen(cmd, cwd=root, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    n = 0
    try:
        while True:
            ok, f = cap.read()
            if not ok:
                break
            img = comicify(_fit_vertical(f, cfg, False, top), cfg)
            if abs(gain - 1.0) > 1e-3:
                img = np.clip(img.astype(np.float32) * gain, 0, 255).astype(np.uint8)
            proc.stdin.write(np.ascontiguousarray(img).tobytes())
            n += 1
    finally:
        cap.release()
        try:
            proc.stdin.close()
        except Exception:
            pass
    err = (proc.stderr.read() or b"").decode("utf-8", "ignore")
    rc = proc.wait(timeout=600)
    return {"ok": rc == 0 and dst.is_file() and n > 0, "frames": n,
            "fps": out_fps, "duration_s": round(n / out_fps, 2),
            "top_watermark_crop_ratio": top, "luma_gain": round(gain, 4),
            "style": cfg["providers"]["frame"],
            "stderr": err[-400:]}


def _motion_expr(camera: str, dur: float, cfg: dict) -> str:
    """zoompan 运镜表达式：低动态、有起止缓动，幅度受导演台 camera_move_pct 约束。"""
    n = max(1, int(dur * cfg["fps"]))
    if "拉" in camera:
        z = f"max(1.14-0.14*min(on/{n},1),1.0)"
    elif "急推" in camera:
        z = f"1.0+0.18*min(on/{n},1)"
    elif "摇" in camera:
        z = "1.06+0.008*sin(on/48)"
    elif "固定" in camera:
        z = "1.015+0.004*sin(on/62)"
    else:
        z = f"1.0+0.09*min(on/{n},1)"
    x = "iw/2-(iw/zoom/2)"
    y = "ih/2-(ih/zoom/2)"
    if "摇" in camera:
        x = "iw/2-(iw/zoom/2)+26*sin(on/130)"
    if "俯拍" in camera or "仰拍" in camera:
        y = "ih/2-(ih/zoom/2)+18*sin(on/150)"
    return (f"zoompan=z='{z}':x='{x}':y='{y}':d=1:"
            f"s={cfg['width']}x{cfg['height']}:fps={cfg['fps']}")


def _light_overlay(root: Path, cfg: dict) -> Path:
    """生成半透明斜向柔光带，作为可移动的前景层，制造视差与光位变化。"""
    from PIL import Image, ImageDraw, ImageFilter
    p = root / "config/light_overlay.png"
    if p.is_file():
        return p
    w, h = cfg["width"], cfg["height"]
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i in range(6):
        x0 = -420 + i * 230
        d.polygon([(x0, 0), (x0 + 130, 0),
                   (x0 + 130 + int(h * 0.30), h), (x0 + int(h * 0.30), h)],
                  fill=(196, 222, 236, 22 + i * 3))
    im = im.filter(ImageFilter.GaussianBlur(70))
    p.parent.mkdir(parents=True, exist_ok=True)
    im.save(p)
    return p


def _subtitle_text(shot: dict, dshot: dict | None) -> str:
    """字幕按 12 字折行（drama-skills 字幕渲染规范），返回写入 textfile 的文本。"""
    txt = (shot.get("subtitle") or "").strip()
    limit = 12
    if len(txt) > limit:
        cut = min(len(txt), limit)
        # 尽量在标点处断行
        for i in range(min(cut + 3, len(txt)), max(cut - 4, 1), -1):
            if txt[i - 1] in "，。、；：？！":
                cut = i
                break
        txt = txt[:cut].rstrip("，。、；：") + "\n" + txt[cut:].lstrip("，。、；：")
    return txt


def make_clip(shot: dict, frame_png: Path, out_mp4: Path,
              root: Path, cfg: dict, ffmpeg_bin: str, font_rel: str,
              is_first: bool, source_video: Path | None = None,
              dshot: dict | None = None, is_last: bool = False) -> dict:
    """单镜生产（v2 双通道）。

    channel = "generated_video"：WorkBuddy 生成的真动态视频，统一画幅/帧率后
              只叠加字幕与 AI 标识，不再做假动效，保留原表演。
    channel = "local_parallax"  ：本地多层视差兜底 —— 主画面运镜 + 可移动前景光带
              + 明暗呼吸 + 胶片颗粒 + 暗角 + 逐句字幕时段 + 插入镜闪白。

    两种通道都输出纯画面（无音轨），全片人声/BGM 在 05/06 阶段统一混音，
    因此音画时间轴可逐镜测量、可复核。
    """
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    sid, dur = shot["id"], float(shot["duration_s"])
    dshot = dshot or {}
    sub_txt = root / f"output/04_clips/{sid}_sub.txt"
    sub_txt.write_text(_subtitle_text(shot, dshot), encoding="utf-8")
    label_txt = root / "config/ai_label.txt"
    label_txt.write_text(cfg["ai_label"], encoding="utf-8")

    win = dshot.get("subtitle_window_s") or [0.30, max(0.5, dur - 0.35)]
    a, b = float(win[0]), min(float(win[1]), dur)
    draw_sub = (
        "drawtext=fontfile={font}:textfile={txt}:fontcolor=white:fontsize={size}:"
        "line_spacing=12:borderw=5:bordercolor=black@0.95:shadowx=0:shadowy=2:"
        "x=(w-text_w)/2:y=h-{margin}:enable='between(t,{a},{b})'"
    ).format(font=font_rel, txt=sub_txt.relative_to(root),
             size=cfg.get("subtitle_size", 60), margin=cfg.get("subtitle_margin", 300),
             a=f"{a:.2f}", b=f"{b:.2f}")
    draw_label = (
        "drawtext=fontfile={font}:textfile={txt}:fontcolor=white@0.88:fontsize=36:"
        "borderw=3:bordercolor=black@0.8:x=w-text_w-46:y=92:"
        "enable='lt(t,{sec})'"
    ).format(font=font_rel, txt=label_txt.relative_to(root),
             sec=cfg["ai_label_seconds"])

    use_video = bool(source_video and Path(source_video).is_file()
                     and Path(source_video).stat().st_size > 10000)
    video_in = Path(source_video) if use_video else None
    comic_info = {}
    if use_video and cfg.get("comicify_generated_video", True):
        cv_path = out_mp4.parent / f"_comic_{sid}.mp4"
        comic_info = comicify_video(video_in, cv_path, cfg, ffmpeg_bin, root)
        if comic_info.get("ok"):
            video_in = cv_path
        else:
            comic_info["fallback"] = "转绘失败，沿用未转绘原片（画风一致性需人工复核）"
    light = _light_overlay(root, cfg)
    W, H, F = cfg["width"], cfg["height"], cfg["fps"]

    if use_video:
        # 真视频：保留真实表演，只做画幅规整 + 轻微调色 + 字幕/标识
        chain = [
            f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
            f"crop={W}:{H},setsar=1,fps={F},"
            f"tpad=stop_mode=clone:stop_duration=12,"
            f"trim=duration={dur:.3f},setpts=PTS-STARTPTS,"
            "eq=contrast=1.02:saturation=0.97,vignette=PI/6[bg]",
            f"[bg]{draw_sub}[t1]",
        ]
        cur = "t1"
        if is_first:
            chain.append(f"[{cur}]{draw_label}[t2]")
            cur = "t2"
        if is_last:
            chain.append(f"[{cur}]fade=t=out:st={max(0, dur-0.45):.2f}:d=0.45[v]")
        else:
            chain.append(f"[{cur}]null[v]")
        fc = ";".join(chain)
        map_label = "[v]"
        cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
               "-i", str(video_in.relative_to(root)
                         if str(video_in).startswith(str(root)) else video_in),
               "-filter_complex", fc, "-map", map_label,
               "-t", f"{dur:.3f}", "-an",
               "-c:v", cfg["video_codec"], "-preset", "veryfast",
               "-b:v", cfg["video_bitrate"], "-minrate", "8M", "-maxrate", "12M",
               "-bufsize", "20M", "-pix_fmt", cfg["pix_fmt"], "-r", str(F),
               "-movflags", "+faststart", str(out_mp4.relative_to(root))]
        channel = "generated_video"
        motion = dshot.get("motion_intensity", "ai_generated")
    else:
        # 本地兜底：多层视差 + 前景光带 + 呼吸光 + 颗粒 + 暗角
        chain0 = ",".join([
            "[0:v]" + _motion_expr(shot.get("camera", ""), dur, cfg),
            "eq=brightness='0.010*sin(2*PI*t/3.6)':contrast=1.04:saturation=0.96",
            "noise=alls=3:allf=t+u", "vignette=PI/5", "format=yuv420p"]) + "[bg]"
        pre = [chain0,
               f"[1:v]scale={W}:{H},fps={F},format=rgba[lt]",
               "[bg][lt]overlay=x='38*sin(t/2.4)':y=0:format=auto[comp]"]
        post = []
        if sid in ("S03", "S05", "S09"):
            post.append("fade=t=in:st=0:d=0.12:color=white")
        post.append(draw_sub)
        if is_first:
            post.append(draw_label)
        if is_last:
            post.append(f"fade=t=out:st={max(0, dur-0.45):.2f}:d=0.45")
        fc = ";".join(pre + ["[comp]" + ",".join(post) + "[v]"])
        cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
               "-loop", "1", "-framerate", str(F), "-i", str(frame_png.relative_to(root)),
               "-loop", "1", "-framerate", str(F), "-i", str(light.relative_to(root)),
               "-filter_complex", fc, "-map", "[v]",
               "-t", f"{dur:.3f}", "-an",
               "-c:v", cfg["video_codec"], "-preset", "veryfast",
               "-b:v", cfg["video_bitrate"], "-minrate", "8M", "-maxrate", "12M",
               "-bufsize", "20M", "-pix_fmt", cfg["pix_fmt"], "-r", str(F),
               "-movflags", "+faststart", str(out_mp4.relative_to(root))]
        channel = "local_parallax"
        motion = shot.get("camera", "")

    r = run(cmd, root, timeout=900)
    return {"ok": r.returncode == 0 and out_mp4.is_file(),
            "cmd": " ".join(cmd[:1] + cmd[cmd.index("-filter_complex"):])[:600],
            "stderr": (r.stderr or "")[-500:], "motion": motion,
            "channel": channel,
            "source_video": str(source_video) if use_video else "",
            "comicify": comic_info}


def build_voice_track(shots: list[dict], per_shot_wavs: list[Path],
                      out_wav: Path, cfg: dict) -> dict:
    """按每镜 duration_s 把音轨首尾相接，形成与画面时间轴严格对齐的全片人声轨。"""
    rate = cfg["sample_rate"]
    pieces, sync = [], []
    cursor = 0
    for shot, p in zip(shots, per_shot_wavs):
        n = int(round(float(shot["duration_s"]) * rate))
        data, _ = wav_read(p)
        buf = np.zeros((n, 2), np.float32)
        take = min(n, len(data))
        buf[:take] = data[:take]
        pieces.append(buf)
        sync.append({"shot_id": shot["id"], "start_s": round(cursor / rate, 3),
                     "end_s": round((cursor + n) / rate, 3),
                     "expected_s": float(shot["duration_s"]),
                     "audio_samples": n})
        cursor += n
    track = np.concatenate(pieces, axis=0) if pieces else np.zeros((rate, 2), np.float32)
    wav_write(out_wav, track, rate)
    return {"duration_s": round(len(track) / rate, 3), "timeline": sync,
            "max_drift_s": max((abs(x["end_s"] - x["start_s"] - x["expected_s"])
                                for x in sync), default=0.0)}


def concat_and_mux(clips: list[Path], voice_wav: Path, bgm_wav: Path, out_mp4: Path,
                   root: Path, cfg: dict, ffmpeg_bin: str, total_duration: float) -> dict:
    """拼接全部镜头 → 混入全片人声/BGM → 写入 AIGC 元数据 → 输出最终 MP4。"""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    lst = root / "output/04_clips/concat_list.txt"
    # concat demuxer 以「列表文件所在目录」为基准解析相对路径，不能用项目根相对路径
    lst.write_text("".join(f"file '{os.path.relpath(p, lst.parent)}'\n" for p in clips),
                   encoding="utf-8")
    tmp = root / "output/06_final/_concat.mp4"
    r1 = run([ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
              "-f", "concat", "-safe", "0", "-i", str(lst.relative_to(root)),
              "-c", "copy", str(tmp.relative_to(root))], root)
    if r1.returncode != 0 or not tmp.is_file():
        return {"ok": False, "stage": "concat", "stderr": (r1.stderr or "")[-800:]}

    # 末尾做 EBU R128 响度归一化，避免离线 TTS/合成 BGM 整体偏轻
    filt = ("[1:a]volume=1.0[v];[2:a]volume={g}[b];"
            "[v][b]amix=inputs=2:duration=first:dropout_transition=0[m];"
            "[m]loudnorm=I={i}:TP=-1.5:LRA=11[a]").format(
                g=cfg["bgm_gain"], i=cfg.get("target_lufs", -16))
    cmd = [ffmpeg_bin, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(tmp.relative_to(root)),
           "-i", str(voice_wav.relative_to(root)),
           "-i", str(bgm_wav.relative_to(root)),
           "-filter_complex", filt, "-map", "0:v", "-map", "[a]",
           "-t", f"{total_duration:.3f}",
           "-c:v", "copy", "-c:a", cfg["audio_codec"], "-b:a", cfg["audio_bitrate"],
           "-ar", str(cfg["sample_rate"]), "-ac", str(cfg["channels"]),
           "-metadata", f"comment={cfg['ai_label']}",
           "-metadata", "genre=AI-assisted comic drama",
           "-movflags", "+faststart", str(out_mp4.relative_to(root))]
    r2 = run(cmd, root, timeout=600)
    if tmp.is_file() and out_mp4.is_file():
        tmp.unlink()
    return {"ok": r2.returncode == 0, "stage": "mux",
            "stderr": (r2.stderr or "")[-800:],
            "probe": probe(out_mp4, ffmpeg_bin) if out_mp4.is_file() else {}}


def make_cover(frame_png: Path, title: str, out_png: Path,
               root: Path, cfg: dict) -> dict:
    """生成 3:4 竖版封面，带描边剧名（平台封面要求）。"""
    from PIL import Image, ImageDraw, ImageFont
    w, h = cfg["cover"]["width"], cfg["cover"]["height"]
    src = Image.open(frame_png).convert("RGB")
    ratio = w / h
    sw, sh = src.size
    if sw / sh > ratio:
        nw = int(sh * ratio)
        src = src.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw / ratio)
        src = src.crop((0, (sh - nh) // 3, sw, (sh - nh) // 3 + nh))
    img = src.resize((w, h), Image.LANCZOS)
    # 底部压暗，保证描边剧名可读
    arr = np.array(img).astype(np.float32)
    grad = np.clip((np.linspace(0, 1, h)[:, None, None] ** 2) * 0.55, 0, 1)
    arr[int(h * 0.55):] *= (1 - grad[int(h * 0.55):])
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    font_path = root / cfg["font_local"]
    try:
        font = ImageFont.truetype(str(font_path), 150)
    except Exception:
        font = ImageFont.load_default()
    box = d.textbbox((0, 0), title, font=font)
    x = (w - (box[2] - box[0])) // 2
    y = int(h * 0.74)
    d.text((x, y), title, font=font, fill="white",
           stroke_width=8, stroke_fill="black")
    out_png.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_png)
    return {"path": str(out_png.relative_to(root)), "size": f"{w}x{h}",
            "title_stroked": True}

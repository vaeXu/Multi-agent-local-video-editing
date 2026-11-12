"""红果/抖音 AI 漫剧验收规则执行器（规范官产出）。

对应 SPEC.md §3.2（config/hongguo_rules.json）与 §3.3（本模块接口）。

设计约束：
- 只用标准库（json / re / subprocess / pathlib / os），不引入第三方依赖；
- 本机没有 ffprobe，统一用 `ffmpeg -i <file>` 的 stderr 正则解析流信息；
- 绝不写死 pass：可自动判定的项由实测值计算，画面级/法律效力级项一律 warn
  并写明「需人工核验」，同时保留 how_to_verify；
- 单条规则异常不中断整体，任何异常都不向流水线抛出。

公开接口：
    check_video(video_path, ffmpeg_bin) -> dict
    run(project_root, status) -> dict
"""

import json
import os
import re
import subprocess
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

# SPEC 3.2 约定：check 只能是这里实现过的 key，或字符串 "manual"。
CHECKER_KEYS = (
    "video_resolution", "video_codec", "video_fps", "video_bitrate",
    "audio_codec", "audio_sample_rate", "audio_channels", "duration",
    "container", "no_alpha", "no_odd_dimension", "subtitle_burned",
    "ai_label", "shot_duration", "shot_count", "dialogue_length",
    "character_anchors", "style_consistency", "archive_completeness",
    "manual", "cover_spec",
)

_STAGE_BY_CATEGORY = {
    "技术规格": "06_final",
    "音画质量": "06_final",
    "内容合规": "01_script",
    "版权留痕": "07_reports",
}

_AI_LABEL_WORDS = (
    "AI辅助制作", "AI 辅助制作", "人工智能辅助生成", "人工智能辅助",
    "本片由人工智能", "AI生成", "AI 生成", "AIGC", "人工智能生成",
)

_ALPHA_RE = re.compile(
    r"\b(?:yuva\w*|rgba\w*|argb|bgra\w*|abgr|gbrap\w*|ya\d+|la\d+|gray8a)\b",
    re.IGNORECASE,
)

# 归档完整性默认必备清单（相对项目根目录）
_DEFAULT_ARCHIVE = (
    "output/01_script/script.md",
    "output/01_script/storyboard.json",
    "output/02_characters/characters.json",
    "config/project.json",
    "output/07_reports/compliance_report.md",
)


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

def _res(status, actual, evidence="", note=""):
    """检查器的统一返回结构。"""
    return {"status": status, "actual": actual, "evidence": evidence, "note": note}


def _read_json(path):
    try:
        with Path(path).open("r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None


def _read_text(path, limit=200000):
    try:
        return Path(path).read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def _rel(root, path):
    try:
        return str(Path(path).relative_to(Path(root)))
    except Exception:
        return str(path)


def _first_existing(root, rels):
    for rel in rels:
        p = Path(root) / rel
        if p.is_file():
            return p, rel
    return None, ""


def _locate_material(root, filename, extra_rels=()):
    """在 input/<任意项目名>/ 下，以及指定的 output 归档目录中定位素材。"""
    cands = []
    try:
        cands.extend(sorted((Path(root) / "input").glob("*/" + filename)))
    except Exception:
        pass
    for rel in extra_rels:
        cands.append(Path(root) / rel)
    for p in cands:
        try:
            if p.is_file():
                return p, _rel(root, p)
        except Exception:
            continue
    return None, ""


def _locate_video(root, status, disk):
    rel = ""
    for src in (status, disk):
        if isinstance(src, dict):
            v = src.get("final_video")
            if isinstance(v, str) and v:
                rel = v
                break
    if rel:
        p = Path(root) / rel
        if p.is_file():
            return p, rel
    for base in ("output/06_final", "output"):
        try:
            cands = sorted((Path(root) / base).rglob("*.mp4"))
        except Exception:
            cands = []
        if cands:
            return cands[0], _rel(root, cands[0])
    return None, ""


def _resolve_ffmpeg_bin(status, disk):
    """ffmpeg 二进制路径：status 显式指定 > 环境变量 > 系统 ffmpeg > imageio_ffmpeg。

    注意：本模块不 import imageio_ffmpeg（避免第三方依赖），改为按任务提示用
    subprocess 执行 `python3 -c "import imageio_ffmpeg; ..."` 取回路径。
    """
    for src in (status, disk):
        if not isinstance(src, dict):
            continue
        for key in ("ffmpeg_bin", "ffmpeg"):
            v = src.get(key)
            if isinstance(v, str) and v and Path(v).exists():
                return v
        cfg = src.get("config")
        if isinstance(cfg, dict):
            v = cfg.get("ffmpeg_bin")
            if isinstance(v, str) and v and Path(v).exists():
                return v
    for key in ("FFMPEG_BIN", "IMAGEIO_FFMPEG_EXE", "SHIXIANG_FFMPEG"):
        v = os.environ.get(key)
        if v and Path(v).exists():
            return v
    try:
        p = subprocess.run(["ffmpeg", "-version"], capture_output=True,
                           text=True, timeout=10)
        if p.returncode == 0:
            return "ffmpeg"
    except Exception:
        pass
    try:
        p = subprocess.run(
            ["python3", "-c",
             "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"],
            capture_output=True, text=True, timeout=20,
        )
        lines = [x.strip() for x in (p.stdout or "").splitlines() if x.strip()]
        if p.returncode == 0 and lines and Path(lines[-1]).exists():
            return lines[-1]
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# ffmpeg -i stderr 解析（无 ffprobe）
# ---------------------------------------------------------------------------

def _empty_probe():
    return {
        "width": None, "height": None, "codec": None, "fps": None,
        "bitrate_kbps": None, "audio_codec": None, "sample_rate": None,
        "channels": None, "duration_s": None, "container": None,
    }


def _probe(ffmpeg_bin, video_path):
    """执行 `ffmpeg -i <file>`，返回合并后的 stderr（ffprobe 不可用）。"""
    if not ffmpeg_bin or not video_path:
        return ""
    try:
        proc = subprocess.run(
            [str(ffmpeg_bin), "-hide_banner", "-i", str(video_path)],
            capture_output=True, text=True, timeout=90,
        )
        return (proc.stderr or "") + "\n" + (proc.stdout or "")
    except Exception:
        return ""


def _channels_of(audio_line):
    words = {
        "stereo": 2, "mono": 1, "5.1": 6, "7.1": 8, "quad": 4,
        "hexagonal": 6, "octagonal": 8, "downmix": 2,
    }
    m = re.search(r"\b(5\.1|7\.1|stereo|mono|quad|hexagonal|octagonal|downmix)\b",
                  audio_line, re.IGNORECASE)
    if m:
        return words.get(m.group(1).lower())
    m = re.search(r"(\d+)\s*channels?", audio_line, re.IGNORECASE)
    if m:
        return int(m.group(1))
    return None


def _parse_probe(stderr):
    """从 ffmpeg -i 的 stderr 正则解析 10 项流信息。"""
    out = _empty_probe()
    if not stderr:
        return out

    # Duration: 00:00:03.00, start: 0.000000, bitrate: 1296 kb/s
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", stderr)
    if m:
        out["duration_s"] = (int(m.group(1)) * 3600
                             + int(m.group(2)) * 60
                             + float(m.group(3)))
    m = re.search(r"bitrate:\s*(\d+(?:\.\d+)?)\s*kb/s", stderr)
    if m:
        out["bitrate_kbps"] = float(m.group(1))

    # Input #0, mov,mp4,m4a,3gp,3g2,mj2, from 'xxx.mp4':
    m = re.search(r"Input\s+#0,\s*(.+?),\s*from\s", stderr)
    if m:
        fmts = [x.strip() for x in m.group(1).split(",") if x.strip()]
        out["container"] = "mp4" if "mp4" in fmts else (fmts[0] if fmts else None)

    # Stream #0:0...: Video: h264 (High) ..., yuv420p(progressive), 1080x1920 ..., 30 fps, ...
    vm = re.search(r"Video:\s*([^\n]+)", stderr)
    if vm:
        line = vm.group(1)
        m = re.search(r"(\d{2,5})x(\d{2,5})", line)
        if m:
            out["width"], out["height"] = int(m.group(1)), int(m.group(2))
        m = re.match(r"\s*([A-Za-z0-9_]+)", line)
        if m:
            out["codec"] = m.group(1).lower()
        m = re.search(r"(\d+(?:\.\d+)?)\s*fps", line)
        if m:
            out["fps"] = float(m.group(1))

    # Stream #0:1...: Audio: aac (LC) ..., 44100 Hz, stereo, fltp, 128 kb/s
    am = re.search(r"Audio:\s*([^\n]+)", stderr)
    if am:
        line = am.group(1)
        m = re.match(r"\s*([A-Za-z0-9_]+)", line)
        if m:
            out["audio_codec"] = m.group(1).lower()
        m = re.search(r"(\d+)\s*Hz", line)
        if m:
            out["sample_rate"] = int(m.group(1))
        out["channels"] = _channels_of(line)

    return out


def check_video(video_path, ffmpeg_bin):
    """返回 {width,height,codec,fps,bitrate_kbps,audio_codec,sample_rate,
    channels,duration_s,container}。不抛异常；解析不到的项为 None。"""
    try:
        return _parse_probe(_probe(ffmpeg_bin, video_path))
    except Exception:
        return _empty_probe()


def _video_line(probe):
    m = re.search(r"Video:\s*([^\n]+)", probe or "")
    return m.group(1) if m else ""


def _alpha_present(probe):
    """返回 True/False；无法判定（无 Video 行）时返回 None。"""
    line = _video_line(probe)
    if not line:
        return None
    return bool(_ALPHA_RE.search(line))


def _has_soft_subtitle_stream(probe):
    return bool(re.search(r"Subtitle:", probe or ""))


# ---------------------------------------------------------------------------
# 上下文
# ---------------------------------------------------------------------------

def _build_ctx(root, status, disk):
    ctx = {
        "root": Path(root),
        "status": status,
        "disk": disk,
        "video_rel": "", "video_path": None, "probe": "", "video": None,
        "ffmpeg_bin": "", "storyboard": None, "storyboard_rel": "",
        "characters": None, "characters_rel": "", "script_rel": "",
    }

    ctx["ffmpeg_bin"] = _resolve_ffmpeg_bin(status, disk)
    ctx["video_path"], ctx["video_rel"] = _locate_video(root, status, disk)

    if ctx["video_path"] and ctx["ffmpeg_bin"]:
        ctx["probe"] = _probe(ctx["ffmpeg_bin"], ctx["video_path"])
        ctx["video"] = _parse_probe(ctx["probe"]) if ctx["probe"] else None
    elif ctx["video_path"]:
        # 没有 ffmpeg 二进制，仍保留路径，交由检查器标 warn
        ctx["video"] = None

    sb_path, sb_rel = _locate_material(
        root, "storyboard.json", ("output/01_script/storyboard.json",)
    )
    if sb_path:
        data = _read_json(sb_path)
        if isinstance(data, dict):
            ctx["storyboard"] = data
            ctx["storyboard_rel"] = sb_rel

    ch_path, ch_rel = _locate_material(
        root, "characters.json", ("output/02_characters/characters.json",)
    )
    if ch_path:
        data = _read_json(ch_path)
        if isinstance(data, dict):
            ctx["characters"] = data
            ctx["characters_rel"] = ch_rel

    sc_path, sc_rel = _locate_material(
        root, "script.md", ("output/01_script/script.md",)
    )
    if sc_path:
        ctx["script_rel"] = sc_rel

    return ctx


def _default_evidence(rule, ctx):
    if rule.get("check") == "manual":
        return "—"
    return ctx["video_rel"] or ctx["storyboard_rel"] or "—"


# ---------------------------------------------------------------------------
# 检查器：技术流信息（成片不存在或无法解析时一律 warn）
# ---------------------------------------------------------------------------

def _need_video(ctx, label):
    if not ctx["video_path"]:
        return _res("warn", "需人工核验：未找到成片（%s），无法自动实测" % label,
                    evidence="—", note="missing_video")
    if not ctx["ffmpeg_bin"]:
        return _res("warn", "需人工核验：未定位到 ffmpeg 二进制，无法解析 %s" % label,
                    evidence=ctx["video_rel"], note="missing_ffmpeg")
    if not ctx["video"]:
        return _res("warn", "需人工核验：ffmpeg -i 未返回可解析的流信息（%s）" % label,
                    evidence=ctx["video_rel"], note="empty_probe")
    return None


def _video_check(rule, ctx, field, label, predicate, fmt=None):
    blocked = _need_video(ctx, label)
    if blocked:
        return blocked
    value = ctx["video"].get(field)
    if value is None:
        return _res("warn", "需人工核验：ffmpeg -i 未解析出 %s" % label,
                    evidence=ctx["video_rel"], note="field_missing")
    text = fmt(value) if fmt else str(value)
    try:
        ok = predicate(value)
    except Exception:
        ok = False
    actual = "%s=%s" % (label, text)
    return _res("pass" if ok else "fail", actual, evidence=ctx["video_rel"],
                note="")


def _ck_video_resolution(rule, ctx):
    blocked = _need_video(ctx, "分辨率")
    if blocked:
        return blocked
    v = ctx["video"]
    if v.get("width") is None or v.get("height") is None:
        return _res("warn", "需人工核验：ffmpeg -i 未解析出宽高",
                    evidence=ctx["video_rel"])
    w, h = v["width"], v["height"]
    ok = (w == 1080 and h == 1920)
    return _res("pass" if ok else "fail", "%dx%d（期望 1080x1920）" % (w, h),
                evidence=ctx["video_rel"])


def _ck_video_codec(rule, ctx):
    return _video_check(rule, ctx, "codec", "视频编码",
                        lambda x: str(x).lower() in ("h264", "avc", "avc1", "x264"))


def _ck_video_fps(rule, ctx):
    return _video_check(
        rule, ctx, "fps", "帧率",
        lambda x: any(abs(float(x) - t) <= 0.6 for t in (25.0, 30.0)),
        fmt=lambda x: "%g fps" % x,
    )


def _ck_video_bitrate(rule, ctx):
    blocked = _need_video(ctx, "码率")
    if blocked:
        return blocked
    b = ctx["video"].get("bitrate_kbps")
    if b is None:
        return _res("warn", "需人工核验：ffmpeg -i 未解析出 bitrate",
                    evidence=ctx["video_rel"])
    ok = b >= 4000
    extra = ""
    if ok and b < 8000:
        extra = "；低于行业建议 8000~12000 kb/s，建议提高但不判失败"
    return _res("pass" if ok else "fail",
                "码率=%g kb/s（下限 4000）%s" % (b, extra),
                evidence=ctx["video_rel"])


def _ck_audio_codec(rule, ctx):
    return _video_check(rule, ctx, "audio_codec", "音频编码",
                        lambda x: str(x).lower() in ("aac", "aac_latm", "mp4a"))


def _ck_audio_sample_rate(rule, ctx):
    return _video_check(rule, ctx, "sample_rate", "采样率",
                        lambda x: int(x) == 44100,
                        fmt=lambda x: "%d Hz" % int(x))


def _ck_audio_channels(rule, ctx):
    return _video_check(rule, ctx, "channels", "声道数",
                        lambda x: int(x) == 2,
                        fmt=lambda x: "%d（stereo）" % int(x))


def _ck_duration(rule, ctx):
    blocked = _need_video(ctx, "单集时长")
    if blocked:
        return blocked
    d = ctx["video"].get("duration_s")
    if d is None:
        return _res("warn", "需人工核验：ffmpeg -i 未解析出 Duration",
                    evidence=ctx["video_rel"])
    if 60 <= d <= 120:
        status, note = "pass", "落在 60~120s 为佳区间"
    elif 120 < d <= 300:
        status, note = "warn", "需人工核验：超出 60~120s 为佳区间，但在 1~5 分钟上传口径内"
    else:
        status, note = "fail", "超出 1~5 分钟上传口径"
    return _res(status, "时长=%.2f s（期望 60~120s，上传口径 60~300s）；%s" % (d, note),
                evidence=ctx["video_rel"])


def _ck_container(rule, ctx):
    return _video_check(rule, ctx, "container", "容器",
                        lambda x: str(x).lower() in ("mp4", "mov", "mov,mp4"))


def _ck_no_alpha(rule, ctx):
    blocked = _need_video(ctx, "alpha 通道")
    if blocked:
        return blocked
    a = _alpha_present(ctx["probe"])
    if a is None:
        return _res("warn", "需人工核验：ffmpeg -i 未给出 Video 行，无法判断像素格式",
                    evidence=ctx["video_rel"])
    line = _video_line(ctx["probe"])
    m = re.search(r",\s*([A-Za-z0-9_]+)\s*\(", line)
    pix = m.group(1) if m else "未识别"
    return _res("fail" if a else "pass",
                "像素格式=%s；%s" % (pix, "检出 alpha 通道" if a else "无 alpha 通道"),
                evidence=ctx["video_rel"])


def _ck_no_odd_dimension(rule, ctx):
    blocked = _need_video(ctx, "宽高奇偶")
    if blocked:
        return blocked
    v = ctx["video"]
    if v.get("width") is None or v.get("height") is None:
        return _res("warn", "需人工核验：ffmpeg -i 未解析出宽高",
                    evidence=ctx["video_rel"])
    w, h = v["width"], v["height"]
    ok = (w % 2 == 0 and h % 2 == 0)
    return _res("pass" if ok else "fail",
                "%dx%d（%s）" % (w, h, "均为偶数" if ok else "存在奇数尺寸"),
                evidence=ctx["video_rel"])


# ---------------------------------------------------------------------------
# 检查器：结构化素材（真实读取 storyboard.json / characters.json）
# ---------------------------------------------------------------------------

def _shots(ctx):
    sb = ctx["storyboard"]
    if not isinstance(sb, dict):
        return None
    shots = sb.get("shots")
    return shots if isinstance(shots, list) else None


def _ck_shot_count(rule, ctx):
    shots = _shots(ctx)
    if shots is None:
        return _res("warn", "需人工核验：未找到可解析的 storyboard.json / shots",
                    evidence=ctx["storyboard_rel"] or "—")
    ids = [str(s.get("id", "")) for s in shots if isinstance(s, dict)]
    unique = len(set(ids)) == len(ids)
    shaped = all(re.fullmatch(r"S\d{2}", i) for i in ids)
    ok = len(shots) >= 8 and unique and shaped
    return _res("pass" if ok else "fail",
                "镜头数=%d（>=8）；id 唯一=%s；id 符合 S\\d{2}=%s" % (len(shots), unique, shaped),
                evidence=ctx["storyboard_rel"])


def _ck_shot_duration(rule, ctx):
    shots = _shots(ctx)
    if shots is None:
        return _res("warn", "需人工核验：未找到可解析的 storyboard.json / shots",
                    evidence=ctx["storyboard_rel"] or "—")
    bad = []
    for i, s in enumerate(shots):
        if not isinstance(s, dict):
            bad.append("#%d(非对象)" % (i + 1))
            continue
        try:
            d = float(s.get("duration_s"))
        except (TypeError, ValueError):
            bad.append("%s(缺/非法 duration_s)" % s.get("id", "#%d" % (i + 1)))
            continue
        if not (3 <= d <= 8):
            bad.append("%s=%g" % (s.get("id", "#%d" % (i + 1)), d))
    ok = not bad
    return _res("pass" if ok else "fail",
                "共 %d 镜；%s" % (len(shots),
                                 "全部在 3~8s" if ok else "越界: " + ", ".join(bad[:8])),
                evidence=ctx["storyboard_rel"])


def _ck_dialogue_length(rule, ctx):
    shots = _shots(ctx)
    if shots is None:
        return _res("warn", "需人工核验：未找到可解析的 storyboard.json / shots",
                    evidence=ctx["storyboard_rel"] or "—")
    bad, counted = [], 0
    for s in shots:
        if not isinstance(s, dict):
            continue
        d = s.get("dialogue")
        text = d.get("text", "") if isinstance(d, dict) else ""
        if not isinstance(text, str) or not text.strip():
            continue
        counted += 1
        if len(text) > 24:
            bad.append("%s=%d字" % (s.get("id", "?"), len(text)))
    ok = not bad
    return _res("pass" if ok else "fail",
                "检查 %d 条非空台词（<=24 字）；%s" % (
                    counted, "全部合规" if ok else "超长: " + ", ".join(bad[:8])),
                evidence=ctx["storyboard_rel"])


def _ck_character_anchors(rule, ctx):
    ch = ctx["characters"]
    if not isinstance(ch, dict) or not isinstance(ch.get("characters"), list):
        return _res("warn", "需人工核验：未找到可解析的 characters.json",
                    evidence=ctx["characters_rel"] or "—")
    items = ch["characters"]
    if not items:
        return _res("warn", "需人工核验：characters.json 的 characters 为空",
                    evidence=ctx["characters_rel"])
    bad, total = [], 0
    for c in items:
        if not isinstance(c, dict):
            bad.append("非对象角色")
            continue
        anchors = c.get("identity_anchors")
        n = len(anchors) if isinstance(anchors, list) else 0
        total += n
        if n < 3:
            bad.append("%s=%d条" % (c.get("name", "?"), n))
    ok = not bad
    return _res("pass" if ok else "fail",
                "%d 个角色 / 共 %d 条锚点；%s" % (
                    len(items), total,
                    "每角色均 >=3 条" if ok else "不足: " + ", ".join(bad[:8])),
                evidence=ctx["characters_rel"])


def _ck_style_consistency(rule, ctx):
    """画风统一是画面级判定，本地只能校验配置与帧齐备性，最终一律 warn。"""
    sb = ctx["storyboard"]
    parts = []
    if not isinstance(sb, dict):
        return _res("warn", "需人工核验：未找到 storyboard.json，无法核对统一画风配置；"
                    "全剧画风/线条/色温一致性需人工连续播放确认",
                    evidence="—")
    style = sb.get("style") if isinstance(sb.get("style"), dict) else {}
    name = style.get("name", "")
    prefix = style.get("prompt_prefix", "")
    neg = style.get("negative_prompt", "")
    parts.append("style.name=%s" % (name or "缺失"))
    parts.append("prompt_prefix=%s" % ("已配置" if prefix else "缺失"))
    parts.append("negative_prompt=%s" % ("已配置" if neg else "缺失"))
    try:
        frames = len(list((ctx["root"] / "output/03_frames").glob("*.png")))
        nshots = len(_shots(ctx) or [])
        parts.append("帧 %d / 镜 %d" % (frames, nshots))
    except Exception:
        parts.append("帧数读取失败")
    return _res("warn",
                "需人工核验：全剧画风/线条/色温一致性与五官稳定性；数据层："
                + "，".join(parts),
                evidence=ctx["storyboard_rel"])


def _ck_archive_completeness(rule, ctx):
    """校验归档文件存在性；内容真实性/版本一致性需人工，缺失记 warn。"""
    rels = list(_DEFAULT_ARCHIVE)
    for m in re.finditer(r"[A-Za-z0-9_][A-Za-z0-9_./-]*\.[A-Za-z0-9]+",
                         rule.get("expected", "")):
        cand = m.group(0)
        if cand not in rels and ("/" in cand):
            rels.append(cand)
    missing = [r for r in rels if not (ctx["root"] / r).is_file()]
    present = [r for r in rels if (ctx["root"] / r).is_file()]
    if missing:
        return _res("warn",
                    "需人工核验：归档缺 %d/%d 项（%s），可能是流水线尚未产出，"
                    "需补齐后复核内容完整性" % (
                        len(missing), len(rels), ", ".join(missing[:6])),
                    evidence="output/")
    return _res("pass",
                "%d/%d 项归档文件齐备（%s）；内容完整性按 how_to_verify 人工核验" % (
                    len(present), len(rels), ", ".join(present[:6])),
                evidence="output/")


# ---------------------------------------------------------------------------
# 检查器：画面级 / 法律效力级（一律 warn，绝不写死 pass）
# ---------------------------------------------------------------------------

def _scan_ai_label_hits(ctx):
    root = ctx["root"]
    cands = []
    for rel in (ctx["storyboard_rel"], ctx["script_rel"]):
        if rel:
            cands.append(root / rel)
    try:
        cands.extend(sorted((root / "output/07_reports").rglob("*.md"))[:20])
    except Exception:
        pass
    try:
        final = root / "output/06_final"
        cands.extend(sorted(final.glob("*.srt"))[:10])
        cands.extend(sorted(final.glob("*.txt"))[:10])
    except Exception:
        pass
    hits = []
    for p in cands:
        try:
            if not p.is_file():
                continue
            txt = _read_text(p)
        except Exception:
            continue
        for w in _AI_LABEL_WORDS:
            if w in txt:
                hits.append("%s(%s)" % (_rel(root, p), w))
                break
    return hits


def _ck_ai_label(rule, ctx):
    hits = _scan_ai_label_hits(ctx)
    hint = ("本地文本线索命中 %d 处：%s" % (len(hits), "；".join(hits[:4]))) if hits \
        else "本地文本未发现 AI 标识线索"
    return _res("warn",
                "需人工核验：每集片头/明显位置的可见 AI 提示标识、封面与简介同步标注、"
                "文件元数据隐式 AIGC 标识是否齐全且未被隐藏；%s。"
                "ffmpeg -i 无法读取画面文字与自定义元数据" % hint,
                evidence=ctx["video_rel"] or ctx["storyboard_rel"] or "—")


def _ck_subtitle_burned(rule, ctx):
    shots = _shots(ctx)
    if shots is None:
        subtitle_info = "未找到 storyboard.json，无法统计字幕文本"
    else:
        with_sub = sum(
            1 for s in shots
            if isinstance(s, dict) and isinstance(s.get("subtitle"), str)
            and s.get("subtitle", "").strip()
        )
        subtitle_info = "%d/%d 镜头有字幕文本" % (with_sub, len(shots))
    soft = "检出独立 Subtitle 流（可能为软字幕，非烧录）" \
        if _has_soft_subtitle_stream(ctx["probe"]) else "未检出独立软字幕流"
    return _res("warn",
                "需人工核验：字幕是否烧录进画面、白字黑描边、字体清晰且不遮挡人脸；"
                "数据层：%s；%s" % (subtitle_info, soft),
                evidence=ctx["video_rel"] or ctx["storyboard_rel"] or "—")


def _image_size(path):
    """只依赖标准库读取 PNG/JPEG 像素尺寸（int.from_bytes，不用 struct/third-party）。"""
    try:
        head = Path(path).read_bytes()[:65536]
    except Exception:
        return None
    if head[:8] == b"\x89PNG\r\n\x1a\n" and len(head) >= 24:
        return (int.from_bytes(head[16:20], "big"),
                int.from_bytes(head[20:24], "big"))
    if head[:2] == b"\xff\xd8":
        i = 2
        sof = {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7,
               0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}
        while i + 9 < len(head):
            if head[i] != 0xFF:
                i += 1
                continue
            marker = head[i + 1]
            if marker in (0xD8, 0xD9, 0x01) or 0xD0 <= marker <= 0xD7:
                i += 2
                continue
            seglen = int.from_bytes(head[i + 2:i + 4], "big")
            if seglen <= 0:
                break
            if marker in sof:
                h = int.from_bytes(head[i + 5:i + 7], "big")
                w = int.from_bytes(head[i + 7:i + 9], "big")
                return (w, h)
            i += 2 + seglen
    return None


def _find_cover(root):
    keys = ("cover", "封面", "poster", "书壳")
    exts = (".png", ".jpg", ".jpeg", ".webp")
    for base in ("output", "input"):
        try:
            paths = sorted((Path(root) / base).rglob("*"))
        except Exception:
            continue
        for p in paths:
            try:
                if p.is_file() and p.suffix.lower() in exts \
                        and any(k in p.name.lower() for k in keys):
                    return p
            except Exception:
                continue
    return None


def _ck_cover_spec(rule, ctx):
    cover = _find_cover(ctx["root"])
    if not cover:
        return _res("warn",
                    "需人工核验：未发现封面文件（cover/封面/poster/书壳），"
                    "需确认比例（3:4 或 350×500）、描边剧名、1~5MB、无拉伸",
                    evidence="—")
    size = _image_size(cover)
    if size:
        w, h = size
        ratio = "3:4" if abs(w / h - 0.75) < 0.02 else (
            "7:10" if abs(w / h - 0.70) < 0.02 else "%.3f" % (w / h))
        measured = "实测 %dx%d（约 %s）" % (w, h, ratio)
    else:
        measured = "图片尺寸无法读取（非 PNG/JPEG 或已损坏）"
    try:
        mb = cover.stat().st_size / (1024.0 * 1024.0)
        measured += "，%.2f MB" % mb
    except Exception:
        pass
    return _res("warn",
                "需人工核验：封面描边剧名、无拉伸变形、比例符合后台当前口径"
                "（版权中台 3:4 建议 1200×1600；另有 350×500 实操口径，二者不一致）；%s" % measured,
                evidence=_rel(ctx["root"], cover))


def _ck_manual(rule, ctx):
    cat = rule.get("category", "")
    if cat == "内容合规":
        ev = ctx["storyboard_rel"] or ctx["script_rel"] or "—"
    elif cat == "版权留痕":
        ev = "output/07_reports/"
    else:
        ev = ctx["video_rel"] or "—"
    return _res("warn",
                "需人工核验：%s" % rule.get("how_to_verify", ""),
                evidence=ev)


# ---------------------------------------------------------------------------
# 检查器注册表
# ---------------------------------------------------------------------------

CHECKERS = {
    "video_resolution": _ck_video_resolution,
    "video_codec": _ck_video_codec,
    "video_fps": _ck_video_fps,
    "video_bitrate": _ck_video_bitrate,
    "audio_codec": _ck_audio_codec,
    "audio_sample_rate": _ck_audio_sample_rate,
    "audio_channels": _ck_audio_channels,
    "duration": _ck_duration,
    "container": _ck_container,
    "no_alpha": _ck_no_alpha,
    "no_odd_dimension": _ck_no_odd_dimension,
    "subtitle_burned": _ck_subtitle_burned,
    "ai_label": _ck_ai_label,
    "shot_duration": _ck_shot_duration,
    "shot_count": _ck_shot_count,
    "dialogue_length": _ck_dialogue_length,
    "character_anchors": _ck_character_anchors,
    "style_consistency": _ck_style_consistency,
    "archive_completeness": _ck_archive_completeness,
    "manual": _ck_manual,
    "cover_spec": _ck_cover_spec,
}


# ---------------------------------------------------------------------------
# 单条规则 -> check 记录（SPEC 3.1）
# ---------------------------------------------------------------------------

def _one_check(rule, seq, ctx, id_map):
    rid = rule.get("id", "") if isinstance(rule, dict) else ""
    rule = rule if isinstance(rule, dict) else {}
    rec = {
        "id": id_map.get(rid) or "C%02d" % seq,
        "rule_id": rid,
        "stage": _STAGE_BY_CATEGORY.get(rule.get("category", ""), "07_reports"),
        "name": rule.get("name", ""),
        "category": rule.get("category", ""),
        "severity": rule.get("severity", "minor"),
        "status": "warn",
        "expected": rule.get("expected", ""),
        "actual": "",
        "evidence": _default_evidence(rule, ctx),
        "source": rule.get("source", ""),
        "how_to_verify": rule.get("how_to_verify", ""),
        "fix_hint": rule.get("fix_hint", ""),
    }
    try:
        key = rule.get("check", "manual")
        fn = CHECKERS.get(key)
        if fn is None:
            result = _res("warn",
                          "需人工核验：config 使用了未实现的检查器 key「%s」" % key,
                          evidence=_default_evidence(rule, ctx))
        else:
            result = fn(rule, ctx)
        rec["status"] = result.get("status", "warn")
        rec["actual"] = result.get("actual", "")
        rec["evidence"] = result.get("evidence") or _default_evidence(rule, ctx)
    except Exception as exc:
        # 单条规则异常 -> fail 并写明原因，不中断整体
        rec["status"] = "fail"
        rec["actual"] = "检查器执行异常：%s: %s" % (type(exc).__name__, exc)
        rec["evidence"] = _default_evidence(rule, ctx)
    if rec["status"] == "warn" and "需人工核验" not in rec["actual"]:
        rec["actual"] = "需人工核验：" + rec["actual"]
    return rec


def _overall(checks):
    total = len(checks)
    if total == 0:
        # 规则集未读到 / 无任何规则：无法判定，不得写死 PASS
        return {"status": "WARN", "score": 0, "total": 0,
                "passed": 0, "warned": 0, "failed": 0, "blocker_failed": 0}
    passed = sum(1 for c in checks if c.get("status") == "pass")
    warned = sum(1 for c in checks if c.get("status") == "warn")
    failed = sum(1 for c in checks if c.get("status") == "fail")
    blocker_failed = sum(
        1 for c in checks
        if c.get("status") == "fail" and c.get("severity") == "blocker"
    )
    # 评分：pass=1，warn=0.5，fail=0（fail 与未计入的 skipped 均为 0 分）
    score = round(100.0 * (passed + 0.5 * warned) / total)
    # blocker 的 fail 直接令 overall.status='FAIL'；任何 fail 亦视为未通过验收。
    if blocker_failed > 0 or failed > 0:
        state = "FAIL"
    elif warned > 0:
        state = "WARN"
    else:
        state = "PASS"
    return {
        "status": state,
        "score": score,
        "total": total,
        "passed": passed,
        "warned": warned,
        "failed": failed,
        "blocker_failed": blocker_failed,
    }


# ---------------------------------------------------------------------------
# 公开接口：run
# ---------------------------------------------------------------------------

def run(project_root: str, status: dict) -> dict:
    """读取 config/hongguo_rules.json 与 output/status.json，逐条执行规则，
    就地补全 status['checks']、status['overall']，返回 status。

    - 真实读取成片（ffmpeg -i stderr 正则解析）与素材（storyboard/characters/
      script/frames/cover/归档文件），逐条计算实测值；
    - 无法自动判定的规则标 warn，actual 写明「需人工核验」并保留 how_to_verify；
    - 绝不写死 pass；单条规则异常记为 fail 并写明原因；
    - 不向流水线抛任何异常，不写任何文件。
    """
    if not isinstance(status, dict):
        status = {}
    try:
        root = Path(project_root)
        disk = _read_json(root / "output/status.json")
        if not isinstance(disk, dict):
            disk = {}
        rules_doc = _read_json(root / "config/hongguo_rules.json")
        rules = rules_doc.get("rules", []) if isinstance(rules_doc, dict) else []
        if not isinstance(rules, list):
            rules = []

        # 也允许 status 自带规则集（便于独立调用），但以磁盘规则集为准
        ctx = _build_ctx(root, status, disk)

        existing = status.get("checks")
        id_map = {}
        if isinstance(existing, list):
            for c in existing:
                if isinstance(c, dict) and c.get("rule_id") and c.get("id"):
                    id_map[c["rule_id"]] = c["id"]

        checks = [_one_check(rule, i, ctx, id_map)
                  for i, rule in enumerate(rules, 1)]
        status["checks"] = checks
        status["overall"] = _overall(checks)
    except Exception as exc:
        # 最外层兜底：任何意外都不向流水线抛异常，也不写死 pass
        if not isinstance(status.get("checks"), list):
            status["checks"] = []
        status["overall"] = _overall(status["checks"])
        # 把原因留在已有 checks 的 actual 里，不擅自新增字段
        if status["checks"] and isinstance(status["checks"][0], dict):
            first = status["checks"][0]
            first["actual"] = (first.get("actual", "")
                               + "；run 级异常：%s: %s" % (type(exc).__name__, exc))
    return status

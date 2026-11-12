"""给新版真视频补上音轨：脚本台词(TTS) + BGM + 音效 + 响度归一化。

复用 providers 的本地音频管线，证明「真视频 + 声音」能端到端跑通。
（A/B 对照 cmp_*.mp4 仍保持静音，仅用于比画面。）
"""
import sys, json, subprocess
from pathlib import Path

ROOT = Path("/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent")
sys.path.insert(0, str(ROOT / "src"))
from providers import (synth_voice, mix_shot_audio, synth_bgm, get_ffmpeg, probe)

cfg = json.loads((ROOT / "config/project.json").read_text(encoding="utf-8"))
FF = get_ffmpeg()
PRO = ROOT / "proof"

# (镜头, 视频, 台词, 音效, 音色)
JOBS = [
    ("S05", PRO / "new_S05.mp4", "纸下面，还有一层压痕。", ["纸声"], "Tingting"),
    ("S02", PRO / "new_S02.mp4", "会议室有监控，调出来。", ["椅子轻响"], "Tingting"),
]


def add_audio(video: Path, text: str, sfx: list, voice: str, out: Path) -> dict:
    dur = float(probe(video, FF).get("duration_s", 5.0))
    vw = PRO / f"_v_{video.stem}.wav"
    mw = PRO / f"_m_{video.stem}.wav"
    bw = PRO / f"_b_{video.stem}.wav"
    synth_voice(text, voice, vw, ROOT, cfg, FF)
    mix_shot_audio(vw, sfx, dur, mw, cfg)
    synth_bgm(dur, bw, cfg)
    filt = ("[1:a]volume=1.0[v];[2:a]volume={g}[b];"
            "[v][b]amix=inputs=2:duration=first:dropout_transition=0[m];"
            "[m]loudnorm=I={i}:TP=-1.5:LRA=11[a]").format(
        g=cfg["bgm_gain"], i=cfg["target_lufs"])
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(video), "-i", str(mw), "-i", str(bw),
           "-filter_complex", filt, "-map", "0:v", "-map", "[a]",
           "-t", f"{dur:.3f}",
           "-c:v", "copy", "-c:a", cfg["audio_codec"], "-b:a", cfg["audio_bitrate"],
           "-ar", str(cfg["sample_rate"]), "-ac", str(cfg["channels"]),
           "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    for t in (vw, mw, bw):
        t.unlink(missing_ok=True)
    return {"ok": out.is_file(), "dur": round(dur, 2), "out": str(out),
            "stderr": (r.stderr or "")[-300:]}


if __name__ == "__main__":
    for sid, vid, txt, sfx, voice in JOBS:
        out = PRO / f"new_{sid}_audio.mp4"
        print(json.dumps(add_audio(vid, txt, sfx, voice, out), ensure_ascii=False))

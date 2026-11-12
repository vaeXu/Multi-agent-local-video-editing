import sys, json, subprocess
from pathlib import Path
sys.path.insert(0, "/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent")
from proof_sharp_comicify import to_mp4

FF = subprocess.check_output(
    ["python3", "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"]
).decode().strip()
ROOT = Path("/Users/xujiahua/WorkBuddy/视频剪辑/shixiang-agent")
GEN = ROOT / "input/demo/generated_video"
PRO = ROOT / "proof"
FONT = "config/font.ttc"


def find(sub: str) -> Path:
    return next(f for f in GEN.glob("*.mp4") if sub in f.name)


def probe(p: Path) -> dict:
    s = subprocess.run([FF, "-hide_banner", "-i", str(p)],
                       capture_output=True, text=True).stderr
    import re
    d = {}
    m = re.search(r"(\d{2,5})x(\d{2,5})", s)
    if m:
        d["w"], d["h"] = int(m.group(1)), int(m.group(2))
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", s)
    if m:
        d["dur"] = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3))
    return d


def motion(p: Path) -> float:
    import cv2, numpy as np
    cap = cv2.VideoCapture(str(p))
    prev, diffs = None, []
    while True:
        ok, f = cap.read()
        if not ok:
            break
        g = cv2.cvtColor(f, cv2.COLOR_BGR2GRAY).astype("float32")
        if prev is not None:
            diffs.append(float(np.mean(np.abs(g - prev))))
        prev = g
    cap.release()
    return round(sum(diffs) / len(diffs), 3) if diffs else 0.0


# 1) 真视频 → 锐化版转绘
r1 = to_mp4(find("物件大特写"), PRO / "new_S05.mp4")
r2 = to_mp4(find("人物面部特写"), PRO / "new_S02.mp4")
print("comicify:", json.dumps([r1, r2], ensure_ascii=False))

for name, old, new in [("S05", PRO / "old_S05.mp4", PRO / "new_S05.mp4"),
                       ("S02", PRO / "old_S02.mp4", PRO / "new_S02.mp4")]:
    mo, mn = motion(old), motion(new)
    print(f"{name}: 旧静态图 帧间运动量={mo} | 新真视频 帧间运动量={mn} | 提升≈{round(mn/mo,1)}x")
    # 2) 左右对照（旧=静态图 / 新=真视频），各裁到相同最短时长
    do, dn = probe(old)["dur"], probe(new)["dur"]
    t = min(do, dn)
    out = PRO / f"cmp_{name}.mp4"
    fc = (
        f"[0:v]scale=540:960:force_original_aspect_ratio=increase,crop=540:960,"
        f"setsar=1,trim=duration={t:.2f},setpts=PTS-STARTPTS,format=yuv420p[l];"
        f"[1:v]scale=540:960:force_original_aspect_ratio=increase,crop=540:960,"
        f"setsar=1,trim=duration={t:.2f},setpts=PTS-STARTPTS,format=yuv420p[r];"
        f"[l][r]hstack=inputs=2[v];"
        f"[v]drawtext=fontfile={FONT}:text='旧·静态图':fontcolor=white:fontsize=30:"
        f"box=1:boxcolor=black@0.6:x=20:y=20,"
        f"drawtext=fontfile={FONT}:text='新·真视频':fontcolor=white:fontsize=30:"
        f"box=1:boxcolor=black@0.6:x=560:y=20[v2]"
    )
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error",
           "-i", str(old), "-i", str(new),
           "-filter_complex", fc, "-map", "[v2]",
           "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
           "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    print(f"  cmp->{out.name} ok={out.is_file()} {r.stderr[-200:]}")

"""Proof: 用「真实视频 + 锐化版转绘」替代「静态图 Ken Burns」，证明糊+静态可解。

与 providers.comicify 的区别（针对根因）：
- 仅单遍轻度双边滤波（原版双遍，是糊的主因之一）
- 色阶量化 8 级（原版 6 级，平涂更死板）
- 半调网点强度 0.10（原版更重，进一步吃掉细节）
- 末尾加 unsharp mask 找回锐度
- 用 LANCZOS 上采样（原版 INTER_AREA 更糊）
"""
import sys, json, subprocess
import cv2, numpy as np
from pathlib import Path

FF = subprocess.check_output(
    ["python3", "-c", "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())"]
).decode().strip()


def sharp_comicify(bgr: np.ndarray) -> np.ndarray:
    d, sig = 9, 45
    smooth = cv2.bilateralFilter(bgr, d, sig, sig)          # 单遍、轻
    step = 256.0 / 8
    quant = np.clip(np.floor(smooth.astype(np.float32) / step) * step + step / 2, 0, 255)
    gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 3)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                  cv2.THRESH_BINARY, 11, 4)
    ink = (edges < 128).astype(np.float32)[:, :, None]
    ink = cv2.GaussianBlur(ink, (3, 3), 0)
    if ink.ndim == 2:
        ink = ink[:, :, None]
    out = quant * (1.0 - 0.55 * ink)
    h, w = out.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dots = (((np.sin(xx * 0.14) * np.sin(yy * 0.14)) + 1) * 0.5) ** 8
    lum = cv2.cvtColor(np.clip(out, 0, 255).astype(np.uint8), cv2.COLOR_BGR2GRAY)
    shadow = 1.0 - lum.astype(np.float32) / 255.0
    out -= (dots * shadow * 0.10 * 255)[:, :, None]
    out = np.clip(out, 0, 255).astype(np.uint8)
    hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] *= 0.92
    out = cv2.cvtColor(np.clip(hsv, 0, 255).astype(np.uint8), cv2.COLOR_HSV2BGR)
    tint = np.array([0.93, 0.97, 1.04], dtype=np.float32)   # B,G,R 冷调
    out = np.clip(out.astype(np.float32) * tint[::-1][None, None, :], 0, 255)
    blur = cv2.GaussianBlur(out, (0, 0), 2.0)
    out = cv2.addWeighted(out, 1.5, blur, -0.5, 0)          # unsharp 找回锐度
    cy, cx = h / 2, w / 2
    Y, X = np.ogrid[:h, :w]
    r = np.sqrt(((X - cx) / cx) ** 2 + ((Y - cy) / cy) ** 2) / np.sqrt(2)
    vig = 1.0 - 0.18 * np.clip(r, 0, 1) ** 2
    return np.clip(out * vig[:, :, None], 0, 255).astype(np.uint8)


def fit(bgr: np.ndarray) -> np.ndarray:
    h, w = bgr.shape[:2]
    bgr = bgr[int(h * 0.075):, :]                            # 去顶部「AI生成」水印
    h, w = bgr.shape[:2]
    tgt = 1080 / 1920
    if w / h > tgt:
        nw = int(round(h * tgt)); x0 = (w - nw) // 2
        bgr = bgr[:, x0:x0 + nw]
    else:
        nh = int(round(w / tgt)); y0 = max(0, (h - nh) // 3)
        bgr = bgr[y0:y0 + nh, :]
    return cv2.resize(bgr, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)


def to_mp4(src: Path, dst: Path, fps: int = 30, bitrate: str = "12M") -> dict:
    cap = cv2.VideoCapture(str(src))
    sfps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    ofps = max(1, int(round(sfps)))
    cmd = [FF, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", "1080x1920",
           "-r", str(ofps), "-i", "-", "-an",
           "-c:v", "libx264", "-preset", "veryfast",
           "-b:v", bitrate, "-minrate", "8M", "-maxrate", "12M", "-bufsize", "20M",
           "-pix_fmt", "yuv420p", "-r", str(ofps), "-movflags", "+faststart", str(dst)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                        stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    n = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        p.stdin.write(np.ascontiguousarray(sharp_comicify(fit(f))).tobytes())
        n += 1
    cap.release()
    try:
        p.stdin.close()
    except Exception:
        pass
    err = (p.stderr.read() or b"").decode("utf-8", "ignore")
    p.wait()
    return {"ok": dst.is_file() and n > 0, "frames": n, "fps": ofps,
            "dst": str(dst), "stderr": err[-300:]}


if __name__ == "__main__":
    src = Path(sys.argv[1]); dst = Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    print(json.dumps(to_mp4(src, dst), ensure_ascii=False))

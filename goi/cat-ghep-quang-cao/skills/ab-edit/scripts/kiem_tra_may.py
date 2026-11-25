"""Kiểm tra máy Windows đã đủ công cụ cho skill ab-edit chưa. Chỉ đọc, không cài gì.
  python kiem_tra_may.py
"""
import importlib.metadata as md
import json
import shutil
import subprocess
from pathlib import Path

from chung import BRANDS, CFG, STUDIO, tim_ffmpeg

THIEU = []


def ok(ten, chi_tiet=""):
    print(f"  ✔ {ten}" + (f": {chi_tiet}" if chi_tiet else ""))


def ng(ten, cach_sua):
    print(f"  ✘ {ten} — {cach_sua}")
    THIEU.append(ten)


def chay(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=60, encoding="utf-8", errors="replace")
    except Exception:
        return None


def goi(ten):
    try:
        return md.version(ten)
    except md.PackageNotFoundError:
        return ""


print("Kiểm tra máy — skill ab-edit v3 (Windows)")

# Thư mục làm việc
if STUDIO.is_dir():
    ok("Thư mục studio", str(STUDIO))
    for d in ("01-video-mau", "02-source-tho", "03-kich-ban", "04-giong-doc", "05-tai-nguyen", "06-thanh-pham", "07-du-an"):
        if not (STUDIO / d).is_dir():
            ng(f"Thư mục {d}", "chạy tao_du_an.py một lần sẽ tự tạo")
else:
    ng("Thư mục studio", f"sửa 'studio' trong config.json (đang là {STUDIO})")

# FFmpeg + bộ lọc
try:
    ff = tim_ffmpeg()
    ok("FFmpeg", chay([ff, "-version"]).stdout.split("\n")[0][:45])
    loc = chay([ff, "-hide_banner", "-filters"]).stdout
    for f, vi in [("drawtext", "chữ"), ("bilateral", "làm mịn da"), ("minterpolate", "cảnh trám chậm"),
                  ("loudnorm", "chuẩn âm lượng"), ("afftdn", "lọc ồn"), ("silencedetect", "dò khoảng lặng")]:
        if f" {f} " in loc:
            ok(f"  bộ lọc {f} ({vi})")
        else:
            ng(f"bộ lọc {f} ({vi})", "cần bản FFmpeg full (Gyan)")
    ma = chay([ff, "-hide_banner", "-encoders"]).stdout
    ok("  mã hoá GPU h264_nvenc") if "h264_nvenc" in ma else print("  ⚠ Không có NVENC — sẽ dùng libx264 (chậm hơn)")
    ok("  ProRes 4444 (chữ nền trong suốt)") if "prores_ks" in ma else ng("prores_ks", "cần bản FFmpeg full")
    tim_ffmpeg("ffprobe")
    ok("ffprobe")
except SystemExit as e:
    ng("FFmpeg", str(e))

# Node + Remotion
nd = chay([shutil.which("node") or "node", "--version"])
ok("Node.js", nd.stdout.strip()) if nd and nd.returncode == 0 else ng("Node.js ≥ 20", "winget install OpenJS.NodeJS.LTS")
rp = STUDIO / "_engine" / "remotion" / "node_modules" / "remotion" / "package.json"
ok("Remotion", json.loads(rp.read_text(encoding="utf-8"))["version"]) if rp.exists() else ng("Remotion", "npm install trong _engine/remotion")

# Python + thư viện
py = Path(CFG["python"]) if Path(CFG["python"]).exists() else Path(shutil.which(CFG["python"]) or CFG["python"])
ok("Python", str(py)) if py.exists() else ng("Python", "winget install Python.Python.3.12")
for ten, vi, cai in [("faster-whisper", "nghe lời tiếng Việt", "faster-whisper"),
                     ("nvidia-cudnn-cu12", "Whisper chạy GPU", "nvidia-cudnn-cu12==9.* nvidia-cublas-cu12"),
                     ("mediapipe", "tìm vị trí mặt", "mediapipe"),
                     ("opencv-python", "đọc khung hình", "opencv-python"),
                     ("auto-editor", "cắt khoảng lặng nhanh", "auto-editor"),
                     ("playwright", "quay màn hình web", "playwright"),
                     ("elevenlabs", "giọng AI (tuỳ chọn)", "elevenlabs")]:
    v = goi(ten)
    ok(f"{ten} ({vi})", v) if v else ng(f"{ten} ({vi})", f"pip install {cai}")

# Chrome (quay khối chữ / đồ hoạ HTML)
ch = Path(CFG.get("chrome", ""))
ok("Google Chrome", str(ch)) if ch.exists() else ng("Google Chrome", "cài Chrome hoặc sửa 'chrome' trong config.json")

# GPU
g = chay(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"])
ok("GPU NVIDIA", g.stdout.strip()) if g and g.returncode == 0 else print("  ⚠ Không thấy GPU NVIDIA — Whisper/encode chạy CPU (chậm)")

# Font chữ có tiếng Việt
fonts = {f.name.lower() for d in (Path("C:/Windows/Fonts"), Path.home() / "AppData/Local/Microsoft/Windows/Fonts") if d.exists() for f in d.iterdir()}
for ten in ("bebas", "montserrat", "bevietnam"):
    print(f"  {'✔' if any(ten in f for f in fonts) else '⚠'} Font {ten} {'đã cài' if any(ten in f for f in fonts) else 'chưa cài — khối chữ dùng Google Fonts dự phòng'}")

# Thương hiệu
br = sorted(p.stem for p in BRANDS.glob("*.json") if not p.stem.startswith("_"))
ok("Thương hiệu", ", ".join(br)) if br else ng("Thương hiệu", "chép brands/_mau.json thành brands/<tên>.json")
print("→ Đủ công cụ." if not THIEU else f"→ Còn thiếu {len(THIEU)} mục ✘ ở trên.")

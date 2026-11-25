"""Ghép các đoạn đã chọn thành master dọc 1080x1920, lọc ồn, chuẩn -16 LUFS.
  python lap_master.py <thư mục dự án>
Đọc doan.json: {"nguon": [file...], "doan": [[số nguồn, từ giây, đến giây]...], "toc": 1.0}
Chế độ giọng AI, không có cảnh quay: {"giong": "file giọng"}. Master là hình đen kèm tiếng, canh.json không dùng được cảnh nguoi*.
Ghi render/master.mp4, public/master.mp4, public/khung-cuoi.jpg, edl-master.json."""
import os
import subprocess
import sys
from pathlib import Path

from chung import chay, doc, ffmpeg_ma_hoa, ghi

VAO, RA = 0.06, 0.12
AM = "highpass=f=80,afftdn=nr=12:nf=-30:tn=1,acompressor=threshold=-20dB:ratio=3:attack=10:release=200,loudnorm=I=-16:TP=-1.5:LRA=9"
MAN = "scale=1080:1920:flags=lanczos,eq=contrast=1.05:saturation=1.05,unsharp=5:5:0.8:3:3:0,format=yuv420p"

da = Path(sys.argv[1])
cfg = doc(da / "doan.json")
(da / "render").mkdir(exist_ok=True)
(da / "public").mkdir(exist_ok=True)
if "giong" in cfg:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", cfg["giong"]], capture_output=True, text=True, check=True)
    dai = float(r.stdout)
    chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi", "-i", f"color=c=black:s=1080x1920:r=30:d={dai}", "-i", cfg["giong"], "-af", "loudnorm=I=-16:TP=-1.5:LRA=9,aresample=48000",
          "-c:v", "libx264", "-preset", "veryfast", "-crf", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "320k", "-shortest", "-movflags", "+faststart", da / "render" / "master.mp4"])
    ghi(da / "edl-master.json", [[0, round(dai, 3)]])
    print("xong giọng AI", round(dai, 2), "giây")
    sys.exit(0)
DOAN, TOC = cfg["doan"], cfg.get("toc", 1.0)

loc, ghep, moc, t = [], "", [], 0.0
for i, (n, a, b) in enumerate(DOAN):
    a2, b2 = max(0, a - VAO), b + RA
    d = b2 - a2
    loc.append(f"[{n}:v]trim={a2:.3f}:{b2:.3f},setpts=PTS-STARTPTS,fps=30[v{i}];[{n}:a]atrim={a2:.3f}:{b2:.3f},asetpts=PTS-STARTPTS,aresample=48000,afade=t=in:d=0.02,afade=t=out:st={d - 0.03:.3f}:d=0.03[a{i}]")
    ghep += f"[v{i}][a{i}]"
    moc.append([round(t / TOC, 3), round((t + d) / TOC, 3)])
    t += d
loc.append(f"{ghep}concat=n={len(DOAN)}:v=1:a=1[cv][ca];[cv]setpts=PTS/{TOC},fps=30,{MAN}[v];[ca]atempo={TOC},{AM},aresample=48000[a]")
vao = [x for f in cfg["nguon"] for x in ("-i", f)]
ra = da / "render" / "master.mp4"
chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *vao, "-filter_complex", ";".join(loc), "-map", "[v]", "-map", "[a]", *ffmpeg_ma_hoa(),
      "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", ra])
ghi(da / "edl-master.json", moc)

pub = da / "public" / "master.mp4"
pub.unlink(missing_ok=True)
try:
    os.link(ra, pub)
except OSError:
    chay(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", ra, "-c", "copy", pub])
subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-sseof", "-0.2", "-i", str(ra), "-frames:v", "1", "-update", "1", "-q:v", "1", str(da / "public" / "khung-cuoi.jpg")], check=True)
print("xong", len(DOAN), "đoạn", round(t / TOC, 2), "giây")

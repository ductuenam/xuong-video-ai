"""Bản master lời NGƯỜI NÓI CHÍNH: dựng đứng, chỉnh màu + cà da, LÀM MỊN DA chỉ vùng mặt–cổ, lọc tạp âm, −16 LUFS, mã hoá GPU NVENC.
Port từ master-nguoi-noi.sh v2 (macOS VideoToolbox → Windows NVENC).
  python master_nguoi_noi.py <nguồn> <ra.mp4> --cx 0.47 --cy 0.34 [--rx 0.22 --ry 0.14] [--fps 50] [--t giây] [--edl edl.json]
  Thử 1 khung trước: --preview <giây> → ra <ra>.png (so sánh trước/sau bằng --so-sanh)
  --edl: ghép luôn các đoạn giữ lại theo EDL (bỏ lặng, bỏ câu NG) — xuất 1 file liền.
"""
import argparse
import json
import subprocess
from pathlib import Path

from chung import chan_ghi_source, ma_hoa, sao_luu, thoi_luong, tim_ffmpeg

# Màu + da (đã duyệt với khách ngày 13/10/2026)
MAU = ("eq=brightness=0.025:contrast=1.06:saturation=1.14:gamma=1.04,"
       "colorbalance=rs=0.02:gs=-0.015:bs=-0.01:rm=0.035:gm=-0.01:bm=-0.02:rh=0.01:bh=0.015")
AM = "highpass=f=80,afftdn=nr=12:nf=-30:tn=1,acompressor=threshold=-20dB:ratio=3:attack=10:release=200,loudnorm=I=-16:TP=-1.5:LRA=9"


def chieu_doc(src):
    """Kích thước sau khi xoay theo cờ (W, H)."""
    p = subprocess.run([tim_ffmpeg("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries",
                        "stream=width,height:stream_side_data=rotation", "-of", "json", str(src)], capture_output=True, text=True).stdout
    st = json.loads(p)["streams"][0]
    rot = abs(int(next((d.get("rotation", 0) for d in st.get("side_data_list", [])), 0)))
    return (st["height"], st["width"]) if rot in (90, 270) else (st["width"], st["height"])


def bo_loc_hinh(W, H, cx, cy, rx, ry):
    # Mặt nạ da tính ở 1/4 độ phân giải (nhanh): màu da YCbCr (Cb 85–128, Cr 136–178) ∩ elip quanh mặt
    mw, mh = W // 4 // 2 * 2, H // 4 // 2 * 2
    MX, MY, MRX, MRY = round(cx * mw), round(cy * mh), round(rx * mw), round(ry * mh)
    mask = (f"scale={mw}:{mh},format=yuv444p,geq=lum='if(between(cb(X,Y),85,128)*between(cr(X,Y),136,178)*"
            f"lte(pow((X-{MX})/{MRX},2)+pow((Y-{MY})/{MRY},2),1),165,0)':cb=128:cr=128,extractplanes=y,gblur=sigma=6,scale={W}:{H}")
    sk = (f"split=3[a][b][c];[b]scale={W // 2 // 2 * 2}:{H // 2 // 2 * 2},bilateral=sigmaS=8:sigmaR=0.06,eq=brightness=0.012,"
          f"scale={W}:{H}:flags=bicubic,format=yuva420p[s];[c]{mask}[m];[s][m]alphamerge[sm];[a][sm]overlay,unsharp=5:5:0.4,format=yuv420p")
    return f"scale={W}:{H},{MAU},{sk}"


def bo_loc_net(W, H, phong):
    """Webcam/nguồn nhỏ cần cắt dọc: không tăng sáng, không làm mịn da (mất chi tiết, trông lóa); phóng sẵn bằng lanczos rồi làm nét. Bài học video 01 (04/11/2026)."""
    PW, PH = round(W * phong / 2) * 2, round(H * phong / 2) * 2
    return f"scale={PW}:{PH}:flags=lanczos,eq=contrast=1.1:saturation=1.1:gamma=0.95,unsharp=7:7:1.1:5:5:0,format=yuv420p"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("out")
    ap.add_argument("--cx", type=float, default=0.47)
    ap.add_argument("--cy", type=float, default=0.34)
    ap.add_argument("--rx", type=float, default=0.22)
    ap.add_argument("--ry", type=float, default=0.14)
    ap.add_argument("--fps", type=float, default=None, help="mặc định giữ fps nguồn")
    ap.add_argument("--t", type=float, default=None)
    ap.add_argument("--edl")
    ap.add_argument("--net", type=float, default=None, help="bản nét cho nguồn nhỏ: bỏ mịn da + tăng sáng, phóng sẵn N lần (vd 1.778 khi cắt dọc từ 1080p)")
    ap.add_argument("--preview", type=float, default=None)
    ap.add_argument("--so-sanh", action="store_true", help="với --preview: ghép trước | sau cạnh nhau")
    a = ap.parse_args()
    out = Path(a.out)
    chan_ghi_source(out)
    W, H = chieu_doc(a.src)
    V = bo_loc_net(W, H, a.net) if a.net else bo_loc_hinh(W, H, a.cx, a.cy, a.rx, a.ry)
    ff = tim_ffmpeg()

    if a.preview is not None:
        png = out.with_suffix(".png")
        fc = f"[0:v]{V}[o]" if not a.so_sanh else f"[0:v]split[x][y];[y]{V}[o1];[x]scale={W}:{H}[o0];[o0][o1]hstack,scale=-2:1600[o]"
        subprocess.run([ff, "-v", "error", "-y", "-ss", str(a.preview), "-i", a.src, "-frames:v", "1", "-filter_complex", fc, "-map", "[o]", str(png)], check=True)
        print(f"✔ ảnh thử: {png}")
        return

    sao_luu(out)
    if a.edl:
        E = json.loads(Path(a.edl).read_text(encoding="utf-8"))
        parts = "".join(f"[0:v]trim={s}:{e},setpts=PTS-STARTPTS[v{i}];[0:a]atrim={s}:{e},asetpts=PTS-STARTPTS,"
                        f"afade=t=in:d=0.02,afade=t=out:st={e - s - 0.03:.3f}:d=0.03[a{i}];" for i, (s, e) in enumerate(E))
        cat = "".join(f"[v{i}][a{i}]" for i in range(len(E))) + f"concat=n={len(E)}:v=1:a=1[cv][ca]"
        fc = f"{parts}{cat};[cv]{V}[v];[ca]{AM}[a]"
    else:
        fc = f"[0:v]{V}[v];[0:a]{AM}[a]"
    cmd = [ff, "-v", "error", "-stats", "-y", "-i", a.src]
    if a.t:
        cmd += ["-t", str(a.t)]
    cmd += ["-filter_complex", fc, "-map", "[v]", "-map", "[a]"]
    if a.fps:
        cmd += ["-r", str(a.fps)]
    cmd += [*ma_hoa("70M"), "-ar", "48000", "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)]
    subprocess.run(cmd, check=True)
    print(f"✔ master: {out} ({thoi_luong(out):.2f}s)")


if __name__ == "__main__":
    main()

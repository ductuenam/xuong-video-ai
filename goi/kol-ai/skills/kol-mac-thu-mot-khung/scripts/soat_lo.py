"""Soát một lô clip Muse của một video KOL trong một lệnh.

Dùng: python soat_lo.py <thư mục video> [--tai vNN]
--tai vNN: chuyển các tệp <thu_muc_tai_ve>/vNN-*.mp4 (và vNN-*.webp/png) vào thư mục video, bỏ tiền tố.
Việc làm:
- so_loi.py cho s1-noi, s2-noi, s3-xoay với loi1-3.txt, in mốc từng chữ và tốc độ nói (chữ/giây).
- Đo độ to 50 ms ở 0,9 giây đầu và từ giây 8,6 đến hết mỗi cảnh nói: biết chỗ bắt đầu, dứt câu.
- tach_khung_soat.py 2 khung/giây cho mọi clip, ghép thành soat/lo.jpg (mỗi cột một clip).
- soi_mat.py cho 3 cảnh nói (soi-mat/*.jpg), để chọn điểm nối lúc mắt mở.
"""
import argparse, shutil, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

S = Path(__file__).parent
sys.path.insert(0, str(S))
from chung import doc_cau_hinh, thu_muc  # noqa: E402


def muc_am(f, a, b):
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(a), "-t", str(b - a), "-i", str(f), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                       capture_output=True).stdout
    x = np.frombuffer(r, np.int16).astype(float) / 32768
    n = 800
    return " ".join(f"{a + i * 0.05:.2f}:{20 * np.log10(np.sqrt(np.mean(x[i * n:(i + 1) * n] ** 2)) + 1e-9):.0f}" for i in range(len(x) // n))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--tai")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    d = Path(a.thu_muc)
    if a.tai:
        tai = thu_muc(doc_cau_hinh(), "thu_muc_tai_ve")
        for duoi in ("mp4", "webp", "png", "jpg"):
            for f in tai.glob(f"{a.tai}-*.{duoi}"):
                shutil.move(str(f), d / f.name[len(a.tai) + 1:])
    noi = [f for f in ["s1-noi", "s2-noi"] if (d / f"{f}.mp4").exists()]
    cap = [f"{f}.mp4=loi{i + 1}.txt" for i, f in enumerate(["s1-noi", "s2-noi"]) if f in noi and (d / f"loi{i + 1}.txt").exists()]
    if cap:
        r = subprocess.run([sys.executable, "-X", "utf8", str(S / "so_loi.py"), *cap], cwd=d, capture_output=True, text=True, encoding="utf-8")
        print("\n".join(l for l in r.stdout.splitlines() if "Warning" not in l))
    for f in noi:
        print(f"[âm] {f} đầu: {muc_am(d / (f + '.mp4'), 0, 0.9)}")
        print(f"[âm] {f} cuối: {muc_am(d / (f + '.mp4'), 8.6, 10)}")
    clip = sorted(p.stem for p in d.glob("*.mp4") if p.stem.startswith(("s1-", "s2-")) and "lui" not in p.stem)
    subprocess.run([sys.executable, "-X", "utf8", str(S / "tach_khung_soat.py"), *[c + ".mp4" for c in clip], "--out-dir", "soat",
                    "--fps", "2", "--giay-moi-trang", "10", "--rong", "180"], cwd=d, capture_output=True)
    ims = [Image.open(d / "soat" / f"{c}_trang01.jpg") for c in clip if (d / "soat" / f"{c}_trang01.jpg").exists()]
    if ims:
        s = Image.new("RGB", (sum(i.width for i in ims), max(i.height for i in ims)))
        x = 0
        for i in ims:
            s.paste(i, (x, 0)); x += i.width
        s.save(d / "soat" / "lo.jpg")
        print("Bảng khung:", d / "soat" / "lo.jpg", "thứ tự", clip)
    subprocess.run([sys.executable, "-X", "utf8", str(S / "soi_mat.py"), *[f + ".mp4" for f in noi], "--out-dir", "soi-mat"], cwd=d, capture_output=True)
    print("Soi mắt: soi-mat/<cảnh>-mat.jpg")


if __name__ == "__main__":
    main()

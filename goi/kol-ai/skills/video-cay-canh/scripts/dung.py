"""Dựng thành phẩm cho cả lô: cắt đoạn lỗi, làm chậm có nội suy, khung 720x1280, nhạc, chuẩn âm lượng, kiểm.

Dùng: python dung.py <du_an> [--chi c01,c03]
Mỗi cảnh ra 2 file trong <du_an>/thanh-pham/:
  <ten>-khong-nhac.mp4   luôn có; đăng lên nền tảng nào cũng được, chọn nhạc trong thư viện nền tảng lúc đăng
  <ten>[-CHI-FACEBOOK].mp4    có nhạc. thu_muc_nhac để trống → dùng 8 bài nhạc mẫu CC0 trong nhac-mau/ (đăng đâu cũng
                         được), tự chọn bài hợp không khí cảnh theo nhac-mau/khong-khi.json, hoặc theo "nhac" của cảnh;
                         điền thư mục → dùng nhạc trong đó; "khong" → không lót nhạc.
                         Nhạc tên CHI-FACEBOOK-* → file ra có chữ CHI-FACEBOOK, chỉ được đăng Facebook.
Cuối cùng kiểm: khổ 720x1280, âm lượng quanh mức lufs, nhạc không tối đục (cổng đo nhạc). Thoát mã 1 nếu có file hỏng.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import can, chay, doc_cau_hinh, doc_du_an, in_utf8, ten_canh, thoi_luong  # noqa: E402

import numpy as np  # noqa: E402

# Cổng nhạc: đo từ 11 video cây cảnh đã được khách duyệt (độ sáng 545–2.344 Hz, 1,2–2,6 nhịp gõ/giây)
# so với 2 video bị chê "chán" (430 Hz / 1,5 nhịp; 627 Hz / 1,7 nhịp).
def do_nhac(path, giay=12, sr=22050):
    raw = chay([can("ffmpeg"), "-v", "error", "-i", str(path), "-t", str(giay), "-vn", "-ac", "1", "-ar", str(sr),
                "-f", "f32le", "-"], capture_output=True).stdout
    x = np.frombuffer(raw, dtype=np.float32)
    if len(x) < sr:
        return None, None
    n, h = 2048, 512
    fr = np.lib.stride_tricks.sliding_window_view(x, n)[::h] * np.hanning(n)
    S = np.abs(np.fft.rfft(fr, axis=1))
    fq = np.fft.rfftfreq(n, 1 / sr)
    sang = float(((S * fq).sum(1) / (S.sum(1) + 1e-9)).mean())
    fl = np.maximum(np.diff(np.log1p(S), axis=0), 0).sum(1)
    z = (fl - fl.mean()) / (fl.std() + 1e-9)
    go = sum(1 for i in range(1, len(z) - 1) if z[i] > 1.5 and z[i] >= z[i - 1] and z[i] >= z[i + 1]) / (len(x) / sr)
    return sang, go


def nhac_dat(sang, go):
    if sang is None:
        return False
    return (sang >= 900 and go >= 1.2) or (sang >= 500 and go >= 1.9)


def chon_bai(c, nhac, khong_khi, da_dung):
    """Ưu tiên 'nhac' ghi trong cảnh; rồi bài trúng nhiều từ khóa không khí nhất; tránh bài vừa dùng."""
    chi_dinh = str(c.get("nhac", "")).strip()
    if chi_dinh:
        for b in nhac:
            if b.name.startswith(chi_dinh):
                return b
    mo_ta = (c.get("anh", "") + " " + c.get("may", "") + " " + c.get("ten", "").replace("-", " ")).lower()
    def diem(b):
        tu = khong_khi.get(b.name[:7], [])
        trung = sum(1 for t in tu if t in mo_ta)
        gan = da_dung[::-1].index(b) if b in da_dung else 99
        return (trung, min(gan, 3))
    return max(nhac, key=diem)


def lufs(path):
    r = chay([can("ffmpeg"), "-i", str(path), "-af", "ebur128", "-f", "null", "-"],
             capture_output=True, text=True, encoding="utf-8", errors="ignore")
    m = re.findall(r"^\s+I:\s+(-?[0-9.]+) LUFS", r.stderr, re.M)
    return float(m[-1]) if m else None


def main():
    in_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("--chi", help="chỉ dựng các mã này, cách nhau dấu phẩy")
    a = ap.parse_args()
    d, da = doc_du_an(a.du_an)
    cfg, _ = doc_cau_hinh()
    cfg = cfg or {}
    toc = float(cfg.get("toc_do", 0.85))
    muc = float(cfg.get("lufs", -14))
    # Để trống thu_muc_nhac = dùng 8 bài nhạc mẫu CC0 đi kèm gói (nhac-mau/), "khong" = không lót nhạc.
    gt = str(cfg.get("thu_muc_nhac") or "").strip()
    if gt.lower() == "khong":
        thu_nhac = None
    else:
        thu_nhac = Path(gt) if gt else Path(__file__).resolve().parent.parent / "nhac-mau"
    nhac = sorted(p for p in thu_nhac.glob("*") if p.suffix.lower() in (".mp3", ".m4a", ".wav")) if thu_nhac else []
    kk = (thu_nhac / "khong-khi.json") if thu_nhac else None
    khong_khi = json.loads(kk.read_text(encoding="utf-8")) if kk and kk.is_file() else {}
    da_dung = []
    chi = set(a.chi.split(",")) if a.chi else None
    ra = d / "thanh-pham"
    ra.mkdir(exist_ok=True)
    cat = da.get("cat", {})
    hong = []
    for i, c in enumerate(da["canh"]):
        t = ten_canh(c)
        if chi and c["ma"] not in chi:
            continue
        f = d / "clip" / f"{t}.mp4"
        if not f.is_file():
            print(f"✘ {t}: chưa có clip")
            hong.append(t)
            continue
        tu, den = cat.get(t, [0, thoi_luong(f)])
        dai = round((den - tu) / toc, 2)
        v = (f"trim={tu}:{den},setpts=(PTS-STARTPTS)/{toc},"
             f"minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:vsbmc=1,"
             f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
             f"trim=0:{dai},setpts=PTS-STARTPTS,fade=t=in:d=0.4,format=yuv420p")
        kn = ra / f"{t}-khong-nhac.mp4"
        chay([can("ffmpeg"), "-v", "error", "-y", "-i", str(f), "-vf", v, "-an", "-c:v", "libx264", "-crf", "18",
              "-preset", "medium", "-movflags", "+faststart", str(kn)], check=True)
        dong = f"{t}: {dai}s"
        if nhac:
            bai = chon_bai(c, nhac, khong_khi, da_dung) if khong_khi or c.get("nhac") else nhac[i % len(nhac)]
            da_dung.append(bai)
            fb = bai.name.upper().startswith("CHI-FACEBOOK")
            cn = ra / f"{t}{'-CHI-FACEBOOK' if fb else ''}.mp4"
            am = (f"[1:a]atrim=0:{dai},asetpts=PTS-STARTPTS,afade=t=out:st={max(0, dai - 1.2)}:d=1.2,"
                  f"loudnorm=I={muc}:TP=-1.5:LRA=11[a]")
            chay([can("ffmpeg"), "-v", "error", "-y", "-i", str(kn), "-stream_loop", "-1", "-i", str(bai),
                  "-filter_complex", am, "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                  "-ar", "48000", "-movflags", "+faststart", "-t", str(dai), str(cn)], check=True)
            l = lufs(cn)
            dong += f", nhạc {bai.name}, {l} LUFS" + (" — CHỈ ĐĂNG FACEBOOK" if fb else "")
            sang, go = do_nhac(cn)
            dong += f", nhạc sáng {sang:.0f} Hz, {go:.1f} nhịp/giây" if sang else ""
            if l is None or abs(l - muc) > 2:
                hong.append(t)
                dong = "✘ " + dong + " (âm lượng lệch)"
            elif not nhac_dat(sang, go):
                hong.append(t)
                dong = "✘ " + dong + " (NHẠC TỐI ĐỤC, NHẠT: đổi bài hoặc chọn đoạn sôi hơn)"
        r = chay([can("ffprobe"), "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height",
                  "-of", "csv=p=0", str(kn)], capture_output=True, text=True).stdout.strip()
        if r != "720,1280":
            hong.append(t)
            dong = "✘ " + dong + f" (khổ {r})"
        print(("" if dong.startswith("✘") else "✔ ") + dong, flush=True)
    print(f"\nThành phẩm ở {ra}")
    sys.exit(1 if hong else 0)


if __name__ == "__main__":
    main()

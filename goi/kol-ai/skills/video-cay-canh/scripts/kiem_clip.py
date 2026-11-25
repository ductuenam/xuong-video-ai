"""Tự soi lỗi từng clip Muse trước khi dựng.

Dùng: python kiem_clip.py <du_an>
Với mỗi clip trong <du_an>/clip/:
  - tờ soi kiem/<ten>.jpg: 20 khung, mỗi khung cách 0,5 giây (Claude PHẢI mở xem từng tờ);
  - đứng hình (freezedetect);
  - nhảy cảnh: Muse thỉnh thoảng tự cắt sang góc khác giữa clip. Đo độ khác giữa hai khung liền nhau,
    chỗ vọt cao bất thường là chỗ nhảy; đề xuất giữ đoạn liền mạch dài nhất và ghi vào du-an.json "cat".
Ghi kiem/bao-cao.json. Thoát mã 1 nếu có clip phải cắt hoặc làm lại.
"""
import json
import re
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import can, chay, doc_du_an, in_utf8, ten_canh, thoi_luong  # noqa: E402

FPS = 8
W, H = 64, 114
NGUONG_TOI_THIEU = 8.0   # độ khác trung bình ảnh thô (0-255) tối thiểu mới coi là nhảy
TI_LE = 2.8              # gấp bao nhiêu lần mức chuyển động quanh đó
DOAN_NGAN_NHAT = 6.0     # giây; đoạn liền mạch ngắn hơn thì phải làm lại clip


def khung(path):
    b = chay([can("ffmpeg"), "-v", "error", "-i", str(path), "-vf", f"fps={FPS},scale={W}:{H},format=gray",
              "-f", "rawvideo", "-"], capture_output=True).stdout
    a = np.frombuffer(b, np.uint8).astype(float)
    return a[: a.size // (W * H) * W * H].reshape(-1, H, W)


def tim_nhay(fr):
    """So ảnh thô 19x16 ô: máy đi chậm thì bố cục thô gần như không đổi, nhảy cảnh thì đổi hẳn.
    Một khung là 'nhảy' khi độ khác gấp TI_LE lần mức quanh nó (±1 giây) và đủ lớn.
    Chỉnh trên 10 clip thật 20/11/2026: 2 clip nhảy ra tỉ lệ 3,5 và 4,0; clip lành tối đa 2,3."""
    if len(fr) < 3:
        return []
    lo = fr.reshape(len(fr), 19, H // 19, 16, W // 16).mean(axis=(2, 4))
    d = np.abs(np.diff(lo, axis=0)).mean(axis=(1, 2))
    ra = []
    for i in range(len(d)):
        nb = np.concatenate([d[max(0, i - FPS):i], d[i + 1:i + 1 + FPS]])
        if d[i] > NGUONG_TOI_THIEU and d[i] / (np.median(nb) + 0.3) > TI_LE:
            t = round((i + 1) / FPS, 2)
            if not ra or t - ra[-1] > 0.5:
                ra.append(t)
    return ra


def dung_hinh(path):
    r = chay([can("ffmpeg"), "-v", "info", "-i", str(path), "-vf", "freezedetect=n=0.002:d=0.8", "-map", "0:v",
              "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="ignore")
    return [float(x) for x in re.findall(r"freeze_start: ([0-9.]+)", r.stderr)]


def main():
    in_utf8()
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    d, da = doc_du_an(sys.argv[1])
    (d / "kiem").mkdir(exist_ok=True)
    bao, can_cat, lam_lai = {}, {}, []
    for c in da["canh"]:
        t = ten_canh(c)
        f = d / "clip" / f"{t}.mp4"
        if not f.is_file():
            print(f"✘ {t}: chưa có clip")
            lam_lai.append(t)
            continue
        dai = round(thoi_luong(f), 2)
        chay([can("ffmpeg"), "-v", "error", "-y", "-i", str(f), "-vf", "fps=2,scale=160:-1,tile=10x2",
              "-frames:v", "1", str(d / "kiem" / f"{t}.jpg")])
        nhay = tim_nhay(khung(f))
        dung = dung_hinh(f)
        moc = [0.0] + nhay + [dai]
        doan = max(zip(moc, moc[1:]), key=lambda p: p[1] - p[0])
        bao[t] = {"dai": dai, "nhay_canh": nhay, "dung_hinh": dung, "doan_giu": list(doan)}
        if dung:
            lam_lai.append(t)
            print(f"✘ {t}: đứng hình từ giây {dung} → tạo lại clip")
        elif nhay and doan[1] - doan[0] < DOAN_NGAN_NHAT:
            lam_lai.append(t)
            print(f"✘ {t}: nhảy cảnh ở {nhay}, đoạn liền dài nhất chỉ {doan[1]-doan[0]:.1f}s → tạo lại clip")
        elif nhay:
            can_cat[t] = [round(doan[0] + (0.25 if doan[0] else 0), 2), round(doan[1] - (0.25 if doan[1] < dai else 0), 2)]
            print(f"! {t}: nhảy cảnh ở {nhay} → giữ đoạn {can_cat[t]}")
        else:
            print(f"✔ {t}: {dai}s, liền mạch")
    (d / "kiem" / "bao-cao.json").write_text(json.dumps(bao, ensure_ascii=False, indent=2), encoding="utf-8")
    if can_cat:
        da.setdefault("cat", {}).update(can_cat)
        (d / "du-an.json").write_text(json.dumps(da, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Đã ghi đoạn cần giữ vào du-an.json (mục cat).")
    print("\nNHỚ: mở từng tờ soi trong kiem/ để xem bằng mắt (cây biến hình, chậu méo, cá bơi trên bờ…).")
    if lam_lai:
        print("CẦN TẠO LẠI: " + ", ".join(lam_lai))
    sys.exit(1 if lam_lai else 0)


if __name__ == "__main__":
    main()

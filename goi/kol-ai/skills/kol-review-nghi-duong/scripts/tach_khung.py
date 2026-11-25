"""Tờ khung 1 hình/giây có mốc giờ để soi; đưa 2 video thì đặt cạnh nhau theo cùng giây.

  tach_khung.py <video> [<video mẫu>] --out <thư mục>  [--fps 1] [--rong 216]
Ra: <out>/to_NN.jpg (mỗi tờ 6 giây × 1 hoặc 2 hàng) và <out>/cat.json (điểm cắt cảnh dò được).
"""
import argparse, json, re, subprocess
from pathlib import Path
import cv2, numpy as np
from chung import khung_tai, do_dai, ghi_anh_cv

def diem_cat(p, nguong=0.25):
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-vf", f"select='gt(scene,{nguong})',showinfo",
                        "-f", "null", "-"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    return [round(float(x), 2) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]

def o(p, g, rong):
    k = khung_tai(p, g, rong)
    hh = int(rong * 16 / 9)
    k = np.zeros((hh, rong, 3), np.uint8) if k is None else cv2.resize(k, (rong, hh))
    cv2.rectangle(k, (0, 0), (rong, 26), (0, 0, 0), -1)
    cv2.putText(k, f"{g:5.1f}s", (4, 19), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (80, 230, 255), 2)
    return k

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("video"); a.add_argument("mau", nargs="?")
    a.add_argument("--out", required=True); a.add_argument("--fps", type=float, default=1); a.add_argument("--rong", type=int, default=216)
    x = a.parse_args(); out = Path(x.out); out.mkdir(parents=True, exist_ok=True)
    ds = [x.video] + ([x.mau] if x.mau else [])
    dai = max(do_dai(v) for v in ds)
    moc = list(np.arange(0.5 / x.fps, dai, 1 / x.fps))
    for i in range(0, len(moc), 6):
        hang = []
        for v in ds:
            hang.append(np.hstack([o(v, g, x.rong) if g < do_dai(v) else np.zeros((int(x.rong * 16 / 9), x.rong, 3), np.uint8) for g in moc[i:i + 6]] +
                                  [np.zeros((int(x.rong * 16 / 9), x.rong, 3), np.uint8)] * (6 - len(moc[i:i + 6]))))
        h = min(r.shape[0] for r in hang)
        ghi_anh_cv(str(out / f"to_{i // 6 + 1:02d}.jpg"), np.vstack([r[:h] for r in hang]), 88)
    cat = {Path(v).name: diem_cat(v) for v in ds}
    (out / "cat.json").write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in cat.items():
        print(k, f"{len(v)} cú cắt:", v)
    print("→", out, "(hàng trên: video mới; hàng dưới: video mẫu)" if x.mau else "")

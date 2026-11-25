"""Soi TỪNG KHUNG một clip AI để bắt lỗi áo biến hình, hình nhảy, trước khi dựng và trước khi giao.

Vì sao: video AI hay "dính AI" ở vài khung: 0,3–1,1 giây chiếc áo đang cầm tự đổi hình
(cổ lật thành mũ, vo thành cục), cuối cảnh khóa áo bung ở gấu. Soi 2 khung/giây không thấy hết.

Dùng: python soi_tung_khung.py clip.mp4 [--tu 0 --den 10] [--mau 7a1a2a] [--out-dir soi-khung]
Ra:
  <ten>-k<NN>.jpg : mỗi tờ 1 giây, ĐỦ MỌI KHUNG (24 khung, 8x3), có ghi giây từng ô. Phải mở xem hết.
  <ten>-do.csv    : từng khung: độ đổi so với khung trước, diện tích vùng màu áo, tâm vùng áo.
  In danh sách khung NGHI: hình nhảy (độ đổi > 3,5 lần trung vị) hoặc vùng áo co giãn đột ngột (> 12% trong 1 khung).
--mau: màu áo dạng hex (lấy bằng mắt từ ảnh gốc); bỏ trống thì chỉ đo độ đổi hình.
"""
import argparse
import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def doc_khung(clip, tu, den, w=240):
    info = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=width,height,r_frame_rate",
                           "-of", "csv=p=0", clip], capture_output=True, text=True, timeout=60).stdout.strip().split(",")
    W, H = int(info[0]), int(info[1])
    a, b = info[2].split("/")
    fps = float(a) / float(b)
    h = round(H * w / W)
    lenh = ["ffmpeg", "-v", "error", "-ss", str(tu)]
    if den:
        lenh += ["-t", str(den - tu)]
    lenh += ["-i", clip, "-vf", f"scale={w}:{h}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    raw = subprocess.run(lenh, capture_output=True, timeout=300).stdout
    n = len(raw) // (w * h * 3)
    return fps, np.frombuffer(raw[: n * w * h * 3], np.uint8).reshape(n, h, w, 3)


def mat_na_mau(k, mau, sai=38):
    r, g, b = int(mau[0:2], 16), int(mau[2:4], 16), int(mau[4:6], 16)
    d = np.abs(k.astype(int) - np.array([r, g, b])).sum(axis=2)
    return d < sai * 3


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("--tu", type=float, default=0.0)
    ap.add_argument("--den", type=float, default=0.0)
    ap.add_argument("--mau", default="")
    ap.add_argument("--out-dir", default="soi-khung")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    ten = Path(a.clip).stem
    fps, ks = doc_khung(a.clip, a.tu, a.den)
    n, h, w, _ = ks.shape
    doi = [0.0] + [float(np.abs(ks[i].astype(int) - ks[i - 1].astype(int)).mean()) for i in range(1, n)]
    dt, tam = [], []
    for k in ks:
        if a.mau:
            m = mat_na_mau(k, a.mau)
            dt.append(float(m.mean()))
            ys, xs = np.nonzero(m)
            tam.append((float(xs.mean() / w) if len(xs) else -1, float(ys.mean() / h) if len(ys) else -1))
        else:
            dt.append(0.0)
            tam.append((-1, -1))
    tv = float(np.median(doi[1:])) if n > 1 else 1.0
    nghi = []
    with open(out / f"{ten}-do.csv", "w", newline="", encoding="utf-8") as f:
        wr = csv.writer(f)
        wr.writerow(["giay", "do_doi", "dien_tich_ao", "tam_x", "tam_y", "nghi"])
        for i in range(n):
            t = a.tu + i / fps
            ly = []
            if i and doi[i] > 3.5 * max(tv, 0.5):
                ly.append("hình nhảy")
            if a.mau and i and dt[i - 1] > 0.02 and abs(dt[i] - dt[i - 1]) / dt[i - 1] > 0.12:
                ly.append("vùng áo co giãn đột ngột")
            if ly:
                nghi.append((t, ", ".join(ly)))
            wr.writerow([f"{t:.3f}", f"{doi[i]:.2f}", f"{dt[i]:.4f}", f"{tam[i][0]:.3f}", f"{tam[i][1]:.3f}", "; ".join(ly)])
    # tờ xem: mỗi giây một tờ, đủ mọi khung
    moi = int(round(fps))
    cot = 8
    for s in range(0, n, moi):
        nhom = ks[s:s + moi]
        hang = (len(nhom) + cot - 1) // cot
        to = Image.new("RGB", (w * cot, h * hang), "black")
        ve = ImageDraw.Draw(to)
        for j, k in enumerate(nhom):
            x, y = (j % cot) * w, (j // cot) * h
            to.paste(Image.fromarray(k), (x, y))
            t = a.tu + (s + j) / fps
            mau_chu = "red" if any(abs(t - tn) < 0.5 / fps for tn, _ in nghi) else "yellow"
            ve.rectangle([x, y, x + 52, y + 14], fill="black")
            ve.text((x + 2, y + 1), f"{t:.2f}", fill=mau_chu)
        to.save(out / f"{ten}-k{s // moi:02d}.jpg", quality=88)
    print(f"{ten}: {n} khung, {fps:.0f} khung/giây, độ đổi trung vị {tv:.2f}. Tờ xem: {out}/{ten}-kNN.jpg (giây đỏ = nghi)")
    if nghi:
        print("KHUNG NGHI (phải mở tờ xem kiểm bằng mắt):")
        for t, ly in nghi:
            print(f"  {t:.2f} giây: {ly}")
    else:
        print("Máy không thấy khung nghi. Vẫn phải xem hết các tờ bằng mắt: máy không thấy áo đổi kiểu, khóa bung, ngón tay.")


if __name__ == "__main__":
    main()

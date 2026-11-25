"""Tìm khoảng ngắt hơi quanh một cụm nói lặp để đặt điểm cắt, ngưỡng tính theo độ to của chính clip.

Vì sao: mỗi clip Muse to nhỏ khác nhau. Ngưỡng cố định (−31 hay −33 dB) có lúc làm cả đoạn
bị coi là "ngắt" (clip nhỏ, giọng chỉ −40 dB), có lúc không thấy khoảng nào (clip to).
Script đo mức giọng của cả clip (bách phân vị 80 của các khung 20 ms) rồi coi khung nào
thấp hơn mức đó từ 18 dB trở lên là ngắt.

Dùng: python tim_khoang_ngat.py canh.mp4 --tu 18.3 --den 18.9 [--tu 20.4 --den 20.9 ...] [--duoi 18]
In: mức giọng của clip, ngưỡng, các khoảng ngắt trong từng vùng và điểm giữa để đặt điểm cắt.
Cách cắt cụm lặp: đặt điểm cắt ở khoảng ngắt NGAY TRƯỚC lần nói đầu và NGAY TRƯỚC lần nói lại,
bỏ phần giữa. Sau khi dựng, chạy so_loi.py trên thành phẩm để chắc không mất chữ.
"""
import argparse
import subprocess
import sys

import numpy as np

SR = 16000
KHUNG = 320  # 20 ms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video")
    ap.add_argument("--tu", type=float, action="append", required=True)
    ap.add_argument("--den", type=float, action="append", required=True)
    ap.add_argument("--duoi", type=float, default=18.0, help="ngắt = thấp hơn mức giọng bao nhiêu dB")
    a = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", a.video, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    n = len(x) // KHUNG
    db = 20 * np.log10(np.sqrt((x[:n * KHUNG].reshape(n, KHUNG) ** 2).mean(1)) + 1e-6)
    giong = float(np.percentile(db, 80))
    nguong = giong - a.duoi
    print(f"Mức giọng của clip {giong:.0f} dB, ngưỡng ngắt {nguong:.0f} dB")
    for tu, den in zip(a.tu, a.den):
        i0, i1 = int(tu * SR / KHUNG), min(n, int(den * SR / KHUNG))
        o, dang = [], None
        for i in range(i0, i1):
            t = i * KHUNG / SR
            if db[i] < nguong and dang is None:
                dang = t
            elif db[i] >= nguong and dang is not None:
                o.append((dang, t))
                dang = None
        if dang is not None:
            o.append((dang, i1 * KHUNG / SR))
        o = [(s, e) for s, e in o if e - s >= 0.04]
        print(f"\nVùng {tu:.2f}–{den:.2f}:")
        for s, e in o:
            print(f"  ngắt {s:.2f}–{e:.2f}, cắt ở {(s + e) / 2:.2f}")
        if not o:
            print("  Không có khoảng ngắt. Nới vùng ra 0,3 giây hoặc giảm --duoi xuống 14.")


if __name__ == "__main__":
    main()

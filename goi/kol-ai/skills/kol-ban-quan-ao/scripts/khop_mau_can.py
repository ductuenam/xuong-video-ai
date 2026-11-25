"""Khớp màu áo của cảnh cận theo cảnh nói.

Muse vẽ cảnh cận (nhất là cảnh thân người xoay) với tông màu khác cảnh nói: ở một video áo dạ đã làm,
áo nâu xám thành vàng ô liu, người soát nói "như một chiếc áo khác", màu nhảy ở cả hai chỗ nối.
Script lấy trung bình và độ lệch kênh màu a, b (LAB) của vùng áo ở cảnh nói, chuyển kênh a, b
của cảnh cận về đó, độ sáng chỉ dịch nhẹ (--sang) và giữ nguyên độ tương phản. Chuyển cả
kênh sáng theo độ lệch sẽ làm hình bạc và mờ.

Dùng:
python khop_mau_can.py --mau s2.mp4@7.0:0.30,0.45,0.42,0.62 \
    --can c3.mp4@1.0:0.25,0.20,0.75,0.55 --ra c3-mau.mp4 [--tu 0 --den 4] [--sang -14]
- @giây:x0,y0,x1,y1 là khung lấy mẫu và vùng áo (tỉ lệ khung), chỉ lấy vải áo, tránh áo thun và da.
- Cảnh ra bắt đầu từ --tu, nên trong ke-hoach.json phải trừ đi --tu.
- Script lưu ảnh so sánh <ra>-so.jpg (cảnh nói | cảnh cận đã chỉnh). Mở xem trước khi dựng.
"""
import argparse
import sys
import subprocess

import cv2
import numpy as np


def doc(spec):
    f, rest = spec.split("@")
    t, box = rest.split(":")
    return f, float(t), [float(v) for v in box.split(",")]


def khung(f, t):
    c = cv2.VideoCapture(f)
    c.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
    ok, x = c.read()
    if not ok:
        raise SystemExit(f"Không đọc được {f} ở {t}s")
    return x


def tk(img, box):
    h, w = img.shape[:2]
    x0, y0, x1, y1 = box
    p = cv2.cvtColor(img, cv2.COLOR_BGR2LAB).astype(float)[int(h * y0):int(h * y1), int(w * x0):int(w * x1)]
    p = p.reshape(-1, 3)
    return p.mean(0), p.std(0)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mau", required=True)
    ap.add_argument("--can", required=True)
    ap.add_argument("--ra", required=True)
    ap.add_argument("--tu", type=float, default=0.0)
    ap.add_argument("--den", type=float, default=10.0)
    ap.add_argument("--sang", type=float, default=0.0, help="dịch độ sáng L (âm là tối đi)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    fm, tm_, bm = doc(a.mau)
    fc, tc, bc = doc(a.can)
    ref = khung(fm, tm_)
    tm, ts = tk(ref, bm)
    sm, ss = tk(khung(fc, tc), bc)
    print("Cảnh nói L,a,b:", np.round(tm, 1), " Cảnh cận:", np.round(sm, 1))
    c = cv2.VideoCapture(fc)
    fps = c.get(cv2.CAP_PROP_FPS)
    w, h = int(c.get(3)), int(c.get(4))
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{w}x{h}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", a.ra],
                         stdin=subprocess.PIPE)
    c.set(cv2.CAP_PROP_POS_MSEC, a.tu * 1000)
    mau_ra = None
    while c.get(cv2.CAP_PROP_POS_MSEC) <= a.den * 1000 + 1:
        ok, f = c.read()
        if not ok:
            break
        L = cv2.cvtColor(f, cv2.COLOR_BGR2LAB).astype(float)
        L[..., 0] += a.sang
        for k in (1, 2):
            L[..., k] = (L[..., k] - sm[k]) / max(ss[k], 0.5) * ts[k] + tm[k]
        o = cv2.cvtColor(np.clip(L, 0, 255).astype(np.uint8), cv2.COLOR_LAB2BGR)
        if mau_ra is None:
            mau_ra = o
        p.stdin.write(o.tobytes())
    p.stdin.close()
    p.wait()
    so = np.hstack([cv2.resize(ref, (336, 608)), cv2.resize(mau_ra, (336, 608))])
    cv2.imwrite(a.ra.rsplit(".", 1)[0] + "-so.jpg", so)
    print("Xong", a.ra)


if __name__ == "__main__":
    main()

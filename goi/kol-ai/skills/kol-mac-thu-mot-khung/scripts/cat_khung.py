"""Cắt ảnh gốc toàn thân thành goc-toan.png và goc-khung.png (khung cảnh nói: từ trên đỉnh đầu xuống giữa đùi).

Dùng: python cat_khung.py <thư mục video> [--kx 0.19] [--kh 0.68]
- Ảnh vào: anh-goc.png (Muse ra khoảng 1152x2048), đưa về 720x1280 (goc-toan.png).
- goc-khung.png: vùng (kx, 0, kh, kh) của goc-toan, phóng lên 720x1280. kx = mép trái khung (tỉ lệ),
  mặc định căn giữa người: kx = tâm người − kh/2. kh = 0.68 cho khung tới giữa đùi (0,62 chỉ tới mép quần short, AK01) như video mẫu.
- Ghi kx, kh vào video.json (cổng khóa mặt cần) và lưu xem-khung.jpg: ảnh toàn thân có vẽ khung để soát.
Soát: khung phải có khoảng trống trên đầu, cắt ở giữa đùi (không thấy đầu gối), người ở giữa.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def tam_nguoi(im):
    """Đoán tâm ngang của người: cột có độ lệch màu so với nền lớn nhất ở dải 15–55% chiều cao."""
    a = np.asarray(im.convert("L")).astype(float)
    h = a.shape[0]
    dai = a[int(h * 0.15):int(h * 0.55)]
    nen = np.median(dai, axis=1, keepdims=True)
    lech = np.abs(dai - nen).mean(axis=0)
    lech = np.convolve(lech, np.ones(31) / 31, mode="same")
    w = a.shape[1]
    trong = lech[int(w * 0.2):int(w * 0.8)]
    return (int(w * 0.2) + int(np.argmax(trong))) / w


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("--kx", type=float)
    ap.add_argument("--kh", type=float, default=0.68)
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    d = Path(a.thu_muc)
    im = Image.open(d / "anh-goc.png").convert("RGB")
    W, H = im.size
    im = im.resize((720, round(H * 720 / W)), Image.LANCZOS)
    dh = im.size[1] - 1280
    im = im.crop((0, max(dh // 2, 0), 720, max(dh // 2, 0) + 1280))
    im.save(d / "goc-toan.png")
    kx = a.kx if a.kx is not None else round(min(max(tam_nguoi(im) - a.kh / 2, 0), 1 - a.kh), 3)
    box = (round(kx * 720), 0, round((kx + a.kh) * 720), round(a.kh * 1280))
    im.crop(box).resize((720, 1280), Image.LANCZOS).save(d / "goc-khung.png")
    xem = im.copy()
    ImageDraw.Draw(xem).rectangle(box, outline=(255, 0, 0), width=4)
    xem.save(d / "xem-khung.jpg", quality=88)
    fv = d / "video.json"
    v = json.loads(fv.read_text(encoding="utf-8")) if fv.is_file() else {}
    v["kx"], v["kh"] = kx, a.kh
    fv.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Đã ghi goc-toan.png, goc-khung.png (kx={kx}, kh={a.kh}). MỞ xem-khung.jpg để soát khung.")


if __name__ == "__main__":
    main()

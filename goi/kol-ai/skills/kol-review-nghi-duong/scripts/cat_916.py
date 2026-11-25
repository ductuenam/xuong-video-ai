"""Đưa ảnh chủ khu gửi về khung dọc 9:16 (1152×2048) để làm bối cảnh cho Muse và ô ảnh góc.

  cat_916.py <ảnh vào> <ảnh ra> [--tam 0.5,0.5]
Ảnh ngang: cắt giữa theo --tam (tỉ lệ x,y của điểm cần giữ). Ảnh quá nhỏ (< 900 px cạnh ngắn) thì báo để xin ảnh to hơn.
"""
import argparse
from PIL import Image

if __name__ == "__main__":
    a = argparse.ArgumentParser(); a.add_argument("vao"); a.add_argument("ra"); a.add_argument("--tam", default="0.5,0.5")
    x = a.parse_args(); cx, cy = map(float, x.tam.split(","))
    im = Image.open(x.vao).convert("RGB")
    if min(im.size) < 900:
        print(f"! Ảnh nhỏ {im.size}: nên xin chủ khu ảnh gốc to hơn (gửi file, không gửi qua ảnh nén).")
    W, H = 1152, 2048; s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    x0 = int(min(max(0, im.width * cx - W / 2), im.width - W)); y0 = int(min(max(0, im.height * cy - H / 2), im.height - H))
    im.crop((x0, y0, x0 + W, y0 + H)).save(x.ra); print("→", x.ra)

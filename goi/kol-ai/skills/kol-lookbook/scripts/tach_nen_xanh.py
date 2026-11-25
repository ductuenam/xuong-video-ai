"""Tách nền xanh lá (#00FF00) của ảnh sản phẩm thành PNG trong suốt, để đặt ở góc video lookbook.

Vì sao: máy không có rembg; tạo ảnh hàng thật (ma-nơ-canh mặc đúng bộ) trên Muse với nền xanh lá thuần
rồi tách bằng khoảng cách màu là cách nhẹ nhất, viền sạch hơn tách nền trắng (quần áo trắng sẽ bị ăn mất).

Dùng: python tach_nen_xanh.py vao.png ra.png [--nguong 120] [--mem 40]
"""
import argparse
import numpy as np
from PIL import Image, ImageFilter

ap = argparse.ArgumentParser(); ap.add_argument("vao"); ap.add_argument("ra")
ap.add_argument("--nguong", type=float, default=120); ap.add_argument("--mem", type=float, default=40)
a = ap.parse_args()
im = np.asarray(Image.open(a.vao).convert("RGB")).astype(float)
r, g, b = im[..., 0], im[..., 1], im[..., 2]
xanh = g - np.maximum(r, b)                     # độ "xanh lá" của điểm ảnh
alpha = np.clip((a.nguong - xanh) / a.mem, 0, 1)  # càng xanh càng trong suốt
# khử viền xanh: kéo kênh G xuống không vượt max(R,B) ở vùng bán trong suốt
g2 = np.where(xanh > 0, np.maximum(r, b), g)
out = np.dstack([r, g2, b, alpha * 255]).astype(np.uint8)
o = Image.fromarray(out)
al = o.getchannel("A").filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8)); o.putalpha(al)
o = o.crop(o.getbbox()); o.save(a.ra)
print("Xong", a.ra, o.size)

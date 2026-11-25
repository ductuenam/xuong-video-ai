"""Cắt ảnh gốc toàn thân thành goc-toan, goc-tren và các ảnh cận 720x1280.
Dùng: python cat_anh.py thu_muc anh_goc.png kx_tren can1=x,y,w can2=x,y,w
x,y,w theo tỉ lệ khung 720x1280; chiều cao tự tính theo 9:16."""
import sys
from pathlib import Path
from PIL import Image

d = Path(sys.argv[1])
im = Image.open(d / sys.argv[2]).convert("RGB")
W, H = im.size
# đưa về 720x1280: phóng theo chiều rộng rồi cắt giữa theo chiều cao
s = 720 / W
im = im.resize((720, round(H * s)), Image.LANCZOS)
dh = im.size[1] - 1280
im = im.crop((0, dh // 2, 720, dh // 2 + 1280))
im.save(d / "goc-toan.png")
kx = float(sys.argv[3])
w = 0.70
im.crop((round(kx * 720), 0, round((kx + w) * 720), round(0.70 * 1280))).resize((720, 1280), Image.LANCZOS).save(d / "goc-tren.png")
for a in sys.argv[4:]:
    ten, v = a.split("=")
    x, y, w = [float(t) for t in v.split(",")]
    box = (round(x * 720), round(y * 1280), round((x + w) * 720), round((y + w) * 1280))
    im.crop(box).resize((720, 1280), Image.LANCZOS).save(d / f"{ten}.png")
print("ok", f"--khung {kx},0,{w if False else 0.70},0.70")

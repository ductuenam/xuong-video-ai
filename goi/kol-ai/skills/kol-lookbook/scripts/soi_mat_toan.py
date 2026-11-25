"""Phóng to vùng mặt trong khúc toàn thân/máy tiến để thấy mắt nhắm hay mở (mặt quá nhỏ ở tờ soi thường).
Dùng: python soi_mat_toan.py clip.mp4 tu den ra.jpg"""
import subprocess, sys
from PIL import Image, ImageDraw
c, tu, den, ra = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), sys.argv[4]
o = []; t = tu
while t < den:
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{t:.3f}', '-i', c, '-frames:v', '1', '_z.png'], timeout=60)
    im = Image.open('_z.png').convert('RGB'); W, H = im.size
    cy = int(H * (0.12 + 0.06 * t)); im = im.crop((W // 2 - 90, max(0, cy - 60), W // 2 + 90, max(0, cy - 60) + 150)).resize((180, 150))
    ImageDraw.Draw(im).text((3, 3), f'{t:.2f}', fill=(255, 255, 0)); o.append(im); t += 1 / 12
S = Image.new('RGB', (180 * 12, 150 * ((len(o) + 11) // 12)))
for i, im in enumerate(o): S.paste(im, ((i % 12) * 180, (i // 12) * 150))
S.save(ra)

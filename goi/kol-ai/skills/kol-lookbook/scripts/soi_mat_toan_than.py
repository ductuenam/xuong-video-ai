# Tờ mắt cảnh toàn thân: dò đỉnh đầu từng khung rồi cắt ô vuông quanh mặt. Dùng: soi_mat_toan_than.py ra.jpg clip:tu:den ...
import subprocess, sys, os, tempfile
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chung import cau_hinh
TAMD = cau_hinh()['thu_muc_tam']; os.makedirs(TAMD, exist_ok=True)
ra = sys.argv[1]; hang = []
for spec in sys.argv[2:]:
    clip, tu, den = spec.rsplit(":", 2); tu, den = float(tu), float(den); o = []; t = tu
    with tempfile.TemporaryDirectory(dir=TAMD) as d:
        while t < den - 1e-6:
            p = os.path.join(d, "k.png"); subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", clip, "-frames:v", "1", p], timeout=60)
            with Image.open(p) as _im: im = _im.convert("RGB"); W, H = im.size; g = im.convert("L"); nen = g.getpixel((5, 5)); top = 0
            for y in range(0, H, 4):
                if sum(abs(g.getpixel((x, y)) - nen) > 45 for x in range(W//4, 3*W//4, 4)) > 4: top = y; break
            # bề rộng tóc ở hàng top+60 ước cỡ đầu
            yy = min(H-1, top + 40); xs = [x for x in range(0, W, 2) if abs(g.getpixel((x, yy)) - nen) > 45]
            s = max(60, int(((xs[-1] - xs[0]) if xs else 120) * 1.0)); cx = (xs[0] + xs[-1]) // 2 if xs else W // 2
            c = im.crop((cx - s//2, top + int(s*0.55), cx + s//2, top + int(s*0.55) + s//2)).resize((200, 100))
            ImageDraw.Draw(c).text((2, 2), f"{t:.2f}", fill="yellow"); o.append(c); t += 1/12
    r = Image.new("RGB", (200*len(o), 100))
    for j, c in enumerate(o): r.paste(c, (200*j, 0))
    ImageDraw.Draw(r).text((2, 88), spec, fill="red"); hang.append(r)
S = Image.new("RGB", (max(x.width for x in hang), 100*len(hang)))
for i, x in enumerate(hang): S.paste(x, (0, 100*i))
S.save(ra, quality=88)

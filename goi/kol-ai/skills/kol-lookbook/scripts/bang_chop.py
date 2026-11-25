# Tờ chớp mắt: mỗi clip một khối, mỗi ô một khung (12 khung/giây, nhãn = giây thật trong clip). Dùng: bang_chop.py ra.jpg clip:tu:den:y0:y1 ...
# Máy tiến làm mắt trượt xuống dần: khúc dài thì tách nhiều đoạn ngắn với y0:y1 riêng (mở tờ, thấy mắt ra khỏi ô là chỉnh).
import subprocess, sys, tempfile, glob, os
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from chung import cau_hinh
TAMD = cau_hinh()['thu_muc_tam']; os.makedirs(TAMD, exist_ok=True)
ra = sys.argv[1]; hang = []
for spec in sys.argv[2:]:
    clip, tu, den, y0, y1 = spec.rsplit(":", 4); tu, den, y0, y1 = map(float, (tu, den, y0, y1))
    tiles = []; t = tu
    with tempfile.TemporaryDirectory(dir=TAMD) as d:
        while t < den - 1e-6:
            p = os.path.join(d, f"{t:.3f}.png")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", clip, "-frames:v", "1", p], timeout=60)
            with Image.open(p) as _im: im = _im.convert("RGB"); w, h = im.size
            c = im.crop((int(w*0.15), int(h*y0), int(w*0.85), int(h*y1))).resize((240, int(240*(h*(y1-y0))/(w*0.7))))
            ImageDraw.Draw(c).text((2, 2), f"{t:.2f}", fill="yellow"); tiles.append(c); t += 1/12
    th = tiles[0].height; cot = 8; r = Image.new("RGB", (244*cot, (th+4)*((len(tiles)+cot-1)//cot)))
    for j, c in enumerate(tiles): r.paste(c, ((j % cot)*244, (j//cot)*(th+4)))  # ô 240 px cách 244: không đè nhau (bản cũ cách 150 làm mất nửa ô)
    ImageDraw.Draw(r).text((2, r.height-12), clip, fill="red"); hang.append(r)
S = Image.new("RGB", (max(x.width for x in hang), sum(x.height for x in hang))); y = 0
for x in hang: S.paste(x, (0, y)); y += x.height
S.save(ra, quality=85)

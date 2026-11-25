"""Tờ so mặt các ảnh toàn thân trước khi gửi Muse: hàng trên mặt phóng to, hàng dưới toàn thân.
Dùng: python so_mat_anh.py ra.jpg anh1.png anh2.png ...   (ảnh đầu nên là ảnh mặt chuẩn đã đạt)
Vì sao: video mẫu 2 mặt các bộ lệch nhau (tròn/bè/cằm V) chỉ lộ ra khi đặt cạnh nhau; soát ở bước ảnh rẻ hơn soát sau Muse."""
import sys
from PIL import Image, ImageDraw
ra = sys.argv[1]; anh = sys.argv[2:]
S = Image.new("RGB", (300 * len(anh), 300 + 520), "black")
for i, p in enumerate(anh):
    im = Image.open(p).convert("RGB"); W, H = im.size
    t = im.copy(); t.thumbnail((300, 520)); S.paste(t, (i * 300, 300))
    g = im.convert("L").resize((W // 8, H // 8)); w8, h8 = g.size; nen = g.getpixel((2, 2)); top = 0
    for y in range(h8):  # đỉnh đầu = hàng đầu tiên khác màu nền
        if sum(abs(g.getpixel((x, y)) - nen) > 40 for x in range(w8)) > 3: top = y * 8; break
    s = int(W * 0.30); cx = W // 2
    c = im.crop((cx - s // 2, top + int(s * 0.15), cx + s // 2, top + int(s * 1.15))).resize((300, 300))
    ImageDraw.Draw(c).text((4, 4), p[-28:], fill=(255, 255, 0)); S.paste(c, (i * 300, 0))
S.save(ra, quality=90)
print("Xong", ra)

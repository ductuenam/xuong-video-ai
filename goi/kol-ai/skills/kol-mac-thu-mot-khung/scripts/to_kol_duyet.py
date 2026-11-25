"""Ghép tờ KOL cho người dùng duyệt TRƯỚC khi tạo clip: mặt chuẩn | mặt ảnh gốc (to) | ảnh gốc toàn thân | khung cảnh nói | ảnh nhà bán, kèm hàng chân.

Dùng: python to_kol_duyet.py <thư mục video> [anh-goc.png] [anh-goc-2.png ...]
Nhiều ảnh gốc (2 ảnh Muse ra) thì mỗi ảnh một hàng để người dùng chọn. Ra: to-kol-duyet.jpg (giữ đúng tỉ lệ, không bóp).
Cần video.json có kx, kh (cat_khung.py) cho ảnh đầu; ảnh sau dùng cùng kx.
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, thu_muc  # noqa: E402
from khoa_mat import cat, o_chan_toan, o_mat_toan, ve_goc_toan  # noqa: E402

CAO = 560


def nhan(im, chu):
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 10 + 8 * len(chu), 22), fill=(0, 0, 0))
    d.text((5, 5), chu, fill=(255, 230, 0))
    return im


def hang(ims):
    ims = [i.resize((round(i.width * CAO / i.height), CAO), Image.LANCZOS) for i in ims]
    t = Image.new("RGB", (sum(i.width for i in ims) + 6 * (len(ims) - 1), CAO), (30, 30, 30))
    x = 0
    for i in ims:
        t.paste(i, (x, 0))
        x += i.width + 6
    return t


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    d = Path(sys.argv[1])
    goc = sys.argv[2:] or ["anh-goc.png"]
    v = json.loads((d / "video.json").read_text(encoding="utf-8"))
    kx, kh = float(v.get("kx", 0.19)), float(v.get("kh", 0.68))
    dk = thu_muc(doc_cau_hinh(), "thu_muc_kol")
    mc = Image.open(dk / "mat-chuan.png").convert("RGB")
    cc = Image.open(dk / "chan-chuan.png").convert("RGB")
    shop = [Image.open(d / p).convert("RGB") for p in v.get("anh_nha_ban", [])[:2]]
    hs = []
    for i, ten in enumerate(goc):
        g = ve_goc_toan(Image.open(d / ten))
        k = g.crop((round(kx * 720), 0, round((kx + kh) * 720), round(kh * 1280)))
        hs.append(hang([nhan(mc.copy(), "MAT CHUAN (anh duyet 23/11)"), nhan(cat(g, o_mat_toan(kx), 400), f"MAT {ten}"),
                        nhan(g.copy(), f"TOAN THAN {ten}"), nhan(k, "KHUNG CANH NOI"),
                        nhan(cc.copy(), "CHAN CHUAN"), nhan(cat(g, o_chan_toan(kx), 300), "CHAN")] +
                       ([nhan(s.copy(), "NHA BAN") for s in shop] if i == 0 else [])))
    W = max(h.width for h in hs)
    t = Image.new("RGB", (W, sum(h.height for h in hs) + 8 * len(hs)), (15, 15, 15))
    y = 0
    for h in hs:
        t.paste(h, (0, y))
        y += h.height + 8
    t.save(d / "to-kol-duyet.jpg", quality=90)
    print("Đã ghi", d / "to-kol-duyet.jpg")


if __name__ == "__main__":
    main()

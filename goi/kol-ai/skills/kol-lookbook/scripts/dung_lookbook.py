"""Dựng video lookbook: nối cảnh theo phách (dung_theo_nhip.py), chèn ảnh sản phẩm thật ở góc dưới phải theo từng bộ,
chữ thương hiệu giữa trên, rồi hậu kỳ quay điện thoại (quay_dien_thoai.py).

Vì sao: kiểu lookbook của các shop thời trang lớn đặt ảnh hàng thật đã tách nền ở góc, đổi theo từng bộ,
và chữ thương hiệu trắng mảnh giữa trên suốt video.

Dùng: python dung_lookbook.py ke-hoach.json   (dừng nếu cổng khóa mặt khoa_mat.py chưa qua)
ke-hoach.json = như dung_theo_nhip.py, thêm:
  mỗi đoạn có "bo": 1|2|3
  "anh_goc": {"1": "bo1/san-pham-tach-nen.png", ...}   PNG có kênh trong suốt
  "chu": "TÊN SHOP"   (bỏ trống thì không ghi chữ)
  "ra": "ten-video.mp4"
Ảnh góc cao 36% khung (42% đè cổ áo, video mẫu 1), sát mép phải, cách đáy 3%. Chữ vẽ bằng PIL (drawtext của ffmpeg lỗi font trên máy này).
"""
import json, subprocess, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

TH = Path(__file__).parent


def chay(l, han=900):
    r = subprocess.run(l, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=han)
    if r.returncode: sys.exit(r.stderr[-1500:])
    return r.stdout


def main():
    if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
    kp = Path(sys.argv[1]); goc = kp.parent; kh = json.loads(kp.read_text(encoding="utf-8"))
    # CỔNG KHÓA MẶT: ảnh gốc mọi bộ và MỌI clip trong kế hoạch phải được chấm đạt (mặt, chân, áo) mới được dựng.
    sys.path.insert(0, str(TH)); import khoa_mat
    khoa_mat.in_utf8()
    khoa_mat.cong(goc, "anh")
    khoa_mat.cong(goc, "clip", ds_clip=sorted({Path(x["clip"]).as_posix() for x in kh.get("doan", [])}))
    ra = kh["ra"]; tho = "_tho-" + ra
    kh2 = dict(kh); kh2["ra"] = tho
    k2 = goc / ("_kh-" + kp.name); k2.write_text(json.dumps(kh2, ensure_ascii=False, indent=1), encoding="utf-8")
    print(chay([sys.executable, "-X", "utf8", str(TH / "dung_theo_nhip.py"), str(k2)]))
    moc = json.loads((goc / (tho + ".moc.json")).read_text(encoding="utf-8"))
    try:  # tệp mốc tạm: dời vào thu_muc_tam cho thư mục video gọn (bản cũ bắt người dựng dời tay)
        from chung import cau_hinh
        _t = Path(cau_hinh()["thu_muc_tam"]); _t.mkdir(parents=True, exist_ok=True)
        (goc / (tho + ".moc.json")).replace(_t / (tho + ".moc.json"))
    except Exception:
        pass
    # khoảng thời gian từng bộ
    bo = {}
    for m in moc:
        b = str(m.get("bo") or "")
        if not b: continue
        a, z = bo.get(b, (m["tu"], m["den"])); bo[b] = (min(a, m["tu"]), max(z, m["den"]))
    if bo:  # bộ cuối kéo tới hết video (mốc làm tròn khung có thể hụt vài khung)
        bc = max(bo, key=lambda x: bo[x][1]); bo[bc] = (bo[bc][0], 9999)
    # lớp phủ: chữ + từng ảnh góc
    lop = [goc / "_lop-chu.png"]
    o = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    if kh.get("chu"):
        d = ImageDraw.Draw(o)
        try: f = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", 52)
        except Exception: f = ImageFont.load_default()
        t = " ".join(kh["chu"].upper())
        w = d.textlength(t, font=f); d.text(((1080 - w) / 2, 70), t, font=f, fill=(255, 255, 255, 235))
    o.save(lop[0])
    vao = ["-i", str(goc / tho), "-loop", "1", "-i", str(lop[0])]
    loc = "[0:v][1:v]overlay=0:0:shortest=1[v0]"; cu = "v0"; n = 2
    fps = kh.get("fps", 24)
    cao_chung = kh.get("goc_cao", 0.36)
    # Từng khúc ảnh góc: mặc định một khúc mỗi bộ. Đoạn nào có "goc_cao" riêng (cảnh trung/cận cho ảnh góc nhỏ lại
    # để không đè áo; video mẫu 2 agent trang phục bắt ma-nơ-canh lạc đà đè vạt măng tô cùng màu ở cận) thì tách khúc theo đoạn.
    # "goc_vi_tri": "tren" (góc trên phải) cho đoạn mà góc dưới che giày/tay/túi (video mẫu 2: cảnh chân bộ 2 che giày).
    khuc = []  # (bo, khung_tu, khung_den, cao, vi_tri)
    doan = kh.get("doan", [])
    if any(("goc_cao" in d or "goc_vi_tri" in d) for d in doan) and len(doan) == len(moc):
        for d, m in zip(doan, moc):
            b = str(m.get("bo") or "")
            if not b: continue
            c = d.get("goc_cao", cao_chung); vt = d.get("goc_vi_tri", "duoi")
            if khuc and khuc[-1][0] == b and khuc[-1][3] == c and khuc[-1][4] == vt and khuc[-1][2] == m["khung_tu"]:
                khuc[-1] = (b, khuc[-1][1], m["khung_den"], c, vt)
            else:
                khuc.append((b, m["khung_tu"], m["khung_den"], c, vt))
        if khuc: khuc[-1] = (khuc[-1][0], khuc[-1][1], 10 ** 7, khuc[-1][3], khuc[-1][4])  # khúc cuối kéo tới hết video
    else:
        for b, (a, z) in sorted(bo.items()):
            khuc.append((b, round(a * fps), round(z * fps), cao_chung, "duoi"))  # so theo số khung, tránh đổi ảnh lệch cú cắt
    for i, (b, fa, fz, cao, vt) in enumerate(khuc):
        p = kh.get("anh_goc", {}).get(b)
        if not p: continue
        im = Image.open(goc / p).convert("RGBA"); im = im.crop(im.getbbox())
        h = int(1920 * cao); w = int(im.width * h / im.height); im = im.resize((w, h), Image.LANCZOS)
        nen = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
        # lề phải 40 px: video mẫu 2 tay áo ma-nơ-canh bộ 5 chạm mép khung bị cắt
        x0, y0 = 1080 - w - 40, (int(1920 * 0.06) if vt == "tren" else 1920 - h - int(1920 * 0.03))
        # KHÔNG thêm quầng sáng/bóng quanh ma-nơ-canh: video mẫu 1 thử quầng sáng, người chấm thấy thành khối mờ đè lên tóc
        nen.paste(im, (x0, y0), im)
        pp = goc / f"_lop-k{i:02d}.png"; nen.save(pp)
        vao += ["-loop", "1", "-i", str(pp)]
        loc += f";[{cu}][{n}:v]overlay=0:0:shortest=1:enable='gte(n,{fa})*lt(n,{fz})'[v{n}]"; cu = f"v{n}"; n += 1
    tam = goc / ("_phu-" + ra)
    chay(["ffmpeg", "-v", "error", "-y", *vao, "-filter_complex", loc, "-map", f"[{cu}]", "-map", "0:a",
          "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", "-c:a", "copy", str(tam)])
    # "hat" trong kế hoạch: độ hạt hậu kỳ (mặc định 3). video mẫu 2 dùng 5: hạt 3 thì agent chấm da cận "mịn kiểu lọc".
    print(chay([sys.executable, "-X", "utf8", str(TH / "quay_dien_thoai.py"), str(tam), str(goc / ra),
                "--hat", str(kh.get("hat", 5))]))
    for p in [k2, goc / tho, tam, *goc.glob("_lop-*.png")]: Path(p).unlink(missing_ok=True)
    print("Mốc bộ:", bo)


if __name__ == "__main__":
    main()

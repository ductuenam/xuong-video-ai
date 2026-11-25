"""CỔNG KHÓA MẶT, CHÂN VÀ MẪU ÁO cho KOL thương hiệu (bản cho kol-mac-thu-mot-khung: 2 cảnh s1-noi, s2-noi; kx = mép trái khung, kh = chiều cao khung).

KOL là gương mặt của shop: sai mặt một cảnh là hỏng cả video. Cổng này đặt mặt chuẩn của KOL
cạnh mặt ở ảnh gốc và ở từng cảnh (1 khung/giây), đặt chân cạnh chân chuẩn, đặt ảnh gốc cạnh ảnh
nhà bán, rồi bắt người chấm ghi điểm từng mục vào phiếu. Thiếu phiếu, điểm dưới ngưỡng, hoặc tệp
đã đổi sau khi chấm thì các bước sau (viet_lenh.py video, dung_chen_can.py, luu_kho.py) DỪNG.

Dùng:
  python khoa_mat.py chuan <thu_muc_kol>          cắt mat-chuan.png, chan-chuan.png từ kol-chuan.png (kx_chuan trong kol.json)
  python khoa_mat.py anh   <thư mục video>        tờ so ảnh gốc: khoa-mat/to-anh.jpg (mặt, chân, áo với ảnh shopee/)
  python khoa_mat.py clip  <thư mục video>        tờ so clip: khoa-mat/to-mat.jpg, khoa-mat/to-chan.jpg
  python khoa_mat.py cham  <thư mục video> <tệp> mat=5 chan=4 ao=5 --nguoi "<ai chấm>" [--ghi "..."]
  python khoa_mat.py duyet <thư mục video> --nguoi "<tên người dùng>" [--ghi "lời duyệt"]
                                                  NGƯỜI DÙNG (chủ shop) xem tờ so mặt và duyệt; máy và agent đạt CHƯA ĐỦ
  python khoa_mat.py kiem  <thư mục video> [--buoc anh|clip|het]

Thang điểm từng mục (1–5), ngưỡng qua là 4:
  mat  5 = chắc chắn cùng một người với mặt chuẩn; 4 = cùng người, khác nhẹ do góc/biểu cảm;
       3 trở xuống = trông như người khác, mặt bè/gầy đi, đổi mắt, mũi, môi, mái, tóc → CHẶN.
  chan 5 = thon, sáng mịn đều màu như chân chuẩn, đầu gối sáng; 4 = đạt, khác nhẹ do ánh sáng;
       3 trở xuống = da sẫm/đỏ, đầu gối thâm, chân to, vết, sần → CHẶN. Chân bị che hết (váy dài,
       quần dài, quần tất đậm) thì ghi chan=0 nghĩa là "không thấy".
  ao   chỉ cho ảnh gốc: 5 = đúng mẫu nhà bán từng chi tiết (cổ, cúc, khóa, túi, tay, gấu, màu);
       3 trở xuống = sai kiểu cổ (vd cổ đứng thay cổ lá sen), thiếu/thừa chi tiết, sai màu → CHẶN.
Máy còn đo màu da chân (độ sáng L, độ đỏ a trong hệ Lab) so với chân chuẩn: sẫm hơn hoặc đỏ hơn
quá ngưỡng thì in CẢNH BÁO và mục đó phải có --ghi giải thích của người chấm mới qua.
Máy không tự nhận ra người: điểm mặt do người chấm nhìn tờ so mặt mà cho. Người chấm nên là
agent kol-livestream-soat (độc lập), không phải người vừa làm video.
BƯỚC CUỐI BẮT BUỘC: người dùng tự xem khoa-mat/to-mat.jpg (và to-anh.jpg) rồi duyệt bằng lệnh duyet.
Đã gặp: agent chấm "giống" mà chủ shop xem thì "không giống". Mặt lệch dù nhẹ (dài, gầy, mắt khác)
là tạo lại cảnh đó. Chưa có câu duyệt của người dùng thì luu_kho.py không lưu, không giao.
"""
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, in_utf8, thu_muc  # noqa: E402

NGUONG = 4
O = 220  # cạnh ô trên tờ so
CANH_MAT = ["s1-noi.mp4", "s2-noi.mp4", "s3-lung.mp4"]  # kol-mac-thu-mot-khung: 2 cảnh nói cùng một khung (đầu tới giữa đùi)
CANH_CHAN = []  # khung cắt ở giữa đùi, không thấy đầu gối: chân chỉ chấm ở ảnh gốc toàn thân
KH = 0.68  # chiều cao khung cảnh nói so với ảnh toàn thân (video.json "kh"), lay_kx() cập nhật
KHONG_MAT = ("q4",)  # cận thân trên: không có mặt, không có chân; vẫn phải qua người soát trang phục
LECH_L, LECH_A = 8.0, 6.0  # ngưỡng cảnh báo màu da chân


# ---------- vùng cắt (theo tỉ lệ khung goc-toan 720x1280; goc-tren = vùng kx,0,0.70,0.70 phóng lên) ----------
def o_mat_toan(kx):
    cx = kx + 0.35
    return (cx - 0.11, 0.06, cx + 0.11, 0.22)


def o_chan_toan(kx):
    cx = kx + 0.35
    return (cx - 0.17, 0.60, cx + 0.17, 0.985)


def sang_tren(o, kx):
    """Đổi ô từ khung toàn thân sang khung cảnh nói (vùng kx,0,KH,KH của ảnh toàn thân phóng lên)."""
    x0, y0, x1, y1 = o
    return ((x0 - kx) / KH, y0 / KH, (x1 - kx) / KH, y1 / KH)


def ve_goc_toan(im):
    """Đưa ảnh gốc bất kỳ về khung goc-toan 720x1280 giống cat_anh.py."""
    W, H = im.size
    im = im.convert("RGB").resize((720, round(H * 720 / W)), Image.LANCZOS)
    dh = im.size[1] - 1280
    return im.crop((0, max(dh // 2, 0), 720, max(dh // 2, 0) + 1280))


def cat(im, o, w=O, h=None):
    W, H = im.size
    x0, y0, x1, y1 = o
    c = im.crop((max(0, round(x0 * W)), max(0, round(y0 * H)), min(W, round(x1 * W)), min(H, round(y1 * H))))
    h = h or round(w * c.size[1] / max(1, c.size[0]))
    return c.resize((w, h), Image.LANCZOS)


# ---------- đo màu da ----------
def do_da(im):
    """Trung bình L, a (Lab) trên các điểm ảnh màu da (YCrCb), bỏ vải và nền."""
    a = np.asarray(im.convert("RGB")).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cr = (r - y) * 0.713 + 0.5
    cb = (b - y) * 0.564 + 0.5
    m = (cr > 0.53) & (cr < 0.68) & (cb > 0.30) & (cb < 0.50) & (y > 0.25)
    if m.sum() < 200:
        return None
    def lin(c):
        return np.where(c > 0.04045, ((c + 0.055) / 1.055) ** 2.4, c / 12.92)
    R, G, B = lin(r[m]), lin(g[m]), lin(b[m])
    X = (0.4124 * R + 0.3576 * G + 0.1805 * B) / 0.9505
    Y = 0.2126 * R + 0.7152 * G + 0.0722 * B
    f = lambda t: np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)  # noqa: E731
    L = 116 * f(Y) - 16
    A = 500 * (f(X) - f(Y))
    return round(float(L.mean()), 1), round(float(A.mean()), 1), int(m.sum())


# ---------- tờ so ----------
def nhan(o, chu, mau=(255, 230, 0)):
    d = ImageDraw.Draw(o)
    d.rectangle((0, 0, min(o.size[0], 8 + 7 * len(chu)), 18), fill=(0, 0, 0))
    d.text((3, 3), chu, fill=mau)
    return o


def ghep_hang(o_list, cao):
    o_list = [x.resize((round(x.size[0] * cao / x.size[1]), cao)) for x in o_list]
    W = sum(x.size[0] for x in o_list) + 4 * (len(o_list) - 1)
    t = Image.new("RGB", (W, cao), (40, 40, 40))
    x = 0
    for o in o_list:
        t.paste(o, (x, 0))
        x += o.size[0] + 4
    return t


def ghep_doc(hang, ra):
    W = max(h.size[0] for h in hang)
    t = Image.new("RGB", (W, sum(h.size[1] for h in hang) + 6 * len(hang)), (20, 20, 20))
    y = 0
    for h in hang:
        t.paste(h, (0, y))
        y += h.size[1] + 6
    ra.parent.mkdir(parents=True, exist_ok=True)
    t.save(ra, quality=88)
    print("Tờ so:", ra)


def khung_clip(f, fps=1.0):
    """Lấy khung mỗi 1/fps giây (giây 0,2; 1,2; ...) bằng ffmpeg, trả [(giây, ảnh)]."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    dai = float(r.stdout.strip() or 10)
    out, t = [], 0.2
    while t < dai - 0.05:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(f), "-frames:v", "1", "-f", "image2pipe",
                            "-vcodec", "png", "-"], capture_output=True, stdin=subprocess.DEVNULL, timeout=60).stdout
        if p:
            from io import BytesIO
            out.append((t, Image.open(BytesIO(p)).convert("RGB")))
        t += 1 / fps
    return out


# ---------- phiếu ----------
def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def doc_phieu(d):
    f = d / "khoa-mat" / "phieu.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {"nguong": NGUONG, "muc": {}}


def ghi_phieu(d, ph):
    f = d / "khoa-mat" / "phieu.json"
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(ph, ensure_ascii=False, indent=1), encoding="utf-8")


def dat_muc(ph, ten, ma, can, do):
    cu = ph["muc"].get(ten, {})
    if cu.get("md5") != ma:  # tệp mới hoặc đã đổi → điểm cũ mất hiệu lực
        cu = {}
    cu.update({"md5": ma, "can_cham": can, "do_da_chan": do})
    ph["muc"][ten] = cu


def kol_va_chuan(cfg):
    dk = thu_muc(cfg, "thu_muc_kol")
    kol = json.loads((dk / "kol.json").read_text(encoding="utf-8"))
    mc, cc = dk / "mat-chuan.png", dk / "chan-chuan.png"
    if not mc.is_file():
        sys.exit(f"Chưa có {mc}. Chạy: python khoa_mat.py chuan {dk}")
    return kol, Image.open(mc).convert("RGB"), (Image.open(cc).convert("RGB") if cc.is_file() else None)


def lay_kx(d):
    v = json.loads((d / "video.json").read_text(encoding="utf-8"))
    global KH
    KH = float(v.get("kh", KH))
    if "kx" not in v:
        sys.exit("video.json chưa có \"kx\" (tâm người − 0,35, số đã dùng cho cat_anh.py). Ghi vào rồi chạy lại.")
    return float(v["kx"])


# ---------- các lệnh ----------
def lenh_chuan(dk):
    kol = json.loads((dk / "kol.json").read_text(encoding="utf-8"))
    kx = float(kol.get("kx_chuan", 0.15))
    im = ve_goc_toan(Image.open(dk / kol.get("anh_chuan", "kol-chuan.png")))
    mat = cat(im, o_mat_toan(kx), 300)
    chan = cat(im, o_chan_toan(kx), 300)
    mat.save(dk / "mat-chuan.png")
    chan.save(dk / "chan-chuan.png")
    ghep_doc([ghep_hang([nhan(mat.copy(), "mat-chuan"), nhan(chan.copy(), "chan-chuan")], 420)], dk / "xem-chuan.jpg")
    print(f"Đã cắt mat-chuan.png, chan-chuan.png (kx_chuan={kx}). MỞ xem-chuan.jpg: khung mặt phải lọt trọn mặt và mái,"
          " khung chân phải lọt trọn hai chân. Lệch thì sửa kx_chuan trong kol.json và chạy lại.")
    do = do_da(chan)
    print("Màu da chân chuẩn (L, a, số điểm):", do)


def lenh_anh(cfg, d):
    kol, mc, cc = kol_va_chuan(cfg)
    kx = lay_kx(d)
    goc = ve_goc_toan(Image.open(d / "anh-goc.png"))
    mat, chan = cat(goc, o_mat_toan(kx), 300), cat(goc, o_chan_toan(kx), 300)
    hang = [ghep_hang([nhan(mc.copy(), "MAT CHUAN"), nhan(mat, "anh-goc")], 400)]
    do = do_da(chan)
    if cc is not None:
        hang.append(ghep_hang([nhan(cc.copy(), "CHAN CHUAN"), nhan(chan, f"anh-goc L,a={do[:2] if do else '-'}")], 400))
    v = json.loads((d / "video.json").read_text(encoding="utf-8"))
    if v.get("anh_nha_ban"):  # ảnh nhà bán đã dùng để tạo ảnh gốc (đường dẫn trong thư mục video)
        shop = [d / x for x in v["anh_nha_ban"]][:4]
    else:
        shop = sorted(p for p in (d / "shopee").glob("*") if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"))[:4]
    hang.append(ghep_hang([nhan(goc.copy(), "anh-goc")] + [nhan(Image.open(p).convert("RGB"), p.name[:24]) for p in shop], 640))
    ghep_doc(hang, d / "khoa-mat" / "to-anh.jpg")
    ph = doc_phieu(d)
    dat_muc(ph, "anh-goc.png", md5(d / "anh-goc.png"), ["mat", "chan", "ao"], do)
    ghi_phieu(d, ph)
    canh_bao_da(cc, do, "anh-goc.png")
    print("Mở khoa-mat/to-anh.jpg, phóng to so từng chi tiết, rồi chấm: python khoa_mat.py cham", d, "anh-goc.png mat=.. chan=.. ao=.. --nguoi ..")


def canh_bao_da(cc, do, ten):
    if cc is None or do is None:
        return False
    c = do_da(cc)
    if not c:
        return False
    dl, da = do[0] - c[0], do[1] - c[1]
    if dl < -LECH_L or da > LECH_A:
        print(f"⚠ CẢNH BÁO {ten}: da chân sẫm hơn {(-dl):.1f} hoặc đỏ hơn {da:.1f} so với chân chuẩn"
              f" (ngưỡng {LECH_L}/{LECH_A}). Soi đầu gối. Muốn cho qua phải ghi --ghi lý do.")
        return True
    return False


def lenh_clip(cfg, d):
    kol, mc, cc = kol_va_chuan(cfg)
    kx = lay_kx(d)
    ph = doc_phieu(d)
    hang = []
    for ten in CANH_MAT:
        f = d / ten
        if not f.is_file():
            print("Thiếu", ten)
            continue
        o = o_mat_toan(kx) if ("xoay" in ten or "lui" in ten) else sang_tren(o_mat_toan(kx), kx)
        o_list = [nhan(mc.copy(), "CHUAN")] + [nhan(cat(im, o, 200), f"{ten[:2]} {t:.1f}s") for t, im in khung_clip(f)]
        hang.append(ghep_hang(o_list, 260))
    ghep_doc(hang, d / "khoa-mat" / "to-mat.jpg")
    hang, do_chan = [], {}
    for ten in CANH_CHAN:
        f = d / ten
        if not f.is_file():
            continue
        kh = khung_clip(f)
        if "xoay" in ten or "lui" in ten:
            crops = [(t, cat(im, o_chan_toan(kx), 200)) for t, im in kh if "lui" not in ten or t >= 1.0]
        else:
            crops = [(t, im.resize((200, round(200 * im.size[1] / im.size[0])))) for t, im in kh[:4]]
        dos = [x for x in (do_da(c) for _, c in crops) if x]
        do_chan[ten] = (round(float(np.mean([x[0] for x in dos])), 1), round(float(np.mean([x[1] for x in dos])), 1), 0) if dos else None
        o_list = ([nhan(cc.copy(), "CHAN CHUAN")] if cc is not None else []) + [nhan(c, f"{ten[:2]} {t:.1f}s") for t, c in crops]
        hang.append(ghep_hang(o_list, 360))
    if hang:
        ghep_doc(hang, d / "khoa-mat" / "to-chan.jpg")
    for ten in sorted(set(CANH_MAT + CANH_CHAN)):
        if (d / ten).is_file():
            can = (["mat"] if ten in CANH_MAT else []) + (["chan"] if ten in CANH_CHAN else [])
            dat_muc(ph, ten, md5(d / ten), can, do_chan.get(ten))
            canh_bao_da(cc, do_chan.get(ten), ten)
    ghi_phieu(d, ph)
    print("Giao 2 tờ to-mat.jpg, to-chan.jpg cho người chấm độc lập, rồi ghi điểm từng cảnh bằng lệnh cham.")


def lenh_cham(d, ten, diem, nguoi, ghi):
    ph = doc_phieu(d)
    if ten not in ph["muc"]:
        sys.exit(f"{ten} chưa có trong phiếu: chạy lệnh anh/clip trước.")
    if not nguoi:
        sys.exit("Thiếu --nguoi (ai chấm).")
    m = ph["muc"][ten]
    if m.get("md5") != md5(d / ten):
        sys.exit(f"{ten} đã đổi sau khi lập tờ so: chạy lại lệnh anh/clip rồi chấm lại.")
    for kv in diem:
        k, v = kv.split("=")
        m[k] = int(v)
    m["nguoi"], m["ghi"] = nguoi, ghi or m.get("ghi", "")
    ghi_phieu(d, ph)
    print("Đã ghi", ten, {k: m.get(k) for k in m.get("can_cham", [])})


def lenh_duyet(d, nguoi, ghi):
    if not nguoi:
        sys.exit("Thiếu --nguoi: tên người dùng đã xem tờ so mặt.")
    ph = doc_phieu(d)
    ph["nguoi_dung_duyet"] = {"nguoi": nguoi, "ghi": ghi,
                              "md5": {t: m.get("md5") for t, m in ph["muc"].items()}}
    ghi_phieu(d, ph)
    print("Đã ghi người dùng duyệt mặt:", nguoi)


def lenh_kiem(cfg, d, buoc):
    ph = doc_phieu(d)
    can = {"anh": ["anh-goc.png"], "clip": [t for t in sorted(set(CANH_MAT + CANH_CHAN)) if (d / t).is_file()]}
    ds = can["anh"] + can["clip"] if buoc == "het" else can[buoc]
    _, _, cc = kol_va_chuan(cfg)
    loi = []
    for ten in ds:
        m = ph["muc"].get(ten)
        if not (d / ten).is_file():
            loi.append(f"thiếu tệp {ten}")
            continue
        if not m:
            loi.append(f"{ten}: chưa lập tờ so (lệnh {'anh' if ten == 'anh-goc.png' else 'clip'})")
            continue
        if m.get("md5") != md5(d / ten):
            loi.append(f"{ten}: tệp đã đổi sau khi chấm, phải lập tờ so và chấm lại")
            continue
        if not m.get("nguoi"):
            loi.append(f"{ten}: chưa có người chấm")
        for k in m.get("can_cham", []):
            v = m.get(k)
            if v is None:
                loi.append(f"{ten}: chưa chấm {k}")
            elif k == "chan" and v == 0:
                continue
            elif v < ph.get("nguong", NGUONG):
                loi.append(f"{ten}: {k} = {v} < {NGUONG} → CHẶN ({m.get('ghi', '')})")
        if "chan" in m.get("can_cham", []) and m.get("chan") not in (0, None):
            if canh_bao_da(cc, m.get("do_da_chan"), ten) and not m.get("ghi"):
                loi.append(f"{ten}: có cảnh báo màu da chân mà người chấm chưa ghi lý do")
    if buoc == "het":
        dd = ph.get("nguoi_dung_duyet")
        if not dd:
            loi.append("người dùng chưa duyệt mặt (lệnh duyet sau khi người dùng xem khoa-mat/to-mat.jpg)")
        elif any(dd["md5"].get(t) != ph["muc"].get(t, {}).get("md5") for t in ds):
            loi.append("có tệp đổi sau khi người dùng duyệt mặt: cho người dùng xem lại tờ so mặt mới")
    if loi:
        print("✘ CỔNG KHÓA MẶT CHƯA QUA:\n  " + "\n  ".join(loi))
        return False
    print(f"✔ Cổng khóa mặt qua ({buoc}): " + ", ".join(ds))
    return True


def main():
    in_utf8()
    ap = argparse.ArgumentParser()
    ap.add_argument("lenh", choices=["chuan", "anh", "clip", "cham", "duyet", "kiem"])
    ap.add_argument("thu_muc")
    ap.add_argument("ten", nargs="?")
    ap.add_argument("diem", nargs="*")
    ap.add_argument("--nguoi", default="")
    ap.add_argument("--ghi", default="")
    ap.add_argument("--buoc", default="het", choices=["anh", "clip", "het"])
    a = ap.parse_args()
    d = Path(a.thu_muc)
    global CANH_MAT
    vj = d / "video.json"
    if vj.is_file():  # nhánh tự nhiên (23/11): tên clip ghi trong video.json "canh_mat", vd ["c1-noi.mp4", "c2-noi-b.mp4"]
        try:
            CANH_MAT = json.loads(vj.read_text(encoding="utf-8")).get("canh_mat") or CANH_MAT
        except ValueError:
            pass
    if a.lenh == "chuan":
        return lenh_chuan(d)
    if a.lenh == "cham":
        return lenh_cham(d, a.ten, a.diem, a.nguoi, a.ghi)
    if a.lenh == "duyet":
        return lenh_duyet(d, a.nguoi, a.ghi)
    cfg = doc_cau_hinh()
    if a.lenh == "anh":
        return lenh_anh(cfg, d)
    if a.lenh == "clip":
        return lenh_clip(cfg, d)
    sys.exit(0 if lenh_kiem(cfg, d, a.buoc) else 1)


def cong_ke_hoach(thu_muc_video, cac_tep):
    """Mọi tệp hình trong kế hoạch dựng phải nằm trong phiếu (trừ cận thân trên q4): không lọt tệp chưa soi mặt."""
    ph = doc_phieu(Path(thu_muc_video))
    thieu = sorted({t for t in cac_tep if t not in ph["muc"] and not t.startswith(KHONG_MAT)})
    if thieu:
        sys.exit("Dừng: kế hoạch dựng dùng tệp chưa qua cổng khóa mặt: " + ", ".join(thieu)
                 + ". Chạy khoa_mat.py clip rồi cho người soát chấm các tệp này.")


def cong(thu_muc_video, buoc):
    """Gọi từ script khác: dừng hẳn nếu cổng chưa qua."""
    if not lenh_kiem(doc_cau_hinh(), Path(thu_muc_video), buoc):
        sys.exit(f"Dừng: cổng khóa mặt ({buoc}) chưa qua. Xem references/soat-do-that.md, mục Cổng khóa mặt.")


if __name__ == "__main__":
    main()

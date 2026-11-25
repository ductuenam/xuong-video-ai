"""CỔNG KHÓA MẶT, CHÂN VÀ MẪU ÁO cho video lookbook của KOL thương hiệu.

KOL là gương mặt của shop: sai mặt một cảnh là hỏng cả video. Cổng này đặt mặt chuẩn của KOL cạnh mặt ở
ảnh toàn thân từng bộ và ở clip máy tiến (mỗi giây một khung), đặt chân cạnh chân chuẩn (ảnh cận chân,
clip chân, có đo màu da), đặt ảnh toàn thân cạnh ảnh shop, rồi bắt người chấm ghi điểm từng mục vào phiếu.
Thiếu phiếu, điểm dưới ngưỡng, hoặc tệp đã đổi sau khi chấm thì các bước sau DỪNG:
  - gửi clip lên Muse (tự kiểm: khoa_mat.py kiem <video> --buoc anh phải qua),
  - dung_lookbook.py (mọi clip trong kế hoạch phải qua cổng),
  - luu_kho.py (cả ảnh, clip VÀ người dùng đã duyệt mặt).

Thư mục KOL (cau-hinh.json: thu_muc_kol, mặc định <thu_muc_du_an>/kol):
  kol-chuan.png   ảnh TOÀN THÂN chuẩn của KOL, đứng thẳng, thấy rõ mặt và hai chân đẹp (chân trắng, mịn, đầu gối sáng)
  kol.json        {"anh_chuan": "kol-chuan.png", "anh_chan_chuan": ""}  (anh_chan_chuan: ảnh cận chân đẹp nếu có)
Thư mục một video: boN/toan.png, boN/chan.png, boN/shopee/*, clip/bN-tien*.mp4, clip/bN-chan*.mp4, ke-hoach.json

Dùng:
  python khoa_mat.py chuan <thu_muc_kol>                 cắt mat-chuan.png, chan-chuan.png; MỞ xem-chuan.jpg kiểm khung cắt
  python khoa_mat.py anh   <thư mục video>               tờ so ảnh gốc: khoa-mat/to-anh.jpg (mặt, chân, áo cạnh ảnh shop)
  python khoa_mat.py clip  <thư mục video> [ke-hoach.json]  tờ so clip: khoa-mat/to-mat.jpg, khoa-mat/to-chan.jpg
  python khoa_mat.py cham  <thư mục video> <tệp> mat=5 ao=5 chan=4 --nguoi "<ai chấm>" [--ghi "..."]
       <tệp> viết như trong phiếu: bo1/toan.png, bo1/chan.png, clip/b1-tien.mp4, clip/b1-chan.mp4
  python khoa_mat.py duyet <thư mục video> --nguoi "<tên người dùng>" [--ghi "lời duyệt"]
       NGƯỜI DÙNG (chủ shop) tự xem khoa-mat/to-mat.jpg và to-anh.jpg rồi duyệt; máy và agent đạt CHƯA ĐỦ
  python khoa_mat.py kiem  <thư mục video> [--buoc anh|clip|het] [--ke-hoach ke-hoach.json]

Thang điểm từng mục (1–5), ngưỡng qua là 4:
  mat  5 = chắc chắn cùng một người với mặt chuẩn; 4 = cùng người, khác nhẹ do góc/biểu cảm;
       3 trở xuống = trông như người khác: mặt bè/đầy/tròn ra hoặc dài/gầy/cằm nhọn đi, đổi mắt, mũi, môi,
       mái, kiểu tóc, son đổi màu rõ (đỏ gạch, tím), già đi → CHẶN.
       DA MẶT (chủ shop chốt): có nốt ruồi, chấm nâu, tàn nhang đậm thấy được ở cỡ xem thường → mat ≤ 3, CHẶN,
       dù ảnh chuẩn có. Da phải xinh, mịn, trắng sáng nhưng vẫn thật (sáp, nhựa, bóng loáng cũng là lỗi).
  chan 5 = chân thon, trắng sáng, mịn đều màu như chân chuẩn, đầu gối sáng (hoặc quần tất/quần/bốt che gọn,
       đúng bộ đồ); 4 = đạt, khác nhẹ do ánh sáng; 3 trở xuống = da sẫm/đỏ/sần, đầu gối thâm, đùi to ra,
       vết bẩn, chân méo, giày đổi kiểu → CHẶN. Chân bị che hết (quần dài, váy dài) thì chan=0 ("không thấy") và BẮT BUỘC --ghi che bằng gì.
  ao   chỉ cho ảnh toàn thân: 5 = đúng mẫu shop từng chi tiết (cổ, cúc, khóa, túi, tay, gấu, vân, màu);
       3 trở xuống = sai kiểu cổ, thiếu/thừa chi tiết, sai màu → CHẶN.
Máy đo màu da chân (độ sáng L, độ đỏ a trong hệ Lab) so với chân chuẩn: sẫm hơn hoặc đỏ hơn quá ngưỡng thì in
CẢNH BÁO, mục đó phải có --ghi giải thích của người chấm mới qua.
Máy dò vị trí mặt bằng mô hình YuNet đi kèm gói (scripts/mo-hinh/; không có thì Haar, cuối cùng theo màu da) để cắt ô so, KHÔNG tự nhận ra người: điểm mặt do người chấm nhìn tờ so mà cho.
Người chấm nên là agent sku-lb-soi-da-mat (độc lập), không phải người vừa làm video.
Đã gặp: agent chấm "giống" mà chủ shop xem thì "không giống". Mặt lệch dù nhẹ là tạo lại ảnh/clip đó.
"""
import argparse
import os

os.environ.setdefault("OPENCV_LOG_LEVEL", "ERROR")  # OpenCV 5 in cảnh báo vô hại mỗi lần dò mặt
import hashlib
import json
import subprocess
import sys
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import cau_hinh  # noqa: E402

NGUONG = 4
LECH_L, LECH_A = 8.0, 6.0  # ngưỡng cảnh báo màu da chân
DUOI_ANH = (".png", ".jpg", ".jpeg", ".webp")
_CASCADE = None


def in_utf8():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def thu_muc_kol():
    ch = cau_hinh()
    return Path(ch.get("thu_muc_kol") or (Path(ch["thu_muc_du_an"]) / "kol")).expanduser()


# ---------- dò mặt, cắt ô ----------
def do_mat(im):
    """Trả (x, y, w, h) của mặt, hoặc None.
    Thứ tự: mô hình YuNet đi kèm gói (scripts/mo-hinh/), bộ dò Haar của OpenCV 4, cuối cùng dò bằng màu da: mặt là khối da CAO NHẤT đủ lớn
    (tay chống hông, chân nằm thấp hơn). Chỉ để cắt ô so cho người chấm, không dùng để nhận người."""
    global _CASCADE
    try:
        import cv2
    except ImportError:
        return None
    W, H = im.size
    mh = Path(__file__).resolve().parent / "mo-hinh" / "face_detection_yunet_2023mar.onnx"
    if mh.is_file() and hasattr(cv2, "FaceDetectorYN"):  # YuNet (OpenCV Zoo, MIT) — chắc nhất, đi kèm gói
        bgr = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2BGR)
        k = min(1.0, 960 / max(W, H))
        if k < 1:
            bgr = cv2.resize(bgr, (round(W * k), round(H * k)))
        dt = cv2.FaceDetectorYN.create(str(mh), "", (bgr.shape[1], bgr.shape[0]), 0.6, 0.3, 50)
        _, f = dt.detect(bgr)
        if f is not None and len(f):
            x, y, w, h = max(f, key=lambda r: r[2] * r[3] * r[14])[:4]
            return int(x / k), int(y / k), int(w / k), int(h / k)
    if hasattr(cv2, "CascadeClassifier"):
        if _CASCADE is None:
            _CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        g = cv2.cvtColor(np.asarray(im.convert("RGB")), cv2.COLOR_RGB2GRAY)
        f = _CASCADE.detectMultiScale(g, 1.08, 5, minSize=(max(24, W // 30), max(24, W // 30)))
        if len(f):
            return tuple(int(v) for v in max(f, key=lambda r: r[2] * r[3]))
    k = 240 / W
    nho = im.convert("RGB").resize((240, max(1, round(H * k))))
    a = np.asarray(nho).astype(np.float32) / 255.0
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    y = 0.299 * r + 0.587 * g + 0.114 * b
    cr = (r - y) * 0.713 + 0.5
    cb = (b - y) * 0.564 + 0.5
    m = ((cr > 0.53) & (cr < 0.68) & (cb > 0.30) & (cb < 0.50) & (y > 0.30)).astype(np.uint8)
    # phông màu da (hồng, be) cũng lọt vùng da: bỏ điểm ảnh gần màu viền khung (mép trên, hai mép bên)
    vien = np.concatenate([a[:4].reshape(-1, 3), a[:, :4].reshape(-1, 3), a[:, -4:].reshape(-1, 3)])
    nen = np.median(vien, axis=0)
    m[np.abs(a - nen).sum(axis=2) < 0.10] = 0
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    n, _, st, _ = cv2.connectedComponentsWithStats(m, 8)
    h_nho = m.shape[0]
    ung = []
    for i in range(1, n):
        x, yy, w, h, dt = st[i]
        if dt < 0.0015 * 240 * h_nho or dt > 0.25 * 240 * h_nho or w < 8 or yy > 0.7 * h_nho:
            continue
        if not (0.5 <= h / max(w, 1) <= 4.0):
            continue
        # mặt có tóc/mái tối ngay trên và hai bên; áo trùng màu da (hồng, be) thì không
        x0, x1 = max(0, x - w // 4), min(240, x + w + w // 4)
        tren = y[max(0, yy - max(3, w // 4)):yy + 1, x + w // 5:x + w - w // 5]
        ben = np.concatenate([y[yy:yy + w, x0:x + 2].ravel(), y[yy:yy + w, x + w - 2:x1].ravel()])
        toc = 0.5 * float((tren < 0.28).mean() if tren.size else 0) + 0.5 * float((ben < 0.28).mean() if ben.size else 0)
        if toc < 0.25 or w > 0.6 * 240:
            continue
        ung.append((yy, x, w, h, dt))
    if not ung:
        return None
    lon = max(u[4] for u in ung)
    ung = [u for u in ung if u[4] >= 0.25 * lon]
    yy, x, w, h, _ = min(ung)  # khối cao nhất
    h = min(h, int(w * 1.3))   # cổ/ngực hở dính liền mặt: chỉ lấy phần trên
    return int(x / k), int(yy / k), int(w / k), int(h / k)


def o_mat(im, canh=220):
    """Ô vuông quanh mặt (có tóc, mái, cằm). Không dò được thì cắt vùng đầu mặc định của ảnh toàn thân."""
    W, H = im.size
    m = do_mat(im)
    if m:
        x, y, w, h = m
        s = int(w * 1.7)
        cx, cy = x + w // 2, y + int(h * 0.48)
        box = (cx - s // 2, cy - s // 2, cx + s // 2, cy + s // 2)
    else:
        box = (int(W * 0.34), int(H * 0.02), int(W * 0.66), int(H * 0.02 + W * 0.32))
    return im.crop(box).resize((canh, canh), Image.LANCZOS), bool(m)


def o_chan_toan(im, rong=200):
    """Vùng chân của ảnh TOÀN THÂN (người đứng giữa khung): 55%–99% chiều cao, giữa ±22%."""
    W, H = im.size
    c = im.crop((int(W * 0.28), int(H * 0.55), int(W * 0.72), int(H * 0.99)))
    return c.resize((rong, round(rong * c.size[1] / c.size[0])), Image.LANCZOS)


def thu_nho(im, rong=200):
    return im.resize((rong, round(rong * im.size[1] / im.size[0])), Image.LANCZOS)


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
    return round(float((116 * f(Y) - 16).mean()), 1), round(float((500 * (f(X) - f(Y))).mean()), 1), int(m.sum())


def canh_bao_da(cc, do, ten):
    if cc is None or not do:
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


# ---------- tờ so ----------
def nhan(o, chu, mau=(255, 230, 0)):
    d = ImageDraw.Draw(o)
    d.rectangle((0, 0, min(o.size[0], 8 + 7 * len(chu)), 18), fill=(0, 0, 0))
    d.text((3, 3), chu, fill=mau)
    return o


def ghep_hang(o_list, cao):
    """Ghép một hàng, GIỮ ĐÚNG TỈ LỆ từng ô (không bóp ngang: bóp làm mặt trông dài/gầy, chấm sai)."""
    o_list = [x.resize((round(x.size[0] * cao / x.size[1]), cao), Image.LANCZOS) for x in o_list]
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


def khung_clip(f, buoc=1.0):
    """Khung ở giây 0,3; 1,3; ... bằng ffmpeg (có giới hạn thời gian), trả [(giây, ảnh)]."""
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=60)
    dai = float(r.stdout.strip() or 10)
    out, t = [], 0.3
    while t < dai - 0.05:
        p = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{t:.2f}", "-i", str(f), "-frames:v", "1", "-f", "image2pipe",
                            "-vcodec", "png", "-"], capture_output=True, stdin=subprocess.DEVNULL, timeout=60).stdout
        if p:
            out.append((t, Image.open(BytesIO(p)).convert("RGB")))
        t += buoc
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


def chuan():
    dk = thu_muc_kol()
    mc, cc = dk / "mat-chuan.png", dk / "chan-chuan.png"
    if not mc.is_file():
        sys.exit(f"Chưa có {mc}. Chạy: python khoa_mat.py chuan \"{dk}\"")
    return Image.open(mc).convert("RGB"), (Image.open(cc).convert("RGB") if cc.is_file() else None)


def cac_bo(d):
    return sorted((p for p in d.glob("bo*") if p.is_dir() and p.name[2:].isdigit()), key=lambda p: int(p.name[2:]))


def anh_shop(bo):
    return sorted(p for p in (bo / "shopee").glob("*") if p.suffix.lower() in DUOI_ANH)[:3] if (bo / "shopee").is_dir() else []


def clip_ke_hoach(d, ke_hoach=None):
    """Các clip kế hoạch dựng dùng (đường dẫn tương đối như trong phiếu). Không có kế hoạch thì mọi clip trong clip/."""
    kp = d / (ke_hoach or "ke-hoach.json")
    if kp.is_file():
        kh = json.loads(kp.read_text(encoding="utf-8"))
        return sorted({Path(x["clip"]).as_posix() for x in kh.get("doan", [])})
    return sorted(p.relative_to(d).as_posix() for p in (d / "clip").glob("*.mp4")) if (d / "clip").is_dir() else []


def la_clip_chan(ten):
    return "chan" in Path(ten).stem


# ---------- các lệnh ----------
def lenh_chuan(dk):
    kol = json.loads((dk / "kol.json").read_text(encoding="utf-8")) if (dk / "kol.json").is_file() else {}
    im = Image.open(dk / kol.get("anh_chuan", "kol-chuan.png")).convert("RGB")
    mat, co = o_mat(im, 300)
    if kol.get("anh_chan_chuan"):
        chan = thu_nho(Image.open(dk / kol["anh_chan_chuan"]).convert("RGB"), 300)
    else:
        chan = o_chan_toan(im, 300)
    mat.save(dk / "mat-chuan.png")
    chan.save(dk / "chan-chuan.png")
    ghep_doc([ghep_hang([nhan(mat.copy(), "mat-chuan"), nhan(chan.copy(), "chan-chuan")], 420)], dk / "xem-chuan.jpg")
    print(f"Đã cắt mat-chuan.png ({'dò được mặt' if co else 'KHÔNG dò được mặt, cắt vùng mặc định'}), chan-chuan.png.")
    print("MỞ xem-chuan.jpg: ô mặt phải trọn mặt, mái, cằm; ô chân phải trọn hai chân ĐẸP (trắng, mịn, đầu gối sáng)."
          " Chân ảnh chuẩn chưa đẹp thì sửa ảnh chuẩn trước (lenh-muse.md, Bước 0), vì mọi chân sau sẽ so với nó.")
    print("Màu da chân chuẩn (L, a, số điểm):", do_da(chan))


def lenh_anh(d):
    mc, cc = chuan()
    ph = doc_phieu(d)
    hang = []
    for bo in cac_bo(d):
        toan = bo / "toan.png"
        if not toan.is_file():
            print("Thiếu", toan)
            continue
        im = Image.open(toan).convert("RGB")
        mat, co = o_mat(im)
        o = [nhan(mc.copy(), "MAT CHUAN"), nhan(mat, f"{bo.name} toan" + ("" if co else " (?)")),
             nhan(thu_nho(im, 260), f"{bo.name}/toan.png")]
        o += [nhan(Image.open(p).convert("RGB"), p.name[:22]) for p in anh_shop(bo)]
        hang.append(ghep_hang(o, 420))
        dat_muc(ph, f"{bo.name}/toan.png", md5(toan), ["mat", "ao"], None)
        chan_f = bo / "chan.png"
        if chan_f.is_file():
            ci = Image.open(chan_f).convert("RGB")
            do = do_da(ci)
            hang.append(ghep_hang(([nhan(cc.copy(), "CHAN CHUAN")] if cc is not None else [])
                                  + [nhan(o_chan_toan(im), f"{bo.name} chan o toan"),
                                     nhan(thu_nho(ci, 260), f"{bo.name}/chan.png L,a={do[:2] if do else '-'}")], 420))
            dat_muc(ph, f"{bo.name}/chan.png", md5(chan_f), ["chan"], do)
            canh_bao_da(cc, do, f"{bo.name}/chan.png")
    if not hang:
        sys.exit("Không thấy boN/toan.png nào.")
    ghep_doc(hang, d / "khoa-mat" / "to-anh.jpg")
    ghi_phieu(d, ph)
    print("Mở khoa-mat/to-anh.jpg, phóng to so từng chi tiết, rồi chấm từng tệp:\n"
          f"  python khoa_mat.py cham \"{d}\" bo1/toan.png mat=.. ao=.. --nguoi ..\n"
          f"  python khoa_mat.py cham \"{d}\" bo1/chan.png chan=.. --nguoi ..")


def lenh_clip(d, ke_hoach=None):
    mc, cc = chuan()
    ph = doc_phieu(d)
    hm, hc = [], []
    for ten in clip_ke_hoach(d, ke_hoach):
        f = d / ten
        if not f.is_file():
            print("Thiếu", ten)
            continue
        kh = khung_clip(f)
        if la_clip_chan(ten):
            crops = [(t, thu_nho(im, 200)) for t, im in kh]
            dos = [x for x in (do_da(c) for _, c in crops) if x]
            do = (round(float(np.mean([x[0] for x in dos])), 1), round(float(np.mean([x[1] for x in dos])), 1), 0) if dos else None
            hc.append(ghep_hang(([nhan(cc.copy(), "CHAN CHUAN")] if cc is not None else [])
                                + [nhan(c, f"{Path(ten).stem} {t:.1f}s") for t, c in crops], 300))
            dat_muc(ph, ten, md5(f), ["chan"], do)
            canh_bao_da(cc, do, ten)
        else:
            o = [nhan(mc.copy(), "CHUAN")]
            for t, im in kh:
                c, co = o_mat(im, 200)
                o.append(nhan(c, f"{Path(ten).stem} {t:.1f}s" + ("" if co else "?")))
            hm.append(ghep_hang(o, 220))
            dat_muc(ph, ten, md5(f), ["mat"], None)
    if hm:
        ghep_doc(hm, d / "khoa-mat" / "to-mat.jpg")
    if hc:
        ghep_doc(hc, d / "khoa-mat" / "to-chan.jpg")
    ghi_phieu(d, ph)
    print("Giao to-mat.jpg, to-chan.jpg cho người chấm độc lập; ghi điểm từng clip bằng lệnh cham"
          " (clip máy tiến: mat=..; clip chân: chan=..). Mặt lệch ở BẤT KỲ giây nào trong khúc định dùng là chấm ≤ 3.")


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
        if k not in m.get("can_cham", []):
            sys.exit(f"{ten} không chấm mục {k} (chỉ chấm: {', '.join(m.get('can_cham', []))}).")
        m[k] = int(v)
    if m.get("chan") == 0 and not ghi:  # phải ghi lý do ngay lần chấm này, không dựa ghi chú cũ
        sys.exit("chan=0 (\"chân bị che hết, không thấy\") phải có --ghi nói rõ che bằng gì (quần dài, váy dài, tất...)."
                 " Thấy da chân dù ít (cổ chân, mu bàn chân) thì chấm điểm 1–5, không chấm 0.")
    m["nguoi"], m["ghi"] = nguoi, ghi or m.get("ghi", "")
    ghi_phieu(d, ph)
    print("Đã ghi", ten, {k: m.get(k) for k in m.get("can_cham", [])})


def lenh_duyet(d, nguoi, ghi):
    if not nguoi:
        sys.exit("Thiếu --nguoi: tên người dùng đã xem tờ so mặt.")
    ph = doc_phieu(d)
    ph["nguoi_dung_duyet"] = {"nguoi": nguoi, "ghi": ghi, "md5": {t: m.get("md5") for t, m in ph["muc"].items()}}
    ghi_phieu(d, ph)
    print("Đã ghi người dùng duyệt mặt:", nguoi)


def lenh_kiem(d, buoc, ke_hoach=None, ds_clip=None):
    ph = doc_phieu(d)
    _, cc = chuan()
    anh = []
    for bo in cac_bo(d):
        anh.append(f"{bo.name}/toan.png")
        if (bo / "chan.png").is_file():
            anh.append(f"{bo.name}/chan.png")
    clip = ds_clip if ds_clip is not None else clip_ke_hoach(d, ke_hoach)
    ds = {"anh": anh, "clip": clip, "het": anh + clip}[buoc]
    loi = []
    if not ds:
        loi.append("không có tệp nào để kiểm")
    for ten in ds:
        m = ph["muc"].get(ten)
        if not (d / ten).is_file():
            loi.append(f"thiếu tệp {ten}")
            continue
        if not m:
            loi.append(f"{ten}: chưa lập tờ so (lệnh {'clip' if ten.endswith('.mp4') else 'anh'})")
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
            loi.append("người dùng chưa duyệt mặt (lệnh duyet sau khi người dùng xem khoa-mat/to-mat.jpg, to-anh.jpg)")
        elif any(dd["md5"].get(t) != ph["muc"].get(t, {}).get("md5") for t in ds):
            loi.append("có tệp đổi sau khi người dùng duyệt mặt: cho người dùng xem lại tờ so mới")
    if loi:
        print("✘ CỔNG KHÓA MẶT CHƯA QUA:\n  " + "\n  ".join(loi))
        return False
    print(f"✔ Cổng khóa mặt qua ({buoc}): " + ", ".join(ds))
    return True


def cong(thu_muc_video, buoc, ke_hoach=None, ds_clip=None):
    """Gọi từ script khác: dừng hẳn nếu cổng chưa qua."""
    if not lenh_kiem(Path(thu_muc_video), buoc, ke_hoach, ds_clip):
        sys.exit(f"Dừng: cổng khóa mặt ({buoc}) chưa qua. Xem SKILL.md, mục Cổng khóa mặt.")


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
    ap.add_argument("--ke-hoach", default=None)
    a = ap.parse_args()
    d = Path(a.thu_muc)
    if a.lenh == "chuan":
        return lenh_chuan(d)
    if a.lenh == "anh":
        return lenh_anh(d)
    if a.lenh == "clip":
        return lenh_clip(d, a.ten or a.ke_hoach)
    if a.lenh == "cham":
        return lenh_cham(d, a.ten, a.diem, a.nguoi, a.ghi)
    if a.lenh == "duyet":
        return lenh_duyet(d, a.nguoi, a.ghi)
    sys.exit(0 if lenh_kiem(d, a.buoc, a.ke_hoach) else 1)


if __name__ == "__main__":
    main()

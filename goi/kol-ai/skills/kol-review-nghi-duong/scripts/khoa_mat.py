"""Cổng khóa mặt KOL cho video nghỉ dưỡng.

  khoa_mat.py kol  <thư mục video>   tờ KOL: mặt chuẩn + mặt mọi ảnh trong kol/ và anh-kol/  → khoa-mat/to-kol.jpg
  khoa_mat.py clip <thư mục video>   tờ mặt mỗi cảnh mỗi giây + tờ bộ đồ                      → khoa-mat/to-mat.jpg, to-do.jpg
  khoa_mat.py cham <thư mục video> <tệp> mat=4.5 [do=5] --nguoi <ai>                          ghi điểm (kèm md5)
  khoa_mat.py duyet <thư mục video> --nguoi "<tên>" --ghi "<lời duyệt>"                        người dùng duyệt mặt
  khoa_mat.py kiem <thư mục video>   in QUA / CHƯA QUA (thoát mã 1 khi chưa qua)

Ảnh mặt chuẩn: video.json → "kol_chuan" (mặc định assets/mat-chuan.png).
Ngưỡng: mỗi ảnh KOL và mỗi clip mặt ≥ 4/5, bộ đồ ≥ 4/5.
"""
import sys, time, argparse
from pathlib import Path
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont
from chung import GOC, doc_json, ghi_json, md5, do_dai, khung_tai, cat_mat, font, doc_anh_cv, ghi_anh_cv

NGUONG = 4.0

def anh_chuan(d):
    vj = doc_json(d / "video.json") if (d / "video.json").exists() else {}
    p = Path(vj.get("kol_chuan") or GOC / "assets" / "mat-chuan.png")
    if not p.is_absolute():
        p = d / p
    return doc_anh_cv(p)

def nhan(img, chu, co=20):
    pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    dr = ImageDraw.Draw(pil)
    f = ImageFont.truetype(font("BeVietnamPro-Bold.ttf"), co)
    dr.rectangle([0, 0, pil.width, co + 8], fill=(0, 0, 0))
    dr.text((4, 2), chu, font=f, fill=(255, 230, 80))
    return cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)

def ghep_hang(o, co):
    return np.hstack(o) if o else np.zeros((co, co, 3), np.uint8)

def ghep_doc(hang):
    r = max(h.shape[1] for h in hang)
    return np.vstack([np.pad(h, ((0, 0), (0, r - h.shape[1]), (0, 0))) for h in hang])

def danh_sach_canh(d):
    vj = doc_json(d / "video.json")
    return [c for c in vj.get("canh", []) if (d / c.get("clip", "-")).exists()]

def lenh_kol(d):
    co = 260
    chuan = cat_mat(anh_chuan(d), co)
    o_mat, o_toan = [nhan(chuan, "CHUAN")], []
    anh = sorted([*(d / "kol").glob("*.*"), *(d / "anh-kol").glob("*.*")]) if True else []
    anh = [p for p in anh if p.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp")]
    for p in anh:
        img = doc_anh_cv(p)
        m = cat_mat(img, co)
        o_mat.append(nhan(m if m is not None else np.zeros((co, co, 3), np.uint8), p.stem[:22]))
        t = cv2.resize(img, (co, int(img.shape[0] * co / img.shape[1])))
        o_toan.append(nhan(t, p.stem[:22]))
    hang = [ghep_hang(o_mat[i:i + 6], co) for i in range(0, len(o_mat), 6)]
    if o_toan:
        hmax = max(t.shape[0] for t in o_toan)
        o_toan = [np.pad(t, ((0, hmax - t.shape[0]), (0, 0), (0, 0))) for t in o_toan]
        hang += [ghep_hang(o_toan[i:i + 6], co) for i in range(0, len(o_toan), 6)]
    (d / "khoa-mat").mkdir(exist_ok=True)
    ghi_anh_cv(str(d / "khoa-mat" / "to-kol.jpg"), ghep_doc(hang))
    print("→", d / "khoa-mat" / "to-kol.jpg", f"({len(anh)} ảnh)")

def lenh_clip(d):
    co = 200
    chuan = nhan(cat_mat(anh_chuan(d), co), "CHUAN")
    hang, do = [], []
    for c in danh_sach_canh(d):
        p = d / c["clip"]
        dai = do_dai(p)
        o = [chuan]
        for g in np.arange(0.5, dai - 0.2, 1.0):
            k = khung_tai(p, g)
            m = cat_mat(k, co) if k is not None else None
            o.append(nhan(m if m is not None else np.zeros((co, co, 3), np.uint8), f"{c['id']} {g:.1f}s"))
        hang.append(ghep_hang(o, co))
        k = khung_tai(p, 1.0, 270)
        if k is not None:
            do.append(nhan(k, c["id"]))
    (d / "khoa-mat").mkdir(exist_ok=True)
    ghi_anh_cv(str(d / "khoa-mat" / "to-mat.jpg"), ghep_doc(hang))
    if do:
        ghi_anh_cv(str(d / "khoa-mat" / "to-do.jpg"), ghep_hang(do, 270))
    print("→", d / "khoa-mat" / "to-mat.jpg", "và to-do.jpg", f"({len(hang)} cảnh)")

def phieu(d):
    p = d / "khoa-mat" / "phieu.json"
    return doc_json(p) if p.exists() else {"cham": {}, "duyet": None}

def lenh_cham(d, tep, diem, nguoi):
    ph = phieu(d)
    f = d / tep
    if not f.exists():
        sys.exit(f"Không thấy {f}")
    dd = dict(x.split("=") for x in diem)
    ph["cham"][tep] = {"md5": md5(f), "diem": {k: float(v.replace(",", ".")) for k, v in dd.items()},
                       "nguoi": nguoi, "luc": time.strftime("%d/%m/%Y %H:%M")}
    (d / "khoa-mat").mkdir(exist_ok=True)
    ghi_json(d / "khoa-mat" / "phieu.json", ph)
    print("Đã ghi", tep, ph["cham"][tep]["diem"])

def lenh_duyet(d, nguoi, ghi):
    ph = phieu(d)
    ph["duyet"] = {"nguoi": nguoi, "ghi": ghi, "luc": time.strftime("%d/%m/%Y %H:%M"),
                   "md5": {c["clip"]: md5(d / c["clip"]) for c in danh_sach_canh(d)}}
    ghi_json(d / "khoa-mat" / "phieu.json", ph)
    print("Đã ghi duyệt mặt của", nguoi)

def lenh_kiem(d):
    ph, loi = phieu(d), []
    for c in danh_sach_canh(d):
        t = c["clip"]
        x = ph["cham"].get(t)
        if not x:
            loi.append(f"{t}: chưa chấm"); continue
        if x["md5"] != md5(d / t):
            loi.append(f"{t}: tệp đã đổi sau khi chấm"); continue
        for k, v in x["diem"].items():
            if v < NGUONG:
                loi.append(f"{t}: {k}={v} dưới {NGUONG}")
    du = ph.get("duyet")
    if not du:
        cho = "CHƯA có người dùng duyệt mặt"
    elif any(du["md5"].get(c["clip"]) != md5(d / c["clip"]) for c in danh_sach_canh(d)):
        cho = "có clip đổi sau khi người dùng duyệt → phải duyệt lại"
    else:
        cho = f"đã duyệt bởi {du['nguoi']} lúc {du['luc']}"
    if loi:
        print("CHƯA QUA cổng khóa mặt:"); [print(" -", l) for l in loi]
        print("Duyệt mặt:", cho); sys.exit(1)
    print("QUA cổng khóa mặt (máy chấm). Duyệt mặt:", cho)

if __name__ == "__main__":
    a = argparse.ArgumentParser()
    a.add_argument("lenh"); a.add_argument("thu_muc"); a.add_argument("them", nargs="*")
    a.add_argument("--nguoi", default=""); a.add_argument("--ghi", default="")
    x = a.parse_args(); d = Path(x.thu_muc)
    if x.lenh == "kol": lenh_kol(d)
    elif x.lenh == "clip": lenh_clip(d)
    elif x.lenh == "cham": lenh_cham(d, x.them[0], x.them[1:], x.nguoi or "?")
    elif x.lenh == "duyet": lenh_duyet(d, x.nguoi, x.ghi)
    elif x.lenh == "kiem": lenh_kiem(d)
    else: sys.exit(__doc__)

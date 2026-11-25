"""Lập props.json từ canh.json. Giờ cảnh tính theo số thứ tự cụm lời trong phu-de.json (đếm từ 1).
  python lap_canh.py <thư mục dự án>

Trong canh.json:
  tu, den : số cụm. tu = 0 là đầu video. den = "het" là hết lời + giữ khung cuối.
  moc     : mỗi phần tử là số nguyên (cụm), số thực (giây tính từ đầu cảnh), hoặc [cụm, giây cộng thêm]. Số 0 là giây 0.
  at      : như một phần tử của moc.
Cảnh dùng clip kho (ten, canhNen, o[].ten) được chép từ kho vào public/canh. Thiếu clip thì liệt kê để tạo trên Flow, mã thoát 2."""
import csv
import shutil
import sys
from pathlib import Path

from chung import doc, duong_dan, ghi, ho_so, kiem_so_dong

GIU_KHUNG_CUOI = 1.3
LOAI_CO_CLIP = {"flow-chu": "ten", "ten-cong-cu": "canhNen", "ket-comment": "clip", "ket-phe": "clip"}

da = Path(sys.argv[1])
P = doc(da / "phu-de.json")
HET = P[-1]["end"]


def A(i):
    return P[i - 1]["start"] if i else 0


def gio_moc(x, tu):
    """Đổi một mốc sang giây tính từ đầu cảnh."""
    if isinstance(x, list):
        return round(A(x[0]) - tu + x[1], 2)
    if isinstance(x, float) or x == 0:
        return x
    return round(max(0, A(x) - tu), 2)


goc_canh = doc(da / "canh.json")["canh"]
# Kiểm số dòng: tu = dòng đầu của cảnh (đếm từ 1, 0 là đầu video), den = dòng đầu của cảnh sau. Mốc ghi bằng số dòng
# phải nằm trong cảnh. Đánh số lệch một đã gặp ở 15-omni-voice và 19-4skill-P2, cảnh chạy trước lời một câu.
sai_dong = kiem_so_dong(goc_canh, len(P))
if sai_dong:
    print("✘ SỐ DÒNG CẢNH KHÔNG KHỚP:\n  " + "\n  ".join(sai_dong))
    sys.exit(3)
# Luật 15: video giới thiệu công cụ phải có tinh-trang.json kiểm ở nguồn gốc; món có sẵn không gọi là thứ phải cài (22-team-6-dev)
from kiem_chot import kiem_tinh_trang
sai_cc = kiem_tinh_trang(da)
if sai_cc:
    print("✘ TÌNH TRẠNG CÔNG CỤ CHƯA ĐÚNG:\n  " + "\n  ".join(sai_cc))
    sys.exit(3)
# Cảnh kết không lặp clip của 5 video gần nhất (21/11/2026, người dùng chê P02 giơ hai tay lặp lại)
from kiem_chot import kiem_canh_ket
sai_ket, gan_ket = kiem_canh_ket(da)
if gan_ket:
    print("clip kết 5 video gần nhất:", ", ".join(f"{ten}={ma}" for _, ten, ma in gan_ket))
if sai_ket:
    print("✘ CẢNH KẾT LẶP:\n  " + "\n  ".join(sai_ket))
    sys.exit(3)
# Đo tiêu đề bằng phông thật trước khi bundle: tràn dòng thì dừng ngay, khỏi mất một vòng ảnh tĩnh (23-skill-ben-trong)
from kiem_chu import kiem_tieu_de
sai_chu, nhac_chu = kiem_tieu_de(goc_canh)
for n in nhac_chu:
    print("⚠ " + n)
if sai_chu:
    print("✘ TIÊU ĐỀ SẼ TRÀN DÒNG:\n  " + "\n  ".join(sai_chu))
    sys.exit(3)
c = []
for x in goc_canh:
    y = dict(x)
    y["tu"] = round(A(x["tu"]), 2) if x["tu"] else 0
    if x["den"] == "het":
        y["den"] = round(HET + GIU_KHUNG_CUOI, 2)
        y["hetTieng"] = round(HET + 0.1, 2)
    else:
        y["den"] = round(A(x["den"]), 2)
    if "moc" in x:
        y["moc"] = [gio_moc(m, A(x["tu"])) for m in x["moc"]]
    if "at" in x:
        y["at"] = gio_moc(x["at"], A(x["tu"]))
    c.append(y)

# Gom clip cần dùng, đối chiếu kho
h = ho_so(da)
can = []
for x in c:
    if x["loai"] in LOAI_CO_CLIP:
        if LOAI_CO_CLIP[x["loai"]] in x:
            can.append(x[LOAI_CO_CLIP[x["loai"]]])
    for o in x.get("o", []):
        if "ten" in o:
            can.append(o["ten"])
can = sorted(set(can))
kho = duong_dan(h, h["khoCanh"]["thuMuc"])
ten_file = {}
danh_muc = kho / h["khoCanh"]["danhMuc"]
if danh_muc.exists():
    for r in csv.DictReader(danh_muc.open(encoding="utf-8-sig")):
        ten_file[r["ma"]] = r["file"]
ra = da / "public" / "canh"
ra.mkdir(parents=True, exist_ok=True)
thieu = []
# Biểu tượng theo mã: tự chép từ kho vào public/
for x in c:
    if x["loai"] == "bieu-tuong" and x.get("ma"):
        tim = next(iter(sorted(duong_dan(h, h.get("khoBieuTuong") or ".").glob(x["ma"] + ".*"))), None)
        if tim is None:
            thieu.append(x["ma"])
            continue
        (da / "public" / "bieu-tuong").mkdir(parents=True, exist_ok=True)
        shutil.copy2(tim, da / "public" / "bieu-tuong" / tim.name)
        x["anh"] = f"bieu-tuong/{tim.name}"
# Không có cảnh mặt người dẫn (học viên mới, 24/11/2026): loai.txt có "khong-mat" thì clip nằm trong thư mục "... CO MAT ..."
# bị chặn; thiếu clip thì gợi ý các clip KHÔNG NGƯỜI đang có thật trên máy để thay, không bắt đi tạo trên Flow.
from kiem_chot import loai_du_an
khong_mat = "khong-mat" in loai_du_an(da).split()
# Video giới thiệu bản thân (24/11/2026, người dẫn duyệt): không dùng cảnh hoạt hình, đồ chơi tí hon, đất sét, 3D cartoon
# (vd K006 robot tí hon chạy băng chuyền như đoàn tàu, K071 cửa hàng tí hon). Lọc theo ghi_chu trong danh mục cảnh.
gioi_thieu = "gioi-thieu" in loai_du_an(da).split()
HOAT_HINH = ("tí hon", "đất sét", "hoạt hình", "cartoon", "đồ chơi")
ghi_chu = {}
if danh_muc.exists():
    for r in csv.DictReader(danh_muc.open(encoding="utf-8-sig")):
        ghi_chu[r["ma"]] = (r.get("ghi_chu") or "").lower()


def hoat_hinh(ma):
    return gioi_thieu and any(t in ghi_chu.get(ma, "") for t in HOAT_HINH)


def co_mat(p):
    return any("CO MAT" in x.upper() for x in p.relative_to(kho).parts[:-1])


co_mat_ds = []
# Quét kho MỘT lần (kho nằm trên ổ USB, rglob từng tên rất chậm): tên file -> đường dẫn
chi_muc = {}
for f in kho.rglob("*.mp4"):
    chi_muc.setdefault(f.name, f)
for ma in can:
    dich = ra / f"{ma}.mp4"
    tim = chi_muc.get(ten_file[ma]) if ma in ten_file else None
    if hoat_hinh(ma):
        co_mat_ds.append(ma + " (hoạt hình/tí hon)")
        dich.unlink(missing_ok=True)
        continue
    if khong_mat and tim is not None and co_mat(tim):
        co_mat_ds.append(ma)
        dich.unlink(missing_ok=True)
        continue
    if dich.exists():
        continue
    if tim is None:
        thieu.append(ma)
    else:
        shutil.copy2(tim, dich)
if thieu or co_mat_ds:
    if co_mat_ds:
        print("✘ Clip không hợp loại video (mặt người dẫn khi khong-mat, hoặc hoạt hình/tí hon khi gioi-thieu):", ", ".join(co_mat_ds))
    if thieu:
        print("✘ THIẾU CẢNH TRONG KHO:", ", ".join(thieu))
    goi_y = []
    if danh_muc.exists():
        for r in csv.DictReader(danh_muc.open(encoding="utf-8-sig")):
            if r.get("dung") != "co" or not r.get("ma"):
                continue
            f = chi_muc.get(r["file"])
            if f is not None and not co_mat(f) and not hoat_hinh(r["ma"]):
                goi_y.append(f"{r['ma']} ({r.get('nhom', '')}: {r.get('ghi_chu', '')[:40]})")
    if goi_y:
        print(f"  Thay bằng clip không người đang có trên máy ({len(goi_y)} clip), ví dụ:")
        for g in goi_y[:25]:
            print("   ", g)
        print("  Xem đủ trong danh mục cảnh. Muốn cảnh riêng thì tạo trên Flow rồi thêm vào danh mục.")
    sys.exit(2)

tong = c[-1]["den"]
ghi(da / "props.json", {"thoiLuongGiay": tong, "phuDe": P, "canh": c})
ghi(da / "timeline.json", {"tong": tong, "het_tieng": HET, "moc": [x["tu"] for x in c[1:]]})
giua = [round((x["tu"] + x["den"]) / 2, 1) for x in c]
(da / "moc.txt").write_text(",".join(map(str, giua)), encoding="utf-8")
(da / "moc-logo.txt").write_text(",".join(str(round((x["tu"] + x["den"]) / 2, 1)) for x in c if x["loai"] == "flow-chu"), encoding="utf-8")
net = [round((x["tu"] + min(x["den"], x.get("hetTieng", x["den"]))) / 2, 1) for x in c if x["loai"] in ("nguoi", "nguoi-chu", "nguoi-so", "ket-phe", "ket-comment") and "clip" not in x]
(da / "moc-net.txt").write_text(",".join(map(str, net)), encoding="utf-8")
for x, g in zip(c, goc_canh):
    dau, cuoi = max(1, g["tu"]), (len(P) if g["den"] == "het" else g["den"] - 1)
    chu = " / ".join(str(g[k]) for k in ("tren", "duoi", "tieuDe") if g.get(k))
    print(f'{x["loai"]:14s} {x["tu"]:7.2f} {x["den"]:7.2f} {x.get("moc", "")}')
    print(f'{"":14s} dòng {dau}–{cuoi}: «{P[dau - 1]["text"][:46]}»' + (f"  | chữ: {chu[:40]}" if chu else ""))
print("tổng", tong, "giây; clip kho:", ", ".join(can) or "không")

"""Rút kinh nghiệm tốc độ sau mỗi video: mỗi video phải nhanh hơn, chất lượng giữ nguyên.
  python rut_kinh_nghiem.py <dự án> --bat-dau          # chạy ngay khi nhận việc (sau dò trùng), ghi giờ bắt đầu
  python rut_kinh_nghiem.py <dự án> [--ghi "nguyên nhân chậm"]   # chạy sau khi bàn giao
Đọc thoi-gian.csv (dung.py tự ghi), đếm số lần làm lại: tạo giọng, bundle (mỗi vòng ảnh tĩnh), xuất video.
Ghi một dòng vào <kênh>/so-toc-do.csv, so với trung vị 5 video gần nhất, in các chỗ làm lại để ghi vào loi-da-gap.md.
Chuẩn: tạo giọng 1 lần, bundle 1 lần, xuất 1 lần. Lỗi đã có trong loi-da-gap.md mà vẫn lặp thì phải khóa bằng code."""
import argparse
import csv
import datetime as dt
import json
import statistics
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("du_an")
ap.add_argument("--bat-dau", action="store_true")
ap.add_argument("--ghi", default="")
ap.add_argument("--tong", type=float, help="tổng phút đã đo bằng cách khác (video làm trước khi có --bat-dau)")
a = ap.parse_args()
da = Path(a.du_an).resolve()
F_BD = da / "bat-dau.txt"
DD = "%Y-%m-%d %H:%M:%S"
if a.bat_dau:
    F_BD.write_text(dt.datetime.now().strftime(DD), encoding="utf-8")
    print(f"✔ Bắt đầu tính giờ {da.name}: {F_BD.read_text(encoding='utf-8')}")
    sys.exit(0)


def tim_kenh(p):
    for x in [p, *p.parents]:
        if (x / "ho-so-kenh.json").exists():
            return x
    sys.exit("✘ Không thấy thư mục kênh (ho-so-kenh.json).")


kenh = tim_kenh(da)
tg = list(csv.DictReader(open(da / "thoi-gian.csv", encoding="utf-8"))) if (da / "thoi-gian.csv").exists() else []
for r in tg:
    r["t"] = dt.datetime.strptime(r["luc"], DD)
bd = dt.datetime.strptime(F_BD.read_text(encoding="utf-8").strip(), DD) if F_BD.exists() else None
if bd:
    tg = [r for r in tg if r["t"] >= bd]
elif tg:  # không ghi giờ bắt đầu: lấy phiên cuối (các bản ghi cách nhau dưới 60 phút), giờ tổng chỉ là ước
    k = len(tg) - 1
    while k > 0 and (tg[k]["t"] - tg[k - 1]["t"]).total_seconds() < 3600:
        k -= 1
    tg = tg[k:]
if not tg:
    sys.exit("✘ Chưa có thoi-gian.csv của lần dựng này: chạy dung.py trước.")
xong = max(r["t"] for r in tg)
tong_phut = a.tong if a.tong else round(((xong - bd).total_seconds() if bd else sum(int(r["giay"]) for r in tg) * 1.0) / 60, 1)
co_gio = bool(bd or a.tong)
may_phut = round(sum(int(r["giay"]) for r in tg) / 60, 1)
dem = lambda b: sum(r["buoc"] == b for r in tg)
lan_bundle, lan_render = dem("bundle"), dem("render")
# Lần tạo giọng: mọi file *.da-gui.txt của cả bài (bỏ bản đọc thử ngắn), kể cả bản cũ cất trong ban-*/ và thu-nghiem/
moc = bd or (min(r["t"] for r in tg) - dt.timedelta(hours=2))
gui = [f for f in (da / "giong").rglob("*.da-gui.txt") if dt.datetime.fromtimestamp(f.stat().st_mtime) >= moc
       and len(f.read_text(encoding="utf-8")) > 400]
lan_giong = len(gui)
tp = da / "render" / "thanh-pham.mp4"
giay = 0.0
if tp.exists():
    o = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(tp)], capture_output=True, text=True)
    giay = round(float(o.stdout.strip() or 0), 1)
phut_moi_10s = round(tong_phut / (giay / 10), 2) if giay else 0

f = kenh / "so-toc-do.csv"
COT = ["du_an", "ngay", "giay_thanh_pham", "tong_phut", "may_phut", "phut_moi_10s", "lan_tao_giong", "lan_bundle", "lan_render", "uoc", "ghi_chu"]
cu = list(csv.DictReader(open(f, encoding="utf-8-sig"))) if f.exists() else []
truoc = [r for r in cu if r["du_an"] != da.name and r["uoc"] != "co" and float(r["phut_moi_10s"] or 0) > 0][-5:]
dong = {"du_an": da.name, "ngay": xong.strftime("%d/%m/%Y"), "giay_thanh_pham": giay, "tong_phut": tong_phut, "may_phut": may_phut,
        "phut_moi_10s": phut_moi_10s, "lan_tao_giong": lan_giong, "lan_bundle": lan_bundle, "lan_render": lan_render,
        "uoc": "" if co_gio else "co", "ghi_chu": a.ghi}
cu = [r for r in cu if r["du_an"] != da.name] + [dong]
with open(f, "w", encoding="utf-8-sig", newline="") as g:
    w = csv.DictWriter(g, fieldnames=COT)
    w.writeheader()
    w.writerows(cu)

print(f"{da.name}: {giay} giây thành phẩm, {tong_phut} phút{' (ước, chưa ghi giờ bắt đầu)' if not co_gio else ''}, máy chạy {may_phut} phút")
print(f"  {phut_moi_10s} phút cho mỗi 10 giây thành phẩm")
if truoc:
    tv = statistics.median(float(r["phut_moi_10s"]) for r in truoc)
    hon = "NHANH HƠN" if phut_moi_10s < tv else "CHẬM HƠN"
    print(f"  {hon} trung vị {len(truoc)} video trước ({tv:.2f} phút mỗi 10 giây)")
lam_lai = [(lan_giong, "tạo giọng cả bài"), (lan_bundle, "vòng dựng ảnh tĩnh (bundle)"), (lan_render, "lần xuất video")]
co = [f"  ✘ {n} {ten} (chuẩn 1)" for n, ten in lam_lai if n > 1]
print("\n".join(co) if co else "  ✔ không phải làm lại bước nào")
if co:
    print("Việc phải làm ngay: ghi nguyên nhân từng lần làm lại vào references/loi-da-gap.md. Lỗi đã có trong sổ mà vẫn lặp"
          " thì khóa bằng code (cổng kiểm trong tao_giong, lap_canh hoặc nghiem_thu), thêm bài vào hoi_quy.py.")
print(f"Đã ghi {f.name}.")

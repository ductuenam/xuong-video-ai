"""Ghi video vừa bàn giao vào sổ video đã làm (so-video.csv ở thư mục kênh). Chạy ở bước bàn giao, MỖI video.
  python ghi_so_video.py <thư mục kênh> <thư mục dự án> --tu-khoa "Tên công cụ; từ khóa; ..." [--chu-de "..."] [--nguon "..."]
Chủ đề mặc định lấy dòng tiêu đề đầu của content.md. Dự án đã có trong sổ thì ghi đè dòng đó (làm lại, sửa bản).
tim_trung.py đọc sổ này để nhắc người dẫn khi chủ đề mới trùng video cũ."""
import argparse
import csv
import datetime
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
COT = ["so", "du_an", "chu_de", "tu_khoa", "nguon", "ngay_xong"]


def doc_so(f):
    if not f.exists():
        return []
    with open(f, encoding="utf-8-sig", newline="") as g:
        return list(csv.DictReader(g))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kenh")
    ap.add_argument("du_an")
    ap.add_argument("--tu-khoa", required=True, help="tên công cụ, tên kho, từ khóa chủ đề, cách nhau bằng dấu chấm phẩy")
    ap.add_argument("--chu-de")
    ap.add_argument("--nguon", default="")
    a = ap.parse_args()
    kenh, da = Path(a.kenh), Path(a.du_an)
    chu_de = a.chu_de
    if not chu_de and (da / "content.md").exists():
        chu_de = next((x[2:].strip() for x in (da / "content.md").read_text(encoding="utf-8").splitlines() if x.startswith("# ")), "")
    if not chu_de:
        sys.exit("✘ Thiếu chủ đề: thêm --chu-de hoặc viết content.md có dòng tiêu đề '# ...'.")
    m = re.match(r"(\d+[a-z]?)", da.name)
    dong = {"so": m.group(1) if m else "", "du_an": da.name, "chu_de": chu_de, "tu_khoa": a.tu_khoa, "nguon": a.nguon,
            "ngay_xong": datetime.date.today().strftime("%d/%m/%Y")}
    f = kenh / "so-video.csv"
    so = [x for x in doc_so(f) if x.get("du_an") != da.name] + [dong]
    with open(f, "w", encoding="utf-8-sig", newline="") as g:
        w = csv.DictWriter(g, fieldnames=COT)
        w.writeheader()
        w.writerows({k: x.get(k, "") for k in COT} for x in so)
    print(f"✔ Đã ghi sổ: {da.name} · {chu_de} · {a.tu_khoa} ({len(so)} video trong sổ)")


if __name__ == "__main__":
    main()

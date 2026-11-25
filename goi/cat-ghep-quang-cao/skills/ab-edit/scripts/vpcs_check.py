"""Soát chữ trên hình theo chính sách quảng cáo (VPCS) + quy tắc gọi tên của thương hiệu — chạy TRƯỚC khi quay khối chữ.
  python vpcs_check.py titles.json --brand an-binh-ai
  python vpcs_check.py --text "Khoá học AI 100% hiệu quả" --brand an-binh-ai
Báo: từ cấm (vpcs.tu_cam), từ phải che (vpcs.che_chu), cách gọi sai tên (vpcs.goi_ten: "sai" → "đúng"). Không tự sửa.
Chỉ soát CHỮ; hình cấm (vpcs.hinh_cam) phải soát bằng mắt trên bảng khung hình."""
import argparse
import json
import re
import sys
import unicodedata

from chung import doc_brand

ap = argparse.ArgumentParser()
ap.add_argument("titles", nargs="?")
ap.add_argument("--text", help="soát nhanh 1 câu")
ap.add_argument("--brand")
a = ap.parse_args()
V = doc_brand(a.brand).get("vpcs", {})
low = lambda s: unicodedata.normalize("NFC", s).lower()


def texts(x):
    for k in ("small", "big", "text", "badge", "under", "mid"):
        if isinstance(x.get(k), str):
            yield x[k]
    for k in ("lines", "labels"):
        for L in x.get(k, []) or []:
            yield L.get("text", "")
    for k in ("left", "right"):
        if isinstance(x.get(k), dict):
            yield x[k].get("text", "")


items = [{"id": "text", "text": a.text}] if a.text else json.load(open(a.titles, encoding="utf-8"))
bad = 0
for x in items:
    for t in texts(x):
        for w in V.get("tu_cam", []):
            if re.search(r"(?<!\w)" + re.escape(low(w)) + r"(?!\w)", low(t)):
                print(f"✘ {x['id']}: từ cấm «{w}» trong «{t}»")
                bad += 1
        for raw, okw in V.get("che_chu", {}).items():
            if not raw.startswith("_") and re.search(r"(?<![\w.])" + re.escape(low(raw)) + r"(?!\w)", low(t)):
                print(f"⚠ {x['id']}: «{raw}» chưa che → viết «{okw}» trong «{t}»")
                bad += 1
        for sai, dung in V.get("goi_ten", {}).items():
            if not sai.startswith("_") and re.search(r"(?<!\w)" + re.escape(low(sai)) + r"(?!\w)", low(t)):
                print(f"⚠ {x['id']}: gọi tên «{sai}» → dùng «{dung}» trong «{t}»")
                bad += 1
print("✔ Không thấy vi phạm chữ." if not bad else f"→ {bad} chỗ cần sửa.")
sys.exit(1 if bad else 0)

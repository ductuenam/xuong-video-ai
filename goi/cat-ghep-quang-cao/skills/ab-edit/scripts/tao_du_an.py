"""Tạo thư mục dự án video mới trong video-studio/07-du-an, kèm cấu hình thương hiệu.
  python tao_du_an.py <ten-du-an> [--brand an-binh-ai] [--che-do dung|livestream|bien-the]
"""
import argparse
import json
import shutil
from datetime import datetime

from chung import BRANDS, DU_AN, SKILL, STUDIO, doc_brand

THU_MUC_STUDIO = ("01-video-mau", "02-source-tho", "03-kich-ban", "04-giong-doc", "05-tai-nguyen", "06-thanh-pham", "07-du-an", "_backup")
# Dự án chỉ chứa file làm việc; source gốc luôn đọc thẳng từ 02-source-tho (không chép, không sửa)
THU_MUC_DU_AN = ("analysis", "broll", "stills", "titles", "so-do", "logo", "render", "ban-xem")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ten")
    ap.add_argument("--brand")
    ap.add_argument("--che-do", default="dung", choices=["dung", "livestream", "bien-the"])
    a = ap.parse_args()

    for d in THU_MUC_STUDIO:
        (STUDIO / d).mkdir(parents=True, exist_ok=True)
    brand = doc_brand(a.brand)
    p = DU_AN / a.ten
    if p.exists():
        raise SystemExit(f"Đã có dự án {p} — chọn tên khác.")
    for d in THU_MUC_DU_AN:
        (p / d).mkdir(parents=True)
    (p / "brand.json").write_text(json.dumps(brand, ensure_ascii=False, indent=2), encoding="utf-8")
    for f in (SKILL / "scripts" / "do-hoa").glob("*.html"):
        shutil.copy2(f, p / "so-do" / f.name)
    (p / "titles.json").write_text("[]", encoding="utf-8")
    (p / "du-an.json").write_text(json.dumps({
        "ten": a.ten, "che_do": a.che_do, "brand": brand.get("ten"), "tao_luc": f"{datetime.now():%Y-%m-%d %H:%M}",
        "source": [], "trang_thai": "moi-tao",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✔ Đã tạo dự án: {p}")
    print(f"  Chế độ: {a.che_do} · Thương hiệu: {brand.get('ten')} · Khổ mặc định: {brand['khung']['ti_le']}")


if __name__ == "__main__":
    main()

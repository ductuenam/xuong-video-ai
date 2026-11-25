"""Chép thành phẩm và cảnh gốc của một video KOL vào kho tài nguyên.

Lưu cả clip gốc cạnh thành phẩm để sau này dùng lại cảnh, làm biến thể hay dựng lại mà không phải tạo lại trên Muse.

Dùng: python luu_kho.py <thu-muc-mau> <thanh-pham.mp4> [--kho <thư mục kho>] [--ke-hoach ke-hoach.json]
Dừng nếu cổng khóa mặt chưa qua toàn bộ (cả bước người dùng duyệt mặt).  (mặc định: kho_thanh_pham trong cau-hinh.json)
Ra:   <kho>/<tên thành phẩm không đuôi>/
        <thanh-pham>.mp4            bản giao
        canh-goc/*.mp4              mọi clip Muse trong thư mục dự án (cả bản không dùng)
        anh/*.png, *.jpg             ảnh gốc, ảnh cận; anh/shopee/ ảnh shop
        nguon.md, ke-hoach.json, loi*.txt, prompt*.txt, lenh*.txt
Chỉ CHÉP, không xóa gì ở thư mục dự án. File đã có cùng cỡ thì bỏ qua.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import cau_hinh
KHO = cau_hinh()["kho_thanh_pham"]


def chep(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size == src.stat().st_size:
        return 0
    shutil.copy2(src, dst)
    return 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("thu_muc")
    ap.add_argument("thanh_pham")
    ap.add_argument("--kho", default=KHO)
    ap.add_argument("--ke-hoach", default="ke-hoach.json", help="kế hoạch dựng bản giao (để biết clip nào đã dùng)")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    tm, tp = Path(a.thu_muc), Path(a.thanh_pham)
    # CỔNG KHÓA MẶT toàn bộ: ảnh gốc + clip đã dùng chấm đạt VÀ người dùng đã tự xem tờ so mặt, duyệt.
    import khoa_mat
    khoa_mat.cong(tm, "het", ke_hoach=a.ke_hoach)
    ra = Path(a.kho) / tp.stem
    n = chep(tp, ra / tp.name)
    for f in sorted(tm.glob("*.mp4")):
        if f.resolve() != tp.resolve():  # thành phẩm đã chép ở trên, không lặp vào canh-goc
            n += chep(f, ra / "canh-goc" / f.name)
    # Ảnh: cả .png lẫn .jpg (ảnh tải về có thể là .jpg).
    # Bỏ tờ soát, bảng ghép, tệp tạm (tên bắt đầu bằng "_", "soat", "bang").
    for duoi in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        for f in sorted(tm.glob(duoi)):
            if not f.name.lower().startswith(("_", "soat", "bang")):
                n += chep(f, ra / "anh" / f.name)
    # Ảnh sản phẩm gốc của shop (thư mục shopee/), để làm lại ảnh gốc khi cần.
    for f in sorted((tm / "shopee").glob("*")) if (tm / "shopee").is_dir() else []:
        if f.is_file():
            n += chep(f, ra / "anh" / "shopee" / f.name)
    # Thư mục con kiểu lookbook (clip/, clip-moi/, bo1/..boN/, boN/shopee/): giữ nguyên cấu trúc.
    # Bản cũ chỉ quét tệp ngoài cùng nên sót toàn bộ clip Muse của video mẫu 2 (21/11/2026).
    for con in sorted(p for p in tm.iterdir() if p.is_dir() and p.name.lower() != "shopee"):
        for f in sorted(con.rglob("*")):
            if not f.is_file() or f.name.startswith("_"):
                continue
            duoi = f.suffix.lower()
            rel = f.relative_to(tm)
            if duoi == ".mp4":
                n += chep(f, ra / "canh-goc" / rel)
            elif duoi in (".png", ".jpg", ".jpeg", ".webp"):
                n += chep(f, ra / "anh" / rel)
            elif duoi in (".txt", ".md", ".json"):
                n += chep(f, ra / rel)
    for mau in ("nguon.md", "ke-hoach*.json", "loi*.txt", "prompt*.txt", "lenh*.txt",
                "mo-ta-canh*.txt", "diem-cat*.md", "DIEM-CHAM.md", "BAN-GIAO*.md", "*.moc.json"):
        for f in sorted(tm.glob(mau)):
            n += chep(f, ra / f.name)
    so_canh = len(list((ra / "canh-goc").rglob("*.mp4")))
    print(f"Đã chép {n} file mới vào {ra} ({so_canh} cảnh gốc)")


if __name__ == "__main__":
    main()

"""Chép thành phẩm và cảnh gốc của một video KOL vào kho tài nguyên.

Lưu cảnh tải về cùng chỗ với thành phẩm để sau này dùng lại cảnh, làm biến thể hay dựng lại
mà không phải tạo lại trên Muse.

Dùng: python luu_kho.py <thu-muc-video> <thanh-pham.mp4> [--kho <thư mục>]   (mặc định: thu_muc_kho trong cau-hinh.json)
Ra:   <kho>/<tên thành phẩm không đuôi>/
        <thanh-pham>.mp4            bản giao
        canh-goc/*.mp4              mọi clip Muse trong thư mục video (cả bản không dùng)
        anh/*.png, *.jpg, *.webp     ảnh gốc, ảnh cận; anh/shopee/ ảnh nhà bán
        nguon.md, ke-hoach.json, loi*.txt, prompt*.txt, lenh*.txt
Chỉ CHÉP, không xóa gì ở thư mục dự án. File đã có cùng cỡ thì bỏ qua.
"""
import argparse
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import doc_cau_hinh, thu_muc  # noqa: E402
from khoa_mat import cong  # noqa: E402


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
    ap.add_argument("--kho")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    tm, tp = Path(a.thu_muc), Path(a.thanh_pham)
    cong(tm, "het")  # không lưu kho video chưa qua cổng khóa mặt
    kho = Path(a.kho) if a.kho else thu_muc(doc_cau_hinh(), "thu_muc_kho")
    ra = kho / tp.stem
    n = chep(tp, ra / tp.name)
    for f in sorted(tm.glob("*.mp4")):
        if f.resolve() != tp.resolve():  # thành phẩm đã chép ở trên, không lặp vào canh-goc
            n += chep(f, ra / "canh-goc" / f.name)
    # Ảnh: .png, .jpg, .webp (ảnh Muse tải về là .webp).
    # Bỏ tờ soát, bảng ghép, tệp tạm (tên bắt đầu bằng "_", "soat", "bang").
    for duoi in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
        for f in sorted(tm.glob(duoi)):
            if not f.name.lower().startswith(("_", "soat", "bang")):
                n += chep(f, ra / "anh" / f.name)
    # Ảnh sản phẩm của nhà bán (thư mục shopee/), để làm lại ảnh gốc khi cần.
    for f in sorted((tm / "shopee").glob("*")) if (tm / "shopee").is_dir() else []:
        if f.is_file():
            n += chep(f, ra / "anh" / "shopee" / f.name)
    for mau in ("nguon.md", "video.json", "ke-hoach*.json", "loi*.txt", "tin*.txt", "lenh*.txt"):
        for f in sorted(tm.glob(mau)):
            n += chep(f, ra / f.name)
    so_canh = len(list((ra / "canh-goc").glob("*.mp4")))
    print(f"Đã chép {n} file mới vào {ra} ({so_canh} cảnh gốc)")


if __name__ == "__main__":
    main()

"""Kiểm máy trước khi dùng: Python, numpy, ffmpeg, cấu hình, thư mục. Không cài, không sửa gì.

Dùng: python kiem_may.py
"""
import importlib
import platform
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from chung import GOC_SKILL, doc_cau_hinh, in_utf8  # noqa: E402


def dong(ok, chu, sua=""):
    print(("✔ " if ok else "✘ ") + chu + ("" if ok or not sua else f"\n    → {sua}"))
    return ok


def main():
    in_utf8()
    tot = dong(sys.version_info >= (3, 10), f"Python {platform.python_version()}",
               "Cài Python 3.10+ (winget install Python.Python.3.12), tích 'Add to PATH'.")
    try:
        importlib.import_module("numpy")
        tot &= dong(True, "Thư viện numpy")
    except Exception:
        tot &= dong(False, "Thiếu numpy", "Chạy: python -m pip install numpy")
    tot &= dong(bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), "ffmpeg và ffprobe",
                "Chạy: winget install Gyan.FFmpeg rồi mở lại Claude.")
    cfg, p = doc_cau_hinh()
    if not dong(cfg is not None, "File cấu hình cau-hinh.json",
                f"Chép {GOC_SKILL / 'cau-hinh.mau.json'} thành cau-hinh.json rồi điền."):
        tot = False
    else:
        for k in ("thu_muc_lam_viec", "thu_muc_tai_ve"):
            q = Path(cfg.get(k, ""))
            tot &= dong(q.is_dir(), f"Thư mục {k}: {q}", "Tạo thư mục này hoặc sửa trong cau-hinh.json.")
        nh = str(cfg.get("thu_muc_nhac") or "").strip()
        if nh.lower() == "khong":
            dong(True, "Không lót nhạc: chỉ xuất bản không nhạc, chọn nhạc lúc đăng")
        else:
            q = Path(nh) if nh else Path(__file__).resolve().parent.parent / "nhac-mau"
            n = len([x for x in q.glob("*") if x.suffix.lower() in (".mp3", ".m4a", ".wav")]) if q.is_dir() else 0
            ten = f"Thư mục nhạc riêng: {n} bài" if nh else f"Nhạc mẫu CC0 đi kèm gói: {n} bài"
            tot &= dong(n > 0, ten, "Thêm nhạc có bản quyền, để trống thu_muc_nhac (dùng nhạc mẫu) hoặc điền \"khong\".")
        if cfg.get("shop", {}).get("ten", "").startswith("Tên shop"):
            tot = dong(False, "Chưa điền thông tin shop trong cau-hinh.json", "Điền mục shop (tên, số điện thoại, phong cách).")
    print("\nMÁY SẴN SÀNG" if tot else "\nCÒN MỤC ✘ — sửa theo hướng dẫn rồi chạy lại")
    print("Ngoài máy còn cần: trình duyệt có tiện ích Claude in Chrome, đã đăng nhập muse.ai.")
    sys.exit(0 if tot else 1)


if __name__ == "__main__":
    main()

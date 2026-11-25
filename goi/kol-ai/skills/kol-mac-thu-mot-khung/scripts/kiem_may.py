"""Kiểm máy trước khi làm video: Python, thư viện, ffmpeg, cấu hình, thư mục, KOL. Không cài, không sửa gì.

Dùng: python kiem_may.py
"""
import importlib
import json
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
               "Cài Python 3.10+ (winget install Python.Python.3.12), tích 'Add python.exe to PATH'.")
    for ten, goi in (("numpy", "numpy"), ("PIL", "pillow"), ("cv2", "opencv-python"), ("faster_whisper", "faster-whisper")):
        try:
            importlib.import_module(ten)
            tot &= dong(True, f"Thư viện {goi}")
        except Exception:
            tot &= dong(False, f"Thiếu thư viện {goi}", f"Chạy: python -m pip install {goi}")
    tot &= dong(bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), "ffmpeg và ffprobe",
                "Chạy: winget install Gyan.FFmpeg rồi mở lại Claude.")
    cfg = doc_cau_hinh(bat_buoc=False)
    du = True  # cấu hình đã điền đủ chưa (không ảnh hưởng MÁY SẴN SÀNG)
    if not dong(cfg is not None, "File cấu hình cau-hinh.json",
                f"Chép {GOC_SKILL / 'cau-hinh.mau.json'} thành cau-hinh.json rồi điền."):
        du = False
    else:
        for k in ("thu_muc_lam_viec", "thu_muc_tai_ve", "thu_muc_kho", "thu_muc_kol"):
            q = Path(cfg.get(k, ""))
            du &= dong(bool(cfg.get(k)) and q.is_dir(), f"Thư mục {k}: {q}", "Tạo thư mục này hoặc sửa trong cau-hinh.json.")
        if (cfg.get("shop", {}).get("ten", "") or "").startswith("Tên shop"):
            du &= dong(False, "Chưa điền tên shop trong cau-hinh.json", "Điền mục shop.")
        kol = Path(cfg.get("thu_muc_kol", "")) / "kol.json"
        if kol.is_file():
            k = json.loads(kol.read_text(encoding="utf-8"))
            anh = Path(cfg["thu_muc_kol"]) / k.get("anh_chuan", "kol-chuan.png")
            du &= dong(anh.is_file(), f"KOL '{k.get('ten', '?')}' đã dựng, ảnh chuẩn {anh.name}",
                       "Thiếu ảnh chuẩn: làm lại Bước 0 (dựng KOL).")
        else:
            print("• Chưa dựng KOL riêng: lần đầu làm Bước 0 của skill (dựng KOL trên Muse).")
            du = False
    print("\nMÁY SẴN SÀNG" if tot else "\nMÁY CÒN MỤC ✘ — sửa theo hướng dẫn rồi chạy lại")
    print("Cấu hình và KOL: đủ, làm video được." if du else "Cấu hình hoặc KOL chưa xong: Claude sẽ hỏi để điền, rồi dựng KOL (Bước 0).")
    print("Ngoài máy còn cần: trình duyệt có tiện ích Claude in Chrome, đã đăng nhập muse.ai.")
    sys.exit(0 if tot else 1)


if __name__ == "__main__":
    main()

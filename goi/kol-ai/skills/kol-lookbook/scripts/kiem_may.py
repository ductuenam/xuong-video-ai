"""Kiểm máy trước khi làm video lookbook: Python, thư viện, FFmpeg, cấu hình. In 'MÁY SẴN SÀNG' nếu đủ."""
import shutil, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
for s in (sys.stdout, sys.stderr):
    try: s.reconfigure(encoding="utf-8")
    except Exception: pass
loi = []
print(f"✔ Python {sys.version.split()[0]}" if sys.version_info >= (3, 9) else "✘ Cần Python 3.9 trở lên")
if sys.version_info < (3, 9): loi.append("python")
for ten, goi in (("numpy", "numpy"), ("PIL", "pillow"), ("cv2", "opencv-python")):
    try:
        __import__(ten); print(f"✔ {goi} đã có")
    except ImportError:
        loi.append(goi); print(f"✘ Thiếu {goi}: chạy  python -m pip install {goi}")
for ct in ("ffmpeg", "ffprobe"):
    if shutil.which(ct): print(f"✔ {ct} đã có")
    else: loi.append(ct); print(f"✘ Thiếu {ct}: chạy  winget install Gyan.FFmpeg  rồi mở lại Claude")
try:
    from chung import cau_hinh, GOC
    if not (GOC / "cau-hinh.json").is_file(): print("! Chưa có cau-hinh.json — đang dùng mẫu; Claude sẽ hỏi anh chị để điền")
    ch = cau_hinh()
    for k in ("thu_muc_du_an", "thu_muc_tam", "kho_thanh_pham", "thu_muc_nhac"):
        Path(ch[k]).mkdir(parents=True, exist_ok=True); print(f"✔ {k}: {ch[k]}")
    if not Path(ch["thu_muc_tai_ve"]).is_dir(): loi.append("tai_ve"); print(f"✘ Không thấy thư mục tải về: {ch['thu_muc_tai_ve']}")
    else: print(f"✔ thu_muc_tai_ve: {ch['thu_muc_tai_ve']}")
except Exception as e:
    loi.append("cau_hinh"); print(f"✘ Lỗi đọc cấu hình: {e}")
print("\nMÁY SẴN SÀNG" if not loi else f"\nCHƯA SẴN SÀNG: còn thiếu {', '.join(loi)}")
sys.exit(1 if loi else 0)

"""Phần dùng chung: đọc cấu hình và dự án, gọi ffmpeg, in tiếng Việt không lỗi."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GOC_SKILL = Path(__file__).resolve().parent.parent


def in_utf8():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass


def doc_cau_hinh(duong_dan=None):
    """Tìm cau-hinh.json theo thứ tự: tham số, biến CAY_CANH_CAU_HINH, thư mục skill."""
    for p in (duong_dan, os.environ.get("CAY_CANH_CAU_HINH"), GOC_SKILL / "cau-hinh.json"):
        if p and Path(p).is_file():
            return json.loads(Path(p).read_text(encoding="utf-8")), Path(p)
    return None, None


def doc_du_an(thu_muc):
    """Một dự án = một thư mục có du-an.json. Trả (thư mục, nội dung)."""
    d = Path(thu_muc)
    f = d / "du-an.json" if d.is_dir() else d
    if not f.is_file():
        sys.exit(f"Không thấy du-an.json trong {thu_muc}. Chép mẫu từ {GOC_SKILL / 'du-an.mau.json'}.")
    return f.parent, json.loads(f.read_text(encoding="utf-8"))


def ten_canh(c):
    return f"{c['ma']}-{c['ten']}"


def can(cmd):
    """Kiểm ffmpeg/ffprobe có trên máy."""
    if not shutil.which(cmd):
        sys.exit(f"Không tìm thấy {cmd}. Windows: winget install Gyan.FFmpeg rồi mở lại cửa sổ lệnh.")
    return cmd


def chay(args, **kw):
    """Chạy lệnh, không bao giờ chờ bàn phím (tránh treo)."""
    return subprocess.run(args, stdin=subprocess.DEVNULL, **kw)


def thoi_luong(path):
    r = chay([can("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
             capture_output=True, text=True)
    try:
        return float(r.stdout.strip())
    except ValueError:
        return 0.0

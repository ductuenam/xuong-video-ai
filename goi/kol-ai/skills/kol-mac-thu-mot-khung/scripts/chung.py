"""Phần dùng chung: đọc cau-hinh.json, in tiếng Việt không lỗi, chạy lệnh không treo."""
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


def doc_cau_hinh(duong_dan=None, bat_buoc=True):
    """Tìm cau-hinh.json theo thứ tự: tham số, biến KOL_CAU_HINH, thư mục skill."""
    for p in (duong_dan, os.environ.get("KOL_CAU_HINH"), GOC_SKILL / "cau-hinh.json"):
        if p and Path(p).is_file():
            return json.loads(Path(p).read_text(encoding="utf-8"))
    if bat_buoc:
        sys.exit(f"Chưa có cau-hinh.json. Chép {GOC_SKILL / 'cau-hinh.mau.json'} thành cau-hinh.json rồi điền.")
    return None


def thu_muc(cfg, khoa):
    """Đọc một đường dẫn thư mục trong cấu hình, trả Path."""
    v = (cfg or {}).get(khoa, "")
    if not v:
        sys.exit(f"cau-hinh.json chưa có mục {khoa}.")
    return Path(os.path.expandvars(os.path.expanduser(v)))


def can(cmd):
    if not shutil.which(cmd):
        sys.exit(f"Không tìm thấy {cmd}. Windows: winget install Gyan.FFmpeg rồi mở lại cửa sổ lệnh.")
    return cmd


def chay(args, **kw):
    """Chạy lệnh, không bao giờ chờ bàn phím (tránh treo)."""
    return subprocess.run(args, stdin=subprocess.DEVNULL, **kw)

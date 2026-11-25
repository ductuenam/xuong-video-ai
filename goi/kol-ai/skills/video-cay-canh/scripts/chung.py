"""Phần dùng chung: đọc cấu hình và dự án, gọi ffmpeg, in tiếng Việt không lỗi."""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GOC_SKILL = Path(__file__).resolve().parent.parent


def cau_hinh_xuong():
    """Đọc <bộ não>/.claude/xuong-video.json do bộ cài ghi: từ thư mục skill đi lên, rồi từ thư mục đang mở đi lên.
    Thêm thư mục ffmpeg, node của xưởng vào đầu PATH của tiến trình này."""
    for goc in (Path(__file__).resolve(), Path.cwd().resolve()):
        for p in (goc, *goc.parents):
            f = p / ".claude" / "xuong-video.json"
            if f.is_file():
                c = json.loads(f.read_text(encoding="utf-8"))
                for d in reversed(c.get("bin", [])):
                    if d and d not in os.environ.get("PATH", "").split(os.pathsep):
                        os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
                return c
    return {}


XUONG = cau_hinh_xuong()


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
            cfg = json.loads(Path(p).read_text(encoding="utf-8"))
            # thu_muc_lam_viec để trống hoặc còn là chữ mẫu "<...>" → <xưởng>/du-an/video-cay-canh khi có xưởng
            lv = str(cfg.get("thu_muc_lam_viec") or "").strip()
            if XUONG.get("xuong") and (not lv or lv.startswith("<")):
                cfg["thu_muc_lam_viec"] = str(Path(XUONG["xuong"]) / "du-an" / "video-cay-canh")
            return cfg, Path(p)
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

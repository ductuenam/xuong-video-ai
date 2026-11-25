"""Phần dùng chung: đọc cau-hinh.json, in tiếng Việt không lỗi, chạy lệnh không treo."""
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


def _mac_dinh_thu_muc(cfg):
    """Mục thư mục để trống thì lấy mặc định: <xưởng>/du-an/<tên skill>/video|kol|kho khi có xưởng, không thì chỗ cũ."""
    x = XUONG.get("xuong")
    goc = Path(x) / "du-an" / GOC_SKILL.name if x else Path("kol-mac-thu")
    for k, ten in (("thu_muc_lam_viec", "video"), ("thu_muc_kol", "kol"), ("thu_muc_kho", "kho")):
        if not cfg.get(k):
            cfg[k] = str(goc / ten)
    return cfg


def doc_cau_hinh(duong_dan=None, bat_buoc=True):
    """Tìm cau-hinh.json theo thứ tự: tham số, biến KOL_CAU_HINH, thư mục skill."""
    for p in (duong_dan, os.environ.get("KOL_CAU_HINH"), GOC_SKILL / "cau-hinh.json"):
        if p and Path(p).is_file():
            return _mac_dinh_thu_muc(json.loads(Path(p).read_text(encoding="utf-8")))
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

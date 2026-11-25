"""Tìm bộ não thứ hai (Second Brain) của người dùng trên máy, khi Claude KHÔNG có công cụ sb_search (24/11/2026).

  python tim_bo_nao.py            in JSON: {"loai": ..., "duong_dan": ..., "thu_muc_kenh": ...}

Nhận 2 kiểu:
  - "khoi-dong": Bộ Não AI Khởi Động (thư mục có INDEX.md và 01_CA_NHAN_VA_THUONG_HIEU/, ngăn 01–06).
  - "obsidian": kho Obsidian (thư mục có .obsidian/).
Tìm theo thứ tự: thư mục đang mở và các thư mục cha, rồi Desktop, Documents, Downloads, OneDrive, rồi gốc ổ D:, E:, F:
(sâu tối đa 3 cấp). Không tìm thấy thì loai = null.
thu_muc_kenh: chỗ để làm video, NẰM NGOÀI bộ não (<thư mục cha của bộ não>/Video-AI) để không xả du-an/ vào các ngăn.
Chỉ đọc, không ghi gì.
"""
import json
import os
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BO_QUA = {"node_modules", ".git", "AppData", "Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin",
          "System Volume Information", ".cache", "ProgramData"}


def loai(p: Path):
    try:
        if (p / "INDEX.md").is_file() and (p / "01_CA_NHAN_VA_THUONG_HIEU").is_dir():
            return "khoi-dong"
        if (p / ".obsidian").is_dir():
            return "obsidian"
    except OSError:
        pass
    return None


def quet(goc: Path, sau: int, thay: list):
    """Gom mọi bộ não trong goc (sâu tối đa `sau` cấp) vào `thay`; không chui vào bên trong một bộ não."""
    try:
        if sau < 0 or not goc.is_dir():
            return
    except OSError:
        return
    k = loai(goc)
    if k:
        thay.append((k, goc))
        return
    try:
        con = sorted(x for x in goc.iterdir() if x.is_dir() and x.name not in BO_QUA and not x.name.startswith(("$", ".")))
    except OSError:
        return
    for c in con:
        quet(c, sau - 1, thay)


def tim():
    cwd = Path.cwd().resolve()
    for p in [cwd, *cwd.parents]:
        k = loai(p)
        if k:
            return k, p
    nha = Path.home()
    cho = [nha / "Desktop", nha / "Documents", nha / "Downloads"]
    cho += sorted(nha.glob("OneDrive*"))
    # Thư mục cá nhân trước; thấy bộ não ở đó thì dùng luôn, KHÔNG lục sang ổ khác (thử 24/11/2026: máy có bản bộ não
    # thử nghiệm ở ổ khác bị chọn nhầm thay cho Second Brain thật trong Documents). Ưu tiên Bộ Não Khởi Động hơn Obsidian.
    for nhom in (cho, [Path(f"{o}:/") for o in "DEF" if os.path.exists(f"{o}:/")]):
        thay = []
        for c in nhom:
            quet(c, 3, thay)
        if thay:
            kd = [r for r in thay if r[0] == "khoi-dong"]
            return kd[0] if kd else thay[0]
    return None, None


if __name__ == "__main__":
    k, p = tim()
    out = {"loai": k, "duong_dan": str(p) if p else None,
           "thu_muc_kenh": str(p.parent / "Video-AI") if p else None}
    print(json.dumps(out, ensure_ascii=False))

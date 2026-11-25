"""Đọc cấu hình máy khách (cau-hinh.json cạnh SKILL.md). Mọi đường dẫn trong gói lấy từ đây, không ghi cứng.

cau-hinh.json (tạo từ cau-hinh.mau.json khi cài):
  thu_muc_du_an   : nơi mỗi video một thư mục con (để trống = <xưởng>/du-an/kol-lookbook/du-an)
  thu_muc_tai_ve  : thư mục trình duyệt tự lưu tệp tải về (nơi có goi-muse-*.bin)
  thu_muc_tam     : nơi ghi khung soi, tờ soát (nên ở ổ có nhiều chỗ trống, KHÔNG để ổ C nếu ổ C nhỏ)
  kho_thanh_pham  : nơi lưu video đạt kèm clip gốc
  thu_muc_nhac    : nơi anh chị để nhạc có quyền dùng
"""
import json
import os
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


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


def cau_hinh():
    p = GOC / "cau-hinh.json"
    if not p.is_file():
        p = GOC / "cau-hinh.mau.json"
    ch = json.loads(p.read_text(encoding="utf-8"))
    # Mục để trống: mặc định <xưởng>/du-an/kol-lookbook/<mục> khi có xưởng, không thì ~/KOL-LOOKBOOK/<mục> (cách cũ)
    x = XUONG.get("xuong")
    goc = Path(x) / "du-an" / "kol-lookbook" if x else Path.home() / "KOL-LOOKBOOK"
    for k, ten in (("thu_muc_tam", "tam"), ("kho_thanh_pham", "kho"), ("thu_muc_du_an", "du-an"), ("thu_muc_nhac", "nhac")):
        ch[k] = str(Path(ch.get(k) or (goc / ten)).expanduser())
    ch["thu_muc_tai_ve"] = str(Path(ch.get("thu_muc_tai_ve") or (Path.home() / "Downloads")).expanduser())
    return ch

"""Đọc cấu hình máy khách (cau-hinh.json cạnh SKILL.md). Mọi đường dẫn trong gói lấy từ đây, không ghi cứng.

cau-hinh.json (tạo từ cau-hinh.mau.json khi cài):
  thu_muc_du_an   : nơi mỗi video một thư mục con (ví dụ D:/KOL-LOOKBOOK)
  thu_muc_tai_ve  : thư mục trình duyệt tự lưu tệp tải về (nơi có goi-muse-*.bin)
  thu_muc_tam     : nơi ghi khung soi, tờ soát (nên ở ổ có nhiều chỗ trống, KHÔNG để ổ C nếu ổ C nhỏ)
  kho_thanh_pham  : nơi lưu video đạt kèm clip gốc
  thu_muc_nhac    : nơi anh chị để nhạc có quyền dùng
"""
import json
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent


def cau_hinh():
    p = GOC / "cau-hinh.json"
    if not p.is_file():
        p = GOC / "cau-hinh.mau.json"
    ch = json.loads(p.read_text(encoding="utf-8"))
    for k in ("thu_muc_tam", "thu_muc_tai_ve", "kho_thanh_pham", "thu_muc_du_an", "thu_muc_nhac"):
        ch[k] = str(Path(ch.get(k) or (Path.home() / "KOL-LOOKBOOK" / k)).expanduser())
    return ch

"""Tạo trang nhắc lời từ loi-thoai.txt để đọc khi quay. Mở trên máy tính hoặc điện thoại, chạm để sang câu.
  python nhac_loi.py <thư mục dự án>"""
import json
import re
import sys
from pathlib import Path

da = Path(sys.argv[1])
cau = [x.strip() for x in (da / "loi-thoai.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
mau = (Path(__file__).resolve().parent.parent / "references" / "nhac-loi.mau.html").read_text(encoding="utf-8")
(da / "nhac-loi.html").write_text(mau.replace("/*CAU*/[]", json.dumps(cau, ensure_ascii=False, indent=0)), encoding="utf-8")
print("xong", da / "nhac-loi.html", len(cau), "câu")

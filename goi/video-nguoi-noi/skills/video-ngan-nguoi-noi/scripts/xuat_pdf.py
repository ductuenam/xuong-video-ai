"""Xuất tờ hướng dẫn HTML thành PDF giữ nguyên màu, liên kết bấm được, và ảnh xem trước từng trang để soát.
  python xuat_pdf.py <file.html> <file.pdf> [--noi-bo]
Tờ hướng dẫn gửi người xem phải có khối lien-he; --noi-bo chỉ dùng cho tài liệu nội bộ như sổ tay bàn giao."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
vao, ra = Path(sys.argv[1]).resolve(), Path(sys.argv[2]).resolve()
_html = vao.read_text(encoding="utf-8")
# Tờ gửi người xem bắt buộc có liên hệ; tài liệu nội bộ như sổ tay bàn giao thì thêm --noi-bo
if "--noi-bo" not in sys.argv and 'class="lien-he"' not in _html or "SO_ZALO" in _html or "TÊN KÊNH" in _html:
    sys.exit("✘ Tờ hướng dẫn thiếu khối lien-he hoặc còn chữ mẫu. Điền theo lienHe và ten trong hồ sơ kênh.")
with sync_playwright() as p:
    b = p.chromium.launch()
    tr = b.new_page(viewport={"width": 794, "height": 1123})
    tr.goto(vao.as_uri(), wait_until="networkidle", timeout=60000)
    tr.evaluate("document.fonts.ready")
    tran = tr.evaluate("[...document.querySelectorAll('.trang')].map(e=>e.scrollHeight-e.clientHeight)")
    if any(n > 1 for n in tran):
        print("✘ Trang bị tràn, số pixel từng trang:", tran)
    tr.pdf(path=str(ra), format="A4", print_background=True, prefer_css_page_size=True)
    tr.screenshot(path=str(ra.with_suffix(".xem-truoc.png")), full_page=True)
    b.close()
print("xong", ra)

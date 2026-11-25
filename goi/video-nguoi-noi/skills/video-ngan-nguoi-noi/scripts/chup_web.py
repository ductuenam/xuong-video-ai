"""Chụp hoặc quay trang web công khai để làm hình minh họa. Trình duyệt riêng, không đăng nhập, không dùng tài khoản của ai.
  python chup_web.py <thư mục dự án> <url> <tên> [--quay 8] [--cuon 900] [--den-chu "chữ cần cuộn tới"] [--ngang 1080] [--cao 1350]
Ra public/web/<tên>.png, hoặc public/web/<tên>.mp4 khi có --quay (số giây, trang tự cuộn chậm).
Cần: pip install playwright, rồi: python -m playwright install chromium"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ap = argparse.ArgumentParser()
ap.add_argument("du_an")
ap.add_argument("url")
ap.add_argument("ten")
ap.add_argument("--quay", type=float)
ap.add_argument("--cuon", type=int, default=900, help="số pixel cuộn khi quay")
ap.add_argument("--den-chu", help="cuộn tới chữ này trước khi chụp hoặc quay")
ap.add_argument("--tim", nargs="*", default=[], help="in toạ độ các chữ này, dùng cho khoanh của man-web")
ap.add_argument("--ngang", type=int, default=1080)
ap.add_argument("--cao", type=int, default=1350)
ap.add_argument("--cho", type=float, default=2.0, help="giây chờ sau khi cuộn: trang có chữ hiện dần khi cuộn tới thì chụp ngay sẽ mờ (21-story-cutter)")
a = ap.parse_args()
ra = Path(a.du_an) / "public" / "web"
ra.mkdir(parents=True, exist_ok=True)
tam = tempfile.mkdtemp()
with sync_playwright() as p:
    b = p.chromium.launch()
    khung = {"width": a.ngang, "height": a.cao}
    ctx = b.new_context(viewport=khung, device_scale_factor=1 if a.quay else 2, locale="en-US", **({"record_video_dir": tam, "record_video_size": khung} if a.quay else {}))
    tr = ctx.new_page()
    tr.goto(a.url, wait_until="domcontentloaded", timeout=60000)
    try:
        tr.wait_for_load_state("networkidle", timeout=15000)
    except Exception:
        pass
    for nhan in ("Reject All", "Reject all", "Decline", "Từ chối tất cả"):  # bảng cookie che hình; chọn từ chối cookie không cần thiết
        nut = tr.get_by_role("button", name=nhan)
        if nut.count():
            nut.first.click(timeout=3000)
            tr.wait_for_timeout(500)
            break
    if a.den_chu:
        e = tr.get_by_text(a.den_chu, exact=False).first
        e.scroll_into_view_if_needed(timeout=10000)
        tr.evaluate("y => window.scrollBy(0, y)", e.bounding_box()["y"] - a.cao * 0.15)  # đưa chữ lên gần đầu khung, tránh thanh menu dính
        tr.mouse.wheel(0, 1)  # một số trang chỉ bắt hiệu ứng khi có sự kiện cuộn thật
    tr.wait_for_timeout(a.cho * 1000)
    for chu in a.tim:
        e = tr.get_by_text(chu, exact=False).locator("visible=true").first
        print(chu, e.bounding_box())
    if a.quay:
        buoc = max(1, int(a.quay * 30))
        for _ in range(buoc):
            tr.mouse.wheel(0, a.cuon / buoc)
            tr.wait_for_timeout(1000 / 30)
        video = tr.video
    else:
        tr.screenshot(path=str(ra / f"{a.ten}.png"))
    ctx.close()
    if a.quay:
        goc = video.path()
    b.close()
if a.quay:
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-sseof", f"-{a.quay}", "-i", str(goc), "-an", "-r", "30", "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(ra / f"{a.ten}.mp4")], check=True)
shutil.rmtree(tam, ignore_errors=True)
print("xong", ra / (a.ten + (".mp4" if a.quay else ".png")))

"""Đổi ảnh, video của chính người dùng thành clip dọc 8 giây làm cảnh trám cho video edit (24/11/2026).

  python canh_toi.py "<dự án>" [file ...]

Không đưa file thì lấy tối đa 4 file trong <thư mục kênh>/anh-video-cua-toi/. Ghi <dự án>/public/canh/TOI1.mp4, TOI2.mp4...
In ra mã (TOI1...) để đặt vào "ten" của cảnh flow-chu trong canh.json. Ảnh tĩnh có chuyển động phóng chậm, video cắt 8 giây không tiếng.
"""
import sys
from pathlib import Path

from bni import ANH, VIDEO, clip_toi
from chung import ho_so

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
da = Path(sys.argv[1]).resolve()
kenh = Path(ho_so(da)["_goc"])
tep = [Path(x) for x in sys.argv[2:]]
if not tep:
    thu_muc = kenh / "anh-video-cua-toi"
    tep = sorted(f for f in thu_muc.glob("*") if f.suffix.lower() in ANH | VIDEO) if thu_muc.exists() else []
if not tep:
    sys.exit("• không có ảnh, video của người dùng: dùng cảnh trong kho-canh hoặc bỏ cảnh trám")
ra = da / "public" / "canh"
ra.mkdir(parents=True, exist_ok=True)
for i, f in enumerate(tep[:4], 1):
    clip_toi(f, ra / f"TOI{i}.mp4")
    print(f"TOI{i} = {f.name}")

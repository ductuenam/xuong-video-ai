"""Ghép chữ lên hình nền, xuất bìa 1080x1920.
  python lap_bia.py <thư mục dự án>
Cần: bia.json, ảnh nền trong public/, bộ công cụ video-ngan-nguoi-noi đã cài (~/.video-ngan/engine). Ra render/bia.jpg."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ENGINE = Path.home() / ".video-ngan" / "engine"
NPX = "npx.cmd" if sys.platform == "win32" else "npx"
TRUONG_KENH = ["ten", "chuLinhVat", "nhanCanhAI", "nhanAnhAI", "mauChinh", "mauPhu", "mauBia"]

da = Path(sys.argv[1]).resolve()
if not (ENGINE / "node_modules").exists():
    sys.exit(f"✘ Chưa cài engine ở {ENGINE}. Chạy cai_dat.py của video-ngan-nguoi-noi trước.")
bia = json.loads((da / "bia.json").read_text(encoding="utf-8"))
if not (da / "public" / bia["anh"]).exists():
    sys.exit(f"✘ Không thấy ảnh nền {da / 'public' / bia['anh']}")
ho_so = next((x / "ho-so-kenh.json" for x in [da, *da.parents] if (x / "ho-so-kenh.json").exists()), None)
if ho_so is None:
    sys.exit("✘ Không thấy ho-so-kenh.json ở dự án hoặc thư mục cha.")
h = json.loads(ho_so.read_text(encoding="utf-8"))
nguon = Path(__file__).resolve().parents[2] / "video-ngan-nguoi-noi" / "engine" / "src"
if nguon.exists():
    shutil.copytree(nguon, ENGINE / "src", dirs_exist_ok=True)
(ENGINE / "src" / "kenh.json").write_text(json.dumps({k: h[k] for k in TRUONG_KENH}, ensure_ascii=False), encoding="utf-8")
(da / "render").mkdir(exist_ok=True)
goi = da / "render" / "bundle-bia"
shutil.rmtree(goi, ignore_errors=True)
pub = da / "render" / "public-bia"  # chỉ chép ảnh nền, không kéo theo master nặng trong public
shutil.rmtree(pub, ignore_errors=True)
pub.mkdir()
shutil.copy2(da / "public" / bia["anh"], pub / bia["anh"])
# Remotion chép nguyên liệu vào Temp mỗi lần chạy và không tự xóa. Cho nó dùng thư mục tạm riêng của lần chạy này
# (%TEMP%\video-ngan\bia-<số>), xong thì xóa đúng thư mục đó; phiên khác dùng Temp chung không bị đụng tới.
tam = Path(tempfile.gettempdir()) / "video-ngan" / f"bia-{os.getpid()}-{int(time.time())}"
tam.mkdir(parents=True, exist_ok=True)
moi_truong = {**os.environ, "TEMP": str(tam), "TMP": str(tam), "TMPDIR": str(tam)}
ra = da / "render" / "bia.jpg"
try:
    subprocess.run([NPX, "remotion", "bundle", "src/index.ts", f"--public-dir={pub}", f"--out-dir={goi}", "--log=error"], cwd=ENGINE, check=True, env=moi_truong)
    subprocess.run([NPX, "remotion", "still", str(goi), "AnhBia", str(ra), f"--props={da / 'bia.json'}", "--image-format=jpeg", "--jpeg-quality=95", "--log=error"], cwd=ENGINE, check=True, env=moi_truong)
finally:
    shutil.rmtree(goi, ignore_errors=True)
    shutil.rmtree(pub, ignore_errors=True)
    shutil.rmtree(tam, ignore_errors=True)
print("xong", ra)

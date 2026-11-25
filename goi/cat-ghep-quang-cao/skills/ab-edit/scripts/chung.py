"""Hàm dùng chung cho skill ab-edit (Windows): đường dẫn, FFmpeg, thương hiệu, luật an toàn file."""
import json
import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
CFG = json.loads((SKILL / "config.json").read_text(encoding="utf-8"))
STUDIO = Path(os.environ.get("AVS_STUDIO", CFG["studio"]))
SOURCE_THO = STUDIO / "02-source-tho"
TAI_NGUYEN = STUDIO / "05-tai-nguyen"
THANH_PHAM = STUDIO / "06-thanh-pham"
DU_AN = STUDIO / "07-du-an"
BACKUP = STUDIO / "_backup"
BRANDS = SKILL / "brands"

# Đuôi file KHÔNG BAO GIỜ được xoá bằng script (bài học sự cố 14/10/2026)
MEDIA_EXT = {".mp4", ".mov", ".mkv", ".mxf", ".avi", ".mp3", ".wav", ".m4a", ".aac", ".flac", ".png", ".jpg", ".jpeg", ".webp"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


def tim_ffmpeg(ten: str = "ffmpeg") -> str:
    """Tìm ffmpeg/ffprobe: PATH → lối tắt winget → thư mục gói winget."""
    p = shutil.which(ten)
    if p:
        return p
    la = Path(os.environ.get("LOCALAPPDATA", ""))
    link = la / "Microsoft" / "WinGet" / "Links" / f"{ten}.exe"
    if link.exists():
        return str(link)
    for f in (la / "Microsoft" / "WinGet" / "Packages").glob(f"Gyan.FFmpeg*/**/bin/{ten}.exe"):
        return str(f)
    raise SystemExit(f"Không tìm thấy {ten}. Cài: winget install Gyan.FFmpeg")


_NVENC = None


def ma_hoa(bitrate: str = "40M") -> list:
    """Tham số mã hoá H.264: NVENC nếu driver hỗ trợ (FFmpeg 9 cần driver NVIDIA ≥ 610), không thì libx264 (CPU)."""
    global _NVENC
    if _NVENC is None:
        r = subprocess.run([tim_ffmpeg(), "-v", "error", "-f", "lavfi", "-i", "color=black:s=256x256:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"],
                           capture_output=True)
        _NVENC = r.returncode == 0
    if _NVENC:
        return ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-b:v", bitrate, "-pix_fmt", "yuv420p"]
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p"]


def doc_brand(ten_hoac_file: str | None = None) -> dict:
    """Đọc brands/<tên>.json (hoặc đường dẫn file). Khoá bắt đầu bằng _ là ghi chú."""
    ten = ten_hoac_file or CFG.get("brand_mac_dinh", "_mau")
    p = Path(ten)
    if not p.exists():
        p = BRANDS / (ten if ten.endswith(".json") else f"{ten}.json")
    if not p.exists():
        raise SystemExit(f"Không thấy thương hiệu: {ten_hoac_file}. Có: {', '.join(x.stem for x in BRANDS.glob('*.json'))}")
    return json.loads(p.read_text(encoding="utf-8"))


def thoi_luong(file: Path) -> float:
    out = subprocess.run(
        [tim_ffmpeg("ffprobe"), "-v", "error", "-show_entries", "format=duration", "-of", "json", str(file)],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out)["format"]["duration"])


def chan_ghi_source(file: Path) -> None:
    """Không bao giờ ghi/xoá trong 02-source-tho."""
    f = Path(file).resolve()
    if f == SOURCE_THO.resolve() or SOURCE_THO.resolve() in f.parents:
        raise SystemExit(f"Từ chối: không được ghi vào 02-source-tho ({f.name}).")


def sao_luu(file: Path) -> None:
    """Sao lưu bản cũ vào _backup trước khi ghi đè."""
    file = Path(file)
    if file.exists() and file.is_file():
        BACKUP.mkdir(parents=True, exist_ok=True)
        dich = BACKUP / f"{datetime.now():%Y%m%d_%H%M%S}_{file.name}"
        shutil.copy2(file, dich)


def xoa_tam(file: Path) -> None:
    """Chỉ xoá file tạm KHÔNG phải media; media thì giữ lại (dồn vào _backup)."""
    file = Path(file)
    chan_ghi_source(file)
    if not file.exists():
        return
    if file.suffix.lower() in MEDIA_EXT:
        sao_luu(file)
    file.unlink()

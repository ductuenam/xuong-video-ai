"""Đọc kho nhạc, tiếng của xưởng (tai-nguyen/nhac|am/chi-muc.csv), dùng chung cho tron_am.py, bni.py, kiem_chot.py, them_am.py.
Một nguồn luật: references/tu-dien-am.json (từ tâm trạng, giấy phép dùng được). Dòng của kho chung và của học viên
(chu=hoc-vien, nằm ở cua-toi/) đọc như nhau; dòng trang_thai=an bị bỏ qua.
Gọi một bài, một tiếng bằng mã (NH0004, UAM0001), bằng phần mô tả trong tên tệp (dong-xu-roi-nay) hoặc tên tệp không đuôi."""
import csv
import json
import re
import subprocess
from pathlib import Path

TU_DIEN = json.loads((Path(__file__).resolve().parent.parent / "references" / "tu-dien-am.json").read_text(encoding="utf-8"))
TAM_TRANG = TU_DIEN["tam_trang"]
GOP = TU_DIEN["gop"]
QUYEN_DUNG = set(TU_DIEN["giay_phep_dung_duoc"])


def _xuong():
    try:
        from chung import XUONG
        return XUONG
    except Exception:  # noqa: BLE001 - máy chưa cài xưởng
        return None


def khong_dau(s):
    import unicodedata
    s = unicodedata.normalize("NFD", (s or "").lower().replace("đ", "d"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")


def chuan_tam(s):
    """'Vui;tre-trung;Ấm áp' -> (['vui', 'am-ap'], []): đưa về từ điển, bỏ trùng, giữ thứ tự. Trả thêm các từ không hiểu."""
    duoc, la = [], []
    for x in re.split(r"[;,]", s or ""):
        k = khong_dau(x)
        if not k:
            continue
        k = k if k in TAM_TRANG else GOP.get(k, "")
        if not k:
            la.append(x.strip())
        elif k not in duoc:
            duoc.append(k)
    return duoc, la


def so(s):
    """Số đầu tiên trong ô ('0 hoặc 64' -> 0.0, '~92 (máy đo 185)' -> 92.0, '114s' -> 114.0); không có thì None."""
    m = re.search(r"-?\d+(?:[.,]\d+)?", str(s or ""))
    return float(m.group().replace(",", ".")) if m else None


def goc(loai, xuong=None):
    x = xuong or _xuong()
    return Path(x) / "tai-nguyen" / loai if x else None


def doc_chi_muc(loai, xuong=None):
    """Các dòng đang dùng, mỗi dòng thêm '_file' (Path tuyệt đối, có thể chưa tồn tại)."""
    g = goc(loai, xuong)
    if not g or not (g / "chi-muc.csv").is_file():
        return []
    with (g / "chi-muc.csv").open(encoding="utf-8-sig", newline="") as f:
        ds = [r for r in csv.DictReader(f) if (r.get("ma") or "").strip() and (r.get("trang_thai") or "dung").strip() != "an"]
    for r in ds:
        r["_file"] = g / (r.get("tep") or "")
    return ds


def tim(loai, ten, xuong=None):
    """Tìm theo mã, mô tả trong tên tệp hoặc tên tệp. Không thấy thì None."""
    t = (ten or "").strip()
    if not t:
        return None
    tk = khong_dau(Path(t).stem)
    for r in doc_chi_muc(loai, xuong):
        stem = Path(r.get("tep") or "").stem
        mo_ta = stem.split("_", 1)[1] if "_" in stem else ""
        if t.upper() == r["ma"].upper() or tk in (khong_dau(stem), mo_ta):
            return r
    return None


def theo_tep(loai, p, xuong=None):
    """Dòng chỉ mục của một tệp (theo mã đứng đầu tên tệp, ví dụ AM0004_...), để lấy điểm nhấn của tiếng khai trong hồ sơ."""
    m = re.match(r"(U?[A-Z]{2}\d{4})_", Path(p).name)
    return tim(loai, m.group(1), xuong) if m else None


def do_dai(p):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                           capture_output=True, text=True, timeout=30)
        return float(r.stdout.strip())
    except (OSError, ValueError, subprocess.SubprocessError):
        return None


def het_tieng(p, duoi_db=12):
    """Giây cuối còn nghe rõ của một bài (bỏ đuôi tắt dần, đuôi im), đo độ to từng 0,1 giây (cửa sổ 0,4 giây) bằng ffmpeg ebur128.
    Dùng khi nối vòng bài ngắn: nối phần có tiếng, không nối cả đuôi im (bài spa 67 giây từng hụt 3 giây câm ở chỗ nối)."""
    try:
        # ffmpeg 8 chỉ in dòng đo từng 0,1 giây khi mức log là verbose
        e = subprocess.run(["ffmpeg", "-nostdin", "-hide_banner", "-v", "verbose", "-i", str(p), "-vn", "-af", "ebur128=framelog=verbose", "-f", "null", "-"],
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120).stderr
    except (OSError, subprocess.SubprocessError):
        return None
    tm = [(float(a), float(b)) for a, b in re.findall(r"t:\s*([\d.]+)\s+TARGET.*?M:\s*(-?[\d.]+)", e)]
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", e)
    if not tm or not i:
        return None
    nguong = float(i[-1]) - duoi_db
    to = [t for t, m in tm if m >= nguong]
    return min(tm[-1][0], to[-1] + 0.3) if to else None


def giay_cua(r):
    """Độ dài (giây) của một dòng: cột giay, rồi phần '95s' trong thong_so ('128kbps;95s'), cuối cùng đo tệp."""
    g = so(r.get("giay"))
    if g:
        return g
    m = re.search(r"(\d+(?:\.\d+)?)s(?![a-z])", r.get("thong_so") or "")
    return float(m.group(1)) if m else do_dai(r["_file"]) if r.get("_file") else None


def quyen(r):
    """'' nếu được dùng trong video đăng công khai, ngược lại là lý do."""
    gp = khong_dau(r.get("giay_phep"))
    if gp in QUYEN_DUNG:
        return ""
    return f"giấy phép '{r.get('giay_phep') or 'trống'}' chưa rõ quyền dùng (chỉ nhận: {', '.join(sorted(QUYEN_DUNG))})"

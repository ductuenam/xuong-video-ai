"""Phần dùng chung: tìm hồ sơ kênh, đường dẫn engine, chạy lệnh ngoài."""
import contextlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
GOC_SKILL = Path(__file__).resolve().parent.parent
THU_MUC_MAY = Path.home() / ".video-ngan"
ENGINE = THU_MUC_MAY / "engine"


def kiem_so_dong(canh, so_dong):
    """Kiểm số dòng trong canh.json: tu = dòng đầu của cảnh (đếm từ 1, 0 là đầu video), den = dòng đầu của cảnh sau.
    Bắt cảnh hở hoặc chồng nhau, và mốc ghi bằng số dòng nằm ngoài cảnh. Lệch đều cả bài một dòng thì không bắt được:
    xem cột "dòng … «câu đầu»" lap_canh.py in ra cạnh chữ trên hình. Trả về danh sách lỗi."""
    sai = []
    for k, x in enumerate(canh):
        dau, sau = max(1, x["tu"]), (so_dong + 1 if x["den"] == "het" else x["den"])
        if k + 1 < len(canh) and x["den"] != canh[k + 1]["tu"]:
            sai.append(f"cảnh {k + 1} ({x['loai']}) den={x['den']} nhưng cảnh sau tu={canh[k + 1]['tu']}")
        for m in x.get("moc", []) + ([x["at"]] if "at" in x else []):
            dong = m[0] if isinstance(m, list) else (m if isinstance(m, int) and not isinstance(m, bool) and m > 0 else None)
            if dong is not None and not (dau <= dong < sau):
                sai.append(f"cảnh {k + 1} ({x['loai']}, dòng {dau} đến {sau - 1}) có mốc dòng {dong} nằm ngoài cảnh")
    return sai


def _dung_luong(p):
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


@contextlib.contextmanager
def tam_rieng():
    """Remotion chép nguyên liệu vào thư mục Temp mỗi lần dựng và không tự xóa (đo 08/11/2026: 325 thư mục, 24 GB).
    Trỏ TEMP của các lệnh con vào %TEMP%\\video-ngan\\<lần chạy>, xong thì xóa đúng thư mục đó.
    Chỉ đụng vào thư mục của chính mình: lần dựng khác, phiên khác (video quần áo...) dùng Temp chung, không bị ảnh hưởng.
    Đường dẫn ở ổ hệ thống, chữ không dấu, vì Chrome của Remotion có thể lỗi với đường dẫn có dấu."""
    goc = Path(os.environ.get("VIDEO_NGAN_TEMP_GOC") or tempfile.gettempdir()) / "video-ngan"
    goc.mkdir(parents=True, exist_ok=True)
    for cu in goc.iterdir():  # sót lại từ lần chạy bị ngắt giữa chừng, quá 6 giờ
        try:
            if time.time() - cu.stat().st_mtime > 6 * 3600:
                shutil.rmtree(cu, ignore_errors=True)
        except OSError:
            pass
    tam = goc / f"{os.getpid()}-{int(time.time())}"
    tam.mkdir()
    cu_env = {k: os.environ.get(k) for k in ("TEMP", "TMP", "TMPDIR")}
    os.environ.update({"TEMP": str(tam), "TMP": str(tam), "TMPDIR": str(tam), "VIDEO_NGAN_TEMP_GOC": str(goc.parent)})
    try:
        yield tam
    finally:
        for k, v in cu_env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        mb = _dung_luong(tam) / 2 ** 20
        shutil.rmtree(tam, ignore_errors=True)
        print(f"(dọn thư mục tạm {mb:.0f} MB{'' if not tam.exists() else ', còn sót: ' + str(tam)})")


def doc(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ghi(p, x, thut=None):
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=thut), encoding="utf-8")


def ho_so(du_an):
    """Tìm ho-so-kenh.json ở thư mục dự án hoặc các thư mục cha."""
    d = Path(du_an).resolve()
    for x in [d, *d.parents]:
        f = x / "ho-so-kenh.json"
        if f.exists():
            h = doc(f)
            h["_goc"] = str(x)
            return h
    sys.exit(f"✘ Không thấy ho-so-kenh.json ở {d} hoặc thư mục cha. Chạy cai_dat.py để tạo.")


def duong_dan(h, gia_tri):
    """Đường dẫn trong hồ sơ có thể tuyệt đối hoặc tính từ thư mục chứa hồ sơ."""
    p = Path(gia_tri)
    return p if p.is_absolute() else Path(h["_goc"]) / p


def chay(cmd, **k):
    return subprocess.run([str(x) for x in cmd], check=True, **k)


def ffmpeg_ma_hoa():
    """h264_nvenc khi có GPU NVIDIA dùng được, không thì libx264."""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.1", "-c:v", "h264_nvenc", "-f", "null", "-"], capture_output=True)
    if r.returncode == 0:
        return ["-c:v", "h264_nvenc", "-preset", "p6", "-rc", "vbr", "-b:v", "30M"]
    return ["-c:v", "libx264", "-preset", "medium", "-crf", "14"]

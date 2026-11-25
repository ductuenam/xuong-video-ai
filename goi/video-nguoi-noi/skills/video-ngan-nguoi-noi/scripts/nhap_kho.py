"""Tự nhận gói KHO-HOC-VIEN (cảnh AI không người, nhạc, tiếng hiệu ứng) cho thư mục kênh (24/11/2026).

  python nhap_kho.py "<thư mục kênh>" ["<đường dẫn gói zip hoặc thư mục KHO-HOC-VIEN>"]

Tìm KHO-HOC-VIEN*.zip hoặc thư mục KHO-HOC-VIEN: chỗ hay để trước, rồi lục sâu thư mục cá nhân và ổ D: trở đi.
Kho cảnh của kênh còn trống thì giải nén kho-canh/ và tai-nguyen/ vào thư mục kênh (không ghi đè tệp đã có),
rồi điền boNhac, boTieng, nhac, tiengChuyenCanh vào ho-so-kenh.json nếu các mục đó còn trống hoặc trỏ tới file không có.
Không thấy gói thì im lặng bỏ qua: bni.py, tron_am.py vẫn chạy được (nền màu tự tạo, chỉ có giọng)."""
import json
import shutil
import sys
import zipfile
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NHAC = ("beat-vlog", "phonk", "future-bass")
TIENG = ("luot", "luot-manh", "hien-the", "thong-bao", "chup", "nhieu", "thanh-cong")


BO_QUA = {"node_modules", ".git", "AppData", "Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin",
          "System Volume Information", "kho-canh", "du-an", ".cache", ".video-ngan", ".claude"}


def la_goi(p: Path):
    """Gói zip KHO-HOC-VIEN*.zip (kể cả "KHO-HOC-VIEN (1).zip" trình duyệt tự đổi tên), hoặc thư mục đã giải nén."""
    if p.is_file() and p.name.upper().startswith("KHO-HOC-VIEN") and p.suffix.lower() == ".zip":
        return p
    if p.is_dir() and p.name.upper().startswith("KHO-HOC-VIEN"):
        for g in (p, p / "KHO-HOC-VIEN"):  # giải nén kiểu "mỗi zip một thư mục" thì bị lồng 2 lớp
            if (g / "kho-canh").is_dir():
                return g
    return None


def quet(goc: Path, sau: int):
    try:
        con = list(goc.iterdir())
    except OSError:
        return []
    ra = [g for g in (la_goi(x) for x in con) if g]
    if sau > 0:
        for x in sorted(con):
            try:
                if x.is_dir() and x.name not in BO_QUA and not x.name.startswith(("$", ".")) and not la_goi(x):
                    ra += quet(x, sau - 1)
            except OSError:
                pass
    return ra


def tim_goi(kenh: Path):
    """Tìm gói ở chỗ hay để trước (thư mục kênh, cạnh bộ não, Downloads, Desktop, Documents), rồi lục sâu các thư mục
    cá nhân (4 cấp) và gốc ổ D:..H: (3 cấp). Học viên để gói ở đâu cũng thấy (thử 24/11/2026). Lấy bản mới nhất."""
    import os
    nha = Path.home()
    for cho in (kenh, kenh.parent, nha / "Downloads", nha / "Desktop", nha / "Documents"):
        if cho.is_dir():
            thay = quet(cho, 0)
            if thay:
                return max(thay, key=lambda f: f.stat().st_mtime)
    thay = []
    for cho in [nha / "Downloads", nha / "Desktop", nha / "Documents", nha / "Videos", *sorted(nha.glob("OneDrive*"))]:
        if cho.is_dir():
            thay += quet(cho, 4)
    if not thay:
        for o in "DEFGH":
            if os.path.exists(f"{o}:/"):
                thay += quet(Path(f"{o}:/"), 3)
    return max(thay, key=lambda f: f.stat().st_mtime) if thay else None


def kho_trong(kenh: Path):
    k = kenh / "kho-canh"
    return not k.is_dir() or not any(k.rglob("*.mp4"))


def nhap(kenh, goi=None) -> bool:
    kenh = Path(kenh)
    if not kho_trong(kenh):
        dien_ho_so(kenh)
        return False
    goi = la_goi(Path(goi)) if goi else tim_goi(kenh)
    if goi is None:
        print("⚠ chưa thấy gói KHO-HOC-VIEN.zip trên máy: video vẫn làm được (nền màu, chưa có nhạc). Có gói thì hỏi người dùng "
              f"để ở đâu rồi chạy: python nhap_kho.py \"{kenh}\" \"<đường dẫn gói>\"")
        return False
    print(f"• thấy gói kho {goi}: đang chép cảnh, nhạc vào {kenh} (vài phút lần đầu)")
    if goi.is_dir():
        for x in ("kho-canh", "tai-nguyen"):
            if (goi / x).is_dir():
                shutil.copytree(goi / x, kenh / x, dirs_exist_ok=True)
    else:
        with zipfile.ZipFile(goi) as z:
            for ten in z.namelist():
                if ten.endswith("/") or ".." in ten:
                    continue
                phan = ten.split("/", 1)[1] if ten.startswith("KHO-HOC-VIEN/") else ten
                if not phan.startswith(("kho-canh/", "tai-nguyen/")):
                    continue
                dich = kenh / phan
                if dich.exists():
                    continue
                dich.parent.mkdir(parents=True, exist_ok=True)
                with z.open(ten) as nguon, open(dich, "wb") as ra:
                    shutil.copyfileobj(nguon, ra)
    dien_ho_so(kenh)
    so = sum(1 for _ in (kenh / "kho-canh").rglob("*.mp4"))
    print(f"✔ đã nhận kho: {so} cảnh không người, nhạc {', '.join(NHAC)}")
    return True


def dien_ho_so(kenh: Path):
    f = kenh / "ho-so-kenh.json"
    if not f.exists():
        return
    h = json.loads(f.read_text(encoding="utf-8"))
    co = lambda p: bool(p) and (kenh / p).is_file()  # noqa: E731
    doi = False
    bo_nhac = h.get("boNhac") or {}
    for n in NHAC:
        p = f"tai-nguyen/nhac/{n}.mp3"
        if n not in bo_nhac and co(p):
            bo_nhac[n] = {"file": p, "tu": 9.5} if n == "future-bass" else p
            doi = True
    bo_tieng = h.get("boTieng") or {}
    for t in TIENG:
        p = f"tai-nguyen/am/{t}.wav"
        if t not in bo_tieng and co(p):
            bo_tieng[t] = p
            doi = True
    if not co(h.get("nhac")) and co("tai-nguyen/nhac/beat-vlog.mp3"):
        h["nhac"] = "tai-nguyen/nhac/beat-vlog.mp3"
        doi = True
    if not co(h.get("tiengChuyenCanh")) and co("tai-nguyen/am/luot.wav"):
        h["tiengChuyenCanh"] = "tai-nguyen/am/luot.wav"
        doi = True
    if doi:
        h["boNhac"], h["boTieng"] = bo_nhac, bo_tieng
        f.write_text(json.dumps(h, ensure_ascii=False, indent=2), encoding="utf-8")
        print("✔ hồ sơ kênh: đã khai nhạc và tiếng hiệu ứng từ kho")


if __name__ == "__main__":
    if not nhap(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None):
        print("• không có gói KHO-HOC-VIEN mới cần nhận (hoặc kho đã có)")

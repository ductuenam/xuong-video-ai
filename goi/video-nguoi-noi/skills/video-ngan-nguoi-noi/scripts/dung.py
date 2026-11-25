"""Dựng cả video từ dữ liệu dự án, một lệnh.
  python dung.py <thư mục dự án> [--tu master|phu-de|canh|bundle|anh-tinh|render|tron|soat|nghiem-thu|nhan-dien] [--den <bước>] [--het]
Mặc định dừng sau bước anh-tinh để xem soat-tinh-*.jpg, ổn thì chạy tiếp: --tu render. Thêm --het để chạy một mạch.
Sửa chữ hoặc cảnh: chạy lại từ "canh". Sửa đoạn cắt: chạy lại từ "master". Sửa loi.txt: chạy lại từ "phu-de".
Giờ từng bước ghi vào thoi-gian.csv của dự án.
Dự án cần: doan.json, loi.txt, canh.json; có thể thêm goi-y.txt (tên riêng để Whisper nghe đúng), nhac.txt (đổi nhạc).
Bước cuối nhan-dien gắn watermark, intro, outro theo "nhanDien" của hồ sơ, ra render/thanh-pham.mp4 để bàn giao."""
import argparse
import datetime
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import cv2
import numpy as np

from chung import ENGINE, GOC_SKILL, chay, doc, ghi, ho_so, tam_rieng

BUOC = ["master", "phu-de", "canh", "bundle", "anh-tinh", "render", "tron", "soat", "nghiem-thu", "nhan-dien"]
NPX = "npx.cmd" if sys.platform == "win32" else "npx"
THU_MUC = Path(__file__).resolve().parent
TRUONG_KENH = ["ten", "chuLinhVat", "nhanCanhAI", "nhanAnhAI", "mauChinh", "mauPhu", "mauBia"]


def b_script(ten, da):
    chay([sys.executable, THU_MUC / ten, da], cwd=THU_MUC)


def dong_bo_engine(h, da=None):
    if not (ENGINE / "node_modules").exists():
        sys.exit(f"✘ Chưa cài engine ở {ENGINE}. Chạy cai_dat.py trước.")
    shutil.copytree(GOC_SKILL / "engine" / "src", ENGINE / "src", dirs_exist_ok=True)
    kenh = {k: h.get(k, "") for k in TRUONG_KENH}
    if str(kenh.get("ten", "")).strip().upper() == "TÊN KÊNH":  # hồ sơ mẫu chưa điền: không in chữ mẫu lên video (thử 24/11/2026)
        kenh["ten"] = ""
    # Video giới thiệu chỉ dùng ảnh thật của người dẫn (TOI*) hoặc nền màu tự tạo (NEN*): không gắn nhãn "Cảnh AI minh họa" (thử 24/11/2026)
    if da is not None and (da / "canh.json").exists() and {"gioi-thieu", "edit"} & set(((da / "loai.txt").read_text(encoding="utf-8") if (da / "loai.txt").exists() else "").split()):
        clip = [c.get("ten") or c.get("clip") for c in doc(da / "canh.json")["canh"] if c.get("ten") or c.get("clip")]
        if clip and all(str(x).startswith(("TOI", "NEN")) for x in clip):
            kenh["nhanCanhAI"] = ""
    ghi(ENGINE / "src" / "kenh.json", kenh)


def b_bundle(da, h):
    dong_bo_engine(h, da)
    chay([NPX, "remotion", "bundle", "src/index.ts", f"--public-dir={da / 'public'}", f"--out-dir={da / 'render' / 'bundle'}", "--log=error"], cwd=ENGINE)


def b_anh_tinh(da):
    """Ảnh tĩnh khung cuối mỗi cảnh, soát trước khi xuất video để khỏi xuất lại."""
    ra = da / "render" / "anh-tinh"
    shutil.rmtree(ra, ignore_errors=True)
    for f in da.glob("soat-tinh-*.jpg"):
        f.unlink()
    chay(["node", THU_MUC / "anh_tinh.cjs", ENGINE, da / "render" / "bundle", da / "props.json", ra], cwd=ENGINE)
    o = []
    for f in sorted(ra.glob("*.jpg")):
        a = cv2.imdecode(np.fromfile(f, "u1"), 1)
        cv2.putText(a, f.stem, (8, 34), cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 255), 3)
        o.append(a)
    cot = 5
    while len(o) % cot:
        o.append(np.zeros_like(o[0]))
    for n, i in enumerate(range(0, len(o), cot), 1):
        cv2.imencode(".jpg", np.hstack(o[i:i + cot]), [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(str(da / f"soat-tinh-{n}.jpg"))
        print("ảnh soát:", da / f"soat-tinh-{n}.jpg")
    giong = doc(da / "doan.json").get("giong")
    if giong:
        for dai, luc in khoang_lang(giong):
            print(f"✘ Giọng có khoảng lặng {dai:.2f} giây ở giây {luc:.1f}, sửa file giọng trước khi xuất")
        from do_nhip import MOC_HOI, MOC_TREN, do as do_nhip
        k = do_nhip(giong)
        if k["hoi"] < MOC_HOI:
            print(f"✘ Giọng rời rạc: một hơi nói chỉ {k['hoi']:.2f} giây (cần ≥ {MOC_HOI}), viết lại bản đọc cho liền hơi")
        elif k["hoi"] > MOC_TREN:
            print(f"⚠ (không chặn) Giọng liền quá: một hơi {k['hoi']:.2f} giây (nên ≤ {MOC_TREN}), giữ dấu phẩy ở chỗ chuyển ý, chạy nghi_dau_phay.py")


def khoang_lang(file, toi_da=0.7):
    """Cùng cách đo với nghiem_thu.py: VAD, không đo năng lượng."""
    from faster_whisper.vad import VadOptions, get_speech_timestamps
    from whisper_vi import doc_am_thanh
    ts = get_speech_timestamps(doc_am_thanh(file), VadOptions(threshold=0.5, min_silence_duration_ms=150, speech_pad_ms=0))
    return [((b["start"] - a["end"]) / 16000, a["end"] / 16000) for a, b in zip(ts, ts[1:]) if (b["start"] - a["end"]) / 16000 > toi_da]


def ghi_gio(da, b, giay):
    f = da / "thoi-gian.csv"
    moi = not f.exists()
    with f.open("a", encoding="utf-8") as g:
        if moi:
            g.write("luc,buoc,giay\n")
        g.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S},{b},{giay:.0f}\n")


def b_render(da):
    chay([NPX, "remotion", "render", da / "render" / "bundle", "MoHinh", da / "render" / "hinh-cam.mp4", f"--props={da / 'props.json'}", "--muted", "--crf=14", f"--concurrency={max(2, min(6, (os.cpu_count() or 4) // 2))}",
          "--image-format=jpeg", "--jpeg-quality=100", "--color-space=bt709", "--pixel-format=yuv420p", "--log=error"], cwd=ENGINE)


def b_soat(da):
    """Tờ soát: khung giữa mỗi cảnh, để xem bằng mắt."""
    moc = [float(x) for x in (da / "moc.txt").read_text(encoding="utf-8").split(",")]
    o = []
    for t in moc:
        c = cv2.VideoCapture(str(da / "render" / "ra.mp4"))
        c.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, f = c.read()
        c.release()
        if ok:
            f = cv2.resize(f, (270, 480), interpolation=cv2.INTER_AREA)
            cv2.putText(f, f"{t:.1f}s", (8, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
            o.append(f)
    cot = 8
    while len(o) % cot:
        o.append(np.zeros_like(o[0]))
    to = np.vstack([np.hstack(o[i:i + cot]) for i in range(0, len(o), cot)])
    cv2.imencode(".jpg", to, [cv2.IMWRITE_JPEG_QUALITY, 90])[1].tofile(str(da / "to-soat.jpg"))
    print("tờ soát:", da / "to-soat.jpg")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("du_an")
    ap.add_argument("--tu", choices=BUOC, default="master")
    ap.add_argument("--den", choices=BUOC)
    ap.add_argument("--het", action="store_true", help="không dừng ở bước anh-tinh")
    a = ap.parse_args()
    if not a.den:
        a.den = "anh-tinh" if not a.het and BUOC.index(a.tu) <= BUOC.index("anh-tinh") else "nhan-dien"
    da = Path(a.du_an).resolve()
    h = ho_so(da)
    for f in ("doan.json", "loi.txt", "canh.json"):
        if not (da / f).exists():
            sys.exit(f"✘ Dự án thiếu {f}")
    cac = BUOC[BUOC.index(a.tu):BUOC.index(a.den) + 1]
    with tam_rieng():
        chay_cac_buoc(a, da, h, cac)


def chay_cac_buoc(a, da, h, cac):
    dau = time.time()
    for b in cac:
        t0 = time.time()
        print(f"\n===== {b}")
        try:
            if b == "master":
                b_script("lap_master.py", da)
            elif b == "phu-de":
                b_script("lap_phu_de.py", da)
            elif b == "canh":
                b_script("lap_canh.py", da)
            elif b == "bundle":
                b_bundle(da, h)
            elif b == "anh-tinh":
                b_anh_tinh(da)
            elif b == "render":
                b_render(da)
            elif b == "tron":
                b_script("tron_am.py", da)
            elif b == "soat":
                b_soat(da)
            elif b == "nghiem-thu":
                b_script("nghiem_thu.py", da)
            elif b == "nhan-dien":
                b_script("gan_nhan_dien.py", da)
        except subprocess.CalledProcessError as e:
            print(f"\n✘ Dừng ở bước {b} (mã {e.returncode}). Tổng {time.time() - dau:.0f} giây.")
            sys.exit(e.returncode)
        ghi_gio(da, b, time.time() - t0)
        print(f"({b}: {time.time() - t0:.0f} giây)")
    if a.den == "anh-tinh":
        print(f"\nTổng {time.time() - dau:.0f} giây. Xem soat-tinh-*.jpg, ổn thì chạy tiếp: python dung.py \"{da}\" --tu render")
        return
    tp = da / "render" / ("thanh-pham.mp4" if "nhan-dien" in cac else "ra.mp4")
    print(f"\nTổng {time.time() - dau:.0f} giây. Thành phẩm: {tp}")


if __name__ == "__main__":
    main()

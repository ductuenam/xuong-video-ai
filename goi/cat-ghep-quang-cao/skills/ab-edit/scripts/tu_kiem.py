"""Tự kiểm video — 2 lúc: khi NHẬN file (keyframe, tốc độ khung) và sau khi XUẤT (khung đen/đứng/cháy, âm lượng, lặng chết, tờ soát khung).
  python tu_kiem.py nhan <file|thư mục> ... [--sua <07-du-an/tên>]   # thiếu keyframe / VFR → --sua tạo bản làm việc 1 keyframe/giây, CFR
  python tu_kiem.py xuat <video> [--moc 0,4.5,12 | --moc-file moc.json] [--brand <b> | --lufs -16] [--so-sanh <bản xuất lần 2>] [--ra <thư mục>]
                                                                      # → <video>-soat/: tờ khung hình + bao-cao.json; mã thoát 1 nếu có lỗi ✘
Bẫy keyframe: video điện thoại/xuất từ phần mềm dựng hay cách keyframe rất xa → máy dựng tua sai hoặc tự huỷ giữa chừng (video "Claude dựng video" 03/11/2026).
Máy kiểm xong vẫn phải SOÁT BẰNG MẮT tờ khung hình (chữ đè mặt, chữ sai, bố cục) — máy không bắt được các lỗi đó."""
import argparse
import json
import re
import subprocess
from pathlib import Path

from chung import chan_ghi_source, doc_brand, ma_hoa, sao_luu, tim_ffmpeg

VIDEO_EXT = {".mp4", ".mov", ".mkv", ".mxf", ".avi", ".m4v", ".webm"}
KF_TOI_DA = 2.0       # keyframe cách nhau quá 2s → cần bản làm việc
DEN_TOI_THIEU = 0.3   # khung đen liền ≥ 0,3s
DUNG_TOI_THIEU = 2.0  # hình đứng yên ≥ 2s
LANG_TOI_THIEU = 1.0  # lặng chết ≥ 1s dưới −50 dB
CHAY_YAVG = 235       # độ sáng trung bình khung (8-bit) ≥ 235 = cháy trắng


def chay(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")


def thong_tin(file):
    """ffprobe: luồng hình/tiếng, fps danh nghĩa và trung bình, thời lượng."""
    p = chay([tim_ffmpeg("ffprobe"), "-v", "error", "-show_entries",
              "stream=codec_type,codec_name,width,height,r_frame_rate,avg_frame_rate:format=duration", "-of", "json", str(file)])
    j = json.loads(p.stdout or "{}")
    v = next((s for s in j.get("streams", []) if s["codec_type"] == "video"), None)
    a = next((s for s in j.get("streams", []) if s["codec_type"] == "audio"), None)

    def ps(x):
        n, d = (x or "0/1").split("/")
        return float(n) / float(d) if float(d) else 0.0

    return {"video": v, "audio": a, "dur": float(j.get("format", {}).get("duration", 0)),
            "fps": ps(v["r_frame_rate"]) if v else 0, "fps_tb": ps(v["avg_frame_rate"]) if v else 0}


def khoang_keyframe(file):
    """Đọc gói tin (không giải mã) → các mốc keyframe, khoảng cách lớn nhất."""
    p = chay([tim_ffmpeg("ffprobe"), "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time,flags",
              "-of", "csv=p=0", str(file)])
    kf = sorted(float(t) for t, f in (ln.split(",")[:2] for ln in p.stdout.splitlines() if ln.count(",") >= 1)
                if "K" in f and t not in ("", "N/A"))
    if len(kf) < 2:
        return kf, None
    return kf, max(b - a for a, b in zip(kf, kf[1:]))


def ban_lam_viec(src, thu_muc, fps):
    """Mã hoá lại: tốc độ khung đều (CFR), 1 keyframe mỗi giây. Không đụng file gốc."""
    out = Path(thu_muc) / f"{Path(src).stem}-lamviec.mp4"
    chan_ghi_source(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    sao_luu(out)
    g = max(1, round(fps))
    cmd = [tim_ffmpeg(), "-y", "-v", "error", "-stats", "-i", str(src), "-fps_mode", "cfr", "-r", f"{fps:.3f}",
           *ma_hoa("60M"), "-g", str(g), "-force_key_frames", "expr:gte(t,n_forced*1)", "-forced-idr", "1",
           "-c:a", "aac", "-b:a", "320k", "-movflags", "+faststart", str(out)]
    if subprocess.run(cmd).returncode:
        raise SystemExit(f"Mã hoá lại lỗi: {src}")
    return out


def nhan(a):
    files = []
    for x in a.files:
        p = Path(x)
        files += sorted(f for f in p.rglob("*") if f.suffix.lower() in VIDEO_EXT) if p.is_dir() else [p]
    can_sua = 0
    for f in files:
        tt = thong_tin(f)
        if not tt["video"]:
            print(f"✘ {f.name}: không có luồng hình")
            continue
        kf, kmax = khoang_keyframe(f)
        vfr = tt["fps_tb"] and abs(tt["fps"] - tt["fps_tb"]) / tt["fps"] > 0.01
        loi = []
        if kmax is None:
            loi.append(f"chỉ {len(kf)} keyframe")
        elif kmax > KF_TOI_DA:
            loi.append(f"keyframe cách nhau tới {kmax:.1f}s")
        if vfr:
            loi.append(f"tốc độ khung không đều ({tt['fps']:.2f} danh nghĩa / {tt['fps_tb']:.2f} trung bình)")
        v = tt["video"]
        mo_ta = f"{v['width']}×{v['height']} {v['codec_name']} {tt['fps']:.2f}fps {tt['dur']:.1f}s" + ("" if tt["audio"] else " · KHÔNG CÓ TIẾNG")
        if not loi:
            print(f"✔ {f.name}: {mo_ta} · keyframe ≤ {kmax:.1f}s")
            continue
        can_sua += 1
        print(f"⚠ {f.name}: {mo_ta} · " + "; ".join(loi))
        if a.sua:
            out = ban_lam_viec(f, a.sua, tt["fps"] if not vfr else round(tt["fps_tb"]))
            _, k2 = khoang_keyframe(out)
            print(f"   → bản làm việc: {out} (keyframe ≤ {k2:.1f}s) — dựng bằng file này, giữ nguyên file gốc")
    if can_sua and not a.sua:
        print(f"\n{can_sua} file cần bản làm việc → chạy lại kèm --sua <07-du-an/tên dự án>")


def quet_hinh_tieng(file, co_tieng):
    """1 lượt ffmpeg: blackdetect + freezedetect + độ sáng (2 khung/s) trên hình; ebur128 + silencedetect trên tiếng."""
    vf = (f"scale=480:-2,format=yuv420p,blackdetect=d={DEN_TOI_THIEU}:pix_th=0.10,freezedetect=n=-60dB:d={DUNG_TOI_THIEU},"
          "fps=2,signalstats,metadata=mode=print:key=lavfi.signalstats.YAVG")
    cmd = [tim_ffmpeg(), "-nostdin", "-hide_banner", "-v", "info", "-i", str(file), "-map", "0:v:0", "-vf", vf, "-f", "null", "-"]
    if co_tieng:
        cmd[cmd.index("-f"):cmd.index("-f")] = ["-map", "0:a:0", "-af",
                                                 f"ebur128=peak=true:framelog=verbose,silencedetect=n=-50dB:d={LANG_TOI_THIEU}"]
    log = chay(cmd).stderr
    den = [(float(s), float(e)) for s, e in re.findall(r"black_start:([\d.]+) black_end:([\d.]+)", log)]
    dung_s = [float(x) for x in re.findall(r"freeze_start: ([\d.]+)", log)]
    dung_e = [float(x) for x in re.findall(r"freeze_end: ([\d.]+)", log)]
    dung = list(zip(dung_s, dung_e + [None] * (len(dung_s) - len(dung_e))))
    sang, t = [], None
    for ln in log.splitlines():
        m = re.search(r"pts_time:([\d.]+)", ln)
        if m:
            t = float(m.group(1))
        m = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", ln)
        if m and t is not None:
            sang.append((t, float(m.group(1))))
    chay_trang, dau = [], None
    for t, y in sang + [(None, 0)]:
        if t is not None and y >= CHAY_YAVG:
            dau = t if dau is None else dau
        elif dau is not None:
            chay_trang.append((dau, t if t is not None else sang[-1][0]))
            dau = None
    lang = []
    if co_tieng:
        s = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", log)]
        e = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
        lang = list(zip(s, e + [None] * (len(s) - len(e))))
    tom = log[log.rfind("Summary:"):] if "Summary:" in log else ""
    lufs = re.search(r"I:\s+(-?[\d.]+) LUFS", tom)
    dinh = re.search(r"Peak:\s+(-?[\d.]+) dBFS", tom)
    return {"den": den, "dung": dung, "chay_trang": chay_trang, "lang": lang,
            "lufs": float(lufs.group(1)) if lufs else None, "dinh": float(dinh.group(1)) if dinh else None}


def to_khung(file, moc, thu_muc):
    """Trích 1 khung ở mỗi mốc (ghi giây lên ảnh) → ghép 1 tờ để soát bằng mắt."""
    ff = tim_ffmpeg()
    thu_muc.mkdir(parents=True, exist_ok=True)
    chu = "fontfile='C\\:/Windows/Fonts/arial.ttf':fontsize=28:fontcolor=white:box=1:boxcolor=black@0.6:boxborderw=6:x=10:y=10"
    for i, t in enumerate(moc, 1):
        out = thu_muc / f"khung_{i:02d}.jpg"
        chay([ff, "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", str(file), "-frames:v", "1",
              "-vf", f"scale=360:-2,drawtext=text='{i:02d} · {t:.1f}s':{chu}", "-q:v", "3", str(out)])
    cot = 6 if len(moc) > 8 else 4
    hang = -(-len(moc) // cot)
    to = thu_muc / "to-soat-khung.jpg"
    chay([ff, "-y", "-v", "error", "-framerate", "1", "-i", str(thu_muc / "khung_%02d.jpg"),
          "-vf", f"tile={cot}x{hang}:padding=6:color=gray", "-frames:v", "1", "-q:v", "3", str(to)])
    return to


def so_khung(a_file, b_file):
    """So 2 lần xuất từng khung (SSIM). Khung lệch = hiệu ứng không ổn định / lỗi ngẫu nhiên khi render."""
    p = chay([tim_ffmpeg(), "-nostdin", "-v", "error", "-i", str(a_file), "-i", str(b_file),
              "-lavfi", "[0:v][1:v]ssim=stats_file=-", "-f", "null", "-"])
    lech = [(int(n), float(s)) for n, s in re.findall(r"n:(\d+).*?All:([\d.]+)", p.stdout) if float(s) < 0.98]
    return lech


def xuat(a):
    f = Path(a.video)
    tt = thong_tin(f)
    if not tt["video"]:
        raise SystemExit(f"✘ {f.name}: không có luồng hình")
    soat = Path(a.ra) / f"{f.stem}-soat" if a.ra else f.with_name(f"{f.stem}-soat")
    chan_ghi_source(soat)
    if a.moc:
        moc = [float(x) for x in a.moc.split(",")]
    elif a.moc_file:
        moc = [float(x) for x in json.loads(Path(a.moc_file).read_text(encoding="utf-8"))]
    else:  # không có mốc cảnh → rải đều ~1 khung/4s, tối đa 24 khung
        n = max(6, min(24, round(tt["dur"] / 4)))
        moc = [tt["dur"] * (i + 0.5) / n for i in range(n)]
    print(f"Bước 1 – quét hình + tiếng ({tt['dur']:.0f}s)…")
    q = quet_hinh_tieng(f, bool(tt["audio"]))
    print("Bước 2 – trích tờ khung hình…")
    to = to_khung(f, moc, soat)

    loi, canh_bao = [], []
    if not tt["audio"]:
        loi.append("không có tiếng")
    for s, e in q["den"]:
        loi.append(f"khung đen {s:.1f}–{e:.1f}s")
    for s, e in q["chay_trang"]:
        canh_bao.append(f"cháy trắng {s:.1f}–{e:.1f}s")
    for s, e in q["dung"]:
        canh_bao.append(f"hình đứng yên {s:.1f}–{e:.1f}s" if e else f"hình đứng yên từ {s:.1f}s tới hết")
    for s, e in q["lang"]:
        canh_bao.append(f"lặng chết {s:.1f}–{e:.1f}s" if e else f"lặng chết từ {s:.1f}s tới hết")
    if q["lufs"] is not None:
        if abs(q["lufs"] - a.lufs) > 1.5:
            loi.append(f"âm lượng {q['lufs']:.1f} LUFS (chuẩn {a.lufs:.0f} ±1,5)")
        if q["dinh"] is not None and q["dinh"] > -1.0:
            canh_bao.append(f"đỉnh tiếng {q['dinh']:.1f} dBFS (nên ≤ −1)")
    lech = []
    if a.so_sanh:
        print("Bước 3 – so từng khung với bản xuất lần 2…")
        lech = so_khung(f, a.so_sanh)
        fps = tt["fps"] or 30
        for n, s in lech[:20]:
            loi.append(f"khung {n} (~{n / fps:.2f}s) khác bản 2 (SSIM {s:.3f})")

    v = tt["video"]
    bao_cao = {"file": str(f), "khung_hinh": f"{v['width']}x{v['height']}", "fps": round(tt["fps"], 3), "thoi_luong": round(tt["dur"], 2),
               "lufs": q["lufs"], "dinh_dbfs": q["dinh"], "loi": loi, "canh_bao": canh_bao, "so_khung_lech": len(lech),
               "to_soat": str(to), "moc_soat": [round(x, 2) for x in moc]}
    (soat / "bao-cao.json").write_text(json.dumps(bao_cao, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"\n{f.name}: {v['width']}×{v['height']} · {tt['fps']:.2f}fps · {tt['dur']:.1f}s · "
          f"{q['lufs'] if q['lufs'] is not None else '—'} LUFS · đỉnh {q['dinh'] if q['dinh'] is not None else '—'} dBFS")
    for x in loi:
        print(f"✘ {x}")
    for x in canh_bao:
        print(f"⚠ {x}")
    if not loi and not canh_bao:
        print("✔ máy kiểm không thấy lỗi")
    print(f"Tờ soát khung: {to}\n→ Vẫn phải mở tờ này soát bằng mắt: chữ đè mặt, chữ sai/tràn khung, bố cục, cảnh trám dính khung cảnh khác.")
    raise SystemExit(1 if loi else 0)


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="lenh", required=True)
    n = sp.add_parser("nhan", help="kiểm file mới nhận (source, cảnh trám, video mẫu)")
    n.add_argument("files", nargs="+")
    n.add_argument("--sua", help="thư mục dự án để ghi bản làm việc")
    x = sp.add_parser("xuat", help="tự kiểm video vừa xuất")
    x.add_argument("video")
    x.add_argument("--moc", help="giây đại diện từng cảnh, cách nhau dấu phẩy")
    x.add_argument("--moc-file", help="file JSON danh sách giây")
    x.add_argument("--brand", help="lấy chuẩn âm lượng từ brands/<tên>.json › am_thanh.giong_lufs")
    x.add_argument("--lufs", type=float, help="chuẩn âm lượng (mặc định: theo --brand, không có thì −16)")
    x.add_argument("--so-sanh", help="bản xuất lần 2 cùng thông số để so từng khung")
    x.add_argument("--ra", help="thư mục ghi tờ soát + báo cáo (mặc định cạnh video)")
    a = ap.parse_args()
    if a.lenh == "xuat" and a.lufs is None:
        a.lufs = float(doc_brand(a.brand).get("am_thanh", {}).get("giong_lufs", -16)) if a.brand else -16.0
    nhan(a) if a.lenh == "nhan" else xuat(a)


if __name__ == "__main__":
    main()

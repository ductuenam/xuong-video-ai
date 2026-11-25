"""Video giới thiệu bản thân 30 giây theo BNI, chạy một lệnh (24/11/2026, mẫu thử lớp làm video).

  python bni.py "<dự án>"

Trong thư mục dự án (bên trong <thư mục kênh>/du-an/) cần có:
  loi.txt      phụ đề, mỗi dòng một cụm, đúng lời đọc
  doc-tts.txt  bản đọc một đoạn liền hơi (vế dài, có ít nhất một dấu chấm than)
  bni.json     {"phan": [số dòng loi.txt của 5 phần], "mo": ["TÊN", "THƯƠNG HIỆU"],
                "giup": {"tren": "Tôi giúp", "duoi": "<khách, ngắn>", "viec": [["việc", "phụ"], ...] tối đa 3},
                "bangChung": ["DÒNG 1", "DÒNG 2"], "khachTot": [["tên", "phụ"], ["tên", "phụ"]],
                "ghiNho": "<câu ghi nhớ ngắn>", "lienHe": "<ít nhất 2 chữ, vd ZALO 09xx...>",
                "giongTuQuay": "<tùy chọn: file video/âm thanh học viên tự đọc đúng lời, trong anh-video-cua-toi/>"}

Script tự làm:
  1. Ảnh, video của chính người dẫn trong <thư mục kênh>/anh-video-cua-toi/: có thì đổi thành clip dọc 8 giây
     (ảnh tĩnh cho chuyển động nhẹ) làm cảnh mở, bằng chứng, kết. Không có thì chế độ khong-mat: cảnh thật không người.
  2. loai.txt = gioi-thieu (+ khong-mat), nhac.txt, doan.json.
  3. Giọng: giongTuQuay thì lấy tiếng trong file đó; không thì tao_giong.py theo giongAI của hồ sơ
     (học viên chưa có giọng nhân bản: provider "edge", giọng miễn phí). Rồi cắt nghỉ, chèn nghỉ dấu phẩy.
  4. Lập canh.json từ bni.json rồi chạy dung.py --het (nghiệm thu, nhận diện kênh).
"""
import csv
import json
import subprocess
import sys
from pathlib import Path

from chung import doc, duong_dan, ghi, ho_so

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ND = Path(__file__).resolve().parent
ANH = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}
AM = {".m4a", ".mp3", ".wav", ".aac"}
# Cảnh thật, không người, hợp người làm nghề. Thứ tự ưu tiên; mã nào không có trên máy thì bỏ qua.
# Mặc định là nền màu dịu (K055 sóng pastel, K049 sóng trắng) và cảnh đời thường đẹp (K082 sân thượng hoàng hôn), hợp mọi nghề; cảnh công nghệ viễn tưởng (N031 bảng số liệu, N100 thành phố neon)
# chỉ hợp người làm công nghệ, khi đó ghi "canh" trong bni.json. bni.json "canh": {"mo", "bang", "ket"} ghi đè từng vai.
UU_TIEN = {
    "mo": ["K055", "K082", "K049", "K075"],
    "bang": ["K049", "K055", "K080", "K082"],
    "ket": ["K082", "K055", "K079", "K075"],
}
HOAT_HINH = ("tí hon", "đất sét", "hoạt hình", "cartoon", "đồ chơi")
# Nền màu dịu tự tạo khi kho cảnh trống: kem cam, xanh ngọc nhạt, tím hồng nhạt (3 vai mở, bằng chứng, kết)
NEN_MEM = [("0xF6D9C4", "0xE9B7A0", "0xF3E6D8"), ("0xCFE8E4", "0xA9D3CF", "0xE6F2EF"), ("0xE8DDF0", "0xD6C3E6", "0xF4EDF7")]


def ff(*a):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *map(str, a)], check=True)


def clip_toi(f, ra):
    """Ảnh hoặc video của người dẫn thành clip dọc 1080x1920, 8 giây, không tiếng."""
    vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
    if f.suffix.lower() in ANH:
        # Giữ trọn ảnh, thu vào khung 1080x1600 đặt sát đáy (chừa 320 px phía trên cho ô tên, ô liên hệ, kể cả ảnh dọc 9:16); nền là chính ảnh đó làm mờ
        # (ô tiêu đề, ô liên hệ nằm phía trên nên không che đầu). Rồi phóng chậm 1,00 -> 1,06 trong 8 giây.
        nen = ra.with_suffix(".nen.png")
        ff("-i", f, "-filter_complex",
           "[0]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:2[bg];"
           "[0]scale=1080:1600:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:H-h",
           "-frames:v", 1, nen)
        ff("-loop", "1", "-i", nen, "-t", 8, "-vf",
           "scale=2160:3840,zoompan=z='1+0.06*on/200':x='iw/2-(iw/zoom/2)':y='ih-(ih/zoom)':d=200:s=1080x1920:fps=25,format=yuv420p",
           "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 18, ra)
        nen.unlink(missing_ok=True)
    else:
        ff("-i", f, "-t", 8, "-vf", vf + ",fps=25,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "fast", "-crf", 18, ra)


def main():
    da = Path(sys.argv[1]).resolve()
    h = ho_so(da)
    kenh = Path(h["_goc"])
    from nhap_kho import nhap
    if nhap(kenh):  # có gói KHO-HOC-VIEN trong Downloads thì tự nhận cảnh, nhạc rồi đọc lại hồ sơ
        h = ho_so(da)
    b = doc(da / "bni.json")
    dong = [x for x in (da / "loi.txt").read_text(encoding="utf-8").splitlines() if x.strip()]
    phan = b["phan"]
    dai = [x for x in dong if len(x) > 28]
    if dai:
        print("⚠ dòng phụ đề dài hơn 28 ký tự sẽ rớt chữ xuống dòng, nên tách:", " | ".join(dai))
    if len(b["ghiNho"]) > 18:
        print(f"⚠ ghiNho {len(b['ghiNho'])} ký tự, thẻ kết dễ rớt chữ giữa tên thương hiệu; nên ≤ 18 (câu đọc vẫn có thể dài hơn)")
    # lời đọc và phụ đề phải cùng chữ, lệch là nghiệm thu "đủ lời" trượt sau khi đã tạo giọng (thử 24/11/2026)
    import difflib, re as _re
    _w = lambda t: _re.findall(r"\w+", t.lower())  # noqa: E731
    giong_nhau = difflib.SequenceMatcher(None, _w(" ".join(dong)), _w((da / "doc-tts.txt").read_text(encoding="utf-8"))).ratio()
    if giong_nhau < 0.85:
        sys.exit(f"✘ doc-tts.txt lệch chữ với loi.txt (giống {giong_nhau:.0%}, cần ≥ 85%): viết doc-tts.txt trước rồi cắt loi.txt từ đúng những chữ đó")
    if len(phan) != 5 or sum(phan) != len(dong):
        sys.exit(f"✘ bni.json phan {phan} (tổng {sum(phan)}) phải đủ 5 phần và bằng số dòng loi.txt ({len(dong)})")

    # 1. Ảnh, video của người dẫn
    thu_muc_toi = kenh / "anh-video-cua-toi"
    giong_tu_quay = b.get("giongTuQuay")
    toi = sorted(f for f in thu_muc_toi.glob("*") if f.suffix.lower() in ANH | VIDEO) if thu_muc_toi.exists() else []
    toi.sort(key=lambda f: (f.suffix.lower() not in VIDEO, f.name))  # video trước, ảnh sau
    canh_dir = da / "public" / "canh"
    canh_dir.mkdir(parents=True, exist_ok=True)
    ma_toi = []
    for i, f in enumerate(toi[:4], 1):
        ma = f"TOI{i}"
        clip_toi(f, canh_dir / f"{ma}.mp4")
        ma_toi.append(ma)
    co_mat = bool(ma_toi)
    print(f"{'✔ có' if co_mat else '• không có'} ảnh/video của người dẫn trong {thu_muc_toi}"
          + (f": {', '.join(f.name for f in toi[:4])}" if co_mat else " → chế độ không mặt, dùng cảnh thật không người"))
    (da / "loai.txt").write_text("gioi-thieu" + ("" if co_mat else " khong-mat"), encoding="utf-8")
    if not (da / "nhac.txt").exists():
        (da / "nhac.txt").write_text("beat-vlog", encoding="utf-8")

    # 2. Clip kho cho chế độ không mặt (hoặc bổ sung khi người dẫn có ít hơn 3 ảnh)
    kho = duong_dan(h, h["khoCanh"]["thuMuc"])
    dm = kho / h["khoCanh"]["danhMuc"]
    chi_muc = {f.name: f for f in kho.rglob("*.mp4")}
    co = {}
    if dm.exists():
        for r in csv.DictReader(dm.open(encoding="utf-8-sig")):
            f = chi_muc.get(r["file"])
            if r.get("dung") == "co" and f is not None and not any("CO MAT" in x.upper() for x in f.relative_to(kho).parts[:-1]) \
                    and not any(t in (r.get("ghi_chu") or "").lower() for t in HOAT_HINH):
                co[r["ma"]] = r
    da_dung = set()

    def chon(vai, so_toi):
        if co_mat:
            return ma_toi[so_toi % len(ma_toi)]
        for ma in [*([b["canh"][vai]] if b.get("canh", {}).get(vai) else []), *UU_TIEN[vai], *sorted(co)]:
            if ma in co and ma not in da_dung:
                da_dung.add(ma)
                return ma
        # Máy học viên mới chưa có kho cảnh (24/11/2026, thử trên máy sạch bị dừng ở đây): tự tạo nền màu dịu chuyển động
        # chậm, không người, không hoạt hình; kho có clip thì không tới đây.
        ma = f"NEN{so_toi + 1}"
        c0, c1, c2 = NEN_MEM[so_toi % len(NEN_MEM)]
        ff("-f", "lavfi", "-i", f"gradients=s=1080x1920:c0={c0}:c1={c1}:c2={c2}:n=3:speed=0.015:d=8:r=25,format=yuv420p",
           "-t", 8, "-c:v", "libx264", "-preset", "fast", "-crf", 20, canh_dir / f"{ma}.mp4")
        print(f"• kho cảnh trống: tự tạo nền màu {ma} cho vai '{vai}' (thả ảnh, video của mình vào anh-video-cua-toi sẽ đẹp hơn)")
        return ma

    # 3. Giọng
    giong = da / "giong"
    giong.mkdir(exist_ok=True)
    from kiem_chot import sua_doc
    chu_doc, _ = sua_doc((da / "doc-tts.txt").read_text(encoding="utf-8").strip())
    cu = giong / "ca-bai.da-gui.txt"
    tho_cu = next((x for x in (giong / "ca-bai.mp3", giong / "ca-bai.wav") if x.exists() and x.stat().st_size > 20000), None)
    if not giong_tu_quay and tho_cu and cu.exists() and cu.read_text(encoding="utf-8").strip() == chu_doc:
        # chạy lại sau khi sửa chữ trên hình: lời đọc không đổi thì giữ giọng cũ, không tốn credit
        tho = tho_cu
        print(f"✔ lời đọc không đổi, dùng lại giọng {tho.name}")
    elif giong_tu_quay:
        nguon = (kenh / giong_tu_quay) if not Path(giong_tu_quay).is_absolute() else Path(giong_tu_quay)
        ff("-i", nguon, "-vn", "-ac", 1, "-ar", 48000, giong / "ca-bai.wav")
        (giong / "ca-bai.da-gui.txt").write_text(chu_doc, encoding="utf-8")
        tho = giong / "ca-bai.wav"
        print(f"✔ dùng tiếng người dẫn tự quay: {nguon.name}")
    else:
        r = subprocess.run([sys.executable, ND / "tao_giong.py", da, "--chu-file", "doc-tts.txt", "--ra", "giong/ca-bai"])
        if r.returncode:
            sys.exit("✘ Tạo giọng chưa được, sửa doc-tts.txt theo dòng ✘ ở trên rồi chạy lại bni.py.")
        tho = giong / "ca-bai.mp3"
    ff("-i", tho, "-af", "silenceremove=stop_periods=-1:stop_duration=0.25:stop_threshold=-40dB:stop_silence=0.2",
       "-ar", 48000, giong / "giong-gon.wav")
    subprocess.run([sys.executable, ND / "nghi_dau_phay.py", giong / "giong-gon.wav", da / "loi.txt", giong / "giong-nghi.wav"], check=True)
    ghi(da / "doan.json", {"nguon": [], "giong": str(giong / "giong-nghi.wav").replace("\\", "/")})

    # 4. Cảnh: tu: N là lúc dòng N (đếm từ 1) bắt đầu, tu: 0 là đầu video; den là lúc dòng đầu của phần sau bắt đầu.
    #    Phần 1 có 2 dòng thì tu 0, den 3; phần 2 có 4 dòng thì tu 3, den 7 (xem mo-hinh-canh.md)
    m, cong = [0], 0
    for n in phan:
        cong += n
        m.append(cong + 1)
    g = b["giup"]
    viec = g["viec"][:3]
    # Mỗi việc hiện đúng lúc đọc tới: tìm dòng đầu tiên trong phần 2 có chữ đầu của việc đó (vd "Viết content" -> dòng có
    # "viết"); không thấy thì chia đều; luôn tăng dần và nằm trong [tu, den - 1].
    def moc_theo_chu(ten, tu, den):
        """moc: N là lúc dòng N bắt đầu. Dò dòng đầu tiên trong [tu, den) có một chữ của mục (bỏ chữ chung chung)."""
        ra, truoc = [], tu
        tach = [[w for w in t.lower().replace(",", " ").split() if len(w) > 1 and w not in {"và", "cho", "các", "có"}] for t in ten]
        # Chữ có ở từ 2 mục trở lên ("hoa" trong "Hoa khai trương", "Hoa sinh nhật") khớp ngay dòng đầu làm mọi thẻ hiện
        # cùng lúc (thử 24/11/2026): bỏ, chỉ dò chữ riêng của từng mục.
        chung = {w for w in {x for c in tach for x in c} if sum(w in c for c in tach) > 1}
        for i, t in enumerate(ten):
            chu = [w for w in tach[i] if w not in chung] or tach[i]
            bat_dau = truoc + (1 if i and truoc + 1 < den else 0)  # mục sau hiện sau mục trước
            tim = next((j for j in range(bat_dau, den) if any(w in dong[j - 1].lower() for w in chu)), None)
            if tim is None:
                tim = tu + round(i * (den - tu) / max(len(ten), 1))
            tim = min(max(tim, bat_dau), den - 1)
            ra.append(tim)
            truoc = tim
        return ra

    moc_viec = moc_theo_chu([v[0] for v in viec], m[1], m[2])
    # Hồ sơ kênh mẫu để "TÊN KÊNH": học viên chưa sửa thì lấy thương hiệu trong bni.json, không in chữ mẫu lên video
    nhan_kenh = h.get("ten", "")
    if not nhan_kenh or nhan_kenh.strip().upper() == "TÊN KÊNH":
        nhan_kenh = b["mo"][1]
        f_hs = kenh / "ho-so-kenh.json"
        if f_hs.exists():  # nhãn góc của dung.py cũng đọc "ten": điền luôn vào hồ sơ mẫu, chỉ thay đúng chữ mẫu
            hs = json.loads(f_hs.read_text(encoding="utf-8"))
            if str(hs.get("ten", "")).strip().upper() in ("", "TÊN KÊNH"):
                hs["ten"] = nhan_kenh
                f_hs.write_text(json.dumps(hs, ensure_ascii=False, indent=2), encoding="utf-8")
                print(f"• hồ sơ kênh còn tên mẫu: đã điền \"{nhan_kenh}\"")
    canh = [
        {"loai": "flow-chu", "nen": True, "ten": chon("mo", 0), "tren": b["mo"][0], "duoi": b["mo"][1],
         "tu": m[0], "den": m[1], "viTriPhuDe": 1420, "y": 150},
        {"loai": "danh-sach-buoc", "kieuNen": "luoi", "tren": g["tren"], "duoi": g["duoi"],
         "buoc": [{"ten": v[0], **({"phu": v[1]} if len(v) > 1 and v[1] else {})} for v in viec],
         "moc": moc_viec, "tu": m[1], "den": m[2], "viTriPhuDe": 1420, "amMoc": "hien-the"},
        {"loai": "flow-chu", "nen": True, "ten": chon("bang", 1), "tren": b["bangChung"][0], "duoi": b["bangChung"][1],
         "tu": m[2], "den": m[3], "viTriPhuDe": 1420, "y": 150},
        {"loai": "canh-bao", "kieuNen": "toi", "tren": "Khách tốt", "duoi": "cho tôi là",
         "dong": [[mau, *x] for mau, x in zip(("xanh", "vang", "xanh"), b["khachTot"][:3])],
         "moc": moc_theo_chu([x[0] for x in b["khachTot"][:3]], m[3], m[4]), "tu": m[3], "den": m[4], "viTriPhuDe": 1500,
         "linhVat": False},
        {"loai": "ket-comment", "clip": chon("ket", 2), "nhan": nhan_kenh, "tieuDe": b["ghiNho"],
         "tuKhoa": b["lienHe"], "tu": m[4], "den": "het", "viTriPhuDe": 1480, "am": "thong-bao", "choLapCanhKet": True},
    ]
    ghi(da / "canh.json", {"canh": canh}, 1)
    print("✔ canh.json:", ", ".join(f"{c['loai']}({c.get('ten') or c.get('clip') or ''})" for c in canh))

    # 5. Dựng một mạch
    r = subprocess.run([sys.executable, ND / "dung.py", da, "--het"])
    if r.returncode:
        sys.exit(r.returncode)
    print(f"\n✔ Video giới thiệu: {da / 'render' / 'thanh-pham.mp4'}")


if __name__ == "__main__":
    main()
